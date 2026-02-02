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
from settings import settings, preferred_pen
from color_helper import contrasting_color, highlight_color
from graph_constants import VIEW_AD_NODE_TYPE
from font_helper import margined_text_height, text_width, \
                        paint_margined_text, HORIZONTAL_PADDING
from strip_underscore import strip_underscore
from main_graph_undo_redo import track_undo_press, track_undo_release

START_TYPE = "s"
END_TYPE = "e"
DECISION_TYPE = "d"
ACTION_TYPE = "a"
BAR_TYPE = "b"
_NODE_TYPE_SET = {START_TYPE, END_TYPE, DECISION_TYPE, ACTION_TYPE, BAR_TYPE}

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
        self.old_position = self.pos()
        if "label" in gry_node:
            self.label = strip_underscore(gry_node["label"])
        if "bar_width" in gry_node:
            self.tg_bar_width = gry_node["bar_width"] # typically 1, 2, or 3

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self._is_hovered = False

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

    def spans_x(self, x):
        return (x >= self.x() - self.w / 2) and (x <= self.x() + self.w / 2)

    def spans_y(self, y):
        return (y >= self.y() - self.h / 2) and (y <= self.y() + self.h / 2)

    def _reset_appearance_start(self):
        self.shape_path = QPainterPath()
        r = settings["ad_start_size"] / 2
        self.shape_path.addEllipse(QPointF(0, 0), r, r)
        self.border_pen = _border_pen(settings["ad_start_use_border"])
        self.fill_color = QColor(settings["ad_start_color"])
        self.r = r

        # for edge
        self.w = r * 2
        self.h = self.w

    def _reset_appearance_end(self):
        self.shape_path = QPainterPath()
        r = settings["ad_end_size"] / 2
        self.shape_path.addEllipse(QPointF(0, 0), r, r)
        self.border_pen = _border_pen(settings["ad_end_use_border"])
        self.fill_color = QColor(settings["ad_end_color"])
        self.r = r

        # for edge
        self.w = r * 2
        self.h = self.w

    def _reset_appearance_decision(self):
        path = QPainterPath()
        w = settings["ad_decision_width"]
        h = settings["ad_decision_height"]
        path.moveTo(w/2,0) # diamond shape
        path.lineTo(0,h/2)
        path.lineTo(-w/2,0)
        path.lineTo(0,-h/2)
        path.lineTo(w/2,0)
        self.shape_path = path
        self.border_pen = _border_pen(settings["ad_decision_use_border"])
        self.fill_color = QColor(settings["ad_decision_color"])
        self.w = w
        self.h = h

    def _reset_appearance_action(self):
        self.border_pen = _border_pen(settings["ad_action_use_border"])
        self.fill_color = QColor(settings["ad_action_color"])
        self.w = settings["ad_action_width"]
        self.h = settings["ad_action_height"]
        self.corner_rounding = settings["ad_action_corner_rounding"]

        # increase node height if node's label does not fit
        text_h = margined_text_height(self.label, self.w)
        self.h = max(text_h, self.h)

        # gradient between upper-left and lower-right
        self.gradient = QLinearGradient(-self.w/2, -self.h/2,
                                        self.w/2, self.h/2)

        # annotation pen
        self.annotation_pen = contrasting_color(
                                    QColor(settings["ad_action_color"]))

        # shape and bounds
        self.shape_path = QPainterPath()
        r = self.corner_rounding
        self.shape_path.addRoundedRect(-self.w/2, -self.h/2, self.w, self.h,
                                                                     r, r)

    def _reset_appearance_bar(self):
        self.w = max((self.tg_bar_width - 1) * settings["ad_h_spacing"]
                                           + settings["ad_bar_width"],
                     text_width(self.label) + HORIZONTAL_PADDING)
        self.h = settings["ad_bar_height"]
        self.shape_path = QPainterPath()
        self.shape_path.addRect(-self.w/2, -self.h/2, self.w, self.h)
        self.border_pen = _border_pen(settings["ad_bar_use_border"])
        self.fill_color = QColor(settings["ad_bar_color"])
        self.annotation_pen = contrasting_color(
                                    QColor(settings["ad_bar_color"]))

    # adjust for appearance change
    def reset_appearance(self):
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

        # bounding rectangle
        pen_width = 1
        self.bounding_rect = self.shape_path.boundingRect().adjusted(
                      -pen_width/2, -pen_width/2, pen_width/2, pen_width/2)

        # changing appearance may change node's bounding rectangle
        self.prepareGeometryChange()

        # adjust edges
        for edge in self.edge_list:
            _changes = edge.change_edge_vector(
                                        edge.edge_start, edge.edge_vector)

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

    def _paint_start(self, painter, fill_color):
        painter.setPen(self.border_pen)
        painter.setBrush(QBrush(fill_color))
        r = settings["ad_start_size"] / 2
        painter.drawEllipse(QPointF(0, 0), r, r)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawEllipse(QPointF(0, 0), r, r)

    def _paint_end(self, painter, fill_color):
        r = settings["ad_end_size"] / 2
        r_inner = r * 0.6
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(fill_color))
        painter.drawEllipse(QPointF(0, 0), r_inner, r_inner)
        painter.setPen(QPen(fill_color))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawEllipse(QPointF(0, 0), r, r)
        painter.setPen(self.border_pen)
        painter.drawEllipse(QPointF(0, 0), r + 0.5, r + 0.5)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawEllipse(QPointF(0, 0), r + 0.5, r + 0.5)

    def _paint_decision(self, painter, fill_color):
        painter.setPen(self.border_pen)
        painter.setBrush(QBrush(fill_color))
        painter.drawPath(self.shape_path)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawPath(self.shape_path)

    def _paint_action(self, painter, fill_color):
        c2 = fill_color
        c1 = c2.lighter(settings["ad_action_color_gradient"])
        c3 = c2.darker(settings["ad_action_color_gradient"])
        self.gradient.setColorAt(0, c1)
        self.gradient.setColorAt(0.5, c2)
        self.gradient.setColorAt(1, c3)

        painter.setPen(self.border_pen)
        painter.setBrush(QBrush(self.gradient))
        painter.drawPath(self.shape_path)
        painter.setPen(self.annotation_pen)
        paint_margined_text(painter, self.bounding_rect, self.label)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawPath(self.shape_path)

    def _paint_bar(self, painter, fill_color):
        painter.setPen(self.border_pen)
        painter.setBrush(QBrush(fill_color))
        painter.drawPath(self.shape_path)
        painter.setPen(self.annotation_pen)
        painter.drawText(self.bounding_rect, Qt.AlignmentFlag.AlignCenter,
                                                        self.label)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawPath(self.shape_path)

    def paint(self, painter, option, widget):
        painter.save()

        # fill color
        if self._is_hovered:
            fill_color = highlight_color(self.fill_color)
        else:
            fill_color = self.fill_color
        if self.node_type == START_TYPE:
            self._paint_start(painter, fill_color)
        elif self.node_type == END_TYPE:
            self._paint_end(painter, fill_color)
        elif self.node_type == DECISION_TYPE:
            self._paint_decision(painter, fill_color)
        elif self.node_type == ACTION_TYPE:
            self._paint_action(painter, fill_color)
        elif self.node_type == BAR_TYPE:
            self._paint_bar(painter, fill_color)
        else:
            raise RuntimeError("bad")
        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # manage delta position
            delta_position = value - self.old_position
            dx, dy = delta_position.x(), delta_position.y()
            self.old_position = value

            for edge in self.edge_list:
                edge.move_edge_because_node_moved(self, dx, dy)

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        # track potential move
        track_undo_press(self, event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # maybe record move
        track_undo_release(self, "AD node", event)
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()

