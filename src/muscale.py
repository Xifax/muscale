# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''

#===============================================================================
# --- muScale ---
# -> main project file <-
# -> contains: 
#   - central GUI dialog
#   - TODO list
#   - dependencies & packages
# -> launch:
#   - python.exe gui.py
#===============================================================================

#TODO: update to PySide 1.0.0 QT 4.7.2
#TODO: fix imports to parsimonious ones

####################################
#            Dependencies          #
####################################

# R 2.12.2 i386                          http://goo.gl/nxOOk
# PySide 1.0.0~beta3 QT 4.7.1            http://goo.gl/owd8y
# PypeR 1.1.0                            http://goo.gl/5Q1JX
# PyWavelets 0.2.0                       http://goo.gl/9pp1Y
# NumPy 1.5.1                            http://goo.gl/lZfYj
# Matplotlib 1.0.1                       http://goo.gl/3cXp
# SciPy 0.9.0                            http://goo.gl/l4Edo

####################################
#            Imports               #
####################################

# internal packages #
import sys

# external packages
from PySide.QtGui import QApplication

# own packages #
from gui.guiMain import MuScaleMainDialog

####################################
#        QT application loop       #
####################################

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('plastique')
    
    muScale = MuScaleMainDialog()
    muScale.show()
    
    sys.exit(app.exec_())