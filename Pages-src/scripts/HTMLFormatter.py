import re
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
from json import JSONDecoder
from pprint import pformat
from os import getenv
from os import path
from os.path import exists, splitext
import sys

def format_anchor_name(match, anchors):
    tag = match.group(1)
    fullname = match.group(2)
    name = fullname
    name = name.lower()                       # To lowercase
    name = re.sub(r"&(?:[a-z\d]+|#\d+|#x[a-f\d]+);", r"-", name)     # Replace HTML entities with '-'
    
    name = re.sub(r"(<|</)([^<>])+>", r"", name)      # Leave out HTML tags
    name = re.sub(r"[^a-z\d]", r"-", name)    # Only alphanumeric lowercase, replace everything else with '-'
    name = re.sub(r"-+", r"-", name)          # More than one '-' replaced with single '-'
    name = re.sub(r"/^-|-$", r"", name)       # Strip '-' from the start or end of the string

    # Don't allow duplicate IDs, so add a number at the end to make it unique
    i = 1
    newname = name
    while newname in anchors:
        newname = name + str(i)
        i += 1
    anchors.add(newname)

    return "<h"+tag+"><a name=\"" + newname \
         + "\" href=\"#" + newname \
         + "\">"+fullname+"</a></h" + tag + ">"

def addAnchors(html):
    anchors = set()
    html = re.sub(r"<h([1-6])>(((?!<a).)+)</h\1>", \
                  lambda match: format_anchor_name(match, anchors), \
                  html)
    return html

def addCodeLines(match):
    pre = match.group(1)
    pre = re.sub(r"(<pre.*?>)(?:\r\n|\n)*", r"\g<1><code>", pre)
    pre = re.sub(r"\r\n|\n", r"</code>\g<0><code>", pre)
    pre = re.sub(r"</pre>", r"</code></pre>", pre)
    return pre

def addLineNumbersEmphasis(match):
    pre = match.group(1)
    pre = re.sub(r"(<pre.*?>)(?:\r\n|\n)*", r"\g<1><code>", pre)
    pre = re.sub(r"\r\n|\n",r"</code>\g<0><code>", pre)
    pre = re.sub(r"</pre>", r"</code></pre>", pre)
    pre = re.sub(r"<code>\*\*\*", r'<code class="emphasis">', pre)
    return pre

def formatCode(html):
    findPre = r"(<pre[^>]* class=\"lineNumbers[^>]*>((?!<pre).|\r\n|\n)*</pre>)"
    findPreEmph = r"(<pre[^>]* class=\"lineNumbersEmphasis[^>]*>((?!<pre).|\r\n|\n)*</pre>)"

    html = re.sub(findPre, addCodeLines, html)
    html = re.sub(findPreEmph, addLineNumbersEmphasis, html)

    # Arduino IDE export HTML doesn't encode HTML entities
    html = re.sub(r">&<", r">&amp;<", html)
    html = re.sub(r">&=<", r">&amp;=<", html)

    return html

def getlinenumber(string: str, index: int) -> int:
    return string.count('\n', 0, index)

def getlinesbetween(string: str, startindex: int, endindex: int) -> int:
    return string.count('\n', startindex, endindex)

def getlines(string: str) -> int:
    return string.count('\n')

def formatPygmentsCodeSnippet(data, html, filepath, lineno):
    startline = data.get('startline', 1)
    endline = data.get('endline')
    file = data['file']
    file = re.sub(r'\$(\w+)', lambda m: getenv(m.group(1)), file)
    file = re.sub(r'\$\{(\w+)\}', lambda m: getenv(m.group(1)), file)
    if file[0] != '/':
        file = path.dirname(filepath) + '/' + file

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

    lex_filename = path.basename(file)
    if lex_filename == 'CMakeLists.txt':
        lex_filename += '.cmake'
    lexer = guess_lexer_for_filename(lex_filename, filecontents)
    cssclass = 'pygments{}'.format(lineno)
    if lexer.name == "Arduino":
        formatter = HtmlFormatter(cssclass=cssclass, style='arduino')
    else:
        formatter = HtmlFormatter(cssclass=cssclass, style='default')
    css = formatter.get_style_defs('.' + cssclass)
    ctrstart = emptylines + startline - 1
    css += '\n.pygments{} pre.snippet{} {{ counter-reset: line {}; }}' \
        .format(lineno, lineno, ctrstart)
    htmlc = highlight(filecontents, lexer, formatter)
    htmlc = htmlc.replace('<pre>', 
                '<pre class="lineNumbers snippet{}">'.format(lineno))
    htmlc = htmlc.replace('\n</pre></div>', '</pre></div>')
    datastr = '<div class="codesnippet"><style>' + css + '</style>'
    datastr += htmlc + '</div>'
    return datastr, file

def formatImage(data, html, filepath, lineno):
    file = data['file']
    # file = re.sub(r'\$(\w+)', lambda m: getenv(m.group(1)), file)
    if file[0] != '/': 
        fullfile = path.dirname(filepath) + '/' + file
    else:
        raise Exception('Image file "' + file + '" is an absolute path')
    if not exists(fullfile):
        raise Exception('Image file "' + fullfile + '" does not exist')

    displayfile = data.get('display-file', file)
    # file = re.sub(r'\$(\w+)', lambda m: getenv(m.group(1)), file)
    if displayfile[0] != '/': 
        fulldisplayfile = path.dirname(filepath) + '/' + displayfile
    else: 
        raise Exception('Image file "' + displayfile + '" is an absolute path')
    if not exists(fulldisplayfile):
        raise Exception('Image file "' + fulldisplayfile + '" does not exist')

    alt = data.get('alt', data.get('caption', file))

    htmlstr = '<a href="{src}"><img src="{dispsrc}" alt="{alt}"/></a>' \
        .format(src=file, dispsrc=displayfile, alt=alt)
        
    cap = data.get('caption')
    if cap:
        htmlstr += '<figcaption>' + cap + '</figcaption>'

    return htmlstr, fullfile

def getKeyWord(keywords: dict, html, index):
    for kw in keywords.keys():
        if kw + '{' == html[index:index + len(kw) + 1]:
            return kw
    return None

def replaceTags(html, filepath, lineno, outpath):
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
            fileline = filepath + ':' + str(lineno + getlinenumber(html, index))
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

def formatHTML(html, filepath, lineno, outpath):
    html = replaceTags(html, filepath, lineno, outpath)
    html = formatCode(html)
    html = addAnchors(html)
    return html