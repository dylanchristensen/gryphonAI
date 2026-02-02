"""
Trace analysis abstraction for different analysis types.

Provides a base class and implementations for different trace analysis approaches.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json

from gryphon_ai.exceptions import TraceAnalysisError


class TraceAnalyzer(ABC):
    """Abstract base class for trace analyzers."""
    
    @abstractmethod
    def analyze(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trace data.
        
        Args:
            trace_data: The trace data to analyze
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    @staticmethod
    def select_trace(trace_data: Dict[str, Any], index: Optional[int] = None) -> Dict[str, Any]:
        """
        Select a trace from trace data.
        
        Args:
            trace_data: Full trace data dictionary
            index: Optional index of trace to select (defaults to first trace)
            
        Returns:
            Selected trace data
            
        Raises:
            TraceAnalysisError: If no traces available or index out of range
        """
        if not trace_data or "traces" not in trace_data:
            raise TraceAnalysisError("No trace data provided")
        
        traces = trace_data.get("traces", [])
        if not traces:
            raise TraceAnalysisError("No traces found in trace data")
        
        if index is None:
            index = 0
        
        if index < 0 or index >= len(traces):
            raise TraceAnalysisError(
                f"Trace index {index} out of range (0-{len(traces)-1})"
            )
        
        return traces[index]
    
    @staticmethod
    def prepare_trace_for_analysis(trace: Any, max_size: int = 10000) -> str:
        """
        Prepare trace data for analysis by serializing and truncating if needed.
        
        Args:
            trace: Trace data (any JSON-serializable type)
            max_size: Maximum size in characters before truncation
            
        Returns:
            JSON string representation of trace
        """
        trace_str = json.dumps(trace, indent=2)
        if len(trace_str) > max_size:
            trace_str = trace_str[:max_size] + "\n... (truncated)"
        return trace_str


class ExploratoryTraceAnalyzer(TraceAnalyzer):
    """
    Exploratory trace analyzer for identifying potential emergent behaviors.
    
    This is the current implementation that helps refine the methodology.
    """
    
    def __init__(self, trace_index: Optional[int] = None):
        """
        Initialize the exploratory analyzer.
        
        Args:
            trace_index: Index of trace to analyze (defaults to first trace)
        """
        self.trace_index = trace_index
    
    def analyze(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trace data for exploratory purposes.
        
        Args:
            trace_data: Full trace data dictionary
            
        Returns:
            Dictionary with:
                - 'trace': The selected trace
                - 'trace_index': Index of analyzed trace
                - 'prepared_trace': Serialized trace for LLM
        """
        try:
            selected_trace = self.select_trace(trace_data, self.trace_index)
            prepared_trace = self.prepare_trace_for_analysis(selected_trace)
            
            return {
                'trace': selected_trace,
                'trace_index': self.trace_index or 0,
                'prepared_trace': prepared_trace,
                'analysis_type': 'exploratory'
            }
        except TraceAnalysisError:
            raise
        except Exception as e:
            raise TraceAnalysisError(f"Error preparing trace for analysis: {e}")


class MethodologyTraceAnalyzer(TraceAnalyzer):
    """
    Methodology-based trace analyzer.
    
    Placeholder for when the formal methodology is implemented.
    """
    
    def __init__(self, methodology_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the methodology-based analyzer.
        
        Args:
            methodology_config: Configuration for the methodology (when available)
        """
        self.methodology_config = methodology_config or {}
    
    def analyze(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trace data using formal methodology.
        
        Args:
            trace_data: Full trace data dictionary
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            TraceAnalysisError: If methodology is not yet implemented
        """
        # TODO: Implement when methodology is formalized
        raise TraceAnalysisError(
            "Methodology-based analysis not yet implemented. "
            "Use ExploratoryTraceAnalyzer for now."
        )
