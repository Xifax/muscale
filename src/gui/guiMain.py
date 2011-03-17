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
from utils.log import log
from utils.const import __name__,\
                        __version__,\
                        WIDTH, HEIGHT
from stats.parser import DataParser
from gui.guiTool import ToolsFrame

#from graphWidget import MPL_Widget

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
        # table
        self.tableResults = QTableWidget()
        # graph
        #self.graphWidget = MPL_Widget()
        
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
        self.loadDataLayout.addWidget(self.tableResults)        
        #self.loadDataLayout.addWidget(self.graphWidget)        

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
        
        # external gui modules #
        self.toolsFrame = ToolsFrame()
        
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
        self.setGeometry(QRect( (desktop.width() - WIDTH)/2, (desktop.height() - HEIGHT)/2, WIDTH, HEIGHT) )
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
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
        
        #self.parseResults.setFrameShape(QFrame.Box);    self.parseResults.setFrameShadow(QFrame.Sunken)
        
        self.tableResults.setHidden(True)
        self.tableResults.setColumnCount(1)
        self.tableResults.setHorizontalHeaderLabels(['Value'])
        
        # dialogs #
        self.openFileDialog.setFileMode(QFileDialog.ExistingFile)
        self.openFileDialog.setViewMode(QFileDialog.List)
        
        # layouts #
        self.loadDataLayout.setAlignment(Qt.AlignCenter)
        
        # tabs #
        self.statTools.setItemEnabled(1, False)
    
    def initActions(self):
        # menu actions #
        quitAction = QAction('&Quit', self)
        quitAction.triggered.connect(self.quitApplication)
        aboutAction = QAction('&About', self)
        aboutAction.triggered.connect(self.showAbout)
        
        self.menuBar.addAction(aboutAction)
        self.menuBar.addAction(quitAction)
        
        self.toggleSizeAction = QAction('&Full screen', self)
        self.toggleSizeAction.triggered.connect(self.fullScreen)
        self.toggleSizeAction.setCheckable(True)
        
        self.toggleTools = QAction('&Show tools', self)
        self.toggleTools.triggered.connect(self.showTools)
        self.toggleTools.setCheckable(True)
        
        self.toolBar.addAction(self.toggleSizeAction)
        self.toolBar.addAction(self.toggleTools)
        
        # load data actions #
        self.toggleManual.clicked.connect(self.toggleInputField)
        self.loadFromFile.clicked.connect(self.openFile)
        self.loadManualData.clicked.connect(self.manualData)
        self.clearAll.clicked.connect(self.resetData)
        self.showTable.clicked.connect(self.updateTable)
    
#------------------- actions ------------------#
    
    def fullScreen(self):
        if self.toggleSizeAction.isChecked():
            self.showFullScreen()
        else:
            self.showNormal()
            
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
        
        self.tableResults.setHidden(True)
        self.showTable.setText('Show table')
        
        self.statTools.setItemEnabled(1, False)
        
    def updateTable(self):
        
        if self.tableResults.isHidden():
            self.tableResults.setVisible(True)
            
            self.tableResults.clearContents()
            self.tableResults.setRowCount(0)
            
            iterList = []
            iterList = iterList + self.currentDataSet[0]; iterList.reverse()
            
            i = 0
            for element in iterList:
                self.tableResults.insertRow(i)
                self.tableResults.setItem(i, 0, QTableWidgetItem(str(element)))
            
            del iterList
            self.showTable.setText('Hide table')
            
        else:
            self.tableResults.setHidden(True)
            self.showTable.setText('Show table')
        
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
                           '\nPySide:\t' + PySide.__version__ + '\nQtCore:\t' + PySide.QtCore.__version__ + 
                           '\nPlatform:\t' + platform.system())
    
    def quitApplication(self):
        self.close()