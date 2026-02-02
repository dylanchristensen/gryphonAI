import re
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal, Slot # for signal/slot support
from PySide6.QtWidgets import QDialog, QPlainTextEdit
from PySide6.QtGui import QKeyEvent, QFocusEvent, QAction
from spellcheck_whitelist_dialog import Ui_SpellcheckWhitelistDialog
from spellcheck import user_whitelist
from verbose import verbose

class SpellcheckWhitelistTextEdit(QPlainTextEdit):

    signal_refresh_whitelist = Signal(name='signalRefreshWhitelist')

    def __init__(self):
        super().__init__()

    # intercept keyPress to prohibit select ascii text but do allow
    # characters such as CR and backspace
    @Slot(QKeyEvent)
    def keyPressEvent(self, e):
        text = e.text()
        if text != '' \
                and text in '0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~':

            if verbose():
                print("text dropped: '%s'"%text)

            # drop the text
            return
        else:
            # keep the text
            super().keyPressEvent(e)

            # refresh on CR
            if e.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.signal_refresh_whitelist.emit()

    @Slot(QFocusEvent)
    def focusOutEvent(self, e):
        # refresh on lose keyboard focus
        self.signal_refresh_whitelist.emit()
        super().focusOutEvent(e)

class SpellcheckWhitelistDialogWrapper(QDialog):

    def __init__(self, parent_window, spellcheck_whitelist_manager):
        super().__init__(parent_window)
        self.spellcheck_whitelist_manager = spellcheck_whitelist_manager
        self.ui = Ui_SpellcheckWhitelistDialog()
        self.ui.setupUi(self) # we refine this further below
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
        self.setWindowTitle("MP Code Spellcheck Whitelist")

        # the QPlainTextEdit editor view
        self.whitelist_text_edit = SpellcheckWhitelistTextEdit()
        self.ui.layout.addWidget(self.whitelist_text_edit)
        self.whitelist_text_edit.setPlainText(user_whitelist())

        # action
        self.action_open_spellcheck_whitelist_dialog = QAction(
                                                "Spellchecker whitelist...")
        self.action_open_spellcheck_whitelist_dialog.setToolTip(
                      "Set a word whitelist for the code editor spellchecker")
        self.action_open_spellcheck_whitelist_dialog.triggered.connect(
                                                          self.show)

        # connect
        self.ui.close_pb.clicked.connect(self.close) # superclass close
        self.whitelist_text_edit.signal_refresh_whitelist.connect(
                                              self._accept_text_changed)
        spellcheck_whitelist_manager.signal_spellcheck_changed.connect(
                                            self._replace_editor_text)

    @Slot()
    def _accept_text_changed(self):
        text = self.whitelist_text_edit.toPlainText()
        self.spellcheck_whitelist_manager.set_user_whitelist(text)

    @Slot()
    def _replace_editor_text(self):
        if self.whitelist_text_edit.toPlainText() != user_whitelist():
            # replace text in whitelist text edit view
            self.whitelist_text_edit.setPlainText(user_whitelist())

