import httpx
import pytest


def test_llm_provider_selects_openai_compat_advisor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai_compat")
    monkeypatch.setenv("OPENAI_OFFLINE", "1")

    from app.coder.application.smart_hybrid_policy import build_hybrid_orchestrator

    orchestrator = build_hybrid_orchestrator(
        ml_predictor=object(),
        rules_engine=object(),
    )

    from app.coder.adapters.llm.openai_compat_advisor import OpenAICompatAdvisorAdapter

    assert isinstance(orchestrator._llm, OpenAICompatAdvisorAdapter)


def test_openai_offline_guard_avoids_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_if_called(*_args, **_kwargs):
        raise AssertionError("Network call attempted in OPENAI_OFFLINE mode")

    monkeypatch.setattr(httpx.Client, "post", _raise_if_called)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_OFFLINE", "1")

    from app.coder.adapters.llm.openai_compat_advisor import OpenAICompatAdvisorAdapter

    advisor = OpenAICompatAdvisorAdapter(allowed_codes=["31652", "31653"])
    suggestions = advisor.suggest_codes("Synthetic bronchoscopy note text.")

    assert suggestions
    assert suggestions[0].code == "31652"
    assert suggestions[0].rationale == "offline_stub"

