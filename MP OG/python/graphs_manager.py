from PySide6.QtCore import QObject, Signal, Slot
from graph_item import GraphItem
from settings import settings
from mp_logger import log_to_statusbar

class GraphsManager(QObject):
    """Provides graph data and signals when the graph list is loaded or cleared.

    The graphs_manager captures mp_code, graphs, and scope taken at the
    time of trace generation.  For real-time state see mp_code_manager.

    Data structures:
      * mp_code - snapshot taken at time of run
      * graphs (list<GraphItem>)
      * scope - taken at time of run

    GraphsManager provides graph and graph metadata accessors.  When
    signal_graphs_loaded is issued, graphs may be accessed from here
    or from graph_list_table_model.

    Signals:
      * signal_graphs_loaded()
    """

    # signals
    signal_graphs_loaded = Signal(name='graphsLoaded')

    def __init__(self, graph_list_table_model, settings_manager):
        super(GraphsManager, self).__init__()
        self.graph_list_table_model = graph_list_table_model
        self.settings_manager = settings_manager

        # set initial state
        self._remember_spacing()
        self.clear_graphs()

        # connect
        settings_manager.signal_settings_changed.connect(self._settings_changed)

    def _remember_spacing(self):
        self.trace_node_h_spacing = settings["trace_node_h_spacing"]
        self.trace_node_v_spacing = settings["trace_node_v_spacing"]
        self.graph_node_h_spacing = settings["graph_node_h_spacing"]
        self.graph_node_v_spacing = settings["graph_node_v_spacing"]
        self.ad_h_spacing = settings["ad_h_spacing"]
        self.ad_v_spacing = settings["ad_v_spacing"]

    # instantiate graphs, set settings, then signal
    def set_graphs(self, mp_code, gry_graphs, scope):
        self.mp_code = mp_code

        # clear graphs
        self.graphs = list()
        self.scope = scope
        self.graph_list_table_model.set_graph_list(list(), "")

        # repopulate graphs
        log_to_statusbar("Creating %d graphs..."%len(gry_graphs))
        for gry_graph in gry_graphs:
             self.graphs.append(GraphItem(gry_graph))
        log_to_statusbar("Done creating %d graphs"%len(gry_graphs))

        # set graphs
        self.graph_list_table_model.set_graph_list(self.graphs, self.mp_code)

        # remember spacing for reference in case spacing changes
        self._remember_spacing()

        # signal
        self.signal_graphs_loaded.emit()

    def clear_graphs(self):
        self.mp_code = ""
        self.graphs = list()
        self.scope = 1
        self.graph_list_table_model.set_graph_list(list(), "")

        # signal
        self.signal_graphs_loaded.emit()

    def restore_graphs(self, existing_mp_code, existing_graphs, existing_scope):
        if self.graphs:
            raise RuntimeError("bad")
        self.mp_code = existing_mp_code
        self.graphs = existing_graphs
        self.scope = existing_scope
        self.graph_list_table_model.set_graph_list(self.graphs, self.mp_code)

        # signal
        self.signal_graphs_loaded.emit()

    def has_non_empty_global_view(self):
        return bool(self.graphs and self.graphs[0].has_non_trace())

    # get .gry graph
    def get_gry_graphs(self):
        gry_graphs = list()
        for graph in self.graphs:
            gry_graphs.append(graph.get_gry())
        return gry_graphs

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

