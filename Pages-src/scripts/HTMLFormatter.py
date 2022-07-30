import re
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename, find_lexer_class_by_name
from json import JSONDecoder
from pprint import pformat
from os import getenv
from os import path
from os.path import exists, splitext, dirname, relpath, basename, join
import subprocess
import sys

from git import get_git_remote_link

from Style import VSCodeStyle

# region Header anchors


def remove_special_chars(name):
    # To lowercase
    name = name.lower()
    # Replace HTML entities with '-'
    name = re.sub(r"&(?:[a-z\d]+|#\d+|#x[a-f\d]+);", r"-", name)
    # Leave out HTML tags
    name = re.sub(r"(<|</)([^<>])+>", r"", name)
    # Only alphanumeric lowercase, replace everything else with '-'
    name = re.sub(r"[^a-z\d]", r"-", name)
    # More than one '-' replaced with single '-'
    name = re.sub(r"-+", r"-", name)
    # Strip '-' from the start or end of the string
    name = re.sub(r"/^-|-$", r"", name)
    return name


def format_anchor_name(match, anchors):
    tag = match.group(1)
    attr = match.group(2)
    fullname = match.group(3)

    a_name = remove_special_chars(fullname)

    # Don't allow duplicate IDs, so add a number at the end to make it unique
    i = 1
    new_a_name = a_name
    while new_a_name in anchors:
        new_a_name = a_name + str(i)
        i += 1
    code_snip = tag == '4' and 'class="snippet-name"' in attr
    anchors[new_a_name] = (fullname, int(tag), code_snip)

    return "<h" + tag + attr + "><a name=\"" + new_a_name \
         + "\" href=\"#" + new_a_name \
         + "\">"+fullname+"</a></h" + tag + ">"


def addAnchors(html: str, metadata: dict) -> str:
    anchors = dict()
    html = re.sub(r"<h([1-6])([^>]*)>(((?!<a).)+)</h\1>",
                  lambda match: format_anchor_name(match, anchors), html)

    if len(anchors) == 0:
        return html

    toc = metadata.get('tableofcontents', '0').lower()
    if toc in ["0", "false", "no", "n", "f"]:
        return html
    if not toc in ["1", "true", "yes", "y", "t"]:
        raise Exception("String should have truth value (e.g. "
                        "\"true\" or \"false\"), got \"" +
                        toc + "\" instead.")
    toc = '\n<div class="toc" id="toc">\n'
    toc += '  <script>\n'
    toc += '  function updateTocSize() {\n'
    toc += '    let toc = document.getElementById("toc");\n'
    toc += "    toc.style.maxHeight = toc.scrollHeight + 'px';\n"
    toc += '  }\n'
    toc += '  </script>'
    toc += '  <h4 class="toc" '
    toc += 'onclick="'
    toc += "if (this.parentElement.classList.toggle('expanded')) {"
    toc += "updateTocSize();"
    toc += "window.addEventListener('resize', updateTocSize);"
    toc += "} else {"
    toc += "this.parentElement.style = undefined;"
    toc += "window.removeEventListener('resize', updateTocSize);"
    toc += '}">'
    toc += 'Table of Contents '
    toc += '<i class="material-icons">list</i>'
    toc += '</h4>\n'
    toc += '  <ul>\n'
    initial_level = min(map(lambda x: x[1], anchors.values()))
    current_level = initial_level
    for name, v in anchors.items():
        title, level, code_snippet = v
        if code_snippet:
            continue
        while current_level < level:
            # toc += '    ' * current_level + '<li>\n'
            toc += '    ' * current_level + '  <ul>\n'
            current_level += 1
        while current_level > level:
            current_level -= 1
            toc += '    ' * current_level + '  </ul>\n'
            # toc += '    ' * current_level + '</li>\n'
        toc += '    ' * current_level
        toc += '<li>'
        toc += f'<a href="#{name}">{title}</a>'
        toc += '</li>\n'
    while current_level > initial_level:
        current_level -= 1
        toc += '    ' * (current_level + 1) + '</ul>\n'
        # toc += '    ' * current_level + '</li>\n'
    toc += '  </ul>'
    toc += '</div>\n'
    return toc + html


# endregion

# region Code line numbers


def addCodeLines(match):
    pre = match.group(1)
    pre = re.sub(r"(<pre.*?>)(?:\r\n|\n)*", r"\g<1><code>", pre)
    pre = re.sub(r"\r\n|\n", r"</code>\g<0><code>", pre)
    pre = re.sub(r"</pre>", r"</code></pre>", pre)
    return pre


