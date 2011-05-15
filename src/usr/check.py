# -*- coding=utf-8 -*-
import sys

__author__ = 'Yadavito'

# internal #
import os
import sys

# external #
import pep8

# own #
from metrics import walk_path

def check(path, ignore=None, to_file=False):

    quite = '-qq'
    source = '--show-source'
    pep = '--show-pep8'
    rep = '--repeat'

    args = [rep]

    if ignore is None:
        ignore = []

    if to_file:
        out_file = './pep8.txt'
        if os.path.exists(out_file):
            os.remove(out_file)
        file_handle = open(out_file, 'a')

    files_count = 0

    for the_file in walk_path(path, recurse=True, pattern='*.py', ignore=ignore):
        arglist = args[:] + [the_file]
        pep8.process_options(arglist)
        try:
            pep8.input_file(the_file)
            error_stats = pep8.get_error_statistics()
            warning_stats = pep8.get_warning_statistics()

            if to_file:
                if warning_stats or error_stats:
                    file_handle.write('\n')
                file_handle.write(the_file)
                file_handle.write('\n')
                
                for warning in warning_stats:
                    file_handle.write("%s\n" % warning)
                for errors in error_stats:
                    file_handle.write("%s\n" % errors)

            files_count += 1
            sys.stdout.write('Processed %d file(s) \r' % files_count)

        except  Exception, e:
            pass

    if to_file:
        file_handle.close()

if __name__ == '__main__':
    ignore_list = ['pyqtgraph', 'usr', 'pyper.py']
    check('../', ignore_list, to_file=True)
    raw_input('\n\nAny key! Any key!')