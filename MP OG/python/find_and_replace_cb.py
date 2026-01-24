from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QKeyEvent

class FindAndReplaceCB(QComboBox):
    """A QComboBox that signals when the user presses Enter."""
    def __init__(self, parent):
        super().__init__(parent)

    def set_enter_listener_function(self, enter_listener_function):
        self.enter_listener_function = enter_listener_function

    @Slot(QKeyEvent)
    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.Key_Enter or key_event.key() == Qt.Key_Return:
            self.enter_listener_function()
        super().keyPressEvent(key_event)

