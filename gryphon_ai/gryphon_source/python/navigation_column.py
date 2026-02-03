from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout

from graph_list_sort_and_filter import GraphListSortAndFilter

class NavigationColumn(QWidget):
    """Container for global view, trace selector, sorting and filtering,
       and the trace list"""

    def __init__(self, gui_manager):
        super(NavigationColumn, self).__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # graph list selection spinner
        layout.addWidget(gui_manager.graph_list_selection_spinner.container)

        # graph list sort and filter menu pushbuttons
        self.graph_list_sort_and_filter = GraphListSortAndFilter(
                                            gui_manager.graph_list_table)
        layout_h = QHBoxLayout()
        layout_h.setContentsMargins(0, 0, 0, 0)
        layout_h.addWidget(self.graph_list_sort_and_filter.sort_menu_button)
        layout_h.addWidget(self.graph_list_sort_and_filter.filter_menu_button)
        layout_h.addStretch()
        container_h = QWidget()
        container_h.setLayout(layout_h)
        layout.addWidget(container_h)

        # graph list
        layout.addWidget(gui_manager.graph_list_table.view)
        gui_manager.graph_list_table.view.setMinimumWidth(50)

        # set layout
        self.setLayout(layout)

