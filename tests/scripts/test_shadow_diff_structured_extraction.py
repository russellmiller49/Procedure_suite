import json
from pathlib import Path


def _write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_shadow_diff_structured_extraction_is_phi_safe_and_skips_unavailable_structurer(
    tmp_path: Path, monkeypatch
) -> None:
    from ml.scripts import shadow_diff_structured_extraction as runner

    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")
    monkeypatch.setenv("GEMINI_OFFLINE", "1")
    monkeypatch.setenv("OPENAI_OFFLINE", "1")

    input_dir = tmp_path / "fixtures"
    input_dir.mkdir(parents=True, exist_ok=True)

    note_text = "PATIENT NAME: John Doe\nMRN: 12345\nProcedure: Bronchoscopy with BAL.\n"
    fixture = {
        "schema_version": "vnext_fixture_v1",
        "case_id": "case_1",
        "note_text": note_text,
        "expected_cpt_codes": ["31624"],
        "migrated_evidence": [],
    }
    _write_json(input_dir / "case_1.json", fixture)

    out_path = tmp_path / "report.json"
    rc = runner.main(["--input", str(input_dir), "--output-json", str(out_path)])
    assert rc == 0
    assert out_path.exists()

    raw = out_path.read_text(encoding="utf-8")
    assert "John Doe" not in raw
    assert "note_text" not in raw

    report = json.loads(raw)
    assert report.get("schema_version") == "shadow_diff_structured_extraction_v1"
    summary = report.get("summary") or {}
    assert summary.get("cases_total") == 1
    assert summary.get("cases_skipped_structurer_unavailable") == 1

    cases = report.get("cases") or []
    assert len(cases) == 1
    case = cases[0]
    assert "note_text" not in case
    assert case.get("engine_b", {}).get("structurer_status") in {"not_implemented", "unknown"}

