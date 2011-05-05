# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''

####################################
#            Imports               #
####################################

# internal #
import platform
from datetime import datetime

# external #
from PyQt4.QtCore import Qt, QRect, QSize, QTimer, PYQT_VERSION_STR, QPointF, QPoint
from PyQt4.QtGui import *
from stats.pyper import R
import pywt
from numpy import *

# own #
from utils.log import log
from utils.const import __name__,\
    __version__,\
    WIDTH, HEIGHT,\
    RES, ICONS, ICO_SIZE,\
    FULL_SCREEN, NORMAL_SIZE, LOGO, WIZARD, TOOLS, INFO,\
    P_PREVIEW_HEIGHT,\
    LOAD_PAUSE, TRAY_VISIBLE_DELAY, TRAY_ICON_DELAY,\
    FIRST, LAST, NEXT, PREV, ABOUT, QUIT, TEST, RESET,\
    LOAD, LAYERS, DECOM, ANALYSIS, FIN,\
    infoTipsDict, infoWavelets, WT, WV, Models, Tabs, Tooltips
from utils.guiTweaks import unfillLayout, createSeparator, createShadow,\
    walkNonGridLayoutShadow, walkGridLayoutShadow
from utils.tools import prettifyNames
from stats.parser import DataParser
from gui.guiTool import ToolsFrame
from gui.guiInfo import InfoFrame
from gui.graphWidget import MplWidget
from gui.faderWidget import StackedWidget
from gui.guiMessage import SystemMessage
from stats.models import processModel, calculateForecast
from stats.wavelets import select_levels_from_swt, update_selected_levels_swt, normalize_dwt_dimensions, iswt
from user.test import test_data

####################################
#            GUI classes           #
####################################

class MuScaleMainDialog(QMainWindow):
    def __init__(self, parent=None):
        super(MuScaleMainDialog, self).__init__(parent)

        ### components ###

        # timer #
        start = datetime.now()

        # geometry #
        self.gem = None

        # data loaders #
        self.loadDataGroup = QGroupBox('Data source')
        self.loadDataLayout = QVBoxLayout()

        self.loadFromFile = QPushButton('&Load from file')
        # manual
        self.toggleManual = QPushButton('Manual &input')
        self.manualDataInput = QTextEdit()
        self.loadManualData = QPushButton('Parse')
        # results
        self.parseResults = QLabel('')
        self.showGraph = QPushButton('Show graph')
        self.showTable = QPushButton('Show table')
        self.clearAll = QPushButton('Reset data')

        self.separator = createSeparator()

        self.loadDataLayout.addWidget(self.loadFromFile)
        self.loadDataLayout.addWidget(self.toggleManual)
        self.loadDataLayout.addWidget(self.manualDataInput)
        self.loadDataLayout.addWidget(self.loadManualData)
        self.loadDataLayout.addWidget(self.separator)
        self.loadDataLayout.addWidget(self.parseResults)
        self.loadDataLayout.addWidget(self.showGraph)
        self.loadDataLayout.addWidget(self.showTable)
        self.loadDataLayout.addWidget(self.clearAll)

        self.loadDataGroup.setLayout(self.loadDataLayout)

        # wavelet decomposition #
        self.decompGroup = QGroupBox('Data decomposition')
        self.decompLayout = QGridLayout()

        self.comboWavelet = QComboBox()
        self.comboWavelist = QComboBox()
        self.comboDecomposition = QComboBox()
        self.spinLevels = QSpinBox()
        self.calculateButton = QPushButton('A&nalyze data')
        self.showWavelist = QPushButton('Show wavelist')
        self.showScalogram = QPushButton('Show scalogram')
        self.decompInfoLabel = QLabel(u'')
        self.wavelistGraph = MplWidget()
        self.scalogramGraph = MplWidget()

        self.decompLayout.addWidget(self.comboWavelet, 0, 0)
        self.decompLayout.addWidget(self.comboWavelist, 0, 1)
        self.decompLayout.addWidget(self.comboDecomposition, 0, 2)
        self.decompLayout.addWidget(self.spinLevels, 0, 3)
        self.decompLayout.addWidget(self.calculateButton, 1, 0, 1, 4)
        self.decompLayout.addWidget(self.showWavelist, 2, 0)
        self.decompLayout.addWidget(self.decompInfoLabel, 2, 1, 1, 2)
        self.decompLayout.addWidget(self.showScalogram, 2, 3)
        self.decompLayout.addWidget(self.wavelistGraph, 3, 0, 1, 4)
        self.decompLayout.addWidget(self.scalogramGraph, 4, 0, 1, 4)

        self.decompGroup.setLayout(self.decompLayout)

        # model hierarchy #
        self.modelGroup = QGroupBox('Model structure')
        self.modelLayout = QGridLayout()

        self.modelGroup.setLayout(self.modelLayout)

        # model implementation #
        self.implementGroup = QGroupBox('Model implementation')
        self.implementLayout = QGridLayout()

        self.implementGroup.setLayout(self.implementLayout)

        # model composition #
        self.reconsGroup = QGroupBox('Reconstruction')
        self.reconsLayout = QGridLayout()

        self.reconTS = QPushButton('Update from WT coeff''s')
        self.plotInitial = QPushButton('Plot initial data')
        self.resultingGraph = MplWidget()

        self.reconsLayout.addWidget(self.reconTS,0, 0)
        self.reconsLayout.addWidget(self.plotInitial, 0, 1)
        self.reconsLayout.addWidget(self.resultingGraph, 1, 0, 1, 2)

        self.reconsGroup.setLayout(self.reconsLayout)

        # menus, toolbars, layouts & composition #
        self.centralWidget = QWidget(self)

        self.statTools = QToolBox()
        self.statTools.addItem(self.loadDataGroup, 'Loading &data')
        self.statTools.addItem(self.decompGroup, 'Anal&yzing data')
        self.statTools.addItem(self.modelGroup, '&Multiscale model')
        self.statTools.addItem(self.implementGroup, '&Simulation')
        self.statTools.addItem(self.reconsGroup, '&Results')

        self.menuBar = QMenuBar()
        self.toolBar = QToolBar()
        self.statusBar = QStatusBar()

        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainLayout.addWidget(self.statTools)

        self.addToolBar(self.toolBar)
        self.setMenuBar(self.menuBar)
        self.setStatusBar(self.statusBar)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.setCentralWidget(self.centralWidget)

        self.trayIcon = QSystemTrayIcon(self)

        # dialogs #
        self.openFileDialog = QFileDialog(self)

        # session variables #
        self.currentDataSet = []
        self.currentPlot = None
        self.multiModel = {}

        ### initialization ###
        self.initComposition()
        self.initComponents()
        self.initActions()

        # computational modules #
        self.trayIcon.show()
        self.trayIcon.showMessage('Loading...', 'Initializing R', QSystemTrayIcon.Information, TRAY_VISIBLE_DELAY)
        self.R = R()

        # external gui modules #
        self.wizard = None
        self.toolsFrame = ToolsFrame(self.R, self)
        self.currentPlot = self.toolsFrame.plotWidget.plot()
        self.infoDialog = InfoFrame(self)
        self.messageInfo = SystemMessage(self)

        ### start ###
        self.statusBar.showMessage('Ready!')

        ### test ###
        loadingTime = datetime.now() - start
        self.trayIcon.showMessage('Ready!', 'Launched in ' + str(loadingTime), QSystemTrayIcon.Information,
                                  TRAY_VISIBLE_DELAY)
        QTimer.singleShot(TRAY_ICON_DELAY, self.trayIcon.hide)

        def startingTip():  self.messageInfo.showInfo(self.statTools.currentIndex())

        QTimer.singleShot(LOAD_PAUSE, startingTip)

        self.toolsFrame.updateLog(['muScale ' + __version__ + ' launched', 'loading time: ' + str(loadingTime)])

