from PySide6.QtCore import QPoint, QRectF, Qt
from PySide6.QtGui import QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from graph_constants import VIEW_REPORT_TYPE
from font_helper import text_width, widest_text, \
                        HORIZONTAL_PADDING, LEFT_PADDING, cell_height
from settings_manager import preferred_pen
from box_menu import show_box_menu

# text looks bad in renderable so we render text in paint

BOX_PADDING = 20

class ViewReportReport(QGraphicsItem):

    def __init__(self, report_box, gry_report):
        super().__init__()

        self.report_box = report_box
        self.title = gry_report["title"]
        self.lines = gry_report["lines"]

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(2)

        self.reset_appearance()
        self.setParentItem(report_box)

    def reset_appearance(self):
        p = BOX_PADDING

        self.w = max(text_width(self.title), widest_text(self.lines)
                                                   + HORIZONTAL_PADDING)
        w = self.w
        h = cell_height()
        num_rows = len(self.lines)

        # lines path
        lines_path = QPainterPath()
        for i in range(1, num_rows + 2):
            y = i * h
            lines_path.moveTo(0, y)
            lines_path.lineTo(w, y)
        y1 = h
        y2 = h + num_rows * h
        lines_path.moveTo(0, y1)
        lines_path.lineTo(0, y2)
        lines_path.moveTo(w, y1)
        lines_path.lineTo(w, y2)
        self.lines_path = lines_path

        # bounds path
        self.bounds_path = QPainterPath()
        self.bounds_path.addRect(0, 0, w, y)

        # pen color
        self.preferred_pen = preferred_pen()

        self.prepareGeometryChange()

    def get_gry(self):
        gry_report = {"title":self.title, "lines":self.lines}
        return gry_report

    def type(self):
        return VIEW_REPORT_TYPE

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounds_path.boundingRect().adjusted(-1, -1, 1, 1)

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

        # lines path
        painter.drawPath(self.lines_path)

        w = self.w
        h = cell_height()

        # title centered
        painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter,
                                                        self.title)

        # lines of text left aligned
        num_rows = len(self.lines)
        x = LEFT_PADDING
        for i, line in enumerate(self.lines, start=1):
            y = h * i
            painter.drawText(QRectF(x, y, w, h),
                             Qt.AlignmentFlag.AlignVCenter, line)

        painter.restore()

    def contextMenuEvent(self, event):
        if event.reason() == QGraphicsSceneContextMenuEvent.Reason.Mouse:
            show_box_menu(self.report_box)

