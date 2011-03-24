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

class InfoFrame(QFrame):
    def __init__(self, parent=None):
        super(InfoFrame, self).__init__(parent)
        
        self.mainLayout = QVBoxLayout()
        
        self.titleLabel = QLabel(u'')
        self.infoLabel = QLabel(u'')

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.infoLabel)
        self.setLayout(self.mainLayout)
        
        self.initComposition()
        self.initComponents()
        
    def initComposition(self):
        self.setWindowFlags(Qt.ToolTip)
        self.setStyleSheet('QFrame { background-color: khaki; border: 1px solid black; border-radius: 4px; } QLabel { border: none; }')
        
        self.setFixedSize(I_WIDTH, I_HEIGHT)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.setMask(roundCorners(self.rect(), 4))
        
    def initComponents(self):
        #self.mainLayout.setAlignment(Qt.AlignCenter)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.infoLabel.setAlignment(Qt.AlignCenter)
        
        self.titleLabel.setWordWrap(True)
        self.infoLabel.setWordWrap(True)
        
    def updateContents(self, index):
        content = infoContens(index)
        self.titleLabel.setText('<b>' + content['title'] + '</b>')
        self.infoLabel.setText(content['info'])