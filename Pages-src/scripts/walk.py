#!/usr/bin/python3

import os, re, time, shutil
from os.path import join, getsize, normpath, basename
from HTMLGenerator import *

script_dir = os.path.dirname(os.path.realpath(__file__))
raw_html_dir = normpath(join(script_dir, '../Raw-HTML'))
html_dir = normpath(join(script_dir, '../../Pages'))
    
def main():
    shutil.rmtree(html_dir)
    os.makedirs(html_dir, exist_ok=False)
    for root, dirs, files in os.walk(raw_html_dir):
        dirs = sorted(dirs)
        files = sorted(files)
        relativePath = os.path.relpath(root, raw_html_dir)
        '''print(relativePath)
        print("Directories:")
        print("\t"+str(dirs))
        print("Files:")
        print("\t"+str(files))
        print()'''
        for d in dirs:
            os.makedirs(join(html_dir, relativePath, d), exist_ok=True)
        if basename(normpath(root)) == "images":
            for f in files:
                shutil.copy2(join(root,f), join(html_dir, relativePath))

        else:
            if not "index.html" in files:
                createAutomaticIndexPage(root)

            for f in files:
                raw_html_path = join(root, f)
                full_html_path = join(html_dir, relativePath, f)
                with open(full_html_path, "w") as full_html_file:
                    if f == "index.html":
                        full_html = createIndexPage(raw_html_path, root)
                    else:
                        full_html = rawToFull(raw_html_path)    
                    full_html_file.write(full_html)

if __name__=="__main__":
   main()
    