def addLineNumbersEmphasis(match):
    pre = match.group(1)
    pre = re.sub(r"(<pre.*?>)(?:\r\n|\n)*", r"\g<1><code>", pre)
    pre = re.sub(r"\r\n|\n", r"</code>\g<0><code>", pre)
    pre = re.sub(r"</pre>", r"</code></pre>", pre)
    pre = re.sub(r"<code>(\s*)\*\*\*", r'<code class="emphasis">\g<1>', pre)
    return pre


def formatCode(html, metadata):
    findPre = r"(<pre[^>]* class=\"lineNumbers( |\")[^>]*>((?!<pre).|\r\n|\n)*</pre>)"
    findPreEmph = r"(<pre[^>]* class=\"lineNumbersEmphasis[^>]*>((?!<pre).|\r\n|\n)*</pre>)"

    html = re.sub(findPre, addCodeLines, html)
    html = re.sub(findPreEmph, addLineNumbersEmphasis, html)

    # Arduino IDE export HTML doesn't encode HTML entities
    html = re.sub(r">&<", r">&amp;<", html)
    html = re.sub(r">&=<", r">&amp;=<", html)

    return html


# endregion

# region Make file

def checkPath(filepath, file, msg):
    # file = re.sub(r'\$(\w+)', lambda m: getenv(m.group(1)), file)
    if path.isabs(file):
        raise Exception(f'{msg} "{file}" cannot be an absolute path')
    fullfile = path.join(path.dirname(filepath), file)
    if not exists(fullfile):
        raise Exception(f'{msg} "{fullfile}" does not exist')
    return fullfile


def handleMake(data, html, filepath, taglineno, refs):
    if not 'make' in data:
        return []
    makefile = data['make'].get('makefile')
    fullmakefile = checkPath(filepath, makefile, "Makefile") if makefile else makefile
    filedir = dirname(data['file']) if 'file' in data else filepath
    cwd = data['make'].get('cwd', filedir)

    cmd = ['make']
    if fullmakefile:
        cmd += ['-f', fullmakefile]
    if cwd:
        cmd += ['-C', checkPath(filepath, cwd, "CWD")]
    if target := data['make'].get('target'):
        cmd += [target]

    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        sys.stdout.buffer.write(res.stdout)
        sys.stdout.flush()
        sys.stderr.buffer.write(res.stderr)
        sys.stderr.flush()
        raise RuntimeError(f'Error executing {res.args}')
    return [fullmakefile if fullmakefile else "Makefile"]

# endregion

# region Code syntax highlighting


def full_filepath(file, fpath):
    file = re.sub(r'\$(\w+)', lambda m: getenv(m.group(1)), file)
    file = re.sub(r'\$\{(\w+)\}', lambda m: getenv(m.group(1)), file)
    if file[0] != '/':
        file = path.dirname(fpath) + '/' + file
    return file


def clip_file_contents(file, startline, endline):
    startline = 1 if startline is None else startline
    emptylines = 0
    nonemptylineencountered = False
    filecontents = ""

    with open(file) as f:
        for i, line in enumerate(f):
            if i >= (startline - 1):
                filecontents += line
                if not nonemptylineencountered and line == '\n':
                    emptylines += 1
                else:
                    nonemptylineencountered = True
            if endline is not None and i >= (endline - 1):
                break

    ctrstart = emptylines + startline - 1
    return filecontents, ctrstart


