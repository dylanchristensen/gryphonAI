"""Highlight text under cursor as follows, even if in comment blocks:
    * (){}: highlight this and its mate.
    * OD, DO, IF, FI words.
    * All other words: highlight in all places in document.
"""

from PySide6.QtCore import QObject
from PySide6.QtCore import Slot
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor
from PySide6.QtGui import QTextCursor
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QTextEdit
from mp_code_expressions import PAREN_EXPRESSION, BRACE_EXPRESSION, \
                     BRACKET_EXPRESSION, IF_EXPRESSION, DO_EXPRESSION

class MPCodeCursorHighlighter(QObject):
    def __init__(self, mp_code_view):
        super(MPCodeCursorHighlighter, self).__init__()
        self.mp_code_view = mp_code_view
        self.document = mp_code_view.mp_code_manager.document

        # background color
        self.word_background_color = QColor("#e4ffe8")
        self.mate_background_color = self.word_background_color.darker(110)
        self.mateless_background_color = QColor("#ffd6cc")

        # connect
        mp_code_view.cursorPositionChanged.connect(self.highlight_extra)
        mp_code_view.textChanged.connect(self.highlight_extra)

        # any selected word
        self.selected_word = ""

        # the QTextEdit.ExtraSelections objects to highlight
        self.extra_selections = list()

    # add pair type ExtraSelection
    def _add_mate_selection(self, cursor):
        extra_selection = QTextEdit.ExtraSelection()
        extra_selection.format.setBackground(self.mate_background_color)
        extra_selection.cursor = QTextCursor(cursor)
        self.extra_selections.append(extra_selection)

    # add mateless pair type ExtraSelection
    def _add_mateless_selection(self, cursor):
        extra_selection = QTextEdit.ExtraSelection()
        extra_selection.format.setBackground(self.mateless_background_color)
        extra_selection.cursor = QTextCursor(cursor)
        self.extra_selections.append(extra_selection)

    # add word type ExtraSelection
    def _add_word_selection(self, cursor):
        extra_selection = QTextEdit.ExtraSelection()
        extra_selection.format.setBackground(self.word_background_color)
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
        self._add_mate_selection(cursor)

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
                self._add_mateless_selection(open_token_cursor)
                break
            if cursor.selectedText() == open_token:
                count += 1
                continue
            if cursor.selectedText() == close_token:
                count -= 1
                if count == 0:
                    # at mate so add highlight
                    self._add_mate_selection(cursor)
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
        self._add_mate_selection(cursor)

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
                self._add_mateless_selection(close_token_cursor)
                break
            if cursor.selectedText() == close_token:
                count += 1
                continue
            if cursor.selectedText() == open_token:
                count -= 1
                if count == 0:
                    # at mate so add highlight
                    self._add_mate_selection(cursor)
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

    # highlight open token, close token pair and anything matching selected_word
    @Slot()
    def highlight_extra(self):

        self.extra_selections.clear()

        # highlight any selected word
        if self.selected_word:
            word_expression = QRegularExpression("\\b%s\\b"%self.selected_word)

            # find word starting at the beginning
            cursor = QTextCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)

            while True:
                cursor = self.document.find(word_expression, cursor)
                if not cursor.selectedText():
                    break
                self._add_word_selection(cursor)

        # highlight any pair if cursor is on a pair side
        self._highlight_pair()

        # now apply the extra selections
        self.mp_code_view.setExtraSelections(self.extra_selections)

    # arrive here from mouse press from text edit
    def highlight_selection(self):

        # get word
        cursor = self.mp_code_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfWord)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfWord,
                            QTextCursor.MoveMode.KeepAnchor)
        self.selected_word = cursor.selectedText()

        # disallow word if it starts with potential regex control codes
        if self.selected_word and self.selected_word[0] != "_" and \
                                      not self.selected_word[0].isalnum():
            self.selected_word = ""

        # now that the selected word is defined call higlight extra
        self.highlight_extra()

