# -*- coding: utf-8 -*-
'''
Created on Mar 18, 2011

@author: Yadavito
'''

# own #
from gui.graphWidget import MplWidget

# external #
from PyQt4.QtCore import QRect, QSize, QPointF
from PyQt4.QtGui import QRegion, QFrame, QGraphicsDropShadowEffect

def unfillLayout(layoutName):
    '''Empty layout from widgets (should be reinit'd, if in another layout)'''
    def deleteItems(layout): 
        if layout is not None: 
            while layout.count(): 
                item = layout.takeAt(0) 
                widget = item.widget() 
                if widget is not None: 
                    widget.deleteLater() 
                else: 
                    deleteItems(item.layout()) 
    deleteItems(layoutName) 
    
def roundCorners(rectangle, radius):
        '''Get region for setting round edges mask'''
        region = QRegion()
        region += rectangle.adjusted(radius,0,-radius,0)
        region += rectangle.adjusted(0,radius,-0,-radius)
        
        corner = QRect(rectangle.topLeft(), QSize(radius*2,radius*2))
        region += QRegion(corner, QRegion.Ellipse)
        
        corner.moveTopRight(rectangle.topRight())
        region += QRegion(corner, QRegion.Ellipse)
        
        corner.moveBottomLeft(rectangle.bottomLeft())
        region += QRegion(corner, QRegion.Ellipse)
        
        corner.moveBottomRight(rectangle.bottomRight())
        region += QRegion(corner, QRegion.Ellipse)
        
        return region

def createSeparator():
    '''Create simple separator'''
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    return separator

def createVerticalSeparator():
    '''Create simple separator'''
    separator = QFrame()
    separator.setFrameShape(QFrame.VLine)
    separator.setFrameShadow(QFrame.Sunken)
    return separator

def createShadow():
    '''Create shadow effect'''
    shadow = QGraphicsDropShadowEffect()
    shadow.setOffset(QPointF(3,3))
    shadow.setBlurRadius(8)
    return shadow

def walkNonGridLayoutShadow(layout):
    '''Add shadow effect to every widget in V/H layout'''
    for position in range(0, layout.count()):
        widget = layout.itemAt(position)
        # in case someone put some layouts in your layout
        if widget is not None:
            if not isinstance(widget.widget(), QFrame):
                if widget.widget() is not None: widget.widget().setGraphicsEffect(createShadow())

def walkGridLayoutShadow(layout):
    '''Add shadow effect to every widget in grid layout'''
    for row in range(0, layout.rowCount()):
        for column in range(0, layout.columnCount()):
            widget = layout.itemAtPosition(row, column)
            if widget is not None:
                if not isinstance(widget.widget(), QFrame):
                    if widget.widget() is not None: widget.widget().setGraphicsEffect(createShadow())
