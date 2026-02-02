from PySide6.QtCore import QRectF, QPointF
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainterPath, QPolygonF
from PySide6.QtWidgets import QGraphicsItem
from settings import settings
from graph_constants import NODE_SHADOW_TYPE

class NodeShadow(QGraphicsItem):

    def __init__(self, corresponding_node):
        super().__init__()
        # Putting parent in __init__ crashes with "pure virtual method called"
        # so we use setParentItem.
 
        # put shadow below edges
        self.setZValue(0)

        self.corresponding_node = corresponding_node
        self.setPos(corresponding_node.pos()) # initial placement

        # shadow size
        self.s = 3

    def reset_appearance(self):
        self.use_shadow = settings["trace_node_use_shadow"]
        s = self.s
        t = self.corresponding_node.t
        w = self.corresponding_node.w
        h = self.corresponding_node.h

        self.prepareGeometryChange()
        # bounding rectangle
        if self.use_shadow:
            # paint uses brush without pen so we do not add pen width
            self.bounding_rectangle = self.corresponding_node \
                             .bounding_rectangle.adjusted(s, s, s, s)
        else:
            self.bounding_rectangle = QRectF()

        # right shadow
        self.right_shadow = QRectF(w/2, -h/2+s, s, h)
        # CW from upper-left
        self.right_shadow_say = QPolygonF(
                          [QPointF(+w/2, -h/2+t),
                           QPointF(+w/2+s, -h/2+t+s),
                           QPointF(+w/2+s, +h/2+s),
                           QPointF(+w/2, +h/2+s)])

        # bottom shadow
        self.bottom_shadow = QRectF(-w/2+s, h/2, w - s, s)

        self.prepareGeometryChange()

    def type(self):
        return NODE_SHADOW_TYPE

    def boundingRect(self):
        return self.bounding_rectangle

    def shape(self):
        return QPainterPath()

    def paint(self, painter, _option, _widget):
        if self.use_shadow:
            node = self.corresponding_node

            # right side
            if node.node_type == "T": # SAY message has right tab fold
                painter.save()
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(node.shadow_color)
                painter.drawPolygon(self.right_shadow_say)
                painter.restore()
            else:
                painter.fillRect(self.right_shadow, node.shadow_color)

            # bottom
            painter.fillRect(self.bottom_shadow, node.shadow_color)

