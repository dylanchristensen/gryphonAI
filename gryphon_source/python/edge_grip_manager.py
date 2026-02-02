from PySide6.QtGui import QColor
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QGraphicsItem
from edge_grip import EdgeGrip
from detached_parent import DetachedParent
from settings import settings
from main_graph_undo_redo import track_undo_bezier_grip_press, \
                                 track_undo_bezier_grip_release

"""
Interface
  * highlight_edge(edge) - edge's mouse press event calls this.  The
                           edge must have from_node, to_node, ep1, ep2.
  * unhighlight_edge() - also call this when scene changes
  * maybe_move_grips(_list) - we move grips when one of the edge's node
                              position changes

An edge is selected when highlighted_edge is not None.
"""

class EdgeGripManager(QObject):
    def __init__(self):
        super().__init__()
        self.highlighted_edge = None
        self.grip1 = None
        self.grip2 = None
        self._detached_parent = DetachedParent()

    # unhighlight any active highlighted edge
    def unhighlight_edge(self):
        if self.highlighted_edge:
            self.highlighted_edge.set_highlighted(False)
            self.grip1.setParentItem(self._detached_parent)
            self.grip2.setParentItem(self._detached_parent)
            self.highlighted_edge.parentItem().reset_appearance()
            self.highlighted_edge = None

    def highlight_edge(self, edge):
        self.unhighlight_edge()
        self.highlighted_edge = edge
        edge.set_highlighted(True)
        self.grip1 = EdgeGrip(self, 1, edge.ep1,
                               QColor(settings["trace_node_root_color"]))
        self.grip1.setParentItem(edge.parentItem())
        self.grip2 = EdgeGrip(self, 2, edge.ep2,
                               QColor(settings["trace_node_atomic_color"]))
        self.grip2.setParentItem(edge.parentItem())

    def move_edge(self, grip_index, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if grip_index == 1:
                self.highlighted_edge.ep1 = value
            elif grip_index == 2:
                self.highlighted_edge.ep2 = value
            else:
                raise Exception("Bad")
            self.highlighted_edge.reset_appearance()
            self.highlighted_edge.itemChange(change, value)

    def maybe_move_grips(self):
        # we move grips when one of the edge's node position changes
        if self.highlighted_edge:
            self.grip1.setPos(self.highlighted_edge.ep1)
            self.grip2.setPos(self.highlighted_edge.ep2)

    def track_undo_grip_press(self, event):
        track_undo_bezier_grip_press(self.highlighted_edge, event)

    def track_undo_grip_release(self, event):
        track_undo_bezier_grip_release(self.highlighted_edge,
                                       "Bezier edge", event)