#------------------- initialization ------------------# #--------------- * * * ---------------#
    def initComposition(self):
        self.setWindowTitle(__name__ + ' ' + __version__)

        desktop = QApplication.desktop()
        self.setGeometry(QRect((desktop.width() - WIDTH) / 2, (desktop.height() - HEIGHT) / 2, WIDTH, HEIGHT))

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWindowIcon(QIcon(RES + ICONS + LOGO))

        self.setStyleSheet('QToolTip { background-color: black; color: white; border: 1px solid white; border-radius: 2px; }')

    def initComponents(self):
        # load data items #
        self.toggleManual.setCheckable(True)
        self.manualDataInput.hide()
        self.loadManualData.hide()
        self.parseResults.hide()
        self.showGraph.hide()
        self.showTable.hide()
        self.clearAll.hide()
        self.separator.hide()

        self.parseResults.setAlignment(Qt.AlignCenter)

        # wavelets #
        self.comboWavelet.addItems(pywt.families())
#        self.comboDecomposition.addItems(['Stationary WT', 'Discrete WT'])
        self.comboDecomposition.addItems(WT._enums.values())
        self.spinLevels.setValue(2)
        self.spinLevels.setRange(2, 10)
        self.wavelistGraph.setVisible(False)
        self.scalogramGraph.setVisible(False)
        self.showScalogram.setVisible(False)
        self.showScalogram.setCheckable(True)
        self.showWavelist.setVisible(False)
        self.showWavelist.setCheckable(True)
        self.decompInfoLabel.setVisible(False)
        self.decompInfoLabel.setAlignment(Qt.AlignCenter)

        self.decompLayout.setAlignment(Qt.AlignCenter)

        # model #
        #self.modelLayout.setAlignment(Qt.AlignCenter)

        # dialogs #
        self.openFileDialog.setFileMode(QFileDialog.ExistingFile)
        self.openFileDialog.setViewMode(QFileDialog.List)

        # layouts #
        self.loadDataLayout.setAlignment(Qt.AlignCenter)

        # tabs #
        self.statTools.setItemEnabled(int(Tabs.Decomposition), False)
        self.statTools.setItemEnabled(int(Tabs.Model), False)
        self.statTools.setItemEnabled(int(Tabs.Simulation), False)
        self.statTools.setItemEnabled(int(Tabs.Results), False)

        # etc #
        self.trayIcon.setIcon(QIcon(RES + ICONS + LOGO))
        self.toolBar.setIconSize(QSize(ICO_SIZE, ICO_SIZE))

        # results #
        self.resultingGraph.setVisible(False)

        # tooltips #
        self.setCustomTooltips()

        # tabs icons #
        self.statTools.setItemIcon(int(Tabs.Data), QIcon(RES + ICONS + LOAD))
        self.statTools.setItemIcon(int(Tabs.Decomposition), QIcon(RES + ICONS + DECOM))
        self.statTools.setItemIcon(int(Tabs.Model), QIcon(RES + ICONS + LAYERS))
        self.statTools.setItemIcon(int(Tabs.Simulation), QIcon(RES + ICONS + ANALYSIS))
        self.statTools.setItemIcon(int(Tabs.Results), QIcon(RES + ICONS + FIN))

        # effects #
        walkNonGridLayoutShadow(self.loadDataLayout)
        walkGridLayoutShadow(self.decompLayout)
        walkGridLayoutShadow(self.reconsLayout)

