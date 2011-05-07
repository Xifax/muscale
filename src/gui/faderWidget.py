# -*- coding: utf-8 -*-
'''
Created on Mar 25, 2011

@author: Yadavito
'''

import sys
from PyQt4.QtCore import QTimeLine
from PyQt4.QtGui import QWidget, QPixmap, QPainter, QStackedWidget

class FaderWidget(QWidget):

    def __init__(self, old_widget, new_widget):
    
        QWidget.__init__(self, new_widget)
        
        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0
        
        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(333)
        self.timeline.start()
        
        self.resize(new_widget.size())
        self.show()
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()
    
    def animate(self, value):
    
        self.pixmap_opacity = 1.0 - value
        self.repaint()

class StackedWidget(QStackedWidget):

    def __init__(self, parent = None):
        QStackedWidget.__init__(self, parent)
    
    def setCurrentIndex(self, index):
        self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)