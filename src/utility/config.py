# -*- coding=utf-8 -*-
__author__ = 'Yadavito'

# own #
from utility.const import __name__, _company,\
                        CONFIG_DICT, RES, FONTS, FONTS_DICT
from utility.log import log
from utility.tools import reverseSearch

# external #
from PyQt4.QtCore import QSettings
from PyQt4.QtGui import QFontDatabase

class Config:
    def __init__(self):
        try:
            self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, _company, __name__)
            self.loadCustomFonts()
        except Exception, e:
            log.exception(e)
    def updateConfig(self, **kwargs):
        for section, options in CONFIG_DICT.iteritems():
            for option in options:
                if option in kwargs:
                    self.settings.setValue(section + option, kwargs[option])

    def loadConfig(self):
        config = {}
        for section, options in CONFIG_DICT.iteritems():
            for option in options:
                config[option] = self.settings.value(section + option)
        # arrange by alphabet
        params = []
        for option in sorted(config):
            params.append(config[option])
        return params

    def getParams(self, **kwargs):
        found = {}
        for option in kwargs:
            if [l for l in CONFIG_DICT.values() if option in l]:
                section = reverseSearch(CONFIG_DICT, option)
                if section:
                    found[option] = self.settings.value(section[0] + option)
        return found

    def loadCustomFonts(self):
        for font in FONTS_DICT.values():
            # 0 ~ font name, 1 ~ extension
            QFontDatabase.addApplicationFont(RES + FONTS + font[0] + '.' + font[1])
