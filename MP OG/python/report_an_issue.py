from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from version_file import VERSION

_issue_url = "https://gitlab.nps.edu/monterey-phoenix" \
             "/user-interfaces/gryphon/-/issues"
_issue_link = "<a href='%s'>%s</a>"%(_issue_url, _issue_url)

_text = 'To report an issue please open the Monterey Phoenix Gryphon ' \
        'issue tracker at %s and click the "New issue" button.<p>' \
        'Please include the version of the Operating System you are ' \
        'using and that you are using Gryphon %s.  ' \
        'If possible, please include a screen capture.<p>' \
        'Please de-identify screen capture and other ' \
        'submitted information as issues and related comments are ' \
        'public.'%(_issue_link, VERSION)

def report_an_issue(parent):
    mb = QMessageBox(parent)
    mb.setWindowTitle("Report an Issue")
    mb.setTextFormat(Qt.RichText)
    mb.setText(_text)
    mb.setStandardButtons(QMessageBox.Ok)
    mb.exec()

