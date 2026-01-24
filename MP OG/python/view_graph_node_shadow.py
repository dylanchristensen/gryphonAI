from PySide6.QtCore import QRectF, QPointF
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem
from graph_constants import VIEW_GRAPH_NODE_SHADOW_TYPE
from settings import settings

class ViewGraphNodeShadow(QGraphicsItem):

    def __init__(self, corresponding_node):
        super().__init__()
        # Putting parent in __init__ crashes with "pure virtual method called"
        # so we use setParentItem later.

        # put shadow below edges
        self.setZValue(0)

        self.corresponding_node = corresponding_node
        self.setPos(corresponding_node.pos()) # initial placement
        self.shadow_color = QColor(Qt.GlobalColor.darkGray)
        self.s = 3

        # Let node call reset_appearance and setParentItem which will
        # access boundingRect.
        pass

    def reset_appearance(self):
        self.use_shadow = settings["graph_node_use_shadow"]
        s = self.s

        # bounding rectangle
        if self.use_shadow:
            # paint uses brush without pen so we do not add pen width
            self.bounding_rectangle = self.corresponding_node \
                             .bounding_rectangle.adjusted(s, s, s, s)
        else:
            self.bounding_rectangle = QRectF()

        # box_shadow
        self.box_shadow = self.corresponding_node.box.adjusted(s, s, s, s)

        # changing appearance may change shadow's bounding rectangle
        self.prepareGeometryChange()

    def type(self):
        return VIEW_GRAPH_NODE_SHADOW_TYPE

    def boundingRect(self):
        return self.bounding_rectangle

    def shape(self):
        return QPainterPath()

    def paint(self, painter, _option, _widget):
        if self.use_shadow:
            painter.save()
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.setBrush(QBrush(self.shadow_color))
            r = self.corresponding_node.corner_rounding
            painter.drawRoundedRect(self.box_shadow, r, r)
            painter.restore()

