from math import sin, cos, atan2
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import (QBrush, QColor, QLinearGradient,
                         QPainterPath, QPen, QPolygonF, QRadialGradient)
from PySide6.QtGui import QFontMetrics
from PySide6.QtGui import QFont
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from settings_manager import settings, preferred_pen
from color_helper import text_color_name, node_text_pen
from node_menu import NodeMenu
from graph_constants import VIEW_AD_NODE_TYPE
from font_helper import bound_text_height, text_width

START_TYPE = "s"
END_TYPE = "e"
DECISION_TYPE = "d"
ACTION_TYPE = "a"
BAR_TYPE = "b"
_NODE_TYPE_SET = {START_TYPE, END_TYPE, DECISION_TYPE, ACTION_TYPE, BAR_TYPE}

START_RADIUS = 12
END_INNER_RADIUS = 12
END_OUTER_RADIUS = 16

# return closest point on diamond at diamond corner and h or v approach
def _diamond_xy(x, y, node_x, node_y, w, h):
    dx = x - node_x
    abs_dx = abs(dx)
    dy = y - node_y
    abs_dy = abs(dy)
    if dx >= 0 and abs_dx >= abs_dy:
        return node_x + w, node_y, "h"
    elif dy >= 0 and abs_dy >= abs_dx:
        return node_x, node_y + h, "v"
    elif dx <= 0 and abs_dx >= abs_dy:
        return node_x - w, node_y, "h"
    elif dy <= 0 and abs_dy >= abs_dx:
        return node_x, node_y - h, "v"
    else:
        # not worth RuntimeError
        print("view_ad_node unexpected point")
        return node_x, node_y, "v"

# return closest point on circle
def _round_xy(x, y, node_x, node_y, w, h):
    theta = atan2(y - node_y, x - node_x)
    return node_x + cos(theta) * w, node_y + sin(theta) * h

def _border_pen(use_border_pen):
    if use_border_pen:
       return QPen(preferred_pen().color(), 0)
    else:
       return QPen(Qt.PenStyle.NoPen)

