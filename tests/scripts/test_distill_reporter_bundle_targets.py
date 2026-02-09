from __future__ import annotations

from ml.scripts import distill_reporter_bundle_targets as mod


class _DummyBundle:
    def model_dump(self, **_kwargs):  # noqa: ANN003
        return {
            "patient": {"mrn": "123"},
            "encounter": {},
            "procedures": [
                {
                    "proc_type": "other",
                    "schema_id": "other.v1",
                    "data": {"source_text": "secret", "nested": {"source_text": "nested-secret"}},
                }
            ],
            "free_text_hint": "should-drop",
            "source_text": "top-level-secret",
        }


def test_prepare_bundle_target_removes_free_text_hint_and_source_text() -> None:
    payload = mod.prepare_bundle_target(_DummyBundle())
    assert "free_text_hint" not in payload
    assert "source_text" not in payload
    proc = payload["procedures"][0]
    assert "source_text" not in proc["data"]
    assert "source_text" not in proc["data"]["nested"]


def test_completeness_accept_patient_id_exception_only() -> None:
    accepted, exceptions, adjusted = mod._completeness_accept(  # noqa: SLF001
        completeness_score=0.7,
        missing_fields=["patient.patient_id or patient.mrn"],
    )
    assert accepted is True
    assert exceptions == ["patient.patient_id or patient.mrn"]
    assert adjusted >= 0.8

    accepted, exceptions, adjusted = mod._completeness_accept(  # noqa: SLF001
        completeness_score=0.7,
        missing_fields=["patient.patient_id or patient.mrn", "procedure.procedure_date"],
    )
    assert accepted is True
    assert set(exceptions) == {"patient.patient_id or patient.mrn", "procedure.procedure_date"}
    assert adjusted >= 0.8

    accepted, exceptions, adjusted = mod._completeness_accept(  # noqa: SLF001
        completeness_score=0.7,
        missing_fields=["patient.patient_id or patient.mrn", "procedure.procedure_date", "procedure.indication"],
    )
    assert accepted is False
    assert exceptions == []
    assert adjusted == 0.7


def test_compute_token_budget_flags_codec_when_overflow_rate_exceeds_threshold() -> None:
    token_lengths = [100] * 95 + [4000] * 5
    audit = mod._compute_token_budget(token_lengths)  # noqa: SLF001

    assert audit["accepted_rows"] == 100
    assert audit["overflow_rate"] > 0.02
    assert audit["enable_short_key_codec"] is True
