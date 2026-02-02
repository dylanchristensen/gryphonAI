from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtGui import QCursor
from PySide6.QtGui import QIcon
from box_types import BACKGROUND_BOX, TRACE_BOX, REPORT_BOX, TABLE_BOX, \
                      GRAPH_BOX, BAR_CHART_BOX, GANTT_CHART_BOX, AD_BOX, \
                      BOX_NAMES
from view_ad_place_edges import place_edges
from main_graph_undo_redo import undo_stack_actions, push_undo_movement

"""
Create and show a box_type-specific box menu.
"""

def _add_generic_menu_content(box, menu):

    # undo redo actions
    undo_action, redo_action = undo_stack_actions(box.scene().graph_item, menu)
    menu.addAction(undo_action)
    menu.addAction(redo_action)
    menu.addSeparator()

    # action box border
    action_set_boxed = QAction("Show %s border"%BOX_NAMES[box.box_type], menu)
    action_set_boxed.setCheckable(True)
    action_set_boxed.setChecked(box.is_boxed)
    @Slot(bool)
    def _set_boxed(is_checked):
        box.set_boxed(is_checked)
    action_set_boxed.triggered.connect(_set_boxed)
    menu.addAction(action_set_boxed)

    # action content visibility
    action_set_visible = QAction("Show %s component"
                                 %BOX_NAMES[box.box_type], menu)
    action_set_visible.setCheckable(True)
    action_set_visible.setChecked(box.is_visible)
    action_set_visible.setEnabled(box.box_type != BACKGROUND_BOX)
    @Slot(bool)
    def _set_visible(is_checked):
        # box menu is only accessible when visible
        box.set_visible(is_checked)
    action_set_visible.triggered.connect(_set_visible)
    menu.addAction(action_set_visible)

def _add_graph_menu_content(box, menu):
    menu.addSeparator()

    @Slot(bool)
    def _align_force_directed():
        push_undo_movement(box.scene(), box.view.align_force_directed,
                                                  "align force directed")

    @Slot(bool)
    def _align_force_directed_slow():
        push_undo_movement(box.scene(), box.view.align_force_directed_x10,
                                                  "align force directed slow")

    @Slot(bool)
    def _align_circular():
        push_undo_movement(box.scene(), box.view.align_circular,
                                                  "align circular")

    # force directed
    action_align_force_directed = QAction("Apply force-directed alignment",
                                          menu)
    action_align_force_directed.setToolTip("Straighten up node placement")
    action_align_force_directed.triggered.connect(_align_force_directed)
    menu.addAction(action_align_force_directed)

    # force directed x10 (slow)
    action_align_force_directed_slow = QAction("Apply more precise "
                   "force-directed alignment (slower)", menu)
    action_align_force_directed_slow.setToolTip("Straighten up node "
                                 "placement with greater precision")
    action_align_force_directed_slow.triggered.connect(
                                         _align_force_directed_slow)
    menu.addAction(action_align_force_directed_slow)

    # circular alignment
    action_align_circular = QAction("Apply circular node alignment", menu)
    action_align_circular.setToolTip("Arrange graph nodes in a circle")
    action_align_circular.triggered.connect(_align_circular)
    menu.addAction(action_align_circular)

def _add_trace_menu_content(box, menu):
    # the trace event menu
    menu.addSeparator()
    graph_main_scene = box.scene()
    menu.addMenu(graph_main_scene.trace_event_menu.trace_event_menu)

def _add_activity_diagram_menu_content(box, menu):
    menu.addSeparator()

    def _realign_edges():
        place_edges(box.view.nodes, box.view.edges)

    @Slot(bool)
    def _undo_realign_edges():
        push_undo_movement(box.scene(), _realign_edges, "realign AD edges")

    # realign edges
    action_realign_edges = QAction("Realign edges", menu)
    action_realign_edges.setToolTip("Realign edges based on node positions")
    action_realign_edges.triggered.connect(_undo_realign_edges)
    menu.addAction(action_realign_edges)

def _add_report_menu_content(box, menu):
    menu.addSeparator()

    # copy report to clipboard as CSV
    action_copy_report_to_clipboard = QAction(QIcon(":/icons/copy_csv"),
                             "Copy report to clipboard as CSV", menu)
    action_copy_report_to_clipboard.setToolTip("Copy the table to the "
                   "system clipboard as a list of comma separated values")
    action_copy_report_to_clipboard.triggered.connect(
                                        box.view.copy_report_to_clipboard)
    menu.addAction(action_copy_report_to_clipboard)

def _add_table_menu_content(box, menu):
    menu.addSeparator()

    # copy table to clipboard as CSV
    action_copy_table_to_clipboard = QAction(QIcon(":/icons/copy_csv"),
                             "Copy table to clipboard as CSV", menu)
    action_copy_table_to_clipboard.setToolTip("Copy the table to the "
                   "system clipboard as a list of comma separated values")
    action_copy_table_to_clipboard.triggered.connect(
                                         box.view.copy_table_to_clipboard)
    menu.addAction(action_copy_table_to_clipboard)

def show_box_menu(box, event):
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

    # REPORT_BOX menu content
    if box.box_type == REPORT_BOX:
        _add_report_menu_content(box, menu)

    # TABLE_BOX menu content
    if box.box_type == TABLE_BOX:
        _add_table_menu_content(box, menu)

    # open the menu
    _action = menu.exec(event.screenPos())

