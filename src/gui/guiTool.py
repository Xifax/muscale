# -*- coding: utf-8 -*-
'''
Created on Mar 17, 2011

@author: Yadavito
'''

# external #
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from pyqtgraph.PlotWidget import *
from pyqtgraph.graphicsItems import *

# own #
from utils.const import T_WIDTH, T_HEIGHT
from utils.tools import checkParentheses
from utils.log import log

class StatusFilter(QObject):
    """Status message mouse click filter"""
    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverEnter:
            object.parent().upScale.setVisible(True)
            object.parent().fixSize.setVisible(True)
            object.parent().toolDetached.setVisible(True)

        if event.type() == QEvent.HoverLeave:
            def hideButton():
                object.parent().upScale.setHidden(True)
                object.parent().fixSize.setHidden(True)
                object.parent().toolDetached.setHidden(True)
            QTimer.singleShot(3000, hideButton)

        return False

class ToolsFrame(QWidget):
    def __init__(self, R, parent=None):
        super(ToolsFrame, self).__init__(parent)

        # r engine #
        self.R = R

        # tabs #
        self.toolTabs = QTabWidget()

        # r console tab #
        self.rConsoleGroup = QGroupBox()
        self.rConsoleLayout = QGridLayout()

        self.rConsole = QTextEdit()
        self.rInput = QLineEdit()
        self.enterButton = QToolButton()
        self.clearButton = QToolButton()
        self.namespaceButton = QToolButton()
        self.namesList = QListWidget()

        self.rConsoleLayout.addWidget(self.rConsole, 0, 0, 1, 5)
        self.rConsoleLayout.addWidget(self.rInput, 1, 0, 1, 2)
        self.rConsoleLayout.addWidget(self.enterButton, 1, 2, 1, 1)
        self.rConsoleLayout.addWidget(self.clearButton, 1, 3, 1, 1)
        self.rConsoleLayout.addWidget(self.namespaceButton, 1, 4, 1, 1)
        self.rConsoleLayout.addWidget(self.namesList, 2, 0, 1, 5)

        self.rConsoleGroup.setLayout(self.rConsoleLayout)
        self.toolTabs.addTab(self.rConsoleGroup, 'R')

        # graphs tab #
        self.plotWidget = PlotWidget()
        #self.plotWidget.setMaximumSize(self.toolTabs.width(), self.toolTabs.height())

        #NB: to fix such behavior, one may try to plot empty list/array at initialization
        geometry = self.saveGeometry()      # somehow, PlotWidget assumes very large size automatically
        self.toolTabs.addTab(self.plotWidget,'Graph')
        self.restoreGeometry(geometry)

        # table tab #
        self.tableWidget = QTableWidget()
        self.toolTabs.addTab(self.tableWidget,'Table')

        # global layout #
        self.mainLayout = QVBoxLayout()
        # hover area #
        self.hoverLayout = QHBoxLayout()
        self.upScale = QToolButton()
        self.fixSize = QToolButton()
        self.toolDetached = QToolButton()
        self.hoverArea = QLabel()
        self.hoverLayout.addWidget(self.upScale)
        self.hoverLayout.addWidget(self.fixSize)
        self.hoverLayout.addWidget(self.toolDetached)

        self.mainLayout.addWidget(self.hoverArea)
        self.mainLayout.addLayout(self.hoverLayout)
