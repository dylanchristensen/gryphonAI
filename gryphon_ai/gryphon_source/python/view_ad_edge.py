# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

from math import sin, cos, atan2, pi
from PySide6.QtCore import QLineF, QPointF
from PySide6.QtCore import Qt
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainterPath, QPen, QPolygonF
from PySide6.QtGui import QPainterPathStroker
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsItem
from settings_manager import settings, preferred_pen
from graph_constants import VIEW_GRAPH_EDGE_TYPE
from edge_bezier_placer import move_cubic_bezier_path
from font_helper import text_width, font_descent

# View Graph Edge
# note: Edge is in charge of managing its EdgeText
#
# class variables:
#     ep0, ep1, ep2, ep3: edge placement points from source to dest
#     color, arrow_size

# make arrowhead along straight line from ep2 to ep3
def _arrowhead(ep2, ep3, arrow_size):
    theta = atan2(ep3.y() - ep2.y(), ep3.x() - ep2.x())
    dest_p1 = ep3 + QPointF(
           sin(theta - pi / 3) * arrow_size,
         - cos(theta - pi / 3) * arrow_size)
    dest_p2 = ep3 + QPointF(
           sin(theta - pi + pi / 3) * arrow_size,
         - cos(theta - pi + pi / 3) * arrow_size)
    arrowhead = QPolygonF([ep3, dest_p1, dest_p2])
    return arrowhead

class ViewADEdge(QGraphicsItem):

    def __init__(self, parent_box, gry_edge, node_lookup):
        super().__init__()

        # graph attributes
        self.from_id = gry_edge["from_id"]
        self.to_id = gry_edge["to_id"]

        # state
        self.from_node = node_lookup[self.from_id]
        self.to_node = node_lookup[self.to_id]
        self.from_node.add_edge(self)
        self.to_node.add_edge(self)
        self._is_highlighted = False

        if "ep1_x" in gry_edge:
            # edge points
            self.ep1 = QPointF(gry_edge["ep1_x"],
                                gry_edge["ep1_y"])
            self.ep2 = QPointF(gry_edge["ep2_x"],
                                gry_edge["ep2_y"])
            self.ep0 = self.from_node.snap_point(self.ep1, False)
            self.ep3 = self.to_node.snap_point(self.ep2, True)

            # appearance
            self.reset_appearance()

        else:
            # set edge points later
            self.bounding_rect = QRectF()

        # parent
        self.setParentItem(parent_box)

    # export
    def get_gry_edge(self):
        gry_edge = dict()
        gry_edge["from_id"] = self.from_id
        gry_edge["to_id"] = self.to_id
        gry_edge["ep1_x"] = self.ep1.x()
        gry_edge["ep1_y"] = self.ep1.y()
        gry_edge["ep2_x"] = self.ep2.x()
        gry_edge["ep2_y"] = self.ep2.y()
        return gry_edge

    def type(self):
        return VIEW_AP_EDGE_TYPE


    # adjust for appearance change or for node position change
    def reset_appearance(self):

        # angular placement
        self.ep0 = self.from_node.snap_point(self.ep1, False)
        self.ep3 = self.to_node.snap_point(self.ep2, True)
        self.edge_path = QPainterPath(self.ep0)
        self.edge_path.lineTo(self.ep1)
        self.edge_path.lineTo(self.ep2)
        self.edge_path.lineTo(self.ep3)

        # the path region for mouse detection
        # note: path without stroker includes concave shape, not just edge path
        painter_path_stroker = QPainterPathStroker()
        self.mouse_path = painter_path_stroker.createStroke(self.edge_path)

        # the arrow
        self.arrow = _arrowhead(self.ep2, self.ep3,
                                settings["ad_edge_arrow_size"])

        # line color
        self.color = QColor(settings["ad_edge_color"])

        # the path region for mouse detection
        # note: path without stroker includes concave shape, not just edge path
        painter_path_stroker = QPainterPathStroker()
        self.shape_path = painter_path_stroker.createStroke(self.edge_path)
        # use padding
        extra = 1
        self.bounding_rect = self.shape_path.boundingRect().adjusted(
                                             -extra, -extra, extra, extra)

        # use red if highlighted
        if self._is_highlighted:
            self.color = QColor(Qt.GlobalColor.red)

        # about to change line's bounding rectangle
        self.prepareGeometryChange()

    def set_highlighted(self, is_highlighted):
        self._is_highlighted = is_highlighted
        self.reset_appearance()

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        # note: path without stroker includes concave shape, not just edge path
        return self.shape_path

    def paint(self, painter, _option, _widget):
        painter.save()

        # paint edge shape of path without brush fill
        painter.strokePath(self.edge_path, QPen(self.color, 1,
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                           Qt.PenJoinStyle.RoundJoin))

        # draw the arrow
        painter.setPen(QPen(self.color, 1, Qt.PenStyle.SolidLine,
                         Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(self.color)
        painter.drawPolygon(self.arrow)

        painter.restore()

    # we get here from itemChange from edge_grip
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super().itemChange(change, value)

    def mousePressEvent(self, _event):

        # highlight edge and show edge grips
        self.scene().edge_grip_manager.highlight_edge(self)

    def set_ap(self, ep1x, ep1y, ep2x, ep2y):
        self.ep1 = QPointF(ep1x, ep1y)
        self.ep2 = QPointF(ep2x, ep2y)
        self.reset_appearance()

