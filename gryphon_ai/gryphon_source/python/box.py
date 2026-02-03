from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainterPath, QPainterPathStroker
from PySide6.QtGui import QFont
from PySide6.QtGui import QCursor
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from PySide6.QtWidgets import QMenu
from graph_constants import BOX_TYPE
from settings_manager import emit_signal_settings_changed, preferred_pen
from box_types import BACKGROUND_BOX
from box_menu import show_box_menu
from verbose import verbose

"""box to contain QGraphicsItems children.  Optionally draw box.
Usage:
 1) Crete box
 2) Fill box with child QGraphicsItem objects.  For each:
       1) reset appearance
       2) prepare geometry change
 3) If unplaced: align to right
"""

BOX_PADDING = 20

# UnparentedItem provides an unparented container for holding box
# when we don't want it to be visible.  We can't just setVisible(False)
# because QGraphicsView still reserves space for it.  We can't unparent
# the top-level box in the QGraphicsView because top-level items are
# managed differently.  We prevent the top-level box from being able
# to be hidden.
#
# If box has no "x" then place it with respect to existing parent bounds.

class _UnparentedItem(QGraphicsItem):
    def __init__(self):
        super().__init__()
    def boundingRect(self):
        raise RuntimeError("bad")
    def paint(self, _painter, _option, _widget):
        raise RuntimeError("bad")

class Box(QGraphicsItem):

    def __init__(self, view, box_type, gry_box):
        super().__init__()
        self.view = view
        self.box_type = box_type
        self.parent_box = None
        self.is_visible = gry_box["is_visible"] or box_type == BACKGROUND_BOX
        self.is_boxed = gry_box["is_boxed"]
        if "x" in gry_box:
            self.setPos(QPointF(gry_box["x"], gry_box["y"]))

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

    def set_parent_box(self, parent_box):
        if self.box_type == BACKGROUND_BOX:
            raise RuntimeError("bad")
        # we parent or unparent this box for visibility in QGraphicsView tree
        self.parent_box = parent_box
        if self.is_visible:
            self.setParentItem(parent_box)

        # parented boxes also do this
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.reset_appearance()

    def set_visible(self, is_visible):
        if self.box_type == BACKGROUND_BOX or is_visible == self.is_visible:
            # no action
            return

        self.is_visible = is_visible

        if is_visible:
            self.setParentItem(self.parent_box)
        else:
            # reparent this to an unparented item so Qt doesn't make this
            # a top-level item when detaching
            self._unparented_item = _UnparentedItem()
            self.setParentItem(self._unparented_item)

        self.reset_appearance()

    def set_boxed(self, is_boxed):
        self.is_boxed = is_boxed
        if is_boxed and not self.is_visible:
            # when making box visible make contents visible too
            self.set_visible(True)
        self.reset_appearance()

    def itemChange(self, change, value):
        self.reset_appearance()

        # change parent unless at top background box or not initialized
        if self.parentItem():
            self.parentItem().itemChange(change, value)

        return super(Box, self).itemChange(change, value)

    def type(self):
        return BOX_TYPE

    def get_gry(self):
        gry_box = {"is_boxed": self.is_boxed,
                    "x":self.x(), "y":self.y(), "is_visible":self.is_visible}
        return gry_box

   # adjust for appearance change
    def reset_appearance(self):

        # make the box
        if self.is_boxed:
            p = BOX_PADDING
            rectangle = self.childrenBoundingRect().adjusted(-p, -p, p, p)
            self.bounding_rect = rectangle.adjusted(-1, -1, 1, 1)
        else:
            self.bounding_rect = self.childrenBoundingRect().adjusted(
                                                    -1, -1, 1, 1)
        self.painter_path = QPainterPath()
        self.painter_path.addRect(self.bounding_rect)

        # shape without auto-fill
        stroker = QPainterPathStroker()
        self.shape_path = stroker.createStroke(self.painter_path).simplified()

        # pen color
        self.preferred_pen = preferred_pen()

        self.prepareGeometryChange()

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounding_rect

    # mouse hovers when on this shape path
    def shape(self):
        return self.painter_path

    def paint(self, painter, _option, _widget):
        # maybe paint the box
        if self.is_visible and self.is_boxed:
            painter.save()
            painter.setPen(self.preferred_pen)
            painter.drawPath(self.painter_path)
            painter.restore()

    def align_to_right(self, parent_box):
        if verbose():
            print("box.align_to_right")
        px, py, pw, _ph = parent_box.childrenBoundingRect().getRect()
        x, y, _w, _h = self.childrenBoundingRect().getRect()

        new_x = px + pw + 40 - x
        new_y = py - y
        self.setPos(new_x, new_y)

    # right-click shows menu
    def contextMenuEvent(self, event):
        if event.reason() == QGraphicsSceneContextMenuEvent.Reason.Mouse:
            show_box_menu(self)

