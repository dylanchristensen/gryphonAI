"""
Reusable UI components for Gryphon AI extension.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QProgressBar
)
from PySide6.QtCore import Qt


class ProgressDialog(QDialog):
    """Reusable progress dialog for long-running operations."""
    
    def __init__(self, parent=None, title="Processing", message="Please wait..."):
        """
        Initialize the progress dialog.
        
        Args:
            parent: Parent widget
            title: Dialog window title
            message: Message to display
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)
        
        # Progress bar (indeterminate)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def set_message(self, message: str):
        """Update the progress message."""
        self.message_label.setText(message)
    
    def set_cancellable(self, cancellable: bool):
        """Enable or disable the cancel button."""
        self.cancel_button.setEnabled(cancellable)
        self.cancel_button.setVisible(cancellable)


class ResultDialog(QDialog):
    """Dialog for displaying LLM results."""
    
    def __init__(self, parent=None, title="Result", content=""):
        """
        Initialize the result dialog.
        
        Args:
            parent: Parent widget
            title: Dialog window title
            content: Content to display
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Text area for content
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(content)
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.text_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def set_content(self, content: str):
        """Update the content."""
        self.text_edit.setPlainText(content)
    
    def _copy_to_clipboard(self):
        """Copy content to clipboard."""
        clipboard = self.text_edit.textCursor().selectedText()
        if not clipboard:
            clipboard = self.text_edit.toPlainText()
        
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(clipboard)
