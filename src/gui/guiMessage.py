# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# external #
from PyQt4.QtCore import Qt, QRect, QSize, QTimer, QObject, QEvent
from PyQt4.QtGui import QFrame, QLabel, QVBoxLayout, QApplication

# own #
from utility.tools import RepeatTimer
from utility.const import infoTips, TIP_VISIBLE, STATUS_CHECK_DELAY, M_INTERVAL, BOTTOM_SPACE

class MessageFilter(QObject):
    """Status message mouse click filter"""
    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverEnter:
            object.countdownTimer.stop()
#            object.info.setStyleSheet('QLabel { border: none; color: lightsteelblue; }')
            object.setWindowOpacity(0.8)
        if event.type() == QEvent.HoverLeave:
            object.countdownTimer.start(TIP_VISIBLE + STATUS_CHECK_DELAY)
#            object.info.setStyleSheet('QLabel { border: none; color: white; }')
            object.setWindowOpacity(1.0)
        if event.type() == QEvent.MouseButtonPress:
            object.countdownTimer.stop()
            object.hide()

        return False

class SystemMessage(QFrame):
    def __init__(self, parent=None):
        super(SystemMessage, self).__init__(parent)

        self.info = QLabel(u'')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.info)
        self.setLayout(self.layout)

        self.countdownTimer = QTimer()

        self.setAttribute(Qt.WA_Hover, True)
        self.filter = MessageFilter()
        self.installEventFilter(self.filter)

        self.initComponents()
        self.initComposition()

        self.isShown = False

    def initComposition(self):
        self.setWindowFlags(Qt.ToolTip)
        self.updateStyle()

    def initComponents(self):
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setWordWrap(True)

        self.countdownTimer.setSingleShot(True)
        self.countdownTimer.timeout.connect(self.fadeStatus)

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

            self.adjustSize()
            self.updatePosition()
            self.fadeStatus()
            self.countdownTimer.start(TIP_VISIBLE)

    def updatePosition(self):
        desktop = QApplication.desktop()
        if self.parent().y() + self.parent().height() + M_INTERVAL > desktop.height() - BOTTOM_SPACE:
            self.move(self.parent().x() + (self.parent().width() - self.width())/2, self.parent().y() + self.parent().height() - BOTTOM_SPACE)
        else:
            self.move(self.parent().x() + (self.parent().width() - self.width())/2, self.parent().y() + self.parent().height() + M_INTERVAL)

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
