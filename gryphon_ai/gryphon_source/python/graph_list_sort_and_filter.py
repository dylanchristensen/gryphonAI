from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QCheckBox, QPushButton
from PySide6.QtWidgets import QSizePolicy
from mp_style import mp_menu_button
import resources_rc

class GraphListSortAndFilter(QObject):
    """Provides sort_menu_pb and filter_menu_pb for sort and filter controls."""

    def __init__(self, graph_list_table):
        super(GraphListSortAndFilter, self).__init__()
        self.graph_list_table = graph_list_table

        # connect to reset selections on graphs loaded event
        graph_list_table.graphs_manager.signal_graphs_loaded.connect(
                                                     self.reset_selections)

        # sort action trace index
        self.action_sort_trace_index_ascending = QAction("Trace index")
        self.action_sort_trace_index_ascending.setCheckable(True)
        self.action_sort_trace_index_ascending.triggered.connect(
                                graph_list_table.sort_trace_index_ascending)

        self.action_sort_trace_index_descending = QAction("Trace index")
        self.action_sort_trace_index_descending.setCheckable(True)
        self.action_sort_trace_index_descending.triggered.connect(
                                graph_list_table.sort_trace_index_descending)

        # sort action mark
        self.action_sort_mark_ascending = QAction("Mark")
        self.action_sort_mark_ascending.setCheckable(True)
        self.action_sort_mark_ascending.triggered.connect(
                                     graph_list_table.sort_mark_ascending)

        self.action_sort_mark_descending = QAction("Mark")
        self.action_sort_mark_descending.setCheckable(True)
        self.action_sort_mark_descending.triggered.connect(
                                     graph_list_table.sort_mark_descending)

        # sort action probability
        self.action_sort_probability_ascending = QAction("Probability")
        self.action_sort_probability_ascending.setCheckable(True)
        self.action_sort_probability_ascending.triggered.connect(
                            graph_list_table.sort_probability_ascending)

        self.action_sort_probability_descending = QAction("Probability")
        self.action_sort_probability_descending.setCheckable(True)
        self.action_sort_probability_descending.triggered.connect(
                            graph_list_table.sort_probability_descending)

        # sort action size
        self.action_sort_size_ascending = QAction("Size")
        self.action_sort_size_ascending.setCheckable(True)
        self.action_sort_size_ascending.triggered.connect(
                            graph_list_table.sort_size_ascending)

        self.action_sort_size_descending = QAction("Size")
        self.action_sort_size_descending.setCheckable(True)
        self.action_sort_size_descending.triggered.connect(
                            graph_list_table.sort_size_descending)

        # sort group
        self.sort_group = QActionGroup(self)
        self.sort_group.addAction(self.action_sort_trace_index_ascending)
        self.sort_group.addAction(self.action_sort_mark_ascending)
        self.sort_group.addAction(self.action_sort_probability_ascending)
        self.sort_group.addAction(self.action_sort_size_ascending)
        self.sort_group.addAction(self.action_sort_trace_index_descending)
        self.sort_group.addAction(self.action_sort_mark_descending)
        self.sort_group.addAction(self.action_sort_probability_descending)
        self.sort_group.addAction(self.action_sort_size_descending)

        # sort menu and button
        self.sort_menu = QMenu()
        sort_menu_ascending = self.sort_menu.addMenu(
                                          QIcon(":/icons/sort_ascending"),
                                          "Ascending")
        sort_menu_ascending.addAction(self.action_sort_trace_index_ascending)
        sort_menu_ascending.addAction(self.action_sort_probability_ascending)
        sort_menu_ascending.addAction(self.action_sort_mark_ascending)
        sort_menu_ascending.addAction(self.action_sort_size_ascending)

        sort_menu_descending = self.sort_menu.addMenu(
                         QIcon(":/icons/sort_descending"), "Descending")
        sort_menu_descending.addAction(self.action_sort_trace_index_descending)
        sort_menu_descending.addAction(self.action_sort_probability_descending)
        sort_menu_descending.addAction(self.action_sort_mark_descending)
        sort_menu_descending.addAction(self.action_sort_size_descending)

        self.sort_menu_button = mp_menu_button(self.sort_menu,
                                               QIcon(":/icons/sort_ascending"),
                                               "Sort",
                                               "Sort the events list")

        # filter action
        self.action_filter_mark = QAction("Hide unmarked traces")
        self.action_filter_mark.setStatusTip("Filter to see marked traces only")
        self.action_filter_mark.setCheckable(True)
        self.action_filter_mark.triggered.connect(self._filter)

        # filter menu
        self.filter_menu = QMenu()
        self.filter_menu.addAction(self.action_filter_mark)

        # filter button
        self.filter_menu_button = mp_menu_button(self.filter_menu,
                                                 QIcon(":/icons/filter"),
                                                 "Filter",
                                                 "Filter the events list")

        # initial state
        self.reset_selections(None, None, None)

    @Slot()
    def _filter(self):
        # change the filter model
        self.graph_list_table.filter(self.action_filter_mark.isChecked(),
               self.graph_list_table.graphs_manager.has_non_empty_global_view())

    @Slot(list, str, int)
    def reset_selections(self, _graphs, _schema_name, _scope):
        self.action_filter_mark.setChecked(False)
        self.action_sort_trace_index_ascending.setChecked(True)
        self.graph_list_table.sort_trace_index_ascending()
        self._filter()

