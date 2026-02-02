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
            "Your task is to help the user improve their MP model by making it more "
            "realistic, complete, and robust. Focus on:\n"
            "- Adding realistic states and interactions between components\n"
            "- Ensuring the model captures system-of-systems behavior accurately\n"
            "- Identifying missing events or edge cases\n"
            "- Suggesting improvements to make the model more complete"
        )
        
        user_prompt = f"Here is the current MP code:\n\n{current_code}\n"
        
        if selection:
            user_prompt += f"\nFocus your suggestions on this selected part:\n{selection}\n"
        
        user_prompt += (
            "\nPlease provide specific MP code suggestions to make this model more "
            "realistic and complete. Explain your changes briefly, focusing on how "
            "they improve the model's representation of system behavior."
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
            "Your task is to analyze event traces generated from MP models to identify "
            "potential emergent behaviors, unexpected interactions, or interesting patterns.\n\n"
            "Emergent behavior in system-of-systems contexts refers to behaviors that arise "
            "from the interactions between components that are not explicitly defined in "
            "individual component specifications. Look for:\n"
            "- Unexpected event sequences or patterns\n"
            "- Interactions between components that produce novel behaviors\n"
            "- Potential safety or reliability concerns\n"
            "- Interesting state transitions or event dependencies"
        )
        
        # Serialize trace data, truncating if too large
        trace_str = json.dumps(trace_data, indent=2)
        max_length = 10000
        
        if len(trace_str) > max_length:
            trace_str = trace_str[:max_length] + "\n... (truncated for length)"
        
        user_prompt = (
            f"Here is the trace data (JSON) generated from an MP model:\n\n{trace_str}\n\n"
            "Analyze this trace and identify potential emergent behaviors, unexpected "
            "interactions, or interesting patterns. For each finding:\n"
            "- Describe what you observed\n"
            "- Explain why it might indicate emergent behavior\n"
            "- Provide a reasoned justification\n"
            "- Suggest what this might mean for the system being modeled"
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
