# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from PyQt4.QtCore import Qt, QObject, QEvent, QThread, pyqtSignal, QByteArray
from PyQt4.QtGui import QWizard, QWizardPage, \
                        QLabel, QVBoxLayout, QPixmap, QPushButton, \
                        QLineEdit, QToolButton, QGridLayout, QFileDialog, \
                        QCheckBox, QDialog, QListWidget, QListWidgetItem, QAction, \
                        QAbstractItemView, QSpinBox, QMovie, QComboBox
import pywt

# own #
from utility.const import RES, ICONS, LOGO, DATA_LOW_LIMIT, FONTS_DICT, \
                            MIN_FORECAST, MAX_FORECAST, PROGRESS
from stats.parser import DataParser
from stats.wavelets import calculate_suitable_lvl
from stats.models import auto_model, calculateForecast

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

    def __init__(self, R=None, parent=None):
        QWizard.__init__(self, parent)

        self.R = R
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
        load = WizardPageEx('loadCheck')

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
        models = WizardPageEx('modelCheck')

        lbl = QLabel("<font style='color: gray'>Forecast horizon:</font>")
        self.steps = QSpinBox()
        self.steps.setRange(MIN_FORECAST, MAX_FORECAST)
        self.steps.setValue(10)
        self.start = QPushButton('Forecast')
        self.start.clicked.connect(self.modelling)
        self.custom = QPushButton('Advanced')
        self.processing = QLabel()

        self.gifLoading = QMovie(RES + ICONS + PROGRESS, QByteArray(), self)
        self.gifLoading.setCacheMode(QMovie.CacheAll)
        self.gifLoading.setSpeed(100)
        self.processing.setMovie(self.gifLoading)
        self.processing.setAlignment(Qt.AlignCenter)
        self.processing.hide()

        self.status = QLabel()
        self.status.setAlignment(Qt.AlignCenter)
        self.status.hide()

        layout = QGridLayout()
        layout.addWidget(lbl, 0, 0)
        layout.addWidget(self.steps, 0, 1)
        layout.addWidget(self.start, 0, 2)
        layout.addWidget(self.custom, 0, 3)
        layout.addWidget(self.status, 1, 0, 1, 4)
        layout.addWidget(self.processing, 2, 0, 1, 4)
        models.setLayout(layout)

        self.customOpt = CustomOption()
        self.custom.clicked.connect(self.customOpt.show)
        self.modelCheck = models.check

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

    def modelling(self):
        self.processing.show()
        self.gifLoading.start()
        self.status.setText('')

        statusText = u"<font style='color: gray'>"

        # decomposition #
        if self.customOpt.options['enable']:
            self.signalEx = self.customOpt.options['signal']
            self.wavelet = pywt.Wavelet(self.customOpt.options['wavelet'])
            wLevel = self.customOpt.options['lvls'] - 1
            maxLevel = pywt.dwt_max_level(len(self.data[0]), self.wavelet)

            if wLevel > maxLevel:
                wLevel = maxLevel

            self.wInitialCoefficients = pywt.wavedec(self.data[0], self.wavelet,
                                                       level=wLevel, mode=self.signalEx)
            self.wCoefficients = self.wInitialCoefficients
        else:
            self.signalEx = pywt.MODES.sp1
            self.wavelet = pywt.Wavelet(pywt.wavelist(pywt.families()[1])[6])

            wLevel = calculate_suitable_lvl(self.data[0],
                                         self.wavelet, self.R, swt=False)
            self.wInitialCoefficients = pywt.wavedec(self.data[0], self.wavelet,
                                                     level=wLevel, mode=self.signalEx)
            self.wCoefficients = self.wInitialCoefficients

        statusText += 'Wavelet: <b>' + self.wavelet.family_name + \
                      '</b> (' + self.wavelet.name + ', ' + self.wavelet.symmetry + ')<br/>'

        statusText += 'Discrete Wavelet Transfom: <b>' + str(wLevel + 1) + ' levels</b><br/>'

        # models #
        options = {}
        options['multi'] = True
        options['fractal'] = False
        options['ljung'] = False
        self.models = auto_model(self.wCoefficients, self.R, options, self.data[0])

        statusText += '<br/>Selected models:<br/>'
        for lvl, model in self.models.iteritems():
            statusText += str(lvl) + '. <b>' + model.enumname.replace('_', ' ') + '</b><br/>'

        # forecasting #
        frequency = 10
        aic = True
        options['hw_gamma'] = True
        options['hw_model'] = 'additive'
        options['hw_period'] = frequency
        options['ar_aic'] = aic
        options['ar_method'] = 'burg'
        options['arima_auto'] = True
        options['lsf_aic'] = aic
        options['ets_auto'] = aic
        options['ets_period'] = frequency
        options['sts_type'] = 'trend'
        options['append_fit'] = True

        self.multi_model_thread = MultiModelThread(self.models,
                                           self.wCoefficients,
                                           self.R,
                                           self.steps.value(),
                                           options,)
        self.multi_model_thread.done.connect(self.multiForecastFinished)
        self.multi_model_thread.start()

        statusText += '<br/>Forecasting...'

        self.status.setText(statusText)
        self.status.show()

    def multiForecastFinished(self, results):
        self.forecast = results
        self.gifLoading.stop()
        self.processing.hide()

        self.status.setText('<br/>'.join(str(self.status.text()).split('<br/>')[:-1]) +
                            '<br/>Forecast complete.')
        self.modelCheck.setChecked(True)

    def checkData(self):
        if self.data is None:
            pass
        else:
            try:
                self.loadCheck.setChecked(True)
            except Exception:
                pass

    def checkModel(self):
        if self.result is None:
            pass
        else:
            try:
                self.modelCheck.setChecked(True)
            except Exception:
                pass

    def initializePage(self, p_int):
        nop = lambda: None

        {0: nop,
         1: self.checkData,
         2: self.checkModel,
         3: nop,
        }[p_int]()

