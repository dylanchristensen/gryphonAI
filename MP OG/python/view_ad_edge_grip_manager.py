from PySide6.QtGui import QColor
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsItem
from edge_grip import EdgeGrip
from settings import settings
from view_ad_edge_points import edge_to_points, points_to_grip_points, \
       points_to_vector
from main_graph_undo_redo import track_undo_ad_grip_press, \
                                 track_undo_ad_grip_release

"""
Interface
  * highlight_edge(edge) - edge's mouse press event calls this.  The
                           edge must have from_node, to_node, ep1, ep2.
  * unhighlight_edge() - also call this when scene changes

An edge is selected when highlighted_edge is not None.
"""

class ViewADEdgeGripManager(QObject):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.highlighted_edge = None
        self._grips = None
        self._is_busy_moving_grips = False
        self._color = QColor(settings["ad_edge_color"])

    # insert grip at position
    def _insert_grip(self, index):
        grip = EdgeGrip(self, None, QPointF(), self._color)
        self._grips.insert(index, grip)
        grip.setParentItem(self.highlighted_edge.parentItem())

    # remove grip at position
    def _remove_grip(self, index):
        grip = self._grips.pop(index)
        grip.prepareGeometryChange()
        grip.setParentItem(None)

    # insert set of grips for edge
    def _insert_grips(self):
        self._grips = list()
        edge_points = edge_to_points(self.highlighted_edge)
        grip_points = points_to_grip_points(edge_points)
        for grip_point in grip_points:
            grip = EdgeGrip(self, None, grip_point, self._color)
            self._grips.append(grip)
            grip.setParentItem(self.highlighted_edge.parentItem())

    # remove set of grips for edge
    def _remove_grips(self):
        for grip in self._grips:
            grip.setParentItem(None)
        self._grips = None

    # change grips based on list of tuple: "insert"|"remove", value
    def _change_grip_list(self, changes):

        self._is_busy_moving_grips = True
        for change, index in changes:
            if change == "insert":
                self._insert_grip(index)
            elif change == "remove":
                self._remove_grip(index)
        self._is_busy_moving_grips = False

    # unhighlight any active highlighted edge
    def unhighlight_edge(self):
        if self.highlighted_edge:
            self.highlighted_edge.set_highlighted(False)
            self._remove_grips()
            self.highlighted_edge.parentItem().reset_appearance()
            self.highlighted_edge = None

    # highlight or fail if already active
    def highlight_edge(self, edge):
        self.unhighlight_edge()
        edge.set_highlighted(True)
        self.highlighted_edge = edge
        self._insert_grips()

    def _grip_points(self):
        points = list()
        if self._grips:
            for grip in self._grips:
                points.append(grip.pos())
        else:
            print("view_ad_edge_grip_manager _grip_points empty")
        return points

    def move_edge(self, _grip_index, change, value):
        if self._is_busy_moving_grips:
            # ignore move events that are programatically generated here
            return

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:

            requested_edge_vector = points_to_vector(
                       self.highlighted_edge.edge_start, self._grip_points())

            grip_list_changes = self.highlighted_edge.change_edge_vector(
                      self.highlighted_edge.edge_start, requested_edge_vector)

            if grip_list_changes:
                # add or remove grips
                self._change_grip_list(grip_list_changes)

            # align moved grips to their visually correct positions
            accepted_points = edge_to_points(self.highlighted_edge)
            accepted_grip_points = points_to_grip_points(accepted_points)
            self._is_busy_moving_grips = True
            for grip, accepted_grip_point in zip(
                                        self._grips, accepted_grip_points):
                grip.setPos(accepted_grip_point)
            self._is_busy_moving_grips = False

    def track_undo_grip_press(self, event):
        track_undo_ad_grip_press(self.highlighted_edge, event)

    def track_undo_grip_release(self, event):
        track_undo_ad_grip_release(self.highlighted_edge, "AD edge", event)

