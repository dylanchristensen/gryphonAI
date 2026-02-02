"""
Prompt construction for LLM interactions.

Separates prompt building logic from API calls and business logic.
"""
from typing import Optional
import json


class PromptBuilder:
    """Builds prompts for different LLM operations."""
    
    @staticmethod
    def build_model_refinement_prompt(
        current_code: str,
        selection: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Build prompt for model refinement.
        
        Args:
            current_code: The current MP code
            selection: Optional selected portion of code to focus on
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = (
            "You are an expert in Monterey Phoenix (MP) modeling. "
            "Your task is to help the user refine their MP model to better represent "
            "the system as they understand it. Important principles:\n"
            "- The model should represent the system as understood, not add defensive "
            "programming or edge case handling\n"
            "- Focus on making the model more accurate to the intended system behavior\n"
            "- Suggest realistic states and interactions that better capture the "
            "system-of-systems behavior\n"
            "- Do NOT suggest adding edge cases or error handling - the model should "
            "represent the system as designed, and traces will reveal what actually happens"
        )
        
        user_prompt = f"Here is the current MP code:\n\n{current_code}\n"
        
        if selection:
            user_prompt += f"\nFocus your suggestions on this selected part:\n{selection}\n"
        
        user_prompt += (
            "\nPlease provide specific MP code suggestions to better represent the system "
            "as understood. Focus on making the model more accurate to the intended system "
            "behavior, not on adding edge cases or error handling. Explain your changes "
            "briefly, focusing on how they improve the model's representation of the "
            "system as designed."
        )
        
        return system_prompt, user_prompt
    
    @staticmethod
    def build_trace_analysis_prompt(
        trace_data: dict,
        analysis_type: str = "exploratory"
    ) -> tuple[str, str]:
        """
        Build prompt for trace analysis.
        
        Args:
            trace_data: The trace data to analyze (JSON-serializable)
            analysis_type: Type of analysis ('exploratory' or 'methodology')
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        if analysis_type == "exploratory":
            return PromptBuilder._build_exploratory_analysis_prompt(trace_data)
        elif analysis_type == "methodology":
            return PromptBuilder._build_methodology_analysis_prompt(trace_data)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    @staticmethod
    def _build_exploratory_analysis_prompt(trace_data: dict) -> tuple[str, str]:
        """Build prompt for exploratory trace analysis."""
        system_prompt = (
            "You are an expert in Monterey Phoenix (MP) modeling and trace analysis. "
            "Your task is to analyze the actual event traces generated from running an MP "
            "model to identify potential emergent behaviors.\n\n"
            "Important: You are analyzing what actually happened in the traces, not what "
            "the code says should happen. The model represents the system as understood, "
            "and the traces reveal what actually occurs when the system runs.\n\n"
            "Emergent behavior in system-of-systems contexts refers to behaviors that arise "
            "from the interactions between components that are not explicitly defined in "
            "individual component specifications. Look for:\n"
            "- Event sequences or patterns that emerge from component interactions\n"
            "- Behaviors that arise from the system dynamics, not from explicit code\n"
            "- Interesting state transitions or event dependencies that reveal system "
            "properties\n"
            "- Patterns that might indicate emergent system-level behaviors"
        )
        
        # Get trace text if available (preferred), otherwise serialize JSON
        if isinstance(trace_data, dict) and 'trace_text' in trace_data:
            trace_str = trace_data['trace_text']
        else:
            trace_str = json.dumps(trace_data, indent=2)
        
        max_length = 10000
        if len(trace_str) > max_length:
            trace_str = trace_str[:max_length] + "\n... (truncated for length)"
        
        user_prompt = (
            f"Here is the trace data showing the SET OF EVENT TRACES generated when "
            f"running an MP model. This file contains MULTIPLE traces (the 'traces' array):\n\n{trace_str}\n\n"
            "Analyze the FULL SET OF TRACES to identify potential emergent behaviors. "
            "Look for patterns and behaviors that emerge ACROSS the trace set.\n\n"
            "Focus on:\n"
            "1. **Patterns across traces**: What event sequences or behaviors appear in "
            "multiple traces? Which traces show similar patterns?\n"
            "2. **Variations between traces**: What interesting differences exist between "
            "traces? What causes these variations?\n"
            "3. **System-level properties**: What behaviors emerge from the full set of "
            "traces that aren't visible in individual traces?\n"
            "4. **Component interactions**: How do components interact across different "
            "traces? What interactions produce emergent outcomes?\n\n"
            "For each finding, provide:\n"
            "- Which specific traces show this behavior (trace indices)\n"
            "- The concrete event sequences observed\n"
            "- Why this indicates emergent behavior (arising from interactions, not explicit code)\n"
            "- How this pattern appears across the trace set (frequency, variations)"
        )
        
        return system_prompt, user_prompt
    
    @staticmethod
    def _build_methodology_analysis_prompt(trace_data: dict) -> tuple[str, str]:
        """
        Build prompt for methodology-based trace analysis.
        
        This is a placeholder for when the methodology is formalized.
        """
        # TODO: Implement when methodology is formalized
        system_prompt = (
            "You are an expert in Monterey Phoenix (MP) modeling and trace analysis. "
            "Your task is to analyze event traces using a formal methodology for "
            "identifying emergent behaviors."
        )
        
        trace_str = json.dumps(trace_data, indent=2)
        if len(trace_str) > 10000:
            trace_str = trace_str[:10000] + "\n... (truncated for length)"
        
        user_prompt = (
            f"Here is the trace data:\n\n{trace_str}\n\n"
            "Analyze this trace using the formal methodology for emergent behavior detection."
        )
        
        return system_prompt, user_prompt
