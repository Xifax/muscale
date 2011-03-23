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

#from pyqtgraph.PlotWidget import *
#from pyqtgraph.graphicsItems import *

# own #
from utils.log import log
from utils.const import __name__,\
                        __version__,\
                        WIDTH, HEIGHT,\
                        RES, ICONS,\
                        FULL_SCREEN, NORMAL_SIZE, LOGO, WIZARD, TOOLS
from utils.guiTweaks import unfillLayout 
from stats.parser import DataParser
from gui.guiTool import ToolsFrame

#from gui.qtPlot import QtDetatchedPlot
#from graphWidget import MPL_Widget

####################################
#            GUI classes           #
####################################

class MuScaleMainDialog(QMainWindow):
    def __init__(self, parent=None):
        super(MuScaleMainDialog, self).__init__(parent)
        
        ### components ###
        from datetime import datetime
        start = datetime.now()
        
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
        #self.loadDataLayout.addWidget(self.tableResults)         

        self.loadDataGroup.setLayout(self.loadDataLayout)
        
        # wavelet decomposition #
        self.decompGroup = QGroupBox('Data decomposition')
        self.decompLayout = QGridLayout()
        
        self.comboWavelet = QComboBox()
        self.comboDecomposition = QComboBox()
        self.spinLevels = QSpinBox()
        self.calculateButton = QPushButton('Analyze data')
        self.resultsView = QTextEdit()
        
        self.decompLayout.addWidget(self.comboWavelet, 0, 0)
        self.decompLayout.addWidget(self.comboDecomposition, 0, 1)
        self.decompLayout.addWidget(self.spinLevels, 0, 2)
        self.decompLayout.addWidget(self.calculateButton, 1, 0, 1, 3)
        self.decompLayout.addWidget(self.resultsView, 2, 0, 1, 3)
        
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
        
        self.setCentralWidget(self.centralWidget)
        
        self.trayIcon = QSystemTrayIcon(self)
        
        # dialogs #
        self.openFileDialog = QFileDialog(self)
        
        # session variables #
        self.currentDataSet = []
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
        self.toolsFrame = ToolsFrame(self.R)
        
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
        self.spinLevels.setRange(1, 10)
        self.resultsView.setHidden(True)
        self.resultsView.setReadOnly(True)
        self.resultsView.setMinimumWidth(WIDTH - 100)
        self.resultsView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
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
        
        self.toolBar.addAction(self.toggleSizeAction)
        self.toolBar.addAction(self.toggleTools)
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
    
    def moveEvent(self, event):
        self.updateToolsPosition()
        
    def updateToolsPosition(self):
        self.toolsFrame.move( self.x() + self.width() + 20, self.y() )
    
    def openFile(self):
        
        if self.openFileDialog.exec_():
            fileName = self.openFileDialog.selectedFiles()   #NB: multiple files selection also possible!
            try:
                if len(fileName) > 0:
                    self.currentDataSet = DataParser.getTimeSeriesFromTextData(data = open(fileName[0], 'r').read())
                    self.showParseResults()
            except:
                QMessageBox.warning(self, 'File error', 'Could not read specified file! ')
                log.error('could not open ' + fileName)
                
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
        
        self.statTools.setItemEnabled(1, False)
        self.statTools.setItemEnabled(2, False)
        self.statusBar.showMessage('Data cleared')
        
        self.resultsView.clear()
        self.resultsView.setHidden(True)
        self.calculateButton.setText('Analyze data')
        
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
            self.toolsFrame.plotWidget.plot(self.currentDataSet[0])
            self.toolsFrame.show()
            self.toolsFrame.toolTabs.setCurrentIndex(1)
            self.showGraph.setText('Hide graph')
        else:
            self.toolsFrame.hide()
            self.showGraph.setText('Show graph')
        
#        import matplotlib.pyplot as plt
#        
#        plt.plot([1,2,3,4])
#        plt.ylabel('some numbers')
#        plt.show()
        
    def waveletTransform(self):
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
        self.resultsView.setVisible(True)
        self.calculateButton.setText('Reanalyze data')
        
        self.R['wcoeff'] = self.wCoefficients
        self.toolsFrame.updateNamespace()
        self.statusBar.showMessage("Added 'wcoeff' variable to R namespace")
        
        #self.resultsView.updateGeometry()
        self.constructModelTemplate()
        self.statTools.setItemEnabled(2, True)
        
    def constructModelTemplate(self):
        unfillLayout(self.modelLayout)
        nLevels = len(self.wCoefficients)
        
        i = 0
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
            
            self.modelLayout.addWidget(labelModel, i, 0)
            self.modelLayout.addWidget(addModel, i, 1); i = i +1
            self.modelLayout.addWidget(comboModel, i, 0, 1, 2); i = i + 1
            self.modelLayout.addWidget(separator, i, 0, 1, 2); i = i + 1
            
        resetModel = QPushButton('Reset model setup')
        resetModel.clicked.connect(self.resetModel)
        constructModel = QPushButton('Construct multiscale model')
        constructModel.clicked.connect(self.constructModel)
        
        self.modelLayout.addWidget(resetModel, i, 0, 1, 2); i = i + 1
        self.modelLayout.addWidget(constructModel, i + 1, 0, 1, 2)
            
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
    
    def constructModel(self):
        self.multiModel.clear()
        for level in range(0, len(self.wCoefficients)):
            widget = self.modelLayout.itemAtPosition(level * 3, 1).widget()
            if widget.isChecked():
                self.multiModel[level] = self.modelLayout.itemAtPosition(level * 3 + 1 , 0).widget().currentText()
        print self.multiModel
        if self.multiModel == {}:
            QMessageBox.warning(self, 'Undefined model', 'You haven not specified any methods at all!')
            
    def showWizard(self):
        pass
    
    def quitApplication(self):
        self.close()