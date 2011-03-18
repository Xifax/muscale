'''
Created on Mar 18, 2011

@author: Yadavito
'''

from scipy import *
#from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
#from PySide.QtGui import *

from pyqtgraph.PlotWidget import *
from pyqtgraph.graphicsItems import *

class QtDetatchedPlot(QtGui.QDialog):
        def __init__(self, parent=None):
            super(QtDetatchedPlot, self).__init__(parent)
            
            self.plotW = PlotWidget()
            self.plotW.registerPlot('Plot')
            
            plot = self.plotW.plot()
            rect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, 0, 1, 1))
            self.plotW.addItem(rect)
            plot.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
            
            self.mainLayout = QVBoxLayout()
            self.mainLayout.addWidget(self.plotW)
            
            self.setLayout(self.mainLayout)
            
            print '!'

#app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#cw = QtGui.QWidget()
#mw.setCentralWidget(cw)
#l = QtGui.QVBoxLayout()
#cw.setLayout(l)
#
#pw = PlotWidget()
#l.addWidget(pw)
#pw2 = PlotWidget()
#l.addWidget(pw2)
#pw3 = PlotWidget()
#l.addWidget(pw3)

#pw.registerPlot('Plot1')
#pw2.registerPlot('Plot2')
#
##p1 = PlotCurveItem()
##pw.addItem(p1)
#p1 = pw.plot()
#rect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, 0, 1, 1))
#rect.setPen(QtGui.QPen(QtGui.QColor(100, 200, 100)))
#pw.addItem(rect)
#p1.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
#
#pw3.plot(array([100000]*100))
#
#
#mw.show()
#
#app.exec_()

#def showWindow():
#
#    app = QtGui.QApplication([])
#    qd = QtDetatchedPlot()
#    qd.show()
#    app.exec_()
