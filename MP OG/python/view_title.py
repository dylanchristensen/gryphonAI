
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainterPath
from PySide6.QtWidgets import QGraphicsItem
from settings import settings, preferred_pen
from graph_constants import VIEW_TITLE_TYPE
from font_helper import cell_height, bound_text_width_and_height
from color_helper import highlight_color
from strip_underscore import strip_underscore
from main_graph_undo_redo import track_undo_press, track_undo_release

# Note: we don't use QGraphicsSimpleTextItem because its paint method
# expects an incompatible QStyleOption type.

class ViewTitle(QGraphicsItem):

    def __init__(self, parent_box, gry_text):
        super().__init__()
        self.gry_text = gry_text

        self.text = strip_underscore(gry_text["text"])
        if 'x' in gry_text:
            self.setPos(QPointF(gry_text["x"], gry_text["y"]))

        # state
        self._is_hovered = False

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(2)

        # appearance
        self.reset_appearance()

        self.setParentItem(parent_box)

    # export
    def get_gry(self):
        self.gry_text["x"] = self.x()
        self.gry_text["y"] = self.y()
        return self.gry_text

    # adjust for appearance change
    def reset_appearance(self):

        # define shape path and bounding rect
        w, h = bound_text_width_and_height(self.text, settings["title_width"])
        self.bounding_rect = QRectF(-w / 2, -h, w, h)
        self.shape_path = QPainterPath()
        self.shape_path.addRect(self.boundingRect())

        self.preferred_pen = preferred_pen()
        self.prepareGeometryChange()

    def type(self):
        return VIEW_TITLE_TYPE

    # boundary for sizing this with other components
    def boundingRect(self):
        return self.bounding_rect

    # mouse acknowledges when on this path so make it a rectangle
    def shape(self):
        return self.shape_path

    def paint(self, painter, _option, _widget):
        painter.save()

        if self._is_hovered:
            # highlight
            color = highlight_color(QColor(settings["background_color"]))
            painter.fillRect(self.bounding_rect, color)

        # text
        painter.setPen(self.preferred_pen)
        flags = Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap
        painter.drawText(self.bounding_rect.toAlignedRect(), flags, self.text)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(self.bounding_rect)

        painter.restore()

    # align text center over top of items
    def align_above(self, other_items):
        if other_items:
            # center over top of nodes
            x_min = min([other_item.x() + other_item.boundingRect().left()
                                        for other_item in other_items])
            x_max = max([other_item.x() + other_item.boundingRect().right()
                                        for other_item in other_items])
            y = min([other_item.y() + other_item.boundingRect().top()
                                        for other_item in other_items])
            self.setX((x_min + x_max) / 2)
            self.setY(y - cell_height())
        else:
            # nothing to align with
            pass

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # change shape of enclosing box
            self.parentItem().itemChange(change, value)
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        # track potential move
        track_undo_press(self, event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # maybe record move
        track_undo_release(self, "title", event)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()

