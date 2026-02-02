"""
Configuration management for Gryphon AI extension.

Handles loading and validation of configuration from config.json and environment variables.
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from gryphon_ai.exceptions import LLMConfigurationError


class ConfigManager:
    """Manages configuration loading and validation for the Gryphon AI extension."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional path to config.json. If not provided, searches
                        in common locations.
        """
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()
        self._validate_config()
    
    def _find_config_file(self) -> Optional[Path]:
        """Find config.json in common locations."""
        if self.config_path:
            path = Path(self.config_path)
            if path.exists():
                return path
            return None
        
        # Search in common locations
        candidates = [
            Path("config.json"),  # Current directory
            Path.home() / ".gryphon_ai" / "config.json",  # User home directory
            Path(__file__).parent.parent / "config.json",  # Project root
        ]
        
        # Also check environment variable
        env_config = os.environ.get("GRYPHON_AI_CONFIG")
        if env_config:
            candidates.insert(0, Path(env_config))
        
        for path in candidates:
            if path.exists():
                return path
        
        return None
    
    def _load_config(self):
        """Load configuration from file and environment variables."""
        config_file = self._find_config_file()
        
        if config_file:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except json.JSONDecodeError as e:
                raise LLMConfigurationError(
                    f"Invalid JSON in config file {config_file}: {e}"
                )
            except Exception as e:
                raise LLMConfigurationError(
                    f"Error reading config file {config_file}: {e}"
                )
        
        # Environment variables override file settings
        if "LLM_API_KEY" in os.environ:
            self._config["llm_api_key"] = os.environ["LLM_API_KEY"]
        if "LLM_MODEL" in os.environ:
            self._config["llm_model"] = os.environ["LLM_MODEL"]
        if "LLM_BASE_URL" in os.environ:
            self._config["llm_base_url"] = os.environ["LLM_BASE_URL"]
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        if not self.get_api_key():
            raise LLMConfigurationError(
                "LLM API key not configured. Set LLM_API_KEY environment variable "
                "or add 'llm_api_key' to config.json"
            )
    
    def get_api_key(self) -> Optional[str]:
        """Get the LLM API key."""
        return self._config.get("llm_api_key")
    
    def get_model(self) -> str:
        """Get the LLM model name, with default fallback."""
        return self._config.get("llm_model") or "google/gemma-2-9b-it:free"
    
    def get_base_url(self) -> str:
        """Get the LLM base URL, with default fallback."""
        base_url = self._config.get("llm_base_url", "").strip()
        if not base_url:
            return "https://openrouter.ai/api/v1"
        # Remove trailing slash if present
        return base_url.rstrip("/")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration setting.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def get_config_path(self) -> Optional[Path]:
        """Get the path to the config file that was loaded."""
        return self._find_config_file()
