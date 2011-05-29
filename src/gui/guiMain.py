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
import traceback
from datetime import datetime

# external #
from PyQt4.QtCore import Qt, QRect, QSize, QTimer,\
                PYQT_VERSION_STR, QPointF, QPoint, QObject, QEvent, \
                pyqtSignal, QThread
from PyQt4.QtGui import *       #TODO: fix imports to parsimonious ones!
from stats.pyper import R
import pywt
from numpy import ndarray

# own #
from utility.log import log
from utility.const import __name__,\
    __version__,\
    WIDTH, HEIGHT, M_INTERVAL,\
    RES, ICONS, TEMP, ICO_SIZE,\
    FULL_SCREEN, NORMAL_SIZE, LOGO, WIZARD, TOOLS, INFO,\
    DATA_LOW_LIMIT,\
    LOAD_PAUSE, TRAY_VISIBLE_DELAY, TRAY_ICON_DELAY,\
    FIRST, LAST, NEXT, PREV, QUIT, SHOW, TEST, RESET,\
    LOAD, LAYERS, DECOM, ANALYSIS, FIN,\
    infoTipsDict, infoWavelets, WT, WV, Models, Tabs, Tooltips, BOTTOM_SPACE,\
    FONTS_DICT, MIN_FORECAST, MAX_FORECAST, DEFAULT_STEPS,\
    R_BIN, MAX_LVL_TRANSFORM
from utility.guiTweaks import unfillLayout, createSeparator,\
    walkNonGridLayoutShadow, walkGridLayoutShadow, createVerticalSeparator
from utility.tools import prettifyNames, clearFolderContents, uniqueModels
from utility.config import Config
from stats.parser import DataParser
from gui.guiTool import ToolsFrame
from gui.guiInfo import InfoFrame
from gui.graphWidget import MplWidget
from gui.faderWidget import StackedWidget
from gui.guiMessage import SystemMessage
from gui.muWizard import MuWizard
from stats.models import processModel, calculateForecast, initRLibraries, auto_model, model_error
from stats.wavelets import select_levels_from_swt, update_selected_levels_swt,\
                    normalize_dwt_dimensions, iswt, update_dwt,\
                    select_node_levels_from_swt, update_swt, calculate_suitable_lvl
from usr.test import test_data
#from gui.flowLayout import FlowLayout

####################################
#            GUI classes           #
####################################

class MuScaleMainDialog(QMainWindow):
    def __init__(self, parent=None):
        super(MuScaleMainDialog, self).__init__(parent)

        ### components ###

        # timer #
        start = datetime.now()

        # settings #
        self.config = Config()
        self.toolbarEnable = self.config.getParams(toolbar=True)['toolbar'].toBool()

        # computational modules #
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(RES + ICONS + LOGO))
        self.trayIcon.show()
        self.trayIcon.showMessage('Loading...', 'Initializing R', QSystemTrayIcon.Information, TRAY_VISIBLE_DELAY)
        self.forbidClose = True

        self.R = R(R_BIN)
        initRLibraries(self.R)

        # external gui modules #
        self.wizard = None
        self.toolsFrame = ToolsFrame(self.R, self)
        self.infoDialog = InfoFrame(self)
        self.messageInfo = SystemMessage(self)
        self.wizard = MuWizard(self.R, self)

        # geometry #
        self.gem = None

        # data loaders #
        self.loadDataGroup = QGroupBox('Data source')
        self.loadDataLayout = QVBoxLayout()

        self.loadFromFile = QPushButton('&Load from file')
        # manual
        self.toggleManual = QPushButton('Manual input')
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
        self.computeLvls = QPushButton('Auto')
        self.spinLevels = QSpinBox()
        self.calculateButton = QPushButton('A&nalyze data')
        self.showWavelist = QPushButton('Show wavelist')
        self.showScalogram = QPushButton('Show scalogram')
        self.decompInfoLabel = QLabel(u'')
        self.wavelistGraph = MplWidget(self.toolsFrame,
                                       toolbar=self.toolbarEnable)
        self.scalogramGraph = MplWidget(self.toolsFrame,
                                        toolbar=self.toolbarEnable)

        self.wvFamilyLbl = QLabel("<font style='color: gray'>Wavelet family</font>")
        self.wvTypeLbl = QLabel("<font style='color: gray'>Wavelet type</font>")
        self.wvDecompLbl = QLabel("<font style='color: gray'>Decomposition method</font>")
        self.wvLevelLbl = QLabel("<font style='color: gray'>Decomposition level</font>")

        self.wvSignalEx = QLabel("<font style='color: gray'>Signal extension model: </font>")
        self.comboSignalEx = QComboBox()

        self.decompLayout.addWidget(self.wvFamilyLbl, 0, 0)
        self.decompLayout.addWidget(self.wvTypeLbl, 0, 1)
        self.decompLayout.addWidget(self.wvDecompLbl, 0, 2)
        self.decompLayout.addWidget(self.wvLevelLbl, 0, 3, 1, 2)
        #---
        self.decompLayout.addWidget(self.comboWavelet, 1, 0)
        self.decompLayout.addWidget(self.comboWavelist, 1, 1)
        self.decompLayout.addWidget(self.comboDecomposition, 1, 2)
        self.decompLayout.addWidget(self.computeLvls, 1, 3)
        self.decompLayout.addWidget(self.spinLevels, 1, 4)
        self.decompLayout.addWidget(self.wvSignalEx, 2, 0, 1, 3)
        self.decompLayout.addWidget(self.comboSignalEx, 2, 3, 1, 2)
        #---
        self.decompLayout.addWidget(self.calculateButton, 3, 0, 1, 5)
        self.decompLayout.addWidget(self.showWavelist, 4, 0)
        self.decompLayout.addWidget(self.decompInfoLabel, 4, 1, 1, 3)
        self.decompLayout.addWidget(self.showScalogram, 4, 4)
        self.decompLayout.addWidget(self.wavelistGraph, 5, 0, 1, 5)
        self.decompLayout.addWidget(self.scalogramGraph, 6, 0, 1, 5)

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

        self.reconTS = QPushButton('Plot constructed model')
        self.plotInitial = QPushButton('Plot initial data')
        self.clearResult = QPushButton('Clear')
        self.infoResult = QPushButton('Info')
        self.resultingGraph = MplWidget(self.toolsFrame,
                                        toolbar=self.toolbarEnable)

#        self.reconsLayout.addWidget(self.reconTS, 0, 0)
#        self.reconsLayout.addWidget(self.clearResult, 0, 1)
#        self.reconsLayout.addWidget(self.infoResult, 0, 2)
#        self.reconsLayout.addWidget(self.plotInitial, 0, 3)
        self.reconsLayout.addWidget(self.reconTS, 0, 0, 1, 2)
        self.reconsLayout.addWidget(self.clearResult, 1, 0)
        self.reconsLayout.addWidget(self.infoResult, 1, 1)
        self.reconsLayout.addWidget(self.plotInitial, 2, 0, 1, 2)
