"""
Custom exception classes for Gryphon AI extension.
"""


class GryphonAIError(Exception):
    """Base exception for all Gryphon AI errors."""
    pass


class LLMConfigurationError(GryphonAIError):
    """Raised when there's an error with LLM configuration."""
    pass


class LLMAPIError(GryphonAIError):
    """Raised when there's an error with LLM API calls."""
    pass


class TraceAnalysisError(GryphonAIError):
    """Raised when there's an error analyzing traces."""
    pass
