# -*- coding: utf-8 -*-
'''
Created on Mar 10, 2011

@author: Yadavito
'''

# external #
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

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
    def __init__(self, parent = None):
        # initialization of Qt MainWindow widget
        QtGui.QWidget.__init__(self, parent)
        # set the canvas to the Matplotlib widget
        self.canvas = MplCanvas()
        # create a vertical box layout
        self.vbl = QtGui.QVBoxLayout()
        # add mpl widget to vertical box
        self.vbl.addWidget(self.canvas)
        # set the layout to th vertical box
        self.setLayout(self.vbl)

    @staticmethod
    def hideAxes(axes):
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)

    def scalogram(self, data, origin='top'):
        self.canvas.ax.clear()
#        if ts is not None:
#            show_ts = True
#        else:
#            show_ts = False

#        figrow = 1
#        figcol = 1

#        if not show_wps and not show_ts:
#            # only show scalogram
#            figrow = 1
#            figcol = 1
#        elif show_wps and not show_ts:
#            # show scalogram and wps
#            figrow = 1
#            figcol = 4
#        elif not show_wps and show_ts:
#            # show scalogram and ts
#            figrow = 2
#            figcol = 1
#        else:
#            # show scalogram, wps, and ts
#            figrow = 2
#            figcol = 4

        #TODO: check
        x = np.arange(len(data[0]))

#        if use_period:
#            pass
##            y = self.motherwavelet.scales / self.motherwavelet.fc
#        else:
##            y = self.motherwavelet.scales
##            y = scales
        y = len(data)

#        fig = plt.figure(figsize=(16, 12), dpi=160)
#        self.canvas.fig.clear()
#        fig = plt.figure()
#        ax1 = fig.add_subplot(figrow, figcol, 1)

        # if show wps, give 3/4 space to scalogram, 1/4 to wps
#        if show_wps:
#            # create temp axis at 3 or 4 col of row 1
#            axt = fig.add_subplot(figrow, figcol, 3)
#            # get location of axtmp and ax1
#            axt_pos = axt.get_position()
#            ax1_pos = ax1.get_position()
#            axt_points = axt_pos.get_points()
#            ax1_points = ax1_pos.get_points()
#            # set axt_pos left bound to that of ax1
#            axt_points[0][0] = ax1_points[0][0]
#            ax1.set_position(axt_pos)
#            fig.delaxes(axt)

#        if ylog_base is not None:
#            ax1.axes.set_yscale('log', basey=ylog_base)

        if origin is 'top':
            self.canvas.ax.set_ylim((y[-1], y[0]))
        elif origin is 'bottom':
            self.canvas.ax.set_ylim((y[0], y[-1]))
        else:
            raise OriginError('`origin` must be set to "top" or "bottom"')

        self.canvas.ax.set_xlim((x[0], x[-1]))
#        ax1.set_title('scalogram')
        self.canvas.ax.set_ylabel('time')
#        if use_period:
#            ax1.set_ylabel('period')
#            ax1.set_xlabel('time')
#        else:
        self.canvas.ax.set_ylabel('scales')
#        if time is not None:
#            ax1.set_xlabel('time')
#        else:
        self.canvas.ax.set_xlabel('sample')

#        if show_wps:
#            ax2 = fig.add_subplot(figrow,figcol,4,sharey=ax1)
#            if use_period:
#                ax2.plot(self.get_wps(), y, 'k')
#            else:
#                ax2.plot(self.motherwavelet.fc * self.get_wps(), y, 'k')
#
#            if ylog_base is not None:
#                ax2.axes.set_yscale('log', basey=ylog_base)
#            if xlog_base is not None:
#                ax2.axes.set_xscale('log', basey=xlog_base)
#            if origin is 'top':
#                ax2.set_ylim((y[-1], y[0]))
#            else:
#                ax2.set_ylim((y[0], y[-1]))
#            if use_period:
#                ax2.set_ylabel('period')
#            else:
#                ax2.set_ylabel('scales')
#            ax2.grid()
#            ax2.set_title('wavelet power spectrum')

#        if show_ts:
#            ax3 = fig.add_subplot(figrow, 2, 3, sharex=ax1)
#            ax3.plot(x, ts)
#            ax3.set_xlim((x[0], x[-1]))
#            ax3.legend(['time series'])
#            ax3.grid()
#            # align time series fig with scalogram fig
#            t = ax3.get_position()
#            ax3pos=t.get_points()
#            ax3pos[1][0]=ax1.get_position().get_points()[1][0]
#            t.set_points(ax3pos)
#            ax3.set_position(t)
#            if (time is not None) or use_period:
#                ax3.set_xlabel('time')
#            else:
#                ax3.set_xlabel('sample')

#        if figname is None:

#        plt.show()
        
#        else:
#            plt.savefig(figname)
#            plt.close('all')