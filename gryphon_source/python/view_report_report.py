from PySide6.QtCore import QPoint, QRectF, Qt
from PySide6.QtGui import QPainterPath, QColor, QBrush
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from graph_constants import VIEW_REPORT_TYPE
from font_helper import text_width, widest_text, \
                        HORIZONTAL_PADDING, LEFT_PADDING, cell_height
from settings import preferred_pen, settings
from box_menu import show_box_menu
from color_helper import highlight_color
from strip_underscore import maybe_strip_underscores
from main_graph_undo_redo import track_undo_press, track_undo_release

# text looks bad in renderable so we render text in paint

BOX_PADDING = 20

class ViewReportReport(QGraphicsItem):

    def __init__(self, report_box, gry_report_data):
        super().__init__()
        self.gry_report_data = gry_report_data

        self.report_box = report_box
        self.rows = maybe_strip_underscores(gry_report_data["rows"])

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(2)

        self._define_appearance()
        self.setParentItem(report_box)
        self._is_hovered = False

    def _define_appearance(self):
        p = BOX_PADDING

        self.w = widest_text(self.rows) + HORIZONTAL_PADDING
        w = self.w
        h = cell_height()
        num_rows = len(self.rows)

        # lines path
        lines_path = QPainterPath()
        for i in range(0, num_rows + 1):
            y = i * h
            lines_path.moveTo(0, y)
            lines_path.lineTo(w, y)
        y1 = 0
        y2 = h * (num_rows)
        lines_path.moveTo(0, y1)
        lines_path.lineTo(0, y2)
        lines_path.moveTo(w, y1)
        lines_path.lineTo(w, y2)
        self.lines_path = lines_path

        self.bounds_path = QPainterPath()
        self.bounds_path.addRect(0, 0, w, y)

        self.rectangle = self.bounds_path.boundingRect()
        pen_width = 1
        self.bounding_rect = self.rectangle.adjusted(
                    -pen_width/2, -pen_width/2, pen_width/2, pen_width/2)

        self.prepareGeometryChange()

        # bounds path
    def reset_appearance(self):
        # no geometry change, just possible color change
        self.update()

    def get_gry(self):
        self.gry_report_data["x"] = self.x()
        self.gry_report_data["y"] = self.y()
        return self.gry_report_data

    def type(self):
        return VIEW_REPORT_TYPE

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounding_rect

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
            painter.fillRect(self.bounding_rect, color)

        painter.setPen(preferred_pen())

        # lines path
        painter.drawPath(self.lines_path)

        w = self.w
        h = cell_height()

        # lines of text left aligned
        num_rows = len(self.rows)
        x = LEFT_PADDING
        for i, row in enumerate(self.rows):
            y = h * i
            painter.drawText(QRectF(x, y, w, h),
                             Qt.AlignmentFlag.AlignVCenter, row)

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
        track_undo_release(self, "report", event)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()

