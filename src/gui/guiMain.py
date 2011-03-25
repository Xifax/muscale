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

#===============================================================================
# PYSIDE
# import PySide
# from PySide.QtCore import *
# from PySide.QtGui import *
#===============================================================================
import PyQt4
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from stats.pyper import R
import pywt
from numpy import *

#from pyqtgraph.PlotWidget import *
#from pyqtgraph.graphicsItems import *

#from gui.qtPlot import QtDetatchedPlot
#from graphWidget import MPL_Widget

# own #
from utils.log import log
from utils.const import __name__,\
                        __version__,\
                        WIDTH, HEIGHT,\
                        RES, ICONS,\
                        FULL_SCREEN, NORMAL_SIZE, LOGO, WIZARD, TOOLS, INFO
from utils.guiTweaks import unfillLayout 
from stats.parser import DataParser
from gui.guiTool import ToolsFrame
from gui.guiInfo import InfoFrame
from gui.graphWidget import MplWidget

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
        self.toggleManual = QPushButton('&Manual input')
        self.manualDataInput = QTextEdit()
        self.loadManualData = QPushButton('Parse')
        # results
        self.parseResults = QLabel('')
        self.showGraph = QPushButton('Show graph')
        self.showTable = QPushButton('Show table')
        self.clearAll = QPushButton('Reset data')
        
        self.separator = QFrame();   self.separator.setFrameShape(QFrame.HLine);    self.separator.setFrameShadow(QFrame.Sunken)
        
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
        self.calculateButton = QPushButton('Analyze data')
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
        
        # menus, toolbars, layouts & composition #
        self.centralWidget = QWidget(self)
        
        self.statTools = QToolBox()
        self.statTools.addItem(self.loadDataGroup, 'Loading data')
        self.statTools.addItem(self.decompGroup, 'Analyzing data')
        self.statTools.addItem(self.modelGroup, 'Multiscale model')
        self.statTools.addItem(self.implementGroup, 'Results')

        self.menuBar = QMenuBar()
        self.toolBar = QToolBar()
        self.statusBar = QStatusBar()

        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainLayout.addWidget(self.statTools)
        
        self.addToolBar(self.toolBar)
        self.setMenuBar(self.menuBar)
        self.setStatusBar(self.statusBar)
        
        #TODO: context menu
        #self.setContextMenuPolicy()
        
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
        #=======================================================================
        # self.trayIcon.showMessage('Loading...', 'Initializing R', QSystemTrayIcon.MessageIcon.Information, 10000)
        #=======================================================================
        self.trayIcon.showMessage('Loading...', 'Initializing R', QSystemTrayIcon.Information, 10000)
        self.R = R()
        
        # external gui modules #
        self.wizard = None
        self.toolsFrame = ToolsFrame(self.R)
        self.currentPlot = self.toolsFrame.plotWidget.plot()
        self.infoDialog = InfoFrame()
        
        ### start ###
        self.statusBar.showMessage('Ready!')
                
        ### test ###
        print 'okay.jpeg'
        loadingTime = datetime.now() - start
        #=======================================================================
        # self.trayIcon.showMessage('Ready!', 'Launched in ' + str(loadingTime), QSystemTrayIcon.MessageIcon.Information, 10000)
        #=======================================================================
        self.trayIcon.showMessage('Ready!', 'Launched in ' + str(loadingTime), QSystemTrayIcon.Information, 10000)
        QTimer.singleShot(3000, self.trayIcon.hide)
        
