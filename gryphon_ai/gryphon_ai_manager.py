"""
Main orchestrator for Gryphon AI extension.

Coordinates UI, services, and data flow using Qt signals/slots for async operations.
"""
from typing import Optional
from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox

from gryphon_ai.config_manager import ConfigManager
from gryphon_ai.llm_client import LLMClient
from gryphon_ai.llm_service import LLMService
from gryphon_ai.worker_thread import LLMWorkerThread
from gryphon_ai.ui_components import ProgressDialog, ResultDialog
from gryphon_ai.exceptions import (
    LLMConfigurationError,
    LLMAPIError,
    TraceAnalysisError
)

# Try to import mp_logger, but don't fail if not available (for testing)
try:
    from mp_logger import log
    _has_logger = True
except ImportError:
    _has_logger = False
    def log(message):
        print(f"[GryphonAI] {message}")


class GryphonAIManager(QObject):
    """
    Main manager for Gryphon AI extension.
    
    Coordinates between the GUI, LLM services, and trace analysis.
    Uses async worker threads to avoid blocking the UI.
    """
    
    def __init__(self, gui_manager):
        """
        Initialize the Gryphon AI manager.
        
        Args:
            gui_manager: Reference to the main GUI manager
        """
        super().__init__()
        self.gui_manager = gui_manager
        
        # Initialize configuration
        try:
            self.config_manager = ConfigManager()
            log("Gryphon AI: Configuration loaded successfully")
        except LLMConfigurationError as e:
            log(f"Gryphon AI: Configuration error - {e}")
            QMessageBox.warning(
                self.gui_manager.w,
                "Configuration Error",
                f"LLM configuration error: {e}\n\n"
                "Please configure your LLM API key in config.json or set the "
                "LLM_API_KEY environment variable."
            )
            # Create a dummy config manager to prevent crashes
            self.config_manager = None
        
        # Initialize LLM components if config is available
        if self.config_manager:
            try:
                llm_client = LLMClient(
                    api_key=self.config_manager.get_api_key(),
                    base_url=self.config_manager.get_base_url(),
                    model=self.config_manager.get_model()
                )
                self.llm_service = LLMService(llm_client)
                self.worker_thread = None  # Created on demand
                log("Gryphon AI: LLM service initialized")
            except Exception as e:
                log(f"Gryphon AI: Failed to initialize LLM service - {e}")
                self.llm_service = None
        else:
            self.llm_service = None
        
        # Store the last compile result for analysis
        self.last_tg_data = None
        
        # Create menu actions
        self.action_refine_model = QAction("Refine Model with AI", self.gui_manager.w)
        self.action_refine_model.triggered.connect(self.refine_model)
        
        self.action_analyze_trace = QAction("Analyze Trace with AI", self.gui_manager.w)
        self.action_analyze_trace.triggered.connect(self.analyze_trace)
        
        # Progress dialog (created on demand)
        self.progress_dialog = None
    
    def set_trace_data(self, tg_data):
        """
        Called when a new trace is generated.
        
        Args:
            tg_data: Trace generator data dictionary
        """
        self.last_tg_data = tg_data
        log("Gryphon AI: Trace data updated")
    
    def _check_llm_available(self) -> bool:
        """Check if LLM service is available."""
        if not self.config_manager:
            QMessageBox.warning(
                self.gui_manager.w,
                "Configuration Required",
                "LLM configuration is not available. Please configure your API key."
            )
            return False
        if not self.llm_service:
            QMessageBox.warning(
                self.gui_manager.w,
                "Service Unavailable",
                "LLM service is not initialized. Please check your configuration."
            )
            return False
        return True
    
    @Slot()
    def refine_model(self):
        """Handle model refinement request."""
        if not self._check_llm_available():
            return
        
        code = self.gui_manager.mp_code_manager.text()
        if not code.strip():
            QMessageBox.warning(
                self.gui_manager.w,
                "No Code",
                "Please write some MP code first."
            )
            return
        
        # Get selection if available (if editor supports it)
        selection = None
        # TODO: Get selection from code editor if available
        
        log("Gryphon AI: Starting model refinement")
        self._start_refine_operation(code, selection)
    
    @Slot()
    def analyze_trace(self):
        """Handle trace analysis request."""
        if not self._check_llm_available():
            return
        
        if not self.last_tg_data or "traces" not in self.last_tg_data or not self.last_tg_data["traces"]:
            QMessageBox.warning(
                self.gui_manager.w,
                "No Trace",
                "Please generate a trace first (Run the model)."
            )
            return
        
        log("Gryphon AI: Starting trace analysis")
        self._start_analyze_operation()
    
    def _start_refine_operation(self, code: str, selection: Optional[str] = None):
        """Start async model refinement operation."""
        # Cancel any existing operation
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.wait()
        
        # Create progress dialog
        self.progress_dialog = ProgressDialog(
            self.gui_manager.w,
            title="AI Processing",
            message="Refining model with AI..."
        )
        self.progress_dialog.show()
        
        # Create and start worker thread
        self.worker_thread = LLMWorkerThread(self.llm_service)
        self.worker_thread.signal_refine_complete.connect(self._on_refine_complete)
        self.worker_thread.signal_error.connect(self._on_error)
        self.worker_thread.signal_progress.connect(self._on_progress)
        
        self.worker_thread.refine_model(code, selection)
    
    def _start_analyze_operation(self):
        """Start async trace analysis operation."""
        # Cancel any existing operation
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.wait()
        
        # Create progress dialog
        self.progress_dialog = ProgressDialog(
            self.gui_manager.w,
            title="AI Processing",
            message="Analyzing trace with AI..."
        )
        self.progress_dialog.show()
        
        # Create and start worker thread
        self.worker_thread = LLMWorkerThread(self.llm_service)
        self.worker_thread.signal_analyze_complete.connect(self._on_analyze_complete)
        self.worker_thread.signal_error.connect(self._on_error)
        self.worker_thread.signal_progress.connect(self._on_progress)
        
        self.worker_thread.analyze_trace(self.last_tg_data)
    
    def _on_refine_complete(self, result: dict):
        """Handle completion of model refinement."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if "error" in result:
            QMessageBox.critical(
                self.gui_manager.w,
                "LLM Error",
                result["error"]
            )
            log(f"Gryphon AI: Model refinement error - {result['error']}")
        else:
            log("Gryphon AI: Model refinement completed successfully")
            self._show_result("AI Suggestions", result.get("content", ""))
    
    def _on_analyze_complete(self, result: dict):
        """Handle completion of trace analysis."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if "error" in result:
            QMessageBox.critical(
                self.gui_manager.w,
                "LLM Error",
                result["error"]
            )
            log(f"Gryphon AI: Trace analysis error - {result['error']}")
        else:
            log("Gryphon AI: Trace analysis completed successfully")
            self._show_result("Trace Analysis", result.get("content", ""))
    
    def _on_error(self, error_message: str):
        """Handle errors from worker thread."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        QMessageBox.critical(
            self.gui_manager.w,
            "Error",
            error_message
        )
        log(f"Gryphon AI: Error - {error_message}")
    
    def _on_progress(self, message: str):
        """Handle progress updates from worker thread."""
        if self.progress_dialog:
            self.progress_dialog.set_message(message)
        log(f"Gryphon AI: {message}")
    
    def _show_result(self, title: str, content: str):
        """
        Show result dialog with LLM response.
        
        Args:
            title: Dialog title
            content: Content to display
        """
        dialog = ResultDialog(
            self.gui_manager.w,
            title=title,
            content=content
        )
        dialog.exec()
