# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'keyboard_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QScrollArea, QSizePolicy, QWidget)

class Ui_KeyboardDialog(object):
    def setupUi(self, KeyboardDialog):
        if not KeyboardDialog.objectName():
            KeyboardDialog.setObjectName(u"KeyboardDialog")
        KeyboardDialog.resize(1145, 767)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(KeyboardDialog.sizePolicy().hasHeightForWidth())
        KeyboardDialog.setSizePolicy(sizePolicy)
        KeyboardDialog.setStyleSheet(u"background:white; border:0")
        self.horizontalLayout = QHBoxLayout(KeyboardDialog)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(KeyboardDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1145, 767))
        self.horizontalLayout_2 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.keyboard_label = QLabel(self.scrollAreaWidgetContents)
        self.keyboard_label.setObjectName(u"keyboard_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.keyboard_label.sizePolicy().hasHeightForWidth())
        self.keyboard_label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.keyboard_label)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.scrollArea)


        self.retranslateUi(KeyboardDialog)

        QMetaObject.connectSlotsByName(KeyboardDialog)
    # setupUi

    def retranslateUi(self, KeyboardDialog):
        KeyboardDialog.setWindowTitle(QCoreApplication.translate("KeyboardDialog", u"Monterey Phoenix - Gryphon Keyboard Shortcuts", None))
        self.keyboard_label.setText(QCoreApplication.translate("KeyboardDialog", u"TextLabel", None))
    # retranslateUi