def formatPygmentsCodeSnippet(data: dict, html, filepath, lineno, refs):
    makedeps = handleMake(data, html, filepath, lineno, refs)
    startline = data.get('startline', None)
    endline = data.get('endline', None)
    name = data.get('name', None)
    file = full_filepath(data['file'], filepath)

    # Get the GitHub/GitLab links for this file
    if data.get('gitlink', True):
        git_service, git_link = get_git_remote_link(file, startline, endline)
    else:
        git_service = git_link = None

    # Select the lines between startline and endline
    filecontents, ctrstart = clip_file_contents(file, startline, endline)
    if 'display_startline' in data:
        ctrstart = int(data['display_startline']) - 1

    # Select the right lexer based on the filename and contents
    if 'lexer' in data:
        lexer = find_lexer_class_by_name(data['lexer'])()
    else:
        lex_filename = path.basename(file)
        if lex_filename == 'CMakeLists.txt':
            lex_filename += '.cmake'
        lexer = guess_lexer_for_filename(lex_filename, filecontents)

    # Select the right formatter based on the lexer
    cssclass = 'pygments{}'.format(lineno)
    if lexer.name == "Arduino" and not "style" in data:
        formatter = HtmlFormatter(cssclass=cssclass, style='arduino')
    else:
        style = data.get('style', VSCodeStyle)
        formatter = HtmlFormatter(cssclass=cssclass, style=style)

    # Extract the CSS from the formatter, and set the line number offset
    css = formatter.get_style_defs('.' + cssclass)
    css += '\n.pygments{} pre.snippet{} {{ counter-reset: line {}; }}' \
        .format(lineno, lineno, ctrstart)

    # Syntax highlight the code
    htmlc = highlight(filecontents, lexer, formatter)

    # Set the right classes
    clslinenos = "lineNumbers" if data.get('lineno', True) else "noLineNumbers"
    htmlc = htmlc.replace('<pre>',
                          f'<pre class="{clslinenos} snippet{lineno}">')
    htmlc = htmlc.replace('\n</pre></div>', '</pre></div>')

    # Construct the final HTML code
    datastr = ''
    if name is not None:
        datastr += '<h4 class="snippet-name">' + name + '</h4>\n'
    datastr += '<div class="codesnippet"><style>' + css + '</style>\n'
    if git_link is not None and git_service == 'github':
        datastr += '<a href="' + git_link + '" title="Open on GitHub">'
        datastr += '<img class="github-mark" src="/Images/GitHub-Mark.svg"/>'
        datastr += '</a>\n'
    if git_link is not None and git_service == 'gitlab':
        datastr += '<a href="' + git_link + '" title="Open on GitLab">'
        datastr += '<img class="gitlab-mark" src="/Images/GitLab-Mark.svg"/>'
        datastr += '</a>\n'
    datastr += htmlc + '</div>'
    return datastr, makedeps + [file]


# endregion

# region Image linking


def formatImage(data, html, filepath, lineno, refs: dict):
    makedeps = handleMake(data, html, filepath, lineno, refs)
    file = data['file']
    # file = re.sub(r'\$(\w+)', lambda m: getenv(m.group(1)), file)
    if path.isabs(file):
        raise Exception(f'Image file "{file}" cannot be an absolute path')
    fullfile = path.join(path.dirname(filepath), file)
    if not exists(fullfile):
        raise Exception(f'Image file "{fullfile}" does not exist')

    dispfile = data.get('display-file', file)
    if path.isabs(dispfile):
        raise Exception(f'Image file "{dispfile}" cannot be an absolute path')
    fulldispfile = path.join(path.dirname(filepath), dispfile)
    if not exists(fulldispfile):
        raise Exception(f'Image file "{fulldispfile}" does not exist')

    alt = data.get('alt', data.get('caption', file))

    def handle_attr(jsonkey, htmlstr):
        if jsonkey in data:
            for attr, value in data[jsonkey].items():
                escvalue = value.replace('"','\\"')
                htmlstr += f' {attr}="{escvalue}"'
        return htmlstr

    anchor = None
    if 'label' in data:
        count = len(refs['Figure']) + 1 if 'Figure' in refs else 1
        anchor = f'fig-{count}'
        figs = refs.setdefault('Figure', dict())
        label = data['label']
        if label in figs:
            raise Exception(f'Duplicate label "{label}"')
        figs[label] = (anchor, count)
        if 'caption' in data:
            data['caption'] = f'Figure {count}: ' + data['caption']
        else:
            data['caption'] = f'Figure {count}'

    htmlstr = f'<div class="img-wrapper"><a href="{file}"'
    htmlstr = handle_attr('a-attr', htmlstr)
    if anchor is not None:
        htmlstr += f' id="{anchor}"'
    htmlstr += f'><img src="{dispfile}" alt="{alt}"'
    htmlstr = handle_attr('img-attr', htmlstr)
    htmlstr += '/></a>'

    src = data.get('source')
    if src:
        if path.isabs(src):
            raise Exception(f'Image source "{src}" cannot be an absolute path')
        fullsrc = path.join(path.dirname(filepath), src)
        if not exists(fullsrc):
            raise Exception(f'Image source "{fullsrc}" does not exist')
        htmlstr += '<small class="image-code-link">'
        htmlstr += f'<a href="{src}">Image source code</a></small>'

    
    cap = data.get('caption')
    if cap:
        htmlstr += f'<figcaption'
        htmlstr = handle_attr('figcaption-attr', htmlstr)
        htmlstr += f'>{cap}</figcaption>'

    htmlstr += '</div>'

    return htmlstr, makedeps + [fullfile, fulldispfile]


# endregion

