from PySide6.QtCore import QPoint, QRectF, Qt
from PySide6.QtGui import QPainterPath, QColor, QBrush
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from graph_constants import VIEW_TABLE_TYPE
from font_helper import cell_height, text_widths, column_text_widths, \
                        LEFT_PADDING, HORIZONTAL_PADDING
from settings import preferred_pen, settings
from color_helper import highlight_color
from box_menu import show_box_menu
from strip_underscore import strip_underscores, maybe_strip_underscores
from main_graph_undo_redo import track_undo_press, track_undo_release

# text looks bad in renderable so we render text in paint

class ViewTableTable(QGraphicsItem):

    def __init__(self, table_box, gry_table_data):
        super().__init__()
        self.gry_table_data = gry_table_data

        self.table_box = table_box
        self.headers = strip_underscores(gry_table_data["headers"])
        self.rows = maybe_strip_underscores(gry_table_data["rows"])

        # state
        self._is_hovered = False

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(2)

        # widths
        _text_widths = column_text_widths(self.rows)
        _header_widths = text_widths(self.headers)
        self.column_widths = [max(w1, w2) + HORIZONTAL_PADDING
                              for w1, w2 in zip(_text_widths, _header_widths)]
        self.table_width = sum(self.column_widths)

        num_rows = len(self.rows)

        # grid lines
        lines_path = QPainterPath()

        # horizontal grid lines
        x1 = 0
        x2 = self.table_width
        h = cell_height()
        for y in range(0, num_rows + 2): # headers then rows
            lines_path.moveTo(x1, y * h)
            lines_path.lineTo(x2, y * h)

        # vertical grid lines
        x = 0
        y1 = 0
        y2 = h * (num_rows + 1)
        lines_path.moveTo(x, y1)
        lines_path.lineTo(x, y2)
        for w in self.column_widths:
            x += w
            lines_path.moveTo(x, y1)
            lines_path.lineTo(x, y2)

        self.lines_path = lines_path

        self.rectangle = QRectF(0, 0, x2, y2)

        # bounds path
        self.bounds_path = QPainterPath()
        self.bounds_path.addRect(self.rectangle)

        # bounding rectangle
        pen_width = 1
        self.bounding_rectangle = self.rectangle.adjusted(
                    -pen_width/2, -pen_width/2, pen_width/2, pen_width/2)

        self.reset_appearance()
        self.setParentItem(table_box)

    def reset_appearance(self):
        # pen color
        self.preferred_pen = preferred_pen()

        self.prepareGeometryChange()

    def get_gry(self):
        self.gry_table_data["x"] = self.x()
        self.gry_table_data["y"] = self.y()
        return self.gry_table_data

    def type(self):
        return VIEW_TABLE_TYPE

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

        painter.setPen(self.preferred_pen)

        h = cell_height()
        column_widths = self.column_widths

        # lines path
        painter.drawPath(self.lines_path)

        # headers centered
        x = 0
        y = 0
        headers = self.headers
        for i, w in enumerate(column_widths):
            painter.drawText(QRectF(x, y, w, h),
                             Qt.AlignmentFlag.AlignCenter, headers[i])
            x += w

        # rows of text left aligned
        num_rows = len(self.rows)
        num_columns = len(headers)
        p = LEFT_PADDING
        for y, row in enumerate(self.rows, start=1):
            x = 0
            for c, cell in enumerate(row):
                painter.drawText(QRectF(x+p, y*h, column_widths[c], h),
                                 Qt.AlignmentFlag.AlignVCenter, "%s"%cell)
                x += column_widths[c]

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(self.rectangle)

        painter.restore()

    def mousePressEvent(self, event):
        # track potential move
        track_undo_press(self, event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # maybe record move
        track_undo_release(self, "table", event)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()

