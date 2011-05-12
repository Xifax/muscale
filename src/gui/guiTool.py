# -*- coding: utf-8 -*-
'''
Created on Mar 17, 2011

@author: Yadavito
'''
# internal #
import time

# external #
from PyQt4.QtCore import Qt, QObject,QEvent, QTimer
from PyQt4.QtGui import *
from pyqtgraph.PlotWidget import PlotWidget
#from pyqtgraph.graphicsItems import *

# own #
from utility.const import T_WIDTH, T_HEIGHT
from utility.tools import checkParentheses
from utility.const import LABEL_VISIBLE, FLASH_LABEL
from utility.log import log

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
            QTimer.singleShot(LABEL_VISIBLE, hideButton)

        return False

class ToolsFrame(QWidget):
    def __init__(self, R, parent=None):
        super(ToolsFrame, self).__init__(parent)

        # r engine #
        self.R = R

        # tabs #
        self.toolTabs = QTabWidget()

        # log tab #
        self.rLogGroup = QGroupBox()
        self.rlogLayout = QVBoxLayout()

        self.logList = QListWidget()
        self.logClear = QPushButton('Clear')
        self.logSearh = QLineEdit()
        self.rlogLayout.addWidget(self.logClear)
        self.rlogLayout.addWidget(self.logList)
        self.rlogLayout.addWidget(self.logSearh)

        self.rLogGroup.setLayout(self.rlogLayout)
        self.toolTabs.addTab(self.rLogGroup, 'Log')

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

        geometry = self.saveGeometry()
        self.toolTabs.addTab(self.plotWidget, 'Graph')
        self.restoreGeometry(geometry)

        # table tab #
        self.tableWidget = QTableWidget()
        self.toolTabs.addTab(self.tableWidget, 'Table')

        # export tab #
        self.exportGroup = QGroupBox()
        self.exportLayout = QGridLayout()

        self.exportGroup.setLayout(self.exportLayout)
        self.toolTabs.addTab(self.exportGroup, 'Export')

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
        self.mainLayout.addWidget(self.toolTabs)

        self.setLayout(self.mainLayout)

        # flags #
        self.flash = False
        self.shownHoverInfo = False

        # initialization #
        self.initComposition()
        self.initComponents()
        self.initActions()

        # post init #
        self.rInput.setFocus()
        self.inStack = { 'stack': [], 'index': -1 }

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

        # table #
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(['Value'])

        # graph #
        self.plotWidget.plot()

        # log #
        self.logList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.logList.setAlternatingRowColors(True)
        self.logList.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.logList.setWordWrap(True)

        self.logList.setStyleSheet(
            '''QListView { alternate-background-color: whitesmoke; }
            QListView::item {
                border: 1px solid #d9d9d9;
                border-top-color: transparent;
                border-bottom-color: transparent;
                    }
            QListView::item:selected {
                border: 1px solid dimgray; border-radius: 4px;
            }
            QListView::item:selected:active {
                 background: qlineargradient(x1: 1, y1: 0, x2: 0, y2: 3, stop: 0 #cbdaf1, stop: 1 #bfcde4);
            }
            QListView::item:hover {
                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
                 border: 1px solid #bfcde4;
            }''')

    def initActions(self):
        # R
        self.rInput.returnPressed.connect(self.rCommand)
        self.clearButton.clicked.connect(self.clearRConsole)
        self.namespaceButton.clicked.connect(self.viewNamespace)
        self.namesList.itemClicked.connect(self.appendItemInline)
        # dialog
        self.upScale.clicked.connect(self.changeScale)

        self.filter = StatusFilter()
        self.hoverArea.setAttribute(Qt.WA_Hover, True)
        self.hoverArea.installEventFilter(self.filter)

        # log
        self.logClear.clicked.connect(self.clearEntries)
        self.logSearh.textChanged.connect(self.highlightSearh)
        self.logSearh.returnPressed.connect(self.logSearh.clear)
        #TODO: implement context menu features
#        self.logList.itemDoubleClicked.connect(self.copyToClipboard)
        self.logList.addAction(QAction('Toggle controls', self, triggered=self.toggleLogControls))