#        self.toolBar.setGraphicsEffect(self.shadow)
#        self.toolBar.setMovable(False)
#        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

    def initActions(self):
        # menu actions #
        quitAction = QAction('&Quit', self)
        #        quitAction.setIcon(QIcon(RES + ICONS + QUIT))
        quitAction.triggered.connect(self.quitApplication)
        aboutAction = QAction('&About', self)
        #        aboutAction.setIcon(QIcon(RES + ICONS + ABOUT))
        aboutAction.triggered.connect(self.showAbout)
        resetTipsAction = QAction('Reset &tips', self)
        resetTipsAction.triggered.connect(self.resetTips)

        self.menuBar.addAction(resetTipsAction)
        self.menuBar.addAction(aboutAction)
        self.menuBar.addAction(quitAction)

        # context menu #
        goToFirstAction = QAction('To the first step', self)
        goToFirstAction.setIcon(QIcon(RES + ICONS + FIRST))
        goToFirstAction.triggered.connect(self.goToFirstStep)
        goToLastAction = QAction('To the last step', self)
        goToLastAction.setIcon(QIcon(RES + ICONS + LAST))
        goToLastAction.triggered.connect(self.goToLastStep)
        nextStepAction = QAction('Next step', self)
        nextStepAction.setShortcut(QKeySequence('Ctrl+N'))
        nextStepAction.setIcon(QIcon(RES + ICONS + NEXT))
        nextStepAction.triggered.connect(self.nextStep)
        previousStepAction = QAction('Previous step', self)
        previousStepAction.setShortcut(QKeySequence('Ctrl+B'))
        previousStepAction.setIcon(QIcon(RES + ICONS + PREV))
        previousStepAction.triggered.connect(self.previousStep)

        self.addAction(nextStepAction)
        self.addAction(previousStepAction)
        self.addAction(goToFirstAction)
        self.addAction(goToLastAction)
        #        self.addAction(aboutAction)
        #        self.addAction(quitAction)

        # toolbar #
        self.toggleSizeAction = QAction('Full screen', self)
        self.toggleSizeAction.triggered.connect(self.fullScreen)
        self.toggleSizeAction.setCheckable(True)
        self.toggleSizeAction.setIcon(QIcon(RES + ICONS + FULL_SCREEN))

        self.toggleTools = QAction('Show tools', self)
        self.toggleTools.triggered.connect(self.showTools)
        self.toggleTools.setCheckable(True)
        self.toggleTools.setIcon(QIcon(RES + ICONS + TOOLS))

        launchWizard = QAction('Launch wizard', self)
        launchWizard.triggered.connect(self.showWizard)
        launchWizard.setIcon(QIcon(RES + ICONS + WIZARD))

        self.toggleInfo = QAction('Show info', self)
        self.toggleInfo.setCheckable(True)
        self.toggleInfo.setIcon(QIcon(RES + ICONS + INFO))
        self.toggleInfo.triggered.connect(self.updateInfoTooltips)

        quickTest = QAction(QIcon(RES + ICONS + TEST), 'Full modelling cycle', self)
        resetAll = QAction(QIcon(RES + ICONS + RESET), 'Reset all', self)
        quickTest.triggered.connect(self.performModellingCycleGUI)
        resetAll.triggered.connect(self.resetData)

        self.toolBar.addAction(self.toggleSizeAction)
        self.toolBar.addAction(self.toggleTools)
        self.toolBar.addAction(self.toggleInfo)
        self.toolBar.addAction(launchWizard)
        self.toolBar.addSeparator()
