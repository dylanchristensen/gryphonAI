from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtCore import Qt
from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtCore import QModelIndex
from graph_list_table_model import GraphListTableModel, GRAPH_COLUMN, \
          TRACE_INDEX_COLUMN, MARK_COLUMN, PROBABILITY_COLUMN, SIZE_COLUMN
from graph_list_table_view import GraphListTableView

class GraphListSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, source_model):
        super(GraphListSortFilterProxyModel, self).__init__()
        self.source_model = source_model
        self.hide_unmarked = None
        self.show_global = None

    def set_filter(self, hide_unmarked, show_global):
        self.hide_unmarked = hide_unmarked 
        self.show_global = show_global 
        self.invalidateFilter()

    # we use this to keep the global view, if present, at the top of the list
    def lessThan(self, left_model_index, right_model_index):
        left_row = left_model_index.row()
        right_row = right_model_index.row()

        # keep any global view at top
        if left_row == 0:
            return bool(self.sortOrder() == Qt.SortOrder.AscendingOrder)
        if right_row == 0:
            return not bool(self.sortOrder() == Qt.SortOrder.AscendingOrder)

        # use normal less than
        return self.source_model.data(left_model_index) \
                   < self.source_model.data(right_model_index)

    # fully control custom filtering
    def filterAcceptsRow(self, row, source_parent):

        if row == 0 and not self.show_global:
            return False
        mark_index = self.source_model.index(row, MARK_COLUMN, source_parent)
        if self.hide_unmarked and self.source_model.data(mark_index) != "M":
            return False
        return True

class GraphListTable(QObject):
    """GraphListTableWidget provides the graph list.  It wraps details of parts,
    ref. http://doc.qt.io/qt-5/model-view-programming.html.

    Sort and filter functions apply to columns in graph_list_table_model

    Parts:
      * GraphListTableModel    Provides graphs from graph_manager
      * GraphListTableViewDelegate    Performs the rendering
      * GraphListTableView            Manages view

    Sockets:
      * signal_graph_selection_changed(graph_index)
      * signal_graphs_loaded()
      * signal_graph_index_view_changed calls graph_index_view_changed
"""

    @Slot(list, str, int)
    def _reset_scrollbar(self, _graphs, _schema_name, _scope):
        self.view.verticalScrollBar().setValue(0)

    @Slot()
    def _settings_changed(self):
        # meaningless index works instead of len(data)
        self.proxy_model.dataChanged.emit(self.proxy_model.index(0, 0),
                       self.proxy_model.index(self.proxy_model.rowCount(), 0))

    def __init__(self, main_splitter, graphs_manager,
                                      navigation_column_width_manager,
                                      signal_settings_changed,
                                      preferences_manager):
        super(GraphListTable, self).__init__()
        self.graphs_manager = graphs_manager

        # model and view services
        self.source_model = GraphListTableModel(
                                       graphs_manager.signal_graphs_loaded)
        self.proxy_model = GraphListSortFilterProxyModel(self.source_model)
        self.proxy_model.setSourceModel(self.source_model)

        self.view = GraphListTableView(main_splitter, self,
                                       navigation_column_width_manager,
                                       preferences_manager)

        # connect move scrollbar to top when graph is reloaded
        graphs_manager.signal_graphs_loaded.connect(self._reset_scrollbar)

        # connect select row when asked
        graphs_manager.signal_graph_selection_changed.connect(self.select_graph)

        # connect to redraw everything when settings changed
        signal_settings_changed.connect(self._settings_changed)

        # connect to redraw everything when probability view preference changes
        preferences_manager.signal_show_type_1_probability_changed.connect(
                                                  self._settings_changed)

    def filter(self, hide_unmarked, show_global):
        self.proxy_model.set_filter(hide_unmarked, show_global)

    def filter_mark(self, filter_on_mark):
        if filter_on_mark:
            self.proxy_model.setFilterKeyColumn(MARK_COLUMN)
            self.proxy_model.setFilterFixedString("M")
        else:
            self.proxy_model.setFilterFixedString("")
            
    def sort_trace_index_ascending(self):
        self.proxy_model.sort(TRACE_INDEX_COLUMN,
                                     order=Qt.SortOrder.AscendingOrder)

    def sort_trace_index_descending(self):
        self.proxy_model.sort(TRACE_INDEX_COLUMN,
                                     order=Qt.SortOrder.DescendingOrder)

    def sort_mark_ascending(self):
        self.proxy_model.sort(MARK_COLUMN, order=Qt.SortOrder.AscendingOrder)

    def sort_mark_descending(self):
        self.proxy_model.sort(MARK_COLUMN, order=Qt.SortOrder.DescendingOrder)

    def sort_probability_ascending(self):
        self.proxy_model.sort(PROBABILITY_COLUMN,
                                     order=Qt.SortOrder.AscendingOrder)

    def sort_probability_descending(self):
        self.proxy_model.sort(PROBABILITY_COLUMN,
                                     order=Qt.SortOrder.DescendingOrder)

    def sort_size_ascending(self):
        self.proxy_model.sort(SIZE_COLUMN, order=Qt.SortOrder.AscendingOrder)

    def sort_size_descending(self):
        self.proxy_model.sort(SIZE_COLUMN, order=Qt.SortOrder.DescendingOrder)

    # convert graph index(row, 0) to proxy table model index(row, col)
    def graph_index_to_proxy_model_index(self, graph_index):
        if graph_index >= 0:
            proxy_model_index = self.proxy_model.mapFromSource(
                                    self.source_model.index(graph_index, 0))
        else:
            proxy_model_index = QModelIndex()
        return proxy_model_index

    # convert proxy table model to graph index
    # a blank model index maps to -1
    def proxy_model_index_to_graph_index(self, proxy_model_index):
        model_index = self.proxy_model.mapToSource(proxy_model_index)
        graph_index, graph_column = model_index.row(), model_index.column()
        return graph_index, graph_column

    # programmatically select the table's row
    @Slot(int)
    def select_graph(self, graph_index):
        proxy_model_index = self.graph_index_to_proxy_model_index(graph_index)
        self.view.setCurrentIndex(proxy_model_index)
        self.view.scrollTo(proxy_model_index)

    # get the graph index that is selected in the model else -1
    def selected_graph(self):
        return self.proxy_model_index_to_graph_index(
                                            self.view.currentIndex())[0]

    # get the graph item that is selected in the model else None
    def selected_graph_item(self):
        index = self.selected_graph()
        if index >= 0:
            return self.graphs_manager.graphs[index]
        else:
            return None

    # tell the table that the graph item at this index needs repainted
    @Slot(int)
    def graph_index_view_changed(self, graph_index):
        proxy_model_index = self.graph_index_to_proxy_model_index(graph_index)
        self.proxy_model.dataChanged.emit(proxy_model_index, proxy_model_index)

