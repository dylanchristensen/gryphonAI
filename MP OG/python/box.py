from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainterPath
from PySide6.QtGui import QFont
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from PySide6.QtWidgets import QMenu
from graph_constants import BOX_TYPE
from settings import preferred_pen
from box_types import BACKGROUND_BOX
from detached_parent import DetachedParent
from verbose import verbose

"""box to contain QGraphicsItems children.  Optionally draw box border.
"""

BOX_PADDING = 20

# We prevent the top-level box from being able to be hidden.
# parent_box is null when box_type is BACKGROUND_BOX.  parent_box always
# points to the parent box while parentItem points to its container which
# might be null or DetachedParent.
#
# If gry_box has "x" then place it else let it be placed later.

class Box(QGraphicsItem):

    def __init__(self, view, box_type, gry_box, parent_box):
        self.is_boxed = gry_box["is_boxed"] # itemChange needs this
        super().__init__()
        self.view = view
        self.box_type = box_type
        self.parent_box = parent_box
        self._detached_parent = DetachedParent()
        self.is_visible = gry_box["is_visible"] or box_type == BACKGROUND_BOX
        self.bounding_rect = QRectF() # boundingRect is called early
        if "x" in gry_box:
            self.setPos(QPointF(gry_box["x"], gry_box["y"]))

        # graphicsItem mode
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        if self.box_type != BACKGROUND_BOX:
            # we parent or unparent this box for visibility in
            # QGraphicsView tree
            if self.is_visible:
                self.setParentItem(parent_box)
            else:
                self.setParentItem(self._detached_parent)

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
            self.setParentItem(self._detached_parent)

        self.reset_appearance()
        # box might not have parent but parent background box will
        self.parent_box.scene().fit_scene()

    def set_boxed(self, is_boxed):
        self.is_boxed = is_boxed
        if is_boxed and not self.is_visible:
            # when making box visible make contents visible too
            self.set_visible(True)
        self.reset_appearance()
        self.scene().fit_scene()

    def itemChange(self, change, value):
        # Some change events impact box size so reset_appearance must be
        # called, while other change events such as ItemChildRemovedChange
        # must not call reset_appearance during destruction.
        if change in (
                   QGraphicsItem.GraphicsItemChange.ItemChildAddedChange,
                   QGraphicsItem.GraphicsItemChange.ItemSceneChange,
                   QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged,
                     ):
            self.reset_appearance()
        return super(Box, self).itemChange(change, value)

    # QGraphicsItem type
    def type(self):
        return BOX_TYPE

    def get_gry(self):
        gry_box = {"is_boxed": self.is_boxed,
                    "x":self.x(), "y":self.y(), "is_visible":self.is_visible}
        return gry_box

    # adjust for appearance change
    def reset_appearance(self):

        # make the box
        self.bounding_rect = self.childrenBoundingRect()
        if self.is_boxed:
            # adjust for border and border pen
            pen_width = 1
            p = BOX_PADDING + pen_width / 2
            self.bounding_rect.adjust(-p, -p, p, p)
        self.painter_path = QPainterPath()
        self.painter_path.addRect(self.bounding_rect)

        # pen color
        self.preferred_pen = preferred_pen()

        self.prepareGeometryChange()
        if self.parent_box:
            # adding or removing boxing impacts the size of the parent
            self.parent_box.reset_appearance()
 
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
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self.painter_path)
            painter.restore()

