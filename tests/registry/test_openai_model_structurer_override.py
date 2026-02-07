from __future__ import annotations

import pytest

from app.common.llm import OpenAILLM
from app.registry.extractors.llm_detailed import LLMDetailedExtractor


def test_openai_model_structurer_override_respected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REGISTRY_USE_STUB_LLM", raising=False)
    monkeypatch.delenv("GEMINI_OFFLINE", raising=False)

    monkeypatch.setenv("LLM_PROVIDER", "openai_compat")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "fallback-model")
    monkeypatch.setenv("OPENAI_MODEL_STRUCTURER", "structurer-model")

    extractor = LLMDetailedExtractor()
    assert isinstance(extractor.llm, OpenAILLM)
    assert extractor.llm.model == "structurer-model"

