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
from font_helper import bound_text_height
from trace_collapse_helpers import at_and_below_in
from node_menu import NodeMenu
from graph_constants import NODE_TYPE

# Node
class Node(QGraphicsItem):

    def __init__(self, parent_box, gry_node, trace):
        super().__init__()
        self.node_id = gry_node["id"]
        self.node_type = gry_node["type"]
        self.label = gry_node["label"]
        self.setPos(QPointF(gry_node["x"], gry_node["y"]))
        self.hide = gry_node["hide"]
        self.collapse = gry_node["collapse"]
        self.collapse_below = gry_node["collapse_below"]

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.show_menu_icon = False

        self.setZValue(1)

        # MP graph attributes
        self.edge_list = []

        # handle back for menus
        self.trace = trace

        # appearance
        self.reset_appearance()

        self.setParentItem(parent_box)

    # export
    def get_gry(self):
        gry_node = dict()
        gry_node["id"] = self.node_id
        gry_node["type"] = self.node_type
        gry_node["label"] = self.label
        gry_node["x"] = self.x()
        gry_node["y"] = self.y()
        gry_node["hide"] = self.hide
        gry_node["collapse"] = self.collapse
        gry_node["collapse_below"] = self.collapse_below
        return gry_node

    # adjust for appearance change
    def reset_appearance(self):
        self.w = settings["trace_node_width"]
        self.h = settings["trace_node_height"]
        self.s = 3  # shadow size
        self.t = 12  # tab fold size
        self.node_border = settings["trace_node_use_border"]
        self.node_shadow = settings["trace_node_use_shadow"]

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
        text_h = bound_text_height(self.label, self.w)
        if text_h > self.h:
            self.h = text_h

        # path region for mouse detection
        self.mouse_path = QPainterPath()
        self.mouse_path.addRect(-self.w/2, -self.h/2, self.w, self.h)

        # define decoration for this node
        self.right_shadow = QRectF(self.w/2, -self.h/2+self.s, self.s, self.h)
        # CW from upper-left
        self.right_shadow_say = QPolygonF(
                          [QPointF(+self.w/2, -self.h/2+self.t),
                           QPointF(+self.w/2+self.s, -self.h/2+self.t+self.s),
                           QPointF(+self.w/2+self.s, +self.h/2+self.s),
                           QPointF(+self.w/2, +self.h/2+self.s)])
        self.bottom_shadow = QRectF(-self.w/2+self.s, self.h/2, self.w, self.s)
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
        self.c1 = c.lighter(settings["trace_node_color_gradient"])
        self.c2 = c
        self.c3 = c.darker(settings["trace_node_color_gradient"])

        # annotation color
        self.annotation_color = QColor(text_color_name(c))
        self.annotation_color.setAlpha(self.opacity)

        # menu icon color
        self.menu_icon_color = QColor(Qt.GlobalColor.black)
        self.menu_icon_color.setAlpha(self.opacity)

        # border color
        self.border_color = QColor(text_color_name(QColor(
                                           settings["background_color"])))
        self.border_color.setAlpha(self.opacity)

        # shadow color
        self.shadow_color = QColor(Qt.GlobalColor.darkGray)
        self.shadow_color.setAlpha(self.opacity)

        # collapse_below color
        self.collapse_below_color = QColor(Qt.GlobalColor.darkGray)
        self.collapse_below_color.setAlpha(self.opacity)

        # collapse_below gradient
        self.collapse_below_gradient = QRadialGradient(-3, -3, 10)
        self.collapse_below_gradient.setColorAt(0, self.c2.lighter(125))
        self.collapse_below_gradient.setColorAt(1, self.c2.darker(125))

        # changing appearance may change node's bounding rectangle
        self.prepareGeometryChange()

    def type(self):
        return NODE_TYPE

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
            if self.node_type == "T": # SAY message has right tab fold
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(self.shadow_color)
                painter.drawPolygon(self.right_shadow_say)
            else:
                painter.fillRect(self.right_shadow, self.shadow_color)
            painter.fillRect(self.bottom_shadow, self.shadow_color)

        # box
        painter.setBrush(QBrush(self.gradient))
        if self.node_border:
            painter.setPen(QPen(self.border_color, 0))
        else:
            painter.setPen(QPen(Qt.PenStyle.NoPen))
        if self.node_type == "T": # SAY message has right tab fold
            painter.drawConvexPolygon(self.tbox)
            painter.drawPolyline(self.tbox_inset)
        else:
            painter.drawRect(self.box)

        # menu icon
        if self.show_menu_icon:
            painter.setPen(QPen(self.menu_icon_color, 1,
                                          c=Qt.PenCapStyle.RoundCap))
            mx, my, mw, mh = self.menu_bounds()
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
        painter.drawText(self.box,
                         Qt.AlignmentFlag.AlignCenter|Qt.TextFlag.TextWordWrap,
                         self.label)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(self.box)

        painter.restore()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edge_list:
                edge.reset_appearance()

            # change shape of enclosing box
            self.parentItem().itemChange(change, value)

        return super(Node, self).itemChange(change, value)

    def mousePressEvent(self, event):
        # select all under IN if SHIFT key is down
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            node_set = at_and_below_in(self)
            for node in node_set:
                node.setSelected(True)

        self.moved = False # may show menu if False
        super(Node, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.moved = True # may show menu if False
        super(Node, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        # show menu if not moved, in menu icon, and no keyboard modifier
        clicked_icon = False
        if not self.moved and event.modifiers() \
                              == Qt.KeyboardModifier.NoModifier:
            x = event.pos().x()
            y = event.pos().y()
            extra_border = 4
            mx, my, mw, mh = self.menu_bounds()
            if x<=mx+mw+2 + extra_border and y <= my+mh + extra_border:
                self.show_menu()
                clicked_icon = True

        # note selection state before running mouse release in parent
        selected_nodes = list()
        for node in self.trace.nodes:
            if node.isSelected():
                selected_nodes.append(node)

        # run mouse release in parent
        super(Node, self).mouseReleaseEvent(event)

        # restore selection as needed
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier \
                                                    or clicked_icon:
            # keep selections by undoing what the parent did
            for node in selected_nodes:
                node.setSelected(True)

    def hoverEnterEvent(self, _event):
        # Hack: When the menu closes, Qt restores _event position and
        # fires enter event even thouguh the cursor is away from the
        # node.  We get around this by ensuring that the screen and
        # cursor positions match.
        if _event.screenPos() == QCursor.pos():
            self.show_menu_icon = True
            self.update()

    def hoverLeaveEvent(self, _event):
        self.show_menu_icon = False
        self.update()

    # right-click shows menu
    def contextMenuEvent(self, event):
        if event.reason() == QGraphicsSceneContextMenuEvent.Reason.Mouse:
            self.show_menu()

    def menu_bounds(self):
        mx = -self.w//2+2
        my = -self.h//2+3
        mw = 7
        mh = 9
        return (mx, my, mw, mh)

    def show_menu(self):
        menu = NodeMenu()
        menu.show_menu(self.trace, self)

