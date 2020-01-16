#!/usr/bin/python3

import os
import shutil
from os.path import join, realpath, normpath, splitext, relpath, dirname, basename
import sys
import re
import subprocess

script_dir = dirname(realpath(__file__))
root_dir = dirname(script_dir)
html_dir = join(script_dir, "Doc/Doxygen")
new_rel_html_dir = 'Control-Surface-doc/docs/Doxygen'
new_html_dir = join(dirname(root_dir), new_rel_html_dir)
print(new_html_dir)


def search_file(searchname):
    return [line[2:] for line in \
        subprocess.check_output(f"find . -name '{searchname}'",
                                shell=True,
                                cwd=new_html_dir).splitlines()]


def search(rel):
    searchname = re.sub(r'^[a-f\d/]*/', '', rel)
    print('   ->', searchname)
    paths = search_file(searchname)
    if len(paths) == 1:
        return paths[0].decode('utf-8')
    searchname = re.sub(r'^class', 'classAH_1_1', searchname)
    searchname = re.sub(r'^struct', 'structAH_1_1', searchname)
    paths = search_file(searchname)
    if len(paths) == 1:
        return paths[0].decode('utf-8')
    return None


def add_link(file, new_path):
    with open(file, 'r+') as f:
        content = f.read()
        f.seek(0)
        top = '<div id="top"><!-- do not remove this div, it is closed by doxygen! -->'
        link = join('/Control-Surface-doc/Doxygen', new_path)
        new_top = top + f'\n<div id="new-version">This is an old version of the documentation. View the latest version <a href="{link}">here</a>.</div>'
        content = content.replace(top, new_top)
        f.write(content)
        f.truncate()


for root, dirs, files in os.walk(html_dir):
    if (basename(root) == 'search'):
        continue
    for f in files:
        name, ext = splitext(f)
        if ext == '.html':
            new_path = relpath(normpath(join(root, f)), normpath(html_dir))
            if (not os.path.exists(join(new_html_dir, new_path))):
                new_path = search(new_path)
            if new_path is not None:
                print(new_path)
                add_link(join(root, f), new_path)
            else:
                print('X <-')
                add_link(join(root, f), 'index.html')
