from PySide6.QtCore import Slot
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from preferences_manager import preferences
from settings import settings
from mp_code_expressions import ATOMIC_NAME_EXPRESSION, \
               COMMENT_START_EXPRESSION, COMMENT_END_EXPRESSION, \
               SINGLE_LINE_COMMENT_EXPRESSION, \
               MP_KEYWORD_EXPRESSION, MP_META_SYMBOL_EXPRESSION, \
               OPERATOR_EXPRESSION, NUMBER_EXPRESSION, \
               VARIABLE_EXPRESSION, QUOTED_TEXT_EXPRESSION
from mp_code_parser import mp_code_event_dict
from spellcheck import unknown_words_regex

"""
Optimization:
Unfortunately, highlightBlock is called automatically by the QT rich
text engine.  Because highlighted event names are created as the user
types, Qt's automatic calling of highlightBlock is useless.  We disable
automatic highlighting and only enable it during rehighlight() after
we have recalculated event highlighting rules.  We do this using switch
self.highlight_block_is_enabled which we control in the rehighlight
function.
"""

# color is a valid QT color, format is one of "b" for bold or "i" for italic
def _text_char_format(color, style=''):
    """Return a QTextCharFormat with the given attributes."""
    text_char_format = QTextCharFormat()
    text_char_format.setForeground(QColor(color))
    if style == 'b':
        text_char_format.setFontWeight(QFont.Weight.Bold)
    if style == 'i':
        text_char_format.setFontItalic(True)

    return text_char_format

class MPCodeSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for MP Code.

    Manages MP Code syntax highlighting.
    See http://doc.qt.io/qt-5/qtwidgets-richtext-syntaxhighlighter-example.html
    Adapted from https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
    Also ref. https://github.com/baoboa/pyqt5/blob/master/examples/richtext/syntaxhighlighter.py
    """

    def __init__(self, document,
                 signal_preferences_changed, signal_settings_changed,
                 signal_spellcheck_changed):
        super().__init__(document)

        self.document = document

        # highlighting rules for dynamically identified event names
        self.event_highlighting_regexes = list()

        # connect
        signal_preferences_changed.connect(self.rehighlight)
        signal_settings_changed.connect(self._set_colors)
        signal_spellcheck_changed.connect(self.rehighlight)

        # set colors
        self._set_colors()

        # for efficiency suppress Qt's automatic highlighting
        self.highlight_block_is_enabled = False

    # create regexes for events and misspelling and then call super
    def rehighlight(self):
        # enable the highlightBlock function
        self.highlight_block_is_enabled = True

        # MP code text
        mp_code_text = self.document.toPlainText()
        event_dict = mp_code_event_dict(mp_code_text)

        # clear dynamic event highlighting regexes
        self.event_highlighting_regexes.clear()

        # create regexes for dynamically generated events
        self.event_highlighting_regexes.append(("schema",
                      QRegularExpression("\\b%s\\b"%event_dict["schema"])))
        for event_type in ["root", "composite", "atomic"]:
                for event_name in event_dict[event_type]:
                    self.event_highlighting_regexes.append((event_type,
                            QRegularExpression("\\b%s\\b"%event_name)))

        # create the regex for misspelled words
        if preferences["use_spellchecker"]:
            self.misspell_expression = unknown_words_regex(mp_code_text)
 
        # perform the rehighlighting
        super().rehighlight()

        # disable the highlightBlock function
        self.highlight_block_is_enabled = False

    # scan for regex match and set any matches with the given color format
    # for numbers, don't re-format if the preceeding character
    # is a letter or underscore
    def _scan_numbers(self, color_format, text):
        match_iterator = NUMBER_EXPRESSION.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            capStart = match.capturedStart()
            if capStart != 0:
                preceedingChar = text[capStart-1:capStart]
            else:
                preceedingChar = ""
            # dont reformat if,
            # the preceeding character is a letter or underscore
            # or if there is no preceeding character
            ignoreStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
            if ((preceedingChar in ignoreStr) and (preceedingChar != "")):
                pass
            else:
                self.setFormat(match.capturedStart(), match.capturedLength(),
                                                             color_format)

    # scan for regex match and set any matches with the given color format
    def _scan(self, regex, color_format, text):
        match_iterator = regex.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(),
                                                             color_format)

    def _scan_spelling(self, text):
        match_iterator = self.misspell_expression.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()

            # start with existing formatting
            existing_format = self.format(match.capturedStart())
            misspelling_format = QTextCharFormat()
            misspelling_format.setForeground(existing_format.foreground())
            misspelling_format.setFontWeight(existing_format.fontWeight())
            misspelling_format.setFontItalic(existing_format.fontItalic())

            # add underline
            misspelling_format.setUnderlineColor(QColor("red"))
            misspelling_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)

            self.setFormat(match.capturedStart(), match.capturedLength(),
                                      misspelling_format)

    # highlightBlock is called automatically by the QT rich text engine
    def highlightBlock(self, text):

        # events
        for name, regex in self.event_highlighting_regexes:
            if name == "schema":
                self._scan(regex, self.schema_name_format, text)
            elif name == "root":
                self._scan(regex, self.root_name_format, text)
            elif name == "atomic":
                self._scan(regex, self.atomic_name_format, text)
            elif name == "composite":
                self._scan(regex, self.composite_name_format, text)
            else:
                print("Warning: unrecognized name '%s'"%name)

        # keywords
        self._scan(MP_KEYWORD_EXPRESSION, self.keyword_format, text)

        # operators
        self._scan(OPERATOR_EXPRESSION, self.operator_format, text)

        # numbers
        self._scan_numbers(self.number_format, text)

        # variables
        self._scan(VARIABLE_EXPRESSION, self.variable_format, text)

        # meta-symbols
        self._scan(MP_META_SYMBOL_EXPRESSION, self.meta_symbol_format, text)

        # quoted text overrides any previous tokens
        self._scan(QUOTED_TEXT_EXPRESSION, self.quoted_text_format, text)

        # text in multiline comments is based on state of previous block
        # and overrides any previously set highlighting
        self.setCurrentBlockState(0) # 0=not in comment, 1=in comment
        start_index = 0 # start of text block
        if self.previousBlockState() != 1:
            # move start index forward if not in comment
            match = COMMENT_START_EXPRESSION.match(text)
            start_index = match.capturedStart()
        # now process forward from start index
        while start_index >= 0:
            match = COMMENT_END_EXPRESSION.match(text, start_index)
            end_index = match.capturedStart()
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + \
                                                      match.capturedLength()
            self.setFormat(start_index, comment_length, self.comment_format)

            # move to next start expression after current end expression
            match = COMMENT_START_EXPRESSION.match(text, start_index+2)
            start_index = match.capturedStart()

        # single line comment, overriding any previous highlighting
        match_iterator = SINGLE_LINE_COMMENT_EXPRESSION.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start_index = match.capturedStart()
            comment_length = match.capturedLength()
            self.setFormat(start_index, comment_length, self.comment_format)

        # spell check highlighting
        if preferences["use_spellchecker"]:
            self._scan_spelling(text)

    # set all clors
    # whenever color scheme changes recalculate colors
    @Slot()
    def _set_colors(self):
        self.root_name_format = _text_char_format(
                           settings["code_editor_root_color"], "b")
        self.composite_name_format = _text_char_format(
                           settings["code_editor_composite_color"], "b")
        self.schema_name_format = _text_char_format(
                           settings["code_editor_schema_color"], "b")
        self.atomic_name_format = _text_char_format(
                           settings["code_editor_atomic_color"], "b")
        self.comment_format = _text_char_format(
                           settings["code_editor_comment_color"], "i")
        self.keyword_format = _text_char_format(
                           settings["code_editor_keyword_color"], "")
        self.meta_symbol_format = _text_char_format(
                           settings["code_editor_meta_symbol_color"], "b")
        self.operator_format = _text_char_format(
                           settings["code_editor_operator_color"], "")
        self.number_format = _text_char_format(
                           settings["code_editor_number_color"], "")
        self.variable_format = _text_char_format(
                           settings["code_editor_variable_color"], "")
        self.quoted_text_format = _text_char_format(
                           settings["code_editor_quoted_text_color"], "")

        # rehighlight to get new color scheme
        self.rehighlight()