#        self.reconsLayout.addWidget(self.resultingGraph, 1, 0, 1, 4)
        self.reconsLayout.addWidget(self.resultingGraph, 3, 0, 1, 2)

        self.reconsGroup.setLayout(self.reconsLayout)

        # options #
        self.optionsGroup = QGroupBox('Settings')
        self.stylesCombo = QComboBox()
        self.toggleShadows = QCheckBox('Enable shadow effect')
        self.lockMaxLevel = QCheckBox('Lock max decomposition level')
        self.autoStep = QCheckBox('Auto next step')
        self.enableToolbar = QCheckBox('Show graph controls on hover')
        self.plotMultiline = QCheckBox('Plot wavelist as multiline graph')
        self.autoBaseSWT = QCheckBox("Process node SWT levels")
        self.autoUpdateTools = QCheckBox('Append data to R workspace')
        self.showStacktrace = QCheckBox('Show exception stacktrace')
        self.saveLastFolder = QCheckBox('Remember last opened folder')
        self.hidetoTray = QCheckBox('Hide to tray on close')
        self.autoUpdateTable = QCheckBox('Update table with resulting data')
        self.autoConstructModel = QCheckBox('Construct model in one click')
        self.applySettings = QToolButton()

        self.optionsLayout = QGridLayout()
        self.optionsLayout.addWidget(self.stylesCombo, 0, 0)
        self.optionsLayout.addWidget(self.toggleShadows, 0, 2)
        self.optionsLayout.addWidget(self.applySettings, 0, 4)
        self.optionsLayout.addWidget(createSeparator(), 1, 0, 1, 5)
        #---
        self.optionsLayout.addWidget(self.autoStep, 2, 0)
        self.optionsLayout.addWidget(self.autoUpdateTable, 3, 0)
        self.optionsLayout.addWidget(self.autoConstructModel, 4, 0)
        self.optionsLayout.addWidget(self.autoUpdateTools, 5, 0)
        self.optionsLayout.addWidget(createVerticalSeparator(), 2, 1, 4, 1)
        #---
        self.optionsLayout.addWidget(self.lockMaxLevel, 2, 2)
        self.optionsLayout.addWidget(self.autoBaseSWT, 3, 2)
        self.optionsLayout.addWidget(self.enableToolbar, 4, 2)
        self.optionsLayout.addWidget(self.plotMultiline, 5, 2)
        self.optionsLayout.addWidget(createVerticalSeparator(), 2, 3, 4, 1)
        #---
        self.optionsLayout.addWidget(self.showStacktrace, 2, 4)
        self.optionsLayout.addWidget(self.saveLastFolder, 3, 4)
        self.optionsLayout.addWidget(self.hidetoTray, 4, 4)

        self.optionsGroup.setLayout(self.optionsLayout)

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

        self.progressBar = QProgressBar()

        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainLayout.addWidget(self.progressBar)
        self.mainLayout.addWidget(self.optionsGroup)
        self.mainLayout.addWidget(self.statTools)

        self.addToolBar(self.toolBar)
        self.setMenuBar(self.menuBar)
        self.setStatusBar(self.statusBar)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.setCentralWidget(self.centralWidget)

        # dialogs #
        self.openFileDialog = QFileDialog(self)

        # session variables #
        self.currentDataSet = []
        self.currentPlot = None
        self.multiModel = {}
        self.tmpConfig = {}

        ### initialization ###
        self.initComposition()
        self.initComponents()
        self.initActions()
        self.loadConfig()
        self.customEffects()

        ### start ###
        self.statusBar.showMessage('Ready!')

        ### post-start ###
        loadingTime = datetime.now() - start
        self.trayIcon.showMessage('Ready!', 'Launched in ' + str(loadingTime), QSystemTrayIcon.Information,
                                  TRAY_VISIBLE_DELAY)
        QTimer.singleShot(TRAY_ICON_DELAY, self.trayIcon.hide)

        def startingTip():
            self.messageInfo.showInfo(self.statTools.currentIndex())

        QTimer.singleShot(LOAD_PAUSE, startingTip)

        self.toolsFrame.updateLog(['muScale ' + __version__ + ' launched', 'loading time: ' + str(loadingTime)])

        ### disable unimplemented features ###

#------------------- initialization ------------------# #--------------- * * * ---------------#
    def initComposition(self):
        self.setWindowTitle(__name__ + ' ' + __version__)

        desktop = QApplication.desktop()
        self.setGeometry(QRect((desktop.width() - WIDTH) / 2, (desktop.height() - HEIGHT) / 2, WIDTH, HEIGHT))

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWindowIcon(QIcon(RES + ICONS + LOGO))

        self.setStyleSheet('QToolTip { background-color: black; color: white;\
                                        border: 1px solid white; border-radius: 2px; }')

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
        self.comboDecomposition.addItems(WT._enums.values())
        self.spinLevels.setValue(2)
        self.spinLevels.setRange(2, 10)
        self.wavelistGraph.hide()
        self.scalogramGraph.hide()
        self.showScalogram.hide()
        self.showScalogram.setCheckable(True)
        self.showWavelist.hide()
        self.showWavelist.setCheckable(True)
        self.decompInfoLabel.hide()
        self.decompInfoLabel.setAlignment(Qt.AlignCenter)
        self.computeLvls.setMaximumHeight(20)
        self.wvLevelLbl.setAlignment(Qt.AlignCenter)
        self.wvFamilyLbl.setAlignment(Qt.AlignCenter)
        self.wvTypeLbl.setAlignment(Qt.AlignCenter)
        self.wvDecompLbl.setAlignment(Qt.AlignCenter)
        
        self.comboSignalEx.addItems(pywt.MODES.modes)
        self.wvSignalEx.setAlignment(Qt.AlignCenter)

        self.decompLayout.setAlignment(Qt.AlignCenter)

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
        self.toolBar.setIconSize(QSize(ICO_SIZE, ICO_SIZE))
        self.progressBar.setRange(0, 0)
        self.progressBar.hide()
        self.progressBar.setMaximumHeight(10)
        self.progressBar.setStyleSheet('''QProgressBar {
                                             border: 1px solid grey;
                                             border-radius: 4px;
                                         }''')
#                                         QProgressBar::chunk {
#                                             background-color: black;
#                                             width: 10px;
#                                             margin: 0.5px;
#                                         }''')
        # results #
        self.resultingGraph.hide()
        constraint = 18
        self.reconTS.setMaximumHeight(constraint)
        self.infoResult.setMaximumHeight(constraint)
        self.clearResult.setMaximumHeight(constraint)
        self.plotInitial.setMaximumHeight(constraint)
        self.reconsLayout.setSpacing(2)
        self.reconsLayout.setMargin(5)
