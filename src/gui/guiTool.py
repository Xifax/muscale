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

# own #
from utility.const import T_WIDTH, T_HEIGHT, FONTS_DICT
from utility.tools import checkParentheses
from utility.const import LABEL_VISIBLE, FLASH_LABEL,\
                        RES, ICONS, CLEAR, GRAPH, COPY, CONTROLS,\
                        ELEMENTS, CUT, SERIES
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
        self.rlogLayout = QGridLayout()

        self.logStats = QLabel()
        self.logList = QListWidget()
        self.logClear = QToolButton()
        self.logSearh = QLineEdit()
        self.rlogLayout.addWidget(self.logStats, 0, 0, 1, 2)
        self.rlogLayout.addWidget(self.logList, 1, 0, 1, 2)
        self.rlogLayout.addWidget(self.logSearh, 2, 0)
        self.rlogLayout.addWidget(self.logClear, 2, 1)

        self.rLogGroup.setLayout(self.rlogLayout)
        self.toolTabs.addTab(self.rLogGroup, 'Lo&g')

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
        self.toolTabs.addTab(self.rConsoleGroup, '&R')

        # graphs tab #
        self.plotWidget = PlotWidget()
        self.data = None

        geometry = self.saveGeometry()
        self.toolTabs.addTab(self.plotWidget, 'Grap&h')
        self.restoreGeometry(geometry)

        # table tab #
        self.tableWidget = QTableWidget()
        self.toolTabs.addTab(self.tableWidget, 'Ta&ble')

        # export tab #
        self.exportGroup = QGroupBox()
        self.exportLayout = QGridLayout()

        self.exportForecast = QCheckBox('Export resulting forecast')
        self.exportStepByStep = QCheckBox('Export modelling steps')
        self.exportGraph = QCheckBox('Export graphics')
        self.exportData = QCheckBox('Export data')
        self.exportButton = QPushButton('Export as')
        self.picLbl = QLabel()

        self.exportLayout.addWidget(self.picLbl, 0, 0, 1, 2)
        self.exportLayout.addWidget(self.exportForecast, 1, 0)
        self.exportLayout.addWidget(self.exportStepByStep, 1, 1)
        self.exportLayout.addWidget(self.exportData, 2, 0)
        self.exportLayout.addWidget(self.exportGraph, 2, 1)
        self.exportLayout.addWidget(self.exportButton, 3, 0, 1, 2)

        self.exportGroup.setLayout(self.exportLayout)
        self.toolTabs.addTab(self.exportGroup, '&Export')

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
        self.inStack = {'stack': [], 'index': -1}
        self.toggleLogControls()

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
        self.namesList.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.namesList.setAlternatingRowColors(True)
        self.namesList.setStyleSheet('''QListView::item:selected:active {
                 background: qlineargradient(x1: 1, y1: 0, x2: 0, y2: 3, stop: 0 #cbdaf1, stop: 1 #bfcde4);
            }
            QListView::item {
                border: 1px solid #d9d9d9;
                border-top-color: transparent;
                border-bottom-color: transparent;
            }
            QListView::item:hover {
                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
                 border: 1px solid #bfcde4;
            }''')

        # table #
        self.tableWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.tableWidget.setAlternatingRowColors(True)

        # graph #
        self.plotWidget.plot()

        # log #
        self.logList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.logList.setAlternatingRowColors(True)
        self.logList.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.logList.setWordWrap(True)
        self.logList.setToolTip('Doubleclick on item to copy')

        self.logClear.setText('Clear')
        self.logStats.setAlignment(Qt.AlignCenter)
        self.logStats.hide()

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

        # table #
        self.tableWidget.setStyleSheet('''QTableView::item:selected:active {
                 background: qlineargradient(x1: 1, y1: 0, x2: 0, y2: 3, stop: 0 #cbdaf1, stop: 1 #bfcde4);
            }
            QTableView::item {
                border: 1px solid #d9d9d9;
                border-top-color: transparent;
                border-bottom-color: transparent;
            }
            QTableView::item:hover {
                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
                 border: 1px solid #bfcde4;
            }''')

        # fonts #
        self.logList.setFont(QFont(FONTS_DICT['log'][0], FONTS_DICT['log'][2]))
        self.tableWidget.setFont(QFont(FONTS_DICT['table'][0], FONTS_DICT['table'][2]))

        # export #
        self.exportLayout.setAlignment(Qt.AlignCenter)
        self.exportData.hide()
        self.exportGraph.hide()

        self.picLbl.setPixmap(QPixmap(RES + ICONS + GRAPH))
        self.picLbl.setAlignment(Qt.AlignCenter)
        self.picLbl.hide()

        # hotkeys #
        # ...

    def initActions(self):
        # R
        self.rInput.returnPressed.connect(self.rCommand)
        self.clearButton.clicked.connect(self.clearRConsole)
        self.namespaceButton.clicked.connect(self.viewNamespace)
        self.namesList.itemDoubleClicked.connect(self.appendItemInline)

        self.namesList.addAction(QAction(QIcon(RES + ICONS + GRAPH), 'Plot selected object',
                                         self, triggered=self.plotFromR))

        # dialog
        self.upScale.clicked.connect(self.changeScale)

        self.filter = StatusFilter()
        self.hoverArea.setAttribute(Qt.WA_Hover, True)
        self.hoverArea.installEventFilter(self.filter)

        # log
        self.logClear.clicked.connect(self.clearEntries)
        self.logSearh.textChanged.connect(self.highlightSearch)
        self.logSearh.returnPressed.connect(self.logSearh.clear)
        self.logList.itemDoubleClicked.connect(self.copyToClipboard)
        self.logList.addAction(QAction(QIcon(RES + ICONS + CONTROLS), 'Toggle controls',
                                       self, triggered=self.toggleLogControls))

        # table
        self.tableWidget.addAction(QAction(QIcon(RES + ICONS + CLEAR), 'Clear all',
                                           self, triggered=self.clearTable))
        self.tableWidget.addAction(QAction(QIcon(RES + ICONS + COPY), 'Copy selected column(s)',
                                           self, triggered=self.copyColumns))
        self.tableWidget.addAction(QAction(QIcon(RES + ICONS + ELEMENTS), 'Copy selected item(s)',
                                           self, triggered=self.copyItems))
        self.tableWidget.addAction(QAction(QIcon(RES + ICONS + CUT), 'Remove selected column(s)',
                                           self, triggered=self.removeColumns))
        self.tableWidget.addAction(QAction(QIcon(RES + ICONS + GRAPH), 'Plot selected items',
                                           self, triggered=self.plotItems))

        # export
        exportMenu = QMenu()
        exportMenu.addAction(QAction('Portable Document Format (PDF)',
                                     self, triggered=self.exportToPdf))
        exportMenu.addAction(QAction('Microsoft Excel Spreadsheet (XLS)',
                                     self, triggered=self.exportToXls))
        exportMenu.addAction(QAction('Plain text (TXT) && PNG', self,
                                     triggered=self.exportToVarious))
        exportMenu.addAction(QAction('Send to print',
                                     self, triggered=self.sendToPrint))
        self.exportButton.setMenu(exportMenu)

        self.exportForecast.stateChanged.connect(self.toggleExportOptions)
        self.exportStepByStep.stateChanged.connect(self.toggleExportOptions)
        self.exportGraph.stateChanged.connect(self.updatePix)

