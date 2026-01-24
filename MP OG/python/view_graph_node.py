# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import (QBrush, QColor, QLinearGradient,
                         QPainterPath, QPen, QPolygonF, QRadialGradient)
from PySide6.QtGui import QFontMetrics
from PySide6.QtGui import QFont
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from settings import settings
from color_helper import contrasting_color
from graph_constants import VIEW_GRAPH_NODE_TYPE
from font_helper import margined_text_height, paint_margined_text
from color_helper import highlight_color
from view_graph_node_shadow import ViewGraphNodeShadow
from strip_underscore import strip_underscore
from main_graph_undo_redo import track_undo_press, track_undo_release

class ViewGraphNode(QGraphicsItem):

    def __init__(self, parent_box, gry_node):
        super().__init__()
        self.gry_node = gry_node

        self.node_id = gry_node["id"]
        self.label = strip_underscore(gry_node["label"])
        if "x" in gry_node:
            self.setPos(QPointF(gry_node["x"], gry_node["y"]))

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self._is_hovered = False

        # MP graph attributes
        self.edge_list = []

        # shadow
        self.view_graph_node_shadow = ViewGraphNodeShadow(self)

        # appearance
        self.reset_appearance()

        # Now that appearance variables exist, set the parent, which calls
        # boundingRect.
        self.setParentItem(parent_box)
        self.view_graph_node_shadow.setParentItem(parent_box)

    # export
    def get_gry_node(self):
        self.gry_node["x"] = self.x()
        self.gry_node["y"] = self.y()
        return self.gry_node

    # adjust for appearance change
    def reset_appearance(self):
        self.w = settings["graph_node_width"]
        self.h = settings["graph_node_height"]
        self.corner_rounding = settings["graph_node_corner_rounding"]
        self.use_border = settings["graph_node_use_border"]

        # set gradient between upper-left and lower-right
        self.gradient = QLinearGradient(-self.w/2, -self.h/2,
                                        self.w/2, self.h/2)

        # increase node height if node's label does not fit
        text_h = margined_text_height(self.label, self.w)
        self.h = max(text_h, self.h)

        # path region for mouse detection
        self.mouse_path = QPainterPath()
        self.mouse_path.addRect(-self.w/2, -self.h/2, self.w, self.h)

        # define decoration for this node CW from upper-left
        self.box = QRectF(-self.w/2, -self.h/2, self.w, self.h)

        # background color
        self.color = QColor(settings["graph_node_color"])

        # annotation color
        self.annotation_color = contrasting_color(self.color)

        # border color
        self.border_color = QColor(contrasting_color(QColor(
                                              settings["background_color"])))

        # bounding rectangle
        pen_width = 1
        self.bounding_rectangle = QRectF(
                       (-self.w - pen_width)/2, (-self.h - pen_width)/2,
                       self.w + pen_width, self.h + pen_width)

        # changing appearance may change node's bounding rectangle
        self.prepareGeometryChange()

        # reset shadow attributes
        self.view_graph_node_shadow.reset_appearance()

    def type(self):
        return VIEW_GRAPH_NODE_TYPE

    def add_edge(self, edge):
        self.edge_list.append(edge)

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounding_rectangle

    # mouse hovers when inside this rectangle
    def shape(self):
        return self.mouse_path

    def paint(self, painter, _option, _widget):
        painter.save()

        # box gradient
        if self._is_hovered:
            c2 = highlight_color(self.color)
        else:
            c2 = self.color
            c2 = self.color
        c1 = c2.lighter(settings["graph_node_color_gradient"])
        c3 = c2.darker(settings["graph_node_color_gradient"])
        self.gradient.setColorAt(0, c1)
        self.gradient.setColorAt(0.5, c2)
        self.gradient.setColorAt(1, c3)

        # box
        painter.setBrush(QBrush(self.gradient))
        if self.use_border:
            painter.setPen(QPen(self.border_color, 0))
        else:
            painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawRoundedRect(self.box, self.corner_rounding,
                                          self.corner_rounding)

        # box text
        painter.setPen(QPen(self.annotation_color, 0))
        paint_margined_text(painter, self.box, self.label)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRoundedRect(self.box, self.corner_rounding,
                                              self.corner_rounding)

        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:

            # move shadow
            self.view_graph_node_shadow.setPos(self.pos())

            for edge in self.edge_list:
                edge.reset_appearance()

            # maybe move grips to match node position change
            # if we are here because positions are not established yet
            # then scene will be Null
            if self.scene():
                self.scene().edge_grip_manager.maybe_move_grips()

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        # track potential move
        track_undo_press(self, event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # maybe record move
        track_undo_release(self, "graph node", event)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()

