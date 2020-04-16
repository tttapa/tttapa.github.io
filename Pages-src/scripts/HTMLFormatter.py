import re
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename, find_lexer_class_by_name
from json import JSONDecoder
from pprint import pformat
from os import getenv
from os import path
from os.path import exists, splitext, dirname, relpath
import sys

from git import get_git_remote_link

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

    toc = metadata.get('tableofcontents', 'false').lower()
    if not toc in ['true', '1', 't', 'y', 'yes']:
        return html

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
    current_level = min(map(lambda x: x[1], anchors.values()))
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
    while current_level > 1:
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


def formatPygmentsCodeSnippet(data: dict, html, filepath, lineno):
    startline = data.get('startline', None)
    endline = data.get('endline', None)
    name = data.get('name', None)
    file = full_filepath(data['file'], filepath)

    # Get the GitHub/GitLab links for this file
    git_service, git_link = get_git_remote_link(file, startline, endline)

    # Select the lines between startline and endline
    filecontents, ctrstart = clip_file_contents(file, startline, endline)

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
        style = data.get('style', 'default')
        formatter = HtmlFormatter(cssclass=cssclass, style=style)

    # Extract the CSS from the formatter, and set the line number offset
    css = formatter.get_style_defs('.' + cssclass)
    css += '\n.pygments{} pre.snippet{} {{ counter-reset: line {}; }}' \
        .format(lineno, lineno, ctrstart)

    # Syntax highlight the code
    htmlc = highlight(filecontents, lexer, formatter)

    # Set the right classes
    htmlc = htmlc.replace('<pre>',
                          '<pre class="lineNumbers snippet{}">'.format(lineno))
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
    return datastr, file


# endregion

# region Image linking


def formatImage(data, html, filepath, lineno):
    file = data['file']
    # file = re.sub(r'\$(\w+)', lambda m: getenv(m.group(1)), file)
    if file[0] != '/':
        fullfile = path.dirname(filepath) + '/' + file
    else:
        raise Exception('Image file "' + file + '" cannot be an absolute path')
    if not exists(fullfile):
        raise Exception('Image file "' + fullfile + '" does not exist')

    displayfile = data.get('display-file', file)
    # file = re.sub(r'\$(\w+)', lambda m: getenv(m.group(1)), file)
    if displayfile[0] != '/':
        fulldisplayfile = path.dirname(filepath) + '/' + displayfile
    else:
        raise Exception('Image file "' + displayfile +
                        '" cannot be an absolute path')
    if not exists(fulldisplayfile):
        raise Exception('Image file "' + fulldisplayfile + '" does not exist')

    alt = data.get('alt', data.get('caption', file))

    htmlstr = '<a href="{src}"><img src="{dispsrc}" alt="{alt}"/></a>' \
        .format(src=file, dispsrc=displayfile, alt=alt)

    cap = data.get('caption')
    if cap:
        htmlstr += '<figcaption>' + cap + '</figcaption>'

    return htmlstr, fullfile


# endregion

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
    keywordhandlers = {
        'codesnippet': formatPygmentsCodeSnippet,
        'image': formatImage,
    }

    deps = []
    index = html.find('@')
    while index >= 0:
        keyword = getKeyWord(keywordhandlers, html, index + 1)
        if not keyword:
            index = html.find('@', index + 1)
            continue
        try:
            jsonstartindex = index + len(keyword) + 1
            data, endindex = JSONDecoder().raw_decode(html, jsonstartindex)
            handler = keywordhandlers[keyword]
            taglineno = lineno + getlinenumber(html, index)
            newdata, dep = handler(data, html, filepath, taglineno)
            if dep: deps.append(dep)
            lineno += getlinesbetween(html, index, endindex)
            lineno -= getlines(newdata)
            html = html[:index] + newdata + html[endindex:]
            index = html.find('@', index + len(newdata))
        except Exception as e:
            fileline = filepath + ':' + str(lineno +
                                            getlinenumber(html, index))
            print('\nError adding code snippet:', file=sys.stderr)
            print(fileline, file=sys.stderr)
            print(type(e).__name__, file=sys.stderr)
            print(e, file=sys.stderr)
            print(file=sys.stderr)
            raise e
    if deps:
        depfname = path.splitext(outpath)[0] + '.dep'
        with open(depfname, 'w') as f:
            f.write('\n'.join(deps))
    return html


# endregion


def formatHTML(html, filepath, lineno, outpath, metadata):
    html = replaceTags(html, filepath, lineno, outpath, metadata)
    html = formatCode(html, metadata)
    html = addAnchors(html, metadata)
    return html