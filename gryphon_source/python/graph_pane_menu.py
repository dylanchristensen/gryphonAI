from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Slot
from graph_item import GraphItem
from empty_gry_graph import empty_gry_graph
from main_graph_undo_redo import undo_stack_actions

"""
Provides the graph pane menu.
"""

class GraphPaneMenu(QMenu):
    def __init__(self, gui_manager):
        super().__init__("&Graph pane")
        self.gui_manager = gui_manager

        # view actions
        # action zoom the graph pane in
        self.action_zoom_in = QAction(QIcon(":/icons/zoom_in"),
                                      "Zoom in", self)
        self.action_zoom_in.setToolTip("Zoom the graph pane in")
        self.action_zoom_in.triggered.connect(
                            self.gui_manager.main_graph_view.scale_view_in)

        # action zoom the graph pane out
        self.action_zoom_out = QAction(QIcon(":/icons/zoom_out"),
                                      "Zoom out", self)
        self.action_zoom_out.setToolTip("Zoom the graph pane out")
        self.action_zoom_out.triggered.connect(
                          self.gui_manager.main_graph_view.scale_view_out)

        # action zoom the graph pane reset to default scale
        self.action_zoom_reset = QAction(QIcon(":/icons/zoom_reset"),
                                      "Zoom reset", self)
        self.action_zoom_reset.setToolTip(
                                "Zoom the graph pane to its default scale")
        self.action_zoom_reset.triggered.connect(
                          self.gui_manager.main_graph_view.scale_view_reset)

        # graph actions
        # action box background border
        self.action_set_boxed = QAction("Show background border")
        self.action_set_boxed.setToolTip("Show the background border")
        self.action_set_boxed.setCheckable(True)
        self.action_set_boxed.triggered.connect(self._show_background_border)

        # action show any hidden views in selected graph
        self.action_show_hidden_views = QAction(
                                             "Show any hidden components")
        self.action_show_hidden_views.setToolTip("Show any components"
                                             " that have been hidden")
        self.action_show_hidden_views.triggered.connect(
                               self._show_hidden_views_this_graph)

        # action show any hidden views all graphs
        self.action_show_hidden_views_all_graphs = QAction(
                                "Show any hidden components in all graphs")
        self.action_show_hidden_views_all_graphs.setToolTip(
                    "In all graphs show any components that have been hidden")
        self.action_show_hidden_views_all_graphs.triggered.connect(
                               self._show_hidden_views_all_graphs)

        self._action_retainer_menu = QMenu("internal retainer menu")
        self._action_retainer_menu.addAction(self.action_set_boxed)
        self._action_retainer_menu.addAction(self.action_show_hidden_views)
        self._action_retainer_menu.addAction(
                               self.action_show_hidden_views_all_graphs)

        # connect
        self.aboutToShow.connect(self._show_menu)

    def _show_menu(self):

        # state
        graph_item = self.gui_manager.main_graph_scene.graph_item
        has_graphs = bool(self.gui_manager.graphs_manager.graphs)
        is_selected= not graph_item == GraphItem(empty_gry_graph())

        # background border checked
        self.action_set_boxed.setChecked(graph_item.background_box.is_boxed)

        # background border
        self.action_set_boxed.setEnabled(is_selected)

        # hidden views this graph
        self.action_show_hidden_views.setEnabled(is_selected)

        # hidden views all graphs
        self.action_show_hidden_views_all_graphs.setEnabled(has_graphs)

        # menu items
        self.clear()

        # undo redo actions
        undo_action, redo_action = undo_stack_actions(graph_item, self)
        self.addAction(undo_action)
        self.addAction(redo_action)
        self.addSeparator()

        # view actions
        self.addAction(self.action_zoom_in)
        self.addAction(self.action_zoom_out)
        self.addAction(self.action_zoom_reset)
        self.addSeparator()

        # graph actions
        self.addAction(self.action_set_boxed)
        self.addAction(self.action_show_hidden_views)
        self.addAction(self.action_show_hidden_views_all_graphs)

        # reconnect actions to self likely because self.clear() breaks them
        self.action_set_boxed.triggered.connect(self._show_background_border)
        self.action_show_hidden_views.triggered.connect(
                               self._show_hidden_views_this_graph)
        self.action_show_hidden_views_all_graphs.triggered.connect(
                               self._show_hidden_views_all_graphs)

    @Slot(bool)
    def _show_background_border(self, is_checked):
        graph_index, graph_item = self.gui_manager.graph_list_selection_model \
                                      .selected_graph_index_and_item()
        if graph_index != -1:
            graph_item.background_box.set_boxed(is_checked)

    @Slot()
    def _show_hidden_views_this_graph(self):
        graph_index, graph_item = self.gui_manager.graph_list_selection_model \
                                      .selected_graph_index_and_item()
        if graph_index != -1:
            graph_item.unhide_hidden_views()

    @Slot()
    def _show_hidden_views_all_graphs(self):
        for graph in self.gui_manager.graphs_manager.graphs:
            graph.unhide_hidden_views()

        # repaint the whole visible graph list
        self.gui_manager.graph_list_view.data_changed()

