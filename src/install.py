# -*- coding: utf-8 -*-
'''
Created on Mar 22, 2011

@author: Yadavito
'''
# internal #
import sys
import urllib
import subprocess
import os
import shutil
import platform

# external #
from utility.const import easy_packages, downloadable_packages,\
                        URL_SETUPTOOLS, URL_R

def dlProgress(count, blockSize, totalSize):
    percent = int(count * blockSize * 100 / totalSize)
    sys.stdout.write('Download progress: %d%%   \r' % percent)

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
        download_and_install(URL_SETUPTOOLS)
    else:
        sys.exit(0)

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
            problematic.append(package)

def install_downloadable(package):
    try:
        __import__(package)
        in_system.append(package)
    except ImportError:
        print 'Installing ' + package
        try:
            download_and_install(downloadable_packages[package])
            installed.append(package)
        except  Exception:
            problematic.append(package)

if __name__ == '__main__':
    installed = []
    in_system = []
    problematic = []

    for package in easy_packages:
        install_with_easyinstall(package)
    for package in downloadable_packages:
        install_downloadable(package)

    # R
    if raw_input('Download and install R? [y/n]: ') == ('y' or 'Y'):
        download_and_install(URL_R)

    print 'Install/Update complete. Status:\n'
    print '\n'.join(installed), '\n\n(total installed: ' + str(len(installed)) + ')\n'
    print '\n------------ # # # ------------\n'
    print '\n'.join(in_system), '\n\n(already in system: ' + str(len(in_system)) + ')\n'
    print '\n------------ # # # ------------\n'
    print '\n'.join(problematic), '\n\n(erred somehow: ' + str(len(problematic)) + ')\n'
    raw_input('Press any key and so on.')
