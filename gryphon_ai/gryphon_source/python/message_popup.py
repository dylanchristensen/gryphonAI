from PySide6.QtWidgets import QMessageBox

def message_popup(_parent, message):
    """Simple message box for simple popup warnings."""
    mb = QMessageBox()
    mb.setText(message)
    mb.exec()

