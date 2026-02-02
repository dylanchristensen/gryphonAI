# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

from math import sin, cos, atan2, pi
from PySide6.QtCore import QLineF, QPointF
from PySide6.QtCore import Qt
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainterPath, QPen, QPolygonF
from PySide6.QtGui import QPainterPathStroker
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsItem
from settings import settings, preferred_pen
from graph_constants import VIEW_AD_EDGE_TYPE
from color_helper import highlight_color
from view_ad_edge_points import edge_to_points, adjusted_edge_vector, \
                                                adjusted_edge_segment

# View Graph Edge
# note: Edge is in charge of managing its EdgeText
#
# class variables:
#     edge_start: h or v
#     edge_vector: list of yxy... or xyx...
#     color

# make arrowhead along straight line from ep2 to ep3
def _arrowhead(ep2, ep3, arrow_size):
    theta = atan2(ep3.y() - ep2.y(), ep3.x() - ep2.x())
    dest_p1 = ep3 + QPointF(
           sin(theta - pi / 3) * arrow_size,
         - cos(theta - pi / 3) * arrow_size)
    dest_p2 = ep3 + QPointF(
           sin(theta - pi + pi / 3) * arrow_size,
         - cos(theta - pi + pi / 3) * arrow_size)
    arrowhead = QPolygonF([ep3, dest_p1, dest_p2, ep3])
    return arrowhead

class ViewADEdge(QGraphicsItem):

    def __init__(self, parent_box, gry_edge, node_lookup):
        super().__init__()
        self.gry_edge = gry_edge

        # graph attributes
        self.from_id = gry_edge["from_id"]
        self.to_id = gry_edge["to_id"]

        # state
        self.from_node = node_lookup[self.from_id]
        self.to_node = node_lookup[self.to_id]
        self.from_node.add_edge(self)
        self.to_node.add_edge(self)
        self._is_highlighted = False
        self._is_hovered = False

        if "edge_vector" in gry_edge:
            self.edge_start = gry_edge["edge_start"]
            self.edge_vector = gry_edge["edge_vector"]

            # appearance
            self.reset_appearance()

        else:
            # generate edge vector later
            self.bounding_rect = QRectF()

        # graphicsItem mode
        self.setAcceptHoverEvents(True)

        # parent
        self.setParentItem(parent_box)

    # placer uses this
    def set_edge_vector(self, edge_start, edge_vector):
        self.edge_start = edge_start
        self.edge_vector = edge_vector
        self.reset_appearance()
        self.itemChange(QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged,
                        None)

    # change edge vector based on request, return list of changes
    def change_edge_vector(self, requested_edge_start, requested_edge_vector):
        edge_start, edge_vector, changes = adjusted_edge_vector(
                            self, requested_edge_start, requested_edge_vector)
        self.set_edge_vector(edge_start, edge_vector)
        return changes # used by edge grips

    def move_edge_because_node_moved(self, node, dx, dy):
        suggested_edge_vector = adjusted_edge_segment(node, self, dx, dy)
        return self.change_edge_vector(self.edge_start, suggested_edge_vector)

    # export
    def get_gry_edge(self):
        self.gry_edge["edge_start"] = self.edge_start
        self.gry_edge["edge_vector"] = self.edge_vector
        return self.gry_edge

    def type(self):
        return VIEW_AD_EDGE_TYPE

    def _set_edge_path_and_arrow(self):
        edge_points = edge_to_points(self)
        if edge_points:
            self.edge_path = QPainterPath(edge_points[0])
            for point in edge_points[1:]:
                self.edge_path.lineTo(point)

            # the arrow
            self.arrow = _arrowhead(edge_points[-2], edge_points[-1],
                                    settings["ad_edge_arrow_size"])

            # add the arrowhead outline to the edge path
            self.edge_path.addPolygon(self.arrow)

        else:
            # no edge
            self.edge_path = QPainterPath()
            self.arrow = QPolygonF()

    # adjust for appearance change or for node position change
    def reset_appearance(self):

        # edge path
        self._set_edge_path_and_arrow()

        # the path region for mouse detection
        # note: path without stroker includes concave shape, not just edge path
        painter_path_stroker = QPainterPathStroker()
        painter_path_stroker.setWidth(3)
        self.shape_path = painter_path_stroker.createStroke(self.edge_path)

        # line color
        self.color = QColor(settings["ad_edge_color"])

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

        # set edge color
        if self._is_hovered:
            # highlight
            color = highlight_color(self.color)
        else:
            color = self.color

        # paint edge shape of path without brush fill
        painter.strokePath(self.edge_path, QPen(color, 1,
                           Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                           Qt.PenJoinStyle.RoundJoin))

        # draw the arrow with brush fill
        painter.setPen(QPen(color, 1, Qt.PenStyle.SolidLine,
                         Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(color)
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
        self.scene().view_ad_edge_grip_manager.highlight_edge(self)

    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()

