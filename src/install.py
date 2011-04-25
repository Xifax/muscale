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

try:
    from setuptools.command import easy_install
except ImportError:
    print 'Please, install easy_install!'
    if raw_input('Download setuptools now? [y/n]: ') == ('y' or 'Y'):
        file = downloadWithProgressbar('http://pypi.python.org/packages/2.6/s/setuptools/setuptools-0.6c11.win32-py2.6.exe')
        subprocess.call('./' + file)
        os.remove('./' + file)
    else: sys.exit(0)

def install_with_easyinstall(package):
    try:
        if package == 'pyqt': __import__('PyQt4')
        else: __import__(package)
        in_system.append(package)
    except ImportError:
        print 'Installing ' + package
        easy_install.main(['-U', package])
        installed.append(package)

if __name__ == '__main__':
    installed = []; in_system = []
    packages = ['pywt', 'flufl.enum', 'userconfig', 'numpy', 'scipy', 'matplotlib', 'simpledropbox', 'pyqt']
    for package in packages:
        install_with_easyinstall(package)

    #TODO: for PyQt and Matplotlib it may be better to use binary installer(s)

    print 'Install/Update complete. Status:\n'
    print '\n'.join(installed), '\n\n(total installed: ' + str(len(installed)) + ')\n'
    print '\n------------ # # # ------------\n'
    print '\n'.join(in_system), '\n\n(already in system: ' + str(len(in_system)) + ')\n'
    raw_input('Press any key and so on.')