# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWizard, QWizardPage, \
                        QLabel, QVBoxLayout, QPixmap, \
                        QLineEdit, QToolButton, QGridLayout, QFileDialog

# own #
from utility.const import RES, ICONS, LOGO, DATA_LOW_LIMIT
from stats.parser import DataParser

class MuWizard(QWizard):

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)

        self.addPage(self.introPage())
        self.addPage(self.loadPage())
#        self.addPage(self.modelsPage())
#        self.addPage(self.resultsPage())
        self.setWindowTitle('Wizard of muScale')
        self.setPixmap(QWizard.LogoPixmap, QPixmap(RES + ICONS + LOGO))

        self.data = None

    def introPage(self):
        intro = QWizardPage()

        intro.setTitle('Hello and welcome')
        label = QLabel('''This is a wizard.
Now you're ready to forecast some time series!
        ''')

        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        intro.setLayout(layout)

        return intro

    def loadPage(self):
        load = QWizardPage()

        load.setTitle('Initial data')
        pathLbl = QLabel("<font style='color: gray'>Specify the file with time series to forecast:</font>")
        self.path = QLineEdit()
        self.path.setPlaceholderText('path to file')
        getPath = QToolButton()
        getPath.setText('...')

        self.resultLbl = QLabel()
        self.resultLbl.setAlignment(Qt.AlignCenter)
        self.resultLbl.hide()

        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.hide()

        getPath.clicked.connect(self.loadData)

        layout = QGridLayout()
        layout.addWidget(pathLbl, 0, 0)
        layout.addWidget(self.path, 1, 0)
        layout.addWidget(getPath, 1, 1)
        layout.addWidget(self.resultLbl, 2, 0, 1, 2)
        layout.addWidget(self.preview, 2, 0, 1, 2)
        load.setLayout(layout)

        return load

    def modelsPage(self):
        pass

    def resultsPage(self):
        pass

    #---- actions ----#
    def loadData(self):
        fileName = unicode(QFileDialog.getOpenFileName(self, 'Open text file', RES))
        if fileName:
            if DataParser.istextfile(fileName):
                self.data = DataParser.getTimeSeriesFromTextData(data=open(fileName, 'r').read())
                if len(self.data[0]) > DATA_LOW_LIMIT:
                    self.resultLbl.setText('Success! Loaded<b> ' + str(len(self.data[0])) +
                                           '</b> values, errors: <b>' + str(
                                            self.data[1]) + '</b>')
                    self.resultLbl.show()
                    self.path.setText(fileName)

                    self.preview.setText(' '.join(self.data[0][:DATA_LOW_LIMIT]))
                    self.preview.show()
                else:
                    self.resultLbl.setText('Not enough values to form data series.')
                    self.resultLbl.show()
            else:
                self.resultLbl.setText('Specified file is binary file!')
                self.resultLbl.show()