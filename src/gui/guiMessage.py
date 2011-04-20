# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from PyQt4.QtCore import Qt, QRect, QSize, QTimer
from PyQt4.QtGui import *

# own #
from utils.tools import RepeatTimer
from utils.guiTweaks import roundCorners
from utils.const import infoTips, TIP_VISIBLE, STATUS_CHECK_DELAY

class SystemMessage(QFrame):
    def __init__(self, parent=None):
        super(SystemMessage, self).__init__(parent)

        self.info = QLabel(u'')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.info)
        self.setLayout(self.layout)

        self.initComponents()
        self.initComposition()

        self.isShown = False

    def initComposition(self):
#        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.setWindowFlags(Qt.ToolTip)
#        self.setStyleSheet('QFrame { background-color: black; border: 1px solid white; border-radius: 4px; } QLabel { border: none; color: white; }')
        self.updateStyle()

    def initComponents(self):
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setWordWrap(True)

    def updateStyle(self, error=False):
        if not error: self.setStyleSheet('QFrame { background-color: black; border: 1px solid white; border-radius: 4px; } QLabel { border: none; color: white; }')
        else: self.setStyleSheet('QFrame { background-color: red; border: 1px solid white; border-radius: 4px; } QLabel { border: none; color: white; }')

    def showInfo(self, message, error=False):
        if not self.isShown:
            self.info.setText('')
            self.updateStyle(error)
            if isinstance(message, int):
                tip = infoTips(message)
                if tip is not None:
                    self.info.setText(tip)
                    self.updateAndShow()
            else:
                self.info.setText(message)
                self.updateAndShow()

    def updateAndShow(self):
        if self.info.text() != '':
            self.show()
            self.setWindowOpacity(0)

            self.isShown = True
            QTimer.singleShot(TIP_VISIBLE + STATUS_CHECK_DELAY, self.updateStatus)

            self.updatePosition()
            self.fadeStatus()
            QTimer.singleShot(TIP_VISIBLE, self.fadeStatus)

    def updatePosition(self):
        self.move(self.parent().x() + (self.parent().width() - self.width())/2, self.parent().y() + self.parent().height() + self.height())

    def updateStatus(self):
        self.isShown = False

    def fadeStatus(self):
        if self.windowOpacity() == 1:
            self.animationTimer = RepeatTimer(0.025, self.fadeOut, 40)
            self.animationTimer.start()
        else:
            self.animationTimer = RepeatTimer(0.025, self.fadeIn, 40)
            self.animationTimer.start()

    def fadeIn(self):
        self.setWindowOpacity(self.windowOpacity() + 0.1)

    def fadeOut(self):
        self.setWindowOpacity(self.windowOpacity() - 0.1)
