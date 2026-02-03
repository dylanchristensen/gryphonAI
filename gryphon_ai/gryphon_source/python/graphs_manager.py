from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Signal # for signal/slot support
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtGui import QAction
from graph_item import GraphItem
from settings_manager import settings, emit_signal_settings_changed

class GraphsManager(QObject):
    """Provides graph data and signals when the graph list is loaded or cleared.

    Register with signal_graphs_loaded to provide current graph data.

    Data structures:
      * graphs (list<GraphItem>)
      * schema_name - taken at time of run
      * scope - taken at time of run
      * selected_graph_index (int)

    Signals:
      * signal_graphs_loaded(graphs, schema name, scope)
      * signal_graph_selection_changed(graph_index) - graph selection changed,
        call this when the selection changes.  selection can happen from
        loading or navigating the graph list table.
    """

    # signals
    signal_graphs_loaded = Signal(list, str, int, name='graphsLoaded')
    signal_graph_selection_changed = Signal(int,
                                                name='graphSelectionChanged')

    def __init__(self, settings_manager):
        super(GraphsManager, self).__init__()
        self.settings_manager = settings_manager

        # set initial state
        self.clear_graphs()

        # connect
        settings_manager.signal_settings_changed.connect(self._settings_changed)

        # action show any hidden components
        self.action_show_hidden_components = QAction(
                                             "Show any hidden components")
        self.action_show_hidden_components.setStatusTip("Show any components"
                                             " that have been hidden")
        self.action_show_hidden_components.triggered.connect(
                                         self._show_hidden_components)

        # action show any hidden components all graphs
        self.action_show_hidden_components_all_graphs = QAction(
                                "Show any hidden components in all graphs")
        self.action_show_hidden_components_all_graphs.setStatusTip(
                    "In all graphs show any components that have been hidden")
        self.action_show_hidden_components_all_graphs.triggered.connect(
                                 self._show_hidden_components_all_graphs)

    @Slot()
    def _show_hidden_components(self):
        if self.selected_graph_index != -1:
            self.graphs[self.selected_graph_index].ensure_visibility()
            emit_signal_settings_changed()

    @Slot()
    def _show_hidden_components_all_graphs(self):
        for graph in self.graphs:
            graph.ensure_visibility()
        emit_signal_settings_changed()

    def _remember_spacing(self):
        self.trace_node_h_spacing = settings["trace_node_h_spacing"]
        self.trace_node_v_spacing = settings["trace_node_v_spacing"]
        self.graph_node_h_spacing = settings["graph_node_h_spacing"]
        self.graph_node_v_spacing = settings["graph_node_v_spacing"]
        self.ad_h_spacing = settings["ad_h_spacing"]
        self.ad_v_spacing = settings["ad_v_spacing"]

    # instantiate graphs, set settings, then signal
    def set_graphs(self, gry_graphs, schema_name, scope, selected_graph_index):
        self.graphs = list()
        self.schema_name = schema_name
        self.scope = scope

        for gry_graph in gry_graphs:
             self.graphs.append(GraphItem(gry_graph))
        self.set_selection(selected_graph_index)

        # remember spacing for reference in case spacing changes
        self._remember_spacing()

        # signal
        self.signal_graphs_loaded.emit(self.graphs, self.schema_name,
                                       self.scope)
        self.signal_graph_selection_changed.emit(self.selected_graph_index)

    def clear_graphs(self):
        self.set_graphs([], "Schema not defined", 1, -1)

    # graph selection index
    def set_selection(self, graph_index):
        self.selected_graph_index = graph_index
        self.signal_graph_selection_changed.emit(graph_index)

    def has_non_empty_global_view(self):
        return bool(self.graphs and self.graphs[0].has_non_trace())

    # get .gry graph
    def get_gry_graphs(self):
        gry_graphs = list()
        for graph in self.graphs:
            gry_graphs.append(graph.get_gry())
        return gry_graphs

    def _change_trace_node_h_spacing(ratio):
        for graph in self.graphs:
            for node in graph.node:
                node.setX(node.x() * ratio)

    # change everything to reflect changed settings
    @Slot()
    def _settings_changed(self):
        spacing_ratios = {"trace_h": settings["trace_node_h_spacing"] \
                                     / self.trace_node_h_spacing,
                          "trace_v": settings["trace_node_v_spacing"] \
                                     / self.trace_node_v_spacing,
                          "graph_h": settings["graph_node_h_spacing"] \
                                     / self.graph_node_h_spacing,
                          "graph_v": settings["graph_node_v_spacing"] \
                                     / self.graph_node_v_spacing,
                          "ad_h": settings["ad_h_spacing"] \
                                     / self.ad_h_spacing,
                          "ad_v": settings["ad_v_spacing"] \
                                     / self.ad_v_spacing,
                         }

        # if any of these ratios changed then change spacing
        change_spacing = False
        for _key, value in spacing_ratios.items():
            if value != 1.0:
                change_spacing = True
                self._remember_spacing()
                break

        for graph in self.graphs:
            if change_spacing:
                graph.change_item_spacing(spacing_ratios)

            # reset appearance whether or not the change was about spacing
            if graph.is_initialized:
                graph.reset_appearance()

