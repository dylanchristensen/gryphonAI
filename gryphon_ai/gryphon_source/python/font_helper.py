"""In text, point (0, 0) is near the lower left part of the first character.
So we paint aligned text inside rectangular areas."""
from PySide6.QtGui import QFontMetrics, QFont
from PySide6.QtCore import Qt

# use default font since we may not have access to the widget's font
# accepts string or numeric cell data


LEFT_PADDING = 4
HORIZONTAL_PADDING = 2 * LEFT_PADDING

# width of text
def text_width(text):
    fm = QFontMetrics(QFont())
    w = fm.horizontalAdvance("%s"%text)
    return w

# widths of text in a list
def text_widths(text_list):
    fm = QFontMetrics(QFont())
    return [fm.horizontalAdvance("%s"%text) for text in text_list]

# widest text in list
def widest_text(text_list):
    fm = QFontMetrics(QFont())
    return max([fm.horizontalAdvance("%s"%text) for text in text_list])

# list of column widths from rows of columns of text
def column_text_widths(list_of_rows):
    fm = QFontMetrics(QFont())

    # list of column widths
    if list_of_rows:
        widths = [0] * len(list_of_rows[0])
        for r, row in enumerate(list_of_rows):
            for c in range(len(row)):
                widths[c] = max(widths[c],
                            fm.horizontalAdvance("%s"%list_of_rows[r][c]))
    else:
        widths = []
    return widths

# text height given a left and right margin constraint
def bound_text_height(text, max_width):
    fm = QFontMetrics(QFont())
    return fm.boundingRect(0, 0, max_width, 500,
                           Qt.TextFlag.TextWordWrap, text).height()

# text width and height given a left and right margin constraint
def bound_text_width_and_height(text, max_width):
    fm = QFontMetrics(QFont())
    rect = fm.boundingRect(0, 0, max_width, 500,
                           Qt.TextFlag.TextWordWrap, text)
    return rect.width(), rect.height()

def cell_height():
    fm = QFontMetrics(QFont())
    h = int(fm.height() * 1.2)
    return h

def font_height():
    fm = QFontMetrics(QFont())
    return int(fm.height())

def font_descent():
    fm = QFontMetrics(QFont())
    return int(fm.descent())

