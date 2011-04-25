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
from PyQt4.QtCore import Qt, QRect, QSize, QTimer, PYQT_VERSION_STR
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
    FIRST, LAST, NEXT, PREV, ABOUT, QUIT,\
    LOAD, LAYERS, DECOM, ANALYSIS, FIN,\
    infoTipsDict, Models, Tabs, Tooltips
from utils.guiTweaks import unfillLayout, createSeparator
from utils.tools import prettifyNames
from stats.parser import DataParser
from gui.guiTool import ToolsFrame
from gui.guiInfo import InfoFrame
from gui.graphWidget import MplWidget
from gui.faderWidget import StackedWidget
from gui.guiMessage import SystemMessage
from stats.models import processModel, calculateForecast

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
        self.comboDecomposition = QComboBox()
        self.spinLevels = QSpinBox()
        self.calculateButton = QPushButton('A&nalyze data')
        self.showScalogram = QPushButton('Show scalogram')
        self.showCoefficients = QPushButton('Show coefficients')
        self.decompInfoLabel = QLabel(u'')
        self.resultsView = QTextEdit()
        self.scalogramGraph = MplWidget()

        self.decompLayout.addWidget(self.comboWavelet, 0, 0)
        self.decompLayout.addWidget(self.comboDecomposition, 0, 1)
        self.decompLayout.addWidget(self.spinLevels, 0, 2)
        self.decompLayout.addWidget(self.calculateButton, 1, 0, 1, 3)
        self.decompLayout.addWidget(self.showScalogram, 2, 0)
        self.decompLayout.addWidget(self.decompInfoLabel, 2, 1)
        self.decompLayout.addWidget(self.showCoefficients, 2, 2)
        self.decompLayout.addWidget(self.resultsView, 3, 0, 1, 3)
        self.decompLayout.addWidget(self.scalogramGraph, 4, 0, 1, 3)

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
        print 'okay.jpeg'
        loadingTime = datetime.now() - start
        self.trayIcon.showMessage('Ready!', 'Launched in ' + str(loadingTime), QSystemTrayIcon.Information,
                                  TRAY_VISIBLE_DELAY)
        QTimer.singleShot(TRAY_ICON_DELAY, self.trayIcon.hide)

        def startingTip():  self.messageInfo.showInfo(self.statTools.currentIndex())

        QTimer.singleShot(LOAD_PAUSE, startingTip)

    #------------------- initialization ------------------#

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
        self.manualDataInput.setHidden(True)
        self.loadManualData.setHidden(True)
        self.parseResults.setHidden(True)
        self.showGraph.setHidden(True)
        self.showTable.setHidden(True)
        self.clearAll.setHidden(True)
        self.separator.setHidden(True)

        self.parseResults.setAlignment(Qt.AlignCenter)

        # wavelets #
        self.comboWavelet.addItems(pywt.families())
        self.comboDecomposition.addItems(['Discrete WT', 'Stationary WT'])
        self.spinLevels.setValue(2)
        self.spinLevels.setRange(2, 10)
        self.resultsView.setHidden(True)
        self.resultsView.setReadOnly(True)
        self.resultsView.setMinimumWidth(WIDTH - 100)
        self.resultsView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scalogramGraph.setVisible(False)
        self.showCoefficients.setVisible(False)
        self.showCoefficients.setCheckable(True)
        self.showScalogram.setVisible(False)
        self.showScalogram.setCheckable(True)
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

    def initActions(self):
        # menu actions #
        quitAction = QAction('&Quit', self)
        #        quitAction.setIcon(QIcon(RES + ICONS + QUIT))
        #        quitAction.setText('Quit')
        quitAction.triggered.connect(self.quitApplication)
        aboutAction = QAction('&About', self)
        #        aboutAction.setIcon(QIcon(RES + ICONS + ABOUT))
        #        aboutAction.setText('About')
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

        self.toolBar.addAction(self.toggleSizeAction)
        self.toolBar.addAction(self.toggleTools)
        self.toolBar.addAction(self.toggleInfo)
        self.toolBar.addAction(launchWizard)
        self.toolBar.addSeparator()
