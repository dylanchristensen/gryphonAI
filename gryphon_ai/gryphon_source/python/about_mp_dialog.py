# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_mp_dialog.ui'
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
    QSizePolicy, QToolButton, QWidget)
import resources_rc

class Ui_AboutMPDialog(object):
    def setupUi(self, AboutMPDialog):
        if not AboutMPDialog.objectName():
            AboutMPDialog.setObjectName(u"AboutMPDialog")
        AboutMPDialog.resize(821, 327)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutMPDialog.sizePolicy().hasHeightForWidth())
        AboutMPDialog.setSizePolicy(sizePolicy)
        AboutMPDialog.setStyleSheet(u"background:white; border:0")
        self.horizontalLayout = QHBoxLayout(AboutMPDialog)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_2 = QWidget(AboutMPDialog)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(300, 0))
        self.widget = QWidget(self.widget_2)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 20, 300, 300))
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(117)
        sizePolicy1.setVerticalStretch(28)
        sizePolicy1.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy1)
        self.widget.setMinimumSize(QSize(300, 300))
        self.mp_gryphon_tb = QToolButton(self.widget)
        self.mp_gryphon_tb.setObjectName(u"mp_gryphon_tb")
        self.mp_gryphon_tb.setGeometry(QRect(10, 10, 251, 151))
        self.mp_gryphon_tb.setFocusPolicy(Qt.NoFocus)
        self.mp_gryphon_tb.setStyleSheet(u"QToolTip{color:black}")
        icon = QIcon()
        icon.addFile(u":/images/phoenix_logo", QSize(), QIcon.Normal, QIcon.Off)
        self.mp_gryphon_tb.setIcon(icon)
        self.mp_gryphon_tb.setIconSize(QSize(600, 150))
        self.nps_tb = QToolButton(self.widget)
        self.nps_tb.setObjectName(u"nps_tb")
        self.nps_tb.setGeometry(QRect(70, 190, 151, 53))
        self.nps_tb.setFocusPolicy(Qt.NoFocus)
        self.nps_tb.setStyleSheet(u"QToolTip{color:black}")
        icon1 = QIcon()
        icon1.addFile(u":/images/nps_logo", QSize(), QIcon.Normal, QIcon.Off)
        self.nps_tb.setIcon(icon1)
        self.nps_tb.setIconSize(QSize(400, 50))
        self.about_mp_label = QLabel(self.widget_2)
        self.about_mp_label.setObjectName(u"about_mp_label")
        self.about_mp_label.setGeometry(QRect(320, 20, 471, 281))
        self.about_mp_label.setWordWrap(True)

        self.horizontalLayout.addWidget(self.widget_2)


        self.retranslateUi(AboutMPDialog)

        QMetaObject.connectSlotsByName(AboutMPDialog)
    # setupUi

    def retranslateUi(self, AboutMPDialog):
        AboutMPDialog.setWindowTitle(QCoreApplication.translate("AboutMPDialog", u"About Montery Phoenix - Gryphon", None))
#if QT_CONFIG(tooltip)
        self.mp_gryphon_tb.setToolTip(QCoreApplication.translate("AboutMPDialog", u"http://wiki.nps.edu/display/MP", None))
#endif // QT_CONFIG(tooltip)
        self.mp_gryphon_tb.setText(QCoreApplication.translate("AboutMPDialog", u"...", None))
#if QT_CONFIG(tooltip)
        self.nps_tb.setToolTip(QCoreApplication.translate("AboutMPDialog", u"http://www.nps.edu", None))
#endif // QT_CONFIG(tooltip)
        self.nps_tb.setText(QCoreApplication.translate("AboutMPDialog", u"...", None))
        self.about_mp_label.setText(QCoreApplication.translate("AboutMPDialog", u"<html><head/><body><p><span style=\" font-size:20pt;\">Monterey Phoenix (MP) Gryphon</span></p><p>The Monterey Phoenix Gryphon GUI supports Monterey Phoenix users with an interface for creating MP schemas and generating trace graphs and other local and global views.</p><p>The Monterey Phoenix language and editor were developed at the <a href=\"http://nps.edu\"><span style=\" text-decoration: underline; color:#0000ff;\">Naval Postgraduate School.</span></a></p><p><span style=\" font-size:16pt;\">Resources:</span><br/>\u2022 <a href=\"https://wiki.nps.edu/display/MP\"><span style=\" text-decoration: underline; color:#0000ff;\">Monterey Phoenix website</span></a></p><p>\u2022 <a href=\"https://wiki.nps.edu/display/MP/about\"><span style=\" text-decoration: underline; color:#0000ff;\">Monterey Phoenix website About page</span></a></p></body></html>", None))
    # retranslateUi