latexmakefiletemplate = """
.PHONY: all
all: {name}.svg

{name}.pdf: {name}.tex
	pdflatex --interaction=batchmode {name}.tex

build/{name}-fonts.pdf: {name}.pdf
	mkdir -p build
	gs -dNoOutputFonts -sDEVICE=pdfwrite -o build/{name}-fonts.pdf {name}.pdf

{name}.svg: build/{name}-fonts.pdf 
	inkscape build/{name}-fonts.pdf -l {name}.svg
"""

def handleLaTeX(data: dict, html, filepath, lineno, refs):
    file = data['file']
    fullfile = checkPath(filepath, file, "LaTeX file")
    fullfiledir = dirname(fullfile)
    filedir = dirname(file)
    filename = basename(file)
    name, ext = splitext(filename)
    if ext != '.tex': 
        raise Exception(f'Invalid LaTeX extension "{ext}"')
    if (not 'make' in data) or (not 'makefile' in data['make']):
        makefile = join(filedir, 'Makefile')
        if not 'make' in data: data['make'] = dict()
        data['make']['makefile'] = makefile
        fullmakefile = join(fullfiledir, 'Makefile')
        if not path.exists(makefile):
            makefilecontents = latexmakefiletemplate.format(name=name)
            with open(fullmakefile, 'w') as f: f.write(makefilecontents)
    data.setdefault('source', file)
    data['file'] = join(filedir, name + '.pdf')
    data.setdefault('display-file', join(filedir, name + '.svg'))
    return formatImage(data, html, filepath, lineno, refs)

def handleInclude(data: dict, html, filepath, lineno, refs):
    file = data['file']
    fullfile = checkPath(filepath, file, "Included file")
    makedeps = handleMake(data, html, filepath, lineno, refs)
    with open(fullfile, 'r') as f:
        contents = f.read()
    return contents, makedeps + [fullfile]

def handleReference(data, html, filepath, lineno, refs):
    label = data['ref']
    reftype = None
    ref = None
    for k, v in refs.items(): 
        if label in v:
            ref = v[label]
            reftype = k
    if ref is None:
        raise Exception(f'Invalid reference "{label}"')
    reflabel, refidx = ref
    htmlstr = f'<a class="pages-xref" href="#{reflabel}">{reftype}&nbsp;{refidx}</a>'
    return htmlstr, []

# region Replace @ JSON tags


def getlinenumber(string: str, index: int) -> int:
    return string.count('\n', 0, index)


def getlinesbetween(string: str, startindex: int, endindex: int) -> int:
    return string.count('\n', startindex, endindex)


def getlines(string: str) -> int:
    return string.count('\n')


def getKeyWord(keywords: dict, html, index):
    for kw in keywords.keys():
        if kw + '{' == html[index:index + len(kw) + 1]:
            return kw
    return None


def replaceTags(html, filepath, lineno, outpath, metadata):
    keywordhandlers = [
        {
            'codesnippet': formatPygmentsCodeSnippet,
            'image': formatImage,
            'latex': handleLaTeX,
            'include': handleInclude,
        },
        {
            'ref': handleReference,
        }
    ]

    refs = dict()
    deps = set()
    for pass_, handlers in enumerate(keywordhandlers):
        index = html.find('@')
        while index >= 0:
            keyword = getKeyWord(handlers, html, index + 1)
            if not keyword:
                index = html.find('@', index + 1)
                continue
            try:
                jsonstartindex = index + len(keyword) + 1
                data, endindex = JSONDecoder().raw_decode(html, jsonstartindex)
                handler = handlers[keyword]
                taglineno = lineno + getlinenumber(html, index)
                newdata, dep = handler(data, html, filepath, taglineno, refs)
                if dep: deps.update(dep)
                lineno += getlinesbetween(html, index, endindex)
                lineno -= getlines(newdata)
                html = html[:index] + newdata + html[endindex:]
                index = html.find('@', index + len(newdata))
            except Exception as e:
                fileline = filepath + ':' + str(lineno +
                                                getlinenumber(html, index))
                print('\nError processing tag:', file=sys.stderr)
                print(fileline, file=sys.stderr)
                print(type(e).__name__, file=sys.stderr)
                print(e, file=sys.stderr)
                print(file=sys.stderr)
                raise e
    if deps:
        depfname = path.splitext(outpath)[0] + '.dep'
        with open(depfname, 'w') as f:
            f.write('\n'.join(sorted(deps)))
    return html


# endregion


def formatHTML(html, filepath, lineno, outpath, metadata):
    html = replaceTags(html, filepath, lineno, outpath, metadata)
    html = formatCode(html, metadata)
    html = addAnchors(html, metadata)
    return html