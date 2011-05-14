# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
@version: 0.0.1
@requires: preferably python 2.6.6
'''

####################################
#        Project structure         #
####################################

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
#   - utility ~ constants & useful methods
#   - res ~ gui objects & initial data
#       * icons ~ gui icons and logos
#       * wv ~ wavelet previews (may be regenerated)
#   - pyqtgraph ~ additional plot modules
#   - user ~ project utilities, stats, docs and so on
# -> launch:
#   - python muscale.py
#===============================================================================

####################################
#             TODO list            #
####################################

#TODO: export menu
#TODO: graph legend
#TODO: wizard template
#TODO: allow multicolumn table
#TODO: implement parse template
#TODO: implement data criterion
#TODO: check parsed data length (> n)
#TODO: implement some kind of automatic resize mechanism
#TODO: write a couple of unit tests for ISWT and levels rearrangement (sic!)
#TODO: initialize R with custom (non-SYSTEM PATH) path [compiled application ver.]
#TODO: ponder what to do with SWT excluded coefficients (bedrock values for reconstruction?)

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
# PyQtGraph                              http://goo.gl/hQjvW    (***)
# PyCairo 1.8.1                          http://goo.gl/ScUvx
# CairoPlot 1.1                          http://goo.gl/VjTUO
# R plot engine

# additional statistical packages:
# scikits.timeseries                     http://goo.gl/t6Hy8

####################################
#               Notes              #
####################################

#NB: (*) needs fix for python 2.6.6  DO NOT INSTALL using easy_install    (http://goo.gl/3js4H)
#NB: (***) documentation is lacking

#---------------R packages---------------#
#Guidelines                               http://goo.gl/dVizL
#stats, tseries, ast, lmtest              http://goo.gl/4WIeW
#TSA (Time Series Analysis)               http://goo.gl/Chh0z

#--------------- IDE ---------------------#
# PyCharm ~ /.idea

#--------------- Data sets ---------------#
# http://goo.gl/Hlts0

####################################
#             Imports              #
####################################

# internal packages #
import sys

# external packages
from PyQt4.QtGui import QApplication, QIcon

# own packages #
from gui.guiMain import MuScaleMainDialog
from gui.guiSplash import showSplash
from utility.const import RES, ICONS, LOGO, STYLE
from utility.log import log

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
        muScale.toolsFrame.updateLog([str(e)], True)
        log.exception(e)

if __name__ == '__main__':
    main()