#--------- actions ---------#

    #-------- export ----------#
    def toggleExportOptions(self):
        if self.exportForecast.isChecked() or\
            self.exportStepByStep.isChecked():
            self.exportData.show()
            self.exportGraph.show()

            self.updatePix()
        else:
            self.exportData.hide()
            self.exportGraph.hide()
            self.picLbl.hide()

    def updatePix(self):

        if self.exportForecast.isChecked() and\
            self.exportStepByStep.isChecked() and\
            self.exportGraph.isChecked():

            self.picLbl.setPixmap(QPixmap(RES + ICONS + SERIES[2]))

        elif self.exportForecast.isChecked() and\
            self.exportStepByStep.isChecked():

            self.picLbl.setPixmap(QPixmap(RES + ICONS + SERIES[1]))
            self.picLbl.show()

        elif self.exportForecast.isChecked():

            self.picLbl.setPixmap(QPixmap(RES + ICONS + SERIES[0]))
            self.picLbl.show()

        elif self.exportStepByStep.isChecked():

            self.picLbl.setPixmap(QPixmap(RES + ICONS + SERIES[3]))
            self.picLbl.show()

        else:
            self.picLbl.hide()

    def exportToPdf(self):
#       QPrinter
#        http://goo.gl/AgX3l
#        http://goo.gl/K5zg4
        pass
    def exportToXls(self):
