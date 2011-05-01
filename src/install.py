# -*- coding: utf-8 -*-
'''
Created on Mar 22, 2011

@author: Yadavito
'''

import sys, urllib, subprocess, os

def dlProgress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    sys.stdout.write("Download progress: %d%%   \r" % percent)
  
def downloadWithProgressbar(url):
    file_name = url.split('/')[-1]
    print 'Downloading ' + file_name
    urllib.urlretrieve(url, file_name, reporthook=dlProgress)
    return file_name

def download_and_install(file_url):
        file = downloadWithProgressbar(file_url)
        subprocess.call('./' + file)
        os.remove('./' + file)
try:
    from setuptools.command import easy_install
except ImportError:
    print 'Please, install easy_install!'
    if raw_input('Download setuptools now? [y/n]: ') == ('y' or 'Y'):
        download_and_install('http://pypi.python.org/packages/2.6/s/setuptools/setuptools-0.6c11.win32-py2.6.exe')
    else: sys.exit(0)

def install_with_easyinstall(package):
    try:
        __import__(package)
        in_system.append(package)
    except ImportError:
        print 'Installing ' + package
        try:
            easy_install.main(['-U', package])
            installed.append(package)
        except Exception:
            pass

if __name__ == '__main__':
    installed = []; in_system = []
    packages = ['pywt', 'flufl.enum', 'userconfig', 'numpy', 'scipy', 'matplotlib', 'simpledropbox']
    for package in packages:
        install_with_easyinstall(package)

    #TODO: convert links to tinyurl and move to constants
    # PyQt
    try:  import PyQt4
    except ImportError: download_and_install('http://cran.r-project.org/bin/windows/base/R-2.13.0-win.exe')

    # matplotlib
    try: import matplotlib
    except ImportError: download_and_install('http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.0.1/matplotlib-1.0.1.win32-py2.6.exe/download')
    
    # R
    if raw_input('Download and install R? [y/n]: ') == ('y' or 'Y'):
        download_and_install('http://www.riverbankcomputing.co.uk/static/Downloads/PyQt4/PyQt-Py2.6-x86-gpl-4.8.3-1.exe')

    print 'Install/Update complete. Status:\n'
    print '\n'.join(installed), '\n\n(total installed: ' + str(len(installed)) + ')\n'
    print '\n------------ # # # ------------\n'
    print '\n'.join(in_system), '\n\n(already in system: ' + str(len(in_system)) + ')\n'
    raw_input('Press any key and so on.')