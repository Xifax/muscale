# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from PyQt4.QtCore import Qt, QObject, QEvent
from PyQt4.QtGui import QWizard, QWizardPage, \
                        QLabel, QVBoxLayout, QPixmap, QPushButton, \
                        QLineEdit, QToolButton, QGridLayout, QFileDialog, \
                        QCheckBox, QDialog, QListWidget, QListWidgetItem, QAction, \
                        QAbstractItemView
# own #
from utility.const import RES, ICONS, LOGO, DATA_LOW_LIMIT, FONTS_DICT
from stats.parser import DataParser

class Filter(QObject):
    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverEnter:
            object.setText(str(object.text()).split('</b>')[0] +
                           str(object.text()).split('</b>')[1] +
                           "</b><br/><font style='color: gray'>Click to show all series</font>")
        if event.type() == QEvent.HoverLeave:
            object.setText(str(object.text()).split('</b>')[0].replace('Preview:', 'Preview:</b>'))
        if event.type() == QEvent.MouseButtonPress:
            object.parent().previewSeries.show()

        return False

class MuWizard(QWizard):

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)

        self.data = None

        self.addPage(self.introPage())
        self.addPage(self.loadPage())
        self.addPage(self.modelsPage())
        self.addPage(self.resultsPage())
        self.setWindowTitle('Wizard of muScale')
        self.setPixmap(QWizard.LogoPixmap, QPixmap(RES + ICONS + LOGO))

#        test = QLabel('lalala')
#        self.setSideWidget(test)

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
        load = WizardPageEx()

        load.setTitle('Initial data')
        pathLbl = QLabel("<font style='color: gray'>Specify the file with time series to forecast:</font>")
        loadLbl = QLabel("<font style='color: gray'>Click</font>")
        loadLbl.setAlignment(Qt.AlignCenter)

        self.path = QLineEdit()
        self.path.setPlaceholderText('path to file')
        getPath = QToolButton()
        getPath.setText('...')

        self.resultLbl = QLabel()
        self.resultLbl.setAlignment(Qt.AlignCenter)
        self.resultLbl.hide()

        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setWordWrap(True)
        self.preview.hide()

        self.preview.setAttribute(Qt.WA_Hover)
        self.filter = Filter()
        self.preview.installEventFilter(self.filter)

        getPath.clicked.connect(self.loadData)

        layout = QGridLayout()
        layout.addWidget(pathLbl, 0, 0)
        layout.addWidget(loadLbl, 0, 1)
        layout.addWidget(self.path, 1, 0)
        layout.addWidget(getPath, 1, 1)
        layout.addWidget(self.resultLbl, 2, 0, 1, 2)
        layout.addWidget(self.preview, 3, 0, 1, 2)
        load.setLayout(layout)

        load.previewSeries = SeriesPreview()
        self.previewSeries = load.previewSeries

        # to be able to reference from class namespace
        self.loadCheck = load.check

        return load

    def modelsPage(self):
        models = QWizardPage()
        return models

    def resultsPage(self):
        results = QWizardPage()
        results.setFinalPage(True)
        return results

    #---- actions ----#
    def loadData(self):
        fileName = unicode(QFileDialog.getOpenFileName(self, 'Open text file', RES))
        if fileName:
            self.resultLbl.hide()
            self.preview.hide()
            if DataParser.istextfile(fileName):
                self.data = DataParser.getTimeSeriesFromTextData(data=open(fileName, 'r').read())
                if len(self.data[0]) > DATA_LOW_LIMIT:
                    self.resultLbl.setText("<font style='color: gray'>Success! Loaded<b> " + str(len(self.data[0])) +
                                           '</b> values, errors: <b>' + str(
                                            self.data[1]) + '</b></font>')
                    self.resultLbl.show()
                    self.path.setText(fileName)

                    previewLength = 40
                    self.preview.setText("<font style='color: gray'><b>Preview:</b> "+ ' '.join(
                                        [str(e) for e in self.data[0][:previewLength]]) +
                                        "...</font>")
                    self.previewSeries.updateData(self.data)
                    self.preview.show()
                    self.loadCheck.setChecked(True)
                else:
                    self.resultLbl.setText('Not enough values to form data series.')
                    self.resultLbl.show()
            else:
                self.resultLbl.setText('Specified file is binary file!')
                self.resultLbl.show()

    def checkData(self):
        if self.data is None:
#            self.button(QWizard.NextButton).setEnabled(False)
            pass
        else:
            try:
                self.loadCheck.setChecked(True)
            except Exception:
                pass
#            self.button(QWizard.NextButton).setEnabled(True)

    def initializePage(self, p_int):
        nop = lambda: None

        {0: nop,
         1: self.checkData,
         2: nop,
         3: nop,
        }[p_int]()

class WizardPageEx(QWizardPage):

    def __init__(self, parent=None):
        QWizardPage.__init__(self, parent)

        self.check = QCheckBox()
        self.check.setVisible(False)
        self.registerField('check*', self.check)
        self.check.setChecked(False)

    def initializePage(self):
        pass

class SeriesPreview(QDialog):

    def __init__(self, parent=None):
        super(SeriesPreview, self).__init__(parent)

        self.data = None
        self.workingSet = None

        self.list = QListWidget()
        self.cancel = QPushButton('Close')
        self.apply = QPushButton('Update')

        self.layout = QGridLayout()
        self.layout.addWidget(self.list, 0, 0, 1, 2)
        self.layout.addWidget(self.apply, 1, 0)
        self.layout.addWidget(self.cancel, 1, 1)
        self.setLayout(self.layout)

        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.initComponents()
        self.initActions()

    def initComponents(self):
        self.list.setAlternatingRowColors(True)
        self.list.setStyleSheet('''QListView::item:selected:active {
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

        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.setContextMenuPolicy(Qt.ActionsContextMenu)

    def initActions(self):
        self.apply.clicked.connect(self.applyChanges)
        self.cancel.clicked.connect(self.close)

        self.list.itemDoubleClicked.connect(self.removeFromList)
        self.list.addAction(QAction('&Remove selected', self, triggered=self.removeItems))

    #--- actions ---#
    def updateData(self, data):
        self.data = data
        self.workingSet = data[0][:]
        self.updateList()

    def updateList(self):
        self.list.clear()
        for item in self.workingSet:
            item = QListWidgetItem(str(item))
            item.setTextAlignment(Qt.AlignCenter)
            self.list.addItem(item)

    def applyChanges(self):
        self.data = (self.workingSet, self.data[1])
#        previewLength = 40
#        self.parentWidget().preview.setText("<font style='color: gray'><b>Preview:</b> "+ ' '.join(
#                            [str(e) for e in self.data[0][:previewLength]]) +
#                            "...</font>")

    def removeFromList(self, item):
        self.workingSet.remove(float(item.text()))
        self.list.takeItem(self.list.indexFromItem(item).row())

    def removeItems(self):
        for item in self.list.selectedItems():
            self.workingSet.remove(float(item.text()))
            self.list.takeItem(self.list.indexFromItem(item).row())