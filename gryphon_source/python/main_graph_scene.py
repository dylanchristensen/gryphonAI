# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

import math
from PySide6.QtCore import QRectF, Qt
from PySide6.QtCore import Slot
from PySide6.QtCore import QObject
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QTransform
from PySide6.QtGui import QCursor
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QGraphicsSceneContextMenuEvent
from edge_grip_manager import EdgeGripManager
from view_ad_edge_grip_manager import ViewADEdgeGripManager
from trace_event_menu import TraceEventMenu
from box_menu import show_box_menu
from node_menu import NodeMenu
from edge_menu import show_edge_menu
from view_ad_edge_menu import show_view_ad_edge_menu
from os_compatibility import control_modifier, pure_right_button_down
from graph_constants import BOX_TYPE, NODE_TYPE, EDGE_TYPE, EDGE_GRIP_TYPE, \
                            VIEW_AD_EDGE_TYPE, VIEW_GRAPH_EDGE_TYPE
from graph_item import GraphItem
from empty_gry_graph import empty_gry_graph
from main_graph_undo_redo import maybe_undo_move, maybe_redo_move

class MainGraphScene(QGraphicsScene):

    def __init__(self, graph_list_table_model, graph_list_selection_model,
                 settings_manager, graph_pane_menu):
        super().__init__()
        self.graph_list_table_model = graph_list_table_model
        self.graph_list_selection_model = graph_list_selection_model
        self.settings_manager = settings_manager
        self.graph_pane_menu = graph_pane_menu

        self._is_setting_scene_rect = False

        # the event menu which applies to any selected graph_item
        self.trace_event_menu = TraceEventMenu(self, settings_manager)

        # the scene's edge grip manager
        self.edge_grip_manager = EdgeGripManager()

        # the scene's AD edge grip manager
        self.view_ad_edge_grip_manager = ViewADEdgeGripManager(self)

        # connect to set main scene
        graph_list_selection_model.currentChanged.connect(self._set_scene)

        # connect to fit scene on settings change
        settings_manager.signal_settings_changed.connect(self.fit_scene)

        # start the scene with an empty graph
        self._set_empty_scene()

        # alert the table model to repaint: a view change is a data change
        self.changed.connect(self.scene_changed)

    def scene_changed(self):
        # Allow the scene to expand.  We do not use QGraphicsScene's native
        # provision to grow and manage scrollbars because we want the scene
        # to reduce to fit when move operations are done.
        self.setSceneRect(self.sceneRect().united(self.itemsBoundingRect()))

        # keep listeners up to date
        model_index = self.graph_list_selection_model \
                                      .selected_graph_model_index()
        if model_index.row() != -1:
            self.graph_list_table_model.dataChanged.emit(
                                                 model_index, model_index)

    def _set_empty_scene(self):
        self.graph_item = GraphItem(empty_gry_graph())
        self.graph_item.initialize_items()
        self.addItem(self.graph_item.background_box)

    # set scene on selection, collapse/expand, or main view geometry change
    def set_scene(self):
        self._clear_scene()

        _graph_index, self.graph_item = self.graph_list_selection_model \
                                        .selected_graph_index_and_item()

        # optimization: just-in-time for display, see graph_item.py
        self.graph_item.initialize_items()

        # add top level parent graph item to this scene
        self.addItem(self.graph_item.background_box)

        # fit scene
        self.fit_scene()

    # populate scene with QGraphicsItem items
    @Slot(QModelIndex, QModelIndex)
    def _set_scene(self, _current_proxy_model_index,
                         _previous_proxy_model_index):
        self.set_scene()

    def _clear_scene(self):
        # this hack allows sceneRect to become 0.  We can't set it to 0
        # because 0 tells QGraphicsScene to use the default rect which is
        # the largest size it grew to.  We can't poll it because polling
        # changes its state (likely reverting to using default rect).  So
        # we change it to a new value so it knows to fix it when cleared
        # (by setting it to 0).
        self.setSceneRect(QRectF(1,1,1,1))

        # remove any edge selection
        self.edge_grip_manager.unhighlight_edge()
        self.view_ad_edge_grip_manager.unhighlight_edge()

        # remove the top level parent graph item from this scene
        self.removeItem(self.graph_item.background_box)

    def keyPressEvent(self, event):

        has_trace = self.graph_item.has_trace()
        # keystroke controls
        key = event.key()

        # undo redo
        maybe_undo_move(self.graph_item, event)
        maybe_redo_move(self.graph_item, event)

        # item selection and event modifiers
        if key == Qt.Key.Key_A and event.modifiers() \
                             == Qt.KeyboardModifier.ControlModifier:
            for item in self.items():
                item.setSelected(True)
        elif has_trace and key == Qt.Key.Key_H \
                       and event.modifiers() == control_modifier():
            self.graph_item.trace.unhide_all_nodes()
        elif has_trace and key == Qt.Key.Key_H:
            self.graph_item.trace.toggle_hide_unhide()
        elif has_trace and key == Qt.Key.Key_C:
            self.graph_item.trace.toggle_collapse_uncollapse()

        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # maybe show context menu
        if pure_right_button_down(event):
            self._show_context_menu(event)
            return

        # unhighlight Bezier-based edges unless the cursor is over
        # something moveable, usually a grip.  Do not unhighlight when
        # selecting other objects because this would cause jitter.
        should_unhighlight_bezier_edge = True
        items_under_cursor = self.items(event.scenePos())
        for item in items_under_cursor:
            if item.type() != BOX_TYPE:
                should_unhighlight_bezier_edge = False
                break
        if should_unhighlight_bezier_edge:
            # remove any trace edge selection
            self.edge_grip_manager.unhighlight_edge()

        # unhighlight AD edge unless the cursor is over a grip
        should_unhighlight_ad_edge = True
        for item in items_under_cursor:
            if item.type() == EDGE_GRIP_TYPE:
                should_unhighlight_ad_edge = False
                break
        if should_unhighlight_ad_edge:
            # remove any ad edge selection
            self.view_ad_edge_grip_manager.unhighlight_edge()

        super().mousePressEvent(event)

    # fit the scene to contained items
    # do not do this if the mouse is down and moving something
    @Slot()
    def fit_scene(self):
        # reset the bounding rectangle, possibly centering the graph
        self.setSceneRect(self.itemsBoundingRect())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if QGuiApplication.mouseButtons() == Qt.NoButton:
            self.fit_scene()

    def _show_scene_menu(self):
        _action = self.graph_pane_menu.exec(QCursor.pos())

    # On right click show the context menu for the topmost of, in order:
    # non-box component menu if available, box menu, blank space menu
    def _show_context_menu(self, event):
 
        items_under_cursor = self.items(event.scenePos())

        # try showing the top non-box menu
        for item in items_under_cursor:
            if item.type() != BOX_TYPE:
                # not box so show it's context menu
                if item.type() == NODE_TYPE:
                    # show node menu
                    _ = NodeMenu(item, event)
                    return

                if item.type() in (EDGE_TYPE, VIEW_GRAPH_EDGE_TYPE):
                    # show edge menu
                    show_edge_menu(item, event)
                    return

                if item.type() == VIEW_AD_EDGE_TYPE:
                    # show edge menu
                    show_view_ad_edge_menu(item, event)
                    return

                # the top non-box item has no menu
                break

        # maybe show the top box menu
        for item in items_under_cursor:
            if item.type() == BOX_TYPE:
                # show box menu
                show_box_menu(item, event)
                return

        if not items_under_cursor:
            # nothing left so show the blank space context menu
            self._show_scene_menu()
        else:
            raise RuntimeError("bad")

