import os, re, time, HTMLFormatter
from os.path import join, getsize, basename, normpath, splitext
from warnings import warn

from walk import html_dir, raw_html_dir, script_dir

template_dir = join(script_dir, "../templates")

author = "Pieter P"
timeformat = "%A, %d %B %Y %H:%M"

meta_keys = None
template_keys = None
template_index_keys = None
template_index_item_keys = None

template_meta = ""
template = ""
template_index = ""
template_index_item = ""

with open(join(template_dir, "template_meta.html"), "r") as template_meta_file:
    template_meta = template_meta_file.read()
    m = re.finditer(r":(\w+):", template_meta, re.IGNORECASE)
    meta_keys = list(map(lambda m: m.group(1), m))

with open(join(template_dir, "template.html"), "r") as template_file:
    template = template_file.read()
    m = re.finditer(r":(\w+):", template, re.IGNORECASE)
    template_keys = list(map(lambda m: m.group(1), m))

with open(join(template_dir, "template_index.html"), "r") as template_index_file:
    template_index = template_index_file.read()
    m = re.finditer(r":(\w+):", template_index, re.IGNORECASE)
    template_index_keys = list(map(lambda m: m.group(1), m))

with open(join(template_dir, "template_index_item.html"), "r") as template_index_item_file:
    template_index_item = template_index_item_file.read()
    m = re.finditer(r":(\w+):", template_index_item, re.IGNORECASE)
    template_index_item_keys = list(map(lambda m: m.group(1), m))

#########################################################################################

def sortDirEntries(it):
    entries = sorted(list(it),key=lambda entry: (entry.is_file(), entry.name))
    # entries = sorted(list(it),key=lambda entry: entry.name)
    # swapped = True
    # while swapped:
    #     swapped = False
    #     for i in range(len(entries)-1):
    #         if entries[i].is_file() and not entries[i+1].is_file():
    #             swapped = True
    #             entries[i], entries[i+1] = entries[i+1], entries[i]
    return entries

def escapeBackSlashes(string):
    return string.replace("\\", "\\\\")

#########################################################################################

def getDocumentProperties(content):
    properties = dict()
    for key in meta_keys:
        m = re.search(r"<!--[\s\S]*@" + key + r":\s*(.*)[\s\S]*-->", content)
        if m:
            properties[key] = m.group(1)
    return properties

def getDocumentHTMLContent(content):
    m = re.search(r"<html>([\s\S]*)</html>", content, re.IGNORECASE)
    if m:
        # print(m.group(1))
        return HTMLFormatter.formatHTML(str(m.group(1)))
    else:
        return ""

def getDocumentMDate(path):
    mdate_time = time.gmtime(os.path.getmtime(path))
    mdate_str = time.strftime(timeformat, mdate_time)
    return mdate_str

def getTemplateValues(path):
    raw_content = ""
    with open(path, "r") as f:
        raw_content = f.read()

    values = getDocumentProperties(raw_content)
    values["nav"] =  createNavIndex(path, raw_html_dir)
    values["mdate"] = getDocumentMDate(path)
    values["html"] = getDocumentHTMLContent(raw_content)
    # print(values["html"])

    return values

def getTitle(path):
    if os.path.isdir(path):
        path = join(path, "index.html")
    raw_content = ""
    try:
        with open(path, "r") as f:
            raw_content = f.read()
        m = re.search(r"<!--[\s\S]*@title:\s*(.*)[\s\S]*-->", raw_content)
        if m:
            return m.group(1)
        else:
            return None
    except:
        return None

#########################################################################################

def createIndexPageListItem(path, filename, link):
    # print("\t"+join(path, filename))
    try:
        raw_content = ""
        with open(join(path, filename), "r") as raw_file:
            raw_content = raw_file.read()

        properties = getDocumentProperties(raw_content)
    except:
        # warn("No index.html for " + path)
        # print("Warning: No index.html for " + os.path.abspath(path))
        properties = dict()
        properties["title"] = link

    properties["link"] = link
    # print("\t"+str(properties))
    
    index_item = template_index_item

    for key in template_index_item_keys:
        index_item = re.sub(r":"+key+r":", escapeBackSlashes(properties.get(key, "")), index_item)
    
    return index_item

