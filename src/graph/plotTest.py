'''
Created on Mar 23, 2011

@author: Yadavito
'''
from scipy import *
from PyQt4 import QtGui, QtCore
from pyqtgraph.PlotWidget import *
from pyqtgraph.graphicsItems import *

from time import sleep

app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
cw = QtGui.QWidget()
mw.setCentralWidget(cw)
l = QtGui.QVBoxLayout()
cw.setLayout(l)

mw.show()
mw.resize(QtCore.QSize(800, 600))

pw = PlotWidget()
l.addWidget(pw)

#plot = pw.plot([1,2,3,4,5])
pw.registerPlot('Plot')
plot = pw.plot()
plot.updateData([1,2,3,4,5])

#plot_b = PlotCurveItem()
#plot_b.updateData([1,2,3])
#pw.addItem(PlotCurveItem())
#pw.update()

#pw.registerPlot('Plot_b')
#plot_b = pw.plot()
#plot_b.updateData([1,2])
#plot.setPointMode('dot')
#plot.free()
#plot.setClickable(True

#sleep(5)

#plot.clear()

app.exec_()