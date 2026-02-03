# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

from math import sin, cos, atan2, pi
from PySide6.QtCore import QLineF, QPointF
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainterPath, QPen, QPolygonF
from PySide6.QtGui import QPainterPathStroker
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsItem
from settings_manager import settings
from edge_bezier_placer import move_cubic_bezier_path
from graph_constants import EDGE_TYPE
from font_helper import text_width, font_descent

# Edge
# note: Edge is in charge of managing its EdgeText
#
# class variables:
#     ep0, ep1, ep2, ep3: Cubic Bezier points from from node to to node
#     old_ep0, old_ep3
#     color, line_width, style, arrow_size
#     label: Edge text

class Edge(QGraphicsItem):

    def __init__(self, parent, gry_edge, node_lookup):
        super().__init__()

        # MP attributes
        self.from_id= gry_edge["from_id"]
        self.relation = gry_edge["relation"]
        self.to_id = gry_edge["to_id"]
        self.label = gry_edge["label"]
        # cubic bezier point
        self.ep1 = QPointF(gry_edge["ep1_x"], gry_edge["ep1_y"])
        self.ep2 = QPointF(gry_edge["ep2_x"], gry_edge["ep2_y"])

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

        self.setParentItem(parent)

    def type(self):
        return EDGE_TYPE

    # export
    def get_gry(self):
        gry_edge = dict()
        gry_edge["from_id"] = self.from_id
        gry_edge["relation"] = self.relation
        gry_edge["to_id"] = self.to_id
        gry_edge["label"] = self.label
        gry_edge["ep1_x"] = self.ep1.x()
        gry_edge["ep1_y"] = self.ep1.y()
        gry_edge["ep2_x"] = self.ep2.x()
        gry_edge["ep2_y"] = self.ep2.y()
        return gry_edge

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
        dest_path = self.to_node.mouse_path.translated(self.to_node.pos())
        t = 0.5
        m = 0.25
        for _i in range(10): # binary search edge with resolution of 12
            arrow_tip = edge_path.pointAtPercent(t)
            if dest_path.contains(arrow_tip):
                # inside dest so move back
                t -= m
            else:
                # outside dest so move toward
                t += m
            m /= 2

        # define the arrow shape as a polygon
        arrow_size = settings["trace_edge_arrow_size"]
        # angleAtPercent takes way too much time so calculate directly instead,
        # https://stackoverflow.com/questions/4089443/find-the-tangent-of-a-point-on-a-cubic-bezier-curve
        omt = 1 - t # one minus t
        arrow_tangent_point = 3*omt*omt*(self.ep1 - self.ep2) + \
                              6*t*omt*(self.ep2 - self.ep1) + \
                              3*t*t*(self.ep3 - self.ep2)
        theta = atan2(-arrow_tangent_point.y(), arrow_tangent_point.x())
        dest_p1 = arrow_tip + QPointF(
                   sin(theta - pi / 3) * arrow_size,
                   cos(theta - pi / 3) * arrow_size)
        dest_p2 = arrow_tip + QPointF(
                   sin(theta - pi + pi / 3) * arrow_size,
                   cos(theta - pi + pi / 3) * arrow_size)
        self.arrow = QPolygonF([arrow_tip, dest_p1, dest_p2])

        # line color based on line relation
        self.line_width = 1
        if self.relation == "IN":
            self.color = QColor(settings["trace_edge_in_color"])
            self.style = Qt.PenStyle.DashLine
        elif self.relation == "FOLLOWS":
            self.color = QColor(settings["trace_edge_follows_color"])
            self.style = Qt.PenStyle.SolidLine
        elif self.relation == "COLLAPSED_FOLLOWS":
            self.color = QColor(settings["trace_edge_follows_color"])
            self.style = Qt.PenStyle.SolidLine
            self.line_width = 2
        elif self.relation == "USER_DEFINED":
            self.color = QColor(settings["trace_edge_user_defined_color"])
            self.style = Qt.PenStyle.SolidLine
        else:
            print("unrecognized edge relation '%s'" % self.relation)
            self.color = QColor(Qt.GlobalColor.gray)
            self.style = Qt.PenStyle.SolidLine

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

        # Use opacity if node on either side is hidden or collapsed
        if self.from_node.hide or self.from_node.collapse or \
                      self.to_node.hide or self.to_node.collapse:
            self.color.setAlpha(settings["trace_hide_collapse_opacity"])

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

        # draw the arrow
        painter.setPen(QPen(self.color, self.line_width, Qt.PenStyle.SolidLine,
                                     Qt.PenCapStyle.RoundCap,
                                     Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(self.color)
        painter.drawPolygon(self.arrow)

        # draw edge label if present
        if self.label:
            fm = painter.fontMetrics()
            label_width = fm.horizontalAdvance(self.label)
            label_descent = fm.descent()
            offset = QPointF(label_width/2, label_descent+1)
            painter.drawText(self.label_point - offset, self.label)

        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super(Edge, self).itemChange(change, value)

    def mousePressEvent(self, _event):

        # highlight edge and show edge grips
        self.scene().edge_grip_manager.highlight_edge(self)

