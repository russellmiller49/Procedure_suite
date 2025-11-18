"""Tests for the Reporter Engine and Gemini integration."""

import os
import unittest.mock
import pytest
from modules.reporter.engine import ReportEngine, GeminiLLM, DeterministicStubLLM

def test_engine_defaults_to_stub():
    """Ensure engine defaults to stub when no API key is present."""
    with unittest.mock.patch.dict(os.environ, {}, clear=True):
        engine = ReportEngine()
        assert isinstance(engine.llm, DeterministicStubLLM)
        # Verify it still works
        report = engine.from_free_text("Some note")
        assert report.indication == "Peripheral nodule"  # Default stub payload

def test_engine_uses_gemini_if_env_set():
    """Ensure engine uses GeminiLLM if env var is set."""
    with unittest.mock.patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}, clear=True):
        engine = ReportEngine()
        assert isinstance(engine.llm, GeminiLLM)
        assert engine.llm.api_key == "fake_key"
        assert not engine.llm.use_oauth

def test_gemini_llm_call_mock():
    """Test GeminiLLM generates a request correctly."""
    llm = GeminiLLM(api_key="test_key", model="gemini-test")
    
    # Mock httpx.Client
    with unittest.mock.patch("httpx.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value.__enter__.return_value
        mock_client.post.return_value.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": '{"indication": "Test Indication"}'}]
                }
            }]
        }
        
        response = llm.generate("Test Prompt")
        assert response == '{"indication": "Test Indication"}'
        
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args
        assert "gemini-test:generateContent" in args[0]
        assert kwargs["json"]["contents"][0]["parts"][0]["text"] == "Test Prompt"

def test_engine_fallback_on_invalid_json():
    """Test that the engine handles invalid JSON from LLM gracefully."""
    mock_llm = unittest.mock.Mock()
    mock_llm.generate.return_value = "Not JSON"
    
    engine = ReportEngine(llm=mock_llm)
    report = engine.from_free_text("Some note")
    
    # Should fall back to default/unknowns
    assert report.indication == "Unknown"
