
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src/python to path
sys.path.append("c:/2026/Spring/MP+AI/src/python")

from llm_interface import LLMInterface

class MockSettingsManager:
    def __init__(self):
        self.settings = {
            "llm_api_key": "test_key",
            "llm_model": "gpt-3.5-turbo"
        }
    
    def get_setting(self, key):
        return self.settings.get(key)

class TestLLMInterface(unittest.TestCase):
    def setUp(self):
        self.settings_manager = MockSettingsManager()
        self.llm_interface = LLMInterface(self.settings_manager)

    @patch('urllib.request.urlopen')
    def test_refine_model(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"choices": [{"message": {"content": "Suggested Code"}}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.llm_interface.refine_model("ROOT A: a;")
        self.assertEqual(result["content"], "Suggested Code")

    @patch('urllib.request.urlopen')
    def test_analyze_emergent_behavior(self, mock_urlopen):
         # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"choices": [{"message": {"content": "Analysis Result"}}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.llm_interface.analyze_emergent_behavior({"trace": []})
        self.assertEqual(result["content"], "Analysis Result")

    @patch('urllib.request.urlopen')
    def test_fetch_models(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"data": [{"id": "model-1"}, {"id": "model-2"}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        models = self.llm_interface.fetch_models()
        self.assertEqual(models, ["model-1", "model-2"])

    def test_missing_api_key(self):
        self.settings_manager.settings["llm_api_key"] = None
        result = self.llm_interface.refine_model("code")
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main()
