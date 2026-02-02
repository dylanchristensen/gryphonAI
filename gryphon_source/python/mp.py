#!/usr/bin/env python3

import sys
from os import environ
from PySide6.QtWidgets import QApplication
from gui_manager import GUIManager

# main
if __name__ == "__main__":

    # create the "application" and the main window
    application = QApplication(sys.argv)

    # create MP GUI manager
    _gui_manager = GUIManager(application)

    # start the GUI
    sys.exit(application.exec())