#        self.toolBar.addAction(goToFirstAction)
        self.toolBar.addAction(previousStepAction)
        self.toolBar.addAction(nextStepAction)
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
        self.showScalogram.clicked.connect(self.viewScalogram)
        self.showCoefficients.clicked.connect(self.viewCoeffs)

        # tooltips #
        self.statTools.currentChanged.connect(self.updateInfoTooltips)

        # results #
        self.reconTS.clicked.connect(self.updateResultingTS)
        self.plotInitial.clicked.connect(self.updateResultingTSWithInitialData)

    def setCustomTooltips(self):
        # data input #
        self.loadFromFile.setToolTip(Tooltips['load_from_file'])
        self.toggleManual.setToolTip(Tooltips['load_manual'])

    #------------------- actions ------------------#

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

    def moveEvent(self, event):
        self.updateToolsPosition()
        self.updateInfoPosition()

    def updateToolsPosition(self):
        if not self.toolsFrame.toolDetached.isChecked():
            self.toolsFrame.move(self.x() + self.width() + 20, self.y())

    def updateToolsSize(self):
        if not self.toolsFrame.fixSize.isChecked():
            self.toolsFrame.resize(QSize(self.toolsFrame.width(), self.height()))

    def updateInfoPosition(self):
        #self.infoDialog.move( self.x() - self.infoDialog.width() - 20, self.y() * 3./2. )
        #self.infoDialog.move( self.x() - self.infoDialog.width() - 20, self.y() +  self.infoDialog.height()/2 )
        if self.infoDialog.dockButtonUp.isChecked():
            self.infoDialog.move(self.x() + self.width() / 3, self.y() - self.infoDialog.height() - 20)
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

    #------------------ functionality ----------------#
    def openFile(self):
        if self.openFileDialog.exec_():
            fileName = self.openFileDialog.selectedFiles()   #NB: multiple files selection also possible!
            try:
                if len(fileName) > 0:
                    self.currentDataSet = DataParser.getTimeSeriesFromTextData(data=open(fileName[0], 'r').read())
                    self.showParseResults()
            except Exception:
                QMessageBox.warning(self, 'File error', 'Could not read specified file! ')
                log.error('could not open ' + fileName.takeFirst())

    def manualData(self):
        if self.manualDataInput.toPlainText() != '':
            self.currentDataSet = DataParser.getTimeSeriesFromTextData(self.manualDataInput.toPlainText())
            self.showParseResults()
        else:
            QMessageBox.warning(self, 'Input error', 'Please, at least enter something')

    def showParseResults(self):
        if len(self.currentDataSet) == 2:
            self.parseResults.setText(
                'Success! Loaded<b> ' + str(len(self.currentDataSet[0])) + '</b> values, errors: <b>' + str(
                    self.currentDataSet[1]) + '</b>')
            self.parseResults.setVisible(True)
            self.showGraph.setVisible(True)
            self.showTable.setVisible(True)
            self.clearAll.setVisible(True)
            self.separator.setVisible(True)

            self.statTools.setItemEnabled(int(Tabs.Decomposition), True)

            self.R['data'] = self.currentDataSet[0]
            self.toolsFrame.updateNamespace()
            self.statusBar.showMessage("Added 'data' variable to R namespace")
        else:
            self.parseResults.setText('Could not parse at all!')
            self.parseResults.setVisible(True)

    def resetTips(self):
        for tip in infoTipsDict: infoTipsDict[tip]['seen'] = False
        self.messageInfo.showInfo('Already seen tips will be shown anew')

    def resetData(self):
        self.currentDataSet = []
        self.parseResults.setHidden(True)
        self.showGraph.setHidden(True)
        self.showTable.setHidden(True)
        self.clearAll.setHidden(True)
        self.separator.setHidden(True)

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

        self.resultsView.clear()
        self.scalogramGraph.canvas.ax.clear()
        self.resultsView.setHidden(True)
        self.scalogramGraph.setHidden(True)
        self.showScalogram.setHidden(True)
        self.showCoefficients.setHidden(True)
        self.decompInfoLabel.setHidden(True)
        self.calculateButton.setText('Analyze data')

        self.toolsFrame.hide()

    def updateTable(self):
        if self.showTable.text() == 'Show table':
            self.toolsFrame.updateTable(self.currentDataSet[0])
            self.toolsFrame.show()
            self.toolsFrame.toolTabs.setCurrentIndex(2)
            self.showTable.setText('Hide table')

            self.toggleTools.setChecked(True)
        else:
            self.toolsFrame.hide()
            self.showTable.setText('Show table')
            self.toggleTools.setChecked(False)

    def toggleInputField(self):
        if self.toggleManual.isChecked():
            self.manualDataInput.setVisible(True)
            self.loadManualData.setVisible(True)

            self.manualDataInput.setFocus()
        else:
            self.manualDataInput.setHidden(True)
            self.loadManualData.setHidden(True)

    def showAbout(self):
        QMessageBox.about(self, 'About muScale',
                          'Version:\t' + __version__ + '\nPython:\t' + platform.python_version() +
                          '\nQtCore:\t' + PYQT_VERSION_STR +
                          '\nPlatform:\t' + platform.system())

    def updateGraph(self):
        if self.showGraph.text() == 'Show graph':
            self.currentPlot.updateData(self.currentDataSet[0])
            self.toolsFrame.show()
            self.toolsFrame.toolTabs.setCurrentIndex(1)

            self.showGraph.setText('Hide graph')
            self.toggleTools.setChecked(True)
        else:
            self.toolsFrame.hide()
            self.showGraph.setText('Show graph')
            self.toggleTools.setChecked(False)

    def waveletTransform(self):
    #        self.scalogramGraph.canvas.ax.clear()
    #        self.scalogramGraph.canvas.fig.clear()
        # stationary decomposition flag
        self.isSWT = False

        try:
            self.wavelet = pywt.Wavelet(pywt.wavelist(self.comboWavelet.currentText())[0])
            w_level = self.spinLevels.value() - 1
            if self.comboDecomposition.currentIndex() == 0:
                #cA3, cD3, cD2, cD1, etc
                self.wCoefficients = pywt.wavedec(self.currentDataSet[0], self.wavelet, level=w_level)
            elif self.comboDecomposition.currentIndex() == 1:
                self.wCoefficients = pywt.swt(self.currentDataSet[0], self.wavelet, level=w_level)
                self.isSWT = True

                #TODO: update graphWidget implementation
            self.scalogramGraph.canvas.fig.clear()
            self.resultsView.clear(); i = 0; rows = 0

            if not self.isSWT: rows = len(self.wCoefficients)
            else:
                for item in self.wCoefficients: rows += len(item)

            for coeff in self.wCoefficients:
                if not self.isSWT:
                    ax = self.scalogramGraph.canvas.fig.add_subplot(rows, 1, i + 1)
                    ax.plot(coeff)
                    MplWidget.hideAxes(ax)

                    self.resultsView.append('<b>Level ' + str(i) + ':</b>\t' + str(coeff) + '<br/>'); i += 1
                else:
                    for subcoeff in coeff:
                        ax = self.scalogramGraph.canvas.fig.add_subplot(rows, 1, i + 1)
                        ax.plot(subcoeff)
                        MplWidget.hideAxes(ax)

                        self.resultsView.append('<b>Level ' + str(i) + ':</b>\t' + str(coeff) + '<br/>'); i += 1

                        #self.scalogramGraph.canvas.ax.imshow(vstack(tuple(self.wCoefficients[:-1])), interpolation='nearest')
                        #self.scalogramGraph.canvas.ax.imshow(row_stack(tuple(self.wCoefficients)), interpolation='nearest')
                        #        self.scalogramGraph.canvas.ax1 = self.scalogramGraph.canvas.fig.add_subplot(211)
                        #        self.scalogramGraph.canvas.ax1.plot(self.wCoefficients[-1:])

                        #self.resultsView.setVisible(True)
            #self.scalogramGraph.setVisible(True)

            self.showScalogram.setVisible(True)
            self.showCoefficients.setVisible(True)
            self.decompInfoLabel.setVisible(True)
            self.calculateButton.setText('Reanalyze data')
            self.decompInfoLabel.setText('Using <b>' + self.wavelet.name + '</b> wavelet')

            self.R['wcoeff'] = self.wCoefficients
            self.toolsFrame.updateNamespace()
            self.statusBar.showMessage("Added 'wcoeff' variable to R namespace")

            #self.resultsView.updateGeometry()
            self.constructModelTemplate()
            self.statTools.setItemEnabled(int(Tabs.Model), True)
            #TODO: refactor temporal solution
            self.statTools.setItemEnabled(int(Tabs.Results), True)
            self.processedWCoeffs = None

            self.scalogramGraph.canvas.draw()
            self.update()
        except Exception, e:
            self.messageInfo.showInfo(str(e), True)
            log.error(e)

    def viewScalogram(self):
        if self.showScalogram.isChecked():
            self.scalogramGraph.setVisible(True)
        else:
            self.scalogramGraph.setHidden(True)

    def viewCoeffs(self):
        if self.showCoefficients.isChecked():
            self.resultsView.setVisible(True)
        else:
            self.resultsView.setHidden(True)

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
    #        self.scalogramGraph.canvas.ax.clear()
    #        self.scalogramGraph.canvas.ax.plot()
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
                            #for 1D array (descrete transform)
                            if not self.isSWT:
                                preview.canvas.ax.plot(self.wCoefficients[level.text().right(1).toInt()[0]])
                            # for SWT
                            else:
                                #TODO: somehow, refactor this felony
                                preview.canvas.fig.clear()
                                sub_ax_0 = preview.canvas.fig.add_subplot(211)
                                sub_ax_0.plot(self.wCoefficients[level.text().right(1).toInt()[0]][0])
                                sub_ax_1 = preview.canvas.fig.add_subplot(212)
                                sub_ax_1.plot(self.wCoefficients[level.text().right(1).toInt()[0]][1])

                            preview.setMaximumHeight(P_PREVIEW_HEIGHT)
                            preview.setVisible(True)
                            #                            self.gem = self.saveGeometry()
                            if not self.toggleSizeAction.isChecked():
                                self.gem = self.size()
                            #                            print self.gem.width(), self.gem.height()
                                self.resize(self.width(), self.height() + P_PREVIEW_HEIGHT)
                        else:
                            preview = self.modelLayout.itemAtPosition(row + 2, 0).widget()
                            preview.setHidden(True)

    def constructModelTemplate(self):
        unfillLayout(self.modelLayout)
        #TODO: add use case for level = 2, SWT
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
            componentPreview.setHidden(True)

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
                #                    self.multiModel[level] = self.modelLayout.itemAtPosition(level * 4 + 3 , 0).widget().currentText()
                    self.multiModel[level] = Models(
                        self.modelLayout.itemAtPosition(level * 4 + 3, 0).widget().currentIndex() + 1)
        print self.multiModel
        if self.multiModel == {}:
            QMessageBox.warning(self, 'Undefined model', 'You haven not specified any methods at all!')
        else:
            self.statTools.setItemEnabled(int(Tabs.Simulation), True)
            self.readyModelsStack()

    def readyModelsStack(self):
        if not self.isSWT:
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
            if not self.isSWT: simulationPlot.canvas.ax.plot(self.wCoefficients[model])
            else:
                simulationPlot.canvas.fig.clear()
                sub_ax_0 = simulationPlot.canvas.fig.add_subplot(211)
                sub_ax_0.plot(self.wCoefficients[model][0])
                sub_ax_1 = simulationPlot.canvas.fig.add_subplot(212)
                sub_ax_1.plot(self.wCoefficients[model][1])
                
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
            if not self.isSWT:
                result = processModel(self.multiModel[model], self.wCoefficients[model], self.R)
                self.processedWCoeffs[model] = result

                #TODO: update, but not plot anew (repetitive plotting cause lag)
                modelsStack.currentWidget().canvas.ax.plot(result)
                modelsStack.currentWidget().canvas.draw()
            else:
                pass

        def forecastModel():
            model = modelsList.currentIndex()
            if not self.isSWT:
                result = calculateForecast(self.multiModel[model], self.wCoefficients[model], self.R, forecastSteps.value())
                self.processedWCoeffs[model] = result

                modelsStack.currentWidget().canvas.ax.plot(result)
                modelsStack.currentWidget().canvas.draw()
            else:
                pass

        def resetModel():
            model = modelsList.currentIndex()
            if not self.isSWT:
                modelsStack.currentWidget().canvas.ax.clear()
                modelsStack.currentWidget().canvas.ax.plot(self.wCoefficients[model])
                modelsStack.currentWidget().canvas.draw()
            else:
                pass

        simulateButton = QPushButton('Simulate')
        actionsMenu = QMenu()
        actionsMenu.addAction(QAction('Fit model', self, triggered=constructModel))
        actionsMenu.addAction(QAction('Forecast', self, triggered=forecastModel))
        actionsMenu.addAction(QAction('Reset', self, triggered=resetModel))
        simulateButton.setMenu(actionsMenu)

        #TODO: move to 'additional options'
        forecastSteps = QSpinBox()
        forecastSteps.setRange(2, 100)
        forecastSteps.valueChanged.connect(forecastModel)

        modelsListLayout.addWidget(simulateButton)
        modelsListLayout.addWidget(forecastSteps)
        self.implementLayout.addLayout(modelsListLayout, 0, 0)
        self.implementLayout.addWidget(modelsStack, 1, 0)

    def updateResultingTS(self):
        if self.processedWCoeffs is None:
            if not self.isSWT:
                self.resultingGraph.canvas.ax.clear()
                self.resultingGraph.canvas.ax.plot(pywt.waverec(self.wCoefficients, self.wavelet))
                self.resultingGraph.show()
                self.resultingGraph.canvas.draw()
            else:
                pass
        else:
            try:
                if not self.isSWT:
                    self.resultingGraph.canvas.ax.clear()
                    self.resultingGraph.canvas.ax.plot(pywt.waverec(self.processedWCoeffs, self.wavelet))
                    self.resultingGraph.show()
                    self.resultingGraph.canvas.draw()
                else:
                    pass
            except Exception, e:
                self.messageInfo.showInfo('Not all levels were processed!', True)
                log.error(e)

    def updateResultingTSWithInitialData(self):
        self.resultingGraph.canvas.ax.plot(self.currentDataSet[0])
        self.resultingGraph.show()
        self.resultingGraph.canvas.draw()

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
        #        self.wizard.setWizardStyle(QWizard.ClassicStyle)
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