from PySide6.QtGui import QRadialGradient, QLinearGradient
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from settings import settings
from font_helper import font_height, text_width

def paint_background(painter, fill_rect):
    gradient = QLinearGradient(fill_rect.topLeft(),
                               fill_rect.bottomRight())
    c = QColor(settings["background_color"])
    gradient.setColorAt(0, c.lighter(settings["background_color_gradient"]))
    gradient.setColorAt(0.5, c)
    gradient.setColorAt(1, c.darker(settings["background_color_gradient"]))
    painter.fillRect(fill_rect, QBrush(gradient))

def mark_flag(graph_item):
    if "trace" in graph_item.gry_graph:
        mark = graph_item.gry_graph["trace"]["mark"]
    else:
        mark = None
    return mark

def _paint_mark(painter, mark, x):
    # move painter to center of mark near top-right corner
    painter.save()

    # get color based on mark
    if mark == "M":
        c1 = Qt.GlobalColor.red
        c2 = Qt.GlobalColor.darkRed
    else:
        # mark not recognized
        c1 = Qt.GlobalColor.gray
        c2 = Qt.GlobalColor.darkGray

    # draw circle
    painter.translate(x - 12, 12)
    gradient = QRadialGradient(-3, -3, 10)
    gradient.setColorAt(0, c1)
    gradient.setColorAt(1, c2)
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(-7, -7, 14, 14)
    painter.restore()

def paint_header(painter, graph_index, left_text, right_text, mark, width):
    y = font_height()
    if graph_index == 0:
        # paint the global view title
        painter.drawText(5, y, left_text)

    else:
        # paint the left text
        painter.drawText(5, y, left_text)

        # paint right text and any mark
        x = int(width) - 5
        if mark == "U":
            # no mark
            painter.drawText(x - text_width(right_text), y, right_text)
        else:
            painter.drawText(x - text_width(right_text) - 30, y, right_text)
            _paint_mark(painter, mark, x)

