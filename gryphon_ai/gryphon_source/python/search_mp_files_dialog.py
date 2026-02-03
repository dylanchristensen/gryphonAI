# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'search_mp_files_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFormLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_SearchMPFilesDialog(object):
    def setupUi(self, SearchMPFilesDialog):
        if not SearchMPFilesDialog.objectName():
            SearchMPFilesDialog.setObjectName(u"SearchMPFilesDialog")
        SearchMPFilesDialog.resize(942, 514)
        self.collection_path_pb = QPushButton(SearchMPFilesDialog)
        self.collection_path_pb.setObjectName(u"collection_path_pb")
        self.collection_path_pb.setGeometry(QRect(170, 100, 61, 25))
        self.collection_path_pb.setAutoDefault(False)
        self.View_pb = QPushButton(SearchMPFilesDialog)
        self.View_pb.setObjectName(u"View_pb")
        self.View_pb.setGeometry(QRect(160, 480, 83, 25))
        self.View_pb.setAutoDefault(False)
        self.close_pb = QPushButton(SearchMPFilesDialog)
        self.close_pb.setObjectName(u"close_pb")
        self.close_pb.setGeometry(QRect(380, 480, 83, 25))
        self.close_pb.setAutoDefault(False)
        self.label = QLabel(SearchMPFilesDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 71, 17))
        self.preloaded_models_cb = QCheckBox(SearchMPFilesDialog)
        self.preloaded_models_cb.setObjectName(u"preloaded_models_cb")
        self.preloaded_models_cb.setGeometry(QRect(20, 40, 221, 23))
        self.preloaded_models_cb.setChecked(True)
        self.preloaded_snippets_cb = QCheckBox(SearchMPFilesDialog)
        self.preloaded_snippets_cb.setObjectName(u"preloaded_snippets_cb")
        self.preloaded_snippets_cb.setGeometry(QRect(20, 70, 221, 23))
        self.preloaded_snippets_cb.setChecked(True)
        self.personal_collection_cb = QCheckBox(SearchMPFilesDialog)
        self.personal_collection_cb.setObjectName(u"personal_collection_cb")
        self.personal_collection_cb.setGeometry(QRect(20, 100, 161, 23))
        self.personal_collection_cb.setChecked(True)
        self.formLayoutWidget = QWidget(SearchMPFilesDialog)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(290, 20, 421, 61))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.formLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.label_3 = QLabel(self.formLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.file_contains_le = QLineEdit(self.formLayoutWidget)
        self.file_contains_le.setObjectName(u"file_contains_le")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.file_contains_le)

        self.filename_contains_le = QLineEdit(self.formLayoutWidget)
        self.filename_contains_le.setObjectName(u"filename_contains_le")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.filename_contains_le)

        self.verticalLayoutWidget = QWidget(SearchMPFilesDialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(20, 140, 901, 331))
        self.file_metadata_table_layout = QVBoxLayout(self.verticalLayoutWidget)
        self.file_metadata_table_layout.setObjectName(u"file_metadata_table_layout")
        self.file_metadata_table_layout.setContentsMargins(0, 0, 0, 0)
        self.refresh_table_pb = QPushButton(SearchMPFilesDialog)
        self.refresh_table_pb.setObjectName(u"refresh_table_pb")
        self.refresh_table_pb.setGeometry(QRect(610, 100, 101, 25))
        self.refresh_table_pb.setAutoDefault(False)
        self.personal_collection_path_le = QLineEdit(SearchMPFilesDialog)
        self.personal_collection_path_le.setObjectName(u"personal_collection_path_le")
        self.personal_collection_path_le.setEnabled(True)
        self.personal_collection_path_le.setGeometry(QRect(250, 100, 341, 25))
        self.personal_collection_path_le.setReadOnly(True)

        self.retranslateUi(SearchMPFilesDialog)

        QMetaObject.connectSlotsByName(SearchMPFilesDialog)
    # setupUi

    def retranslateUi(self, SearchMPFilesDialog):
        SearchMPFilesDialog.setWindowTitle(QCoreApplication.translate("SearchMPFilesDialog", u"Search .mp text", None))
        self.collection_path_pb.setText(QCoreApplication.translate("SearchMPFilesDialog", u"Path...", None))
        self.View_pb.setText(QCoreApplication.translate("SearchMPFilesDialog", u"View", None))
        self.close_pb.setText(QCoreApplication.translate("SearchMPFilesDialog", u"Close", None))
        self.label.setText(QCoreApplication.translate("SearchMPFilesDialog", u"Search in:", None))
        self.preloaded_models_cb.setText(QCoreApplication.translate("SearchMPFilesDialog", u"Preloaded example models", None))
        self.preloaded_snippets_cb.setText(QCoreApplication.translate("SearchMPFilesDialog", u"Preloaded example snippets", None))
        self.personal_collection_cb.setText(QCoreApplication.translate("SearchMPFilesDialog", u"Personal collection", None))
        self.label_2.setText(QCoreApplication.translate("SearchMPFilesDialog", u"Filename contains:", None))
        self.label_3.setText(QCoreApplication.translate("SearchMPFilesDialog", u"File contains:", None))
        self.refresh_table_pb.setText(QCoreApplication.translate("SearchMPFilesDialog", u"Refresh table", None))
    # retranslateUi

