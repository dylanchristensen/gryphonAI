"""
Main orchestrator for Gryphon AI extension.

Coordinates UI, services, and data flow using Qt signals/slots for async operations.
"""
from typing import Optional
from pathlib import Path
from datetime import datetime
import json
import shutil
from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox

from gryphon_ai.config_manager import ConfigManager
from gryphon_ai.llm_client import LLMClient
from gryphon_ai.llm_service import LLMService
from gryphon_ai.worker_thread import LLMWorkerThread
from gryphon_ai.ui_components import ProgressDialog, ResultDialog, AIChatDialog
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
        self.last_trace_text = None
        
        # Set up trace history directory
        trace_history_dir = Path.home() / ".gryphon_ai" / "traces"
        trace_history_dir.mkdir(parents=True, exist_ok=True)
        self.trace_history_dir = trace_history_dir
        
        # Create menu actions
        self.action_refine_model = QAction("Refine Model with AI", self.gui_manager.w)
        self.action_refine_model.triggered.connect(self.refine_model)
        
        self.action_analyze_trace = QAction("Analyze Trace with AI", self.gui_manager.w)
        self.action_analyze_trace.triggered.connect(self.analyze_trace)
        
        self.action_ai_chat = QAction("AI Chat...", self.gui_manager.w)
        self.action_ai_chat.triggered.connect(self.open_ai_chat)
        
        self.action_open_traces = QAction("Open Trace Folder", self.gui_manager.w)
        self.action_open_traces.triggered.connect(self.open_trace_folder)
        
        # Progress dialog (created on demand)
        self.progress_dialog = None
        
        # AI chat dialog (persistent)
        self.ai_chat_dialog = None
    
    def set_trace_data(self, tg_data, schema_name=None, mp_code=None, scope=None):
        """
        Called when a new trace is generated.
        
        Saves the trace to history with metadata for later analysis.
        
        Args:
            tg_data: Trace generator data dictionary
            schema_name: Schema name from MP code
            mp_code: The MP code text that generated this trace
            scope: The scope value used
        """
        self.last_tg_data = tg_data
        
        # Try to get metadata from gui_manager if not provided
        if schema_name is None:
            try:
                schema_name = getattr(self.gui_manager, '_proposed_schema_name', None)
            except:
                pass
        if mp_code is None:
            try:
                mp_code = getattr(self.gui_manager, '_proposed_mp_code', None)
            except:
                pass
        if scope is None:
            try:
                scope = getattr(self.gui_manager, '_proposed_scope', None)
            except:
                pass
        
        # Capture and save trace
        try:
            self._save_trace_to_history(tg_data, schema_name, mp_code, scope)
        except Exception as e:
            log(f"Gryphon AI: Warning - could not save trace to history: {e}")
        
        log("Gryphon AI: Trace data updated")
    
    def _save_trace_to_history(self, tg_data, schema_name, mp_code, scope):
        """
        Save trace to history directory with metadata.
        
        Args:
            tg_data: Trace generator data dictionary
            schema_name: Schema name
            mp_code: MP code text
            scope: Scope value
        """
        # Read the raw trace text file
        try:
            from paths_gryphon import TRACE_GENERATED_OUTFILE_TG
            trace_file_path = Path(TRACE_GENERATED_OUTFILE_TG)
            
            if trace_file_path.exists():
                with open(trace_file_path, 'r', encoding='utf-8') as f:
                    trace_text = f.read()
                self.last_trace_text = trace_text
            else:
                # Fallback: serialize JSON to text
                trace_text = json.dumps(tg_data, indent=4, sort_keys=True)
                self.last_trace_text = trace_text
        except Exception as e:
            # Fallback: serialize JSON to text
            trace_text = json.dumps(tg_data, indent=4, sort_keys=True)
            self.last_trace_text = trace_text
        
        # Get number of traces
        num_traces = len(tg_data.get("traces", [])) if tg_data else 0
        
        # Create safe schema name for directory (sanitize)
        if schema_name:
            safe_schema_name = "".join(c for c in schema_name if c.isalnum() or c in ('_', '-'))
            if not safe_schema_name:
                safe_schema_name = "unknown"
        else:
            safe_schema_name = "unknown"
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create directory structure: traces/{schema_name}/{timestamp}/
        trace_dir = self.trace_history_dir / safe_schema_name / timestamp
        trace_dir.mkdir(parents=True, exist_ok=True)
        
        # Save trace file (.tg)
        trace_file = trace_dir / "trace.tg"
        with open(trace_file, 'w', encoding='utf-8') as f:
            f.write(trace_text)
        
        # Save .gry file (converted format with visualization data)
        try:
            from paths_gryphon import TRACE_GENERATED_OUTFILE_GRY
            gry_file_path = Path(TRACE_GENERATED_OUTFILE_GRY)
            
            if gry_file_path.exists():
                with open(gry_file_path, 'r', encoding='utf-8') as f:
                    gry_text = f.read()
                
                gry_file = trace_dir / "trace.gry"
                with open(gry_file, 'w', encoding='utf-8') as f:
                    f.write(gry_text)
            else:
                # Fallback: try to generate .gry from tg_data
                try:
                    from tg_to_gry import tg_to_gry_graphs
                    from settings import settings
                    
                    gry_graphs = tg_to_gry_graphs(tg_data)
                    selected_graph_index = 1 if num_traces > 0 else 0
                    
                    gry_data = {
                        "graphs": gry_graphs,
                        "mp_code_current": mp_code or "",
                        "mp_code_runtime": mp_code or "",
                        "scope": scope,
                        "selected_graph_index": selected_graph_index,
                        "settings": settings
                    }
                    
                    gry_file = trace_dir / "trace.gry"
                    with open(gry_file, 'w', encoding='utf-8') as f:
                        json.dump(gry_data, f, indent=4, sort_keys=True)
                except Exception as e:
                    log(f"Gryphon AI: Could not generate .gry file: {e}")
        except Exception as e:
            log(f"Gryphon AI: Could not save .gry file: {e}")
        
        # Save MP code if available
        if mp_code:
            model_file = trace_dir / "model.mp"
            with open(model_file, 'w', encoding='utf-8') as f:
                f.write(mp_code)
        
        # Save metadata
        metadata = {
            "schema": schema_name or "unknown",
            "scope": scope,
            "timestamp": timestamp,
            "num_traces": num_traces,
            "has_global": "GLOBAL" in tg_data if tg_data else False
        }
        metadata_file = trace_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        log(f"Gryphon AI: Saved trace to {trace_dir}")
        
        # Optionally open trace folder (can be made configurable)
        # Uncomment the next line if you want it to auto-open:
        # self._maybe_open_trace_folder()
    
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
        
        self.worker_thread.analyze_trace(
            self.last_tg_data,
            trace_text=getattr(self, 'last_trace_text', None)
        )
    
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
        # If chat dialog is open, show result there too
        if self.ai_chat_dialog and self.ai_chat_dialog.isVisible():
            self.ai_chat_dialog.show_result(title, content)
        
        # Also show in result dialog
        dialog = ResultDialog(
            self.gui_manager.w,
            title=title,
            content=content
        )
        dialog.exec()
    
    def open_ai_chat(self):
        """Open or show the AI chat dialog."""
        if not self.ai_chat_dialog:
            self.ai_chat_dialog = AIChatDialog(self.gui_manager.w, self)
        self.ai_chat_dialog.show()
        self.ai_chat_dialog.raise_()
        self.ai_chat_dialog.activateWindow()
    
    def open_trace_folder(self):
        """Open the trace history folder in file explorer."""
        import subprocess
        import platform
        
        if self.trace_history_dir.exists():
            if platform.system() == "Windows":
                subprocess.Popen(f'explorer "{self.trace_history_dir}"')
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", str(self.trace_history_dir)])
            else:  # Linux
                subprocess.Popen(["xdg-open", str(self.trace_history_dir)])
            log(f"Gryphon AI: Opened trace folder: {self.trace_history_dir}")
        else:
            QMessageBox.information(
                self.gui_manager.w,
                "No Traces",
                "Trace folder doesn't exist yet. Run some models first to generate traces!"
            )