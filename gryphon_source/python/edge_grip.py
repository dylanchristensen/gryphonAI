from PySide6.QtCore import QPointF, QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QGraphicsItem
from settings import settings
from color_helper import highlight_color
from graph_constants import EDGE_GRIP_TYPE

# EdgeGrip
class EdgeGrip(QGraphicsItem):

    def __init__(self, edge_grip_manager, grip_index, position, color):
        super().__init__()

        self.edge_grip_manager = edge_grip_manager
        self.grip_index = grip_index
        self.setPos(position)
        self.color = color

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(3)
        self.setAcceptHoverEvents(True)
        self._is_hovered = False

        # bounding rectangle and shape
        d = 10 # diameter
        a = 2 # border adjust
        self.bounding_rectangle = QRectF(-d/2-a, -d/2-a, d+a, d+a)
        self.grip_shape = QPainterPath()
        self.grip_shape.addEllipse(QPointF(0, 0), d/2, d/2)

        # gradient
        self.gradient = QRadialGradient(-2, -2, 0.7*d)

    def type(self):
        return EDGE_GRIP_TYPE

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounding_rectangle

    # mouse hover is detected when inside this shape
    def shape(self):
        return self.grip_shape

    def paint(self, painter, _option, _widget):

        # circle gradient color
        if self._is_hovered:
            c = highlight_color(self.color)
        else:
            c = self.color
        self.gradient.setColorAt(0, c.lighter(170))
        self.gradient.setColorAt(1, c.darker(110))

        # draw circle
        painter.setBrush(QBrush(self.gradient))
        painter.setPen(QPen(QColor(Qt.GlobalColor.red), 0))
        painter.drawPath(self.grip_shape)

    def itemChange(self, change, value):
        # note this can happen fast so keep handler short to avoid recursion
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.edge_grip_manager.move_edge(self.grip_index, change, value)

        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        self.scene().clearSelection()
        self.edge_grip_manager.track_undo_grip_press(event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.edge_grip_manager.track_undo_grip_release(event)
        super().mouseReleaseEvent(event)


    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()
        super().hoverEnterEvent(_event)

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()
        super().hoverLeaveEvent(_event)

