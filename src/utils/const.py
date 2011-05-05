# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''
# external
from flufl.enum import make_enum

#--------- global ---------#
__name__    = 'muScale'
__version__ = '0.0.3'

#----------- id -----------#
_company = 'nonbyte'
_product = __name__.lower()
_subproduct = _product
_version = __version__.replace('.', '')
_separator = '.'

#------- main window ------#
WIDTH = 640
HEIGHT = 600

#------ tools dialog ------#
T_WIDTH = 400
T_HEIGHT = HEIGHT

#------ info dialog -------#
I_WIDTH = 200
I_HEIGHT = HEIGHT/2

#------ graphs/plots ------#

P_PREVIEW_HEIGHT = 240

#---------- paths ---------#
RES = '../res/'
ICONS = 'icons/'
WV = 'wv/'

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
RESET = 'delete.png'
# ~*~ #
LOAD = 'load.png'
DECOM = 'cog.png'
LAYERS = 'layers.png'
ANALYSIS = 'forecast.png'
FIN = 'fin.png'

ICO_SIZE = 32
#---------- styles ---------#
STYLE = 'plastique'
SPLASH = 'mu_logo.png'

#---------- parser ---------#
LR_PRNTH_MAPPINGS = { "(":")", "[":"]", "{":"}" }

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
def infoContens(index):
    try:
        return { 
                    0  : { 'title' : u'Исходные данные', 'info' : u'Ввод одномерного временного ряда из файла или вручную: \
в дальнейшем желательно реализовать шаблон считывания и возможность одновременной работы с несколькими временными рядами.'},
                    1  : { 'title' : u'Декомпозиция', 'info' : u'Стационарное/дискретное вейвлет-разложение на определённое число составляющих: \
дискретное разложение предполагает существенную редукцию исходных данных; стационарное обеспечивает временную инвариантность получаемых компонент.'},
                    2  : { 'title' : u'Формирование модели', 'info' : u'Выбор прогностических моделей в зависимости от уровня представления. \
Предполагается использование гармонической регрессии для компонент с ярко выраженной периодичностью, модели Хольта-Винтерса — для выявления общего тренда.'},
                    3  : { 'title' : u'Настройка и симуляция', 'info' : u'Задание параметров результирующей модели и формирование прогноза для каждой из компонент \
с последующим обратным вейвлет-преобразованием и формированием конечного прогноза.'},
                    4  : { 'title' : u'Конечная модель и прогноз', 'info' : u'Композиция результирующего временного ряда на основе преобразованных уровней \
вейвлет-разложения.'}
                }[index]
    except KeyError:
        return {'title' : '...', 'info' : '...'}

infoTipsDict = { 0 : { 'tip' : u'To begin time series modelling, you should first load some data', 'seen' : False },
                 1 : { 'tip' : u'Perform time series decomposition using wavelet transformation', 'seen' : False },
                 2 : { 'tip' : u'Choose model depending on level configuration', 'seen' : False },
                 3 : { 'tip' : u'Simulate forecast on multiple levels', 'seen' : False },
                 4 : { 'tip' : u'Reconstruct time series based on processed multiscale levels', 'seen' : False },
                }

def infoTips(index):
    try:
        if not infoTipsDict[index]['seen']:
            infoTipsDict[index]['seen'] = True
            return infoTipsDict[index]['tip']
    except KeyError:
        return None

infoWavelets = { 'haar' : u'Haar (step function)',
                 'db' : u'Daubechies (compactly supported orthonormal)',
                 'sym' : u'Symlets (nearly symmetrical db)',
                 'coif' : u'Coiflets (symmetrical)', # <---
                 'bior' : u'Biorthogonal (linear phase property)',
                 'rbio' : u'Reverse biorthogonal',
                 'dmey' : u'Discrete approximation of Meyer wavelet (scaling in frequency domain)',
                 # mexican hat
                 # morlet
            }

#----------- WT ------------#
WT = make_enum('WT', 'StationaryWT DiscreteWT')

#--------- models ----------#

Models = make_enum('Models', 'Holt_Winters Harmonic_Regression Least_Squares_Fit ARIMA')

#-------- gui tabs ---------#
Tabs = make_enum('Tabs', 'Decomposition Model Simulation Results'); Tabs.Data = 0

#------ gui tooltips -------#
Tooltips = {# data input
            'load_from_file' : u'Load data series from text file',
            'load_manual' : u'Input data series manually',

            # decomposition
            'max_level' : u'Max level, depending on wavelet and initial data: ()',
            'swt' : u'Non-decimated (stationary) wavelet transform',
            'dwt' : u'Decimated wavelet transform'

}

#------ install url --------#
URL_PYQT = 'http://cran.r-project.org/bin/windows/base/R-2.13.0-win.exe'
URL_R = 'http://www.riverbankcomputing.co.uk/static/Downloads/PyQt4/PyQt-Py2.6-x86-gpl-4.8.3-1.exe'
URL_MATPLOTLIB = 'http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.0.1/matplotlib-1.0.1.win32-py2.6.exe/download'
URL_NUMPY = 'http://sourceforge.net/projects/numpy/files/NumPy/1.6.0rc1/numpy-1.6.0c1-win32-superpack-python2.6.exe/download'
URL_SCIPY = 'http://sourceforge.net/projects/scipy/files/scipy/0.9.0/scipy-0.9.0-win32-superpack-python2.6.exe/download'
URL_SETUPTOOLS = 'http://pypi.python.org/packages/2.6/s/setuptools/setuptools-0.6c11.win32-py2.6.exe'

#---- required packages ----#
easy_packages = ['pywt', 'flufl.enum', 'userconfig', 'simpledropbox']
downloadable_packages = {'PyQt4' : URL_PYQT, 'matplotlib' : URL_MATPLOTLIB,
                         'numpy' : URL_NUMPY, 'scipy' : URL_SCIPY}