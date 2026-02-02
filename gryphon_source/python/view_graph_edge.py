# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

from math import sin, cos, atan2, pi
from PySide6.QtCore import QLineF, QPointF
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainterPath, QPen, QPolygonF
from PySide6.QtGui import QPainterPathStroker
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsItem
from settings import settings, preferred_pen
from graph_constants import VIEW_GRAPH_EDGE_TYPE
from edge_bezier_placer import move_cubic_bezier_path
from edge_path import path_and_arrow
from font_helper import text_width, font_descent
from color_helper import highlight_color
from edge_annotation import EdgeAnnotation
from strip_underscore import strip_underscore

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

class ViewGraphEdge(QGraphicsItem):

    def __init__(self, parent_box, gry_edge, node_lookup):
        super().__init__()
        self.gry_edge = gry_edge

        # graph attributes
        self.from_id = gry_edge["from_id"]
        self.label = strip_underscore(gry_edge["label"])
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
        self.setAcceptHoverEvents(True)
        self.setZValue(1) # below nodes but above node shadows

        self.from_node = node_lookup[self.from_id]
        self.to_node = node_lookup[self.to_id]
        self.from_node.add_edge(self)
        self.to_node.add_edge(self)

        # old points to manage move
        self.old_ep0 = self.from_node.pos()
        self.old_ep3 = self.to_node.pos()

        # state
        self._is_highlighted = False
        self._is_hovered = False

        # annotation
        self.edge_annotation = EdgeAnnotation(self.label)

        # appearance
        self.reset_appearance()

        self.setParentItem(parent_box)
        self.edge_annotation.setParentItem(parent_box)

    # export
    def get_gry_edge(self):
        self.gry_edge["ep1_x"] = self.ep1.x()
        self.gry_edge["ep1_y"] = self.ep1.y()
        self.gry_edge["ep2_x"] = self.ep2.x()
        self.gry_edge["ep2_y"] = self.ep2.y()
        return self.gry_edge

    def type(self):
        return VIEW_GRAPH_EDGE_TYPE

    # adjust for appearance change or for node position change
    def reset_appearance(self):

        # Cubic Bezier path
        self.ep0 = self.from_node.pos()
        self.ep3 = self.to_node.pos()
        if self.old_ep0 != self.ep0 or self.old_ep3 != self.ep3:
            move_cubic_bezier_path(self)

        # get the drawable edge path and arrow
        self.edge_path, self.arrow = path_and_arrow(
                          self.from_node, self.to_node, self.ep1, self.ep2,
                          settings["graph_edge_arrow_size"])

        # define the path region for mouse detection
        # note: path without stroker includes concave shape, not just edge path
        # note: without arrow because arrow edges change path center
        painter_path_stroker = QPainterPathStroker()
        painter_path_stroker.setWidth(3)
        self.mouse_path = painter_path_stroker.createStroke(self.edge_path)

        # line color
        self.line_width = 1
        self.color = QColor(settings["graph_edge_color"])
        self.style = Qt.PenStyle.SolidLine

        # the rectangular boundary
        _path = QPainterPath(self.edge_path)
        extra = 1
        self.bounding_rect = _path.boundingRect().adjusted(-extra, -extra,
                                                           extra, extra)

        # use red if highlighted
        if self._is_highlighted:
            self.color = QColor(Qt.GlobalColor.red)

        # about to change line's bounding rectangle
        self.prepareGeometryChange()

        # update annotation appearance
        self._reset_annotation_appearance()

    def _reset_annotation_appearance(self):
        self.edge_annotation.reset_appearance(
                        settings["background_color"],
                        settings["graph_edge_color"],
                        settings["graph_edge_annotation_width"],
                        settings["graph_edge_annotation_background_opacity"],
                        self.center(),
                        self._is_highlighted,
                        self._is_hovered,
                       )

    # use this for annotation placement
    def center(self):
        return self.edge_path.pointAtPercent(0.5)

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

        # set edge color
        if self._is_hovered:
            # highlight
            color = highlight_color(self.color)
        else:
            color = self.color

        # paint edge shape of path without brush fill
        painter.strokePath(self.edge_path, QPen(color, self.line_width,
                           self.style, Qt.PenCapStyle.RoundCap,
                           Qt.PenJoinStyle.RoundJoin))

        # maybe draw the arrow
        if self.use_arrow:
            painter.setPen(QPen(color, self.line_width, self.style,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(color)
            painter.drawPolygon(self.arrow)

        painter.restore()

    # we get here from itemChange from edge_grip
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:

            # move annotation
            self._reset_annotation_appearance()

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

    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()
        self._reset_annotation_appearance()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()
        self._reset_annotation_appearance()

