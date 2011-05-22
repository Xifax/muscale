# -*- coding: utf-8 -*-
'''
Created on Mar 9, 2011

@author: Yadavito
'''

# internal #
import string

# own #
from utility.log import log
from utility.const import DATA_LOW_LIMIT, DATA_HIGH_LIMIT

# external #
from PyQt4.QtCore import QString

class DataParser():

    text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
    _null_trans = string.maketrans("", "")

    @staticmethod
    def istext(s):
        if "\0" in s:
            return False

        # empty file
        if not s:
            return True

        t = s.translate(DataParser._null_trans, DataParser.text_characters)

        if float(len(t))/len(s) > 0.30:
            return False
        return True

    @staticmethod
    def istextfile(filename, blocksize = 512):
        return DataParser.istext(open(filename).read(blocksize))

    @staticmethod
    def getTimeSeriesFromTextData(data, template=' '):
        series = []
        parseErrors = 0

        parsed = DataParser.readDataByTemplate(data, template)
        if len(parsed) < DATA_LOW_LIMIT:
            parsed = DataParser.readDataByTemplate(data, '\n')

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
                 except Exception, e:
                    parseErrors += 1
                    log.exception(e)

        if len(series) > DATA_HIGH_LIMIT:
            series = series[:DATA_HIGH_LIMIT]
                    
        return series, parseErrors

    @staticmethod
    def readDataByTemplate(data, template):
        parsed = data.split(template)
        return [el for el in parsed if el != template]