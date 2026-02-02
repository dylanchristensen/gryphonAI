from copy import deepcopy
from PySide6.QtCore import QObject # for signal/slot support
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu
from mp_style import mp_menu_button
from filter_event_dialog_wrapper import FilterEventDialogWrapper
from filter_event_conditions import regenerate_trace_set
import resources_rc

class GraphListFilterManager(QObject):
    """Oversees filtering: Provides the filter menu, wraps filter inputs,
       and calls graph_list_proxy_model set_filter."""

    def __init__(self, gui_manager):
        super().__init__()
        self.graph_list_proxy_model = gui_manager.graph_list_proxy_model

        self.filter_event_dialog_wrapper = FilterEventDialogWrapper(
                          gui_manager.w, gui_manager.graphs_manager,
                          gui_manager.mp_code_manager.signal_mp_code_loaded)

        self.graphs_manager = gui_manager.graphs_manager

        # event conditions inputs and outputs
        self._cached_relationship_list = None
        self._cached_recurrence_list = None
        self._cached_event_trace_set = set()
        self._cached_event_condition_traces_use_or = None
        self._cached_event_trace_set_is_valid = False

        # connect to clear filter inputs when mp code is loaded
        gui_manager.mp_code_manager.signal_mp_code_loaded.connect(
                                                     self._reset_state)

        # connect to rerun the filter when graphs are loaded
        self.graphs_manager.signal_graphs_loaded.connect(self._reset_state)

        # connect to rerun the filter when filter inputs change
        self.filter_event_dialog_wrapper.relationship_item_delegate \
                          .signal_relationship_changed.connect(self._filter)
        self.filter_event_dialog_wrapper.recurrence_item_delegate \
                          .signal_recurrence_changed.connect(self._filter)
        self.filter_event_dialog_wrapper.ui.or_rb.toggled.connect(self._filter)
        self.filter_event_dialog_wrapper.relationship_table_model \
                          .rowsInserted.connect(self._filter)
        self.filter_event_dialog_wrapper.relationship_table_model \
                          .rowsRemoved.connect(self._filter)
        self.filter_event_dialog_wrapper.recurrence_table_model \
                          .rowsInserted.connect(self._filter)
        self.filter_event_dialog_wrapper.recurrence_table_model \
                          .rowsRemoved.connect(self._filter)

        # the filter menu, specifically, filter_menu_button
        self._make_filter_menu()

    # create filter_menu and filter actions and connect them
    def _make_filter_menu(self):
        # filter action mark
        self.action_filter_mark = QAction("&Hide unmarked traces")
        self.action_filter_mark.setToolTip("Filter to see marked traces only")
        self.action_filter_mark.setCheckable(True)
        self.action_filter_mark.triggered.connect(self._filter)

        # define filter event conditions
        self.action_custom_event_filters = QAction(
                                       "&Custom event filters...")
        self.action_custom_event_filters.setToolTip(
                      "Define event conditions for finding specific traces")
        self.action_custom_event_filters.triggered.connect(
                          self.filter_event_dialog_wrapper.show)

        # filter on event conditions
        self.action_disable_custom_event_filtering = QAction(
                                  "&Disable custom event filtering")
        self.action_disable_custom_event_filtering.setToolTip(
                    "Disable custome event filtering so that all traces show")
        self.action_disable_custom_event_filtering.setCheckable(True)
        self.action_disable_custom_event_filtering.triggered.connect(
                                                               self._filter)

        # filter menu
        self.filter_menu = QMenu()
        self.filter_menu.addAction(self.action_filter_mark)
        self.filter_menu.addSeparator()
        self.filter_menu.addAction(self.action_custom_event_filters)
        self.filter_menu.addAction(
                         self.action_disable_custom_event_filtering)

        # filter button
        self.filter_menu_button = mp_menu_button(self.filter_menu,
                                                 QIcon(":/icons/filter"),
                                                 "Filter",
                                                 "Filter the events list")

    def _maybe_refresh_event_condition_trace_set(self):
        relationship_list, recurrence_list \
                      = self.filter_event_dialog_wrapper.event_filters()
        use_or = self.filter_event_dialog_wrapper.ui.or_rb.isChecked()
        if self._cached_event_trace_set_is_valid \
                     and relationship_list == self._cached_relationship_list \
                     and recurrence_list == self._cached_recurrence_list \
                     and use_or == self._cached_event_condition_traces_use_or:
            # still valid
            return

        # regenerate trace set
        self._cached_event_trace_set = regenerate_trace_set(
                                self.graphs_manager.graphs,
                                relationship_list, recurrence_list, use_or)
        self._cached_relationship_list = deepcopy(relationship_list)
        self._cached_recurrence_list = deepcopy(recurrence_list)
        self._cached_event_condition_traces_use_or = use_or
        self._cached_event_trace_set_is_valid = True

    @Slot()
    def _filter(self):
        # pull together the filter selections
        # global view
        hide_global_view = not self.graphs_manager.has_non_empty_global_view()

        # marked traces
        hide_unmarked = self.action_filter_mark.isChecked()

        # selected event traces
        disable_custom_event_filtering \
                = self.action_disable_custom_event_filtering.isChecked()
        event_condition_traces_use_or = self.filter_event_dialog_wrapper \
                                                 .ui.or_rb.isChecked()
        if not disable_custom_event_filtering:
            self._maybe_refresh_event_condition_trace_set()

        filter_selections = {
                    "hide_global_view": hide_global_view,
                    "hide_unmarked": hide_unmarked,
                    "disable_custom_event_filtering":
                                       disable_custom_event_filtering,
                    "matched_event_condition_traces":
                                           self._cached_event_trace_set,
                            }

        # apply the filter
        self.graph_list_proxy_model.set_filter(filter_selections)

    @Slot()
    def _reset_state(self):
        self.action_filter_mark.setChecked(False)
        self.action_disable_custom_event_filtering.setChecked(False)
        self._cached_event_trace_set_is_valid = False
        self._filter()

