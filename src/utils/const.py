# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''

#--------- global ---------#

__name__    = 'muScale'
__version__ = '0.0.1'


#------- main window ------#
WIDTH = 640
HEIGHT = 489

#------ tools dialog ------#
T_WIDTH = 400
T_HEIGHT = HEIGHT

#------ info dialog -------#
I_WIDTH = 200
I_HEIGHT = HEIGHT/2

#---------- paths ---------#
RES = '../res/'
ICONS = 'icons/'

#--------- icons ----------#
LOGO = 'chart_line.png'
FULL_SCREEN = 'full.png'
NORMAL_SIZE = 'normal.png'
TOOLS = 'chart_bar.png'
WIZARD = 'wizzard.png'
INFO = 'info.png'

#--------- info ------------#
def infoContens(index):
    try:
        return { 
                    0  : { 'title' : 'Data loading', 'info' : '...'},
                    1  : { 'title' : 'Wavelet decomposition', 'info' : '...'},
                    2  : { 'title' : 'Model construction', 'info' : '...'},
                    3  : { 'title' : 'Model simulation', 'info' : '...'}
                }[index]
    except KeyError:
        return {'title' : '...', 'info' : '...'}