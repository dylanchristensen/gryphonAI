from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QHBoxLayout, \
                              QToolButton
from PySide6.QtWidgets import QAbstractSpinBox
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import QObject

class GraphListSelectionSpinner(QObject):
    """The trace selection spinner."""

    @Slot()
    def _navigate_left(self):
        selected_graph_index = self.graphs_manager.selected_graph_index
        self.graphs_manager.set_selection(selected_graph_index - 1)

    @Slot()
    def _navigate_right(self):
        selected_graph_index = self.graphs_manager.selected_graph_index
        self.graphs_manager.set_selection(selected_graph_index + 1)

    def __init__(self, graphs_manager, graph_list_table):
        super(GraphListSelectionSpinner, self).__init__()

        self.graphs_manager = graphs_manager
        self.graph_list_table = graph_list_table

        # state
        self.disabled_for_compiler = False

        # connect
        graphs_manager.signal_graphs_loaded.connect(self.set_range)
        graphs_manager.signal_graph_selection_changed.connect(
                                             self._set_selected_graph_index)

        # left and right arrow buttons
        self.left_arrow_pb = QToolButton()
        self.left_arrow_pb.setIcon(QIcon(":/icons/left_arrow"))
        self.left_arrow_pb.pressed.connect(self._navigate_left)
        self.right_arrow_pb = QToolButton()
        self.right_arrow_pb.setIcon(QIcon(":/icons/right_arrow"))
        self.right_arrow_pb.pressed.connect(self._navigate_right)

        # spin box
        self.spinner = QSpinBox()
        self.spinner.setStatusTip("Select a trace number")
        self.spinner.setToolTip("Select a trace number")
        self.spinner.setSizePolicy(QSizePolicy.Policy.Maximum,
                                   QSizePolicy.Policy.Maximum)
        self.spinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spinner.valueChanged.connect(self._value_changed)
        self.total_count_label = QLabel()

        # layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.left_arrow_pb)
        layout.addWidget(self.right_arrow_pb)
        layout.addWidget(self.spinner)
        layout.addWidget(self.total_count_label)

        # container
        self.container = QWidget()
        self.container.setLayout(layout)
        self._ignore_selection_change = False
        self.set_range([], "", -1)

    # We want the spinner disabled while compiling, when there are no graphs,
    # and when the global view at index 0 is selected.
    def set_disable_for_compiler(self, disable):
        self.disabled_for_compiler = disable
        self._maybe_set_disabled()

    def _maybe_set_disabled(self):

        # maybe disable the whole container
        if self.disabled_for_compiler:
            self.container.setDisabled(True)
            # this encompases all available inputs
            return
        else:
            self.container.setDisabled(False)

        # enable or disable inputs inside the container based on state
        graph_size = len(self.graphs_manager.graphs)
        selected_graph_index = self.graphs_manager.selected_graph_index
        
        # left arrow
        if self.graphs_manager.has_non_empty_global_view:
            smallest = 0
        else:
            smallest = 1
        self.left_arrow_pb.setDisabled(selected_graph_index <= smallest)

        # right arrow
        self.right_arrow_pb.setDisabled(selected_graph_index >= graph_size - 1)

        # spinner and text
        has_graphs = bool(self.graphs_manager.graphs)
        self.spinner.setDisabled(not has_graphs)
        self.total_count_label.setDisabled(not has_graphs)

    @Slot(list, str, int)
    def set_range(self, graphs, _schema_name, _scope):
        self._ignore_selection_change = True
        if graphs:
            self.spinner.setRange(0, len(graphs) - 1)
            self.total_count_label.setText(
                                 "of %d"%(len(graphs) - 1))
        else:
            self.spinner.setRange(0,0)
            self.total_count_label.setText("of 0")
        self._maybe_set_disabled()
        self._ignore_selection_change = False

    # set current trace number using this event
    @Slot(int)
    def _set_selected_graph_index(self, selected_graph_index):
        self._ignore_selection_change = True
        self.spinner.setValue(selected_graph_index)
        self._ignore_selection_change = False
        self._maybe_set_disabled()

    # entry for spinner
    @Slot(int)
    def _value_changed(self, selected_graph_index):
        if not self._ignore_selection_change:
            self.graphs_manager.set_selection(selected_graph_index)
        self._maybe_set_disabled()

