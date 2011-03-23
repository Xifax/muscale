# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''
from utils.log import log

class DataParser():
    
    @staticmethod
    def getTimeSeriesFromTextData(data, template=' '):
        series = []
        parseErrors = 0

        parsed = data.split(template)
        
        parsed = [el for el in parsed if el != template]
        
        for element in parsed:
            if element != '':
                #===============================================================
                # try:
                #    series.append(float(element.strip()))
                # except:
                #    parseErrors = parseErrors + 1
                #    log.debug('skipped value')
                #===============================================================
                value = element.toDouble()      #NB: pyqt uses QString
                if value[1]:
                    series.append(value[0])
                else:
                    parseErrors = parseErrors + 1
                    log.debug('skipped value')
                    
        return (series, parseErrors)