# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# iternal #
from distutils.core import setup
from glob import glob

# own #
from utils.const import *

# compound data go into site-packages
from distutils.command.install import INSTALL_SCHEMES
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']
#TODO: complete specification using constants and test on vm
setup(name=__name__,
      version=__version__,
      requires=[],
      description='',
      author=__author__,
      author_email='',
      url='',
      py_modules=[''],
      data_files=[
          ('muscale-res/icons', glob('../res/icons/.*')),
          ],
      )

