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
import PySide
from PySide.QtCore import *
from PySide.QtGui import *

# own #
from utils.const import __name__,\
                        __version__,\
                        WIDTH, HEIGTH
from stat.parser import DataParser

####################################
#            GUI classes           #
####################################

class MuScaleMainDialog(QMainWindow):
    def __init__(self, parent=None):
        super(MuScaleMainDialog, self).__init__(parent)
        
        ### components ###
        
        # data loaders #
        self.loadDataGroup = QGroupBox('Data source')
        self.loadDataLayout = QVBoxLayout()
        
        self.loadFromFile = QPushButton('Load from file')
        # manual
        self.toggleManual = QPushButton('Manual input')
        self.manualDataInput = QTextEdit()
        self.loadManualData = QPushButton('Parse')
        # results
        self.parseResults = QLabel('')
        self.showGraph = QPushButton('Show graph')
        self.showTable = QPushButton('Show table')
        self.clearAll = QPushButton('Reset data')
        
        
        self.loadDataLayout.addWidget(self.loadFromFile)
        self.loadDataLayout.addWidget(self.toggleManual)
        self.loadDataLayout.addWidget(self.manualDataInput)        
        self.loadDataLayout.addWidget(self.loadManualData)        
        self.loadDataLayout.addWidget(self.parseResults)        
        self.loadDataLayout.addWidget(self.showGraph)        
        self.loadDataLayout.addWidget(self.showTable)        
        self.loadDataLayout.addWidget(self.clearAll)        

        self.loadDataGroup.setLayout(self.loadDataLayout)
        
        # wavelet decomposition #
        self.decompGroup = QGroupBox('Data decomposition')
        self.decompLayout = QVBoxLayout()
        
        self.decompGroup.setLayout(self.decompLayout)
        
        # menus, toolbars, layouts & composition #
        self.centralWidget = QWidget(self)
        
        self.statTools = QToolBox()
        self.statTools.addItem(self.loadDataGroup, 'Loading data')
        self.statTools.addItem(self.decompGroup, 'Analyzing data')
        
        self.menuBar = QMenuBar()
        self.toolBar = QToolBar()
        self.statusBar = QStatusBar()
                
        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainLayout.addWidget(self.statTools)
        
        self.addToolBar(self.toolBar)
        self.setMenuBar(self.menuBar)
        self.setStatusBar(self.statusBar)
        
        self.setCentralWidget(self.centralWidget)
        
        # dialogs #
        self.openFileDialog = QFileDialog(self)
        
        # temporary variables #
        self.currentDataSet = []
        
        ### initialization ###
        self.initComposition()
        self.initComponents()
        self.initActions()
        
        ### start ###
        self.statusBar.showMessage('Ready!')
                
        ### test ###
        print 'okay.jpeg'
        
#------------------- initialization ------------------#
    
    def initComposition(self):
        self.setWindowTitle(__name__ + ' ' +  __version__)
        
        desktop = QApplication.desktop()
        self.setGeometry(QRect( (desktop.width() - WIDTH)/2, (desktop.height() - HEIGTH)/2, WIDTH, HEIGTH) )
    
    def initComponents(self):
        # load data items #
        self.toggleManual.setCheckable(True)
        self.manualDataInput.setHidden(True)
        self.loadManualData.setHidden(True)
        self.parseResults.setHidden(True)
        self.showGraph.setHidden(True)
        self.showTable.setHidden(True)
        self.clearAll.setHidden(True)
        
        self.parseResults.setAlignment(Qt.AlignCenter)
        
        # dialogs #
        self.openFileDialog.setFileMode(QFileDialog.ExistingFile)
        self.openFileDialog.setViewMode(QFileDialog.List)
        
        # layouts #
        self.loadDataLayout.setAlignment(Qt.AlignCenter)
    
    def initActions(self):
        # menu actions #
        quitAction = QAction('&Quit', self)
        quitAction.triggered.connect(self.quitApplication)
        aboutAction = QAction('&About', self)
        aboutAction.triggered.connect(self.showAbout)
        
        self.menuBar.addAction(aboutAction)
        self.menuBar.addAction(quitAction)
        
        # load data actions #
        self.toggleManual.clicked.connect(self.toggleInputField)
        self.loadFromFile.clicked.connect(self.openFile)
        self.loadManualData.clicked.connect(self.manualData)
        self.clearAll.clicked.connect(self.resetData)
    
#------------------- actions ------------------#
    
    def openFile(self):
        
        if self.openFileDialog.exec_():
            fileName = self.openFileDialog.selectedFiles()   #NB: multiple files selection also possible!
            try:
                if len(fileName) > 0:
                    self.currentDataSet = DataParser.getTimeSeriesFromTextData(data = open(fileName[0], 'r').read())
                    self.showParseResults()
            except:
                QMessageBox.warning(self, 'File error', 'Could not read specified file! ')
                
    def manualData(self):
        self.currentDataSet = DataParser.getTimeSeriesFromTextData(self.manualDataInput.toPlainText())
        self.showParseResults()
        
    def showParseResults(self):
        if len(self.currentDataSet) == 2:
            self.parseResults.setText('Success! Loaded ' + str(len(self.currentDataSet[0])) +' values, errors: ' + str(self.currentDataSet[1]) )
            self.parseResults.setVisible(True)
            self.showGraph.setVisible(True)
            self.showTable.setVisible(True)
            self.clearAll.setVisible(True)
        else:
            self.parseResults.setText('Could not parse at all!')
            self.parseResults.setVisible(True)
            
    def resetData(self):
        self.currentDataSet = []
        self.loadManualData.setHidden(True)
        self.parseResults.setHidden(True)
        self.showGraph.setHidden(True)
        self.showTable.setHidden(True)
        self.clearAll.setHidden(True)
        
    def toggleInputField(self):
        if self.toggleManual.isChecked():
            self.manualDataInput.setVisible(True)
            self.loadManualData.setVisible(True)
        else:
            self.manualDataInput.setHidden(True)
            self.loadManualData.setHidden(True)
        
    def showAbout(self):
        QMessageBox.about(self, 'About muScale','Version:\t' + __version__ + '\nPython:\t' + platform.python_version() + 
                           '\nPySide:\t' + PySide.__version__ + '\nQtCore:\t' + PySide.QtCore.__version__ + 
                           '\nPlatform:\t' + platform.system())
    
    def quitApplication(self):
        self.close()