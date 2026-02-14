from __future__ import annotations

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_seed_from_text_llm_findings_respects_already_scrubbed(api_client: AsyncClient, monkeypatch) -> None:
    monkeypatch.setenv("REPORTER_SEED_STRATEGY", "llm_findings")

    # If server-side scrubbing runs despite already_scrubbed=true, fail loudly.
    from app.phi.adapters.scrubber_stub import StubScrubber

    def _should_not_scrub(*_args, **_kwargs):  # noqa: ANN001
        raise AssertionError("PHI scrubber should not run when already_scrubbed=true")

    monkeypatch.setattr(StubScrubber, "scrub", _should_not_scrub, raising=True)

    # Stub the LLM seed path so the route doesn't attempt network calls.
    from app.registry.schema import RegistryRecord
    from app.reporting.llm_findings import LLMFindingsSeedResult

    fake_record = RegistryRecord.model_validate({"procedures_performed": {"bal": {"performed": True}}})

    def _fake_seed(note_text: str) -> LLMFindingsSeedResult:
        return LLMFindingsSeedResult(
            record=fake_record,
            masked_prompt_text=note_text,
            cpt_codes=["31624"],
            warnings=["LLM_FINDINGS_DROPPED: missing_evidence_quote index=0 key='bal'"],
            needs_review=False,
            context=None,
            accepted_items=[],
            accepted_findings=1,
            dropped_findings=1,
        )

    monkeypatch.setattr("app.reporting.llm_findings.seed_registry_record_from_llm_findings", _fake_seed)

    response = await api_client.post(
        "/report/seed_from_text",
        json={
            "text": "Patient underwent BAL performed in RUL.",
            "already_scrubbed": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload.get("bundle")
    assert payload.get("markdown")

    warnings = payload.get("warnings") or []
    assert any(str(w).startswith("LLM_FINDINGS_DROPPED:") for w in warnings)
