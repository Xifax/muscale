# -*- coding: utf-8 -*-
'''
Created on Mar 23, 2011

@author: Yadavito
'''
# external #
from PyQt4.QtCore import QObject, QEvent, Qt, QPoint
from PyQt4.QtGui import QFrame, QVBoxLayout,\
                        QLabel, QPushButton, QAction, QFont

# own #
from utility.const import I_WIDTH, infoContens, FONTS_DICT
from utility.guiTweaks import roundCorners

class InfoFilter(QObject):
    """Status message mouse click filter"""
    def eventFilter(self, object, event):
        if event.type() == QEvent.HoverEnter:
            object.dockButtonUp.setVisible(True)
            object.dockButtonDown.setVisible(True)
            object.adjustSize()
            object.updateCornersMask()
        if event.type() == QEvent.HoverLeave:
            object.dockButtonUp.setHidden(True)
            object.dockButtonDown.setHidden(True)
            object.adjustSize()

        return False

class InfoFrame(QFrame):
    def __init__(self, parent=None):
        super(InfoFrame, self).__init__(parent)

        self.mainLayout = QVBoxLayout()
        
        self.titleLabel = QLabel(u'')
        self.infoLabel = QLabel(u'')

        self.dockButtonUp = QPushButton()
        self.dockButtonDown = QPushButton()

        self.mainLayout.addWidget(self.dockButtonUp)
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.infoLabel)
        self.mainLayout.addWidget(self.dockButtonDown)
        self.setLayout(self.mainLayout)
        
        self.initComposition()
        self.initComponents()
        self.initActions()

        self.offset = QPoint()
        
    def initComposition(self):
        self.setWindowFlags(Qt.ToolTip)
        self.setStyleSheet('''QFrame { background-color: khaki;
                            border: 1px solid black;
                            border-radius: 4px; }
                            QLabel { border: none; }''')
        
        self.setMaximumWidth(I_WIDTH)
        
    def initComponents(self):
        self.titleLabel.setAlignment(Qt.AlignCenter)
#        self.infoLabel.setAlignment(Qt.AlignCenter)
        
        self.titleLabel.setWordWrap(True)
        self.infoLabel.setWordWrap(True)
        self.infoLabel.setTextFormat(Qt.RichText)
        
        self.dockButtonUp.setHidden(True)
        self.dockButtonUp.setCheckable(True)
        self.dockButtonUp.setMaximumHeight(8)
        self.dockButtonUp.setStyleSheet('QWidget { background-color: khaki; }')

        self.dockButtonDown.setHidden(True)
        self.dockButtonDown.setCheckable(True)
        self.dockButtonDown.setMaximumHeight(8)
        self.dockButtonDown.setStyleSheet('QWidget { background-color: khaki; }')

        self.filter = InfoFilter()
        self.setAttribute(Qt.WA_Hover, True)
        self.installEventFilter(self.filter)

        self.offset = QPoint()

        font = QFont(FONTS_DICT['info'][0], FONTS_DICT['info'][2])
        self.titleLabel.setFont(font)
        self.infoLabel.setFont(font)

    def initActions(self):
        self.dockButtonUp.clicked.connect(self.setTopPosition)
        self.dockButtonDown.clicked.connect(self.setBottomPosition)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.detach = QAction('Detatch', self)
        self.detach.setCheckable(True)
        self.addAction(self.detach)
        self.addAction(QAction('Hide', self, triggered=self.hideInfo))
        
    def updateContents(self, index):
        content = infoContens(index)
        self.titleLabel.setText('<b>' + content['title'] + '</b>')
        self.infoLabel.setText(content['info'])
        self.adjustSize()

    def setTopPosition(self):
        self.dockButtonDown.setChecked(False)
        self.jumpPositionUnchecked()

    def setBottomPosition(self):
        self.dockButtonUp.setChecked(False)
        self.jumpPositionUnchecked()

    def jumpPositionUnchecked(self):
        if self.detach.isChecked():
            self.detach.setChecked(False)
            self.parent().updateInfoPosition()
            self.detach.setChecked(True)
        else:
            self.parent().updateInfoPosition()
        
    def updateCornersMask(self):
        self.setMask(roundCorners(self.rect(), 5))

    def hideInfo(self):
        self.parent().toggleInfo.setChecked(False)
        self.hide()

    #------------ events -------------#
    def showEvent(self, event):
        self.adjustSize()

    def mousePressEvent(self, event):
        event.accept()
        self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        event.accept()
        self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        event.accept()
        self.offset = QPoint()
