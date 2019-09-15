import re
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
from json import JSONDecoder
from pprint import pformat
from os import getenv

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

def formatPygmentsCode(html, path):
    keyword = '@codesnippet{'
    index = html.find(keyword)
    while index >= 0:
        data, endindex = JSONDecoder().raw_decode(html, index + len(keyword)-1)
        startline = data.get('startline', 1)
        endline = data.get('endline')
        file = data['file']
        file = re.sub(r'\$(\w+)', lambda m: getenv(m.group(1)), file)
        if file[0] != '/':
            file = path + '/' + file

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

        lexer = guess_lexer_for_filename(file, filecontents)
        formatter = HtmlFormatter(cssclass='pygments')
        css = formatter.get_style_defs('.pygments')
        ctrstart = emptylines + startline - 1
        css += '.pygments pre.snippet{} {{ counter-reset: line {}; }}' \
            .format(index, ctrstart)
        htmlc = highlight(filecontents, lexer, formatter)
        htmlc = htmlc.replace('<pre>', 
                    '<pre class="lineNumbers snippet{}">'.format(index))
        htmlc = htmlc.replace('\n</pre></div>', '</pre></div>')
        datastr = '<div><style>' + css + '</style>'
        datastr += formatCode(htmlc)
        html = html[:index] + datastr + html[endindex:] + '</div>'
        index = html.find(keyword, index + len(datastr))
    return html
    

def formatHTML(html, path):
    html = formatCode(html)
    html = addAnchors(html)
    html = formatPygmentsCode(html, path)
    return html