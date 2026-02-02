from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QPainterPath, QColor, QBrush, QPen
from PySide6.QtWidgets import QGraphicsItem
from graph_constants import VIEW_LEGEND_TYPE
from font_helper import text_widths, cell_height, font_height, \
                        LEFT_PADDING, font_descent
from color_helper import highlight_color
from settings import settings, preferred_pen
from strip_underscore import strip_underscores
from main_graph_undo_redo import track_undo_press, track_undo_release

# text looks bad in renderable so we render text in paint

# brush corresponding to color i
# Could put in dict and refresh dict when settings change but don't optimize.
def brush(i):
    i = i%8 # make this match number of colors offered in settings
    if i == 0:
        color = settings["bar_chart_bar_color1"]
    elif i == 1:
        color = settings["bar_chart_bar_color2"]
    elif i == 2:
        color = settings["bar_chart_bar_color3"]
    elif i == 3:
        color = settings["bar_chart_bar_color4"]
    elif i == 4:
        color = settings["bar_chart_bar_color5"]
    elif i == 5:
        color = settings["bar_chart_bar_color6"]
    elif i == 6:
        color = settings["bar_chart_bar_color7"]
    elif i == 7:
        color = settings["bar_chart_bar_color8"]
    else:
        raise RuntimeError("bad")
    return QBrush(QColor(color))

class ViewLegend(QGraphicsItem):

    def __init__(self, view_box, gry_legend):
        super().__init__()
        self.gry_legend = gry_legend

        self.view_box = view_box
        self.names = strip_underscores(gry_legend["names"])
        if "x" in gry_legend:
            self.setPos(QPointF(gry_legend["x"], gry_legend["y"]))

        # state
        self._is_hovered = False

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(2)

        # widest text
        self.max_text_width = max(text_widths(self.names))

        # bounds path
        self.bounds_path = QPainterPath()
        rectangle = QRectF(0, 0,
                           self.max_text_width + LEFT_PADDING + cell_height(),
                           len(self.names) * cell_height()
                           - (cell_height() - font_height()))
        self.bounds_path.addRect(rectangle)

        # bounding rectangle
        pen_width = 1
        self.bounding_rectangle = rectangle.adjusted(
                      -pen_width/2, -pen_width/2, pen_width/2, pen_width/2)

        self.reset_appearance()
        self.setParentItem(view_box)

    def reset_appearance(self):

        # pen color
        self.preferred_pen = preferred_pen()

        self.prepareGeometryChange()

    def get_gry(self):
        self.gry_legend["x"] = self.x()
        self.gry_legend["y"] = self.y()
        return self.gry_legend

    def type(self):
        return VIEW_LEGEND_TYPE

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounding_rectangle

    # mouse hovers when inside this rectangle
    def shape(self):
        return self.bounds_path

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super().itemChange(change, value)

    def paint(self, painter, _option, _widget):

        painter.save()

        if self._is_hovered:
            # highlight
            color = highlight_color(QColor(settings["background_color"]))
            painter.fillRect(self.bounding_rectangle, color)

        row_height = cell_height()
        box_size = font_height()
        w = self.max_text_width
        box_x = 0
        text_x = box_x + box_size + 2 * LEFT_PADDING

        # legend box and text
        box_pen = QPen(self.preferred_pen.color(), 0)
        for i, name in enumerate(self.names):
            cell_y = row_height * i

            # legend box
            painter.setPen(box_pen)
            painter.setBrush(brush(i))
            painter.drawRect(box_x, cell_y, box_size, box_size)

            # text
            painter.setPen(self.preferred_pen)
            painter.drawText(text_x, cell_y + box_size - font_descent(), name)

        # selection border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(self.bounding_rectangle)

        painter.restore()

    def mousePressEvent(self, event):
        # track potential move
        track_undo_press(self, event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # maybe record move
        track_undo_release(self, "legend", event)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()

