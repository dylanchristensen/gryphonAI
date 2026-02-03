
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import (QBrush, QColor, QLinearGradient,
                         QPainterPath, QPen, QPolygonF, QRadialGradient)
from PySide6.QtGui import QFontMetrics
from PySide6.QtGui import QFont
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from settings_manager import settings, preferred_pen
from color_helper import text_color_name
from node_menu import NodeMenu
from graph_constants import VIEW_TEXT_TYPE
from font_helper import cell_height, bound_text_width_and_height

# Note: we don't use QGraphicsSimpleTextItem because its paint method
# expects an incompatible QStyleOption type.

DEFAULT_MAX_TEXT_WIDTH = 300

class ViewText(QGraphicsItem):

    def __init__(self, parent_box, gry_text):
        super().__init__()
        self.text = gry_text["text"]
        if 'x' in gry_text:
            self.setPos(QPointF(gry_text["x"], gry_text["y"]))
            self.max_text_width = gry_text["max_w"]
        else:
            self.max_text_width = DEFAULT_MAX_TEXT_WIDTH

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.setZValue(2)

        # appearance
        self.reset_appearance()

        self.setParentItem(parent_box)

    # export
    def get_gry(self):
        gry_text = dict()
        gry_text["text"] = self.text
        gry_text["x"] = self.x()
        gry_text["y"] = self.y()
        gry_text["max_w"] = self.max_text_width
        return gry_text

    # adjust for appearance change
    def reset_appearance(self):

        # define shape path and bounding rect
        w, h = bound_text_width_and_height(self.text, self.max_text_width)
        self.bounding_rect = QRectF(-w / 2, -h, w, h)
        self.shape_path = QPainterPath()
        self.shape_path.addRect(self.boundingRect())

        self.preferred_pen = preferred_pen()
        self.prepareGeometryChange()

    def type(self):
        return VIEW_TEXT_TYPE

    # boundary for sizing this with other components
    def boundingRect(self):
        return self.bounding_rect

    # mouse acknowledges when on this path so make it a rectangle
    def shape(self):
        return self.shape_path

    def paint(self, painter, _option, _widget):
        painter.save()

        # text
        painter.setPen(self.preferred_pen)
        flags = Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap
        painter.drawText(self.bounding_rect.toAlignedRect(), flags, self.text)

        painter.restore()

    # align text center over top of items
    def align_above(self, other_items):
        if other_items:
            # center over top of nodes
            x_min = min([other_item.x() + other_item.boundingRect().left()
                                        for other_item in other_items])
            x_max = max([other_item.x() + other_item.boundingRect().right()
                                        for other_item in other_items])
            y = min([other_item.y() for other_item in other_items])
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