class WizardPageEx(QWizardPage):

    def __init__(self, field='check', parent=None):
        QWizardPage.__init__(self, parent)

        self.check = QCheckBox()
        self.check.setVisible(False)
        self.registerField(field + '*', self.check)
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

    def removeFromList(self, item):
        self.workingSet.remove(float(item.text()))
        self.list.takeItem(self.list.indexFromItem(item).row())

    def removeItems(self):
        for item in self.list.selectedItems():
            self.workingSet.remove(float(item.text()))
            self.list.takeItem(self.list.indexFromItem(item).row())

class CustomOption(QDialog):

     def __init__(self, parent=None):
        super(CustomOption, self).__init__(parent)

        self.options = {}

        self.enable = QCheckBox('Enable custom settings')
        self.lblFamily = QLabel("<font style='color: gray'>Family:</font>")
        self.lblWavelet = QLabel("<font style='color: gray'>Wavelet:</font>")
        self.lblSignal = QLabel("<font style='color: gray'>Extension:</font>")
        self.lblLvls = QLabel("<font style='color: gray'>Levels:</font>")
        self.waveletFamily = QComboBox()
        self.wavelet = QComboBox()
        self.signalEx = QComboBox()
        self.lvls = QSpinBox()
        self.lvls.setRange(2, 10)

        self.periodic = QCheckBox('Frequency')
        self.frequency = QSpinBox()
        self.frequency.setMinimum(2)
        self.frequency.hide()

        self.apply = QPushButton('Apply')
        self.cancel = QPushButton('Cancel')

        self.layout = QGridLayout()
        self.layout.addWidget(self.enable, 0, 0, 1, 2)
        self.layout.addWidget(self.lblFamily, 1, 0)
        self.layout.addWidget(self.waveletFamily, 1, 1)
        self.layout.addWidget(self.lblWavelet, 2, 0)
        self.layout.addWidget(self.wavelet, 2, 1)
        self.layout.addWidget(self.lblSignal, 3, 0)
        self.layout.addWidget(self.signalEx, 3, 1)
        self.layout.addWidget(self.lblLvls, 4, 0)
        self.layout.addWidget(self.lvls, 4, 1)
        self.layout.addWidget(self.periodic, 5, 0)
        self.layout.addWidget(self.frequency, 5, 1)
        self.layout.addWidget(self.apply, 6, 0)
        self.layout.addWidget(self.cancel, 6, 1)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        self.initComponents()
        self.initActions()

        self.updateWavelet()

     def initComponents(self):
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.waveletFamily.addItems(pywt.families())
        self.signalEx.addItems(pywt.MODES.modes)
        self.periodic.clicked.connect(self.showFrequency)
        self.options['enable'] = False

     def initActions(self):
        self.apply.clicked.connect(self.saveOptions)
        self.cancel.clicked.connect(self.close)
        self.waveletFamily.currentIndexChanged.connect(self.updateWavelet)
        self.enable.clicked.connect(self.enableDisable)

     def saveOptions(self):
        self.options['enable'] = self.enable.isChecked()
#        self.options['family'] = self.waveletFamily.currentIndex()
        self.options['wavelet'] = unicode(self.wavelet.currentText())
        self.options['signal'] = unicode(self.signalEx.currentText())
        self.options['lvls'] = self.lvls.value()
        if self.periodic.isChecked():
            self.options['frequency'] = self.frequency.value()
            
        self.close()

     def updateWavelet(self):
         self.wavelet.clear()
         self.wavelet.addItems(pywt.wavelist(self.waveletFamily.currentText()))

     def showFrequency(self):
         if self.periodic.isChecked():
             self.frequency.show()
         else:
             self.frequency.hide()

     def enableDisable(self):
         if self.enable.isChecked():
            self.waveletFamily.setEnabled(True)
            self.wavelet.setEnabled(True)
            self.lvls.setEnabled(True)
            self.signalEx.setEnabled(True)
            self.periodic.setEnabled(True)
            self.frequency.setEnabled(True)
         else:
            self.waveletFamily.setEnabled(False)
            self.wavelet.setEnabled(False)
            self.lvls.setEnabled(False)
            self.signalEx.setEnabled(False)
            self.periodic.setEnabled(False)
            self.frequency.setEnabled(False)

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