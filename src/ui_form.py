# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(800, 600)
        Widget.setMinimumSize(QSize(800, 600))
        self.horizontalLayout_2 = QHBoxLayout(Widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.rewindButton = QPushButton(Widget)
        self.rewindButton.setObjectName(u"rewindButton")
        font = QFont()
        font.setFamilies([u"FreeSans"])
        font.setPointSize(16)
        self.rewindButton.setFont(font)

        self.horizontalLayout_3.addWidget(self.rewindButton, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.toggleButton = QPushButton(Widget)
        self.toggleButton.setObjectName(u"toggleButton")
        font1 = QFont()
        font1.setFamilies([u"FreeSans"])
        font1.setPointSize(16)
        font1.setBold(False)
        font1.setItalic(False)
        self.toggleButton.setFont(font1)

        self.horizontalLayout_3.addWidget(self.toggleButton, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.frequencyLabel = QLabel(Widget)
        self.frequencyLabel.setObjectName(u"frequencyLabel")
        self.frequencyLabel.setFont(font)

        self.horizontalLayout_4.addWidget(self.frequencyLabel, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.frequencySlider = QSlider(Widget)
        self.frequencySlider.setObjectName(u"frequencySlider")
        self.frequencySlider.setMinimum(1)
        self.frequencySlider.setMaximum(50)
        self.frequencySlider.setValue(5)
        self.frequencySlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_4.addWidget(self.frequencySlider)

        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 7)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)

        self.horizontalLayout.addLayout(self.verticalLayout)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.rewindButton.setText(QCoreApplication.translate("Widget", u"\u23ee", None))
        self.toggleButton.setText(QCoreApplication.translate("Widget", u"\u23f5", None))
        self.frequencyLabel.setText(QCoreApplication.translate("Widget", u"5/s", None))
    # retranslateUi

