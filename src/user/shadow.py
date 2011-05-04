# -*- coding=utf-8 -*-
__author__ = 'Yadavito'

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, QPointF

app = QApplication(sys.argv)

frame = QFrame()
frame.setWindowFlags(Qt.FramelessWindowHint)

frame.layout = QVBoxLayout()
frame.button = QPushButton('A button')
frame.layout.addWidget(frame.button)
frame.setLayout(frame.layout)

shadow = QGraphicsDropShadowEffect()
shadow.setOffset(QPointF(3,3))
shadow.setBlurRadius(8)
#frame.setGraphicsEffect(shadow)
frame.button.setGraphicsEffect(shadow)

frame.show()

sys.exit(app.exec_())