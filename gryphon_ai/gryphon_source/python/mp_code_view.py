# Adapted from:
# https://stackoverflow.com/questions/33243852/codeeditor-example-in-pyqt
# http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html

from os.path import join, split
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QCompleter
from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QAction
from PySide6.QtGui import QFont
from PySide6.QtGui import QFontMetrics
from PySide6.QtGui import QColor
from PySide6.QtGui import QTextCursor
from PySide6.QtGui import QPainter
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QTextOption
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtCore import QRect
from PySide6.QtCore import Slot
from PySide6.QtCore import QStringListModel
from mp_code_cursor_highlighter import MPCodeCursorHighlighter
from os_compatibility import control_modifier
from mp_code_expressions import KEYWORD_SET, WORD_EXPRESSION, \
                                LEADING_WHITESPACE_EXPRESSION
from find_and_replace_dialog_wrapper import FindAndReplaceDialogWrapper
from mp_json_io_manager import save_mp_code_file
from preferences_manager import preferences
from message_popup import message_popup
from mp_logger import log

# the set of words and the number of words
def words(text):
    word_set = set()
    word_count = 0
    match_iterator = WORD_EXPRESSION.globalMatch(text)
    while match_iterator.hasNext():
        word_set.add(match_iterator.next().captured()) # QRegularExpressionMatch
        word_count += 1
    return word_set, word_count

