# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
import webbrowser
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtWidgets import QDialog
from about_mp_dialog import Ui_AboutMPDialog

class AboutMPDialogWrapper(QDialog):
    def __init__(self, parent):
        super(AboutMPDialogWrapper, self).__init__(parent)
        self.ui = Ui_AboutMPDialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.ui.about_mp_label.setOpenExternalLinks(True)

