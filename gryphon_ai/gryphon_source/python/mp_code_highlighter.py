from PySide6.QtCore import Slot
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from settings_manager import settings
from mp_code_dynamic_tokens import dynamic_token_tuples
from mp_code_expressions import ATOMIC_NAME_EXPRESSION, \
               COMMENT_START_EXPRESSION, COMMENT_END_EXPRESSION, \
               SINGLE_LINE_COMMENT_EXPRESSION, \
               KEYWORD_EXPRESSION, META_SYMBOL_EXPRESSION, \
               OPERATOR_EXPRESSION, NUMBER_EXPRESSION, \
               VARIABLE_EXPRESSION, QUOTED_TEXT_EXPRESSION

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

class MPCodeHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for MP Code.

    Manages MP Code syntax highlighting.
    See http://doc.qt.io/qt-5/qtwidgets-richtext-syntaxhighlighter-example.html
    Adapted from https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
    Also ref. https://github.com/baoboa/pyqt5/blob/master/examples/richtext/syntaxhighlighter.py
    """

    def __init__(self, document, signal_settings_changed):
        super(MPCodeHighlighter, self).__init__(document)
        self.document = document
        self.skip_recalculate_names = False

        # highlighting rules
        self.dynamic_highlighting_rules = list()

        # define schema name
        self.schema_name = "SCHEMA not defined"

        # handle document change event
        document.contentsChanged.connect(self.recalculate_names)

        # handle settings change event to get changed colors
        signal_settings_changed.connect(self.set_colors)

        # set colors
        self.set_colors()

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

    # highlightBlock is called automatically by the QT rich text engine
    def highlightBlock(self, text):

        # atomic: start by calling all words atomic events
        self._scan(ATOMIC_NAME_EXPRESSION, self.atomic_name_format, text)

        # composite, root, schema
        for name, regex in self.dynamic_highlighting_rules:
            if name == "root":
                self._scan(regex, self.root_name_format, text)
            elif name == "schema":
                self._scan(regex, self.schema_name_format, text)
            elif name == "composite":
                self._scan(regex, self.composite_name_format, text)
            else:
                print("Warning: unrecognized name '%s'"%name)

        # keywords
        self._scan(KEYWORD_EXPRESSION, self.keyword_format, text)

        # operators
        self._scan(OPERATOR_EXPRESSION, self.operator_format, text)

        # numbers
        self._scan_numbers(self.number_format, text)

        # variables
        self._scan(VARIABLE_EXPRESSION, self.variable_format, text)

        # meta-symbols
        self._scan(META_SYMBOL_EXPRESSION, self.meta_symbol_format, text)

        # quoted text which can override any previous tokens
        self._scan(QUOTED_TEXT_EXPRESSION, self.quoted_text_format, text)

        # now highlight any text in multiline comments
        # set initial state, 0=not in comment, 1=in comment
        self.setCurrentBlockState(0)
        start_index = 0

        # handle multiline comment based on state of previous block,
        # overriding any previously set highlighting
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

        # handle single line comment, overriding any previous highlighting
        match_iterator = SINGLE_LINE_COMMENT_EXPRESSION.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start_index = match.capturedStart()
            comment_length = match.capturedLength()
            self.setFormat(start_index, comment_length, self.comment_format)

    # set all clors
    # whenever color scheme changes recalculate colors
    @Slot()
    def set_colors(self):
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

    # whenever document changes recalculate dynamic names
    # and colors
    @Slot()
    def recalculate_names(self):

        # clear schema name
        self.schema_name = "SCHEMA not defined"

        # clear dynamic rules
        self.dynamic_highlighting_rules.clear()

        # get dynamically generated tokens
        tokens = dynamic_token_tuples(self.document)

        # add dynamic rules
        for token_type, token_name in tokens:
            if token_type == "root":
                self.dynamic_highlighting_rules.append(("root",
                            QRegularExpression("\\b%s\\b"%token_name)))
            elif token_type == "composite":
                self.dynamic_highlighting_rules.append(("composite",
                            QRegularExpression("\\b%s\\b"%token_name)))
            elif token_type == "schema":
                self.dynamic_highlighting_rules.append(("schema",
                            QRegularExpression("\\b%s\\b"%token_name)))

                # track schema name too
                self.schema_name = token_name
            else:
                print("Warning: unrecognized token '%s'" % token_type)

        # prevent recursion
        if self.skip_recalculate_names:
            return

        self.skip_recalculate_names = True

        # rehighlight, this runs highlightBlock on everything
        self.rehighlight()
        self.skip_recalculate_names = False