#        self.mainLayout.addWidget(self.upScale)
#        self.mainLayout.addWidget(self.fixSize)
        self.mainLayout.addWidget(self.toolTabs)

        self.setLayout(self.mainLayout)

        # flags #
        self.flash = False
        self.shownHoverInfo = False

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
        # layout and tabs
        self.toolTabs.setTabPosition(QTabWidget.South)

        self.upScale.setText('&Upscale')
        self.upScale.setMaximumHeight(18)
        self.upScale.setCheckable(True)
        self.upScale.setHidden(True)

        self.fixSize.setText('&Lock vertical resize')
        self.fixSize.setMaximumHeight(18)
        self.fixSize.setCheckable(True)
        self.fixSize.setHidden(True)

        self.toolDetached.setText('&Detach')
        self.toolDetached.setMaximumHeight(18)
        self.toolDetached.setCheckable(True)
        self.toolDetached.setHidden(True)

        self.hoverArea.setMaximumHeight(2)
        self.hoverArea.setAlignment(Qt.AlignCenter)

        self.hoverLayout.setAlignment(Qt.AlignCenter)
        self.mainLayout.setAlignment(Qt.AlignCenter)

        # r console #
        self.enterButton.setText('enter')
        self.enterButton.setCheckable(True)
        self.clearButton.setText('clear')
        self.namespaceButton.setText('..')
        self.namespaceButton.setCheckable(True)

        self.rConsole.setReadOnly(True)
        self.namesList.setHidden(True)
        #self.namesList.setMaximumHeight(self.rConsole.height()/3)

        # table #
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(['Value'])

        # graph #
        self.plotWidget.plot()

    def initActions(self):
        self.rInput.returnPressed.connect(self.rCommand)
        self.clearButton.clicked.connect(self.clearRConsole)
        self.namespaceButton.clicked.connect(self.viewNamespace)

        self.upScale.clicked.connect(self.changeScale)

        self.filter = StatusFilter()
        self.hoverArea.setAttribute(Qt.WA_Hover, True)
        self.hoverArea.installEventFilter(self.filter)

        #self.namesList.itemDoubleClicked.connect(self.showItemInR)
        self.namesList.itemClicked.connect(self.appendItemInline)

    #--------- actions ---------#
    def rCommand(self, internalIn=None):
        try:
            if internalIn is None:
                request = self.checkRequest(self.rInput.text())
                if request is not None: result = '\n'.join(self.R(request).split(self.R.newline)[1:])   #PyQt shenanigans
                else: result = None
            else:
                result = '\n'.join(self.R(str(self.internalIn)).split(self.R.newline)[1:])
            if result != self.R.newline and result is not None:
                self.rConsole.append(result)
        except Exception:
                self.parentWidget().messageInfo.showInfo('Sudden PypeR combustion!', True)
                log.error('R interpreter crush')
        if self.enterButton.isChecked():
            self.rInput.clear()

        self.indicateInput()
        self.updateNamespace()

    def checkRequest(self, input):
        if str(input).strip() == '': self.parentWidget().messageInfo.showInfo('Empty query! Use "help(topic)" for help.', True);  return None
        elif checkParentheses(str(input)): return str(input)
        else: self.parentWidget().messageInfo.showInfo('Incorrect input: check if brackets are evenly matched.', True);  return None

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

    def viewNamespace(self):
        if self.namespaceButton.isChecked():
            self.namesList.setMaximumHeight(self.rConsole.height()/3)
            self.namesList.setVisible(True)
        else:
            self.namesList.setHidden(True)

    def updateNamespace(self):
        self.namesList.clear()
        for object in  self.R('objects()').split(self.R.newline)[1:]:
            if object != self.R.newline:
                for e in object.split(' '):
                    if e != '[1]' and e != '':
                        item = QListWidgetItem(e.strip('"')); item.setTextAlignment(Qt.AlignCenter)
                        self.namesList.addItem(item)

    def updateTable(self, dataSet):

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)

        iterList = []
        iterList = iterList + dataSet; iterList.reverse()

        i = 0
        for element in iterList:
            self.tableWidget.insertRow(i)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(element)))

        del iterList

    def changeScale(self):
        if self.upScale.isChecked():
            self.showFullScreen()
        else:
            self.showNormal()

    def showEvent(self, event):
        if not self.shownHoverInfo:
            self.hoverArea.setText(u'mouse over here')
            self.hoverArea.setMaximumHeight(16)
            self.setStyleSheet('QLabel { border: 1px solid gray; border-radius: 4px; }')
            def flashLabel():
                self.hoverArea.setText(u'')
                self.setStyleSheet('QLabel { border: none; }')
                self.hoverArea.setMaximumHeight(2)
            QTimer.singleShot(2000, flashLabel)
            self.shownHoverInfo = True

    def appendItemInline(self, event):
        self.rInput.setText(self.rInput.text() + ' ' + self.namesList.selectedItems()[0].text())

    def closeEvent(self, QCloseEvent):
        self.parentWidget().toggleTools.setChecked(False)