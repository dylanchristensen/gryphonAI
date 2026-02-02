from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox, QSpinBox
from mp_code_parser import mp_code_event_dict, mp_code_event_list

"""
Provides widgets for the cells for relationship and recurrence event filters.
"""

ANY_EVENT = "any event"
EQUALITY_TOKENS = ["==", "!=", "<=", "<", ">=", ">"]

class RelationshipItemDelegate(QStyledItemDelegate):
    """Cells are: from event, to event, equality, threshold.

    Signals:
      * signal_relationship_changed
    """

    # signal
    signal_relationship_changed = Signal(name='relationshipChanged')

    def __init__(self, parent_widget, graphs_manager):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.graphs_manager = graphs_manager

    # create widget
    def createEditor(self, parent_widget, option, model_index):
        column = model_index.column()
        if column == 0 or column == 1:
            event_list = mp_code_event_list(mp_code_event_dict(
                                              self.graphs_manager.mp_code))
            cb = QComboBox(parent_widget)
            cb.insertItem(0, ANY_EVENT)
            cb.insertItems(1, event_list)
            def _index_changed(_index):
                self.commitData.emit(cb)
            cb.currentIndexChanged.connect(_index_changed)
            return cb
        elif column == 2:
            cb = QComboBox(parent_widget)
            cb.insertItems(0, EQUALITY_TOKENS)
            def _index_changed(_index):
                self.commitData.emit(cb)
            cb.currentIndexChanged.connect(_index_changed)
            return cb
        elif column == 3:
            spinner = QSpinBox(parent_widget)
            def _value_changed(_value):
                self.commitData.emit(spinner)
            spinner.valueChanged.connect(_value_changed)
            return spinner
        raise RuntimeError("bad")

    # put model value into widget
    def setEditorData(self, editor, model_index):
        value = model_index.model().data(model_index, Qt.EditRole)
        column = model_index.column()
        editor.blockSignals(True) # signaling causes a commitData warning
        if column == 0 or column == 1 or column == 2:
            editor.setCurrentText(value)
        elif column == 3:
            editor.setValue(int(value))
        else:
            raise RuntimeError("bad")
        editor.blockSignals(False)
        self.signal_relationship_changed.emit()

    # put widget value into model
    def setModelData(self, editor, model, model_index):
        column = model_index.column()
        if column == 0 or column == 1 or column == 2:
            value = editor.currentText()
            model.setData(model_index, value, Qt.EditRole)
        elif column == 3:
            value = editor.value()
            model.setData(model_index, value, Qt.EditRole)
        else:
            raise RuntimeError("bad")

    def updateEditorGeometry(self, editor, option, _model_index):
        editor.setGeometry(option.rect)

class RecurrenceItemDelegate(QStyledItemDelegate):
    """Cells are: event, equality, threshold.

    Signals:
      * signal_recurrence_changed
    """

    # signal
    signal_recurrence_changed = Signal(name='recurrenceChanged')

    def __init__(self, parent_widget, graphs_manager):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.graphs_manager = graphs_manager

    # create widget
    def createEditor(self, parent_widget, option, model_index):
        column = model_index.column()
        if column == 0:
            event_list = mp_code_event_list(mp_code_event_dict(
                                              self.graphs_manager.mp_code))
            cb = QComboBox(parent_widget)
            cb.insertItem(0, ANY_EVENT)
            cb.insertItems(1, event_list)
            def _index_changed(_index):
                self.commitData.emit(cb)
            cb.currentIndexChanged.connect(_index_changed)
            return cb
        elif column == 1:
            cb = QComboBox(parent_widget)
            cb.insertItems(0, EQUALITY_TOKENS)
            def _index_changed(_index):
                self.commitData.emit(cb)
            cb.currentIndexChanged.connect(_index_changed)
            return cb
        elif column == 2:
            spinner = QSpinBox(parent_widget)
            def _value_changed(_value):
                self.commitData.emit(spinner)
            spinner.valueChanged.connect(_value_changed)
            return spinner
        raise RuntimeError("bad")

    # put model value into widget
    def setEditorData(self, editor, model_index):
        value = model_index.model().data(model_index, Qt.EditRole)
        column = model_index.column()
        editor.blockSignals(True) # signaling causes a commitData warning
        if column == 0 or column == 1:
            editor.setCurrentText(value)
        elif column == 2:
            editor.setValue(int(value))
        else:
            raise RuntimeError("bad")
        editor.blockSignals(False)
        self.signal_recurrence_changed.emit()

    # put widget value into model
    def setModelData(self, editor, model, model_index):
        column = model_index.column()
        if column == 0 or column == 1:
            value = editor.currentText()
            model.setData(model_index, value, Qt.EditRole)
        elif column == 2:
            value = editor.value()
            model.setData(model_index, value, Qt.EditRole)
        else:
            raise RuntimeError("bad")

    def updateEditorGeometry(self, editor, option, _model_index):
        editor.setGeometry(option.rect)

