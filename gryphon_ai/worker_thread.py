"""
Worker thread for asynchronous LLM operations.

Follows the pattern from TraceGeneratorManager and RunnerThread.
"""
from PySide6.QtCore import QThread, Signal, QObject
from typing import Dict, Any, Optional

from gryphon_ai.llm_service import LLMService
from gryphon_ai.trace_analyzer import ExploratoryTraceAnalyzer
from gryphon_ai.exceptions import LLMAPIError, TraceAnalysisError


class LLMWorkerThread(QThread):
    """
    Worker thread for non-blocking LLM operations.
    
    Emits signals for progress, completion, and errors.
    """
    
    # Signals
    signal_refine_complete = Signal(dict)  # Emits result dict
    signal_analyze_complete = Signal(dict)  # Emits result dict
    signal_error = Signal(str)  # Emits error message
    signal_progress = Signal(str)  # Emits progress message
    
    def __init__(self, llm_service: LLMService, parent: Optional[QObject] = None):
        """
        Initialize the worker thread.
        
        Args:
            llm_service: Configured LLM service instance
            parent: Parent QObject
        """
        super().__init__(parent)
        self.llm_service = llm_service
        self.operation = None
        self.operation_args = {}
        self._stop_event = False
    
    def refine_model(self, current_code: str, selection: Optional[str] = None):
        """
        Queue a model refinement operation.
        
        Args:
            current_code: The MP code to refine
            selection: Optional selected portion
        """
        self.operation = "refine"
        self.operation_args = {
            "current_code": current_code,
            "selection": selection
        }
        self.start()
    
    def analyze_trace(self, trace_data: Dict[str, Any], trace_text: Optional[str] = None, trace_index: Optional[int] = None):
        """
        Queue a trace analysis operation.
        
        Args:
            trace_data: The trace data to analyze
            trace_text: Optional raw text representation (preferred for LLM)
            trace_index: Optional index of trace to analyze
        """
        self.operation = "analyze"
        self.operation_args = {
            "trace_data": trace_data,
            "trace_text": trace_text,
            "trace_index": trace_index
        }
        self.start()
    
    def cancel(self):
        """Request cancellation of the current operation."""
        self._stop_event = True
    
    def run(self):
        """Execute the queued operation."""
        self._stop_event = False
        
        try:
            if self.operation == "refine":
                self._run_refine()
            elif self.operation == "analyze":
                self._run_analyze()
            else:
                self.signal_error.emit("No operation specified")
        except LLMAPIError as e:
            self.signal_error.emit(f"LLM API Error: {str(e)}")
        except TraceAnalysisError as e:
            self.signal_error.emit(f"Trace Analysis Error: {str(e)}")
        except Exception as e:
            self.signal_error.emit(f"Unexpected error: {str(e)}")
    
    def _run_refine(self):
        """Execute model refinement operation."""
        if self._stop_event:
            return
        
        self.signal_progress.emit("Building prompt...")
        current_code = self.operation_args["current_code"]
        selection = self.operation_args.get("selection")
        
        if self._stop_event:
            return
        
        self.signal_progress.emit("Calling LLM...")
        result = self.llm_service.refine_model(current_code, selection)
        
        if self._stop_event:
            return
        
        self.signal_refine_complete.emit(result)
    
    def _run_analyze(self):
        """Execute trace analysis operation."""
        if self._stop_event:
            return
        
        self.signal_progress.emit("Preparing trace data...")
        trace_data = self.operation_args["trace_data"]
        trace_text = self.operation_args.get("trace_text")
        trace_index = self.operation_args.get("trace_index")
        
        # Use trace analyzer to prepare the trace
        analyzer = ExploratoryTraceAnalyzer(trace_index=trace_index)
        analysis_data = analyzer.analyze(trace_data, trace_text=trace_text)
        
        if self._stop_event:
            return
        
        self.signal_progress.emit("Calling LLM...")
        result = self.llm_service.analyze_trace(
            trace_data,  # Pass full trace data
            trace_text=trace_text,  # Pass raw text if available
            analysis_type=analysis_data['analysis_type']
        )
        
        if self._stop_event:
            return
        
        self.signal_analyze_complete.emit(result)
