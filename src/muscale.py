# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
@version: 0.0.1
@requires: preferably python 2.6.6
'''

#===============================================================================
# --- muScale ---
# -> main project file <-
# -> contains: 
#   - central GUI dialog
#   - TODO list
#   - dependencies & packages
# -> structure:
#   - gui ~ qt frontend
#   - stats ~ processing backend
#   - utils ~ constants & useful methods
#   - res ~ gui objects & initial data
# -> launch:
#   - python muscale.py
#===============================================================================

#TODO: fix imports to parsimonious ones
#TODO: implement parse template
#TODO: preemptive R input validation

####################################
#            Dependencies          #
####################################

# R 2.12.2 i386                          http://goo.gl/nxOOk
# PySide 1.0.0 (PyQT 4.8.1)              http://goo.gl/owd8y
# PypeR 1.1.0                            http://goo.gl/5Q1JX    (*)
# PyWavelets 0.2.0                       http://goo.gl/9pp1Y
# NumPy 1.5.1                            http://goo.gl/lZfYj
# Matplotlib 1.0.1                       http://goo.gl/3cXp
# SciPy 0.9.0                            http://goo.gl/l4Edo

# possible plot lib alternatives:
# Chaco 3.4.1                            http://goo.gl/8SbDY    (**)
# PyQtGraph                              http://goo.gl/hQjvW    (***)
# PyCairo 1.8.1                          http://goo.gl/ScUvx
# CairoPlot 1.1                          http://goo.gl/VjTUO
# R plot engine

# additional statistical packages:
# scikits.timeseries                     http://goo.gl/t6Hy8

#-----------------NOTES------------------#
#NB: (*) needs fix for python 2.6.6  DO NOT INSTALL using easy_install    (http://goo.gl/3js4H)
#NB: (**) requires CygWin (and infamous vcvarsall.bat), yet still does not build with one
#NB: (***) standalone mode possible (PyQt4 only), if not usingOpenGl

#---------------R packages---------------#
#Guidelines                               http://goo.gl/dVizL
#stats, tseries, ast, lmtest              http://goo.gl/4WIeW
#TSA (Time Series Analysis)               http://goo.gl/Chh0z

####################################
#            Imports               #
####################################

# internal packages #
import sys

# external packages
#===============================================================================
# from PySide.QtGui import QApplication
#===============================================================================
from PyQt4.QtGui import QApplication

# own packages #
from gui.guiMain import MuScaleMainDialog
from utils.log import log

####################################
#        QT application loop       #
####################################

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('plastique')
    
    muScale = MuScaleMainDialog()
    muScale.show()
    
    try:
        sys.exit(app.exec_())
    except Exception, e:
        print e
        log.debug(e)
    finally:
        print 'Bye!'
        