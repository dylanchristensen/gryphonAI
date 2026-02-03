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
from settings_manager import settings
from color_helper import text_color_name
from node_menu import NodeMenu
from graph_constants import VIEW_GRAPH_NODE_TYPE
from font_helper import bound_text_height

class ViewGraphNode(QGraphicsItem):

    def __init__(self, parent_box, gry_node):
        super().__init__()
        self.node_id = gry_node["id"]
        self.label = gry_node["label"]
        if "x" in gry_node:
            self.setPos(QPointF(gry_node["x"], gry_node["y"]))

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.setZValue(1)

        # MP graph attributes
        self.edge_list = []

        # appearance
        self.reset_appearance()

        self.setParentItem(parent_box)

    # export
    def get_gry_node(self):
        gry_node = dict()
        gry_node["id"] = self.node_id
        gry_node["label"] = self.label
        gry_node["x"] = self.x()
        gry_node["y"] = self.y()
        return gry_node

    # adjust for appearance change
    def reset_appearance(self):
        self.w = settings["graph_node_width"]
        self.h = settings["graph_node_height"]
        self.corner_rounding = settings["graph_node_corner_rounding"]
        self.s = 3  # shadow size
        self.node_border = settings["graph_node_use_border"]
        self.node_shadow = settings["graph_node_use_shadow"]

        # set gradient between upper-left and lower-right
        self.gradient = QLinearGradient(-self.w/2, -self.h/2,
                                        self.w/2, self.h/2)

        # increase node height if node's label does not fit
        text_h = bound_text_height(self.label, self.w)
        self.h = max(text_h, self.h)

        # path region for mouse detection
        self.mouse_path = QPainterPath()
        self.mouse_path.addRect(-self.w/2, -self.h/2, self.w, self.h)

        # define decoration for this node
        self.right_shadow = QRectF(self.w/2, -self.h/2+self.s, self.s, self.h)
        # CW from upper-left
        self.bottom_shadow = QRectF(-self.w/2+self.s, self.h/2, self.w, self.s)
        self.box = QRectF(-self.w/2, -self.h/2, self.w, self.h)

        # background color
        c = QColor(settings["graph_node_color"])
        self.c1 = c.lighter(settings["graph_node_color_gradient"])
        self.c2 = c
        self.c3 = c.darker(settings["graph_node_color_gradient"])


        # annotation color
        self.annotation_color = QColor(text_color_name(c))

        # border color
        self.border_color = QColor(text_color_name(QColor(
                                              settings["background_color"])))

        # shadow color
        self.shadow_color = QColor(Qt.GlobalColor.darkGray)

        # changing appearance may change node's bounding rectangle
        self.prepareGeometryChange()

    def type(self):
        return VIEW_GRAPH_NODE_TYPE

    def add_edge(self, edge):
        self.edge_list.append(edge)

    # draw inside this rectangle
    def boundingRect(self):
        adjust = 2
        return QRectF(-self.w/2 - adjust, -self.h/2 - adjust,
                      self.w+self.s + adjust, self.h+self.s + adjust)

    # mouse hovers when inside this rectangle
    def shape(self):
        return self.mouse_path

    def paint(self, painter, _option, _widget):
        painter.save()

        # box gradient
        if self.isSelected():
            self.gradient.setColorAt(0, self.c1.lighter(125))
            self.gradient.setColorAt(0.5, self.c2.lighter(125))
            self.gradient.setColorAt(1, self.c3.lighter(125))
        else:
            self.gradient.setColorAt(0, self.c1)
            self.gradient.setColorAt(0.5, self.c2)
            self.gradient.setColorAt(1, self.c3)

        # box shadow
        if self.node_shadow:
            painter.fillRect(self.right_shadow, self.shadow_color)
            painter.fillRect(self.bottom_shadow, self.shadow_color)

        # box
        painter.setBrush(QBrush(self.gradient))
        if self.node_border:
            painter.setPen(QPen(self.border_color, 0))
        else:
            painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawRoundedRect(self.box, self.corner_rounding,
                                          self.corner_rounding)

        # box text
        painter.setPen(QPen(self.annotation_color, 0))
        painter.drawText(self.box, Qt.AlignmentFlag.AlignCenter |
                               Qt.TextFlag.TextWordWrap, self.label)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRoundedRect(self.box, self.corner_rounding,
                                              self.corner_rounding)

        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edge_list:
                edge.reset_appearance()

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super().itemChange(change, value)

