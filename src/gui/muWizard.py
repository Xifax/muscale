# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from PyQt4.QtCore import Qt, QObject, QEvent, QThread, pyqtSignal, QByteArray
from PyQt4.QtGui import QWizard, QWizardPage, \
                        QLabel, QVBoxLayout, QPixmap, QPushButton, \
                        QLineEdit, QToolButton, QGridLayout, QFileDialog, \
                        QCheckBox, QDialog, QListWidget, QListWidgetItem, QAction, \
                        QAbstractItemView, QSpinBox, QMovie, QComboBox, QHBoxLayout
import pywt
from xlwt import Workbook, Alignment, XFStyle, Font, Borders

# own #
from utility.const import RES, ICONS, LOGO, DATA_LOW_LIMIT, FONTS_DICT, \
                            MIN_FORECAST, MAX_FORECAST, PROGRESS,\
                            ARROW_DOWN, GRADIENT, TEMP
from stats.parser import DataParser
from stats.wavelets import calculate_suitable_lvl, update_dwt, select_wavelet
from stats.models import auto_model, calculateForecast
from gui.graphWidget import MplWidget

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

class ResFilter(QObject):
    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverEnter:
            object.setStyleSheet('QLabel { color: black; }')
        if event.type() == QEvent.HoverLeave:
            object.setStyleSheet('QLabel { color: gray; }')
        if event.type() == QEvent.MouseButtonPress:
            if str(object.text()).split('>')[1].split('<')[0] == 'Export':
                object.parent().parent().parent().parent().exportToXls()
            elif str(object.text()).split('>')[1].split('<')[0] == 'Plot':
                object.parent().parent().parent().parent().togglePlot()
            elif str(object.text()).split('>')[1].split('<')[0] == 'Data':
                object.parent().parent().parent().parent().toggleData()

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

        self.setStyleSheet('QWizard {' + GRADIENT +'}\
                        QPushButton {\
                            color: #333;\
                            border: 1px solid #555;\
                            border-radius: 11px;\
                            padding: 2px;\
                            background: qradialgradient(cx: 0.3, cy: -0.4,\
                            fx: 0.3, fy: -0.4,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #888);\
                            min-width: 80px;}\
                        QPushButton:hover {\
                            color: #fff;\
                            background: qradialgradient(cx: 0.3, cy: -0.4,\
                            fx: 0.3, fy: -0.4,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #bbb);}\
                        QPushButton:pressed {\
                            color: #800;\
                            background: qradialgradient(cx: 0.4, cy: -0.1,\
                            fx: 0.4, fy: -0.1,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}\
                        QPushButton:checked {\
                            background: qradialgradient(cx: 0.4, cy: -0.1,\
                            fx: 0.4, fy: -0.1,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}\
                        QComboBox {\
                            color: #333;\
                            border: 1px solid #555;\
                            border-radius: 11px;\
                            padding: 1px 18px 1px 3px;\
                            background: qradialgradient(cx: 0.3, cy: -0.4,\
                            fx: 0.3, fy: -0.4,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #888);\
                            min-width: 20px;}\
                        QComboBox:hover {\
                            color: #fff;\
                            background: qradialgradient(cx: 0.3, cy: -0.4,\
                            fx: 0.3, fy: -0.4,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #bbb);}\
                        QComboBox::down-arrow {\
                             image: url(' + RES + ICONS + ARROW_DOWN + ');}\
                        QComboBox::down-arrow:on {\
                             top: 1px;\
                             left: 1px;}\
                        QComboBox::drop-down {\
                             subcontrol-origin: padding;\
                             subcontrol-position: top right;\
                             width: 15px;\
                             border-left-width: 1px;\
                             border-left-color: darkgray;\
                             border-left-style: solid;\
                             border-top-right-radius: 3px;\
                             border-bottom-right-radius: 3px;}\
                         QToolButton {\
                            color: #333;\
                            border: 1px solid #555;\
                            border-radius: 11px;\
                            padding: 2px;\
                            background: qradialgradient(cx: 0.3, cy: -0.4,\
                            fx: 0.3, fy: -0.4,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #888);\
                            min-width: 20px;}\
                        QToolButton:hover {\
                            color: #fff;\
                            background: qradialgradient(cx: 0.3, cy: -0.4,\
                            fx: 0.3, fy: -0.4,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #bbb);}\
                        QToolButton:pressed {\
                            background: qradialgradient(cx: 0.4, cy: -0.1,\
                            fx: 0.4, fy: -0.1,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}\
                        QToolButton:checked {\
                            background: qradialgradient(cx: 0.4, cy: -0.1,\
                            fx: 0.4, fy: -0.1,\
                            radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}')

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
        models.setTitle('Forecast')

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
        results.setTitle('Results')

        self.graph = QLabel("<font style='font-size: 16px;'>Plot</font>")
        self.export = QLabel("<font style='font-size: 16px;'>Export</font>")
        self.showData = QLabel("<font style='font-size: 16px;'>Data</font>")
        
        self.plotResult = MplWidget(None)
        self.plotResult.canvas.fig.set_facecolor('white')
        self.resData = QLabel('')
        self.resData.setAlignment(Qt.AlignCenter)
        self.resData.setWordWrap(True)
        self.resData.hide()

        self.resFilter = ResFilter()

        self.resLayout = QVBoxLayout()
        self.resLayout.addWidget(self.export)
        self.resLayout.addWidget(self.graph)
        self.resLayout.addWidget(self.showData)
        self.resLayout.addWidget(self.plotResult)
        self.resLayout.addWidget(self.resData)

        self.plotResult.hide()

        for index in range(0, self.resLayout.count()):
            try:
                self.resLayout.itemAt(index).widget().setAlignment(Qt.AlignCenter)
                self.resLayout.itemAt(index).widget().setStyleSheet('QLabel { color: gray; }')
                self.resLayout.itemAt(index).widget().setAttribute(Qt.WA_Hover)
                self.resLayout.itemAt(index).widget().installEventFilter(self.resFilter)
            except Exception:
                pass

        self.resLayout.setAlignment(Qt.AlignCenter)
        self.resLayout.setSpacing(60)

        results.setLayout(self.resLayout)

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
                    self.resultLbl.setText("<font style='color: gray'>Not enough values to form data series.</font>")
                    self.resultLbl.show()
            else:
                self.resultLbl.setText("<font style='color: gray'>Specified file is binary file!</font>")
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
            selected = select_wavelet(self.data[0], self.R)
            index = max(selected)
            self.wavelet = pywt.Wavelet(selected[index][1])

            wLevel = calculate_suitable_lvl(self.data[0],
                                         self.wavelet, self.R, swt=False)
            self.wInitialCoefficients = pywt.wavedec(self.data[0], self.wavelet,
                                                     level=wLevel, mode=self.signalEx)
            self.wCoefficients = self.wInitialCoefficients

        statusText += 'Wavelet: <b>' + self.wavelet.family_name + \
                      '</b> (' + self.wavelet.name + ', ' + self.wavelet.symmetry + ', orthognal: ' + \
                      str(self.wavelet.orthogonal) + ')<br/>'

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
        try:
            frequency = self.customOpt.options['frequency']
        except Exception:
            frequency = 8
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

    #---- results -----#
    def togglePlot(self):
        if self.plotResult.isVisible():
            self.plotResult.hide()
            self.export.show()
            self.showData.show()
            self.resLayout.setSpacing(60)
        else:
            self.updateGraph()
            self.plotResult.show()
            self.export.hide()
            self.showData.hide()
            self.resLayout.setSpacing(5)

    def toggleData(self):
        if self.resData.isVisible():
            self.export.show()
            self.graph.show()
            self.showData.show()
            self.resData.hide()
            self.resLayout.setSpacing(60)
        else:
            self.plotResult.hide()
            self.graph.hide()
            self.export.hide()
            self.showData.show()
            self.resData.show()
            self.resLayout.setSpacing(5)

            res = self.inverseWT()
            max = len(self.data[0]) - 1
            resText = '<table border="0" align="center" style="border-style: groove;">'
            resText += '<tr><td align="center"><i>Initial</i></td><td align="center"><i>Forecast</i></td></tr>'
            resText += '<tr><td align="center">...</td><td></td></tr>'
            table = zip(self.data[0][max-10:max], res[max-10:max])
            for i, j in table:
                resText += '<tr>'
                resText += '<td align="center">' + str(i) + '</td>'
                resText += '<td align="center">' + str(j) + '</td>'
                resText += '</tr>'

            for e in res[max+1:max+10]:
                resText += '<tr>'
                resText += '<td align="center"></td>'
                resText += '<td align="center">' + str(e) + '</td>'
                resText += '</tr>'

            resText += '<tr><td align="center"></td><td align="center">...</td></tr>'
            resText += '</table>'

            self.resData.setText(resText)

    def inverseWT(self):
        return pywt.waverec(update_dwt([e [1] for e in self.forecast], self.wavelet),
                                            self.wavelet, mode=self.signalEx)

    def updateGraph(self):
        self.plotResult.updatePlot(self.inverseWT(), label='Simulation', color='r')
        self.plotResult.updatePlot(self.data[0], label='Time series', color='b')

    def exportToXls(self):
        # opening file dialog
        fileName = QFileDialog.getSaveFileName(self,
            'Save as', RES, 'Microsoft Excel Spreadsheet (*.xls)')

        if fileName.count() > 0:
            try:
                COLUMN_WIDTH = 3000

                alignment = Alignment()
                alignment.horizontal = Alignment.HORZ_CENTER
                alignment.vertical = Alignment.VERT_CENTER

                borders = Borders()
                borders.left = Borders.THIN
                borders.right = Borders.THIN
                borders.top = Borders.THIN
                borders.bottom = Borders.THIN

                style = XFStyle()
                style.alignment = alignment
                style.borders = borders

                font = Font()
                font.bold = True
                headerStyle = XFStyle()
                headerStyle.font = font

                separate = Borders()
                separate.left = Borders.THIN
                separate.right = Borders.DOUBLE
                separate.top = Borders.THIN
                separate.bottom = Borders.THIN
                separateStyle = XFStyle()
                separateStyle.borders = separate

                book = Workbook(encoding='utf-8')

                # modelling data
                dec_sheet = book.add_sheet('Data decomposition')

                # decomposition data
                # initial data
                column = 0
                row = 0
                dec_sheet.write(row, column, 'Time series', headerStyle)
                dec_sheet.col(column).width = COLUMN_WIDTH
                row += 1
                for item in self.data[0]:
                    dec_sheet.write(row, column, item, separateStyle)
                    row += 1

                # decomposition
                for lvl in self.wCoefficients:
                    row = 0
                    column += 1
                    dec_sheet.write(row, column, 'Level' + str(column - 1), headerStyle)
                    dec_sheet.col(column).width = COLUMN_WIDTH
                    row += 1
                    for item in lvl:
                        dec_sheet.write(row, column, item, style)
                        row += 1

                # decomposition graphs
                pass

                levels_sheet = book.add_sheet('Multiscale forecast')

                # levels data
                column = 0
                for lvl in self.forecast:
                    row = 0
                    levels_sheet.write(row, column, 'Level' + str(column), headerStyle)
                    levels_sheet.col(column).width = COLUMN_WIDTH
                    row += 1
                    for item in lvl[1]:
                        levels_sheet.write(row, column, float(item), style)
                        row += 1
                    column += 1

                result_sheet = book.add_sheet('Results')

                # initial
                column = 0
                row = 0
                result_sheet.write(row, column, 'Initial data', headerStyle)
                result_sheet.col(column).width = COLUMN_WIDTH
                row += 1
                for item in self.data[0]:
                    result_sheet.write(row, column, item, separateStyle)
                    row += 1

                # forecast
                row = 0
                column += 1
                result_sheet.write(row, column, 'Forecast', headerStyle)
                result_sheet.col(column).width = COLUMN_WIDTH
                row += 1
                for item in self.inverseWT():
                    result_sheet.write(row, column, item, style)
                    row += 1

                row = 0
                column = 2
                self.updateGraph()
                self.plotResult.saveFigure('forecast', format='bmp')

                result_sheet.insert_bitmap(RES + TEMP + 'forecast.bmp', row, column)

                # saving xls
                try:
                    book.save(unicode(fileName))
                except Exception:
                    pass

            except Exception, e:
                pass

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

        self.initComponents()
        self.initActions()

    def initComponents(self):
        self.setWindowFlags(Qt.Tool)
        self.setWindowTitle("Time series")

        self.setStyleSheet('''QPushButton {
                                color: #333;
                                border: 1px solid #555;
                                border-radius: 11px;
                                padding: 2px;
                                background: qradialgradient(cx: 0.3, cy: -0.4,
                                fx: 0.3, fy: -0.4,
                                radius: 1.35, stop: 0 #fff, stop: 1 #888);
                                min-width: 80px;
                            }
                            QPushButton:hover {
                                color: #fff;
                                background: qradialgradient(cx: 0.3, cy: -0.4,
                                fx: 0.3, fy: -0.4,
                                radius: 1.35, stop: 0 #fff, stop: 1 #bbb);}
                            QPushButton:pressed {
                                background: qradialgradient(cx: 0.4, cy: -0.1,
                                fx: 0.4, fy: -0.1,
                                radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}
                            QPushButton:checked {
                                background: qradialgradient(cx: 0.4, cy: -0.1,
                                fx: 0.4, fy: -0.1,
                                radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}
                            QListView::focus {
                                border: 2px solid black;
                                border-radius: 6px;
                            }
                            QScrollBar:vertical {
                              width: 20px;
                              border: 1px solid grey;
                              border-radius: 6px;
                              background-color: transparent;
                              margin: 28px 0 28px 0;
                            }
                            QScrollBar::add-line:vertical {
                              background: transparent;
                              height: 32px;
                              subcontrol-position: bottom;
                              subcontrol-origin: margin;
                            }
                            QScrollBar::sub-line:vertical {
                              background: transparent;
                              height: 32px;
                              subcontrol-position: top;
                              subcontrol-origin: margin;
                            }
                            QScrollBar::up-arrow:vertical {
                              width: 20px;
                              height: 32px;
                              background: transparent;
                              image: url(../res/icons/arrow_up.png);
                            }
                            QScrollBar::up-arrow:hover {
                              bottom: 2px;
                            }
                            QScrollBar::down-arrow:vertical {
                              width: 20px;
                              height: 32px;
                              background: transparent;
                              image: url(../res/icons/arrow_down.png);
                            }
                            QScrollBar::down-arrow:hover {
                              top: 2px;
                            }
                            QScrollBar::handle:vertical {
                                border-radius: 6px;
                                background: url(../res/icons/handle.png) 0% center no-repeat;
                                background-color: white;
                                min-height: 32px;
                            }
                            QScrollBar::handle:hover {
                                background: url(../res/icons/handle_hover.png) 0% center no-repeat;
                                background-color: white;
                                border: 1px solid gray;
                            }''')

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
        self.lblFamily = QLabel('Family:')
        self.lblWavelet = QLabel('Wavelet:')
        self.lblSignal = QLabel('Extension:')
        self.lblLvls = QLabel('Levels:')
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
        self.enableDisable()

     def initComponents(self):
        self.setWindowFlags(Qt.Tool)
        self.setWindowTitle('Custom settings')
        self.waveletFamily.addItems(pywt.families())
        self.signalEx.addItems(pywt.MODES.modes)
        self.periodic.clicked.connect(self.showFrequency)
        self.options['enable'] = False
        
        self.setStyleSheet('QPushButton {\
                    color: #333;\
                    border: 1px solid #555;\
                    border-radius: 11px;\
                    padding: 2px;\
                    background: qradialgradient(cx: 0.3, cy: -0.4,\
                    fx: 0.3, fy: -0.4,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #888);\
                    min-width: 80px;}\
                QPushButton:hover {\
                    color: #fff;\
                    background: qradialgradient(cx: 0.3, cy: -0.4,\
                    fx: 0.3, fy: -0.4,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #bbb);}\
                QPushButton:pressed {\
                    background: qradialgradient(cx: 0.4, cy: -0.1,\
                    fx: 0.4, fy: -0.1,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}\
                QPushButton:checked {\
                    background: qradialgradient(cx: 0.4, cy: -0.1,\
                    fx: 0.4, fy: -0.1,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}\
                QComboBox {\
                    color: #333;\
                    border: 1px solid #555;\
                    border-radius: 11px;\
                    padding: 1px 18px 1px 3px;\
                    background: qradialgradient(cx: 0.3, cy: -0.4,\
                    fx: 0.3, fy: -0.4,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #888);\
                    min-width: 20px;}\
                QComboBox:hover {\
                    color: #fff;\
                    background: qradialgradient(cx: 0.3, cy: -0.4,\
                    fx: 0.3, fy: -0.4,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #bbb);}\
                QComboBox::down-arrow {\
                     image: url(' + RES + ICONS + ARROW_DOWN + ');}\
                QComboBox::down-arrow:on {\
                     top: 1px;\
                     left: 1px;}\
                QComboBox::drop-down {\
                     subcontrol-origin: padding;\
                     subcontrol-position: top right;\
                     width: 15px;\
                     border-left-width: 1px;\
                     border-left-color: darkgray;\
                     border-left-style: solid;\
                     border-top-right-radius: 3px;\
                     border-bottom-right-radius: 3px;}\
                QToolButton {\
                    color: #333;\
                    border: 1px solid #555;\
                    border-radius: 11px;\
                    padding: 2px;\
                    background: qradialgradient(cx: 0.3, cy: -0.4,\
                    fx: 0.3, fy: -0.4,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #888);\
                    min-width: 20px;}\
                QToolButton:hover {\
                    color: #fff;\
                    background: qradialgradient(cx: 0.3, cy: -0.4,\
                    fx: 0.3, fy: -0.4,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #bbb);}\
                QToolButton:pressed {\
                    background: qradialgradient(cx: 0.4, cy: -0.1,\
                    fx: 0.4, fy: -0.1,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}\
                QToolButton:checked {\
                    background: qradialgradient(cx: 0.4, cy: -0.1,\
                    fx: 0.4, fy: -0.1,\
                    radius: 1.35, stop: 0 #fff, stop: 1 #ddd);}')

     def initActions(self):
        self.apply.clicked.connect(self.saveOptions)
        self.cancel.clicked.connect(self.close)
        self.waveletFamily.currentIndexChanged.connect(self.updateWavelet)
        self.enable.clicked.connect(self.enableDisable)

     def saveOptions(self):
        self.options['enable'] = self.enable.isChecked()
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
         else:
            self.waveletFamily.setEnabled(False)
            self.wavelet.setEnabled(False)
            self.lvls.setEnabled(False)
            self.signalEx.setEnabled(False)

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