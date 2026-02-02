from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from view_ad_place_edges import place_edges
from graph_constants import VIEW_AD_NODE_TYPE
from main_graph_undo_redo import push_undo_movement

"""
Create and show the view AD edge menu.
"""

def _nodes(edge):
    items = edge.parentItem().childItems()
    nodes = list()
    for item in items:
        if item.type() == VIEW_AD_NODE_TYPE:
            nodes.append(item)
    return nodes

def show_view_ad_edge_menu(edge, event):
    menu = QMenu()

    def _make_direct_route():
        edge.scene().view_ad_edge_grip_manager.unhighlight_edge()
        nodes = _nodes(edge)
        place_edges(nodes, [edge])
        edge.scene().fit_scene()

    @Slot(bool)
    def _undoable_make_direct_route():
        push_undo_movement(edge.scene(), _make_direct_route,
                                                "reset AD edge route")

    # actions
    action_reset_route = QAction("Reset AD edge route")
    action_reset_route.setToolTip("Reset this activity diagram edge route")
    action_reset_route.triggered.connect(_undoable_make_direct_route)

    menu.addAction(action_reset_route)

    _ = menu.exec(event.screenPos())

