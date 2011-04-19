# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''

#--------- global ---------#
__name__    = 'muScale'
__version__ = '0.0.1'

#----------- id -----------#
_company = 'nonbyte'
_product = __name__.lower()
_subproduct = _product
_version = __version__.replace('.', '')
_separator = '.'

#------- main window ------#
WIDTH = 640
HEIGHT = 570

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
ABOUT = 'about.png'
QUIT = 'quit.png'

ICO_SIZE = 32
#---------- styles ---------#
STYLE = 'plastique'
SPLASH = 'mu_logo.png'

#--------- timers ----------#
TIP_VISIBLE = 4000 #ms
STATUS_CHECK_DELAY = 1000
TRAY_VISIBLE_DELAY = 10000
TRAY_ICON_DELAY = 2000
LOAD_PAUSE = 3000

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
с последующим обратным вейвлет-преобразованием и формированием конечного прогноза.'}
                }[index]
    except KeyError:
        return {'title' : '...', 'info' : '...'}

infoTipsDict = { 0 : { 'tip' : u'To begin time series modelling, you should first load some data.', 'seen' : False },
                 1 : { 'tip' : u'Perform time series decomposition using wavelet transformation', 'seen' : False },
                 2 : { 'tip' : u'Choose model depending on level configuration', 'seen' : False },
                 3 : { 'tip' : u'Simulate forecast on multiple levels', 'seen' : False },
                }

def infoTips(index):
    try:
        if not infoTipsDict[index]['seen']:
            infoTipsDict[index]['seen'] = True
            return infoTipsDict[index]['tip']
    except KeyError:
        return None
