# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''

# own #
from utils.log import log

# external #
from PyQt4.QtCore import QString

class DataParser():
    
    @staticmethod
    def getTimeSeriesFromTextData(data, template=' '):
        series = []
        parseErrors = 0

        parsed = data.split(template)
        
        parsed = [el for el in parsed if el != template]
        
        for element in parsed:
            if element != '':
                # QString (manual input)
                if isinstance(element, QString):
                    value = element.toDouble()
                    if value[1]:
                        series.append(value[0])
                    else:
                        parseErrors += 1
                        log.debug('skipped value')
                # str (from file)        
                elif isinstance(element, str):
                 try:
                    series.append(float(element.strip()))
                 except:
                    parseErrors += 1
                    log.debug('skipped value')
                    
        return (series, parseErrors)