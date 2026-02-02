# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'spellcheck_whitelist_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
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

class Ui_SpellcheckWhitelistDialog(object):
    def setupUi(self, SpellcheckWhitelistDialog):
        if not SpellcheckWhitelistDialog.objectName():
            SpellcheckWhitelistDialog.setObjectName(u"SpellcheckWhitelistDialog")
        SpellcheckWhitelistDialog.resize(572, 320)
        self.close_pb = QPushButton(SpellcheckWhitelistDialog)
        self.close_pb.setObjectName(u"close_pb")
        self.close_pb.setGeometry(QRect(240, 290, 83, 25))
        self.verticalLayoutWidget = QWidget(SpellcheckWhitelistDialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 571, 281))
        self.layout = QVBoxLayout(self.verticalLayoutWidget)
        self.layout.setObjectName(u"layout")
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.retranslateUi(SpellcheckWhitelistDialog)

        QMetaObject.connectSlotsByName(SpellcheckWhitelistDialog)
    # setupUi

    def retranslateUi(self, SpellcheckWhitelistDialog):
        SpellcheckWhitelistDialog.setWindowTitle(QCoreApplication.translate("SpellcheckWhitelistDialog", u"MP Code Whitelist", None))
        self.close_pb.setText(QCoreApplication.translate("SpellcheckWhitelistDialog", u"Close", None))
    # retranslateUi

