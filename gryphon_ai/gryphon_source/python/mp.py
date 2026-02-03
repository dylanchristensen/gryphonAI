#!/usr/bin/env python3

import sys
from os import environ
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from gui_manager import GUIManager

# main
if __name__ == "__main__":

    # reduce distracting Qt logging
    environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

    # create the "application" and the main window
    application = QApplication(sys.argv)
    print("QApplication font", application.font().family())
    application.setFont(QFont("arial"))
    print("QApplication font", application.font().family())

    # create MP GUI manager
    gui_manager = GUIManager(application)

    # start the GUI
    sys.exit(application.exec())

