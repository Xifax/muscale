# -*- coding: utf-8 -*-
'''
Created on Mar 10, 2011

@author: Yadavito
'''

# external #
from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QObject, QEvent
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

class Filter(QObject):
    """Status message mouse click filter"""
    def eventFilter(self, object, event):

        if event.type() == QEvent.HoverEnter:
            object.toolbar.show()

        if event.type() == QEvent.HoverLeave:
            object.toolbar.hide()

        if event.type() == QEvent.MouseButtonPress:
            pass

        return False

class MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self):
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # define the widget as expandable
        FigureCanvas.setSizePolicy(self,
        QtGui.QSizePolicy.Expanding,
        QtGui.QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)
        
class MplWidget(QtGui.QWidget):
    """Widget defined in Qt Designer"""
    def __init__(self, toolbar=True, parent=None):
        # initialization of Qt MainWindow widget
        QtGui.QWidget.__init__(self, parent)
        # set the canvas to the Matplotlib widget
        self.canvas = MplCanvas()
        # create a vertical box layout
        self.layout = QtGui.QVBoxLayout()
        # add mpl widget to layout
        self.layout.addWidget(self.canvas)

        if toolbar:
            # add navigation toolbar to layout
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.layout.addWidget(self.toolbar)
            # enable hover event handling
            self.setAttribute(Qt.WA_Hover)
            # create and install event filter
            self.filter = Filter(self)
            self.installEventFilter(self.filter)
            # hide toolbar
            self.initComponents()

        # set the layout to th vertical box
        self.setLayout(self.layout)

    def initComponents(self):
        self.toolbar.hide()

    @staticmethod
    def hideAxes(axes):
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)

    def clearCanvas(self, repaint_axes=True):
        self.canvas.ax.clear()
        self.canvas.fig.clear()
        if repaint_axes: self.canvas.ax = self.canvas.fig.add_subplot(111)

    def scalogram(self, data, top=True, colorbar=True, power=False):
        self.clearCanvas()

        x = np.arange(len(data[0]))
        y = np.arange(len(data))

        if power: contour = self.canvas.ax.contourf(x,y,np.abs(data)**2)
        else: contour = self.canvas.ax.contourf(x,y,np.abs(data))

        if colorbar: self.canvas.fig.colorbar(contour, ax=self.canvas.ax, orientation='vertical', format='%2.1f')

        if top: self.canvas.ax.set_ylim((y[-1], y[0]))
        else: self.canvas.ax.set_ylim((y[0], y[-1]))

        self.canvas.ax.set_xlim((x[0], x[-1]))
#        self.canvas.ax.set_ylabel('scales')
        
        self.canvas.draw()