#        self.logList.addAction(QAction('Export to file', self, triggered=self.toggleLogControls))
#        self.logList.addAction(QAction('Copy to clipboard', self, triggered=self.toggleLogControls))

#--------- actions ---------#

    #------ ---- log -----------#
    def updateLog(self, entries, error=False, warning=False, NB=False):
        timestamp = time.strftime('%H:%M:%S')
        for entry in entries:
            item = QListWidgetItem(13 * ' ' + entry)      # one tab is too much, it seems
            if error: item.setTextColor(QColor(255, 0, 0, 127))
            if warning: item.setTextColor(QColor(255, 127, 80, 127))
            if NB: item.setTextColor(QColor(0, 0, 255, 127))
            label = QLabel("<font style='font-size: 7pt; color: gray'>" + timestamp + "</font>")
            label.setAlignment(Qt.AlignTop)
            self.logList.addItem(item)
            self.logList.setItemWidget(item, label)

    def clearEntries(self):
        self.logList.clear()

    def highlightSearh(self):
        self.logList.clearSelection()
        if unicode(self.logSearh.text()).strip() != '':
            match = self.logList.findItems(self.logSearh.text(), Qt.MatchContains)
            for item in match: self.logList.setItemSelected(item, True)

            if match: self.logList.scrollToItem(match[0])
#            self.logList.setText('<b>' + str(len(match)) + '</b> items found')
        else:
            pass
#            self.updateItemsCount()

    def toggleLogControls(self):
        if self.logClear.isHidden():
            self.logClear.show()
            self.logSearh.show()
        else:
            self.logClear.hide()
            self.logSearh.hide()

    #----------- R -------------#
    def updateStack(self, request):
        if request not in self.inStack['stack']:
            self.inStack['stack'].append(request)
            self.inStack['index'] += 1

    def rCommand(self, internalIn=None):
        try:
            if internalIn is None:
                request = self.checkRequest(self.rInput.text())
                if request is not None:
                    result = '\n'.join(self.R(request).split(self.R.newline)[1:])   #PyQt shenanigans
                    self.updateStack(request)
                else:
                    result = None
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
        for object in self.R('objects()').split(self.R.newline)[1:]:
            if object != self.R.newline:
                for e in object.split(' '):
                    if e != '[1]' and e != '':
                        item = QListWidgetItem(e.strip('"')); item.setTextAlignment(Qt.AlignCenter)
                        self.namesList.addItem(item)

    def appendItemInline(self):
        self.rInput.setText(self.rInput.text() + ' ' + self.namesList.selectedItems()[0].text())

    #---------- Table -----------#
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

    #------ dialog behavior ------#
    def changeScale(self):
        if self.upScale.isChecked():
            self.showFullScreen()
        else:
            self.showNormal()

    def showEvent(self, event):
        if not self.shownHoverInfo:
            self.hoverArea.setText(u'mouseover here to show dialog controls')
            self.hoverArea.setMaximumHeight(16)
            self.hoverArea.setStyleSheet('QLabel { border: 1px solid gray; border-radius: 4px; }')
            def flashLabel():
                self.hoverArea.setText(u'')
                self.hoverArea.setStyleSheet('QLabel { border: none; }')
                self.hoverArea.setMaximumHeight(2)
            QTimer.singleShot(FLASH_LABEL, flashLabel)
            self.shownHoverInfo = True
        self.updateNamespace()

    def closeEvent(self, QCloseEvent):
        self.parentWidget().toggleTools.setChecked(False)
        self.parentWidget().showGraph.setText('Show graph')
        self.parentWidget().showTable.setText('Show table')

    def keyPressEvent(self, QKeyEvent):
        if self.rInput.hasFocus():
            if QKeyEvent.key() == Qt.Key_Up:
                if self.inStack['stack']:
                    if self.inStack['index'] < len(self.inStack['stack']) - 1:
                        self.inStack['index'] += 1
                    self.rInput.setText(self.inStack['stack'][self.inStack['index']])
            if QKeyEvent.key() == Qt.Key_Down:
                if self.inStack['stack']:
                    if self.inStack['index'] > -1:
                        self.inStack['index'] -= 1
                    self.rInput.setText(self.inStack['stack'][self.inStack['index']])

