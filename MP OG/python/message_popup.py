from PySide6.QtWidgets import QMessageBox

def message_popup(parent, message):
    """Simple message box for simple popup warnings."""
    mb = QMessageBox(parent)
    mb.setWindowTitle("Gryphon Message")
    mb.setText(message)
    mb.exec()