# Activity Diagram node
class ViewADNode(QGraphicsItem):

    def __init__(self, parent_box, gry_node):
        super().__init__()
        self.gry_node = gry_node
        self.node_type = gry_node["node_type"]
        if not self.node_type in _NODE_TYPE_SET:
            # fail if type is invalid
            print("bad", gry_node)
            raise RuntimeError("bad AD node")
        self.node_id = gry_node["node_id"]
        self.setPos(QPointF(gry_node["x"], gry_node["y"]))
        if "label" in gry_node:
            self.label = gry_node["label"]
        if "bar_width" in gry_node:
            self.tg_bar_width = gry_node["bar_width"] # typically 1, 2, or 3

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
        self.gry_node["x"] = self.x()
        self.gry_node["y"] = self.y()
        return self.gry_node

    def _reset_appearance_start(self):
        self.shape_path = QPainterPath()
        r = settings["ad_start_size"] / 2
        self.shape_path.addEllipse(QPointF(0, 0), r, r)
        self.bounding_rect = self.shape_path.boundingRect()
        self.border_pen = _border_pen(settings["ad_start_use_border"])
        self.fill_brush = QBrush(QColor(settings["ad_start_color"]))
        self.r = r

    def _reset_appearance_end(self):
        self.shape_path = QPainterPath()
        r = settings["ad_end_size"] / 2
        self.shape_path.addEllipse(QPointF(0, 0), r, r)
        self.bounding_rect = self.shape_path.boundingRect()
        self.border_pen = _border_pen(settings["ad_end_use_border"])
        self.fill_brush = QBrush(QColor(settings["ad_end_color"]))
        self.r = r

    def _reset_appearance_decision(self):
        path = QPainterPath()
        w = settings["ad_decision_width"] / 2
        h = settings["ad_decision_height"] / 2
        path.moveTo(w,0) # diamond shape
        path.lineTo(0,h)
        path.lineTo(-w,0)
        path.lineTo(0,-h)
        path.lineTo(w,0)
        self.shape_path = path
        self.bounding_rect = self.shape_path.boundingRect()
        self.border_pen = _border_pen(settings["ad_decision_use_border"])
        self.fill_brush = QBrush(QColor(settings["ad_decision_color"]))
        self.w = w
        self.h = h

    def _reset_appearance_action(self):
        self.border_pen = QPen() # not used
        self.fill_brush = QBrush() # not used
        self.w = settings["ad_action_width"]
        self.h = settings["ad_action_height"]
        self.corner_rounding = settings["ad_action_corner_rounding"]

        # increase node height if node's label does not fit
        text_h = bound_text_height(self.label, self.w)
        self.h = max(text_h, self.h)

        # background color
        c = QColor(settings["ad_action_color"])
        self.c1 = c.lighter(settings["ad_action_color_gradient"])
        self.c2 = c
        self.c3 = c.darker(settings["ad_action_color_gradient"])

        # gradient between upper-left and lower-right
        self.gradient = QLinearGradient(-self.w/2, -self.h/2,
                                        self.w/2, self.h/2)

        # annotation pen
        self.annotation_pen = node_text_pen(settings["ad_action_color"])

        # shape and bounds
        self.shape_path = QPainterPath()
        r = self.corner_rounding
        self.shape_path.addRoundedRect(-self.w/2, -self.h/2, self.w, self.h,
                                                                     r, r)
        self.bounding_rect = self.shape_path.boundingRect()

    def _reset_appearance_bar(self):
        self.w = max((self.tg_bar_width - 1) * settings["ad_h_spacing"]
                                           + settings["ad_bar_width"],
                     text_width(self.label))
        self.h = settings["ad_bar_height"]
        self.shape_path = QPainterPath()
        self.shape_path.addRect(-self.w/2, -self.h/2, self.w, self.h)
        self.bounding_rect = self.shape_path.boundingRect()
        self.border_pen = _border_pen(settings["ad_bar_use_border"])
        self.fill_brush = QBrush(QColor(settings["ad_bar_color"]))
        self.annotation_pen = node_text_pen(settings["ad_bar_color"])

    # adjust for appearance change
    def reset_appearance(self):
        self.preferred_pen = preferred_pen()
        if self.node_type == START_TYPE:
            self._reset_appearance_start()
        elif self.node_type == END_TYPE:
            self._reset_appearance_end()
        elif self.node_type == DECISION_TYPE:
            self._reset_appearance_decision()
        elif self.node_type == ACTION_TYPE:
            self._reset_appearance_action()
        elif self.node_type == BAR_TYPE:
            self._reset_appearance_bar()
        else:
            raise RuntimeError("bad")

        # adjust to draw inside
        adjust = 1
        self.bounding_rect.adjust(-adjust, -adjust, adjust, adjust)

        # changing appearance may change node's bounding rectangle
        self.prepareGeometryChange()

    # provide a snap point on the node given an approach-from point
    # and whether the flow is to or from the node
    # returns: tuple snap_point, expected "h" or "v" approach at snap_point
    # returns a right-angle-aligned placer snap point along with h or v approach
    def placer_snap_point(self, point, is_to):
        x = point.x()
        y = point.y()
        if self.node_type == START_TYPE:
            node_x, node_y, h_or_v_approach = _diamond_xy(
                                   x, y, self.x(), self.y(), self.r, self.r)
        elif self.node_type == END_TYPE:
            node_x, node_y, h_or_v_approach = _diamond_xy(
                                   x, y, self.x(), self.y(), self.r, self.r)
        elif self.node_type == DECISION_TYPE:
            node_x, node_y, h_or_v_approach = _diamond_xy(
                                   x, y, self.x(), self.y(), self.w, self.h)
        elif self.node_type == ACTION_TYPE:
            node_x = self.x()
            if is_to:
                node_y = self.y() - self.h / 2
            else:
                node_y = self.y() + self.h / 2
            h_or_v_approach = "v"
        elif self.node_type == BAR_TYPE:
            left_x = self.x() - self.w / 2
            right_x = self.x() + self.w / 2
            if x < left_x:
                node_x = left_x
            elif x > right_x:
                node_x = right_x
            else:
                node_x = x
            if is_to:
                node_y = self.y() - self.h / 2
            else:
                node_y = self.y() + self.h / 2
            h_or_v_approach = "v"
        else:
            raise RuntimeError("bad")
        return QPointF(node_x, node_y), h_or_v_approach

    # returns the run-time snap point which allows non-right-angle for
    # start and end
    def snap_point(self, point, is_to):
        x = point.x()
        y = point.y()
        if self.node_type == START_TYPE:
            node_x, node_y = _round_xy(x, y, self.x(), self.y(),
                                                           self.r, self.r)
        elif self.node_type == END_TYPE:
            node_x, node_y = _round_xy(x, y, self.x(), self.y(),
                                                           self.r, self.r)
        elif self.node_type == DECISION_TYPE:
            node_x, node_y, _approach = _diamond_xy(x, y, self.x(), self.y(),
                                                           self.w, self.h)
        elif self.node_type == ACTION_TYPE:
            node_x = self.x()
            if is_to:
                node_y = self.y() - self.h / 2
            else:
                node_y = self.y() + self.h / 2
        elif self.node_type == BAR_TYPE:
            left_x = self.x() - self.w / 2
            right_x = self.x() + self.w / 2
            if x < left_x:
                node_x = left_x
            elif x > right_x:
                node_x = right_x
            else:
                node_x = x
            if is_to:
                node_y = self.y() - self.h / 2
            else:
                node_y = self.y() + self.h / 2
        else:
            raise RuntimeError("bad")
        return QPointF(node_x, node_y)

    def type(self):
        return VIEW_AD_NODE_TYPE

    def add_edge(self, edge):
        self.edge_list.append(edge)

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounding_rect

    # mouse detects when inside this rectangle
    def shape(self):
        return self.shape_path

    def _paint_start(self, painter, _option, _widget):
        r = settings["ad_start_size"] / 2
        painter.drawEllipse(QPointF(0, 0), r, r)

    def _paint_end(self, painter, _option, _widget):
        r = settings["ad_end_size"] / 2
        r_inner = r * 0.6
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(QPointF(0, 0), r_inner, r_inner)
        painter.setPen(QPen(self.fill_brush.color()))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawEllipse(QPointF(0, 0), r, r)
        painter.setPen(self.border_pen)
        painter.drawEllipse(QPointF(0, 0), r + 0.5, r + 0.5)

    def _paint_decision(self, painter, _option, _widget):
        painter.drawPath(self.shape_path)

    def _paint_action(self, painter, _option, _widget):
        # box gradient
        if self.isSelected():
            self.gradient.setColorAt(0, self.c1.lighter(125))
            self.gradient.setColorAt(0.5, self.c2.lighter(125))
            self.gradient.setColorAt(1, self.c3.lighter(125))
        else:
            self.gradient.setColorAt(0, self.c1)
            self.gradient.setColorAt(0.5, self.c2)
            self.gradient.setColorAt(1, self.c3)

        painter.setBrush(QBrush(self.gradient))
        painter.setPen(_border_pen(settings["ad_action_use_border"]))
        painter.drawPath(self.shape_path)
        annotation_color = QColor(text_color_name(self.c2))
        painter.setPen(self.annotation_pen)
        painter.drawText(self.bounding_rect, Qt.AlignmentFlag.AlignCenter
                         | Qt.TextFlag.TextWordWrap, self.label)

    def _paint_bar(self, painter, _option, _widget):
        painter.drawPath(self.shape_path)
        painter.setPen(self.annotation_pen)
        painter.drawText(self.bounding_rect, Qt.AlignmentFlag.AlignCenter,
                                                        self.label)

    def paint(self, painter, option, widget):
        painter.save()
        painter.setPen(self.border_pen)
        painter.setBrush(self.fill_brush)
        if self.node_type == START_TYPE:
            self._paint_start(painter, option, widget)
        elif self.node_type == END_TYPE:
            self._paint_end(painter, option, widget)
        elif self.node_type == DECISION_TYPE:
            self._paint_decision(painter, option, widget)
        elif self.node_type == ACTION_TYPE:
            self._paint_action(painter, option, widget)
        elif self.node_type == BAR_TYPE:
            self._paint_bar(painter, option, widget)
        else:
            raise RuntimeError("bad")
        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edge_list:
                edge.reset_appearance()

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super().itemChange(change, value)

