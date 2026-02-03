# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

from math import sin, cos, atan2, pi
from PySide6.QtCore import QLineF, QPointF
from PySide6.QtCore import Qt
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
#     ep0, ep1, ep2, ep3: Cubic Bezier points from source to dest
#     old_ep0, old_ep3
#     color, arrow_size
#     label: Edge text

def _use_arrow(type):
    if type == "directed":
        return True
    elif type == "undirected":
        return False
    else:
        raise RuntimeError("bad")
def _gry_use_arrow(use_arrow):
    if use_arrow:
        return "directed"
    else:
        return "undirected"

def _make_arrow(edge):

    # get coordinate of arrow tip based on destination node
    # using binary search
    dest_path = edge.to_node.mouse_path.translated(edge.to_node.pos())
    t = 0.5
    m = 0.25
    for _i in range(10): # binary search edge with resolution of 12
        arrow_tip = edge.edge_path.pointAtPercent(t)
        if dest_path.contains(arrow_tip):
            # inside dest so move back
            t -= m
        else:
            # outside dest so move toward
            t += m
        m /= 2

    # define the arrow shape as a polygon
    arrow_size = settings["graph_edge_arrow_size"]
    # angleAtPercent takes way too much time so calculate directly instead,
    # https://stackoverflow.com/questions/4089443/find-the-tangent-of-a-point-on-a-cubic-bezier-curve
    omt = 1 - t # one minus t
    arrow_tangent_point = 3*omt*omt*(edge.ep1 - edge.ep2) + \
                          6*t*omt*(edge.ep2 - edge.ep1) + \
                          3*t*t*(edge.ep3 - edge.ep2)
    theta = atan2(-arrow_tangent_point.y(), arrow_tangent_point.x())
    dest_p1 = arrow_tip + QPointF(
               sin(theta - pi / 3) * arrow_size,
               cos(theta - pi / 3) * arrow_size)
    dest_p2 = arrow_tip + QPointF(
               sin(theta - pi + pi / 3) * arrow_size,
               cos(theta - pi + pi / 3) * arrow_size)
    arrow = QPolygonF([arrow_tip, dest_p1, dest_p2])
    return arrow

class ViewGraphEdge(QGraphicsItem):

    def __init__(self, parent_box, gry_edge, node_lookup):
        super().__init__()

        # graph attributes
        self.from_id = gry_edge["from_id"]
        self.label = gry_edge["label"]
        self._type = gry_edge["type"]
        self.to_id = gry_edge["to_id"]
        self.use_arrow = _use_arrow(gry_edge["type"])

        # cubic bezier points
        if "ep1_x" in gry_edge:
            self.ep1 = QPointF(gry_edge["ep1_x"],
                                gry_edge["ep1_y"])
            self.ep2 = QPointF(gry_edge["ep2_x"],
                                gry_edge["ep2_y"])
        else:
            self.ep1 = QPointF(0,0)
            self.ep2 = QPointF(0,0)

        # graphicsItem mode
        pass

        self.from_node = node_lookup[self.from_id]
        self.to_node = node_lookup[self.to_id]
        self.from_node.add_edge(self)
        self.to_node.add_edge(self)

        # old points to manage move
        self.old_ep0 = self.from_node.pos()
        self.old_ep3 = self.to_node.pos()

        # state
        self._is_highlighted = False

        # appearance
        self.reset_appearance()

        self.setParentItem(parent_box)

    # export
    def get_gry_edge(self):
        gry_edge = dict()
        gry_edge["from_id"] = self.from_id
        gry_edge["type"] = _gry_use_arrow(self.use_arrow)
        gry_edge["to_id"] = self.to_id
        gry_edge["label"] = self.label
        gry_edge["ep1_x"] = self.ep1.x()
        gry_edge["ep1_y"] = self.ep1.y()
        gry_edge["ep2_x"] = self.ep2.x()
        gry_edge["ep2_y"] = self.ep2.y()
        return gry_edge

    def type(self):
        return VIEW_GRAPH_EDGE_TYPE

    # adjust for appearance change or for node position change
    def reset_appearance(self):

        # Cubic Bezier path
        self.ep0 = self.from_node.pos()
        self.ep3 = self.to_node.pos()
        if self.old_ep0 != self.ep0 or self.old_ep3 != self.ep3:
            move_cubic_bezier_path(self)
        self.edge_path = QPainterPath(self.ep0)
        self.edge_path.cubicTo(self.ep1, self.ep2, self.ep3)

        # the path region for mouse detection
        # note: path without stroker includes concave shape, not just edge path
        painter_path_stroker = QPainterPathStroker()
        self.mouse_path = painter_path_stroker.createStroke(self.edge_path)

        # get coordinate of arrow tip based on destination node
        # using binary search
        edge_path = self.edge_path
        if self.use_arrow:
            self.arrow = _make_arrow(self)

        # line color
        self.line_width = 1
        self.color = QColor(settings["graph_edge_color"])
        self.style = Qt.PenStyle.SolidLine

        # text pen
        self.preferred_pen = preferred_pen()

        # define edge text point
        _label_corner = edge_path.pointAtPercent(0.5)
        _label_offset = QPointF(text_width(self.label) / 2, font_descent() + 1)
        self.label_point = _label_corner - _label_offset

        # the rectangular boundary including text
        _path = QPainterPath(self.edge_path)
        _path.addText(self.label_point, QFont(), self.label)
        extra = 1
        self.bounding_rect = _path.boundingRect().adjusted(-extra, -extra,
                                                           extra, extra)


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
        return self.mouse_path

    def paint(self, painter, _option, _widget):
        painter.save()

        # paint edge shape of path without brush fill
        painter.strokePath(self.edge_path, QPen(self.color, self.line_width,
                           self.style, Qt.PenCapStyle.RoundCap,
                           Qt.PenJoinStyle.RoundJoin))

        # maybe draw the arrow
        if self.use_arrow:
            painter.setPen(QPen(self.color, self.line_width, self.style,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(self.color)
            painter.drawPolygon(self.arrow)

        # draw edge label
        painter.setPen(self.preferred_pen)
        painter.drawText(self.label_point, self.label)

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

    def set_ep(self, ep1x, ep1y, ep2x, ep2y):
        self.ep1 = QPointF(ep1x, ep1y)
        self.ep2 = QPointF(ep2x, ep2y)
        self.reset_appearance()

