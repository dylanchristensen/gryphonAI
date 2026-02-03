# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'find_and_replace_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFormLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QWidget)

class Ui_FindAndReplaceDialog(object):
    def setupUi(self, FindAndReplaceDialog):
        if not FindAndReplaceDialog.objectName():
            FindAndReplaceDialog.setObjectName(u"FindAndReplaceDialog")
        FindAndReplaceDialog.resize(411, 164)
        self.formLayoutWidget = QWidget(FindAndReplaceDialog)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 20, 391, 61))
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

        self.find_cb = QComboBox(self.formLayoutWidget)
        self.find_cb.setObjectName(u"find_cb")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.find_cb)

        self.replace_pb = QPushButton(FindAndReplaceDialog)
        self.replace_pb.setObjectName(u"replace_pb")
        self.replace_pb.setGeometry(QRect(10, 130, 83, 25))
        self.previous_pb = QPushButton(FindAndReplaceDialog)
        self.previous_pb.setObjectName(u"previous_pb")
        self.previous_pb.setGeometry(QRect(100, 130, 83, 25))
        self.next_pb = QPushButton(FindAndReplaceDialog)
        self.next_pb.setObjectName(u"next_pb")
        self.next_pb.setGeometry(QRect(190, 130, 83, 25))
        self.close_pb = QPushButton(FindAndReplaceDialog)
        self.close_pb.setObjectName(u"close_pb")
        self.close_pb.setGeometry(QRect(320, 130, 83, 25))
        self.match_case_cb = QCheckBox(FindAndReplaceDialog)
        self.match_case_cb.setObjectName(u"match_case_cb")
        self.match_case_cb.setGeometry(QRect(10, 90, 111, 23))
        QWidget.setTabOrder(self.find_cb, self.replace_with_le)
        QWidget.setTabOrder(self.replace_with_le, self.match_case_cb)
        QWidget.setTabOrder(self.match_case_cb, self.replace_pb)
        QWidget.setTabOrder(self.replace_pb, self.previous_pb)
        QWidget.setTabOrder(self.previous_pb, self.next_pb)
        QWidget.setTabOrder(self.next_pb, self.close_pb)

        self.retranslateUi(FindAndReplaceDialog)

        QMetaObject.connectSlotsByName(FindAndReplaceDialog)
    # setupUi

    def retranslateUi(self, FindAndReplaceDialog):
        FindAndReplaceDialog.setWindowTitle(QCoreApplication.translate("FindAndReplaceDialog", u"Find and replace", None))
        self.find_l.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Find", None))
        self.replace_l.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Replace with", None))
        self.replace_pb.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Replace", None))
        self.previous_pb.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Previous", None))
        self.next_pb.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Next", None))
        self.close_pb.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Close", None))
        self.match_case_cb.setText(QCoreApplication.translate("FindAndReplaceDialog", u"Match case", None))
    # retranslateUi

