# -*- coding: utf-8 -*-
__author__ = 'Yadavito'


# external #
from py2exe.build_exe import py2exe
from distutils.core import setup
from distutils.dir_util import copy_tree

# internal #
import glob
import os
import sys

# own #
from utility.const import __version__, __name__, _company

##############

distDit = 'muScale_build_' + __version__

##############

class Target(object):
    """ A simple class that holds information on our executable file. """
    def __init__(self, **kw):
        """ Default class constructor. Update as you need. """
        self.__dict__.update(kw)

## ETS and VTK
#
#tvtkPath = os.path.join( os.path.join(distDir, "enthought"), "tvtk")
#copy_tree(enthought.tvtk.__path__[0], tvtkPath )
#
#mayaviPath = os.path.join( os.path.join(distDir, "enthought"), "mayavi")
#copy_tree(enthought.mayavi.__path__[0], mayaviPath )
#
#vtkPath = os.path.join( distDir, "vtk")
#copy_tree(vtk.__path__[0], vtkPath )
#
## M2Crypto
#
#m2CryptoPath = os.path.join( distDir, "M2Crypto")
#copy_tree(M2Crypto.__path__[0], m2CryptoPath )
#
## h5Py
#
#h5pyPath = os.path.join( distDir, "h5py")
#copy_tree(h5py.__path__[0], h5pyPath )


includes = ['']
excludes = ['pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs']

packages = ['']

dll_excludes = ['']

data_files = []
icon_resources = []
bitmap_resources = []
other_resources = []

muScale = Target(
    # what to build
    script = "run.py",
    icon_resources = icon_resources,
    bitmap_resources = bitmap_resources,
    other_resources = other_resources,
    dest_base = __name__,
    version = __version__,
    company_name = _company,
    copyright = _company,
    name = __name__,

    )

setup(
    data_files = data_files,
    options = {"py2exe": {"compressed": 0,
                          "optimize": 1,
                          "includes": includes,
                          "excludes": excludes,
                          "packages": packages,
                          "dll_excludes": dll_excludes,
                          "bundle_files": 3,
                          "dist_dir": distDir,
                          "xref": False,
                          "skip_archive": True,
                          "ascii": False,
                          "custom_boot_script": '',
                         }
              },

    zipfile = r'library.zip',
    console = [],
    windows = [muScale],
    service = [],
    com_server = [],
    ctypes_com_server = []
    )
