from PySide6.QtGui import QTextDocument
from PySide6.QtCore import Signal, Slot
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QPlainTextDocumentLayout
from mp_code_highlighter import MPCodeHighlighter
from mp_code_syntax_checker import SyntaxCheckSignaller, mp_check_syntax

# get int line number from MP Code compiler error message
def _parse_error_line_number(line):
    if line[:14] == "*** error: at ":
        line_number = int(line.split()[3])
    else:
        # unexpected line
        line_number = 0
    return line_number

class MPCodeManager(QObject):
    """Provides the mp code QTextDocument document containing text and
    highlighting and signals for when text is set.  This also signals
    the syntax check report whenever text changes.

    Interfaces:
      * set_text(<new mp_code text>)
      * text() - mp code text
      * schema_name()
      * document - the mp code QTextDocument
      * syntax_error_line_number - line number of error or 0 for no error

    Signals:
      * signal_mp_code_loaded()
      * signal_syntax_error_line_number_changed()
"""

    # signals
    signal_mp_code_loaded = Signal(name='signalMPCodeLoaded')
    signal_syntax_error_line_number_changed = Signal(
                                   name='signalSyntaxErrroLineNumberChanged')

    def __init__(self, signal_settings_changed, statusbar):
        super().__init__()

        self.statusbar = statusbar
        self.document = QTextDocument()
        self.document.setDocumentLayout(QPlainTextDocumentLayout(self.document))
        self.highlighter = MPCodeHighlighter(self.document,
                                             signal_settings_changed)
        self.syntax_error_line_number = 0

        self.document.contentsChanged.connect(self._run_syntax_check)
        self.old_mp_code_text = ""
        self.syntax_check_signaler = SyntaxCheckSignaller()
        self.syntax_check_signaler.signal_mp_code_syntax_checked.connect(
                                               self._syntax_check_completed)

    def set_text(self, text):
        self.document.setPlainText(text)
        self._run_syntax_check()
        self.signal_mp_code_loaded.emit()

    def text(self):
        return self.document.toPlainText()

    def schema_name(self):
        return self.highlighter.schema_name

    @Slot()
    def _run_syntax_check(self):
        # text
        mp_code_text = self.document.toPlainText()

        # contentsChanged can be triggered when formatting changes
        # so only service change when text changes.
        if mp_code_text == self.old_mp_code_text:
            # done, do not signal syntax report
            return

        self.old_mp_code_text = mp_code_text

        # schema name and mp_code text
        schema_name = self.highlighter.schema_name

        # perform check
        status = mp_check_syntax(schema_name, mp_code_text,
                                 self.syntax_check_signaler.send_signal)

    @Slot(str)
    def _syntax_check_completed(self, status):

        # set the error line number else 0
        self.syntax_error_line_number = _parse_error_line_number(status)
        self.signal_syntax_error_line_number_changed.emit()

        # show status in statusbar
        self.statusbar.showMessage(status)

