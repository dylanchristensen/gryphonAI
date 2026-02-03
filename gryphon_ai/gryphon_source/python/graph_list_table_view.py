from PySide6.QtCore import Slot
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QAbstractItemView
from graph_list_table_view_delegate import GraphListTableViewDelegate
from graph_list_table_model import COLUMN_COUNT

class GraphListTableView(QTableView):

    def __init__(self, parent, graph_list_table,
                 navigation_column_width_manager, preferences_manager):
        super(GraphListTableView, self).__init__(parent)
        self.graph_list_table = graph_list_table
        self.setModel(graph_list_table.proxy_model)
        for i in range(1, COLUMN_COUNT):
            self.setColumnHidden(i, True)
        self.setColumnWidth(0, 20) # otherwise minimum is 100
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setShowGrid(False)
        view_delegate = GraphListTableViewDelegate(graph_list_table,
                                          navigation_column_width_manager)
        self.setItemDelegate(view_delegate)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setSectionResizeMode(
                                     QHeaderView.ResizeMode.ResizeToContents)

        navigation_column_width_manager.signal_navigation_column_width_changed\
                                      .connect(self.changed_width)

        # connect preferences
        preferences_manager.signal_scroll_mode_changed.connect(
                                                      self._set_scroll_mode)
        self._set_scroll_mode(preferences_manager.scroll_mode())

    # user selection changed
    def currentChanged(self, current, _previous):
        graph_index, _column = self.graph_list_table\
                           .proxy_model_index_to_graph_index(current)
        self.graph_list_table.graphs_manager.set_selection(graph_index)

    # width changed
    @Slot(int)
    def changed_width(self, _width):
        self.resizeRowsToContents()

    # scroll mode preference changed
    @Slot(str)
    def _set_scroll_mode(self, scroll_mode):
        if scroll_mode == "scroll_per_pixel":
            self.setVerticalScrollMode(
                            QAbstractItemView.ScrollMode.ScrollPerPixel)
        elif scroll_mode == "scroll_per_item":
            self.setVerticalScrollMode(
                            QAbstractItemView.ScrollMode.ScrollPerItem)
        else:
            raise RuntimeError("bad")

