"""Highlight text under cursor as follows, even if in comment blocks:
    * (){}: highlight this and its mate.
    * OD, DO, IF, FI words.
    * All other words: highlight in all places in document.
"""

from PySide6.QtCore import QObject
from PySide6.QtCore import Slot
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QBrush
from PySide6.QtGui import QTextCursor
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QTextEdit, QPlainTextEdit
from preferences import preferences
from mp_code_expressions import PAREN_EXPRESSION, BRACE_EXPRESSION, \
                     BRACKET_EXPRESSION, IF_EXPRESSION, DO_EXPRESSION

class MPCodeCursorHighlighter(QObject):
    def __init__(self, mp_code_view):
        super(MPCodeCursorHighlighter, self).__init__()
        self.mp_code_view = mp_code_view
        self.document = mp_code_view.mp_code_manager.document

        # background color
        self.find_background_brush_light = QBrush(QColor("#eaffe6"))# pale green
        self.find_background_brush_dark = QBrush(QColor("#40a52c"))
        self.mate_background_color = QColor("#e4ffe8")
        self.mateless_background_color = QColor("#ffd6cc")

        # connect
        mp_code_view.cursorPositionChanged.connect(self.highlight_extra)
        mp_code_view.textChanged.connect(self.highlight_extra)
        mp_code_view.find_and_replace_dialog_wrapper \
                     .signal_find_and_replace_dialog_showing \
                     .connect(self.highlight_extra)
        mp_code_view.find_and_replace_dialog_wrapper.ui.find_cb \
                     .currentTextChanged.connect(self.highlight_extra_text)

        # any selected word
        self.selected_word = ""

        # the QTextEdit.ExtraSelections objects to highlight
        self.extra_selections = list()

    # add cursor content to extra selection
    def _add_selection(self, cursor, color):
        extra_selection = QTextEdit.ExtraSelection()
        extra_selection.format.setBackground(color)
        extra_selection.cursor = QTextCursor(cursor)
        self.extra_selections.append(extra_selection)

    # highlight mate going forward, cursor captures open_token
    def _highlight_pair_forward(self, expression, cursor):
        open_token = cursor.selectedText()
        if open_token == "(":
            close_token = ")"
        elif open_token == "{":
            close_token = "}"
        elif open_token == "[":
            close_token = "]"
        elif open_token == "IF":
            close_token = "FI"
        elif open_token == "DO":
            close_token = "OD"
        else:
            print("internal error highlight pair forward at %d: '%s'"%(
                                         cursor.position(), open_token))
            raise Exception("Bad")

        # highlight open token
        self._add_selection(cursor, self.mate_background_color)

        # remember open token cursor in case mate cannot be found
        open_token_cursor = QTextCursor(cursor)

        # clear selection since movePosition fails when there is a selection
        cursor.clearSelection()

        # find and highlight close token
        count = 1
        while True:


            # search forward to find mate
            cursor = self.document.find(expression, cursor)

            if not cursor.selectedText():
                # None so open token has no mate
                self._add_selection(open_token_cursor,
                                    self.mateless_background_color)
                break
            if cursor.selectedText() == open_token:
                count += 1
                continue
            if cursor.selectedText() == close_token:
                count -= 1
                if count == 0:
                    # at mate so add highlight
                    self._add_selection(cursor, self.mate_background_color)
                    break

    # highlight mate going backward, cursor captures close_token
    def _highlight_pair_backward(self, expression, cursor):
        close_token = cursor.selectedText()
        if close_token == ")":
            open_token = "("
        elif close_token == "}":
            open_token = "{"
        elif close_token == "]":
            open_token = "["
        elif close_token == "FI":
            open_token = "IF"
        elif close_token == "OD":
            open_token = "DO"
        else:
            print("internal error highlight pair backward at %d: '%s'"%(
                                         cursor.position(), close_token))
            raise Exception("Bad")

        # highlight close token
        self._add_selection(cursor, self.mate_background_color)

        # remember open token cursor in case mate cannot be found
        close_token_cursor = QTextCursor(cursor)

        # clear selection since movePosition fails when there is a selection
        cursor.clearSelection()

        # back up to behind this token
        cursor = self.document.find(expression, cursor,
                                    QTextDocument.FindBackward)

        # find and highlight open token
        count = 1
        while True:

            # search backward to find mate
            cursor = self.document.find(expression, cursor,
                                        QTextDocument.FindBackward)

            if not cursor.selectedText():
                # None so close token has no mate
                self._add_selection(close_token_cursor,
                                    self.mateless_background_color)
                break
            if cursor.selectedText() == close_token:
                count += 1
                continue
            if cursor.selectedText() == open_token:
                count -= 1
                if count == 0:
                    # at mate so add highlight
                    self._add_selection(cursor, self.mate_background_color)
                    break

    # highlight pair
    def _highlight_pair(self):
        # get the character the cursor is over
        cursor = self.mp_code_view.textCursor()

        # do not highlight if user selects a range
        if cursor.position() != cursor.anchor():
            return

        char = self.document.characterAt(cursor.position())

        # (
        if char == "(":
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter,
                                QTextCursor.MoveMode.KeepAnchor)
            self._highlight_pair_forward(PAREN_EXPRESSION, cursor)

        # {
        elif char == "{":
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter,
                                QTextCursor.MoveMode.KeepAnchor)
            self._highlight_pair_forward(BRACE_EXPRESSION, cursor)

        elif char == "[":
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter,
                                QTextCursor.MoveMode.KeepAnchor)
            self._highlight_pair_forward(BRACKET_EXPRESSION, cursor)

        # )
        elif char == ")":
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter,
                                QTextCursor.MoveMode.KeepAnchor)
            self._highlight_pair_backward(PAREN_EXPRESSION, cursor)

        # }
        elif char == "}":
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter,
                                QTextCursor.MoveMode.KeepAnchor)
            self._highlight_pair_backward(BRACE_EXPRESSION, cursor)

        # ]
        elif char == "]":
            cursor.movePosition(QTextCursor.MoveOperation.NextCharacter,
                                QTextCursor.MoveMode.KeepAnchor)
            self._highlight_pair_backward(BRACKET_EXPRESSION, cursor)

        # evaluate word
        else:

            # get word
            cursor.movePosition(QTextCursor.MoveOperation.StartOfWord)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfWord,
                                QTextCursor.MoveMode.KeepAnchor)
            word = cursor.selectedText()

            # IF, FI, DO, OD
            if word == "IF":
                self._highlight_pair_forward(IF_EXPRESSION, cursor)
            elif word == "FI":
                self._highlight_pair_backward(IF_EXPRESSION, cursor)
            elif word == "DO":
                self._highlight_pair_forward(DO_EXPRESSION, cursor)
            elif word == "OD":
                self._highlight_pair_backward(DO_EXPRESSION, cursor)
            else:
                # not an IF or DO block
                pass

    def _highlight_extra_text(self, text, color):
        # scan document for matches
        selected_text_expression = QRegularExpression(text)
        cursor = QTextCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        while True:
            cursor = self.document.find(selected_text_expression, cursor)
            if not cursor.selectedText():
                break
            self._add_selection(cursor, color)

    # set background and foreground for "selected" text and for "find" text
    def _highlight_text_2(self, text, background_brush, foreground_brush):
        # scan document for matches
        selected_text_expression = QRegularExpression(text)
        cursor = QTextCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        while True:
            cursor = self.document.find(selected_text_expression, cursor)
            if not cursor.selectedText():
                break

            # add the "selected" or "find" text
            extra_selection = QTextEdit.ExtraSelection()
            extra_selection.format.setBackground(background_brush)
            extra_selection.format.setForeground(foreground_brush)
            extra_selection.cursor = QTextCursor(cursor)
            self.extra_selections.append(extra_selection)

    # highlight open token, close token pair and anything matching selected_word
    @Slot()
    def highlight_extra(self):

        self.extra_selections.clear()

        # highlight any selected text
        selected_text = self.mp_code_view.textCursor().selectedText()
        if selected_text and not selected_text.isspace():
            self._highlight_text_2(selected_text,
                                   QPlainTextEdit().palette().highlight(),
                                   QPlainTextEdit().palette().highlightedText())

        # highlight any find text for find-and-replace
        if self.mp_code_view.find_and_replace_dialog_wrapper.isVisible():
            find_text = self.mp_code_view.find_and_replace_dialog_wrapper \
                                                   .ui.find_cb.currentText()
            if find_text and not find_text.isspace():
                if preferences["use_dark_mode"]:
                    background_brush = self.find_background_brush_dark
                    foreground_brush = QBrush(QColor("white"))
                else:
                    background_brush = self.find_background_brush_light
                    foreground_brush = QBrush(QColor("black"))
                self._highlight_text_2(find_text,
                                       background_brush, foreground_brush)

        # highlight any pair if cursor is over a pairable token
        self._highlight_pair()

        # now put these extra selections into the view
        self.mp_code_view.setExtraSelections(self.extra_selections)

    @Slot(str)
    def highlight_extra_text(self, _text):
        self.highlight_extra()