#        http://goo.gl/xalIt
#        http://goo.gl/K9cjx
        pass
    def exportToVarious(self):
        pass
    def sendToPrint(self):
        pass

    #---------- log -----------#
    def updateLog(self, entries, error=False, warning=False, NB=False):
        timestamp = time.strftime('%H:%M:%S')
        for entry in entries:
            indent = 13
            item = QListWidgetItem(indent * ' ' + entry)      # one tab is too much, as it seems
            if error:
                item.setTextColor(QColor(255, 0, 0, 127))
            if warning:
                item.setTextColor(QColor(255, 127, 80, 127))
            if NB:
                item.setTextColor(QColor(0, 0, 255, 127))
            label = QLabel("<font style='font-size: 7pt; color: gray'>" + timestamp + "</font>")
            label.setAlignment(Qt.AlignTop)
            self.logList.addItem(item)
            self.logList.setItemWidget(item, label)

    def clearEntries(self):
        self.logList.clear()

    def highlightSearch(self):
        self.logList.clearSelection()
        if unicode(self.logSearh.text()).strip():
            match = self.logList.findItems(self.logSearh.text(), Qt.MatchContains)
            for item in match: self.logList.setItemSelected(item, True)

            if match:
                self.logList.scrollToItem(match[0])
            self.logStats.setText('Found <b>' + str(len(match)) + '</b> item(s)')
            self.logStats.show()
        else:
            self.logStats.hide()

    def toggleLogControls(self):
        if self.logClear.isHidden():
            self.logClear.show()
            self.logSearh.show()
        else:
            self.logClear.hide()
            self.logSearh.hide()

    def copyToClipboard(self, item):
        clipboard = QApplication.clipboard()
        clipboard.setText(item.text())

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
                    # also possible: self.R.newline
                    result = '\n'.join(self.R(request).split('\n')[1:])   #PyQt shenanigans
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
        if str(input).strip() == '':
            self.parentWidget().messageInfo.showInfo('Empty query! Use "help(topic)" for help.', True)
            return None
        elif checkParentheses(str(input)):
            return str(input)
        else:
            self.parentWidget().messageInfo.showInfo('Incorrect input: check if brackets are evenly matched.', True)
            return None

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
            self.namesList.setMaximumHeight(self.rConsole.height() / 3)
            self.namesList.setVisible(True)
        else:
            self.namesList.setHidden(True)

    def updateNamespace(self):
        self.namesList.clear()
        for object in self.R('objects()').split('\n')[1:]:
            if object != self.R.newline:
                for e in object.split(' '):
                    if e != '[1]' and e != '':
                        item = QListWidgetItem(e.strip('"'))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.namesList.addItem(item)

    def appendItemInline(self):
        self.rInput.setText(self.rInput.text() + ' ' + self.namesList.selectedItems()[0].text())

    def plotFromR(self):
        variable = self.namesList.currentItem().text()
        try:
            self.updatePlot(self.R[str(variable)])
            self.toolTabs.setCurrentIndex(2)
        except Exception, e:
            self.parentWidget().messageInfo.showInfo(str(e), True)

    #---------- Table -----------#
    def clearTable(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

    def updateTable(self, dataSet, header=None):
        new_column = self.tableWidget.columnCount()
        self.tableWidget.setColumnCount(new_column + 1)
        if header is None:
            header = 'Value' + str(new_column)
        else:
            pass

        self.tableWidget.setHorizontalHeaderItem(new_column, QTableWidgetItem(header))

        if self.tableWidget.rowCount() < len(dataSet):
            for row in range(self.tableWidget.rowCount(), len(dataSet)):
                self.tableWidget.insertRow(row)

        i = 0
        for element in dataSet:
            self.tableWidget.setItem(i, new_column, QTableWidgetItem(str(element))); i += 1

        self.tableWidget.update()

    def copyColumns(self):
        if self.tableWidget.selectedIndexes():
            copy = u''
            column_n = 0
            for the_range in self.tableWidget.selectedRanges():
                for column in range(the_range.leftColumn(), the_range.rightColumn() + 1):
                    copy += self.tableWidget.horizontalHeaderItem(column).text()
                    column_n += 1
                    try:
                        for row in range(0, self.tableWidget.rowCount() - 1):
                            copy += ' ' +  self.tableWidget.item(row, column).text()
                        copy += '\n'
                    except Exception:
                        pass

            clipboard = QApplication.clipboard()
            clipboard.setText(copy)

            self.parentWidget().messageInfo.showInfo('Copied ' + str(column_n) + ' full column(s)')

    def copyItems(self):
        copy = u''
        for item in self.tableWidget.selectedItems():
            copy += item.text()

        clipboard = QApplication.clipboard()
        clipboard.setText(copy)
        self.parentWidget().messageInfo.showInfo('Copied ' + str(len(self.tableWidget.selectedItems())) + ' item(s)')

    def removeColumns(self):
        if self.tableWidget.selectedIndexes():
            for the_range in self.tableWidget.selectedRanges():
                for column in range(the_range.leftColumn(), the_range.rightColumn() + 1):
                    self.tableWidget.removeColumn(column)

    def plotItems(self):
        data = []
        for item in self.tableWidget.selectedItems():
            data.append(float(item.text()))

        self.updatePlot(data)
        self.toolTabs.setCurrentIndex(2)

    #----------- graph -----------#
    def updatePlot(self, data, append=False):
        #TODO: update axes and position
        if not append:
            if self.data is None:
                self.data = self.plotWidget.plot(data)
            else:
                self.data.updateData(data)
        else:
            return self.plotWidget.plot(data)

    def resetPlot(self):
        if self.data is not None:
            self.data.free()

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