#------------------- initialization ------------------#
    
    def initComposition(self):
        self.setWindowTitle(__name__ + ' ' +  __version__)
        
        desktop = QApplication.desktop()
        self.setGeometry(QRect( (desktop.width() - WIDTH)/2, (desktop.height() - HEIGHT)/2, WIDTH, HEIGHT) )
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWindowIcon(QIcon(RES + ICONS + LOGO))
    
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
        self.spinLevels.setRange(1, 6)
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
        self.statTools.setItemEnabled(1, False)
        self.statTools.setItemEnabled(2, False)
        self.statTools.setItemEnabled(3, False)
        
        # etc #
        self.trayIcon.setIcon(QIcon(RES + ICONS + LOGO))
        self.toolBar.setIconSize(QSize(48,48))
    
    def initActions(self):
        # menu actions #
        quitAction = QAction('&Quit', self)
        quitAction.triggered.connect(self.quitApplication)
        aboutAction = QAction('&About', self)
        aboutAction.triggered.connect(self.showAbout)
        
        self.menuBar.addAction(aboutAction)
        self.menuBar.addAction(quitAction)
        
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
        if not self.toolsFrame.toolDetatched.isChecked():
            self.toolsFrame.move( self.x() + self.width() + 20, self.y() )
        
    def updateToolsSize(self):
        if not self.toolsFrame.fixSize.isChecked():
            self.toolsFrame.resize(QSize(self.toolsFrame.width(), self.height()))
        
    def updateInfoPosition(self):
        #self.infoDialog.move( self.x() - self.infoDialog.width() - 20, self.y() * 3./2. )
        #self.infoDialog.move( self.x() - self.infoDialog.width() - 20, self.y() +  self.infoDialog.height()/2 )
        self.infoDialog.move( self.x() - self.infoDialog.width() - 20, self.y() +  self.height()/2 )
    
    #------------------ functionality ----------------#
    def openFile(self):
        
        if self.openFileDialog.exec_():
            fileName = self.openFileDialog.selectedFiles()   #NB: multiple files selection also possible!
            try:
                if len(fileName) > 0:
                    self.currentDataSet = DataParser.getTimeSeriesFromTextData(data = open(fileName[0], 'r').read())
                    self.showParseResults()
            except:
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
            self.parseResults.setText('Success! Loaded<b> ' + str(len(self.currentDataSet[0])) +'</b> values, errors: <b>' + str(self.currentDataSet[1]) + '</b>')
            self.parseResults.setVisible(True)
            self.showGraph.setVisible(True)
            self.showTable.setVisible(True)
            self.clearAll.setVisible(True)
            self.separator.setVisible(True)
                        
            self.statTools.setItemEnabled(1, True)
            
            self.R['data'] = self.currentDataSet[0]
            self.toolsFrame.updateNamespace()
            self.statusBar.showMessage("Added 'data' variable to R namespace")
        else:
            self.parseResults.setText('Could not parse at all!')
            self.parseResults.setVisible(True)
            
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
        
        self.statTools.setItemEnabled(1, False)
        self.statTools.setItemEnabled(2, False)
        self.statTools.setItemEnabled(3, False)
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
        QMessageBox.about(self, 'About muScale','Version:\t' + __version__ + '\nPython:\t' + platform.python_version() + 
                           #====================================================
                           # '\nPySide:\t' + PySide.__version__ + '\nQtCore:\t' + PySide.QtCore.__version__ + 
                           #====================================================
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
        self.scalogramGraph.canvas.ax.clear()
        
        wavelet = pywt.Wavelet( pywt.wavelist(self.comboWavelet.currentText())[0] )
        if self.comboDecomposition.currentIndex() == 0:
            #cA3, cD3, cD2, cD1
            self.wCoefficients = pywt.wavedec(self.currentDataSet[0], wavelet, level=self.spinLevels.value())
        elif self.comboDecomposition.currentIndex() == 1:
            self.wCoefficients = pywt.swt(self.currentDataSet[0], wavelet, level=self.spinLevels.value())
        
        self.resultsView.clear(); i = 0
        for coeff in self.wCoefficients:
            self.resultsView.append('<b>Level ' + str(i) + ':</b>\t' + str(coeff) + '<br/>'); i = i + 1
            #self.resultsView.append('<b>Level ' + str(i) + ':</b>\t' + ' '.join(list(coeff)) + '<br/>'); i = i + 1
            self.scalogramGraph.canvas.ax.plot(coeff)
            
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
        self.decompInfoLabel.setText('Using <b>' + wavelet.name + '</b> wavelet')
        
        self.R['wcoeff'] = self.wCoefficients
        self.toolsFrame.updateNamespace()
        self.statusBar.showMessage("Added 'wcoeff' variable to R namespace")
        
        #self.resultsView.updateGeometry()
        self.constructModelTemplate()
        self.statTools.setItemEnabled(2, True)
        
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
                        #TODO: do something else
                        widget.click()
                        
#                        if not widget.isChecked():
#                            widget.setChecked(True)
#                            widget.setText('OK')
#                            combo = self.modelLayout.itemAtPosition(row + 2, 0).widget()
#                            combo.setDisabled(True)
#
#                        else:
#                            widget.setChecked(False)
#                            widget.setText('+')
#                            combo = self.modelLayout.itemAtPosition(row + 2, 0).widget()
#                            combo.setEnabled(True)
    
    def previewAll(self):
        for row in range(0, self.modelLayout.rowCount()):
            if self.modelLayout.itemAtPosition(row, 2) is not None:
                    widget = self.modelLayout.itemAtPosition(row, 2).widget()
                    if hasattr(widget, 'isCheckable'):
                        if widget.isCheckable():
                            widget.click()
    
    def autoModel(self):
        #TODO: ...
        combo = self.modelLayout.itemAt(self.modelLayout.count() - 5).widget()
        combo.setCurrentIndex(1)
    
    def showComponentPreview(self):
#        self.scalogramGraph.canvas.ax.clear()
#        self.scalogramGraph.canvas.ax.plot()
        #self.gem = self.saveGeometry()
        if self.gem is not None: 
            if not self.toggleSizeAction.isChecked():
                #TODO: change only vertical size, not geometry at all
                self.restoreGeometry(self.gem)

        for row in range(0, self.modelLayout.rowCount()):
            if self.modelLayout.itemAtPosition(row, 2) is not None:
                widget = self.modelLayout.itemAtPosition(row, 2).widget()
                if hasattr(widget, 'isCheckable'):
                    if widget.isCheckable():
                        if widget.isChecked():
                            preview = self.modelLayout.itemAtPosition(row + 2, 0).widget()
                            level = self.modelLayout.itemAtPosition(row, 0).widget()
                            #NB: for 1D array (descrete transform)
                            preview.canvas.ax.plot(self.wCoefficients[level.text().right(1).toInt()[0]])
                            preview.setVisible(True)
                            
                            self.gem = self.saveGeometry()
                            self.resize(self.width(), self.height() + 220)
                        else:
                            preview = self.modelLayout.itemAtPosition(row + 2, 0).widget()
                            preview.setHidden(True)
                            
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
        
        separator_b = QFrame();   separator_b.setFrameShape(QFrame.HLine);    separator_b.setFrameShadow(QFrame.Sunken)
        
        self.modelLayout.addLayout(buttonsLayout, 0, 0, 1, 3)
        self.modelLayout.addWidget(separator_b, 1, 0, 1, 3)
        
        i = 2
        for level in range(0, nLevels):
            labelModel = QLabel('Level ' + str(level))
            
            addModel = QToolButton()
            addModel.setText('+')
            addModel.setCheckable(True)
            addModel.clicked.connect(self.addModel)
            
            comboModel = QComboBox()
            comboModel.addItems(['Harmonic Regression', 'Holt-Winters', 'ARMA'])            
            
            separator = QFrame();   separator.setFrameShape(QFrame.HLine);    separator.setFrameShadow(QFrame.Sunken)
            
            #TODO: add plot preview
            togglePreview = QToolButton()
            togglePreview.setText('Preview')
            togglePreview.setCheckable(True)
            togglePreview.clicked.connect(self.showComponentPreview)
            
            componentPreview = MplWidget()
            componentPreview.setHidden(True)
            
            self.modelLayout.addWidget(labelModel, i, 0)
            self.modelLayout.addWidget(addModel, i, 1)
            self.modelLayout.addWidget(togglePreview, i, 2); i = i +1
#            self.modelLayout.addWidget(comboModel, i, 0, 1, 2); i = i + 1
#            self.modelLayout.addWidget(separator, i, 0, 1, 2); i = i + 1
            self.modelLayout.addWidget(comboModel, i, 0, 1, 3); i = i + 1
            self.modelLayout.addWidget(componentPreview, i, 0, 1, 3); i = i + 1
            self.modelLayout.addWidget(separator, i, 0, 1, 3); i = i + 1
            
        resetModel = QPushButton('Reset model setup')
        resetModel.clicked.connect(self.resetModel)
        constructModel = QPushButton('Construct multiscale model')
        constructModel.clicked.connect(self.constructModel)
        
        self.modelLayout.addWidget(resetModel, i, 0, 1, 3); i = i + 1
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
        self.statTools.setItemEnabled(3, False)
    
    def constructModel(self):
        self.multiModel.clear()
        for level in range(0, len(self.wCoefficients)):
#            widget = self.modelLayout.itemAtPosition(level * 3, 1).widget()
#            if isinstance(widget, QWidget):
#                if widget.isChecked():
#                    self.multiModel[level] = self.modelLayout.itemAtPosition(level * 3 + 1 , 0).widget().currentText()

#            widget = self.modelLayout.itemAtPosition(level * 3 + 2, 1).widget()
#            if isinstance(widget, QWidget):
#                if widget.isChecked():
#                    self.multiModel[level] = self.modelLayout.itemAtPosition(level * 3 + 3 , 0).widget().currentText()

            widget = self.modelLayout.itemAtPosition(level * 4 + 2, 1).widget()
            if isinstance(widget, QWidget):
                if widget.isChecked():
                    self.multiModel[level] = self.modelLayout.itemAtPosition(level * 4 + 3 , 0).widget().currentText()
        print self.multiModel
        if self.multiModel == {}:
            QMessageBox.warning(self, 'Undefined model', 'You haven not specified any methods at all!')
        else:
            self.statTools.setItemEnabled(3, True)
            
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
        #page.setPixmap(QWizard.LogoPixmap, QPixmap(RES + ICONS + LOGO))
        
        self.wizard.addPage(page)
        self.wizard.setWindowTitle("A Wizard")
        #self.wizard.setWizardStyle(QWizard.ClassicStyle)
        #self.wizard.setPixmap(QWizard.LogoPixmap, QPixmap(RES + ICONS + LOGO))
        self.wizard.show()
    
    def quitApplication(self):
        self.close()
        
    def updateInfoTooltips(self):
        #print self.statTools.currentWidget().title()
        if self.toggleInfo.isChecked():
            self.infoDialog.updateContents(self.statTools.currentIndex())
            self.infoDialog.show()
            self.updateInfoPosition()
        else:
            self.infoDialog.hide()