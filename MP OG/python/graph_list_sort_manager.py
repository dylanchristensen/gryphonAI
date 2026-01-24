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
from graph_list_table_model import GRAPH_COLUMN, TRACE_INDEX_COLUMN, \
                           MARK_COLUMN, PROBABILITY_COLUMN, SIZE_COLUMN
import resources_rc

class GraphListSortManager(QObject):
    """Provides sort_menu_pb sort controls and connects them to the
       sort filter proxy model."""

    def __init__(self, gui_manager):
        super().__init__()
        self.graph_list_proxy_model = \
                   gui_manager.graph_list_proxy_model
        self.graph_list_table_dialog = gui_manager.graph_list_table_dialog

        # connect to reset selections on graphs loaded event
        gui_manager.graphs_manager.signal_graphs_loaded.connect(
                                                     self._reset_selections)

        self._add_sort_menu()

    def _triggered_function_function(self, sort_column, direction):
        @Slot(bool)
        def _triggered_function(_is_checked):
            self.graph_list_proxy_model.sort(sort_column, direction)
        return _triggered_function


    def _make_ascending_sort_action(self, menu, text, sort_column):
        action = QAction(QIcon(":/icons/sort_ascending"), text, menu)
        action.setCheckable(True)
        action.triggered.connect(self._triggered_function_function(
                                 sort_column, Qt.SortOrder.AscendingOrder))
        self.sort_group.addAction(action)
        return action

    def _make_descending_sort_action(self, menu, text, sort_column):
        action = QAction(QIcon(":/icons/sort_descending"), text, menu)
        action.setCheckable(True)
        action.triggered.connect(self._triggered_function_function(
                                 sort_column, Qt.SortOrder.DescendingOrder))
        self.sort_group.addAction(action)
        return action

    # create sort_menu and sort actions and connect them
    def _add_sort_menu(self):
        self.sort_menu = QMenu()
        self.sort_group = QActionGroup(self)
        ascending = Qt.SortOrder.AscendingOrder
        descending = Qt.SortOrder.DescendingOrder

        # marked
        self.sort_menu.addAction(self._make_ascending_sort_action(
                                     self.sort_menu, "&Marked", MARK_COLUMN))

        # size
        sort_menu_size = self.sort_menu.addMenu("&Size")
        sort_menu_size.addAction(self._make_ascending_sort_action(
                              sort_menu_size, "Ascending", SIZE_COLUMN))
        sort_menu_size.addAction(self._make_descending_sort_action(
                              sort_menu_size, "Descending", SIZE_COLUMN))

        # probability
        sort_menu_probability = self.sort_menu.addMenu("&Probability")
        sort_menu_probability.addAction(self._make_ascending_sort_action(
                       sort_menu_probability, "Ascending", PROBABILITY_COLUMN))
        sort_menu_probability.addAction(self._make_descending_sort_action(
                       sort_menu_probability, "Descending", PROBABILITY_COLUMN))

        # trace index
        sort_menu_trace_index = self.sort_menu.addMenu("&Trace index")
        sort_menu_trace_index.addAction(self._make_ascending_sort_action(
                       sort_menu_trace_index, "Ascending", TRACE_INDEX_COLUMN))
        sort_menu_trace_index.addAction(self._make_descending_sort_action(
                       sort_menu_trace_index, "Descending", TRACE_INDEX_COLUMN))

        # sort by attribute
        action_sort_by_attribute = QAction("Sort by &attribute...",
                                           self.sort_menu)
        action_sort_by_attribute.setToolTip("Sort traces by attribute value")
        action_sort_by_attribute.triggered.connect(self._sort_by_attribute)
        self.sort_menu.addSeparator()
        self.sort_menu.addAction(action_sort_by_attribute)

        # sort menu button
        self.sort_menu_button = mp_menu_button(self.sort_menu,
                                               QIcon(":/icons/sort_ascending"),
                                               "Sort",
                                               "Sort the events list")

    @Slot()
    def _sort_by_attribute(self):
        self.graph_list_table_dialog.show()
        
    @Slot()
    def _reset_selections(self):
        self.sort_group.actions()[0].setChecked(True)
        self.graph_list_proxy_model.sort(TRACE_INDEX_COLUMN,
                                          Qt.SortOrder.AscendingOrder)

