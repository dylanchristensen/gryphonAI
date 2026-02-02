from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QMenu, QGraphicsItem
from PySide6.QtGui import QAction
from edge_bezier_placer import direct_route
from main_graph_undo_redo import push_undo_movement

"""
Create and show the edge menu.
"""

def show_edge_menu(edge, event):
    menu = QMenu()

    def _make_direct_route():
        edge.scene().edge_grip_manager.unhighlight_edge()
        edge.ep1, edge.ep2 = direct_route(edge)
        edge.reset_appearance()

        # propagate edge position change to QGraphicsItem parents so
        # box sizes adjust since parentItem is not called for edges
        edge.parentItem().itemChange(QGraphicsItem.GraphicsItemChange \
                                     .ItemPositionHasChanged, None)

    @Slot(bool)
    def _undoable_make_direct_route():
        push_undo_movement(edge.scene(), _make_direct_route,
                                                "reset Bezier edge route")

    # actions
    action_reset_route = QAction("Reset Bezier edge route")
    action_reset_route.setToolTip("Reset to a direct Bezier edge route")
    action_reset_route.triggered.connect(_undoable_make_direct_route)

    menu.addAction(action_reset_route)

    _ = menu.exec(event.screenPos())

