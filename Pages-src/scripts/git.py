from subprocess import check_output, CalledProcessError
from os.path import dirname, relpath
import re

def get_git_remote_link(file, startline, endline):
    """
    E.g. https://github.com/tttapa/RPi-Cpp-Toolchain/blob/acd5b556709de02fa2de5f0cd05e5d24be6f7768/applications/hello-world/hello-world.cpp#L1-L3
    """

    # First check if the directory is in a Git repository
    directory = dirname(file)
    try:
        git_dir = check_output(["git", "rev-parse", "--show-toplevel"], 
                               cwd=directory)
    except CalledProcessError:
        return None, None
    
    # Get the relative path of the file, relative to the toplevel git folder
    git_dir = git_dir.decode('utf-8').strip()
    rel = relpath(file, git_dir)

    # Get the hash of the latest commit
    commit = check_output(["git", "rev-list", "-1", "HEAD", "--", rel],
                          cwd=git_dir)
    commit = commit.decode('utf-8').strip()
    if commit == '':
        commit = 'master'

    # Get the remote of the repository
    remote = check_output(["git", "remote", "get-url", "origin"],
                          cwd=directory)
    remote = remote.decode('utf-8').strip()
    if m := re.match(r'^\w+@([\w.]+):([\w/.-]+)$', remote): # if SSH URL
        remote = 'https://' + m.group(1) + '/' + m.group(2)
    if m := re.match(r'^(.*)\.git$', remote): # Remove .git suffix
        remote = m.group(1)
    m = re.match(r'^https://(\w+)\..+$', remote)
    if m is None:
        print("Warning: unknown Git remote: " + remote)
        return None, None
    service = m.group(1)
    
    if remote == 'https://github.com/tttapa/tttapa.github.io':
        commit = 'master'

    # Append the commit hash and file path
    remote += '/' + 'blob' + '/' + commit + '/' + rel

    # Add the line numbers
    if startline is not None:
        remote += '#L' + str(startline)
        if endline is not None:
            if service == 'github':
                remote += '-L' + str(endline)
            else:
                remote += '-' + str(endline)
    else:
        if endline is not None:
            if service == 'github':
                remote += '#L1-L' + str(endline)
            else:
                remote += '#L1-' + str(endline)

    return service, remote