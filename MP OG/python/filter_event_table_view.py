from PySide6.QtCore import Qt, Slot, QModelIndex
from PySide6.QtWidgets import QTableView

class FilterEventTableView(QTableView):
    def __init__(self, parent):
        super().__init__(parent)

    # when we set the model it internally defines the selection model
    def setModel(self, table_model):
        super().setModel(table_model)

        # we put this here instead of in __init__ because table_model
        # doesn't exist yet
        table_model.rowsInserted.connect(self._open_persistent_editors)

        # also make a data reset clear the selection model
        table_model.modelReset.connect(self._force_emit_current_changed)

    @Slot(QModelIndex, int, int)
    def _open_persistent_editors(self, _parent, first, last):

        # make each cell in new row be a persistent editor
        for i in range(self.model().columnCount()):
            self.openPersistentEditor(self.model().index(first, i))

    @Slot()
    def _force_emit_current_changed(self):
        # Force emit change because selection model clears selection
        # without emitting change.
        self.selectionModel().currentChanged.emit(QModelIndex(), QModelIndex())

