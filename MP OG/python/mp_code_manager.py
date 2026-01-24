from PySide6.QtCore import Signal, Slot
from PySide6.QtCore import QObject
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QPlainTextDocumentLayout
from mp_code_syntax_highlighter import MPCodeSyntaxHighlighter
from mp_code_syntax_checker import mp_check_syntax
from mp_code_parser import mp_code_schema
from mp_code_filename import set_active_mp_code_filename

# use this to signal completion to GUI.
class SyntaxCheckSignaller(QObject):
    """
    Signals:
      signal_mp_code_syntax_checked(status)
    """

    # signal "" if okay
    signal_mp_code_syntax_checked = Signal(str,
                                          name='signalMPCodeSyntaxChecked')

    def __init__(self):
        super().__init__()

    def send_signal(self, syntax_text):
        self.signal_mp_code_syntax_checked.emit(syntax_text)

# get int line number from MP Code compiler error message
def _parse_error_line_number(line):
    if line[:14] == "*** error: at ":
        line_number = int(line.split()[3])
    else:
        # unexpected line
        line_number = 0
    return line_number

class MPCodeManager(QObject):
    """Provides the mp code document containing text and
    highlighting and signals for when text is set.  This also signals
    the syntax check report whenever text changes.

    For mp_code state associated with a run, see graphs_manager.

    Interfaces:
      * set_text(<new mp_code filename>, <new mp_code text>)
      * text() - returns current text from document
      * document - the mp code document
      * syntax_error_line_number - line number of error or 0 for no error

    Signals:
      * signal_mp_code_loaded()
      * signal_syntax_error_line_number_changed()
"""

    # signals
    signal_mp_code_loaded = Signal(name='signalMPCodeLoaded')
    signal_syntax_error_line_number_changed = Signal(
                                   name='signalSyntaxErrroLineNumberChanged')

    def __init__(self, signal_preferences_changed, signal_settings_changed,
                 signal_spellcheck_changed, statusbar):
        super().__init__()

        self.statusbar = statusbar
        self.document = QTextDocument()
        self.document.setDocumentLayout(QPlainTextDocumentLayout(self.document))
        self.highlighter = MPCodeSyntaxHighlighter(self.document,
                          signal_preferences_changed, signal_settings_changed,
                          signal_spellcheck_changed)
        self.syntax_error_line_number = 0

        self.syntax_check_signaler = SyntaxCheckSignaller()

        self._mp_code_text = ""

        # connect
        self.document.contentsChanged.connect(self._mp_code_changed)
        self.syntax_check_signaler.signal_mp_code_syntax_checked.connect(
                                               self._syntax_check_completed)

    def set_text(self, filename, text):
        set_active_mp_code_filename(filename)
        self.document.setPlainText(text)
        self._mp_code_changed()
        self.document.setModified(False)
        self.signal_mp_code_loaded.emit()

    def text(self):
        return self.document.toPlainText()

    @Slot()
    def _mp_code_changed(self):
        # parse mp code
        mp_code_text = self.document.toPlainText()

        # done if no change
        if mp_code_text == self._mp_code_text:
            # no change to actual text
            return
        self._mp_code_text = mp_code_text

        # run highlighter
        self.highlighter.rehighlight()

        # run trace-generator syntax check
        if mp_code_text:
            schema = mp_code_schema(mp_code_text)
            _status = mp_check_syntax(schema, mp_code_text,
                                      self.syntax_check_signaler.send_signal)

    @Slot(str)
    def _syntax_check_completed(self, status):

        # set the error line number else 0
        self.syntax_error_line_number = _parse_error_line_number(status)
        self.signal_syntax_error_line_number_changed.emit()

        # show status in statusbar
        self.statusbar.showMessage(status)

