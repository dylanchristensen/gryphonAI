# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'search_mp_code_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_SearchMPCodeDialog(object):
    def setupUi(self, SearchMPCodeDialog):
        if not SearchMPCodeDialog.objectName():
            SearchMPCodeDialog.setObjectName(u"SearchMPCodeDialog")
        SearchMPCodeDialog.resize(822, 613)
        self.copy_pb = QPushButton(SearchMPCodeDialog)
        self.copy_pb.setObjectName(u"copy_pb")
        self.copy_pb.setGeometry(QRect(150, 580, 83, 25))
        self.close_pb = QPushButton(SearchMPCodeDialog)
        self.close_pb.setObjectName(u"close_pb")
        self.close_pb.setGeometry(QRect(370, 580, 83, 25))
        self.verticalLayoutWidget = QWidget(SearchMPCodeDialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 821, 571))
        self.layout = QVBoxLayout(self.verticalLayoutWidget)
        self.layout.setObjectName(u"layout")
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.retranslateUi(SearchMPCodeDialog)

        QMetaObject.connectSlotsByName(SearchMPCodeDialog)
    # setupUi

    def retranslateUi(self, SearchMPCodeDialog):
        SearchMPCodeDialog.setWindowTitle(QCoreApplication.translate("SearchMPCodeDialog", u"Search .mp code", None))
        self.copy_pb.setText(QCoreApplication.translate("SearchMPCodeDialog", u"Copy", None))
        self.close_pb.setText(QCoreApplication.translate("SearchMPCodeDialog", u"Close", None))
    # retranslateUi

