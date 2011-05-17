# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''
# external
try:
    from flufl.enum import make_enum
except ImportError, e:
    print e

#--------- global ---------#
__name__    = 'muScale'
__version__ = '0.1.0'

#----------- id -----------#
_company = 'nonbyte'
_product = __name__.lower()
_subproduct = _product
_version = __version__.replace('.', '')
_separator = '.'

#------- main window ------#
WIDTH = 640
HEIGHT = 700

#------ tools dialog ------#
T_WIDTH = 400
T_HEIGHT = HEIGHT

#------ info dialog -------#
I_WIDTH = 200

#--------- message --------#
M_INTERVAL = 45
BOTTOM_SPACE = 100

#------ graphs/plots ------#

P_PREVIEW_HEIGHT = 240

#---------- paths ---------#
RES = '../res/'
ICONS = 'icons/'
WV = 'wv/'
TEMP = 'tmp/'
FONTS = 'fonts/'

#--------- icons ----------#
LOGO = 'chart_line.png'
FULL_SCREEN = 'full.png'
NORMAL_SIZE = 'normal.png'
TOOLS = 'chart_line_dots.png'
WIZARD = 'wizzard.png'
INFO = 'info.png'
NEXT = 'next.png'
PREV = 'prev.png'
FIRST = 'first.png'
LAST = 'last.png'
TEST = 'flag.png'
ABOUT = 'about.png'
QUIT = 'quit.png'
SHOW = 'show.png'
RESET = 'delete.png'
# ~*~ #
LOAD = 'load.png'
DECOM = 'cog.png'
LAYERS = 'layers.png'
ANALYSIS = 'forecast.png'
FIN = 'fin.png'
# ~*~ #
CONTROLS = 'ctrl.png'
GRAPH = 'graph.png'
CLEAR = 'clear.png'
COPY = 'copy.png'
ELEMENTS = 'elements.png'
CUT = 'cut.png'
SERIES = ['series0.png', 'series1.png', 'series2.png', 'series3.png']

# toolbar icons #
TOOLBAR_ICONS = ['home.png', 'back.png', 'forward.png', '',
                 'pan.png', 'zoom.png', '',
                 'sub.png', 'edit.png', 'save.png']
LEGEND = 'legend.png'

ICO_SIZE = 32
ICO_GRAPH = 16
#---------- styles ---------#
STYLE = 'plastique'
SPLASH = 'mu_logo.png'

#---------- parser ---------#
LR_PRNTH_MAPPINGS = { "(": ")", "[": "]", "{": "}"}

L_PRNTH = set(LR_PRNTH_MAPPINGS.iterkeys())
R_PRNTH = set(LR_PRNTH_MAPPINGS.itervalues())

#--------- timers ----------#
TIP_VISIBLE = 3000 #ms
STATUS_CHECK_DELAY = 1000
TRAY_VISIBLE_DELAY = 10000
TRAY_ICON_DELAY = 2000
LOAD_PAUSE = 3000
FLASH_LABEL = 2000
LABEL_VISIBLE = 3000

#--------- info ------------#

#NB: Alas, QLabel does not support advanced css (ul/ol use results in crooked formatting)
def infoContens(index):
    try:
        return {    #NB: newline at the end secures correct sizeHint with different fonts
                    0: {'title': u'Загрузка исходных данных',
                        'info': u'''<div align="center">Ввод одномерного временного ряда из файла или вручную:<br/><br/>
Допускается загрузка из любого формата — будет осуществленна попытка чтения текстовых данных;<br/><br/>
При ручном вводе необходимо разделять вводимые величины запятой, пробелом или переносом строки.</div><br/><br/>'''},
                    1: {'title': u'Декомпозиция временного ряда',
                        'info': u'''<div align="center">Стационарное/дискретное вейвлет-разложение на определённое число составляющих:
дискретное разложение предполагает существенную редукцию исходных данных; стационарное обеспечивает временную инвариантность получаемых компонент.</div><br/><br/>'''},
                    2: {'title': u'Формирование полимасштабной модели',
                        'info': u'''<div align="center">Выбор прогностических моделей в зависимости от уровня представления.
Предполагается использование гармонической регрессии для компонент с ярко выраженной периодичностью, модели Хольта-Винтерса — для выявления общего тренда.</div><br/><br/>'''},
                    3: {'title': u'Настройка моделей, симуляция и прогнозирование',
                        'info' : u'''<div align="center">Задание параметров результирующей модели и формирование прогноза для каждой из компонент
с последующим обратным вейвлет-преобразованием и формированием конечного прогноза.</div><br/><br/>'''},
                    4: {'title': u'Реконструкция',
                        'info': u'''<div align="center">Композиция результирующего временного ряда на основе преобразованных уровней
вейвлет-разложения.</div><br/><br/>'''}
                }[index]
    except KeyError:
        return {'title': '...', 'info': '...'}

