from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot
from PySide6.QtCore import Qt
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtWidgets import QAbstractItemView, QTableView, QHeaderView
from graph_list_sort_filter_proxy_model import GraphListSortFilterProxyModel
from graph_list_view_delegate import GraphListViewDelegate
from preferences import preferences
from graph_item import GraphItem
from empty_gry_graph import empty_gry_graph

class GraphListView(QTableView):
    """GraphListView provides the graph list view and holds the view delegate.
    """

    def __init__(self, main_splitter,
                       graphs_manager,
                       graph_list_proxy_model,
                       graph_list_selection_model,
                       navigation_column_width_manager,
                       signal_preferences_changed):
        super().__init__(main_splitter)

        # the data model
        self.setModel(graph_list_proxy_model)

        # table appearance
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.setSelectionModel(graph_list_selection_model)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setSectionResizeMode(
                                     QHeaderView.ResizeMode.ResizeToContents)
        self._set_scroll_mode()

        # the delegate which will paint the graphs in the list
        view_delegate = GraphListViewDelegate(graph_list_selection_model,
                                              navigation_column_width_manager)
        self.setItemDelegate(view_delegate)

        # connect model reset
        graph_list_proxy_model.modelReset.connect(self._hide_unused_columns)

        # connect width changed
        navigation_column_width_manager.signal_navigation_column_width_changed\
                                      .connect(self._changed_width)

        # connect scroll mode changed
        signal_preferences_changed.connect(self._set_scroll_mode)

    @Slot()
    def _hide_unused_columns(self):
        # hide all but the first column so the first column stretches
        for i in range(1, self.model().columnCount()):
            self.setColumnHidden(i, True)

    # width changed
    @Slot(int)
    def _changed_width(self, _width):
        self.resizeRowsToContents()

    # scroll mode preference changed
    @Slot()
    def _set_scroll_mode(self):
        scroll_mode = preferences["scroll_mode"]
        if scroll_mode == "scroll_per_pixel":
            self.setVerticalScrollMode(
                            QAbstractItemView.ScrollMode.ScrollPerPixel)
        elif scroll_mode == "scroll_per_item":
            self.setVerticalScrollMode(
                            QAbstractItemView.ScrollMode.ScrollPerItem)
        else:
            raise RuntimeError("bad: %s"%scroll_mode)

