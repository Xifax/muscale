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
#   - TO DO list
#   - dependencies & packages
# -> structure:
#   - gui ~ qt frontend
#   - stats ~ processing backend
#   - utils ~ constants & useful methods
#   - res ~ gui objects & initial data
#   - pyqtgraph ~ additionaly plot moduels
#   - user ~ project utilities, stats, docs and so on
# -> launch:
#   - python muscale.py
#===============================================================================

#TODO: implement parse template
#TODO: preemptive R input validation (partially done)
#TODO: implement scalogram
#TODO: tweak level plot previews
#TODO: investingate post-startup lag
#TODO: set tooltips handsomely
#TODO: output formats
#TODO: wizard template
#TODO: fix info dialog text wrap
#TODO: restructure resulting levels for SWT
#TODO: fix button states on reset; update graphs on levels change
#TODO: check wavelet reconstruction procedure

####################################
#            Dependencies          #
####################################

# R 2.12.2 i386                          http://goo.gl/nxOOk
# PySide 1.0.0 (PyQT 4.8.1)              http://goo.gl/owd8y
# PypeR 1.1.0                            http://goo.gl/5Q1JX    (*)
# PyWavelets 0.2.0                       http://goo.gl/9pp1Y    (http://goo.gl/Zhb65)
# NumPy 1.5.1                            http://goo.gl/lZfYj
# Matplotlib 1.0.1                       http://goo.gl/3cXp     (http://goo.gl/wgosD)
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
#NB: (**) requires CygWin/MinGW compiler (and infamous vcvarsall.bat) and SWIG for building Traits and Enable + Cython packages  (#)   (http://goo.gl/U07x) (http://goo.gl/FCoZS)
#NB: (***) documentation is lacking
#NB: (#) python setup.py install build –compiler=mingw32 (Traits -> Cython -> Enable)

#---------------R packages---------------#
#Guidelines                               http://goo.gl/dVizL
#stats, tseries, ast, lmtest              http://goo.gl/4WIeW
#TSA (Time Series Analysis)               http://goo.gl/Chh0z

#--------------- IDE ---------------------#
# PyCharm ~ /.idea

####################################
#            Imports               #
####################################

# internal packages #
import sys

# external packages
from PyQt4.QtGui import QApplication, QIcon
from PyQt4.QtCore import Qt

# own packages #
from gui.guiMain import MuScaleMainDialog
from gui.guiSplash import showSplash
from utils.const import RES, ICONS, LOGO, STYLE
from utils.log import log

####################################
#        QT application loop       #
####################################
def main():

    # qt application
    app = QApplication(sys.argv)
    app.setStyle(STYLE)
    app.setWindowIcon(QIcon(RES + ICONS + LOGO))

    # splash screen
    splash = showSplash(app)

    # main widget
    muScale = MuScaleMainDialog()
    muScale.show()
    splash.finish(muScale)

    try:
        sys.exit(app.exec_())
    except Exception, e:
        muScale.messageInfo.showInfo(str(e))
        log.debug(e)
    finally:
        print 'Bye!'

if __name__ == '__main__':
    main()