# -*- coding: utf-8 -*-
'''
Created on Mar 23, 2011

@author: Yadavito
'''
# external #
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# own #
from utils.const import I_WIDTH, I_HEIGHT, infoContens
from utils.guiTweaks import roundCorners

class InfoFilter(QObject):
    """Status message mouse click filter"""
    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverEnter:
            object.dockButtonUp.setVisible(True)
            object.dockButtonDown.setVisible(True)
            object.adjustSize()
#            object.updateCornersMask()
        if event.type() == QEvent.HoverLeave:
            object.dockButtonUp.setHidden(True)
            object.dockButtonDown.setHidden(True)
            object.adjustSize()

        return False

class InfoFrame(QFrame):
    def __init__(self, parent=None):
        super(InfoFrame, self).__init__(parent)
        
        self.mainLayout = QVBoxLayout()
        
        self.titleLabel = QLabel(u'')
        self.infoLabel = QLabel(u'')

        self.dockButtonUp = QPushButton()
        self.dockButtonDown = QPushButton()
#        self.dockButtonLeft = QPushButton()
#        self.dockButtonRight = QPushButton()

        self.mainLayout.addWidget(self.dockButtonUp)
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.infoLabel)
        self.mainLayout.addWidget(self.dockButtonDown)
        self.setLayout(self.mainLayout)
        
        self.initComposition()
        self.initComponents()
        self.initActions()
        
    def initComposition(self):
        self.setWindowFlags(Qt.ToolTip)
        self.setStyleSheet('QFrame { background-color: khaki; border: 1px solid black; border-radius: 4px; } QLabel { border: none; }')
        
        #self.setFixedSize(I_WIDTH, I_HEIGHT)
        self.setMaximumWidth(I_WIDTH)
#        self.setFocusPolicy(Qt.StrongFocus)
        
    def initComponents(self):
        #self.mainLayout.setAlignment(Qt.AlignCenter)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.infoLabel.setAlignment(Qt.AlignCenter)
        
        self.titleLabel.setWordWrap(True)
        self.infoLabel.setWordWrap(True)
        
        self.dockButtonUp.setHidden(True)
        self.dockButtonUp.setCheckable(True)
        self.dockButtonUp.setMaximumHeight(8)
        self.dockButtonUp.setStyleSheet('QWidget { background-color: khaki; }')

        self.dockButtonDown.setHidden(True)
        self.dockButtonDown.setCheckable(True)
        self.dockButtonDown.setMaximumHeight(8)
        self.dockButtonDown.setStyleSheet('QWidget { background-color: khaki; }')

        self.filter = InfoFilter()
        self.setAttribute(Qt.WA_Hover, True)
        self.installEventFilter(self.filter)
        
    def initActions(self):
        self.dockButtonUp.clicked.connect(self.setTopPosition)
        self.dockButtonDown.clicked.connect(self.setBottomPosition)
        
    def updateContents(self, index):
        content = infoContens(index)
        self.titleLabel.setText('<b>' + content['title'] + '</b>')
        self.infoLabel.setText(content['info'])
        self.infoLabel.adjustSize()
        self.adjustSize()
#        self.updateCornersMask()
        
    def setTopPosition(self):
        self.dockButtonDown.setChecked(False)
        self.parent().updateInfoPosition()
    
    def setBottomPosition(self):
        self.dockButtonUp.setChecked(False)
        self.parent().updateInfoPosition()
        
    def updateCornersMask(self):
        self.setMask(roundCorners(self.rect(), 5))
    
    def showEvent(self, event):
        pass
#        self.infoLabel.adjustSize()
#        self.adjustSize()
#        self.updateCornersMask()