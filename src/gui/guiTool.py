# -*- coding: utf-8 -*-
'''
Created on Mar 17, 2011

@author: Yadavito
'''
# internal #
import time
import operator

# external #
from PyQt4.QtCore import Qt, QObject,QEvent, QTimer
from PyQt4.QtGui import *
from pyqtgraph.PlotWidget import PlotWidget
from xlwt import Workbook, Alignment, XFStyle, Font, Borders

# own #
from utility.const import T_WIDTH, T_HEIGHT, FONTS_DICT
from utility.tools import checkParentheses
from utility.const import LABEL_VISIBLE, FLASH_LABEL,\
                        RES, ICONS, CLEAR, GRAPH, COPY, CONTROLS,\
                        ELEMENTS, CUT, SERIES, SCALE, TEMP, GRADIENT
from utility.log import log

class StatusFilter(QObject):
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

class RFilter(QObject):
    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverEnter:
            object.setText('''<html>Click to enable R console at your own risk!<br/>
<i>Be aware though, it may spontaneously combust.</i></html>''')
            object.setStyleSheet('QLabel { border: 1px solid SteelBlue; color: SteelBlue; border-radius: 4px; }')

        if event.type() == QEvent.HoverLeave:
            object.setText('R console is for testing purposes only, and by default is disabled.')
            object.setStyleSheet('QLabel { border: none; color: gray; }')

        if event.type() == QEvent.MouseButtonPress:
            object.parent().parent().parent().parent().showRConsole()

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

        self.rEnable = QLabel('R console is for testing purposes only, and by default is disabled.')
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
        self.rConsoleLayout.addWidget(self.rEnable, 3, 0, 1, 5)

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
        self.exportAll = QPushButton('Export all')
        self.exportButton = QPushButton('Export as')
        self.picLbl = QLabel()

        self.exportLayout.addWidget(self.picLbl, 0, 0, 1, 2)
        self.exportLayout.addWidget(self.exportForecast, 1, 0)
        self.exportLayout.addWidget(self.exportStepByStep, 1, 1)
        self.exportLayout.addWidget(self.exportData, 2, 0)
        self.exportLayout.addWidget(self.exportGraph, 2, 1)
        self.exportLayout.addWidget(self.exportAll, 3, 0)
        self.exportLayout.addWidget(self.exportButton, 3, 1)

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
        self.rNewline = '\n'
