from PySide6.QtCore import Slot
from PySide6.QtCore import Qt
from PySide6.QtCore import QSortFilterProxyModel
from graph_list_table_model import MARK_COLUMN

class GraphListSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, source_model,
                 signal_preferences_changed, signal_settings_changed):
        super().__init__()
        super().setSourceModel(source_model)
        self._clear_filter()

        # connect to redraw everything when settings change
        signal_settings_changed.connect(self.data_changed)

        # connect to redraw everything when probability view preference changes
        signal_preferences_changed.connect(self.data_changed)

    @Slot()
    def data_changed(self):
        super().dataChanged.emit(super().index(0, 0),
                                 super().index(super().rowCount(), 0))

    def _clear_filter(self):
        # filters, see graph list sort and filter managers
        filter_selections = {
                    "hide_global_view": False,
                    "hide_unmarked": False,
                    "disable_custom_event_filtering": True,
                    "matched_event_condition_traces": None,
                            }
        self.set_filter(filter_selections)

    def set_filter(self, filter_selections):
        self.hide_global_view = filter_selections["hide_global_view"]
        self.hide_unmarked = filter_selections["hide_unmarked"]
        self.disable_custom_event_filtering \
                   = filter_selections["disable_custom_event_filtering"]
        self.matched_event_condition_traces \
                   = filter_selections["matched_event_condition_traces"]

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
        return super().sourceModel().data(left_model_index) \
                   < super().sourceModel().data(right_model_index)

    # fully control custom filtering
    def filterAcceptsRow(self, row, source_parent):

        # hide_global_view
        if row == 0:
            return not self.hide_global_view

        # hide_unmarked
        if self.hide_unmarked:
            mark_index = super().sourceModel().index(
                                       row, MARK_COLUMN, source_parent)
            if super().sourceModel().data(mark_index) != "M":
                return False

        # disable_custom_event_filtering
        if not self.disable_custom_event_filtering \
                        and not row in self.matched_event_condition_traces:
            return False

        return True

