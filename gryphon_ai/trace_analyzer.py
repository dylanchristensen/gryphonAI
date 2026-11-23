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
    def extract_trace_summary(tg_trace: list, trace_index: int) -> Dict[str, Any]:
        """
        Extract compact structured summary from a single trace.
        
        Args:
            tg_trace: Raw trace data [mark, probability, nodes, IN_edges, FOLLOWS_edges, ...]
            trace_index: Index of this trace in the set
            
        Returns:
            Dictionary with structured trace information
        """
        mark = tg_trace[0] if len(tg_trace) > 0 else "U"
        probability = tg_trace[1] if len(tg_trace) > 1 else 0.0
        tg_nodes = tg_trace[2] if len(tg_trace) > 2 else []
        tg_in_edges = tg_trace[3] if len(tg_trace) > 3 else []
        tg_follows_edges = tg_trace[4] if len(tg_trace) > 4 else []
        
        # Extract event sequence (ordered by y position, then x)
        events = []
        for tg_node in tg_nodes:
            events.append({
                "id": tg_node[2],
                "label": tg_node[0],
                "type": tg_node[1]
            })
        
        # Sort events by y (vertical position), then x (horizontal)
        # Store original positions for sorting
        event_positions = {tg_node[2]: (tg_node[4], tg_node[3]) for tg_node in tg_nodes}
        events.sort(key=lambda e: event_positions.get(e["id"], (0, 0)))
        event_sequence = [e["label"] for e in events]
        
        # Extract edges (compact - just relation type and event labels)
        event_map = {e["id"]: e["label"] for e in events}
        
        in_relations = []
        for edge in tg_in_edges:
            from_label = event_map.get(edge[0], f"E{edge[0]}")
            to_label = event_map.get(edge[1], f"E{edge[1]}")
            in_relations.append(f"{from_label}->{to_label}")
        
        follows_relations = []
        for edge in tg_follows_edges:
            from_label = event_map.get(edge[0], f"E{edge[0]}")
            to_label = event_map.get(edge[1], f"E{edge[1]}")
            follows_relations.append(f"{from_label}->{to_label}")
        
        return {
            "i": trace_index,
            "m": mark,
            "p": round(probability, 6),
            "seq": event_sequence,
            "in": in_relations,
            "fol": follows_relations
        }
    
    @staticmethod
    def extract_trace_set_summary(tg_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract compact structured summary from the full trace set.
        
        Args:
            tg_data: Full trace data with 'traces' array
            
        Returns:
            Dictionary with structured information about all traces
        """
        traces = tg_data.get("traces", [])
        
        trace_summaries = []
        all_event_labels = set()
        event_frequencies = {}
        pattern_counts = {}
        
        for i, tg_trace in enumerate(traces):
            summary = TraceAnalyzer.extract_trace_summary(tg_trace, i)
            trace_summaries.append(summary)
            
            # Collect all unique events and frequencies
            for event_label in summary["seq"]:
                all_event_labels.add(event_label)
                event_frequencies[event_label] = event_frequencies.get(event_label, 0) + 1
            
            # Track event sequences as patterns (compact string)
            seq_str = "->".join(summary["seq"])
            pattern_counts[seq_str] = pattern_counts.get(seq_str, 0) + 1
        
        return {
            "n": len(traces),
            "traces": trace_summaries,
            "events": sorted(list(all_event_labels)),
            "freq": event_frequencies,
            "patterns": pattern_counts,
            "unique_p": len(pattern_counts)
        }
    
    @staticmethod
    def format_extracted_for_llm(trace_set_summary: Dict[str, Any], max_size: int = 100000) -> str:
        """
        Format extracted trace summary into compact text for LLM.
        
        Args:
            trace_set_summary: Extracted trace set summary
            max_size: Maximum size in characters
            
        Returns:
            Compact formatted string for LLM
        """
        lines = []
        lines.append(f"TRACE SET: {trace_set_summary['n']} traces, {trace_set_summary['unique_p']} unique patterns")
        lines.append("")
        
        # Event frequencies (compact)
        lines.append("EVENT FREQUENCIES:")
        for event, freq in sorted(trace_set_summary['freq'].items(), key=lambda x: -x[1])[:50]:  # Top 50
            lines.append(f"  {event}:{freq}")
        lines.append("")
        
        # Pattern frequencies (most common)
        lines.append("TOP PATTERNS:")
        for pattern, count in sorted(trace_set_summary['patterns'].items(), key=lambda x: -x[1])[:30]:  # Top 30
            lines.append(f"  [{count}x] {pattern}")
        lines.append("")
        
        # All traces (compact format)
        lines.append("ALL TRACES:")
        for trace in trace_set_summary['traces']:
            # Format: i:0 m:U p:0.029412 seq:EventA→EventB→EventC in:2 fol:3
            line_parts = [f"i:{trace['i']}", f"m:{trace['m']}", f"p:{trace['p']}"]
            line_parts.append(f"seq:{'->'.join(trace['seq'])}")
            if trace['in']:
                line_parts.append(f"in:{','.join(trace['in'])}")
            if trace['fol']:
                line_parts.append(f"fol:{','.join(trace['fol'])}")
            lines.append("  " + " ".join(line_parts))
        
        result = "\n".join(lines)
        
        # Truncate if needed, but try to keep complete traces
        if len(result) > max_size:
            # Find last complete trace
            truncated = result[:max_size]
            last_trace_idx = truncated.rfind("  i:")
            if last_trace_idx > 0:
                result = truncated[:last_trace_idx] + f"\n... ({trace_set_summary['n'] - truncated[:last_trace_idx].count('  i:')} traces truncated)"
            else:
                result = truncated + "\n... (truncated)"
        
        return result
    
    @staticmethod
    def prepare_trace_for_analysis(trace: Any, trace_text: Optional[str] = None, max_size: int = 100000) -> str:
        """
        Prepare trace data for analysis using extracted structured data.
        
        Args:
            trace: Trace data (any JSON-serializable type)
            trace_text: Optional raw text representation (fallback if extraction fails)
            max_size: Maximum size in characters before truncation
            
        Returns:
            Compact formatted string representation of trace set
        """
        # Try to extract structured data if we have the full trace data
        if isinstance(trace, dict) and "traces" in trace:
            try:
                trace_set_summary = TraceAnalyzer.extract_trace_set_summary(trace)
                return TraceAnalyzer.format_extracted_for_llm(trace_set_summary, max_size)
            except Exception:
                # Fallback to raw text if extraction fails
                pass
        
        # Fallback: use raw text if available
        if trace_text:
            trace_str = trace_text
        else:
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
    
    def analyze(self, trace_data: Dict[str, Any], trace_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze trace data for exploratory purposes.
        
        Args:
            trace_data: Full trace data dictionary
            trace_text: Optional raw text representation of trace (fallback)
            
        Returns:
            Dictionary with:
                - 'trace_data': Full trace data
                - 'trace_set_summary': Extracted structured summary
                - 'prepared_trace': Compact formatted trace for LLM
                - 'analysis_type': 'exploratory'
        """
        try:
            # Extract structured summary
            trace_set_summary = TraceAnalyzer.extract_trace_set_summary(trace_data)
            
            # Format for LLM (compact)
            prepared_trace = TraceAnalyzer.format_extracted_for_llm(trace_set_summary)
            
            return {
                'trace_data': trace_data,
                'trace_set_summary': trace_set_summary,
                'prepared_trace': prepared_trace,
                'analysis_type': 'exploratory'
            }
        except TraceAnalysisError:
            raise
        except Exception as e:
            raise TraceAnalysisError(f"Error preparing trace for analysis: {e}")
