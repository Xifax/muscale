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

import matplotlib.pyplot as plt
from gui.graphWidget import MPL_Widget

#plt.plot([1,2,3,4])
#plt.ylabel('some numbers')
#plt.show()

from matplotlib import patches
axes = plt.subplot(111)
axes.add_patch(patches.Rectangle((0.2, 0.2), 0.5, 0.5))
plt.show()

#mpl_widget = MPL_Widget()
#l.addWidget(mpl_widget)

#l.addWidget(plt)

#===============================================================================
# pw = PlotWidget()
# l.addWidget(pw)
# 
# #plot = pw.plot([1,2,3,4,5])
# pw.registerPlot('Plot')
# plot = pw.plot()
# plot.updateData([1,2,3,4,5])
# #plot.setPen(QtGui.QPen(QtGui.QColor(120, 255, 255)))
# plot.setColor(QtGui.QColor(0, 255, 255))
#===============================================================================



#lg = QtGui.QGraphicsGridLayout()
#vb = ViewBox()
#p1 = PlotCurveItem()
#p1.updateData([1,2,3,4,5])
#vb.addItem(p1)
#xScale = ScaleItem(orientation='bottom', linkView=vb)
#lg.addItem(xScale, 1, 1)

#l.addWidget(vb)

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