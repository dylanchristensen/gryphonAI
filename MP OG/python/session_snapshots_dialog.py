# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'session_snapshots_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHeaderView, QPushButton,
    QSizePolicy, QTableView, QWidget)

class Ui_SessionSnapshotsDialog(object):
    def setupUi(self, SessionSnapshotsDialog):
        if not SessionSnapshotsDialog.objectName():
            SessionSnapshotsDialog.setObjectName(u"SessionSnapshotsDialog")
        SessionSnapshotsDialog.resize(551, 324)
        SessionSnapshotsDialog.setModal(True)
        self.open_pb = QPushButton(SessionSnapshotsDialog)
        self.open_pb.setObjectName(u"open_pb")
        self.open_pb.setGeometry(QRect(20, 290, 83, 25))
        self.delete_pb = QPushButton(SessionSnapshotsDialog)
        self.delete_pb.setObjectName(u"delete_pb")
        self.delete_pb.setGeometry(QRect(140, 290, 83, 25))
        self.delete_all_pb = QPushButton(SessionSnapshotsDialog)
        self.delete_all_pb.setObjectName(u"delete_all_pb")
        self.delete_all_pb.setGeometry(QRect(240, 290, 83, 25))
        self.close_pb = QPushButton(SessionSnapshotsDialog)
        self.close_pb.setObjectName(u"close_pb")
        self.close_pb.setGeometry(QRect(440, 290, 83, 25))
        self.snapshots_table_view = QTableView(SessionSnapshotsDialog)
        self.snapshots_table_view.setObjectName(u"snapshots_table_view")
        self.snapshots_table_view.setGeometry(QRect(0, 0, 551, 281))

        self.retranslateUi(SessionSnapshotsDialog)

        QMetaObject.connectSlotsByName(SessionSnapshotsDialog)
    # setupUi

    def retranslateUi(self, SessionSnapshotsDialog):
        SessionSnapshotsDialog.setWindowTitle(QCoreApplication.translate("SessionSnapshotsDialog", u"Session snapshots", None))
        self.open_pb.setText(QCoreApplication.translate("SessionSnapshotsDialog", u"Open", None))
        self.delete_pb.setText(QCoreApplication.translate("SessionSnapshotsDialog", u"Delete", None))
        self.delete_all_pb.setText(QCoreApplication.translate("SessionSnapshotsDialog", u"Delete All", None))
        self.close_pb.setText(QCoreApplication.translate("SessionSnapshotsDialog", u"Close", None))
    # retranslateUi

