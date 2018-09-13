#!/usr/bin/python3

import os, re, time, shutil
from os.path import join, getsize, normpath, basename, splitext, relpath
from HTMLGenerator import *
from subprocess import run, Popen, check_output
import sys

port = 4654

script_dir = os.path.dirname(os.path.realpath(__file__))
raw_html_dir = normpath(join(script_dir, '../Raw-HTML'))
root_dir = normpath(join(script_dir, '../..'))
html_dir = normpath(join(root_dir, 'Pages'))

def exportPDF(html_path):
    pdf_path = splitext(html_path)[0] + '.pdf'
    html_uri = 'http://127.0.0.1:{}/{}'.format(port, relpath(html_path, root_dir))
    options = ['google-chrome', '--headless', '--print-to-pdf='+pdf_path, html_uri]
    print(options)
    run(options)
    os.chmod(pdf_path, 0o664)

class Server:
    def __init__(self, directory, address, port):
            cwd = os.getcwd()
            os.chdir(directory)
            self.process = Popen([sys.executable, '-m', 'http.server', str(port), '--bind', str(address)])
            time.sleep(0.100)
            os.chdir(cwd)
    
    def __exit__(self, type, value, traceback):
        self.process.terminate()

    def __enter__(self):
        return self

    
def main(print_to_pdf):
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

    for root, dirs, files in os.walk(raw_html_dir):
        dirs = sorted(dirs)
        files = sorted(files)
        relativePath = os.path.relpath(root, raw_html_dir)
        if basename(normpath(root)) != "images":
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
                    if print_to_pdf:
                        full_html = check_output(
                            ["mjpage", '--output=CommonHTML', "--eqno=AMS",
                            '--fontURL=/MathJax/fonts/HTML-CSS'],
                            timeout=10, input=bytes(full_html, 'utf-8')
                        ).decode('utf-8')
                    full_html_file.write(full_html)
                    if print_to_pdf:
                        exportPDF(full_html_path)

if __name__=="__main__":
    if len(sys.argv) > 1 and "pdf" in sys.argv:
        with Server(root_dir, '127.0.0.1', port) as server:
            main(True)
    else:
        main(False)
    