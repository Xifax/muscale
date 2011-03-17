# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''

class DataParser():
    
    @staticmethod
    def getTimeSeriesFromTextData(data, template=' '):
        series = []
        parseErrors = 0

        parsed = data.split(template)
        
        parsed = [el for el in parsed if el != template]
        
        for element in parsed:
            if element != '':
                try:
                    series.append(float(element.strip()))
                except:
                    parseErrors = parseErrors + 1
                    
        return (series, parseErrors)