# private support for MPCodeView
class LineNumberArea(QWidget):
    def __init__(self, mp_code_view):
        super(LineNumberArea, self).__init__(mp_code_view)
        self.mp_code_view = mp_code_view

    def sizeHint(self):
        return QSize(self.mp_code_view.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.mp_code_view.line_number_area_paint_event(event)

class MPCodeView(QPlainTextEdit):

    # Help reduce effect of jump bug where Qt scrolls to cursor the
    # first time the first MPCodeView loses focus.
    # A fix would be prefereable.  This may be a Qt bug.
    @Slot()
    def _move_cursor_to_top(self):
        self.moveCursor(QTextCursor.MoveOperation.Start)

    def __init__(self, mp_code_manager, preferences_manager,
                 action_search_mp_files, instance_number):
        super().__init__()

        # the mp code
        self.mp_code_manager = mp_code_manager
        self.instance_number = instance_number
        self.setDocument(self.mp_code_manager.document)

        # the find and replace dialog wrapper
        self.find_and_replace_dialog_wrapper \
                                      = FindAndReplaceDialogWrapper(self)

        # line number area
        self.line_number_area = LineNumberArea(self)

        # connect
        mp_code_manager.signal_mp_code_loaded.connect(self._move_cursor_to_top)
        mp_code_manager.signal_syntax_error_line_number_changed.connect(
                                             self.line_number_area.update)
        preferences_manager.signal_wrap_mode_changed.connect(self.set_wrap_mode)
        preferences_manager.signal_use_auto_indent_changed.connect(
                                      self.set_use_auto_indent)
        preferences_manager.signal_use_dark_mode_changed.connect(
                                      self.set_use_dark_mode)

        # action find and replace
        self.action_find_and_replace = QAction(
                    QIcon(":/icons/find_and_replace"),
                    "&Find and replace (screen %d)..."%self.instance_number)
        self.action_find_and_replace.setStatusTip(
                            "Find and replace text in the code editor pane")
        self.action_find_and_replace.triggered.connect(
                               self.find_and_replace_dialog_wrapper.show)

        # action search MP files
        self.action_search_mp_files = action_search_mp_files
        self.action_save_selection = QAction(QIcon(":/icons/save"),
                                                "&Save selection...", self)
        self.action_save_selection.triggered.connect(self._save_selection)


        # the cursor highlighter manages cursor highlighting on mouse click
        self.mp_code_cursor_highlighter = MPCodeCursorHighlighter(self)

        # the word list model provides the list model for MP Code keywords
        self.mp_code_string_list_model = QStringListModel()

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)

        self.update_line_number_area_width(0)
        self.set_wrap_mode(preferences_manager.wrap_mode())
        self.set_use_auto_indent(preferences_manager.use_auto_indent())
        self.set_use_dark_mode(preferences_manager.use_dark_mode())

        # monospace
        # https://stackoverflow.com/questions/13027091/how-to-override-tab-width-in-qt
        font = QFont()
        font.setFamily("Monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)

        # tab stop
        tab_stop = 4
        metrics = QFontMetrics(font)
        self.setTabStopDistance(metrics.horizontalAdvance(' ') * tab_stop)

        # background at line number of syntax error
        self.syntax_error_color = QColor("#cc0000")

        # code completer
        self.completer = QCompleter(self.mp_code_string_list_model, None)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(
                               QCompleter.CompletionMode.PopupCompletion)
        self.completer.activated.connect(self.insert_completion_text)

    # save selection
    @Slot()
    def _save_selection(self):

        # suggested filename
        suggested_filename = "selection.mp"

        mp_code_filename, _ = QFileDialog.getSaveFileName(None,
                      "Save MP Code selection",
                      join(preferences[
                      "preferred_save_selection_dir"],
                      suggested_filename),
                      "MP Code files (*.mp);;All Files (*)",
                      options = QFileDialog.Option.DontUseNativeDialog)

        if mp_code_filename:
            # remember the preferred path
            head, _tail = split(mp_code_filename)
            preferences["preferred_save_selection_dir"] = head

            # get the selection
            selected_text = self.textCursor().selectedText()
            status = save_mp_code_file(selected_text, mp_code_filename)
            print("Saved selection to", mp_code_filename)
            if status:
                # log failure
                log(status)
                message_popup(None, status)
            else:
                # great, exported.
                log("Selection saved as %s"%mp_code_filename)

    # standard menu plus custom items
    def contextMenuEvent(self, context_menu_event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction(self.action_find_and_replace)
        self.action_find_and_replace.setDisabled(
                   FindAndReplaceDialogWrapper.a_wrapper_instance_is_visible)
        menu.addAction(self.action_search_mp_files)
        menu.addAction(self.action_save_selection)
        self.action_save_selection.setDisabled(
                                      not self.textCursor().hasSelection())
        menu.exec_(context_menu_event.globalPos())
        del menu

    @Slot(str)
    def set_wrap_mode(self, wrap_mode):
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

    @Slot(bool)
    def set_use_auto_indent(self, use_auto_indent):
        self.use_auto_indent = use_auto_indent

    @Slot(bool)
    def set_use_dark_mode(self, use_dark_mode):
        self.use_dark_mode = use_dark_mode

    # insert the right portion of the completion text at the end of the cursor
    @Slot(str)
    def insert_completion_text(self, completion_text):
        tc = self.textCursor()
        extra = (len(completion_text) - len(self.completer.completionPrefix()))
        tc.movePosition(QTextCursor.MoveOperation.Left)
        tc.movePosition(QTextCursor.MoveOperation.EndOfWord)
        tc.insertText(completion_text[-extra:])
        self.setTextCursor(tc)

    # list of words to suggest for look-ahead typing
    def _suggested_word_list(self):

        # get word at cursor
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfWord)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfWord,
                            QTextCursor.MoveMode.KeepAnchor)
        word_at_cursor = cursor.selectedText()

        # get all words in document
        word_set, _word_count = words(self.mp_code_manager.text())

        # remove the word at cursor
        word_set.discard(word_at_cursor)

        # add keywords to set
        word_set.update(KEYWORD_SET)

        # put words into case-insensitive sorted word list
        suggested_word_list = list(word_set)
        suggested_word_list.sort(key=str.lower)
        return suggested_word_list

    def _add_auto_indent(self):
        previous_block_text = self.textCursor().block().previous().text()
        if previous_block_text:
            previous_whitespace = LEADING_WHITESPACE_EXPRESSION.match(
                                            previous_block_text).captured()
            if previous_whitespace:
                self.insertPlainText(previous_whitespace)

    # intercept keyPress to work with completer
    @Slot(QKeyEvent)
    def keyPressEvent(self, e):

        # disregard these keystrokes if the completer popup is active
        if self.completer.popup().isVisible():
            if e.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return,
                           Qt.Key.Key_Escape, Qt.Key.Key_Tab,
                           Qt.Key.Key_Backtab):
                e.ignore()
                return

        # recognize the CTRL-Spacebar shortcut
        is_shortcut = (e.modifiers() == control_modifier()) and \
                                                 e.key() == Qt.Key.Key_Space

        # forward all but the CTRL-Spacebar shortcut to superclass
        if not is_shortcut:
            super(MPCodeView, self).keyPressEvent(e)

        # auto-indent if auto-indent is enabled and key is enter
        if self.use_auto_indent and e.key() in (Qt.Key.Key_Enter,
                                                Qt.Key.Key_Return):
            self._add_auto_indent()

        # recognize CTRL or SHIFT
        ctrl_or_shift = e.modifiers() & (control_modifier()
                                         | Qt.KeyboardModifier.ShiftModifier)

        # disregard CTRL or SHIFT without character
