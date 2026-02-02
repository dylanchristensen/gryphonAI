"""
Reusable UI components for Gryphon AI extension.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QProgressBar, QLineEdit, QSplitter
)
from PySide6.QtCore import Qt, Signal


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


class AIChatDialog(QDialog):
    """
    Interactive AI chat window for asking questions about traces and models.
    """
    # Signal emitted when user wants to analyze or refine
    signal_analyze_requested = Signal()
    signal_refine_requested = Signal()
    
    def __init__(self, parent=None, ai_manager=None):
        """
        Initialize the AI chat dialog.
        
        Args:
            parent: Parent widget
            ai_manager: Reference to GryphonAIManager for AI operations
        """
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.setWindowTitle("AI Assistant - Gryphon")
        self.resize(800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Chat history (read-only)
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.chat_history.setPlaceholderText(
            "Ask me about your traces, models, or emergent behaviors...\n\n"
            "Examples:\n"
            "- 'Analyze the last trace for emergent behavior'\n"
            "- 'What patterns do you see in the traces?'\n"
            "- 'Suggest improvements to the current model'\n"
            "- 'Compare this trace to the previous one'"
        )
        layout.addWidget(self.chat_history, stretch=1)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your question here... (Press Enter to send)")
        self.input_field.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.input_field, stretch=1)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setDefault(True)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Quick action buttons
        button_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("Analyze Last Trace")
        self.analyze_button.clicked.connect(self._quick_analyze)
        button_layout.addWidget(self.analyze_button)
        
        self.refine_button = QPushButton("Refine Model")
        self.refine_button.clicked.connect(self._quick_refine)
        button_layout.addWidget(self.refine_button)
        
        self.open_traces_button = QPushButton("Open Trace Folder")
        self.open_traces_button.clicked.connect(self._open_trace_folder)
        button_layout.addWidget(self.open_traces_button)
        
        button_layout.addStretch()
        
        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self._clear_chat)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Add welcome message
        self._add_message("assistant", "Hello! I'm your AI assistant for Gryphon. I can help you analyze traces, refine models, and identify emergent behaviors. What would you like to know?")
    
    def _add_message(self, role: str, content: str):
        """Add a message to the chat history."""
        if role == "user":
            prefix = "You: "
            color = "#0066cc"
        else:
            prefix = "AI: "
            color = "#666666"
        
        self.chat_history.append(f'<span style="color: {color}; font-weight: bold;">{prefix}</span>')
        self.chat_history.append(content)
        self.chat_history.append("")  # Blank line
        
        # Scroll to bottom
        cursor = self.chat_history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.chat_history.setTextCursor(cursor)
    
    def _send_message(self):
        """Send the current input message."""
        message = self.input_field.text().strip()
        if not message:
            return
        
        self.input_field.clear()
        self._add_message("user", message)
        
        # Process the message
        self._process_message(message)
    
    def _process_message(self, message: str):
        """Process user message and generate response."""
        message_lower = message.lower()
        
        # Check for quick commands
        if "analyze" in message_lower and ("trace" in message_lower or "last" in message_lower):
            self._add_message("assistant", "Analyzing the last trace for emergent behavior...")
            if self.ai_manager:
                self.ai_manager.analyze_trace()
            return
        
        if "refine" in message_lower or "improve" in message_lower:
            self._add_message("assistant", "Refining the model with AI suggestions...")
            if self.ai_manager:
                self.ai_manager.refine_model()
            return
        
        # For other messages, show a helpful response
        self._add_message("assistant", 
            "I can help you with:\n"
            "- Analyzing traces for emergent behavior\n"
            "- Refining your MP models\n"
            "- Understanding trace patterns\n\n"
            "Try using the quick action buttons, or ask me to 'analyze the last trace' or 'refine the model'.")
    
    def _quick_analyze(self):
        """Quick action: Analyze last trace."""
        self._add_message("user", "Analyze the last trace")
        self._process_message("analyze last trace")
    
    def _quick_refine(self):
        """Quick action: Refine model."""
        self._add_message("user", "Refine the model")
        self._process_message("refine model")
    
    def _open_trace_folder(self):
        """Open the trace history folder in file explorer."""
        import subprocess
        import platform
        from pathlib import Path
        
        if self.ai_manager:
            trace_dir = self.ai_manager.trace_history_dir
            if trace_dir.exists():
                if platform.system() == "Windows":
                    subprocess.Popen(f'explorer "{trace_dir}"')
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", str(trace_dir)])
                else:  # Linux
                    subprocess.Popen(["xdg-open", str(trace_dir)])
                self._add_message("assistant", f"Opened trace folder: {trace_dir}")
            else:
                self._add_message("assistant", "Trace folder doesn't exist yet. Run some models first!")
        else:
            self._add_message("assistant", "AI manager not available.")
    
    def _clear_chat(self):
        """Clear the chat history."""
        self.chat_history.clear()
        self._add_message("assistant", "Chat cleared. How can I help you?")
    
    def show_result(self, title: str, content: str):
        """Display an AI result in the chat."""
        self._add_message("assistant", f"{title}:\n\n{content}")
