# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_mp_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QSizePolicy,
    QToolButton, QWidget)
import resources_rc

class Ui_AboutMPDialog(object):
    def setupUi(self, AboutMPDialog):
        if not AboutMPDialog.objectName():
            AboutMPDialog.setObjectName(u"AboutMPDialog")
        AboutMPDialog.resize(946, 328)
        self.widget = QWidget(AboutMPDialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(30, 30, 291, 271))
        self.widget.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.mp_gryphon_tb = QToolButton(self.widget)
        self.mp_gryphon_tb.setObjectName(u"mp_gryphon_tb")
        self.mp_gryphon_tb.setGeometry(QRect(20, 20, 251, 151))
        self.mp_gryphon_tb.setFocusPolicy(Qt.NoFocus)
        self.mp_gryphon_tb.setStyleSheet(u"border:none")
        icon = QIcon()
        icon.addFile(u":/images/phoenix_logo", QSize(), QIcon.Normal, QIcon.Off)
        self.mp_gryphon_tb.setIcon(icon)
        self.mp_gryphon_tb.setIconSize(QSize(600, 150))
        self.nps_tb = QToolButton(self.widget)
        self.nps_tb.setObjectName(u"nps_tb")
        self.nps_tb.setGeometry(QRect(70, 200, 151, 53))
        self.nps_tb.setFocusPolicy(Qt.NoFocus)
        self.nps_tb.setStyleSheet(u"border:none")
        icon1 = QIcon()
        icon1.addFile(u":/images/nps_logo", QSize(), QIcon.Normal, QIcon.Off)
        self.nps_tb.setIcon(icon1)
        self.nps_tb.setIconSize(QSize(400, 50))
        self.about_mp_label = QLabel(AboutMPDialog)
        self.about_mp_label.setObjectName(u"about_mp_label")
        self.about_mp_label.setGeometry(QRect(370, 10, 551, 311))

        self.retranslateUi(AboutMPDialog)

        QMetaObject.connectSlotsByName(AboutMPDialog)
    # setupUi

    def retranslateUi(self, AboutMPDialog):
        AboutMPDialog.setWindowTitle(QCoreApplication.translate("AboutMPDialog", u"About Monterey Phoenix - Gryphon", None))
#if QT_CONFIG(tooltip)
        self.mp_gryphon_tb.setToolTip(QCoreApplication.translate("AboutMPDialog", u"http://wiki.nps.edu/display/MP", None))
#endif // QT_CONFIG(tooltip)
        self.mp_gryphon_tb.setText(QCoreApplication.translate("AboutMPDialog", u"...", None))
#if QT_CONFIG(tooltip)
        self.nps_tb.setToolTip(QCoreApplication.translate("AboutMPDialog", u"http://www.nps.edu", None))
#endif // QT_CONFIG(tooltip)
        self.nps_tb.setText(QCoreApplication.translate("AboutMPDialog", u"...", None))
        self.about_mp_label.setText(QCoreApplication.translate("AboutMPDialog", u"TextLabel", None))
    # retranslateUi

