from PySide6.QtCore import Qt, Slot
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QModelIndex

"""
Provides table models:
  * RelationshipTableModel: [["any event", "any event", ">=", 1]]
  * RecurrenceTableModel: [["any event", ">=", 1]]
"""
RELATIONSHIP_TABLE_HEADERS = ["From event", "To event",
                               "Equality", "Threshold"]
RECURRENCE_TABLE_HEADERS = ["Event", "Equality", "Threshold"]
NEW_RELATIONSHIP_ROW = ["any event", "any event", ">=", 1]
NEW_RECURRENCE_ROW = ["any event", ">=", 1]

class RelationshipTableModel(QAbstractTableModel):
    """Defines filterable relationships between pairs of events.
       Use "any event" for wildcard events."""

    def __init__(self, parent, signal_mp_code_loaded):
        super().__init__(parent)

        # the list of relationships to filter with
        self.relationship_list = list()

        # connect
        signal_mp_code_loaded.connect(self.clear_table)

    @Slot()
    def clear_table(self):
        self.beginResetModel()
        self.relationship_list.clear()
        self.endResetModel()

    def add_row(self):
        index = len(self.relationship_list)
        self.beginInsertRows(QModelIndex(), index, index)
        self.relationship_list.append(NEW_RELATIONSHIP_ROW.copy())
        self.endInsertRows()

    def remove_row(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        del self.relationship_list[index]
        self.endRemoveRows()
  
    def headerData(self, section, orientation,
                                   role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole \
                            and orientation == Qt.Orientation.Horizontal:
            return RELATIONSHIP_TABLE_HEADERS[section]
        else:
            return None # QVariant()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self.relationship_list)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(RELATIONSHIP_TABLE_HEADERS)

    def data(self, model_index, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.DisplayRole \
                                or role == Qt.ItemDataRole.EditRole:
            row = model_index.row()
            column = model_index.column()
            return self.relationship_list[row][column]
        else:
            return None # QVariant()

    def setData(self, model_index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row = model_index.row()
            column = model_index.column()
            self.relationship_list[row][column] = value
            self.dataChanged.emit(model_index, model_index, [])
            return True
        else:
            print("unexpected role")
            return False

    def flags(self, model_index):
        return super().flags(model_index) | Qt.ItemIsEditable

class RecurrenceTableModel(QAbstractTableModel):
    """Defines filterable recurrence of events.
       Use "any event" for wildcard events."""

    def __init__(self, parent, signal_mp_code_loaded):
        super().__init__(parent)

        # the list of recurrences to filter with
        self.recurrence_list = list()

        # connect
        signal_mp_code_loaded.connect(self.clear_table)

    @Slot()
    def clear_table(self):
        self.beginResetModel()
        self.recurrence_list.clear()
        self.endResetModel()

    def add_row(self):
        index = len(self.recurrence_list)
        self.beginInsertRows(QModelIndex(), index, index)
        self.recurrence_list.append(NEW_RECURRENCE_ROW.copy())
        self.endInsertRows()
  
    def remove_row(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        del self.recurrence_list[index]
        self.endRemoveRows()

    def headerData(self, section, orientation,
                                   role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole \
                            and orientation == Qt.Orientation.Horizontal:
            return RECURRENCE_TABLE_HEADERS[section]
        else:
            return None # QVariant()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self.recurrence_list)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(RECURRENCE_TABLE_HEADERS)

    def data(self, model_index, role=Qt.ItemDataRole.EditRole):

        if role == Qt.ItemDataRole.DisplayRole \
                                or role == Qt.ItemDataRole.EditRole:
            row = model_index.row()
            column = model_index.column()
            return self.recurrence_list[row][column]
        else:
            return None # QVariant()

    def setData(self, model_index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row = model_index.row()
            column = model_index.column()
            self.recurrence_list[row][column] = value
            self.dataChanged.emit(model_index, model_index, [])
            return True
        else:
            print("unexpected role")
            return False

    def flags(self, model_index):
        return super().flags(model_index) | Qt.ItemIsEditable