infoTipsDict = { 0: {'tip': u'To begin time series modelling, you should first load some data', 'seen': False},
                 1: {'tip': u'Perform time series decomposition using wavelet transformation', 'seen': False},
                 2: {'tip': u'Choose model depending on level configuration', 'seen': False},
                 3: {'tip': u'Simulate forecast on multiple levels', 'seen': False },
                 4: {'tip': u'Reconstruct time series based on processed multiscale levels', 'seen': False},
                }

def infoTips(index):
    try:
        if not infoTipsDict[index]['seen']:
            infoTipsDict[index]['seen'] = True
            return infoTipsDict[index]['tip']
    except KeyError:
        return None

infoWavelets = {'haar': u'Haar (step function)',
                 'db': u'Daubechies (compactly supported orthonormal)',
                 'sym': u'Symlets (nearly symmetrical db)',
                 'coif': u'Coiflets (symmetrical)', # <---
                 'bior': u'Biorthogonal (linear phase property)',
                 'rbio': u'Reverse biorthogonal',
                 'dmey': u'Discrete approximation of Meyer wavelet (scaling in frequency domain)',
                 # mexican hat
                 # morlet
            }

#----------- WT ------------#
try:
    WT = make_enum('WT', 'StationaryWT DiscreteWT')

#--------- models ----------#

    Models = make_enum('Models', 'Holt_Winters Harmonic_Regression Least_Squares_Fit ARIMA \
                                GARCH ETS StructTS Cubic_Splines')

#-------- gui tabs ---------#
    Tabs = make_enum('Tabs', 'Decomposition Model Simulation Results')
    Tabs.Data = 0

except NameError, e:
    print e
    
#------ gui tooltips -------#
Tooltips = {# data input
            'load_from_file': u'Load data series from text file',
            'load_manual': u'Input data series manually',

            # decomposition
            'max_level': u'Max level, depending on wavelet and initial data: ()',
            'swt': u'Non-decimated (stationary) wavelet transform',
            'dwt': u'Decimated wavelet transform'
            #TODO: complete tooltips
}

#------ install url --------#
#TODO: find static url for PyQt4
URL_PYQT = 'http://www.riverbankcomputing.co.uk/static/Downloads/PyQt4/PyQt-Py2.6-x86-gpl-4.8.4-1.exe'
URL_R = 'http://cran.r-project.org/bin/windows/base/R-2.13.0-win.exe'
URL_MATPLOTLIB = 'http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.0.1/matplotlib-1.0.1.win32-py2.6.exe/download'
URL_NUMPY = 'http://sourceforge.net/projects/numpy/files/NumPy/1.6.0rc1/numpy-1.6.0c1-win32-superpack-python2.6.exe/download'
URL_SCIPY = 'http://sourceforge.net/projects/scipy/files/scipy/0.9.0/scipy-0.9.0-win32-superpack-python2.6.exe/download'
URL_SETUPTOOLS = 'http://pypi.python.org/packages/2.6/s/setuptools/setuptools-0.6c11.win32-py2.6.exe'

#---- required packages ----#
easy_packages = ['PyWavelets', 'flufl.enum', 'userconfig', 'simpledropbox', 'pep8']
downloadable_packages = {'PyQt4': URL_PYQT, 'matplotlib': URL_MATPLOTLIB,
                         'numpy': URL_NUMPY, 'scipy': URL_SCIPY}

#------------ R ------------#
R = 'r/'
R_PKG = RES + R + 'pkg_zip/'
R_PATH = RES + R + 'R/'
R_BIN = R_PATH + 'bin/R'
R_LIB = R_PATH + 'library/'
R_COMPONENTS = '"main, i386"'

r_packages = []

#----- here be options -----#
# sections
s_gui = 'gui/'
s_graph = 'graph/'
s_model = 'model/'

# values
auto_step = 'step'
shadows = 'shadows'
show_toolbar = 'toolbar'
plot_multiline = 'multiline'
basic_swt = 'basic'
lock_max = 'lock'
data_r = 'r'
style = 'style'
tray = 'tray'
trace = 'trace'
folder = 'folder'
table = 'table'
model = 'model'

# dictionary
CONFIG_DICT = {s_gui: [auto_step, shadows, style, tray, trace, folder, table],
               s_graph: [show_toolbar, plot_multiline],
               s_model: [data_r, basic_swt, lock_max, model],
            }

#---------- data -----------#
DATA_LOW_LIMIT = 10 # values count
DATA_HIGH_LIMIT = 1000
MAX_FORECAST = 500
MIN_FORECAST = 2
DEFAULT_STEPS = 20

#---- preview generation ---#
LINE_WITH = 0.9

#-------- typefaces --------#
# application (typeface, format, size)
#FONTS_DICT = {'main': ('Anonymous', 'ttf', 10),
FONTS_DICT = {'main': ('Consolas', 'ttf', 12),
              'info': ('Droid Sans', 'ttf', 9),
              'message': ('Consolas', 'ttf', 9),
              'log': ('Droid Serif', 'ttf', 9),
              'splash': ('GreyscaleBasic', 'ttf', 10),
              'table': ('Dekar', 'otf', 12)
            }
