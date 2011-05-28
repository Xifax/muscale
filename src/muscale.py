# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
@version: 0.1.0
@requires: preferably python 2.6.6
@requires: PyQt 4.8.1
@requires: R 2.13.0
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
#       * wv ~ wavelet previews (in repo, may be regenerated)
#       * data ~ time series samples
#       * tmp ~ temporary folder for previews
#       * r ~ R binaries and packages (zip packages in repo)
#       * fonts ~ custom fonts
#       * docs ~ docs for R modules (not in repo)
#   - pyqtgraph ~ additional plot modules
#   - usr ~ project utilities, stats, docs and so on
#   - src:
#       * muscale.py, mu.pyw ~ main modules
#       * install.py ~ install script
#       * build.py, setup.py ~ currently do not work
#   - muscale:
#       * .gitignore ~ ignore list for git
#       * .idea ~ project configuration
#       * .git ~ repo
#       * README.md ~ readme in markdown format
# -> launch:
#   - python muscale.py
#   or
#   - pythonw mu.pyw
# -> Install:
#   - python install.py
#===============================================================================

####################################
#             TODO list            #
####################################

####################################
#            Dependencies          #
####################################

# R 2.13.0 i386                          http://goo.gl/nxOOk
# PyQT 4.8.1                             http://goo.gl/owd8y
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
# Guidelines                               http://goo.gl/dVizL
# stats, tseries, ast, lmtest              http://goo.gl/4WIeW
# TSA (Time Series Analysis)               http://goo.gl/Chh0z
# forecast
# timsac
# wavethresh
# wavesim

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
