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
import os.path
import zipfile

# external #
from utility.const import easy_packages, downloadable_packages,\
                        URL_SETUPTOOLS, URL_R, R_PATH,\
                        R_COMPONENTS, R_PKG, R_LIB

class unzip:
    def __init__(self, verbose = False, percent = 10):
        self.verbose = verbose
        self.percent = percent

    def extract(self, file, dir):
        if not dir.endswith(':') and not os.path.exists(dir):
            os.mkdir(dir)

        zf = zipfile.ZipFile(file)

        # create directory structure to house files
        self._createstructure(file, dir)

        num_files = len(zf.namelist())
        percent = self.percent
        divisions = 100 / percent
        perc = int(num_files / divisions)

        # extract files to directory structure
        for i, name in enumerate(zf.namelist()):

            if self.verbose == True:
                print "Extracting %s \r" % name
            elif perc > 0 and (i % perc) == 0 and i > 0:
                complete = int (i / perc) * percent
                print "%s%% complete \r" % complete

            if not name.endswith('/'):
                outfile = open(os.path.join(dir, name), 'wb')
                outfile.write(zf.read(name))
                outfile.flush()
                outfile.close()


    def _createstructure(self, file, dir):
        self._makedirs(self._listdirs(file), dir)


    def _makedirs(self, directories, basedir):
        """ Create any directories that don't currently exist """
        for dir in directories:
            curdir = os.path.join(basedir, dir)
            if not os.path.exists(curdir):
                os.mkdir(curdir)

    def _listdirs(self, file):
        """ Grabs all the directories in the zip structure
        This is necessary to create the structure before trying
        to extract the file to it. """
        zf = zipfile.ZipFile(file)

        dirs = []

        for name in zf.namelist():
            if name.endswith('/'):
                dirs.append(name)

        dirs.sort()
        return dirs

def dlProgress(count, blockSize, totalSize):
    percent = int(count * blockSize * 100 / totalSize)
    sys.stdout.write('Download progress: %d%%   \r' % percent)

def downloadWithProgressbar(url):
    file_name = url.split('/')[-1]
    print 'Downloading ' + file_name
    urllib.urlretrieve(url, file_name, reporthook=dlProgress)
    return file_name

def download_and_install(file_url, options=''):
        file = downloadWithProgressbar(file_url)
        print 'Download complete, now launching...'
        subprocess.call('./' + file + ' ' + options)
        try:
            os.remove('./' + file)
        except Exception, e:
            print e
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
        if package == 'PyWavelets':
            __import__('pywt')
        elif package == 'PIL':
            __import__('Image')
        else: __import__(package)
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
        download_and_install(URL_R, '/VERYSILENT /DIR="' + R_PATH + '" /COMPONENTS=' + R_COMPONENTS)
        # update packages
        print 'Updating R packages...'
        unzipper = unzip()
        unzipper.verbose = True
        for the_file in os.listdir(R_PKG):
            file_path = os.path.join(R_PKG, the_file)
            try:
                if os.path.isfile(file_path):
                    unzipper.extract(file_path, R_LIB)
                    # removing zip
                    os.unlink(file_path)
            except Exception, e:
                print e

    print 'Install/Update complete. Status:\n'
    print '\n'.join(installed), '\n\n(total installed: ' + str(len(installed)) + ')\n'
    print '------------ # # # ------------'
    print '\n'.join(in_system), '\n\n(already in system: ' + str(len(in_system)) + ')\n'
    print '------------ # # # ------------'
    print '\n'.join(problematic), '\n\n(erred somehow: ' + str(len(problematic)) + ')\n'
    raw_input('Press any key and so on.')