#        if ctrl_or_shift and not e.text():
        if ctrl_or_shift and e.key() > 255: # modifier codes are above ASCII
            return

        # recognize non-ctrl_or_shift modifier
        has_modifier = e.modifiers() != Qt.KeyboardModifier.NoModifier \
                               and not ctrl_or_shift

        # require cursor to be at the end of word and without range selection
        cursor = self.textCursor()
        position = cursor.position()
        anchor = cursor.anchor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word_end_position = cursor.position()
        word_end_anchor = cursor.anchor()
        at_end_of_word = position == anchor and position == word_end_position \
                         and word_end_position != word_end_anchor
        if not at_end_of_word:
            self.completer.popup().hide()
            return

        # find user's completion text prefix
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        completion_prefix = cursor.selectedText()

        # recognize an invalid keystroke
        text = e.text()
        is_invalid_key = not text.isalnum() and text != "_"

        # abort completer under these conditions:
        if not is_shortcut:
            if has_modifier or not text or len(completion_prefix) < 3 or \
                                                        is_invalid_key:
                self.completer.popup().hide()
                return

        # set the completion text prefix
        self.completer.setCompletionPrefix(completion_prefix)
        suggested_word_list = self._suggested_word_list()

        # update the word list model
        self.mp_code_string_list_model.setStringList(suggested_word_list)

        # set pop-up view to top
        self.completer.popup().setCurrentIndex(
                            self.completer.completionModel().index(0, 0))

        # configure and open popup
        cursor_rectangle = self.cursorRect()
        cursor_rectangle.setWidth(self.completer.popup().sizeHintForColumn(0)
             + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursor_rectangle)

    # intercept mouse press for cursor highlighting
    @Slot(str)
    def mousePressEvent(self, event):
        super(MPCodeView, self).mousePressEvent(event)
        self.mp_code_cursor_highlighter.highlight_selection()

    def line_number_area_width(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    @Slot(int)
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    @Slot(QRect, int)
    def update_line_number_area(self, rect, dy):

        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                         self.line_number_area.width(),
                                         rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)


    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(),
                                          self.line_number_area_width(),
                                          cr.height()))

    def line_number_area_paint_event(self, event):
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
                row_rectangle = QRect(0, int(top), width, height)

                # set background for error line number
                if block_number+1 == \
                             self.mp_code_manager.syntax_error_line_number:
                    painter.fillRect(row_rectangle, self.syntax_error_color)

                line_number_string = str(block_number + 1)
                painter.drawText(row_rectangle, Qt.AlignmentFlag.AlignRight,
                                 line_number_string)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