#        self.reconsLayout.setAlignment(Qt.AlignCenter)

        # tooltips #
        self.setCustomTooltips()

        # tabs icons #
        self.statTools.setItemIcon(int(Tabs.Data), QIcon(RES + ICONS + LOAD))
        self.statTools.setItemIcon(int(Tabs.Decomposition), QIcon(RES + ICONS + DECOM))
        self.statTools.setItemIcon(int(Tabs.Model), QIcon(RES + ICONS + LAYERS))
        self.statTools.setItemIcon(int(Tabs.Simulation), QIcon(RES + ICONS + ANALYSIS))
        self.statTools.setItemIcon(int(Tabs.Results), QIcon(RES + ICONS + FIN))

        # tabs alignment #
        for tab in range(0, self.statTools.count()):
            self.statTools.widget(tab).setAlignment(Qt.AlignCenter)

        # settings #
        self.stylesCombo.addItems(QStyleFactory.keys())
        self.optionsLayout.setAlignment(Qt.AlignCenter)
        self.applySettings.setText('Apply visual style')
        self.optionsGroup.hide()

        # fonts #
        font_tooltip = 'Cambria'
        tooltip_size = 12
        edit_font = FONTS_DICT['table'][0]
        edit_size = FONTS_DICT['table'][2] + 3
        font = FONTS_DICT['main'][0]
        size = FONTS_DICT['main'][2]
        self.centralWidget.setStyleSheet('QPushButton {font-family: ' + font + '; font-size: ' + str(size) + 'px;}\
                                            QComboBox {font-family: ' + font + '; font-size: ' + str(size) + 'px;}\
                                            QLabel {font-family: ' + font + '; font-size: ' + str(size) + 'px;}\
                                            QToolBox::tab {font-family: ' + font + '; font-size: ' + str(size) + 'px;}\
                                            QTooBar {font-family: ' + font + '; font-size: ' + str(size) + 'px;}\
                                            QToolButton {font-family: ' + font + '; font-size: ' + str(size) + 'px;}\
                                            QCheckBox {font-family: ' + font + '; font-size: ' + str(size) + 'px;}\
                                            QGroupBox::title {font-family: ' + font + '; \
                                                                            font-size: ' + str(size) + 'px;}\
                                            QTextEdit {font-family: ' + edit_font + '; \
                                                                            font-size: ' + str(edit_size) + 'px;}\
                                            QToolTip {font-family: ' + font_tooltip + '; \
                                                                            font-size: ' + str(tooltip_size) + 'px;}')

        self.toolBar.setStyleSheet('QTooBar {font-family: ' + font + '; font-size: ' + str(size) + 'px;}\
                                    QToolTip {font-family: ' + font_tooltip + '; font-size: ' +
                                   str(tooltip_size) + 'px;}')

        self.menuBar.setStyleSheet('QMenu {font-family: ' + font + '; font-size: ' + str(size) + 'px;}')

        self.statusBar.setStyleSheet('QStatusBar {font-family: ' + font + '; font-size: ' + str(size) + 'px;}')

        # tray #
        self.trayIcon.setToolTip(u'Ensconced in system tray, μScale awaits')

    def initActions(self):
        # menu actions #
        quitAction = QAction('&Quit', self)
        quitAction.triggered.connect(self.quitApplication)
        aboutAction = QAction('&About', self)
        aboutAction.triggered.connect(self.showAbout)
        resetTipsAction = QAction('Reset &tips', self)
        resetTipsAction.triggered.connect(self.resetTips)
        self.toggleSettings = QAction('Show &options', self)
        self.toggleSettings.triggered.connect(self.viewSettings)
        self.toggleSettings.setCheckable(True)

        self.menuBar.addAction(self.toggleSettings)
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

        # toolbar #
        self.toggleSizeAction = QAction('Full screen', self)
        self.toggleSizeAction.setShortcut(QKeySequence('F11'))
        self.toggleSizeAction.triggered.connect(self.fullScreen)
        self.toggleSizeAction.setCheckable(True)
        self.toggleSizeAction.setIcon(QIcon(RES + ICONS + FULL_SCREEN))

        self.toggleTools = QAction('Show tools', self)
        self.toggleTools.setShortcut(QKeySequence('F10'))
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
        self.toolBar.addAction(previousStepAction)
        self.toolBar.addAction(nextStepAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(quickTest)
        self.toolBar.addAction(resetAll)

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
        self.computeLvls.clicked.connect(self.processLvls)

        # tooltips #
        self.statTools.currentChanged.connect(self.updateInfoTooltips)

        # results #
        self.reconTS.clicked.connect(self.updateResultingTS)
        self.plotInitial.clicked.connect(self.updateResultingTSWithInitialData)
        self.clearResult.clicked.connect(self.clearResultingGraph)

        # settings #
        self.applySettings.clicked.connect(self.saveSettings)

        # tray #
        self.trayIcon.activated.connect(self.restoreFromTray)
        self.trayMenu = QMenu()
        self.trayMenu.addAction(QAction(QIcon(RES + ICONS + QUIT), '&Quit', self, triggered=self.quit))
        self.trayMenu.addAction(QAction(QIcon(RES + ICONS + SHOW), '&Show', self, triggered=self.showHide))
        self.trayIcon.setContextMenu(self.trayMenu)

    def setCustomTooltips(self):
        # data input #
        self.loadFromFile.setToolTip(Tooltips['load_from_file'])
        self.toggleManual.setToolTip(Tooltips['load_manual'])

        # level
        self.spinLevels.setToolTip(Tooltips['max_level'])

    def loadConfig(self):
        self.lastFolder = RES
        # by alphabet
        basic, folder, lock, model, multiline, r, shadows,\
        step, style, table, toolbar, trace, tray = self.config.loadConfig()

        self.toggleShadows.setChecked(shadows.toBool())
        self.stylesCombo.setCurrentIndex(style.toInt()[0])
        self.lockMaxLevel.setChecked(lock.toBool())
        self.autoStep.setChecked(step.toBool())
        self.plotMultiline.setChecked(multiline.toBool())
        self.enableToolbar.setChecked(toolbar.toBool())
        self.autoUpdateTools.setChecked(r.toBool())
        self.autoBaseSWT.setChecked(basic.toBool())
        self.showStacktrace.setChecked(trace.toBool())
        self.hidetoTray.setChecked(tray.toBool())
        self.autoUpdateTable.setChecked(table.toBool())
        self.autoConstructModel.setChecked(model.toBool())
        try:
            self.saveLastFolder.setChecked(folder.toList()[0].toBool())
            self.lastFolder = folder.toList()[1].toString()
        except Exception:
            pass
        # update style settings
        self.saveSettings()

    def saveConfig(self):
        self.config.updateConfig(
            step=self.autoStep.isChecked(),
            shadows=self.toggleShadows.isChecked(),
            basic=self.autoBaseSWT.isChecked(),
            lock=self.lockMaxLevel.isChecked(),
            multiline=self.plotMultiline.isChecked(),
            r=self.autoUpdateTools.isChecked(),
            style=self.stylesCombo.currentIndex(),
            toolbar=self.enableToolbar.isChecked(),
            trace=self.showStacktrace.isChecked(),
            tray=self.hidetoTray.isChecked(),
            folder=[self.saveLastFolder.isChecked(), self.lastFolder],
            table=self.autoUpdateTable.isChecked(),
            model=self.autoConstructModel.isChecked(),
        )

    def customEffects(self):
        if self.toggleShadows.isChecked():
            walkNonGridLayoutShadow(self.loadDataLayout)
            walkGridLayoutShadow(self.decompLayout)
            walkGridLayoutShadow(self.reconsLayout)

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
        desktop = QApplication.desktop()
        if self.y() + self.height() + M_INTERVAL > desktop.height() - BOTTOM_SPACE:
            pass
        else:
            self.messageInfo.move(self.x() + (self.width() - self.messageInfo.width()) / 2,
                                  self.y() + self.height() + M_INTERVAL)

    def updateInfoPosition(self):
        if not self.infoDialog.detach.isChecked():
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
#-------------------- settings -------------------#
###################################################
    def viewSettings(self):
        if self.toggleSettings.isChecked():
            self.optionsGroup.show()
            self.toggleSettings.setText('Hide &options')
        else:
            self.optionsGroup.hide()
            self.toggleSettings.setText('Show &options')

    def saveSettings(self):
        QApplication.setStyle(QStyleFactory.create(self.stylesCombo.currentText()))
        self.update()

###################################################
#------------------ loading data -----------------#
###################################################
    def openFile(self):
        self.resetData()
        if self.saveLastFolder.isChecked():
            self.openFileDialog.setDirectory(self.lastFolder)
        if self.openFileDialog.exec_():
            fileName = self.openFileDialog.selectedFiles()
            if self.saveLastFolder.isChecked():
                self.lastFolder = self.openFileDialog.directory().path()
            try:
                if fileName.count() > 0:
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
            if len(self.currentDataSet[0]) > DATA_LOW_LIMIT:
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

                if self.autoUpdateTable.isChecked():
                    self.toolsFrame.updateTable(self.currentDataSet[0], 'Series')

                if self.autoStep.isChecked():
                    self.statTools.setCurrentIndex(int(Tabs.Decomposition))
            else:
                self.messageInfo.showInfo('Not enough values to form data series.', True)
                self.toolsFrame.updateLog(['not enough values'], warning=True)
        else:
            self.messageInfo.showInfo('Could not parse at all!', True)
            self.toolsFrame.updateLog(['could not parse'], warning=True)

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

        self.toolsFrame.clearTable()
        self.showTable.setText('Show table')

        self.toolsFrame.resetPlot()
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

        self.resultingGraph.canvas.ax.clear()
        
        # clearing R workspace
        self.R('rm(list = ls())')
        self.toolsFrame.updateNamespace()

    def updateTable(self):
        if self.showTable.text() == 'Show table':
#            self.toolsFrame.updateTable(self.currentDataSet[0])
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
            self.toolsFrame.updatePlot(self.currentDataSet[0])
#            self.currentPlot.updateData(self.currentDataSet[0])
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
    def processLvls(self):
        if self.comboDecomposition.currentIndex() is int(WT.DiscreteWT) - 1:
            swt = False
        else:
            swt = True
        lvl = calculate_suitable_lvl(self.currentDataSet[0],
                                     pywt.Wavelet(unicode(self.comboWavelist.currentText())), self.R, swt)
        self.spinLevels.setValue(lvl + 1)
        self.messageInfo.showInfo('Decomposition set at ' + str(lvl + 1) + ' level(s)')

    def updateWavelist(self):
        self.comboWavelist.clear()
        self.comboWavelist.addItems(pywt.wavelist(self.comboWavelet.currentText()))
        self.comboWavelet.setToolTip(infoWavelets[unicode(self.comboWavelet.currentText())])

    def updateWaveletPreview(self):
        self.comboWavelist.setToolTip("<img src='" + RES + WV + self.comboWavelist.currentText() + "'.png'>")
        try:
            self.updateMaxDLevel()
        except Exception:
            pass

    def updateMaxDLevel(self):
        current_max = MAX_LVL_TRANSFORM
        if self.comboDecomposition.currentIndex() is int(WT.DiscreteWT) - 1:
            new_max = pywt.dwt_max_level(len(self.currentDataSet[0]),
                                             pywt.Wavelet(unicode(self.comboWavelist.currentText()))) + 1
            self.comboDecomposition.setToolTip(Tooltips['dwt'])

            self.wvSignalEx.show()
            self.comboSignalEx.show()
        elif self.comboDecomposition.currentIndex() is int(WT.StationaryWT) - 1:
            new_max = pywt.swt_max_level(len(self.currentDataSet[0])) + 1
            self.comboDecomposition.setToolTip(Tooltips['swt'])

            self.wvSignalEx.hide()
            self.comboSignalEx.hide()
        if self.lockMaxLevel.isChecked():
            current_max = new_max
        else:
            pass
        
        self.spinLevels.setMaximum(current_max)
        self.spinLevels.setToolTip(' '.join(str(self.spinLevels.toolTip()).split(' ')[:-1]) +
                                   ' <b>' + str(current_max) + '</b>')
        self.spinLevels.setValue(current_max/2 + 1)

    def waveletTransform(self):
        # stationary decomposition flag
        self.isSWT = False

        try:
            self.wavelet = pywt.Wavelet(unicode(self.comboWavelist.currentText()))
            w_level = self.spinLevels.value() - 1
            # discrete
            if self.comboDecomposition.currentIndex() is int(WT.DiscreteWT) - 1:
                self.signalEx = unicode(self.comboSignalEx.currentText())
                self.wInitialCoefficients = pywt.wavedec(self.currentDataSet[0], self.wavelet,
                                                         level=w_level, mode=self.signalEx)
                #TODO: check
                self.wCoefficients = self.wInitialCoefficients[:]
            # stationary
            elif self.comboDecomposition.currentIndex() is int(WT.StationaryWT) - 1:
                self.wInitialCoefficients = pywt.swt(self.currentDataSet[0], self.wavelet, level=w_level)
                self.wCoefficients = select_levels_from_swt(self.wInitialCoefficients)
                self.isSWT = True
                # node coefficients
                if self.autoBaseSWT.isChecked():
                    self.wNodeCoefficients = select_node_levels_from_swt(self.wInitialCoefficients)

            if self.autoUpdateTable.isChecked():
                lvl = 0
                for level in self.wCoefficients:
                    self.toolsFrame.updateTable(level, 'Level' + str(lvl)); lvl += 1

            # resulting wavelist
            self.wavelistGraph.clearCanvas(repaint_axes=False)
            if not self.plotMultiline.isChecked():
                rows = len(self.wCoefficients);  i = 0
                for coeff in self.wCoefficients:
                     ax = self.wavelistGraph.canvas.fig.add_subplot(rows, 1, i + 1); i += 1
                     ax.plot(coeff, label='Lvl' + str(rows))
                     MplWidget.hideAxes(ax)
            else:
                self.wavelistGraph.multiline(self.wCoefficients)
                
            self.wavelistGraph.show()
            self.showWavelist.setChecked(True)

            # resulting scalogram
            if not self.isSWT:
                self.scalogramGraph.scalogram(normalize_dwt_dimensions(self.wCoefficients))
            else:
                self.scalogramGraph.scalogram(self.wCoefficients)

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

            if self.isSWT:
                self.toolsFrame.updateLog(['performed SWT'])
            else:
                self.toolsFrame.updateLog(['performed DWT'])
            self.toolsFrame.updateLog(['decomposed to ' + str(w_level + 1) + ' levels using ' +
                                       self.wavelet.name + ' wavelet'])

            if self.autoStep.isChecked():
                self.statTools.setCurrentIndex(int(Tabs.Model))
        except Exception, e:
            if self.showStacktrace.isChecked():
                message = traceback.format_exc(e)
            else:
                message = str(e)
            self.messageInfo.showInfo(message, True)
            self.toolsFrame.updateLog([message], True)
            log.exception(e)

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
        # Check all 'add' buttons (3rd in grid)
        for row in range(0, self.modelLayout.rowCount()):
            if self.modelLayout.itemAtPosition(row, 2) is not None:
                widget = self.modelLayout.itemAtPosition(row, 2).widget()
                if hasattr(widget, 'isCheckable'):
                    if widget.isCheckable():
                        if not widget.isChecked():
                            widget.click()

    def previewAll(self):
        # Check all 'preview' buttons (4th in grid)
        for row in range(0, self.modelLayout.rowCount()):
            if self.modelLayout.itemAtPosition(row, 3) is not None:
                widget = self.modelLayout.itemAtPosition(row, 3).widget()
                if hasattr(widget, 'isCheckable'):
                    if widget.isCheckable():
                        widget.click()

    def showComponentPreview(self):

        for row in range(0, self.modelLayout.rowCount()):
            # 4th row in grid layout ~ 'preview' button
            if self.modelLayout.itemAtPosition(row, 3) is not None:
                widget = self.modelLayout.itemAtPosition(row, 3).widget()
                if hasattr(widget, 'isCheckable'):
                    if widget.isCheckable():
                        if widget.isChecked():
                            # MPL widget
                            preview = self.modelLayout.itemAtPosition(row + 1, 0).widget()
                            # Current level
                            level = self.modelLayout.itemAtPosition(row, 0).widget()
                            # Level number enclosed in <b>N</b>
                            index = level.text().right(5)[0].toInt()[0]
                            preview.updatePlot(self.wCoefficients[index], label='Lvl' + str(index))

                            preview.show()
                        else:
                            preview = self.modelLayout.itemAtPosition(row + 1, 0).widget()
                            preview.hide()

    def constructModelTemplate(self):
        MplWidget.generatePreviews(self.wCoefficients)

        unfillLayout(self.modelLayout)
        nLevels = len(self.wCoefficients)

        addAll = QPushButton()
        previewAll = QPushButton()
        autoAll = QPushButton()
        addAll.setText('Add a&ll')
        previewAll.setText('Preview all')
        previewAll.setCheckable(True)
        autoAll.setText('Auto model')

        # auto model options
        autoConfigGroup = QGroupBox('Active models')
        autoConfigLayout = QVBoxLayout()
        autoConfigLayout.setAlignment(Qt.AlignCenter)

        def constructAuto():
            options = {}
            options['fractal'] = fractalDim.isChecked()
            options['ljung'] = ljungBox.isChecked()
            options['multi'] = fractalCompex.isChecked()

            models = auto_model(self.wCoefficients, self.R, options, self.currentDataSet[0])
            for lvl, model in models.iteritems():
                combo = self.modelLayout.itemAtPosition(lvl * 2 + 2, 1).widget()
                combo.setCurrentIndex(int(model) - 1)
            self.messageInfo.showInfo('Models set')

        self.applyAuto = QToolButton()
        self.applyAuto.setText('Choose using:')
        self.applyAuto.clicked.connect(constructAuto)
        autoButtonLayout = QHBoxLayout()
        autoButtonLayout.addWidget(self.applyAuto)
        autoButtonLayout.setAlignment(Qt.AlignCenter)

        fractalDim = QRadioButton('Fractal dimension')
        ljungBox = QRadioButton('Ljung-Box criterion')
        fractalCompex = QRadioButton('Multiple t/s properties')
        fractalDim.setChecked(True)

        autoConfigLayout.addLayout(autoButtonLayout)
        autoConfigLayout.addWidget(fractalDim)
        autoConfigLayout.addWidget(ljungBox)
        autoConfigLayout.addWidget(fractalCompex)

        autoConfigGroup.setLayout(autoConfigLayout)

        def autoModel():
            if autoAll.isChecked():
                autoConfigGroup.show()
            else:
                autoConfigGroup.hide()

        # buttons and layouts
        addAll.clicked.connect(self.addAllLevelToModel)
        previewAll.clicked.connect(self.previewAll)
        autoAll.clicked.connect(autoModel)
        autoAll.setCheckable(True)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(addAll)
        buttonsLayout.addWidget(autoAll)
        buttonsLayout.addWidget(previewAll)

        modelSetupLayout = QVBoxLayout()
        modelSetupLayout.addWidget(autoConfigGroup)
        modelSetupLayout.addLayout(buttonsLayout)

        self.modelLayout.addLayout(modelSetupLayout, 0, 0, 1, 4)
        self.modelLayout.addWidget(createSeparator(), 1, 0, 1, 4)

        autoConfigGroup.hide()

        self.filter = LabelFilter()

        i = 2
        for level in range(0, nLevels):
            labelModel = QLabel('Level <b>' + str(level) + '</b>')
            labelModel.setAlignment(Qt.AlignCenter)
            labelModel.setToolTip("<img src='" + RES + TEMP + str(level) + "'.png'>")
            labelModel.setAttribute(Qt.WA_Hover)
            labelModel.installEventFilter(self.filter)

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

            componentPreview = MplWidget(self.toolsFrame,
                                       toolbar=self.toolbarEnable)
            componentPreview.hide()

            # level label
            self.modelLayout.addWidget(labelModel, i, 0)
            # model list
            self.modelLayout.addWidget(comboModel, i, 1)
            # add button
            self.modelLayout.addWidget(addModel, i, 2)
            # preview button
            self.modelLayout.addWidget(togglePreview, i, 3); i += 1
            # graph widget
            self.modelLayout.addWidget(componentPreview, i, 0, 1, 4); i += 1

        resetModel = QPushButton('Reset model setup')
        resetModel.clicked.connect(self.resetModel)
        constructModel = QPushButton('&Construct multiscale model')
        constructModel.clicked.connect(self.constructModel)

        self.modelLayout.addWidget(createSeparator(), i, 0, 1, 4); i += 1
        self.modelLayout.addWidget(constructModel, i, 0, 1, 2)
        self.modelLayout.addWidget(resetModel, i, 2, 1, 2)

        self.modelLayout.setAlignment(Qt.AlignCenter)

        if self.toggleShadows.isChecked():
            walkNonGridLayoutShadow(buttonsLayout)
            walkNonGridLayoutShadow(autoConfigLayout)
            walkNonGridLayoutShadow(autoButtonLayout)
            walkGridLayoutShadow(self.modelLayout)

        if self.modelLayout.rowCount() - 9 > 2:
            previewAll.setDisabled(True)

    def addModel(self):
        for row in range(0, self.modelLayout.rowCount()):
            # 3rd row in grid layout ~ 'add' button
            if self.modelLayout.itemAtPosition(row, 2) is not None:
                widget = self.modelLayout.itemAtPosition(row, 2).widget()
                if hasattr(widget, 'isCheckable'):
                    if widget.isCheckable():
                        if widget.isChecked():
                            widget.setText('OK')
                            # Model list
                            combo = self.modelLayout.itemAtPosition(row, 1).widget()
                            combo.setDisabled(True)
                        else:
                            widget.setText('+')
                            combo = self.modelLayout.itemAtPosition(row, 1).widget()
                            combo.setEnabled(True)

    def resetModel(self):
        self.constructModelTemplate()
        self.statTools.setItemEnabled(int(Tabs.Simulation), False)

    def constructModel(self):
        self.multiModel.clear()
        if self.autoConstructModel.isChecked():
            self.addAllLevelToModel()
        for level in range(0, len(self.wCoefficients)):
            # 'add' button, starting from 2nd row, skipping graph widget
            widget = self.modelLayout.itemAtPosition(level * 2 + 2, 2).widget()
            if isinstance(widget, QWidget):
                if widget.isChecked():
                    self.multiModel[level] = Models(
                        # selected model
                        self.modelLayout.itemAtPosition(level * 2 + 2, 1).widget().currentIndex() + 1)
        if self.multiModel == {}:
            self.messageInfo.showInfo('You haven not specified any methods at all!', True)
        else:
            self.statTools.setItemEnabled(int(Tabs.Simulation), True)
            self.readyModelsStack()
            self.statTools.setItemEnabled(int(Tabs.Results), True)
            self.toolsFrame.updateLog(['multiscale model complete'])

            info = u''
            for index, model in self.multiModel.iteritems():
                info += 'Lvl ' + str(index) + ': <i>' + prettifyNames([model._enumname])[0] + '</i>\t'
            self.messageInfo.showInfo('Multiscale model complete<br/>' + info, adjust=False)

            if self.autoStep.isChecked(): self.statTools.setCurrentIndex(int(Tabs.Simulation))

###################################################
#-------------- model simulation -----------------#
###################################################
    def readyModelsStack(self):
        self.processedWCoeffs = [0] * len(self.wCoefficients)
        self.nodesProcessed = False
        self.inProgress = False

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

            simulationPlot = MplWidget(self.toolsFrame,
                                       toolbar=self.toolbarEnable)
            simulationPlot.updatePlot(self.wCoefficients[model], label='Series' + str(model))

            modelsStack.addWidget(simulationPlot)

        modelsListLayout.addWidget(previousModel)
        modelsListLayout.addWidget(modelsList)
        modelsListLayout.addWidget(nextModel)

        def changeStackPage():
            modelsStack.setCurrentIndex(modelsList.currentIndex())

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
        
        extractLevel = lambda qcombo: int(str(qcombo.currentText()).split('.')[0])

        def constructModel():
            model = extractLevel(modelsList)
            result = processModel(self.multiModel[model],
                                  self.wCoefficients[model],
                                  self.R,
                                  compileOptions(optMod))
            self.processedWCoeffs[model] = result

            modelsStack.currentWidget().updatePlot(result, label='Model fit', style='dashed', color='g')

        def forecastFinished(result, model):
            for index in range(0, len(result)):
                try:
                    result[index] = float(result[index])
                except Exception:
                    result[index] = float(result[index].split('e')[0])

            try:
                self.processedWCoeffs[model] = result

                modelsStack.currentWidget().updatePlot(result, label='Forecast', style='dotted', color='r')

                self.tmpConfig['steps'] = forecastSteps.value()

                errors = model_error(self.wCoefficients[model], result, self.R)

                self.messageInfo.showInfo('Resulting errors ~ <i>SSE</i>: ' + str(errors['sse']) +
                                          ' <i>MSE</i>: ' + str(errors['mse']))

                self.toolsFrame.updateLog(['model [lvl ' + str(modelsList.currentIndex()) + '] ' +
                                           prettifyNames([self.multiModel[model]._enumname])[0] +
                                            ': forecast ~ ' + str(forecastSteps.value()) + ' steps'])

                self.toolsFrame.updateLog(['SSE: ' + str(errors['sse']) +
                                          ' MSE: ' + str(errors['mse'])
                                            ])
            except Exception:
                self.toolsFrame.updateLog(['Unexpected error for model ' + str(model)])
            finally:
                self.progressBar.hide()
                self.inProgress = False
                self.statusBar.showMessage('Forecast complete.')

        def forecastModel():
            if not self.inProgress:
                model = extractLevel(modelsList)
                self.model_thread = ModelThread(self.multiModel[model],
                                           self.wCoefficients[model],
                                           self.R,
                                           forecastSteps.value(),
                                           compileOptions(optMod),
                                           model)
                self.model_thread.done.connect(forecastFinished)
                self.model_thread.start()
                self.inProgress = True
                self.progressBar.show()
                self.statusBar.showMessage('Forecasting...')

        def resetModel():
            model = extractLevel(modelsList)
            modelsStack.currentWidget().canvas.ax.clear()
            modelsStack.currentWidget().updatePlot(self.wCoefficients[model], label='Series' + str(model))

            self.toolsFrame.updateLog(['model [lvl ' + str(modelsList.currentIndex()) + '] reset'])

        def getModelIndexInStack(model, modelsList):
            for index in range(0, modelsList.count()):
                if model == int(str(modelsList.itemText(index)).split('.')[0]):
                    return index

        def fitAllLevels():
            for model in self.multiModel:
                try:
                    self.processedWCoeffs[model] = processModel(self.multiModel[model],
                                                                self.wCoefficients[model],
                                                                self.R,
                                                                compileOptions(optMod))
                    index = getModelIndexInStack(model, modelsList)
                    modelsStack.widget(index).updatePlot(self.processedWCoeffs[model],
                                                         label='Model fit', style='dashed', color='g')
                except Exception:
                    pass

            self.messageInfo.showInfo('Performed models fit')

        def multiForecastFinished(results):
            try:
                for model, data in results:
                    for i in range(0, len(data)):
                        try:
                            data[i] = float(data[i])
                        except Exception:
                            data[i] = float(data[i].split('e')[0])

                    self.processedWCoeffs[model] = data
                    index = getModelIndexInStack(model, modelsList)

                    modelsStack.widget(index).updatePlot(self.processedWCoeffs[model],
                                                             label='Forecast', style='dotted', color='r')

                    self.toolsFrame.updateLog(['model  ' + prettifyNames([self.multiModel[model]._enumname])[0] +
                                    ': forecast ~ ' + str(forecastSteps.value()) + ' steps'])
            except Exception:
                self.toolsFrame.updateLog(['Unexpected error for model ' + str(model)])
            finally:
                self.messageInfo.showInfo('Simulation completed')
                self.progressBar.hide()
                self.inProgress = False
                self.statusBar.showMessage('Forecast complete.')

        def forecastAllLevels():
            if not self.inProgress:

                self.multi_model_thread = MultiModelThread(self.multiModel,
                                                           self.wCoefficients,
                                                           self.R,
                                                           forecastSteps.value(),
                                                            compileOptions(optMod),)
                self.multi_model_thread.done.connect(multiForecastFinished)
                self.multi_model_thread.start()
                self.inProgress = True
                self.progressBar.show()
                self.statusBar.showMessage('Forecasting...')
                
                self.tmpConfig['steps'] = forecastSteps.value()

#            # forecast node levels
#            if hasattr(optMod, 'node_label'):
#                if optMod.node_label.isChecked():
#                    node_model = Models(optMod.node_combo.currentIndex() + 1)
#                    self.wUpdatedNodeCoefficients = [0] * len(self.wNodeCoefficients)
#                    index = 0
#
#                    try:
#                        for coeff in self.wNodeCoefficients:
#                            self.wUpdatedNodeCoefficients[index] = calculateForecast(node_model,
#                                                                                  coeff,
#                                                                                  self.R,
#                                                                                  forecastSteps.value(),
#                                                                                  compileOptions(optMod))
#                            index += 1
#
#                        self.toolsFrame.updateLog(['basic nodes processed using ' +
#                                                   prettifyNames([node_model._enumname])[0] +
#                                    ': forecast ~ ' + str(forecastSteps.value()) + ' steps'])
#                        self.nodesProcessed = True
#                    except Exception:
#                        pass
#
#            self.messageInfo.showInfo('Simulation completed')

        def resetAllLevels():
            for model in self.multiModel:
                try:
                    index = getModelIndexInStack(model, modelsList)
                    modelsStack.widget(index).canvas.ax.clear()
                    modelsStack.widget(index).updatePlot(self.wCoefficients[model], label='Series' + str(model))
                except Exception:
                    pass

            self.wUpdatedNodeCoefficients = [0] * len(self.wNodeCoefficients)

            self.toolsFrame.updateLog(['all models reset'], warning=True)
            self.messageInfo.showInfo('All changes reverted')

        simulateButton = QPushButton('Simulate')
        actionsMenu = QMenu()
        actionsMenu.addAction(QAction('Fit model', self, triggered=constructModel))
        actionsMenu.addAction(QAction('Forecast', self, triggered=forecastModel))
        actionsMenu.addAction(QAction('Reset', self, triggered=resetModel))
        simulateButton.setMenu(actionsMenu)

        lblLayout = QHBoxLayout()
        lblLevels = QLabel("<font style='color: gray'>Models by level</font>")
        lblLevels.setAlignment(Qt.AlignCenter)
        lblSimulate = QLabel("<font style='color: gray'>Fit/forecast</font>")
        lblSteps = QLabel("<font style='color: gray'>Forecast horizon</font>")

        lblLayout.addWidget(lblLevels)
        lblLayout.addWidget(QLabel())
        lblLayout.addWidget(lblSimulate)
        lblLayout.addWidget(lblSteps)
        lblLayout.setAlignment(Qt.AlignCenter)

        forecastSteps = QSpinBox()
        forecastSteps.setRange(MIN_FORECAST, MAX_FORECAST)
        try:
            forecastSteps.setValue(self.tmpConfig['steps'])
        except Exception:
            forecastSteps.setValue(DEFAULT_STEPS)
        forecastSteps.valueChanged.connect(forecastModel)

        class TestHandle(object):
            pass
        self.testHandle = TestHandle()

        self.testHandle.forecastAll = QPushButton('Simulate all levels')
        self.testHandle.forecastAll.clicked.connect(forecastAllLevels)
        fitAll = QPushButton('Fit all')
        fitAll.clicked.connect(fitAllLevels)
        resetAll = QPushButton('Reset all')
        resetAll.clicked.connect(resetAllLevels)

        batchLayout = QHBoxLayout()
        batchLayout.addWidget(self.testHandle.forecastAll)
        batchLayout.addWidget(fitAll)
        batchLayout.addWidget(resetAll)

        modelOptionsGroup = QGroupBox()
        modelOptionsGroupLayout = QVBoxLayout()
        modelOptionsGroup.setLayout(modelOptionsGroupLayout)
        modelOptionsGroup.setFlat(True)
        modelOptionsGroup.hide()

        def toggleModelOptions():
            if modelOptions.isChecked():
                modelOptionsGroup.show()
                if modelsStack.isVisible():
                    hideGraph.click()
            else:
                modelOptionsGroup.hide()
                if modelsStack.isHidden():
                    hideGraph.click()

        def toggleGraph():
            if hideGraph.isChecked():
                modelsStack.hide()
                for widget in range(0, modelsListLayout.count()):
                    modelsListLayout.itemAt(widget).widget().hide()
                for widget in range(0, lblLayout.count()):
                    lblLayout.itemAt(widget).widget().hide()
            else:
                modelsStack.show()
                for widget in range(0, modelsListLayout.count()):
                    modelsListLayout.itemAt(widget).widget().show()
                for widget in range(0, lblLayout.count()):
                    lblLayout.itemAt(widget).widget().show()

        modelOptions = QToolButton()
        hideGraph = QToolButton()
        modelOptions.setText('Configure models')
        hideGraph.setText('Hide graph')
        hideGraph.setCheckable(True)
        modelOptions.clicked.connect(toggleModelOptions)
        hideGraph.clicked.connect(toggleGraph)
        modelOptions.setCheckable(True)

        modelOptButtons = QHBoxLayout()
        modelOptButtons.addWidget(modelOptions)
        modelOptButtons.addWidget(hideGraph)
        modelOptButtons.setAlignment(Qt.AlignCenter)

        modelOptionsLayout = QVBoxLayout()
        modelOptionsLayout.addLayout(modelOptButtons)

        allowZeroShift = QCheckBox('Exclude fit from forecast')
        shiftLayout = QHBoxLayout()
        shiftLayout.addWidget(allowZeroShift)
        shiftLayout.setAlignment(Qt.AlignCenter)
        modelOptionsGroupLayout.addLayout(shiftLayout)

        modelOptionsLayout.addWidget(modelOptionsGroup)
        modelOptionsLayout.setAlignment(Qt.AlignCenter)

        class optElem(object):
            pass
        optMod = optElem()
        # models options groups
        def optHW(optMod):
            optMod.hwGroup = QGroupBox('Holt-Winters')
            optMod.hwGroup.setCheckable(True)
            hwLayout = QGridLayout()

            def hwSeasonalShow():
                if optMod.seasonal.isChecked():
                    optMod.seasonal.setText('Use seasonal model:')
                    optMod.model.show()
                    periodLbl.show()
                    optMod.period.show()
                else:
                    optMod.seasonal.setText('Use seasonal model')
                    optMod.model.hide()
                    periodLbl.hide()
                    optMod.period.hide()

            optMod.seasonal = QCheckBox('Use seasonal model')
            optMod.seasonal.clicked.connect(hwSeasonalShow)
            optMod.model = QComboBox()
            optMod.model.addItems(['additive', 'multiplicative'])
            periodLbl = QLabel('Estimated frequency:')
            periodLbl.setAlignment(Qt.AlignCenter)
            optMod.period = QSpinBox()
            optMod.period.setMinimum(2)
            optMod.period.setValue(12)

            hwLayout.addWidget(optMod.seasonal, 0, 0)
            hwLayout.addWidget(optMod.model, 0, 1)
            hwLayout.addWidget(periodLbl, 1, 0)
            hwLayout.addWidget(optMod.period, 1, 1)
            hwLayout.setAlignment(Qt.AlignCenter)

            hwSeasonalShow()

            optMod.hwGroup.setLayout(hwLayout)
            modelOptionsGroupLayout.addWidget(optMod.hwGroup)

        def optAR(optMod):
            optMod.arGroup = QGroupBox('Harmonic Regression')
            optMod.arGroup.setCheckable(True)
            arLayout = QHBoxLayout()

            def arOrderShow():
                if optMod.ar_useAIC.isChecked():
                    ar_orderLbl.hide()
                    optMod.ar_order.hide()
                else:
                    ar_orderLbl.show()
                    optMod.ar_order.show()

            ar_methodLbl = QLabel('Method:')
            ar_methodLbl.setAlignment(Qt.AlignCenter)
            optMod.ar_method = QComboBox()
            optMod.ar_method.addItems(['yule-walker', 'burg', 'mle'])
            optMod.ar_useAIC = QCheckBox('Use AIC')    #Akaike Information Criterion
            optMod.ar_useAIC.clicked.connect(arOrderShow)
            ar_orderLbl = QLabel('Model order:')
            ar_orderLbl.setAlignment(Qt.AlignCenter)
            optMod.ar_order = QSpinBox()
            optMod.ar_order.setMinimum(1)

            optMod.ar_useAIC.setChecked(True)
            arOrderShow()
            
            arLayout.addWidget(ar_methodLbl)
            arLayout.addWidget(optMod.ar_method)
            arLayout.addWidget(ar_orderLbl)
            arLayout.addWidget(optMod.ar_order)
            arLayout.addWidget(optMod.ar_useAIC)
            arLayout.setAlignment(Qt.AlignCenter)

            optMod.arGroup.setLayout(arLayout)
            modelOptionsGroupLayout.addWidget(optMod.arGroup)

        def optLSF(optMod):
            optMod.lsfGroup = QGroupBox('Least Squares Fit')
            optMod.lsfGroup.setCheckable(True)
            lsfayout = QHBoxLayout()

            def lsfOrderShow():
                if optMod.lsf_useAIC.isChecked():
                    lsf_orderLbl.hide()
                    optMod.lsf_order.hide()
                else:
                    lsf_orderLbl.show()
                    optMod.lsf_order.show()

            optMod.lsf_useAIC = QCheckBox('Use AIC')
            optMod.lsf_useAIC.clicked.connect(lsfOrderShow)
            lsf_orderLbl = QLabel('Model order:')
            lsf_orderLbl.setAlignment(Qt.AlignCenter)
            optMod.lsf_order = QSpinBox()
            optMod.lsf_order.setMinimum(1)

            lsfayout.addWidget(lsf_orderLbl)
            lsfayout.addWidget(optMod.lsf_order)
            lsfayout.addWidget(optMod.lsf_useAIC)
            lsfayout.setAlignment(Qt.AlignCenter)

            optMod.lsfGroup.setLayout(lsfayout)
            modelOptionsGroupLayout.addWidget(optMod.lsfGroup)

        def optARIMA(optMod):
            optMod.arimaGroup = QGroupBox('ARIMA')
            optMod.arimaGroup.setCheckable(True)
            arimaLayout = QGridLayout()

            def showOptions():
                if optMod.arima_automatic.isChecked():
                    optMod.arima_orderCheck.setChecked(False)
                    optMod.arima_orderCheck.hide()
                    optMod.arima_seasonalOrderCheck.setChecked(False)
                    optMod.arima_seasonalOrderCheck.hide()
                    showOrder()
                else:
                    optMod.arima_orderCheck.show()
                    optMod.arima_seasonalOrderCheck.show()

            def showOrder():
                if optMod.arima_orderCheck.isChecked():
                    optMod.arima_order.show()
                else:
                    optMod.arima_order.hide()
                if optMod.arima_seasonalOrderCheck.isChecked():
                    optMod.arima_seasonalOrder.show()
                else:
                    optMod.arima_seasonalOrder.hide()

            optMod.arima_automatic = QCheckBox('Estimate orders automatically')
            optMod.arima_automatic.clicked.connect(showOptions)
            optMod.arima_automatic.setChecked(True)

            optMod.arima_orderCheck = QCheckBox('Non-seasonal orders')
            optMod.arima_orderCheck.clicked.connect(showOrder)
            optMod.arima_order = QLineEdit()
            optMod.arima_order.setInputMask('9,9,9')
            optMod.arima_order.setText('1,0,0')
            optMod.arima_order.setMaximumWidth(80)

            optMod.arima_seasonalOrderCheck = QCheckBox('Seasonal orders')
            optMod.arima_seasonalOrderCheck.clicked.connect(showOrder)
            optMod.arima_seasonalOrder = QLineEdit()
            optMod.arima_seasonalOrder.setInputMask('9,9,9')
            optMod.arima_seasonalOrder.setText('0,0,1')
            optMod.arima_seasonalOrder.setMaximumWidth(80)
            # should also add period

            showOptions()
            showOrder()

            arimaLayout.addWidget(optMod.arima_automatic, 0, 0, 1, 2)
            arimaLayout.addWidget(optMod.arima_orderCheck, 1, 0)
            arimaLayout.addWidget(optMod.arima_order, 1, 1)
            arimaLayout.addWidget(optMod.arima_seasonalOrderCheck, 2, 0)
            arimaLayout.addWidget(optMod.arima_seasonalOrder, 2, 1)
            arimaLayout.setAlignment(Qt.AlignCenter)

            optMod.arimaGroup.setLayout(arimaLayout)
            modelOptionsGroupLayout.addWidget(optMod.arimaGroup)

        def optETS(optMod):
            optMod.etsGroup = QGroupBox('ETS')
            optMod.etsGroup.setCheckable(True)
            etsLayout = QGridLayout()

            def showModel():
                if optMod.ets_auto.isChecked():
                    optMod.ets_seasonal.hide()
                    optMod.ets_seasonal_model.hide()
                    optMod.ets_trend.hide()
                    optMod.ets_trend_model.hide()
                    optMod.ets_random.hide()
                    optMod.ets_random_model.hide()

                    ets_preiodLbl.hide()
                    optMod.ets_period.hide()
                else:
                    optMod.ets_seasonal.show()
                    optMod.ets_seasonal.setChecked(False)
                    optMod.ets_trend.show()
                    optMod.ets_trend.setChecked(False)
                    optMod.ets_random.show()
                    optMod.ets_random.setChecked(False)

                    ets_preiodLbl.show()
                    optMod.ets_period.show()
                    showModels()

            def showModels():
                if optMod.ets_seasonal.isChecked():
                    optMod.ets_seasonal_model.show()
                    optMod.ets_seasonal.setText('Seasonal:')
                else:
                    optMod.ets_seasonal_model.hide()
                    optMod.ets_seasonal.setText('Seasonal')

                if optMod.ets_trend.isChecked():
                    optMod.ets_trend_model.show()
                    optMod.ets_trend.setText('Trend:')
                else:
                    optMod.ets_trend_model.hide()
                    optMod.ets_trend.setText('Trend:')

                if optMod.ets_random.isChecked():
                    optMod.ets_random_model.show()
                    optMod.ets_random.setText('Random:')
                else:
                    optMod.ets_random_model.hide()
                    optMod.ets_random.setText('Random')

            optMod.ets_auto = QCheckBox('Choose model automatically')
            optMod.ets_auto.clicked.connect(showModel)
            optMod.ets_auto.setChecked(True)

            models = ['additive', 'multiplicative', 'auto']
            optMod.ets_seasonal = QCheckBox('Seasonal')
            optMod.ets_seasonal.clicked.connect(showModels)
            optMod.ets_seasonal_model = QComboBox()
            optMod.ets_seasonal_model.addItems(models)

            optMod.ets_trend = QCheckBox('Trend')
            optMod.ets_trend.clicked.connect(showModels)
            optMod.ets_trend_model = QComboBox()
            optMod.ets_trend_model.addItems(models)

            optMod.ets_random = QCheckBox('Random')
            optMod.ets_random.clicked.connect(showModels)
            optMod.ets_random_model = QComboBox()
            optMod.ets_random_model.addItems(models)

            ets_preiodLbl = QLabel('Estimated frequency:')
            optMod.ets_period = QSpinBox()
            optMod.ets_period.setMinimum(2)
            optMod.ets_period.setValue(12)
            ets_preiodLbl.hide()
            optMod.ets_period.hide()

            showModels()
            showModel()

            etsLayout.addWidget(optMod.ets_auto, 0, 0, 1, 2)
            etsLayout.addWidget(optMod.ets_seasonal, 1, 0)
            etsLayout.addWidget(optMod.ets_seasonal_model, 1, 1)
            etsLayout.addWidget(optMod.ets_trend, 2, 0)
            etsLayout.addWidget(optMod.ets_trend_model, 2, 1)
            etsLayout.addWidget(optMod.ets_random, 3, 0)
            etsLayout.addWidget(optMod.ets_random_model, 3, 1)
            etsLayout.addWidget(ets_preiodLbl, 4, 0)
            etsLayout.addWidget(optMod.ets_period, 4, 1)

            etsLayout.setAlignment(Qt.AlignCenter)

            optMod.etsGroup.setLayout(etsLayout)
            modelOptionsGroupLayout.addWidget(optMod.etsGroup)

        def optSTS(optMod):
            optMod.stsGroup = QGroupBox('StructTS')
            optMod.stsGroup.setCheckable(True)
            stsLayout = QHBoxLayout()

            sts_typeLbl = QLabel('Structural model type:')
            optMod.sts_type = QComboBox()
            optMod.sts_type.addItems(['level', 'trend', 'BSM'])

            stsLayout.setAlignment(Qt.AlignCenter)
            stsLayout.addWidget(sts_typeLbl)
            stsLayout.addWidget(optMod.sts_type)

            optMod.stsGroup.setLayout(stsLayout)
            modelOptionsGroupLayout.addWidget(optMod.stsGroup)

        def compileOptions(optMod):
            options = {}
            # HoltWinter
            try:
                if optMod.hwGroup.isChecked():
                    options['hw_gamma'] = optMod.seasonal.isChecked()
                    if options['hw_gamma']:
                        options['hw_model'] = str(optMod.model.currentText())
                        options['hw_period'] = optMod.period.value()
            except Exception:
                pass
            # Harmonic Regression
            try:
                if optMod.arGroup.isChecked():
                    options['ar_aic'] = optMod.ar_useAIC.isChecked()
                    options['ar_method'] = str(optMod.ar_method.currentText())
                    options['ar_order'] = optMod.ar_order.value()
            except Exception:
                pass
            # LSF
            try:
                if optMod.lsfGroup.isChecked():
                    options['lsf_aic'] = optMod.lsf_useAIC.isChecked()
                    options['lsf_order'] = optMod.lsf_order.value()
            except Exception:
                pass
            # ARIMA
            try:
                if optMod.arimaGroup.isChecked():
                    options['arima_auto'] = optMod.arima_automatic.isChecked()
                    options['arima_nons'] = optMod.arima_orderCheck.isChecked()
                    options['arima_nons_order'] = [int(o) for o in
                                                   optMod.arima_order.text().split(',')]
                    options['arima_seas'] = optMod.arima_seasonalOrderCheck.isChecked()
                    options['arima_seas_order'] = [int(o) for o in
                                                   optMod.arima_seasonalOrder.text().split(',')]
            except Exception:
                pass
            # ETS
            try:
                if optMod.etsGroup.isChecked():
                    modelId = { 'additive': 'A', 'multiplicative': 'M', 'auto': 'Z', 'none': 'N'}
                    options['ets_auto'] = optMod.ets_auto.isChecked()
                    options['ets_period'] = optMod.ets_period.value()
                    
                    if optMod.ets_seasonal.isChecked():
                        options['ets_seasonal_model'] = \
                            modelId[str(optMod.ets_seasonal_model.currentText())]
                    else:
                        options['ets_seasonal_model'] = modelId['none']
                    if optMod.ets_trend.isChecked():
                        options['ets_trend_model'] = \
                            modelId[str(optMod.ets_trend_model.currentText())]
                    else:
                        options['ets_trend_model'] = modelId['none']
                    if optMod.ets_random.isChecked():
                        options['ets_random_model'] = \
                            modelId[str(optMod.ets_random_model.currentText())]
                    else:
                        options['ets_random_model'] = modelId['none']
            except Exception:
                pass
            # StructTS
            try:
                if optMod.stsGroup.isChecked():
                    options['sts_type'] = str(optMod.sts_type.currentText())
            except Exception:
                pass

            options['append_fit'] = not allowZeroShift.isChecked()

            return options

        for model in uniqueModels(self.multiModel.values()):
            try:
                {Models.Holt_Winters: optHW,
                        Models.Harmonic_Regression: optAR,
                        Models.Least_Squares_Fit: optLSF,
                        Models.ARIMA: optARIMA,
                        Models.ETS: optETS,
                        Models.StructTS: optSTS,
                }[model](optMod)
            except KeyError:
                pass

        if self.isSWT:
            if self.autoBaseSWT.isChecked():
                def basicModels():
                    if optMod.node_label.isChecked():
                        optMod.node_label.setText('Process node levels using:')
                        optMod.node_combo.show()
                    else:
                        optMod.node_label.setText('Process node levels')
                        optMod.node_combo.hide()

                basicLvlLayout = QHBoxLayout()
                optMod.node_label = QCheckBox('Process node levels')
                optMod.node_label.clicked.connect(basicModels)
                optMod.node_combo = QComboBox()
                optMod.node_combo.addItems(
                    prettifyNames(Models._enums.values()))

                basicModels()

                basicLvlLayout.addWidget(optMod.node_label)
                basicLvlLayout.addWidget(optMod.node_combo)
                basicLvlLayout.setAlignment(Qt.AlignCenter)

                modelOptionsGroupLayout.addLayout(basicLvlLayout)

        modelsListLayout.addWidget(simulateButton)
        modelsListLayout.addWidget(forecastSteps)

        # labels
        self.implementLayout.addLayout(lblLayout, 0, 0)
        # controls
        self.implementLayout.addLayout(modelsListLayout, 1, 0)
        # models
        self.implementLayout.addWidget(modelsStack, 2, 0)
        # options groups
        self.implementLayout.addLayout(modelOptionsLayout, 3, 0)
        # batch controls
        self.implementLayout.addLayout(batchLayout, 4, 0)

        self.implementLayout.setAlignment(Qt.AlignCenter)

        if self.toggleShadows.isChecked():
            walkNonGridLayoutShadow(modelsListLayout)
            walkNonGridLayoutShadow(modelOptionsLayout)
            walkNonGridLayoutShadow(shiftLayout)
            walkNonGridLayoutShadow(modelOptButtons)
            walkNonGridLayoutShadow(batchLayout)

#####################################################
#-------------- resulting forecast -----------------#
#####################################################
    def updateResultingTS(self):
        if self.processedWCoeffs is None:
            self.resultingGraph.updatePlot(pywt.waverec(self.wCoefficients, self.wavelet),
                                           label='Simulation', color='r')
            self.resultingGraph.show()
            self.toolsFrame.updateLog(['no new data: reconstructed initial decomposition'])
        else:
            try:
                if not self.isSWT:
                    self.resultingForecast = pywt.waverec(
                                        update_dwt(self.processedWCoeffs, self.wavelet),
                                        self.wavelet, mode=self.signalEx)
                    self.resultingGraph.updatePlot(self.resultingForecast, label='Simulation', color='r')
                else:
                    if self.nodesProcessed:
                             self.resultingGraph.updatePlot(iswt(update_swt(self.wInitialCoefficients,
                                                                            self.processedWCoeffs,
                                                                            self.wUpdatedNodeCoefficients),
                                                                 self.wavelet),
                                                       label='Simulation', color='r')
                    else:
                        self.resultingForecast = iswt(update_selected_levels_swt(self.wInitialCoefficients,
                                                                                       self.processedWCoeffs),
                                                                                self.wavelet)
                        self.resultingGraph.updatePlot(self.resultingForecast, label='Simulation', color='r')
                if self.autoUpdateTable.isChecked():
                    try:
                        self.toolsFrame.updateTable(self.resultingForecast, 'Forecast')
                    except Exception:
                        pass

                # draw forecast boundary
                if 'bound' not in [line._label for line in self.resultingGraph.canvas.ax.get_lines()]:
                    self.resultingGraph.canvas.ax.axvline(x=len(self.currentDataSet[0]) - 1, color='m',
                                                          linestyle='dashed', label='bound')
                self.resultingGraph.show()

                self.toolsFrame.updateLog(['reconstruction complete [' + str(len(self.processedWCoeffs)) + ' levels]'])
            except Exception, e:
                if self.showStacktrace.isChecked():
                    message = traceback.format_exc(e)
                else:
                    message = str(e)
                self.messageInfo.showInfo(message, True)
                self.toolsFrame.updateLog([message], True)
                log.exception(e)

    def updateResultingTSWithInitialData(self):
        #TODO: add information regarding processed levels
        self.resultingGraph.updatePlot(self.currentDataSet[0], label='Initial data', color='b')
        self.resultingGraph.show()

    def clearResultingGraph(self):
        self.resultingGraph.canvas.ax.clear()
        self.resultingGraph.canvas.draw()

#####################################################
#------------- utilities and modules ---------------#
#####################################################
    def showWizard(self):
        self.wizard.restart()
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
        self.R('ver <- R.Version()$version.string')
        QMessageBox.about(self, 'About muScale',
                          'Version:\t' + __version__ + '\nPython:\t' + platform.python_version() +
                          '\nQtCore:\t' + PYQT_VERSION_STR +
                          '\nR:\t' + self.R.ver.split()[2] +
#                          '\n' + '  ' + '-' * 22 + # mmm, magic number!
                          '\n' + '  ' * 10 + '***'
                            '\nPlatform:\t' + platform.system() + ' ' + platform.release() +
                            '\nAuthor:\t' + 'Artiom Basenko')

    def closeEvent(self, event):
        if self.hidetoTray.isChecked() and self.forbidClose:
            self.hide()
            self.messageInfo.hide()
            self.infoDialog.hide()
            self.toolsFrame.hide()
            self.trayIcon.show()
            event.ignore()
        else:
            self.saveConfig()
            clearFolderContents(RES + TEMP)
            self.toolsFrame.close()
            self.infoDialog.close()
            self.messageInfo.close()
            event.accept()

    def restoreFromTray(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()
            self.trayIcon.hide()
            
    def quit(self):
        self.forbidClose = False
        self.close()

    def showHide(self):
        self.show()
        self.trayIcon.hide()

#####################################################
#---------------------- tests ----------------------#
#####################################################

    def performModellingCycleGUI(self):
        self.toolsFrame.updateLog(['starting modelling cycle test...'], NB=True)
        # loading data
        self.manualDataInput.setText(' '.join([str(value) for value in test_data]))
        # parse data
        self.manualData()
        # perform SWT
        self.spinLevels.setValue(4)
        self.waveletTransform()
        # construct model
        self.applyAuto.click()
        self.addAllLevelToModel()
        self.constructModel()

        if hasattr(self, 'testHandle'):
            if self.testHandle.forecastAll is not None:
                self.testHandle.forecastAll.click()

                self.reconTS.click()
                self.plotInitial.click()

        self.toolsFrame.updateLog(['modelling cycle test complete'], NB=True)
        self.messageInfo.showInfo('Modelling cycle performed successfully')

        self.statTools.setCurrentIndex(int(Tabs.Results))

    def reInitR(self):
        self.R = R(R_BIN)
        return self.R

## Hover event filter for level names.
class LabelFilter(QObject):
    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverEnter:
            object.setStyleSheet('QLabel { color: SteelBlue; }')
        if event.type() == QEvent.HoverLeave:
            object.setStyleSheet('QLabel { color: black; }')

        return False

## Model forecasting thread.
class ModelThread(QThread):
    done = pyqtSignal(ndarray, int)

    def __init__(self, model, data, r, steps, options, index, parent=None):
        super(ModelThread, self).__init__(parent)
        self.model = model
        self.data = data
        self.r = r
        self.steps = steps
        self.options = options
        self.index = index

    def run(self):
        self.result = calculateForecast(self.model, self.data,
                                        self.r, self.steps, self.options)
        self.done.emit(self.result, self.index)

## Multi-model forecasting thread.
class MultiModelThread(QThread):
    done = pyqtSignal(list)

    def __init__(self, models, data, r, steps, options, parent=None):
        super(MultiModelThread, self).__init__(parent)
        self.models = models
        self.data = data
        self.r = r
        self.steps = steps
        self.options = options
        self.results = []

    def run(self):
        for model in self.models:
            self.results.append((model, 
                                 calculateForecast(self.models[model],
                                                          self.data[model],
                                        self.r, self.steps, self.options)))

        self.done.emit(self.results)