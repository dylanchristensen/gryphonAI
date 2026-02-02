from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QHBoxLayout, \
                              QToolButton
from PySide6.QtWidgets import QAbstractSpinBox
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import QObject, QModelIndex

# https://stackoverflow.com/questions/29824591/qsortfilterproxymodel-filtering-complete-signal

class GraphListSelectionSpinner(QObject):
    """Trace selection navigation."""

    def __init__(self, graph_list_proxy_model, graph_list_selection_model):
        super().__init__()

        self.graph_list_proxy_model = graph_list_proxy_model
        self.graph_list_selection_model = graph_list_selection_model

        # connect
        graph_list_proxy_model.modelReset.connect(self._set_spinner_range)
        graph_list_selection_model.currentChanged.connect(
                                             self._set_spinner_value)

        # connect for filter
        graph_list_proxy_model.rowsRemoved.connect(self._set_spinner_range)
        graph_list_proxy_model.rowsInserted.connect(self._set_spinner_range)

        # connect for sort
        graph_list_proxy_model.layoutChanged.connect(self._set_spinner_range)

        # left and right arrow buttons
        self.left_arrow_pb = QToolButton()
        self.left_arrow_pb.setIcon(QIcon(":/icons/left_arrow"))
        self.left_arrow_pb.pressed.connect(self._navigate_left)
        self.right_arrow_pb = QToolButton()
        self.right_arrow_pb.setIcon(QIcon(":/icons/right_arrow"))
        self.right_arrow_pb.pressed.connect(self._navigate_right)

        # spin box
        self.spinner = QSpinBox()
        self.spinner.setToolTip("Select a trace number")
        self.spinner.setSizePolicy(QSizePolicy.Policy.Maximum,
                                   QSizePolicy.Policy.Maximum)
        self.spinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spinner.setWrapping(True)
        self.spinner.valueChanged.connect(self._spinner_value_changed)
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
        self._ignore_value_change = False
        self._set_spinner_range()

    def _maybe_set_disabled(self, row_count):

        # enable or disable inputs inside the container based on state
        do_disable_navigation = row_count < 2
        do_disable_label = row_count == 0
        self.left_arrow_pb.setDisabled(do_disable_navigation)
        self.right_arrow_pb.setDisabled(do_disable_navigation)
        self.spinner.setDisabled(do_disable_navigation)
        self.total_count_label.setDisabled(do_disable_label)

    @Slot()
    def _navigate_left(self):
        # decrement with wrap-around
        row_count = self.graph_list_proxy_model.rowCount()
        index = self.spinner.value()
        if self.graph_list_proxy_model.hide_global_view:
            if index == 1:
                new_index = row_count
            else:
                new_index = index - 1
        else:
            if index == 0:
                new_index = row_count - 1
            else:
                new_index = index - 1
        self.spinner.setValue(new_index)

    @Slot()
    def _navigate_right(self):
        # increment with wrap-around
        row_count = self.graph_list_proxy_model.rowCount()
        index = self.spinner.value()
        if self.graph_list_proxy_model.hide_global_view:
            if index == row_count:
                new_index = 1
            else:
                new_index = index + 1
        else:
            if index == row_count:
                new_index = 0
            else:
                new_index = index + 1
        self.spinner.setValue(new_index)

    # proxy range changes when the filter changes
    @Slot()
    def _set_spinner_range(self):
        self._ignore_value_change = True
        row_count = self.graph_list_proxy_model.rowCount()
        if row_count == 0:
            # no data
            self.spinner.setRange(0, row_count)
            self.total_count_label.setText("of %d"%(row_count))

        elif self.graph_list_proxy_model.hide_global_view:
            # no global view
            self.spinner.setRange(1, row_count)
            self.total_count_label.setText("of %d"%(row_count))
        else:
            # global view at [0]
            self.spinner.setRange(0, row_count - 1)
            self.total_count_label.setText("of %d"%(row_count - 1))
        self._maybe_set_disabled(row_count)
        self._ignore_value_change = False

    # set spinner value to match the graph list selection
    @Slot(QModelIndex, QModelIndex)
    def _set_spinner_value(self, current_index, _previous_index):
        value = current_index.row()
        if self.graph_list_proxy_model.hide_global_view:
            value += 1
        self._ignore_value_change = True
        self.spinner.setValue(value)
        self._ignore_value_change = False

    # spinner value changed
    @Slot(int)
    def _spinner_value_changed(self, value):
        if not self._ignore_value_change:
            if self.graph_list_proxy_model.hide_global_view:
                value -= 1
            self.graph_list_selection_model.select_proxy_index(value)

