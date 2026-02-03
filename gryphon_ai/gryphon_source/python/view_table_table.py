from PySide6.QtCore import QPoint, QRectF, Qt
from PySide6.QtGui import QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from graph_constants import VIEW_TABLE_TYPE
from font_helper import cell_height, text_widths, column_text_widths, \
                        LEFT_PADDING, HORIZONTAL_PADDING
from settings_manager import preferred_pen
from box_menu import show_box_menu

# text looks bad in renderable so we render text in paint

class ViewTableTable(QGraphicsItem):

    def __init__(self, table_box, gry_table_data):
        super().__init__()

        self.table_box = table_box
        self.headers = gry_table_data["headers"]
        self.rows = gry_table_data["rows"]

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
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

        rectangle = QRectF(0, 0, x2, y2)

        # bounds path
        self.bounds_path = QPainterPath()
        self.bounds_path.addRect(rectangle)

        # bounding rectangle
        self.bounding_rectangle = rectangle.adjusted(-1, -1, 1, 1)

        self.reset_appearance()
        self.setParentItem(table_box)

    def reset_appearance(self):
        # pen color
        self.preferred_pen = preferred_pen()

        self.prepareGeometryChange()

    def get_gry(self):
        gry_table_data = {"headers":self.headers,
                          "rows":self.rows,
                          "x":self.x(),
                          "y":self.y(),
                         }
        return gry_table_data

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

        painter.restore()

    def contextMenuEvent(self, event):
        if event.reason() == QGraphicsSceneContextMenuEvent.Reason.Mouse:
            show_box_menu(self.table_box)

