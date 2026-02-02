"""
Pure LLM API client for HTTP communication.

This module handles only the HTTP communication with LLM APIs,
with no business logic or prompt construction.
"""
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from gryphon_ai.exceptions import LLMAPIError


class LLMClient:
    """Pure HTTP client for LLM API communication."""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            model: Model name to use
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_retries = 3
        self.retry_backoff = 1
    
    def _build_url(self) -> str:
        """Build the full API URL."""
        return f"{self.base_url}/chat/completions"
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for the request."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def _build_request_data(self, messages: list) -> Dict[str, Any]:
        """Build the request payload."""
        return {
            "model": self.model,
            "messages": messages
        }
    
    def _parse_response(self, response_data: bytes) -> str:
        """
        Parse the API response and extract the content.
        
        Args:
            response_data: Raw response bytes
            
        Returns:
            Extracted content string
            
        Raises:
            LLMAPIError: If response parsing fails
        """
        try:
            result = json.loads(response_data.decode('utf-8'))
            if 'choices' not in result or len(result['choices']) == 0:
                raise LLMAPIError("Invalid API response: no choices in response")
            
            content = result['choices'][0]['message'].get('content')
            if content is None:
                raise LLMAPIError("Invalid API response: no content in message")
            
            return content
        except json.JSONDecodeError as e:
            raise LLMAPIError(f"Failed to parse API response as JSON: {e}")
        except KeyError as e:
            raise LLMAPIError(f"Invalid API response structure: missing key {e}")
    
    def _handle_http_error(self, error: urllib.error.HTTPError, attempt: int) -> bool:
        """
        Handle HTTP errors and determine if retry should occur.
        
        Args:
            error: The HTTP error that occurred
            attempt: Current attempt number (0-indexed)
            
        Returns:
            True if should retry, False otherwise
            
        Raises:
            LLMAPIError: If error is not retryable or max retries reached
        """
        if error.code == 429:  # Rate limit
            if attempt < self.max_retries:
                return True
            else:
                raise LLMAPIError(
                    f"Rate limit exceeded (429). Please check your API quota and billing details."
                )
        elif error.code == 401:  # Unauthorized
            raise LLMAPIError(
                f"Authentication failed (401). Please check your API key."
            )
        elif error.code == 404:  # Not found
            raise LLMAPIError(
                f"API endpoint not found (404). Please check your base URL: {self.base_url}"
            )
        else:
            raise LLMAPIError(
                f"HTTP Error {error.code}: {error.reason}"
            )
    
    def call(self, messages: list) -> str:
        """
        Make an API call to the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            Response content string
            
        Raises:
            LLMAPIError: If the API call fails
        """
        url = self._build_url()
        headers = self._build_headers()
        data = self._build_request_data(messages)
        
        backoff = self.retry_backoff
        
        for attempt in range(self.max_retries + 1):
            try:
                req = urllib.request.Request(
                    url,
                    json.dumps(data).encode('utf-8'),
                    headers
                )
                
                with urllib.request.urlopen(req, timeout=60) as response:
                    result = self._parse_response(response.read())
                    return result
                    
            except urllib.error.HTTPError as e:
                should_retry = self._handle_http_error(e, attempt)
                if should_retry:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                # If we get here, _handle_http_error raised an exception
                raise
                
            except urllib.error.URLError as e:
                raise LLMAPIError(
                    f"Network error connecting to {self.base_url}: {e.reason}"
                )
                
            except Exception as e:
                if attempt < self.max_retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise LLMAPIError(f"Unexpected error during API call: {str(e)}")
        
        # Should never reach here, but just in case
        raise LLMAPIError("Max retries exceeded")
