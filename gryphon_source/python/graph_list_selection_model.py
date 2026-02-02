from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Qt
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtWidgets import QAbstractItemView, QTableView, QHeaderView
from graph_list_sort_filter_proxy_model import GraphListSortFilterProxyModel
from preferences import preferences
from graph_item import GraphItem
from empty_gry_graph import empty_gry_graph

class GraphListSelectionModel(QItemSelectionModel):
    """GraphListSelectionModel provides the selection model for graph list
       views.

       Parameters:
         * graph_index - the graph subscript
         * proxy_index - the proxy's subscript
         * select_graph_index - the graph subscript
         * select_proxy_index - the proxy's subscript
    """

    def __init__(self, graph_list_table_model, graph_list_proxy_model):
        super().__init__(graph_list_proxy_model)

        self.graph_list_table_model = graph_list_table_model
        self.graph_list_proxy_model = graph_list_proxy_model

    def select_graph_index(self, graph_index):
        graph_model_index = self.graph_list_table_model.index(graph_index, 0)
        proxy_model_index = self.graph_list_proxy_model.mapFromSource(
                                                           graph_model_index)
        super().setCurrentIndex(proxy_model_index,
                        QItemSelectionModel.SelectionFlag.ClearAndSelect)

    def select_proxy_index(self, proxy_index):
        proxy_model_index = self.graph_list_proxy_model.index(proxy_index, 0)
        super().setCurrentIndex(proxy_model_index,
                        QItemSelectionModel.SelectionFlag.ClearAndSelect)

    def selected_graph_model_index(self):
        proxy_model_index = super().currentIndex()
        graph_model_index = self.graph_list_proxy_model.mapToSource(
                                                           proxy_model_index)
        return graph_model_index

    def selected_graph_index(self):
        return self.selected_graph_model_index().row()

    def selected_proxy_model_index(self):
        proxy_model_index = super().currentIndex()
        return proxy_model_index

    # graph item or None if row is -1
    def graph_index_and_item(self, proxy_model_index):
        graph_model_index = self.graph_list_proxy_model.mapToSource(
                                                           proxy_model_index)
        row = graph_model_index.row()
        if row >= 0:
            graph_item = self.graph_list_table_model.graphs[
                                                  graph_model_index.row()]
        else:
            graph_item = GraphItem(empty_gry_graph())
        return row, graph_item

    def selected_graph_index_and_item(self):
        proxy_model_index = super().currentIndex()
        return self.graph_index_and_item(proxy_model_index)

