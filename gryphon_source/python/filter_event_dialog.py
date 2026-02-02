# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filter_event_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHeaderView, QLabel, QRadioButton, QSizePolicy,
    QToolButton, QWidget)

from filter_event_table_view import FilterEventTableView

class Ui_FilterEventDialog(object):
    def setupUi(self, FilterEventDialog):
        if not FilterEventDialog.objectName():
            FilterEventDialog.setObjectName(u"FilterEventDialog")
        FilterEventDialog.resize(770, 538)
        self.button_box = QDialogButtonBox(FilterEventDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setGeometry(QRect(70, 500, 341, 32))
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Close)
        self.and_rb = QRadioButton(FilterEventDialog)
        self.and_rb.setObjectName(u"and_rb")
        self.and_rb.setGeometry(QRect(310, 10, 91, 25))
        self.or_rb = QRadioButton(FilterEventDialog)
        self.or_rb.setObjectName(u"or_rb")
        self.or_rb.setGeometry(QRect(400, 10, 81, 25))
        self.relationship_table_view = FilterEventTableView(FilterEventDialog)
        self.relationship_table_view.setObjectName(u"relationship_table_view")
        self.relationship_table_view.setGeometry(QRect(10, 50, 721, 201))
        self.label = QLabel(FilterEventDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 30, 221, 19))
        self.label_2 = QLabel(FilterEventDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 270, 181, 19))
        self.recurrence_table_view = FilterEventTableView(FilterEventDialog)
        self.recurrence_table_view.setObjectName(u"recurrence_table_view")
        self.recurrence_table_view.setGeometry(QRect(10, 290, 481, 201))
        self.add_relationship_button = QToolButton(FilterEventDialog)
        self.add_relationship_button.setObjectName(u"add_relationship_button")
        self.add_relationship_button.setGeometry(QRect(740, 50, 21, 21))
        self.remove_relationship_button = QToolButton(FilterEventDialog)
        self.remove_relationship_button.setObjectName(u"remove_relationship_button")
        self.remove_relationship_button.setGeometry(QRect(740, 80, 21, 21))
        self.add_recurrence_button = QToolButton(FilterEventDialog)
        self.add_recurrence_button.setObjectName(u"add_recurrence_button")
        self.add_recurrence_button.setGeometry(QRect(500, 290, 21, 21))
        self.remove_recurrence_button = QToolButton(FilterEventDialog)
        self.remove_recurrence_button.setObjectName(u"remove_recurrence_button")
        self.remove_recurrence_button.setGeometry(QRect(500, 320, 21, 21))

        self.retranslateUi(FilterEventDialog)
        self.button_box.accepted.connect(FilterEventDialog.accept)
        self.button_box.rejected.connect(FilterEventDialog.reject)

        QMetaObject.connectSlotsByName(FilterEventDialog)
    # setupUi

    def retranslateUi(self, FilterEventDialog):
        FilterEventDialog.setWindowTitle(QCoreApplication.translate("FilterEventDialog", u"Custom Event Filter", None))
        self.and_rb.setText(QCoreApplication.translate("FilterEventDialog", u"And", None))
        self.or_rb.setText(QCoreApplication.translate("FilterEventDialog", u"Or", None))
        self.label.setText(QCoreApplication.translate("FilterEventDialog", u"Event relationships:", None))
        self.label_2.setText(QCoreApplication.translate("FilterEventDialog", u"Event recurrence:", None))
        self.add_relationship_button.setText(QCoreApplication.translate("FilterEventDialog", u"+", None))
        self.remove_relationship_button.setText(QCoreApplication.translate("FilterEventDialog", u"-", None))
        self.add_recurrence_button.setText(QCoreApplication.translate("FilterEventDialog", u"+", None))
        self.remove_recurrence_button.setText(QCoreApplication.translate("FilterEventDialog", u"-", None))
    # retranslateUi

