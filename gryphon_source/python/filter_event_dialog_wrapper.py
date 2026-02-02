from PySide6.QtCore import Qt
from PySide6.QtCore import Slot # for signal/slot support
from PySide6.QtCore import QAbstractTableModel, QModelIndex, \
                           QSortFilterProxyModel, QItemSelectionModel
from PySide6.QtWidgets import QDialog, QAbstractItemView, QDialogButtonBox
from filter_event_dialog import Ui_FilterEventDialog
from filter_event_table_models import RelationshipTableModel, \
                                      RecurrenceTableModel
from filter_event_item_delegates import RelationshipItemDelegate, \
                                      RecurrenceItemDelegate

class FilterEventDialogWrapper(QDialog):

    def __init__(self, parent_window, graphs_manager, signal_mp_code_loaded):
        super().__init__(parent_window)
        self.ui = Ui_FilterEventDialog()
        self.ui.setupUi(self) # we refine this further below
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)
        self.graphs_manager = graphs_manager

        # default mode
        self.ui.and_rb.setChecked(True)
        self.use_and = True

        # event relationship
        self.relationship_table_model = RelationshipTableModel(
                                             self, signal_mp_code_loaded)
        self.relationship_item_delegate = RelationshipItemDelegate(
                                                 self, graphs_manager)
        self.relationship_view = self.ui.relationship_table_view # QTableView
        self.relationship_view.setModel(self.relationship_table_model)
        self.relationship_view.setItemDelegate(self.relationship_item_delegate)
        self.relationship_view.setColumnWidth(0, 250)
        self.relationship_view.setColumnWidth(1, 250)
        self.relationship_view.horizontalHeader().setStretchLastSection(True)
        self.relationship_view.setSelectionMode(
                         QAbstractItemView.SelectionMode.SingleSelection)

        # event recurrence
        self.recurrence_table_model = RecurrenceTableModel(
                                             self, signal_mp_code_loaded)
        self.recurrence_item_delegate = RecurrenceItemDelegate(
                                                 self, graphs_manager)
        self.recurrence_view = self.ui.recurrence_table_view
        self.recurrence_view.setModel(self.recurrence_table_model)
        self.recurrence_view.setItemDelegate(self.recurrence_item_delegate)
        self.recurrence_view.setColumnWidth(0, 250)
        self.recurrence_view.horizontalHeader().setStretchLastSection(True)
        self.recurrence_view.setSelectionMode(
                         QAbstractItemView.SelectionMode.SingleSelection)

        # initial state
        self.ui.remove_relationship_button.setEnabled(False)
        self.ui.remove_recurrence_button.setEnabled(False)

        # connect buttons
        self.ui.add_relationship_button.clicked.connect(
                                             self._add_relationship_row)
        self.ui.remove_relationship_button.clicked.connect(
                                             self._remove_relationship_row)
        self.ui.add_recurrence_button.clicked.connect(
                                             self._add_recurrence_row)
        self.ui.remove_recurrence_button.clicked.connect(
                                             self._remove_recurrence_row)
        self.ui.button_box.button(QDialogButtonBox.StandardButton.Close) \
                          .clicked.connect(self.accept)

        # connect selection model
        self.relationship_view.selectionModel().currentChanged.connect(
                            self._set_remove_relationship_button_visibility)
        self.recurrence_view.selectionModel().currentChanged.connect(
                            self._set_remove_recurrence_button_visibility)

    def event_filters(self):
        return self.relationship_table_model.relationship_list, \
               self.recurrence_table_model.recurrence_list

    @Slot(QModelIndex, QModelIndex)
    def _set_remove_relationship_button_visibility(self, current, previous):
        self.ui.remove_relationship_button.setEnabled(current.row() != -1)

    @Slot(QModelIndex, QModelIndex)
    def _set_remove_recurrence_button_visibility(self, current, previous):
        self.ui.remove_recurrence_button.setEnabled(current.row() != -1)

    @Slot()
    def _add_relationship_row(self):
        self.relationship_table_model.add_row()
        self.relationship_view.selectionModel().setCurrentIndex(
              self.relationship_table_model.index(
               self.relationship_table_model.rowCount() - 1, 0, QModelIndex()),
              QItemSelectionModel.SelectionFlag.ClearAndSelect)

    @Slot()
    def _add_recurrence_row(self):
        self.recurrence_table_model.add_row()
        self.recurrence_view.selectionModel().setCurrentIndex(
              self.recurrence_table_model.index(
               self.recurrence_table_model.rowCount() - 1, 0, QModelIndex()),
              QItemSelectionModel.SelectionFlag.ClearAndSelect)

    @Slot()
    def _remove_relationship_row(self):
        indexes = self.relationship_view.selectionModel().selectedIndexes()
        if len(indexes) != 1:
            raise RuntimeError("bad")
        self.relationship_table_model.remove_row(indexes[0].row())

    @Slot()
    def _remove_recurrence_row(self):
        indexes = self.recurrence_view.selectionModel().selectedIndexes()
        if len(indexes) != 1:
            raise RuntimeError("bad")
        self.recurrence_table_model.remove_row(indexes[0].row())


