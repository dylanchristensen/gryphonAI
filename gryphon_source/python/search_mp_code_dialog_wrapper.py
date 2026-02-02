# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtCore import QRect
from PySide6.QtCore import QSize
from PySide6.QtGui import QTextDocument
from PySide6.QtGui import QTextOption, QFont, QPainter
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QDialog, QAbstractItemView, QPlainTextEdit
from PySide6.QtWidgets import QPlainTextDocumentLayout
from mp_code_syntax_highlighter import MPCodeSyntaxHighlighter
from search_mp_code_dialog import Ui_SearchMPCodeDialog
from preferences import preferences
from settings import settings

# private support for SearchMPCodeView, this is a duplicate of mp_code_view.py
class SecondLineNumberArea(QWidget):
    def __init__(self, mp_code_view):
        super().__init__(mp_code_view)
        self.mp_code_view = mp_code_view

    def sizeHint(self):
        return QSize(self.mp_code_view.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.mp_code_view.lineNumberAreaPaintEvent(event)

class SearchMPCodeView(QPlainTextEdit):

    def __init__(self, parent, signal_preferences_changed):
        super().__init__(parent)

        # connect
        signal_preferences_changed.connect(self._set_preferences)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)

        self.line_number_area = SecondLineNumberArea(self)
        self.updateLineNumberAreaWidth(0)
        self._set_preferences()
        self.setReadOnly(True)

        # monospace
        # https://stackoverflow.com/questions/13027091/how-to-override-tab-width-in-qt
        font = QFont()
        font.setFamily("Monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)

    def line_number_area_width(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().maxWidth() * digits
        return space

    @Slot(int)
    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    @Slot(QRect, int)
    def updateLineNumberArea(self, rect, dy):

        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                         self.line_number_area.width(),
                                         rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                                          self.line_number_area_width(),
                                          cr.height()))

    # similar to mp_code_view but without background error color
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)

        # line number area background color based on using dark mode
        if self.use_dark_mode:
            background_color = Qt.GlobalColor.darkGray
        else:
            background_color = Qt.GlobalColor.lightGray
        painter.fillRect(event.rect(), background_color)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
                                            self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # paint the visible line numbers
        width = self.line_number_area.width()
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                row_rectangle = QRect(0, top, width, height)

                line_number_string = str(block_number + 1)
                painter.drawText(row_rectangle, Qt.AlignmentFlag.AlignRight,
                                 line_number_string)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    @Slot()
    def _set_preferences(self):
        # wrap mode
        wrap_mode = preferences["wrap_mode"]
        if wrap_mode == "no_wrap":
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
            self.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        elif wrap_mode == "wrap_at_edge":
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            self.setWordWrapMode(QTextOption.WrapMode.WrapAnywhere)
        elif wrap_mode == "wrap_at_word":
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            self.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        else:
            raise RuntimeError("bad")

        # dark mode
        self.use_dark_mode = preferences["use_dark_mode"]

class SearchMPCodeManager(QObject):
    def __init__(self, document, mp_code_text,
                 signal_preferences_changed, signal_settings_changed,
                 signal_spellcheck_changed):
        super().__init__()
        self.document = document
        self.highlighter = MPCodeSyntaxHighlighter(document,
                                                   signal_preferences_changed,
                                                   signal_settings_changed,
                                                   signal_spellcheck_changed)
        self._set_text(mp_code_text)

    # set text
    def _set_text(self, mp_code_text):
        self.document.setPlainText(mp_code_text)
        self.highlighter.rehighlight()
 
class SearchMPCodeDialogWrapper(QDialog):

    def __init__(self, parent_window,
                 signal_preferences_changed, signal_settings_changed,
                 signal_spellcheck_changed,
                 posix_path, mp_code_text):
        super().__init__(parent_window)
        self.ui = Ui_SearchMPCodeDialog()
        self.ui.setupUi(self) # we refine this further below
        self.ui.copy_pb.setDisabled(True)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
        self.setWindowTitle("Search %s"%posix_path.name)

        # the QPlainTextEdit view
        self.search_mp_code_view = SearchMPCodeView(
                     self.ui.verticalLayoutWidget, # Qt Designer assigned name
                     signal_preferences_changed)
        self.ui.layout.addWidget(self.search_mp_code_view)

        # the search mp code manager
        search_mp_code_manager = SearchMPCodeManager(
                                    self.search_mp_code_view.document(),
                                    mp_code_text,
                                    signal_preferences_changed,
                                    signal_settings_changed,
                                    signal_spellcheck_changed)

        # connect buttons
        self.ui.copy_pb.clicked.connect(self.search_mp_code_view.copy)
        self.ui.close_pb.clicked.connect(self.close) # superclass close
        self.search_mp_code_view.copyAvailable.connect(self._copy_available)

    # copy available
    @Slot(bool)
    def _copy_available(self, copy_is_available):
        self.ui.copy_pb.setDisabled(not copy_is_available)