#        self.toolBar.addAction(goToFirstAction)
        self.toolBar.addAction(previousStepAction)
        self.toolBar.addAction(nextStepAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(quickTest)
        self.toolBar.addAction(resetAll)

#        self.toolBar.addAction(goToLastAction)

        # load data actions #
        self.toggleManual.clicked.connect(self.toggleInputField)
        self.loadFromFile.clicked.connect(self.openFile)
        self.loadManualData.clicked.connect(self.manualData)
        self.clearAll.clicked.connect(self.resetData)
        self.showTable.clicked.connect(self.updateTable)
        self.showGraph.clicked.connect(self.updateGraph)

        # wavelet decomposition actions #
        self.calculateButton.clicked.connect(self.waveletTransform)
        self.showWavelist.clicked.connect(self.viewWavelist)
        self.showScalogram.clicked.connect(self.viewScalogram)
        self.comboDecomposition.currentIndexChanged.connect(self.updateMaxDLevel)
        self.comboWavelet.currentIndexChanged.connect(self.updateWavelist)
        self.comboWavelist.currentIndexChanged.connect(self.updateWaveletPreview)

        # tooltips #
        self.statTools.currentChanged.connect(self.updateInfoTooltips)

        # results #
        self.reconTS.clicked.connect(self.updateResultingTS)
        self.plotInitial.clicked.connect(self.updateResultingTSWithInitialData)

    def setCustomTooltips(self):
        # data input #
        self.loadFromFile.setToolTip(Tooltips['load_from_file'])
        self.toggleManual.setToolTip(Tooltips['load_manual'])

        # level
        self.spinLevels.setToolTip(Tooltips['max_level'])

#------------------- actions ------------------# #--------------- * * * ---------------#
    def fullScreen(self):
        if self.toggleSizeAction.isChecked():
            self.showFullScreen()
            self.toggleSizeAction.setIcon(QIcon(RES + ICONS + NORMAL_SIZE))
        else:
            self.showNormal()
            self.toggleSizeAction.setIcon(QIcon(RES + ICONS + FULL_SCREEN))

    def showTools(self):
        if self.toggleTools.isChecked():
            self.toolsFrame.show()
        else:
            self.toolsFrame.hide()

    def resizeEvent(self, event):
        self.updateToolsPosition()
        self.updateToolsSize()
        self.updateMessagePosition()

    def moveEvent(self, event):
        self.updateToolsPosition()
        self.updateInfoPosition()
        self.updateMessagePosition()

    def updateToolsPosition(self):
        if not self.toolsFrame.toolDetached.isChecked():
            self.toolsFrame.move(self.x() + self.width() + 20, self.y())

    def updateToolsSize(self):
        if not self.toolsFrame.fixSize.isChecked():
            self.toolsFrame.resize(QSize(self.toolsFrame.width(), self.height()))

    def updateMessagePosition(self):
        self.messageInfo.move(self.x() + (self.width() - self.messageInfo.width())/2, self.y() + self.height() + self.messageInfo.height())

    def updateInfoPosition(self):
        if self.infoDialog.dockButtonUp.isChecked():
            self.infoDialog.move(self.x() + self.width() / 3, self.y() - self.infoDialog.height())
        elif self.infoDialog.dockButtonDown.isChecked():
            self.infoDialog.move(self.x() + self.width() / 3, self.y() + self.height() + 60)
        else:
            self.infoDialog.move(self.x() - self.infoDialog.width() - 20, self.y() + self.height() / 3)

    def goToFirstStep(self):
        self.statTools.setCurrentIndex(0)

    def goToLastStep(self):
        if self.statTools.isItemEnabled(self.statTools.count() - 1):
            self.statTools.setCurrentIndex(self.statTools.count() - 1)

    def nextStep(self):
        if self.statTools.currentIndex() + 1 != self.statTools.count():
            if self.statTools.isItemEnabled(self.statTools.currentIndex() + 1):
                self.statTools.setCurrentIndex(self.statTools.currentIndex() + 1)

    def previousStep(self):
        if self.statTools.currentIndex() - 1 >= 0:
            if self.statTools.isItemEnabled(self.statTools.currentIndex() - 1):
                self.statTools.setCurrentIndex(self.statTools.currentIndex() - 1)

#------------------ functionality ----------------# #--------------- * * * ---------------#

###################################################
#------------------ loading data -----------------#
###################################################
    def openFile(self):
        self.resetData()
        if self.openFileDialog.exec_():
            fileName = self.openFileDialog.selectedFiles()
            try:
                if len(fileName) > 0:
                    if DataParser.istextfile(fileName[0]):
                        self.currentDataSet = DataParser.getTimeSeriesFromTextData(data=open(fileName[0], 'r').read())
                        self.toolsFrame.updateLog(['loading data from file:', fileName[0]])
                        self.showParseResults()
                    else:
                        self.messageInfo.showInfo('Binary file specified!', True)
            except Exception:
                self.messageInfo.showInfo('Could not read from specified file!', True)
                self.toolsFrame.updateLog(['error reading file:', fileName[0]], True)
                log.error('could not open ' + fileName[0])

    def manualData(self):
        self.resetData()
        if self.manualDataInput.toPlainText() != '':
            self.currentDataSet = DataParser.getTimeSeriesFromTextData(self.manualDataInput.toPlainText())
            self.toolsFrame.updateLog(['data entered manually'])
            self.showParseResults()
        else:
            self.messageInfo.showInfo('Would you kindly enter at least something?', True)

    def showParseResults(self):
        if len(self.currentDataSet) == 2:   # data and status
            self.parseResults.setText(
                'Success! Loaded<b> ' + str(len(self.currentDataSet[0])) + '</b> values, errors: <b>' + str(
                    self.currentDataSet[1]) + '</b>')
            self.parseResults.show()
            self.showGraph.show()
            self.showTable.show()
            self.clearAll.show()
            self.separator.show()

            self.statTools.setItemEnabled(int(Tabs.Decomposition), True)
            self.updateWavelist()
            self.updateMaxDLevel()

            self.R['data'] = self.currentDataSet[0]
            self.toolsFrame.updateNamespace()
            self.statusBar.showMessage("Added 'data' variable to R namespace")

            self.toolsFrame.updateLog([str(len(self.currentDataSet[0])) + ' values loaded'])
        else:
            self.parseResults.setText('Could not parse at all!')
            self.parseResults.show()

    def resetTips(self):
        for tip in infoTipsDict: infoTipsDict[tip]['seen'] = False
        self.messageInfo.showInfo('Already seen tips will be shown anew')

    def resetData(self):
        self.currentDataSet = []
        self.parseResults.hide()
        self.showGraph.hide()
        self.showTable.hide()
        self.clearAll.hide()
        self.separator.hide()

        self.toolsFrame.tableWidget.setRowCount(0)
        self.showTable.setText('Show table')

        self.currentPlot.free()
        self.toolsFrame.plotWidget.update()
        self.showGraph.setText('Show graph')

        self.statTools.setItemEnabled(int(Tabs.Decomposition), False)
        self.statTools.setItemEnabled(int(Tabs.Model), False)
        self.statTools.setItemEnabled(int(Tabs.Simulation), False)
        self.statTools.setItemEnabled(int(Tabs.Results), False)
        self.statusBar.showMessage('Data cleared')

        self.wavelistGraph.canvas.ax.clear()
        self.wavelistGraph.hide()
        self.scalogramGraph.clearCanvas()
        self.scalogramGraph.hide()
        self.showWavelist.hide()
        self.showScalogram.hide()
        self.decompInfoLabel.hide()
        self.calculateButton.setText('Perform &wavelet decomposition')

        self.toolsFrame.updateLog(['data reset'], warning=True)
        self.showScalogram.setChecked(False)
        self.showWavelist.setChecked(False)
        # clearing R workspace
        self.R('rm(list = ls())')
        self.toolsFrame.updateNamespace()

#        self.messageInfo.showInfo("Data's been reset")

    def updateTable(self):
        if self.showTable.text() == 'Show table':
            self.toolsFrame.updateTable(self.currentDataSet[0])
            self.toolsFrame.show()
            self.toolsFrame.toolTabs.setCurrentIndex(3)
            self.showTable.setText('Hide table')

            self.toggleTools.setChecked(True)
        else:
            self.toolsFrame.hide()
            self.showTable.setText('Show table')
            self.toggleTools.setChecked(False)

    def toggleInputField(self):
        if self.toggleManual.isChecked():
            self.manualDataInput.show()
            self.loadManualData.show()

            self.manualDataInput.setFocus()
        else:
            self.manualDataInput.hide()
            self.loadManualData.hide()

    def updateGraph(self):
        if self.showGraph.text() == 'Show graph':
            self.currentPlot.updateData(self.currentDataSet[0])
            self.toolsFrame.show()
            self.toolsFrame.toolTabs.setCurrentIndex(2)

            self.showGraph.setText('Hide graph')
            self.toggleTools.setChecked(True)
        else:
            self.toolsFrame.hide()
            self.showGraph.setText('Show graph')
            self.toggleTools.setChecked(False)

#####################################################
#-------------- wavelet decomposition --------------#
#####################################################
    def updateWavelist(self):
        self.comboWavelist.clear()
        self.comboWavelist.addItems(pywt.wavelist(self.comboWavelet.currentText()))
        self.comboWavelet.setToolTip(infoWavelets[unicode(self.comboWavelet.currentText())])

    def updateWaveletPreview(self):
        self.comboWavelist.setToolTip("<img src='" + RES + WV + self.comboWavelist.currentText() + "'.png'>")

    def updateMaxDLevel(self):
        if self.comboDecomposition.currentIndex() is int(WT.DiscreteWT) - 1:
            self.spinLevels.setMaximum( pywt.dwt_max_level(len(self.currentDataSet[0]), pywt.Wavelet(unicode(self.comboWavelist.currentText()))) + 1)
            self.comboDecomposition.setToolTip(Tooltips['dwt'])
        elif self.comboDecomposition.currentIndex() is int(WT.StationaryWT) - 1:
            self.spinLevels.setMaximum( pywt.swt_max_level(len(self.currentDataSet[0])) + 1)
            self.comboDecomposition.setToolTip(Tooltips['swt'])
        self.spinLevels.setToolTip(' '.join(str(self.spinLevels.toolTip()).split(' ')[:-1]) + ' <b>' + str(self.spinLevels.maximum()) + '</b>')
        self.spinLevels.setValue(self.spinLevels.maximum()/2 + 1)

    def waveletTransform(self):
        # stationary decomposition flag
        self.isSWT = False

        try:
            self.wavelet = pywt.Wavelet(unicode(self.comboWavelist.currentText()))
            w_level = self.spinLevels.value() - 1
            # discrete
            if self.comboDecomposition.currentIndex() is int(WT.DiscreteWT) - 1:
                self.wInitialCoefficients = pywt.wavedec(self.currentDataSet[0], self.wavelet, level=w_level)
                self.wCoefficients = self.wInitialCoefficients
            # stationary
            elif self.comboDecomposition.currentIndex() is int(WT.StationaryWT) - 1:
                self.wInitialCoefficients = pywt.swt(self.currentDataSet[0], self.wavelet, level=w_level)
                self.wCoefficients = select_levels_from_swt(self.wInitialCoefficients)
                self.isSWT = True

            # resulting wavelist
            self.wavelistGraph.clearCanvas(repaint_axes=False)
            rows = len(self.wCoefficients);  i = 0
            for coeff in self.wCoefficients:
                 ax = self.wavelistGraph.canvas.fig.add_subplot(rows, 1, i + 1); i += 1
                 ax.plot(coeff)
                 MplWidget.hideAxes(ax)
                
            self.wavelistGraph.show()
            self.showWavelist.setChecked(True)

            # resulting scalogram
            if not self.isSWT: self.scalogramGraph.scalogram(normalize_dwt_dimensions(self.wCoefficients))
            else: self.scalogramGraph.scalogram(self.wCoefficients)

            self.showWavelist.show()
            self.showScalogram.show()
            self.decompInfoLabel.show()
            self.calculateButton.setText('Update &wavelet decomposition')
            self.decompInfoLabel.setText('Using <b>' + self.wavelet.name + '</b> wavelet')

            self.R['wcoeff'] = self.wCoefficients
            self.toolsFrame.updateNamespace()
            self.statusBar.showMessage("Added 'wcoeff' variable to R namespace")

            self.constructModelTemplate()
            self.statTools.setItemEnabled(int(Tabs.Model), True)
            self.processedWCoeffs = None

            self.wavelistGraph.canvas.draw()
            self.update()

            if self.isSWT: self.toolsFrame.updateLog(['performed SWT'])
            else: self.toolsFrame.updateLog(['performed DWT'])
            self.toolsFrame.updateLog(['decomposed to ' + str(w_level + 1) + ' levels using ' + self.wavelet.name + ' wavelet'])
        except Exception, e:
            self.messageInfo.showInfo(str(e), True)
            self.toolsFrame.updateLog([str(e)], True)
            log.error(e)

    def viewWavelist(self):
        if self.showWavelist.isChecked():
            self.wavelistGraph.show()
        else:
            self.wavelistGraph.hide()

    def viewScalogram(self):
        if self.showScalogram.isChecked():
            self.scalogramGraph.show()
        else:
            self.scalogramGraph.hide()

####################################################
#----------------- model structure ----------------#
####################################################
    def addAllLevelToModel(self):
        for row in range(0, self.modelLayout.rowCount()):
            if self.modelLayout.itemAtPosition(row, 1) is not None:
                widget = self.modelLayout.itemAtPosition(row, 1).widget()
                if hasattr(widget, 'isCheckable'):
                    if widget.isCheckable():
                        if not widget.isChecked():
                            widget.click()

    def previewAll(self):
        for row in range(0, self.modelLayout.rowCount()):
            if self.modelLayout.itemAtPosition(row, 2) is not None:
                widget = self.modelLayout.itemAtPosition(row, 2).widget()
                if hasattr(widget, 'isCheckable'):
                    if widget.isCheckable():
                        widget.click()

    def autoModel(self):
        #TODO: Implement automatic configuration
        combo = self.modelLayout.itemAt(self.modelLayout.count() - 5).widget()
        combo.setCurrentIndex(1)

    def showComponentPreview(self):
    #        self.wavelistGraph.canvas.ax.clear()
    #        self.wavelistGraph.canvas.ax.plot()
        if self.gem is not None:
            if not self.toggleSizeAction.isChecked():
            #                self.restoreGeometry(self.gem)
                self.resize(self.width(), self.gem.height())
            self.gem = None

        for row in range(0, self.modelLayout.rowCount()):
            if self.modelLayout.itemAtPosition(row, 2) is not None:
                widget = self.modelLayout.itemAtPosition(row, 2).widget()
                if hasattr(widget, 'isCheckable'):
                    if widget.isCheckable():
                        if widget.isChecked():
                            preview = self.modelLayout.itemAtPosition(row + 2, 0).widget()
                            level = self.modelLayout.itemAtPosition(row, 0).widget()
                            preview.canvas.ax.plot(self.wCoefficients[level.text().right(1).toInt()[0]])

                            preview.setMaximumHeight(P_PREVIEW_HEIGHT)
                            preview.show()
                            #                            self.gem = self.saveGeometry()
                            if not self.toggleSizeAction.isChecked():
                                self.gem = self.size()
                                self.resize(self.width(), self.height() + P_PREVIEW_HEIGHT)
                        else:
                            preview = self.modelLayout.itemAtPosition(row + 2, 0).widget()
                            preview.hide()

    def constructModelTemplate(self):
        unfillLayout(self.modelLayout)
        nLevels = len(self.wCoefficients)

        addAll = QPushButton()
        previewAll = QPushButton()
        autoAll = QPushButton()
        addAll.setText('Add all')
        #        addAll.setCheckable(True)
        previewAll.setText('Preview all')
        previewAll.setCheckable(True)
        autoAll.setText('Auto model')
        #        autoAll.setCheckable(True)

        addAll.clicked.connect(self.addAllLevelToModel)
        previewAll.clicked.connect(self.previewAll)
        autoAll.clicked.connect(self.autoModel)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(addAll)
        buttonsLayout.addWidget(autoAll)
        buttonsLayout.addWidget(previewAll)

        self.modelLayout.addLayout(buttonsLayout, 0, 0, 1, 3)
        self.modelLayout.addWidget(createSeparator(), 1, 0, 1, 3)

        i = 2
        for level in range(0, nLevels):
            labelModel = QLabel('Level ' + str(level))

            addModel = QToolButton()
            addModel.setText('+')
            addModel.setCheckable(True)
            addModel.clicked.connect(self.addModel)

            comboModel = QComboBox()
            comboModel.addItems(
                prettifyNames(Models._enums.values()))

            togglePreview = QToolButton()
            togglePreview.setText('Preview')
            togglePreview.setCheckable(True)
            togglePreview.clicked.connect(self.showComponentPreview)

            componentPreview = MplWidget()
            componentPreview.hide()

            self.modelLayout.addWidget(labelModel, i, 0)
            self.modelLayout.addWidget(addModel, i, 1)
            self.modelLayout.addWidget(togglePreview, i, 2);            i += 1
            self.modelLayout.addWidget(comboModel, i, 0, 1, 3);            i += 1
            self.modelLayout.addWidget(componentPreview, i, 0, 1, 3);            i += 1
            self.modelLayout.addWidget(createSeparator(), i, 0, 1, 3);            i += 1

        resetModel = QPushButton('Reset model setup')
        resetModel.clicked.connect(self.resetModel)
        constructModel = QPushButton('Construct multiscale model')
        constructModel.clicked.connect(self.constructModel)

        self.modelLayout.addWidget(resetModel, i, 0, 1, 3); i += 1
        self.modelLayout.addWidget(constructModel, i + 1, 0, 1, 3)

        walkNonGridLayoutShadow(buttonsLayout)
        walkGridLayoutShadow(self.modelLayout)

    def addModel(self):
        for row in range(0, self.modelLayout.rowCount()):
            if self.modelLayout.itemAtPosition(row, 1) is not None:
                widget = self.modelLayout.itemAtPosition(row, 1).widget()
                if hasattr(widget, 'isCheckable'):
                    if widget.isCheckable():
                        if widget.isChecked():
                            widget.setText('OK')
                            combo = self.modelLayout.itemAtPosition(row + 1, 0).widget()
                            combo.setDisabled(True)
                        else:
                            widget.setText('+')
                            combo = self.modelLayout.itemAtPosition(row + 1, 0).widget()
                            combo.setEnabled(True)

    def resetModel(self):
        self.constructModelTemplate()
        self.statTools.setItemEnabled(int(Tabs.Simulation), False)

    def constructModel(self):
        self.multiModel.clear()
        for level in range(0, len(self.wCoefficients)):
            widget = self.modelLayout.itemAtPosition(level * 4 + 2, 1).widget()
            if isinstance(widget, QWidget):
                if widget.isChecked():
                    self.multiModel[level] = Models(
                        self.modelLayout.itemAtPosition(level * 4 + 3, 0).widget().currentIndex() + 1)
        if self.multiModel == {}:
            self.messageInfo.showInfo('You haven not specified any methods at all!', True)
        else:
            self.statTools.setItemEnabled(int(Tabs.Simulation), True)
            self.readyModelsStack()
            self.statTools.setItemEnabled(int(Tabs.Results), True)
            self.toolsFrame.updateLog(['multiscale model complete'])

###################################################
#-------------- model simulation -----------------#
###################################################
    def readyModelsStack(self):
        self.processedWCoeffs = [0] * len(self.wCoefficients)

        unfillLayout(self.implementLayout)

        previousModel = QToolButton()
        previousModel.setText('<')
        nextModel = QToolButton()
        nextModel.setText('>')
        modelsList = QComboBox()

        modelsStack = StackedWidget()
        modelsListLayout = QHBoxLayout()

        for model in self.multiModel:

            modelsList.addItem(str(model) + '. ' + self.multiModel[model].enumname.replace('_', ' '))

            simulationPlot = MplWidget()
            simulationPlot.canvas.ax.plot(self.wCoefficients[model])

            modelsStack.addWidget(simulationPlot)

        modelsListLayout.addWidget(previousModel)
        modelsListLayout.addWidget(modelsList)
        modelsListLayout.addWidget(nextModel)

        def changeStackPage(): modelsStack.setCurrentIndex(modelsList.currentIndex())

        modelsList.currentIndexChanged.connect(changeStackPage)

        def nextM():
            if modelsList.currentIndex() + 1 < modelsList.count():
                modelsList.setCurrentIndex(modelsList.currentIndex() + 1)
            else:
                modelsList.setCurrentIndex(0)

        def prevM():
            if modelsList.currentIndex() - 1 > -1:
                modelsList.setCurrentIndex(modelsList.currentIndex() - 1)
            else:
                modelsList.setCurrentIndex(modelsList.count() - 1)

        nextModel.clicked.connect(nextM)
        previousModel.clicked.connect(prevM)

        modelsListLayout.setAlignment(Qt.AlignCenter)

        #TODO: move into class namespace and refactor
        def constructModel():
            model = modelsList.currentIndex()
            result = processModel(self.multiModel[model], self.wCoefficients[model], self.R)
            self.processedWCoeffs[model] = result

            #TODO: update, but without plotting anew (repetitive plotting causes lag)
            modelsStack.currentWidget().canvas.ax.plot(result)
            modelsStack.currentWidget().canvas.draw()

        def forecastModel():
            model = modelsList.currentIndex()
            result = calculateForecast(self.multiModel[model], self.wCoefficients[model], self.R, forecastSteps.value())
            self.processedWCoeffs[model] = result

            modelsStack.currentWidget().canvas.ax.plot(result)
            modelsStack.currentWidget().canvas.draw()

        def resetModel():
            model = modelsList.currentIndex()
            modelsStack.currentWidget().canvas.ax.clear()
            modelsStack.currentWidget().canvas.ax.plot(self.wCoefficients[model])
            modelsStack.currentWidget().canvas.draw()

        simulateButton = QPushButton('Simulate')
        actionsMenu = QMenu()
        actionsMenu.addAction(QAction('Fit model', self, triggered=constructModel))
        actionsMenu.addAction(QAction('Forecast', self, triggered=forecastModel))
        actionsMenu.addAction(QAction('Reset', self, triggered=resetModel))
        simulateButton.setMenu(actionsMenu)

        #TODO: move to 'additional options'
        forecastSteps = QSpinBox()
        forecastSteps.setRange(2, 100)
        forecastSteps.setValue(20)
        forecastSteps.valueChanged.connect(forecastModel)

        modelsListLayout.addWidget(simulateButton)
        modelsListLayout.addWidget(forecastSteps)
        self.implementLayout.addLayout(modelsListLayout, 0, 0)
        self.implementLayout.addWidget(modelsStack, 1, 0)

        walkNonGridLayoutShadow(modelsListLayout)

    def updateResultingTS(self):
        if self.processedWCoeffs is None:
            self.resultingGraph.canvas.ax.clear()
            self.resultingGraph.canvas.ax.plot(pywt.waverec(self.wCoefficients, self.wavelet))
            self.resultingGraph.show()
            self.resultingGraph.canvas.draw()
        else:
            try:
                self.resultingGraph.canvas.ax.clear()
                if not self.isSWT:
                    self.resultingGraph.canvas.ax.plot(pywt.waverec(self.processedWCoeffs, self.wavelet))
                else:
                    self.resultingGraph.canvas.ax.plot(iswt(update_selected_levels_swt(self.wInitialCoefficients, self.processedWCoeffs), self.wavelet))
                self.resultingGraph.show()
                self.resultingGraph.canvas.draw()
            except Exception, e:
#                self.messageInfo.showInfo('Not all levels were processed!', True)
                self.messageInfo.showInfo(str(e), True)
                self.toolsFrame.updateLog([str(e)], True)
                log.error(e)

#####################################################
#-------------- resulting forecast -----------------#
#####################################################
    def updateResultingTSWithInitialData(self):
        self.resultingGraph.canvas.ax.plot(self.currentDataSet[0])
        self.resultingGraph.show()
        self.resultingGraph.canvas.draw()

#####################################################
#------------- utilities and modules ---------------#
#####################################################
    def showWizard(self):
        self.wizard = QWizard()

        page = QWizardPage()
        page.setTitle("Introduction")
        label = QLabel('Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. \
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.')

        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)
        #        page.setPixmap(QWizard.LogoPixmap, QPixmap(RES + ICONS + LOGO))

        self.wizard.addPage(page)
        self.wizard.setWindowTitle("A Wizard")
        self.wizard.setPixmap(QWizard.LogoPixmap, QPixmap(RES + ICONS + LOGO))
        self.wizard.show()

    def quitApplication(self):
        self.close()

    def updateInfoTooltips(self):
        self.messageInfo.showInfo(self.statTools.currentIndex())
        if self.toggleInfo.isChecked():
            self.infoDialog.updateContents(self.statTools.currentIndex())
            self.infoDialog.show()
            self.updateInfoPosition()
        else:
            self.infoDialog.hide()
            
    def showAbout(self):
        QMessageBox.about(self, 'About muScale',
                          'Version:\t' + __version__ + '\nPython:\t' + platform.python_version() +
                          '\nQtCore:\t' + PYQT_VERSION_STR +
                          '\nPlatform:\t' + platform.system())

#####################################################
#---------------------- tests ----------------------#
#####################################################

    def performModellingCycleGUI(self):
        #TODO: add similar option to wizard
        self.toolsFrame.updateLog(['starting modelling cycle test...'], NB=True)
        # loading data
        self.manualDataInput.setText(' '.join([str(value) for value in test_data]))
        # parse data
        self.manualData()
        # perform SWT
        self.spinLevels.setValue(4)
        self.waveletTransform()
        # construct model
        self.autoModel()
        self.addAllLevelToModel()
        self.constructModel()

        self.toolsFrame.updateLog(['modelling cycle test complete'], NB=True)
        self.messageInfo.showInfo('Modelling cycle performed successfully')
        
        self.statTools.setCurrentIndex(int(Tabs.Simulation))