def createIndexPageList(path):
    it = os.scandir(path)
    entries = sortDirEntries(it)
    index = ""
    for entry in entries:
        if isFolderToIgnore(entry):
            continue
        if not entry.is_file():
            index += createIndexPageListItem(join(path, entry.name), "index.html", entry.name)
        elif entry.name != "index.html":
            index += createIndexPageListItem(path, entry.name, entry.name)
    '''print(path)
    print(index)
    print()'''
    return index

#########################################################################################

def rawToFull(path):
    values = getTemplateValues(path)
    values['filenamepdf'] = splitext(basename(path))[0] + '.pdf'

    content = template

    for key in template_keys:
        content = re.sub(r":"+key+r":", escapeBackSlashes(values.get(key,"")), content)

    return content

def createIndexPage(path, root):
    values = getTemplateValues(path)
        
    values["index"] = createIndexPageList(root)
    values['filenamepdf'] = 'index.pdf'

    content = template_index

    for key in template_index_keys:
        content = re.sub(r":"+key+r":", escapeBackSlashes(values.get(key,"")), content)
    # print(content)
    return content

def createAutomaticIndexPage(root):
    # warn("No index.html for " + path)
    print("Warning: No index.html for " + os.path.abspath(root))

    meta = dict()
    meta["title"] = basename(root)
    meta["author"] = author

    content = template_meta

    for key in template_index_keys:
        content = re.sub(r":"+key+r":", escapeBackSlashes(meta.get(key,"")), content)

    with open(join(root, "index.html"), "w") as raw_index_file:
        raw_index_file.write(content)

#########################################################################################

def createNavIndex(open_directory, directory):
    nav = addListEntries(open_directory, directory)
    return nav

def addListEntries(open_directory, directory, level=1, link="/Pages"):
    it = os.scandir(directory)
    entries = sortDirEntries(it)
    '''
    for entry in entries:
        filetype = "F" if entry.is_file() else "D"
        print("  "*(level-1) + entry.name + " " + filetype)
        print("  "*(level-1) + directory)
        rel = os.path.relpath(open_directory, join(directory, entry.name))
        collapse = not ".." in rel
        print("  "*(level-1) + rel)
        print("  "*(level-1) + str(collapse))
        print()
    '''
    listStr = "  "*(level-1) + "<ul>\r\n"
    for entry in entries:
        newlink = join(link, entry.name)
        name = getTitle(join(directory, entry.name))
        if name is None:
            name = entry.name
        rel = os.path.relpath(open_directory, join(directory, entry.name))
        open_entry = " class=\"openEntry\"" if rel == "." or rel == "index.html" else ""
        if not entry.name.startswith('.') and entry.name != "index.html" and entry.is_file():
            listStr += "  "*level + "<li><span class=\"ftriangle\"></span><a"+open_entry+" href=\"" + newlink + "\">" + name + "</a></li>\r\n"
        elif not entry.is_file() and not isFolderToIgnore(entry):
            collapse = ".." in rel
            expanded = "" if collapse else " class=\"expanded\""
            triangle  = "<span class=\"dtriangle\" onclick=\"this.parentElement.classList.toggle('expanded');\">"
            triangle += "" # "▶" if collapse else "◢"
            triangle += "</span>"
            listStr += "  "*level + "<li" + expanded + ">"+triangle+"<a"+open_entry+" href=\"" + newlink + "\">" + name + "</a>\r\n" + \
                       addListEntries(open_directory, join(directory, entry.name), level + 1, newlink) + \
                       "  "*level + "</li>\r\n"
    listStr += "  "*(level-1) + "</ul>\r\n"
    return listStr

def isFolderToIgnore(dirEntry):
    name =  dirEntry.name
    return name == "images" or name.startswith(".")