from PySide6.QtCore import QPointF, QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QGraphicsItem
from settings_manager import settings
from graph_constants import EDGE_GRIP_TYPE

# EdgeGrip
class EdgeGrip(QGraphicsItem):

    def __init__(self, edge, grip_side):
        super().__init__()

        # active side, "source" or "dest"
        self.grip_side = grip_side

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(3)

        # bounding rectangle and shape
        d = 10 # diameter
        a = 2 # border adjust
        self.bounding_rectangle = QRectF(-d/2-a, -d/2-a, d+a, d+a)
        self.grip_shape = QPainterPath()
        self.grip_shape.addEllipse(QPointF(0, 0), d/2, d/2)

        # gradient
        self.gradient = QRadialGradient(-2, -2, 0.7*d)

        # edge
        self.edge = edge

        # bind properties to grip depending on source or dest side
        if self.grip_side == "source":
            self.setPos(edge.ep1)
            self.color = QColor(settings["trace_node_root_color"])
        elif self.grip_side == "dest":
            self.setPos(edge.ep2)
            self.color = QColor(settings["trace_node_atomic_color"])
        else:
            raise Exception("Bad")

    def type(self):
        return EDGE_GRIP_TYPE

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounding_rectangle

    # mouse considered hovering when inside this rectangle
    def shape(self):
        return self.grip_shape

    def paint(self, painter, _option, _widget):

        # circle gradient color
        if self.isSelected():
            self.gradient.setColorAt(0, self.color.lighter(170))
            self.gradient.setColorAt(1, self.color.darker(110))
        else:
            self.gradient.setColorAt(0, self.color.lighter(140))
            self.gradient.setColorAt(1, self.color.darker(140))

        # draw circle
        painter.setBrush(QBrush(self.gradient))
        painter.setPen(QPen(QColor(Qt.GlobalColor.red), 0))
        painter.drawPath(self.grip_shape)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self.grip_side == "source":
                self.edge.ep1 = self.pos()
            elif self.grip_side == "dest":
                self.edge.ep2 = self.pos()
            else:
                raise Exception("Bad")
            self.edge.reset_appearance()

            # grip position change changes edge position
            self.edge.itemChange(change, value)

        return super().itemChange(change, value)