#        self.rNewline = self.R.newline  # glitches starting with R 2.13

    def initComposition(self):
        self.setWindowTitle('Tools')
        self.setWindowFlags(Qt.Tool)

        self.setMinimumSize(T_WIDTH, T_HEIGHT)
        self.setFocusPolicy(Qt.StrongFocus)

    def initComponents(self):
        self.setStyleSheet('''QGroupBox {''' + GRADIENT +
                            '''}
                            QPushButton {
                                color: #333;
                                border: 1px solid #555;
                                border-radius: 11px;
                                padding: 2px;
                                background: qradialgradient(cx: 0.3, cy: -0.4,
                                fx: 0.3, fy: -0.4,
                                radius: 1.35, stop: 0 #fff, stop: 1 #888);
                                min-width: 80px;
                            }
                            QPushButton:hover {
                                color: #fff;
                                background: qradialgradient(cx: 0.3, cy: -0.4,
                                fx: 0.3, fy: -0.4,
                                radius: 1.35, stop: 0 #fff, stop: 1 #bbb);}
                            QPushButton:pressed {
                                background: qradialgradient(cx: 0.4, cy: -0.1,
                                fx: 0.4, fy: -0.1,
                                radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}
                            QPushButton:checked {
                                background: qradialgradient(cx: 0.4, cy: -0.1,
                                fx: 0.4, fy: -0.1,
                                radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}
                            QToolButton {
                                color: #333;
                                border: 1px solid #555;
                                border-radius: 11px;
                                padding: 2px;
                                background: qradialgradient(cx: 0.3, cy: -0.4,
                                fx: 0.3, fy: -0.4,
                                radius: 1.35, stop: 0 #fff, stop: 1 #888);
                                min-width: 20px;
                            }
                            QToolButton:hover {
                                color: #fff;
                                background: qradialgradient(cx: 0.3, cy: -0.4,
                                fx: 0.3, fy: -0.4,
                                radius: 1.35, stop: 0 #fff, stop: 1 #bbb);
                            }
                            QToolButton:pressed {
                                background: qradialgradient(cx: 0.4, cy: -0.1,
                                fx: 0.4, fy: -0.1,
                                radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
                            }
                            QToolButton:checked {
                                background: qradialgradient(cx: 0.4, cy: -0.1,
                                fx: 0.4, fy: -0.1,
                                radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
                            }
                            QTabWidget::tab-bar {
                                alignment: center;
                            }
                            QTabBar::tab {''' + GRADIENT +
                                 '''border: 1px solid #C4C4C3;
                                 border-bottom-color: #C2C7CB;
                                 border-bottom-left-radius: 4px;
                                 border-bottom-right-radius: 4px;
                                 min-width: 16ex;
                                 padding: 2px;
                            }
                            QTabBar::tab:selected, QTabBar::tab:hover {
                                 background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                             stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                                             stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
                            }
                            QTabBar::tab:selected {
                                 border-color: #9B9B9B;
                                 border-bottom-color: #C2C7CB;
                            }
                            QTabBar::tab:!selected {
                                 margin-bottom: 2px;
                            }
                            QTabBar::tab:selected {
                                 margin-left: -4px;
                                 margin-right: -4px;
                            }
                            QTabBar::tab:first:selected {
                                 margin-left: 0;
                            }
                            QTabBar::tab:last:selected {
                                 margin-right: 0;
                            }
                            QTabBar::tab:only-one {
                                 margin: 0;
                            }
                            QLineEdit {
                            border: 2px solid gray;
                                    border-radius: 6px;
                            }
                            QLineEdit:focus {
                                selection-color: white;
                                selection-background-color: gray;
                                border: 2px solid black;
                                border-radius: 6px;
                            }
                            QScrollBar:vertical {
                              width: 20px;
                              border: 1px solid grey;
                              border-radius: 6px;
                              background-color: transparent;
                              margin: 28px 0 28px 0;
                            }
                            QScrollBar::add-line:vertical {
                              background: transparent;
                              height: 32px;
                              subcontrol-position: bottom;
                              subcontrol-origin: margin;
                            }
                            QScrollBar::sub-line:vertical {
                              background: transparent;
                              height: 32px;
                              subcontrol-position: top;
                              subcontrol-origin: margin;
                            }
                            QScrollBar::up-arrow:vertical {
                              width: 20px;
                              height: 32px;
                              background: transparent;
                              image: url(../res/icons/arrow_up.png);
                            }
                            QScrollBar::up-arrow:hover {
                              bottom: 2px;
                            }
                            QScrollBar::down-arrow:vertical {
                              width: 20px;
                              height: 32px;
                              background: transparent;
                              image: url(../res/icons/arrow_down.png);
                            }
                            QScrollBar::down-arrow:hover {
                              top: 2px;
                            }
                            QScrollBar::handle:vertical {
                                border-radius: 6px;
                                background: url(../res/icons/handle.png) 0% center no-repeat;
                                background-color: white;
                                min-height: 32px;
                            }
                            QScrollBar::handle:hover {
                                background: url(../res/icons/handle_hover.png) 0% center no-repeat;
                                background-color: white;
                                border: 1px solid gray;
                            }
                            QScrollBar:horizontal {
                              height: 20px;
                              border: 1px solid grey;
                              border-radius: 6px;
                              background-color: transparent;
                              margin: 0 28px 0 28px;
                            }
                            QScrollBar::add-line:horizontal {
                              background: transparent;
                              width: 32px;
                              subcontrol-position: right;
                              subcontrol-origin: margin;
                            }
                            QScrollBar::sub-line:horizontal {
                              background: transparent;
                              width: 32px;
                              subcontrol-position: left;
                              subcontrol-origin: margin;
                            }
                            QScrollBar::left-arrow:horizontal {
                              width: 32px;
                              height: 20px;
                              background: transparent;
                              image: url(../res/icons/arrow_left.png);
                            }
                            QScrollBar::left-arrow:hover {
                              right: 2px;
                            }
                            QScrollBar::right-arrow:horizontal {
                              width: 32px;
                              height: 20px;
                              background: transparent;
                              image: url(../res/icons/arrow_right.png);
                            }
                            QScrollBar::right-arrow:hover {
                              left: 2px;
                            }
                            QScrollBar::handle:horizontal {
                                border-radius: 6px;
                                background: url(../res/icons/handle_horizontal.png) 0% center no-repeat;
                                background-color: white;
                                min-width: 32px;
                            }
                            QCheckBox::indicator {
                                 width: 16px;
                                 height: 16px;
                            }
                            QCheckBox::indicator:unchecked {
                                 image: url(../res/icons/checkbox_no.png);
                            }
                            QCheckBox::indicator:checked {
                                 image: url(../res/icons/checkbox_yes.png);
                            }
                            QCheckBox::indicator:unchecked:pressed {
                                 image: url(../res/icons/checkbox_pressed.png);
                            }
                            QCheckBox::indicator:unchecked:hover {
                                 background: gray;
                                 border-radius: 4px;
                            }
                            QCheckBox::indicator:checked:pressed {
                                 image: url(../res/icons/checkbox_pressed.png);
                            }
                            QCheckBox::indicator:checked:hover {
                                 background: gray;
                                 border-radius: 4px;
                            }''')

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

        self.rEnable.setAlignment(Qt.AlignCenter)
        self.rEnable.setWordWrap(True)
        self.rEnable.setFont(QFont(FONTS_DICT['warn'][0], FONTS_DICT['warn'][2]))
        self.rEnable.setStyleSheet('QLabel { border: none; color: gray; }')

        self.rConsole.setReadOnly(True)
        self.rConsole.setStyleSheet('''QTextEdit::focus {
                                         border: 2px solid black;
                                         border-radius: 6px;
                                    }''')

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
            }
            QListView::focus {
                 border: 2px solid black;
                 border-radius: 6px;
            }''')

        # hide r components
        self.enterButton.hide()
        self.clearButton.hide()
        self.namespaceButton.hide()
        self.namesList.hide()
        self.rInput.hide()
        self.rConsole.hide()

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
        self.logList.setToolTip('Doubleclick to copy')

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
            }
            QListView::focus {
                 border: 2px solid black;
                 border-radius: 6px;
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
            }
            QTableView::focus {
                 border: 2px solid black;
                 border-radius: 6px;
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

        self.rFilter = RFilter()
        self.rEnable.setAttribute(Qt.WA_Hover, True)
        self.rEnable.installEventFilter(self.rFilter)

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
        self.tableWidget.addAction(QAction(QIcon(RES + ICONS + SCALE), 'Resize to contents',
                                           self, triggered=self.resizeTableToFit))

        # export
        exportMenu = QMenu()
        exportMenu.addAction(QAction('Microsoft Excel Spreadsheet (XLS)',
                                     self, triggered=self.exportToXls))
        toPDF = QAction('Portable Document Format (PDF)',
                                     self, triggered=self.exportToPdf)
        toTXT = QAction('Plain text (TXT) && PNG',
                                     self, triggered=self.exportToVarious)
        toPrint = QAction('Send to print',
                                     self, triggered=self.sendToPrint)
        exportMenu.addAction(toPrint)
        exportMenu.addAction(toTXT)
        exportMenu.addAction(toPDF)

        toTXT.setDisabled(True)
        toPDF.setDisabled(True)
        toPrint.setDisabled(True)
        self.exportButton.setMenu(exportMenu)

        self.exportForecast.stateChanged.connect(self.toggleExportOptions)
        self.exportStepByStep.stateChanged.connect(self.toggleExportOptions)
        self.exportGraph.stateChanged.connect(self.updatePix)
        self.exportAll.clicked.connect(self.exportAllXls)

#--------- actions ---------#

    #-------- export ----------#
    def exportAllXls(self):
        self.exportForecast.setChecked(True)
        self.exportStepByStep.setChecked(True)
        self.exportData.setChecked(True)
        self.exportGraph.setChecked(True)

        self.toggleExportOptions()
        self.exportToXls()

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
        # opening file dialog
        fileName = QFileDialog.getSaveFileName(self,
            'Save as', RES, 'Microsoft Excel Spreadsheet (*.xls)')

        if fileName.count() > 0:
            try:
                COLUMN_WIDTH = 3000

                alignment = Alignment()
                alignment.horizontal = Alignment.HORZ_CENTER
                alignment.vertical = Alignment.VERT_CENTER

                borders = Borders()
                borders.left = Borders.THIN
                borders.right = Borders.THIN
                borders.top = Borders.THIN
                borders.bottom = Borders.THIN

                style = XFStyle()
                style.alignment = alignment
                style.borders = borders

                font = Font()
                font.bold = True
                headerStyle = XFStyle()
                headerStyle.font = font

                separate = Borders()
                separate.left = Borders.THIN
                separate.right = Borders.DOUBLE
                separate.top = Borders.THIN
                separate.bottom = Borders.THIN
                separateStyle = XFStyle()
                separateStyle.borders = separate

                book = Workbook(encoding='utf-8')

                # modelling data
                if self.exportStepByStep.isChecked():
                    dec_sheet = book.add_sheet('Data decomposition')

                    # decomposition data
                    if self.exportData.isChecked():
                        # initial data
                        column = 0
                        row = 0
                        dec_sheet.write(row, column, 'Time series', headerStyle)
                        dec_sheet.col(column).width = COLUMN_WIDTH
                        row += 1
                        for item in self.parentWidget().currentDataSet[0]:
                            dec_sheet.write(row, column, item, separateStyle)
                            row += 1

                        # decomposition
                        for lvl in self.parentWidget().wCoefficients:
                            row = 0
                            column += 1
                            dec_sheet.write(row, column, 'Level' + str(column - 1), headerStyle)
                            dec_sheet.col(column).width = COLUMN_WIDTH
                            row += 1
                            for item in lvl:
                                dec_sheet.write(row, column, item, style)
                                row += 1

                    # decomposition graphs
                    if self.exportGraph.isChecked():
                        pass

                    levels_sheet = book.add_sheet('Multiscale forecast')

                    # levels data
                    if self.exportData.isChecked():
                        column = 0
                        for lvl in self.parentWidget().processedWCoeffs:
                            row = 0
                            levels_sheet.write(row, column, 'Level' + str(column), headerStyle)
                            levels_sheet.col(column).width = COLUMN_WIDTH
                            row += 1
                            for item in lvl:
                                levels_sheet.write(row, column, float(item), style)
                                row += 1
                            column += 1

                if self.exportForecast.isChecked():
                    result_sheet = book.add_sheet('Results')

                    if self.exportData.isChecked():
                        # initial
                        column = 0
                        row = 0
                        result_sheet.write(row, column, 'Initial data', headerStyle)
                        result_sheet.col(column).width = COLUMN_WIDTH
                        row += 1
                        for item in self.parentWidget().currentDataSet[0]:
                            result_sheet.write(row, column, item, separateStyle)
                            row += 1

                        # forecast
                        row = 0
                        column += 1
                        result_sheet.write(row, column, 'Forecast', headerStyle)
                        result_sheet.col(column).width = COLUMN_WIDTH
                        row += 1
                        for item in self.parentWidget().resultingForecast:
                            result_sheet.write(row, column, item, style)
                            row += 1

                    if self.exportGraph.isChecked():
                        row = 0
                        column = 2
                        self.parentWidget().resultingGraph.saveFigure('forecast', format='bmp')

                        result_sheet.insert_bitmap(RES + TEMP + 'forecast.bmp', row, column)

                # saving xls
                try:
                    book.save(unicode(fileName))
                    self.parentWidget().messageInfo.showInfo('Saved as ' + unicode(fileName))
                except Exception:
                    self.parentWidget().messageInfo.showInfo('Could not save as ' + unicode(fileName), True)

            except Exception, e:
                self.parentWidget().messageInfo.showInfo('Not enough data.', True)


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
    def showRConsole(self):
        self.rEnable.hide()
        
        self.enterButton.show()
        self.clearButton.show()
        self.namespaceButton.show()
        self.rInput.show()
        self.rConsole.show()
        
    def updateStack(self, request):
        if request not in self.inStack['stack']:
            self.inStack['stack'].append(request)
            self.inStack['index'] += 1

    def rCommand(self, internalIn=None):
        try:
            if internalIn is None:
                request = self.checkRequest(self.rInput.text())
                if request is not None:
                    result = '\n'.join(self.R(request).split(self.rNewline)[1:])   #PyQt shenanigans
                    self.updateStack(request)
                else:
                    result = None
            else:                result = '\n'.join(self.R(str(self.internalIn)).split(self.R.newline)[1:])
            if result != self.R.newline and result is not None:
                self.rConsole.append(result)
        except Exception:
                self.parentWidget().messageInfo.showInfo('Sudden PypeR combustion!', True)
                log.error('R interpreter crush')
                self.R = self.parentWidget().reInitR()
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
        for object in self.R('objects()').split(self.rNewline)[1:]:
            if object != self.rNewline:
                for e in object.split(' '):
                    if not e.startswith('[') and e != '' and e != 'character(0)':
                        item = QListWidgetItem(e.strip().strip('"'))
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

    def sortRanges(self, ranges):
        rangesByLeftColumn = [(r.leftColumn(), r) for r in ranges]
        map(operator.itemgetter(0), rangesByLeftColumn)
        map(operator.itemgetter(1), rangesByLeftColumn)
        return [tpl[1] for tpl in sorted(rangesByLeftColumn, key=operator.itemgetter(0))]

    def removeColumns(self):
        if self.tableWidget.selectedIndexes():
            deleted = 0
            for the_range in self.sortRanges(self.tableWidget.selectedRanges()):
                for column in range(the_range.leftColumn(), the_range.rightColumn() + 1):
                    index = column - deleted
                    if index < 0:
                        index = 0
                    self.tableWidget.removeColumn(index)
                    deleted += 1

    def resizeTableToFit(self):
        if self.tableWidget.columnCount() > 0:
            new_width = self.tableWidget.columnWidth(0) * self.tableWidget.columnCount()
            self.resize(new_width + 84, self.height())  # self.width() - self.tableWidget.width() yields wrong results

    def plotItems(self):
        data = []
        for item in self.tableWidget.selectedItems():
            data.append(float(item.text()))

        self.updatePlot(data)
        self.toolTabs.setCurrentIndex(2)

    #----------- graph -----------#
    def updatePlot(self, data, append=False):
        if not append:
            if self.data is None:
                self.data = self.plotWidget.plot(data)
            else:
                self.data.updateData(data)
                self.plotWidget.updateMatrix()
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

    def hideEvent(self, QHideEvent):
        if self.toolDetached.isChecked():
            QHideEvent.ignore()
