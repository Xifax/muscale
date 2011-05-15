# -*- coding: utf-8 -*-
__author__ = 'Robin Parmar, Yadavito'

# internal #
import os
import fnmatch

def walk_ignore(root, ignore):
    for path, subdirs, files in os.walk(root):
        subdirs[:] = [
            d for d in subdirs
            if d not in ignore ]
        files[:] = [
            f for f in files
            if f not in ignore ]
        yield path, subdirs, files

def walk_path(root='.', recurse=True, pattern='*', ignore=None):
    """
        Generator for walking a directory tree.
        Starts at specified root folder, returning files
        that match our pattern. Optionally will also
        recurse through sub-folders.
    """
    if ignore is None:
        ignore = []
    for path, subdirs, files in walk_ignore(root, ignore):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                yield os.path.join(path, name)
        if not recurse:
            break

def lines_of_code(root='', ignore=None, recurse=True):
    """
        Counts lines of code in two ways:
            maximal size (source LOC) with blank lines and comments
            minimal size (logical LOC) stripping same

        Sums all Python files in the specified folder.
        By default recurses through subfolders.
    """
    if ignore is None:
        ignore = []
    count_mini, count_maxi = 0, 0
    for the_file in walk_path(root, recurse, '*.py', ignore):
        skip = False
        for line in open(the_file).readlines():
            count_maxi += 1

            line = line.strip()
            if line:
                if line.startswith('#'):
                    continue
                if line.startswith('"""'):
                    skip = not skip
                    continue
                if line.startswith("'''"):
                    skip = not skip
                    continue
                if not skip:
                    count_mini += 1

    return count_mini, count_maxi

def show_results():
    ignore_list = ['pyqtgraph', 'usr', 'pyper.py']
    loc_result = lines_of_code('../', ignore_list)
    
    print 'Excluded modules: ' + ', '.join(ignore_list)
    print 'LOC (with blanks and comments): ', loc_result[1]
    print 'LOC (code only): ', loc_result[0]

if __name__ == '__main__':
    show_results()
