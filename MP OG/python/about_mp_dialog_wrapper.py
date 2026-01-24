# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
import webbrowser
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from about_mp_dialog import Ui_AboutMPDialog

def _make_link(url, text):
    return "<a href='%s'>%s</a>"%(url, text)

_nps_link = _make_link("http://nps.edu", "Naval Postgraduate School")
_mp_link = _make_link("https://wiki.nps.edu/display/MP",
                      "Monterey Phoenix website")
_mp_about_link = _make_link("https://wiki.nps.edu/display/MP/about",
                            "Monterey Phoenix website About page")
_doc_link = _make_link("https://gitlab.nps.edu/monterey-phoenix/"
                       "user-interfaces/gryphon/-/wikis/home",
                       "Gryphon Wiki home page")

_text = '<p><span style="font-size:20pt;">Monterey Phoenix (MP) Gryphon' \
        '</span></p>' \
        'The Monterey Phoenix Gryphon GUI supports Monterey Phoenix users ' \
        'with an interface for creating MP schemas and generating trace ' \
        'graphs and other local and global views.' \
        '<p>The Monterey Phoenix language and editor were developed at ' \
        'the %s.' \
        '<p><span style="font-size:16pt;">Resources:</span>' \
        '<p>• %s' \
        '<p>• %s' \
        '<p>• %s'%(_nps_link, _mp_link, _mp_about_link, _doc_link)

class AboutMPDialogWrapper(QDialog):
    def __init__(self, parent):
        super(AboutMPDialogWrapper, self).__init__(parent)
        self.ui = Ui_AboutMPDialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
        self.ui.about_mp_label.setOpenExternalLinks(True)

        self.ui.about_mp_label.setOpenExternalLinks(True)

        label = self.ui.about_mp_label
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)
        label.setText(_text)

