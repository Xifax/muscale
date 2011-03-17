# -*- coding: utf-8 -*-
'''
Created on Mar 17, 2011

@author: Yadavito
'''

# external #
from PySide.QtCore import *
from PySide.QtGui import *
from stats.pyper import *

# own #
from utils.const import T_WIDTH, T_HEIGHT

class ToolsFrame(QWidget):
    def __init__(self, parent=None):
        super(ToolsFrame, self).__init__(parent)
        
        # r engine #
        self.R = R()
        
        # tabs #
        self.toolTabs = QTabWidget()
        
        # r console tab #
        self.rConsoleGroup = QGroupBox()
        self.rConsoleLayout = QGridLayout()
        
        self.rConsole = QTextEdit()
        self.rInput = QLineEdit()
        self.enterButton = QToolButton()
        self.clearButton = QToolButton()
        
        self.rConsoleLayout.addWidget(self.rConsole, 0, 0, 1, 4)
        self.rConsoleLayout.addWidget(self.rInput, 1, 0, 1, 2)
        self.rConsoleLayout.addWidget(self.enterButton, 1, 2, 1, 1)
        self.rConsoleLayout.addWidget(self.clearButton, 1, 3, 1, 1)
        
        self.rConsoleGroup.setLayout(self.rConsoleLayout)
        self.toolTabs.addTab(self.rConsoleGroup, 'R')
        
        # global layout #
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.toolTabs)
        
        self.setLayout(self.mainLayout)
        
        # flags #
        self.flash = False
        
        # initialization #
        self.initComposition()
        self.initComponents()        
        self.initActions()
        
        # test #
        self.rInput.setFocus()        
        
    def initComposition(self):
        self.setWindowTitle('Tools')
        self.setWindowFlags(Qt.Tool)

        self.setMinimumSize(T_WIDTH, T_HEIGHT)
        self.setFocusPolicy(Qt.StrongFocus)
        
    def initComponents(self):
        self.toolTabs.setTabPosition(QTabWidget.TabPosition.South)
        
        self.enterButton.setText('enter')
        self.enterButton.setCheckable(True)
        self.clearButton.setText('clear')
        
        self.rConsole.setReadOnly(True)
        
    def initActions(self):
        self.rInput.returnPressed.connect(self.rCommand)
        self.clearButton.clicked.connect(self.clearRConsole)
    
    #--------- actions ---------#
    def rCommand(self):
        result = '\n'.join(self.R(self.rInput.text()).split(self.R.newline)[1:])
        if result != self.R.newline:
            self.rConsole.append(result)
        if self.enterButton.isChecked():
            self.rInput.clear()
            
        self.indicateInput()
            
    def indicateInput(self):
        if not self.flash:
            self.rInput.setStyleSheet( 'QLineEdit { border: 2px solid black; border-radius: 6px;}')
            self.flash = True
                        
            QTimer.singleShot(100, self.indicateInput)
        else:
            self.rInput.setStyleSheet( 'QLineEdit { border: 2px solid gray ; border-radius: 6px;}')
            self.flash = False
    
    def clearRConsole(self):
        self.rConsole.clear()
        