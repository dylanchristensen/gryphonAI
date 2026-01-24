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
from color_helper import contrasting_color, highlight_color
from font_helper import margined_text_height, paint_margined_text
from trace_collapse_helpers import at_and_below_in
from node_menu import NodeMenu
from graph_constants import NODE_TYPE
from node_shadow import NodeShadow
from strip_underscore import strip_underscore
from os_compatibility import pure_left_button_down, pure_right_button_down
from main_graph_undo_redo import track_undo_press, track_undo_release

# Node
class Node(QGraphicsItem):

    def __init__(self, parent_box, gry_node, trace):
        super().__init__()
        self.gry_node = gry_node

        self.node_id = gry_node["id"]
        self.node_type = gry_node["type"]
        self.label = strip_underscore(gry_node["label"])
        self.setPos(QPointF(gry_node["x"], gry_node["y"]))
        self.hide = gry_node["hide"]
        self.collapse = gry_node["collapse"]
        self.collapse_below = gry_node["collapse_below"]

        # put node above edges
        self.setZValue(2)

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self._is_hovered = False

        # MP graph attributes
        self.edge_list = []

        # handle back for menus
        self.trace = trace

        # circle and box shadows
        self.shadow_color = QColor(Qt.GlobalColor.darkGray)

        # node shadow
        self.node_shadow = NodeShadow(self)

        # appearance
        self.reset_appearance()

        self.setParentItem(parent_box)
        self.node_shadow.setParentItem(parent_box)

    # export
    def get_gry(self):
        self.gry_node["x"] = self.x()
        self.gry_node["y"] = self.y()
        self.gry_node["hide"] = self.hide
        self.gry_node["collapse"] = self.collapse
        self.gry_node["collapse_below"] = self.collapse_below
        return self.gry_node

    # adjust for appearance change
    def reset_appearance(self):
        self.w = settings["trace_node_width"]
        self.h = settings["trace_node_height"]
        self.t = 12  # tab fold size
        self.use_border = settings["trace_node_use_border"]

        # set opacity
        if self.hide or self.collapse:
            self.opacity = settings["trace_hide_collapse_opacity"]
        else:
            # totally opaque
            self.opacity = 255

        # set gradient between upper-left and lower-right
        self.gradient = QLinearGradient(-self.w/2, -self.h/2,
                                        self.w/2, self.h/2)

        # increase node height if node's label does not fit
        text_h = margined_text_height(self.label, self.w)
        if text_h > self.h:
            self.h = text_h

        # path region for mouse detection
        self.mouse_path = QPainterPath()
        self.mouse_path.addRect(-self.w/2, -self.h/2, self.w, self.h)

        # define decoration for this node
        self.box = QRectF(-self.w/2, -self.h/2, self.w, self.h)
        # CW from upper-left
        self.tbox = QPolygonF([QPointF(-self.w/2, -self.h/2),
                               QPointF(+self.w/2-self.t, -self.h/2),
                               QPointF(+self.w/2, -self.h/2+self.t),
                               QPointF(+self.w/2, +self.h/2),
                               QPointF(-self.w/2, +self.h/2)])
        self.tbox_inset = QPolygonF([QPointF(self.w/2-self.t, -self.h/2),
                                     QPointF(self.w/2-self.t, -self.h/2+self.t),
                                     QPointF(self.w/2, -self.h/2+self.t)])

        # background color
        if self.node_type == "R": # root
            c = QColor(settings["trace_node_root_color"])
        elif self.node_type == "A": # atomic
            c = QColor(settings["trace_node_atomic_color"])
        elif self.node_type == "C": # composite
            c = QColor(settings["trace_node_composite_color"])
        elif self.node_type == "S": # schema
            c = QColor(settings["trace_node_schema_color"])
        elif self.node_type == "T": # say
            c = QColor(settings["trace_node_say_color"])
        else:
            print("unrecognized node type '%s'" % self.node_type)
            c = Qt.GlobalColor.darkGray
        # opacity
        c.setAlpha(self.opacity)
        self.color = c

        # annotation color
        self.annotation_color = contrasting_color(c)
        self.annotation_color.setAlpha(self.opacity)

        # menu icon color
        self.menu_icon_color = QColor(Qt.GlobalColor.black)
        self.menu_icon_color.setAlpha(self.opacity)

        # border color
        self.border_color = contrasting_color(QColor(
                                           settings["background_color"]))
        self.border_color.setAlpha(self.opacity)

        # node and collapse-below circle shadow color
        self.shadow_color.setAlpha(self.opacity)

        # bounding rectangle
        pen_width = 1
        self.bounding_rectangle = QRectF(
                       (-self.w - pen_width)/2, (-self.h - pen_width)/2,
                       self.w + pen_width, self.h + pen_width)

        # collapse_below color
        self.collapse_below_color = QColor(Qt.GlobalColor.darkGray)
        self.collapse_below_color.setAlpha(self.opacity)

        # collapse_below gradient
        self.collapse_below_gradient = QRadialGradient(-3, -3, 10)
        self.collapse_below_gradient.setColorAt(0, self.color.lighter(125))
        self.collapse_below_gradient.setColorAt(1, self.color.darker(125))

        # changing appearance may change node's bounding rectangle
        self.prepareGeometryChange()

        # shadow attributes
        self.node_shadow.reset_appearance()

    def type(self):
        return NODE_TYPE

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
        c1 = c2.lighter(settings["trace_node_color_gradient"])
        c3 = c2.darker(settings["trace_node_color_gradient"])
        self.gradient.setColorAt(0, c1)
        self.gradient.setColorAt(0.5, c2)
        self.gradient.setColorAt(1, c3)

        # box
        painter.setBrush(QBrush(self.gradient))
        if self.use_border:
            painter.setPen(QPen(self.border_color, 0))
        else:
            painter.setPen(QPen(Qt.PenStyle.NoPen))
        if self.node_type == "T": # SAY message has right tab fold
            painter.drawConvexPolygon(self.tbox)
            painter.drawPolyline(self.tbox_inset)
        else:
            painter.drawRect(self.box)

        # menu icon
        if self._is_hovered:
            painter.setPen(QPen(self.menu_icon_color, 1,
                                          c=Qt.PenCapStyle.RoundCap))
            mx, my, mw, mh = self._menu_bounds()
            spacing = mh//3
            for i in range(3):
                painter.drawLine(mx, my+i*spacing, mx+mw, my+i*spacing)

        # collapse_below icon
        if self.collapse_below:
            # move painter to center of icon near top-right corner
            painter.save()
            painter.translate(self.w/2 - 7, -self.h/2 + 7)

            # draw circle shadow
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.shadow_color)
            painter.drawEllipse(-5.8, -5.8, 12, 12)

            # draw circle
            painter.setBrush(QBrush(self.collapse_below_gradient))
            painter.setPen(QPen(self.border_color, 0))
            painter.drawEllipse(-6, -6, 12, 12)
            painter.restore()

        # box text
        painter.setPen(QPen(self.annotation_color, 0))
        paint_margined_text(painter, self.box, self.label)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(self.box)

        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:

            # move shadow
            self.node_shadow.setPos(self.pos())

            # move edge positions
            for edge in self.edge_list:
                edge.reset_appearance()

            # maybe move grips to match node position change
            # Horizontal and vertical spacing changes made to all traces
            # impact nodes that are not assigned to a scene so make sure
            # the node is assigned to a scene.
            if self.scene():
                self.scene().edge_grip_manager.maybe_move_grips()

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super(Node, self).itemChange(change, value)

    def _menu_bounds(self):
        mx = -self.w//2+2
        my = -self.h//2+3
        mw = 7
        mh = 9
        return (mx, my, mw, mh)

    def _is_over_menu_icon(self, event):
        x = event.pos().x()
        y = event.pos().y()
        extra_border = 4
        mx, my, mw, mh = self._menu_bounds()
        return x<=mx+mw+2 + extra_border and y <= my+mh + extra_border

    def mousePressEvent(self, event):
        # move starts on left button press with no other button down
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.did_move = False

        # open the menu on left click over menu icon
        if pure_left_button_down(event) and self._is_over_menu_icon(event):
            NodeMenu(self, event)
            return

        # open the menu on right click
        if pure_right_button_down(event):
            NodeMenu(self, event)
            return

        # track potential move
        track_undo_press(self, event)
    
        # perform selection where SHIFT can impact nodes below IN relation
        self.selected_before_press = self.isSelected()

        # if SHIFT is down then add all nodes under IN
        if bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            node_set = at_and_below_in(self)
            for node in node_set:
                node.setSelected(True)

        # now apply built-in rules for no event modifiers or SHIFT and CTRL
        super(Node, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.did_move = True
        super(Node, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        # apply built-in selections
        super(Node, self).mouseReleaseEvent(event)

        # maybe record move
        track_undo_release(self, "trace node", event)

        # if node moved or no SHIFT then keep built-in selections
        if self.did_move or not bool(event.modifiers()
                                     & Qt.KeyboardModifier.ShiftModifier):
            return

        # node did not move and shift was pressed so select IN nodes
        # based on CTRL and previous selection
        node_set = at_and_below_in(self)
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # toggle selection at and below IN relation
            for node in node_set:
                node.setSelected(not self.selected_before_press)
        else:
            # no CTRL so keep selection at and below IN relation selected
            for node in node_set:
                node.setSelected(True)

        return

    def hoverEnterEvent(self, _event):
        self._is_hovered = True
        self.update()

    def hoverLeaveEvent(self, _event):
        self._is_hovered = False
        self.update()

