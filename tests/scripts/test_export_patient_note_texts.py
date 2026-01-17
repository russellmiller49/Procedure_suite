import json
from pathlib import Path


def _write_golden(path: Path, entries: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f)


def test_exports_per_patient_note_id_to_text_sorted_by_syn_num(tmp_path: Path):
    from scripts import export_patient_note_texts as exporter

    input_dir = tmp_path / "golden"
    input_dir.mkdir()
    output_dir = tmp_path / "out"

    _write_golden(
        input_dir / "golden_001.json",
        [
            {"note_text": "A1", "registry_entry": {"patient_mrn": "445892_syn_1"}},
            {"note_text": "A3", "registry_entry": {"patient_mrn": "445892_syn_3"}},
            {"note_text": "B2", "registry_entry": {"patient_mrn": "1034928_syn_2"}},
        ],
    )
    _write_golden(
        input_dir / "golden_002.json",
        [
            {"note_text": "A2", "registry_entry": {"patient_mrn": "445892_syn_2"}},
            {"note_text": "B1", "registry_entry": {"patient_mrn": "1034928_syn_1"}},
        ],
    )

    by_patient, stats = exporter.collect_notes(
        input_dir,
        id_field="registry_entry.patient_mrn",
        text_field="note_text",
        only_synthetic=True,
    )

    assert stats["kept"] == 5
    written = exporter.write_patient_files(by_patient, output_dir)
    assert written == 2

    a = json.loads((output_dir / "445892.json").read_text(encoding="utf-8"))
    assert list(a.keys()) == ["445892_syn_1", "445892_syn_2", "445892_syn_3"]
    assert a["445892_syn_2"] == "A2"

    b = json.loads((output_dir / "1034928.json").read_text(encoding="utf-8"))
    assert list(b.keys()) == ["1034928_syn_1", "1034928_syn_2"]
    assert b["1034928_syn_1"] == "B1"

