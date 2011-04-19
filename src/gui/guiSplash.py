# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from PyQt4.QtGui import QApplication, QPixmap, QSplashScreen, QGraphicsDropShadowEffect
from PyQt4.QtCore import Qt

# own #
from utils.const import RES, ICONS, LOGO, STYLE, SPLASH, __version__, __name__

def showSplash(app):

    # splash pixmap
    logo = QPixmap(RES + ICONS + SPLASH)
    splash = QSplashScreen(logo, Qt.WindowStaysOnTopHint)
#    splash.setWindowFlags(Qt.WindowStaysOnTopHint)

    # shadow effect
    #TODO: make shadow effect work!

#    shadow = QGraphicsDropShadowEffect()
    #shadow.setOffset(QPointF(3,3))
    #shadow.setBlurRadius(8)
#    splash.setGraphicsEffect(shadow)

    # alpha mask
    splash.show()
    splash.setMask(logo.mask())
#    splash.setGraphicsEffect(shadow)

    # status message
    labelAlignment = Qt.Alignment(Qt.AlignBottom | Qt.AlignCenter | Qt.AlignAbsolute)
    newline = '<br/>'
    font = "<font style='font-family: Courier New; font-size: 10pt; color: white;'>"
    info = newline * 10 + font + 'Loading...<br/>' + __name__ + ' ' + __version__ + '</font'
    splash.showMessage(info, labelAlignment)        #NB: html tags completely break alignment and color settings

    # checking for mouse click
    app.processEvents()

    return splash