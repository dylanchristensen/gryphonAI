"""
Business logic layer for LLM operations.

Orchestrates prompt building and API calls, handling business rules and transformations.
"""
from typing import Dict, Any, Optional

from gryphon_ai.llm_client import LLMClient
from gryphon_ai.prompt_builder import PromptBuilder
from gryphon_ai.exceptions import LLMAPIError


class LLMService:
    """Service layer for LLM operations."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the LLM service.
        
        Args:
            llm_client: Configured LLM client instance
        """
        self.llm_client = llm_client
        self.prompt_builder = PromptBuilder()
    
    def refine_model(
        self,
        current_code: str,
        selection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request model refinement suggestions from the LLM.
        
        Args:
            current_code: The current MP code
            selection: Optional selected portion to focus on
            
        Returns:
            Dictionary with 'content' key containing LLM response, or 'error' key if failed
            
        Raises:
            LLMAPIError: If the API call fails
        """
        try:
            system_prompt, user_prompt = self.prompt_builder.build_model_refinement_prompt(
                current_code, selection
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            content = self.llm_client.call(messages)
            return {"content": content}
            
        except LLMAPIError:
            raise
        except Exception as e:
            raise LLMAPIError(f"Unexpected error during model refinement: {str(e)}")
    
    def analyze_trace(
        self,
        trace_data: Dict[str, Any],
        analysis_type: str = "exploratory"
    ) -> Dict[str, Any]:
        """
        Request trace analysis from the LLM.
        
        Args:
            trace_data: The trace data to analyze
            analysis_type: Type of analysis ('exploratory' or 'methodology')
            
        Returns:
            Dictionary with 'content' key containing LLM response, or 'error' key if failed
            
        Raises:
            LLMAPIError: If the API call fails
        """
        try:
            system_prompt, user_prompt = self.prompt_builder.build_trace_analysis_prompt(
                trace_data, analysis_type
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            content = self.llm_client.call(messages)
            return {"content": content}
            
        except LLMAPIError:
            raise
        except Exception as e:
            raise LLMAPIError(f"Unexpected error during trace analysis: {str(e)}")
