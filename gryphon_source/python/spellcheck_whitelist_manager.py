from os.path import isfile
from spellchecker import SpellChecker
from PySide6.QtCore import QObject, Signal, Slot # for signal/slot support
from PySide6.QtCore import QFile, QTextStream, QIODevice
from PySide6.QtGui import QTextDocument, QTextCursor
from paths_gryphon import SPELLCHECK_WHITELIST_FILENAME
from mp_code_expressions import MP_KEYWORDS, MP_META_SYMBOLS
#from spellcheck import change_user_whitelist
#from spellcheck_whitelist_dialog_wrapper import SpellcheckWhitelistDialogWrapper

from spellcheck import set_checker, user_whitelist


class SpellcheckWhitelistManager(QObject):
    """
    Use this for updating the user whitelist.

    Use spellcheck for singleton access to the checker.

    The spellcheck whitelist dialog should call set_user_whitelist on CR
    or on lose focus in order to reset the checker with new whitelist_text.
    It should not call set_user_whitelist every time text in the dialog
    changes.

    Interfaces:
      * set_user_whitelist(whitelist_text) - words separated by space
      * add_user_whitelist_word(word) - add word

    Signals:
      * signal_spellcheck_changed(whitelist_text) - The spellcheck
        whitelist dialog should refresh with new text on this signal.
    """

    # signal
    signal_spellcheck_changed = Signal(name='signalSpellcheckChanged')

    def __init__(self):
        super().__init__()

    def set_user_whitelist(self, whitelist_text):
        set_checker(whitelist_text)
        self.signal_spellcheck_changed.emit()

    def add_user_whitelist_word(self, word):
        set_checker("%s %s"%(user_whitelist(), word))
        self.signal_spellcheck_changed.emit()

