from __future__ import annotations

from pathlib import Path

import pytest


def test_v3_note_281_prompt_is_narrative_first_and_includes_anchors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import modules.registry.extractors.v3_extractor as v3_extractor
    from modules.registry.pipelines.v3_pipeline import run_v3_extraction

    note_text = Path("tests/fixtures/notes/note_281.txt").read_text(encoding="utf-8")

    captured: dict[str, str] = {}

    def _fake_generate_structured_json(  # type: ignore[no-untyped-def]
        *,
        llm,
        system_prompt,
        user_prompt,
        response_model,
        response_json_schema,
    ):
        captured["system_prompt"] = system_prompt
        captured["user_prompt"] = user_prompt

        return {
            "note_id": "note_281",
            "source_filename": "note_281.txt",
            "schema_version": "v3",
            "procedures": [
                {
                    "event_id": "bal_1",
                    "type": "bal",
                    "target": {"lobe": "RML", "segment": "Lateral Segment (RB4)"},
                    "measurements": {"volume_instilled_ml": 40, "volume_returned_ml": 17},
                    "evidence": {
                        "quote": "Bronchial alveolar lavage was performed at Lateral Segment of RML (RB4).  Instilled 40 cc of NS, suction returned with 17 cc of NS."
                    },
                },
                {
                    "event_id": "ebus_11l",
                    "type": "linear_ebus",
                    "target": {"station": "11L"},
                    "findings": "Type 2 elastographic pattern",
                    "evidence": {
                        "quote": "The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions."
                    },
                },
            ],
        }

    monkeypatch.setattr(v3_extractor, "_generate_structured_json", _fake_generate_structured_json)

    v3 = run_v3_extraction(note_text)

    # Prompt contains narrative/support tags and explicitly deprioritizes supporting data.
    system_prompt = captured.get("system_prompt", "")
    assert "<primary_narrative>" in system_prompt
    assert "<supporting_data>" in system_prompt
    assert "prefer evidence quotes from <primary_narrative>" in system_prompt.lower()

    user_prompt = captured.get("user_prompt", "")
    assert "Deterministic anchors" in user_prompt
    assert "\"RML\"" in user_prompt
    assert "RB4" in user_prompt
    assert "\"volume_instilled_ml\": 40" in user_prompt
    assert "\"volume_returned_ml\": 17" in user_prompt

    # SPECIMEN(S) must not appear inside <primary_narrative>.
    primary_end = user_prompt.index("</primary_narrative>")
    assert "SPECIMEN(S):" not in user_prompt[:primary_end]
    assert "SPECIMEN(S):" in user_prompt[primary_end:]

    bal = next(e for e in v3.procedures if (e.type or "").lower() == "bal")
    assert (bal.target.lobe or "").upper() == "RML"
    assert "RB4" in (bal.target.segment or "")
    measurements = bal.measurements or {}
    assert measurements.get("volume_instilled_ml") == 40
    assert measurements.get("volume_returned_ml") == 17

    ebus = next(e for e in v3.procedures if (e.type or "").lower() == "linear_ebus" and (e.target.station or "").upper() == "11L")
    assert "Type 2" in str(ebus.findings)
    assert "SPECIMEN" not in ((ebus.evidence.quote if ebus.evidence else "") or "").upper()

