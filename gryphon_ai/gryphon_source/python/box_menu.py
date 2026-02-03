from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtGui import QCursor
from settings_manager import emit_signal_settings_changed
from box_types import BACKGROUND_BOX, TRACE_BOX, GRAPH_BOX, AD_BOX
from edge_angular_placer import place_edges

"""
Create and show a box_type-specific box menu.
"""

def _add_generic_menu_content(box, menu):

    # action box border
    action_set_boxed = QAction("Show border", menu)
    action_set_boxed.setCheckable(True)
    action_set_boxed.setChecked(box.is_boxed)
    @Slot(bool)
    def _set_boxed(is_checked):
        box.set_boxed(is_checked)
        emit_signal_settings_changed()
    action_set_boxed.triggered.connect(_set_boxed)
    menu.addAction(action_set_boxed)

    # action content visibility
    action_set_visible = QAction("Show component", menu)
    action_set_visible.setCheckable(True)
    action_set_visible.setChecked(box.is_visible)
    action_set_visible.setEnabled(box.box_type != BACKGROUND_BOX)
    @Slot(bool)
    def _set_visible(is_checked):
        box.set_visible(is_checked)
        emit_signal_settings_changed()
    action_set_visible.triggered.connect(_set_visible)
    menu.addAction(action_set_visible)

def _add_graph_menu_content(box, menu):
    menu.addSeparator()

    # force directed
    action_align_force_directed = QAction("Apply force-directed alignment",
                                          menu)
    action_align_force_directed.setStatusTip("Straighten up node placement")
    action_align_force_directed.triggered.connect(
                                      box.view.align_force_directed)
    menu.addAction(action_align_force_directed)

    # force directed x10 (slow)
    action_align_force_directed = QAction("Apply more precise "
                   "force-directed alignment (slower)", menu)
    action_align_force_directed.setStatusTip("Straighten up node "
                                 "placement with greater precision")
    action_align_force_directed.triggered.connect(
                                      box.view.align_force_directed_x10)
    menu.addAction(action_align_force_directed)

    # circular alignment
    action_align_circular = QAction("Apply circular node alignment", menu)
    action_align_circular.setStatusTip("Arrange graph nodes in a circle")
    action_align_circular.triggered.connect(box.view.align_circular)
    menu.addAction(action_align_circular)

def _add_trace_menu_content(box, menu):
    menu.addSeparator()
    graph_main_scene = box.scene()
    menu.addMenu(graph_main_scene.event_menu.event_menu)

def _add_activity_diagram_menu_content(box, menu):
    menu.addSeparator()

    # place edges
    action_place_edges = QAction("Reset edge placement", menu)
    action_place_edges.setStatusTip("Reset edge placement based on "
                                    "node positions")
    @Slot(bool)
    def _place_edges():
        place_edges(box.view.nodes, box.view.edges)
    action_place_edges.triggered.connect(_place_edges)
    menu.addAction(action_place_edges)

def show_box_menu(box):
    menu = QMenu()

    # generic content
    _add_generic_menu_content(box, menu)

    # GRAPH_BOX menu content
    if box.box_type == GRAPH_BOX:
        _add_graph_menu_content(box, menu)

    # TRACE_BOX menu content
    if box.box_type == TRACE_BOX:
        _add_trace_menu_content(box, menu)

    # AD_BOX menu content
    if box.box_type == AD_BOX:
        _add_activity_diagram_menu_content(box, menu)

    # open the menu
    _action = menu.exec(QCursor.pos())

