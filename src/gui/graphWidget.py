# -*- coding: utf-8 -*-
'''
Created on Mar 10, 2011

@author: Yadavito
'''

# internal #
import os

# own #
from utility.const import RES, ICONS, TOOLBAR_ICONS, TEMP, LINE_WITH
from utility.tools import clearFolderContents

# external #
from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QObject, QEvent, QSize
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.pyplot import setp
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
    def __init__(self, toolbar=True, menu=True, parent=None):
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
            self.toolbar.layout()
            #TODO: add button to show/hide legend
#            self.toolbar.setStyleSheet('QWidget { border-style: outset;  border-width: 2px; border-color: beige; }')
#            self.toolbar.setStyleSheet('QWidget {  border: 1px solid black; border-radius: 4px; }')
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
        # active lines list
        self.lines = []

        if menu:
            # setup context menu
            self.setContextMenuPolicy(Qt.ActionsContextMenu)
            self.initActions()

    #-------------- initialization ---------------#
    def initComponents(self):
        self.toolbar.hide()
        self.newIcons()

    def initActions(self):
        #TODO: add 'plot to Tools'
        #TODO: add copy data
        #TODO: add something else!
#        self.addAction(QtGui.QAction('Hide', self, triggered=self.hide))
        pass

    def newIcons(self):
        for position in range(0, self.toolbar.layout().count()):
            widget = self.toolbar.layout().itemAt(position).widget()
            if isinstance(widget, QtGui.QToolButton):
                icon = QtGui.QIcon(RES + ICONS + TOOLBAR_ICONS[position])
                self.toolbar.layout().itemAt(position).widget().setIcon(icon)
                self.toolbar.layout().itemAt(position).widget().resize(QSize(8, 8))
                self.update()
#                self.toolbar.layout().itemAt(position).widget().setIconSize(QSize(16, 16))

    def resetGraphicEffect(self):
        if self.graphicsEffect() is not None:
            self.graphicsEffect().setEnabled(False)

    #------------- plotting methods ---------------#

    ## Hides axes in widget.
    #  @param axes Widget axes form canvas.
    @staticmethod
    def hideAxes(axes):
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)

    ## Clears widget canvas, removing all data and clearing figure.
    #  @param repaint_axes Add standard plot after clearing figure.
    def clearCanvas(self, repaint_axes=True):
        self.canvas.ax.clear()
        self.canvas.fig.clear()
        if repaint_axes:
            self.canvas.ax = self.canvas.fig.add_subplot(111)

    ## Update existing data or plot anew.
    #  @param data List or array to plot/update.
    #  @param line Which line (by index) to update (if any).
    #  @param label Data label (new or existing).
    def updatePlot(self, data, line=0, label=None):
        if not self.canvas.ax.has_data():
            if label is not None:
                self.lines = self.canvas.ax.plot(data, label=label)
            else:
                self.lines = self.canvas.ax.plot(data)
        else:
            if not self.lines:
                self.lines = self.canvas.ax.get_lines()
            if label is not None:
                if label not in [l._label for l in self.lines]:
                    self.lines.extend(self.canvas.ax.plot(data, label=label))
                    line = len(self.lines) - 1
                else:
                    line = [l._label for l in self.lines].index(label)
            line_to_update = self.lines[line]
            if len(data) != len(line_to_update._x):
                # x, y ~ data in y
                line_to_update.set_data(np.arange(len(data)), data)
            else:
                # in case data length stays the same
                line_to_update.set_data(line_to_update._x, data)
            self.canvas.draw()

    ## Plots scalogram for wavelet decomposition.
    #  @param data Wavelet coefficients in matrix.
    #  @param top Axis position.
    #  @param colorbar Shows colorbar for data levels.
    #  @param power Scales resulting graph by power of 2.
    def scalogram(self, data, top=True, colorbar=True, power=False):
#        self.resetGraphicEffect()
        self.clearCanvas()

        x = np.arange(len(data[0]))
        y = np.arange(len(data))

        if power:
            contour = self.canvas.ax.contourf(x, y, np.abs(data) ** 2)
        else:
            contour = self.canvas.ax.contourf(x, y, np.abs(data))

        if colorbar:
            self.canvas.fig.colorbar(contour, ax=self.canvas.ax, orientation='vertical', format='%2.1f')

        if top:
            self.canvas.ax.set_ylim((y[-1], y[0]))
        else:
            self.canvas.ax.set_ylim((y[0], y[-1]))

        self.canvas.ax.set_xlim((x[0], x[-1]))
#        self.canvas.ax.set_ylabel('scales')

        self.canvas.draw()

    ## Plots list of arrays with shared x/y axes.
    #  @param data Arrays to plot (list or matrix).
    def multiline(self, data):
#        self.resetGraphicEffect()
        # abscissa
        axprops = dict(yticks=[])
        # ordinate
        yprops = dict(rotation=0,
              horizontalalignment='right',
              verticalalignment='center',
              x=-0.01)

        # level/figure ratio
        ratio = 1. / len(data)

        # positioning (fractions of total figure)
        left = 0.1
        bottom = 1.0
        width = 0.85
        space = 0.035
        height = ratio - space

        # legend
        label = 'Lvl %d'
        i = 0

        bottom -= height
        ax = self.canvas.fig.add_axes([left, bottom - space, width, height], **axprops)

        ax.plot(data[i])
        setp(ax.get_xticklabels(), visible=False)
        ax.set_ylabel(label % i, **yprops)
        i += 1

        axprops['sharex'] = ax
        axprops['sharey'] = ax

        while i < len(data):
            bottom -= height
            ax = self.canvas.fig.add_axes([left, bottom, width, height], **axprops)
            ax.plot(data[i])
            ax.set_ylabel(label % i, **yprops)
            i += 1
            if i != len(data):
                setp(ax.get_xticklabels(), visible=False)

    #------------------ utils ------------------#
    ## Generates previews for specified data.
    #  @param data List of arrays.
    @staticmethod
    def generatePreviews(data):
        # if data is of array type, it's preferable to use .any()
        if len(data) > 0:
            # temp folder
            tmp = RES + TEMP
            # prepare folder
            if not os.path.exists(tmp):
                os.makedirs(tmp)
            # clear temp folder contents
            clearFolderContents(tmp)

            level = 0
            for array in data:
                matplotlib.pyplot.figure(figsize=(6, 3))
                matplotlib.pyplot.axis('off')
                matplotlib.pyplot.plot(array, color='w', linewidth=LINE_WITH)
                matplotlib.pyplot.savefig(RES + TEMP + str(level) + '.png', transparent=True)
                level += 1
