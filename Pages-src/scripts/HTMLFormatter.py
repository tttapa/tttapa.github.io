import re

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
    findPre = r"(<pre[^>]* class=\"lineNumbers\"[^>]*>((?!<pre).|\r\n|\n)*</pre>)"
    findPreEmph = r"(<pre[^>]* class=\"lineNumbersEmphasis\"[^>]*>((?!<pre).|\r\n|\n)*</pre>)"

    html = re.sub(findPre, addCodeLines, html)
    html = re.sub(findPreEmph, addLineNumbersEmphasis, html)

    # Arduino IDE export HTML doesn't encode HTML entities
    html = re.sub(r">&<", r">&amp;<", html)
    html = re.sub(r">&=<", r">&amp;=<", html)

    return html

def formatHTML(html):
    html = formatCode(html)
    html = addAnchors(html)
    return html