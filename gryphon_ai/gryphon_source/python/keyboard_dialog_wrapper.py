# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
from os.path import join, dirname
from PySide6.QtWidgets import QDialog
from keyboard_dialog import Ui_KeyboardDialog

class KeyboardDialogWrapper(QDialog):
    def __init__(self, parent):
        super(KeyboardDialogWrapper, self).__init__(parent)
        self.ui = Ui_KeyboardDialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.width(), self.height())

        # put in text from file
        shortcuts_file = join(dirname(__file__), "html",
                              "Keyboardshortcuts.html")
        with open(shortcuts_file) as f:
            text = f.read()
        self.ui.keyboard_label.setText(text)

