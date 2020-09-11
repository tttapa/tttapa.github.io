#!/usr/bin/env python3

"""
Reads the "Last edited" time from the pages in the Pages directory, and updates
the modification times of the corresponding files in Pages-src.

Useful after downloading the repo to a new computer, since Git doesn't preserve
modification times of files.

WARNING: Rewrites history!
"""

import os
from os.path import join, getsize, normpath, basename, splitext, relpath
import sys
import re
import dateutil.parser

script_dir = os.path.dirname(os.path.realpath(__file__))
pages_dir = normpath(join(script_dir, "../../Pages"))
src_dir = normpath(join(script_dir, "../Raw-HTML"))

def touch(fname, times=None):
    try:
        with open(fname, 'a'):
            os.utime(fname, times)
    except FileNotFoundError as e:
        print(e)

for root, dirs, files in os.walk(pages_dir):
    for f in files:
        name, ext = splitext(f)
        if ext == '.html' and not (name == 'index' and root == pages_dir):
            with open(join(root, f), 'r+') as file:
                pattern = r'<footer>Last edited: ([a-zA-Z0-9_:, ]+)</footer>'
                m = re.search(pattern, file.read())
                if m:
                    rel = join(relpath(root, pages_dir), f)
                    print(rel, name, m.group(1))
                    time = dateutil.parser.parse(m.group(1))
                    times = (time.timestamp(), time.timestamp())
                    touch(join(src_dir, rel), times)
