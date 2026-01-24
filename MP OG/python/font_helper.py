"""In text, point (0, 0) is near the lower left part of the first character.
So we paint aligned text inside rectangular areas."""
from PySide6.QtGui import QFontMetrics, QFont, QTextOption, QPainter
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QImage

_TEXT_OPTION = QTextOption()
_TEXT_OPTION.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
_TEXT_OPTION.setAlignment(Qt.AlignCenter)

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

# necessary height given a constrained text width
def margined_text_height(text, constrained_width):
    # we use painter.boundingRect because QFontMetrics.boundingRect does
    # not support QTextOption which provides WrapAtWordBoundaryOrAnywhere.
    image = QImage(1, 1, QImage.Format_RGB32)
    painter = QPainter(image)
    constrained_rect = QRectF(0, 0, constrained_width - HORIZONTAL_PADDING, 800)
    rect = painter.boundingRect(constrained_rect, text, _TEXT_OPTION)
    painter.end()
    return rect.height()

# draw text with margin allowance inside the box
def paint_margined_text(painter, box, text):
    constrained_rect = box.adjusted(LEFT_PADDING, -400, -LEFT_PADDING, 400)
    painter.drawText(constrained_rect, text, _TEXT_OPTION)

# text width and height given a specific width constraint, wrapping at
# word boundaries only, no wrapping within words
def bound_text_width_and_height(text, max_width):
    fm = QFontMetrics(QFont())
    rect = fm.boundingRect(0, 0, max_width, 800,
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

