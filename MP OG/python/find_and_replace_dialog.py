# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'find_and_replace_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QToolButton,
    QWidget)

from find_and_replace_cb import FindAndReplaceCB

class Ui_FindAndReplaceDialog(object):
    def setupUi(self, FindAndReplaceDialog):
        if not FindAndReplaceDialog.objectName():
            FindAndReplaceDialog.setObjectName(u"FindAndReplaceDialog")
        FindAndReplaceDialog.resize(472, 126)
        self.formLayoutWidget = QWidget(FindAndReplaceDialog)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 20, 391, 63))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.find_l = QLabel(self.formLayoutWidget)
        self.find_l.setObjectName(u"find_l")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.find_l)

        self.replace_l = QLabel(self.formLayoutWidget)
        self.replace_l.setObjectName(u"replace_l")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.replace_l)

        self.replace_with_le = QLineEdit(self.formLayoutWidget)
        self.replace_with_le.setObjectName(u"replace_with_le")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.replace_with_le)

        self.find_cb = FindAndReplaceCB(self.formLayoutWidget)
        self.find_cb.setObjectName(u"find_cb")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.find_cb)

        self.replace_pb = QPushButton(FindAndReplaceDialog)
        self.replace_pb.setObjectName(u"replace_pb")
        self.replace_pb.setGeometry(QRect(200, 90, 83, 25))
        self.close_pb = QPushButton(FindAndReplaceDialog)
        self.close_pb.setObjectName(u"close_pb")
        self.close_pb.setGeometry(QRect(380, 90, 83, 25))
        self.previous_tb = QToolButton(FindAndReplaceDialog)
        self.previous_tb.setObjectName(u"previous_tb")
        self.previous_tb.setGeometry(QRect(410, 20, 21, 26))
        self.next_tb = QToolButton(FindAndReplaceDialog)
        self.next_tb.setObjectName(u"next_tb")
        self.next_tb.setGeometry(QRect(440, 20, 21, 26))
        QWidget.setTabOrder(self.find_cb, self.replace_with_le)
        QWidget.setTabOrder(self.replace_with_le, self.replace_pb)
        QWidget.setTabOrder(self.replace_pb, self.close_pb)

        self.retranslateUi(FindAndReplaceDialog)

        QMetaObject.connectSlotsByName(FindAndReplaceDialog)
    # setupUi

    def retranslateUi(self, FindAndReplaceDialog):
        FindAndReplaceDialog.setWindowTitle(QCoreApplication.translate("FindAndReplaceDialog", u"Find and replace", None))
        self.find_l.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Find", None))
        self.replace_l.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Replace with", None))
        self.replace_pb.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Replace", None))
        self.close_pb.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Close", None))
        self.previous_tb.setText(QCoreApplication.translate("FindAndReplaceDialog", u"<", None))
        self.next_tb.setText(QCoreApplication.translate("FindAndReplaceDialog", u">", None))
    # retranslateUi

