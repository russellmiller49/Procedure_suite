from __future__ import annotations

import json
from pathlib import Path

from scripts.distill_phi_labels import (
    align_spans_to_bio_labels,
    load_records_from_json,
    suppress_provider_spans,
    window_text,
)


def test_window_text_overlap() -> None:
    text = "ABCDEFGHIJ"
    windows = window_text(text, window_chars=4, overlap_chars=1)
    assert windows == [
        (0, 4, "ABCD"),
        (3, 7, "DEFG"),
        (6, 10, "GHIJ"),
    ]


def test_align_spans_to_bio_labels_partial_overlap() -> None:
    text = "John Smith went home"
    tokens = ["John", "Smith", "went", "home"]
    offsets = [(0, 4), (5, 10), (11, 15), (16, 20)]
    spans = [{"start": 2, "end": 10, "entity_group": "PERSON", "score": 0.9}]

    filtered_tokens, tags = align_spans_to_bio_labels(text, spans, offsets, tokens)

    assert filtered_tokens == tokens
    assert tags == ["B-PERSON", "I-PERSON", "O", "O"]


def test_provider_suppression_drop_and_label() -> None:
    text = "SURGEON: John Smith, MD"
    start = text.index("John")
    end = start + len("John Smith")
    spans = [{"start": start, "end": end, "entity_group": "PERSON", "score": 0.9}]

    kept, dropped, labeled = suppress_provider_spans(text, spans, policy="drop")
    assert kept == []
    assert dropped == 1
    assert labeled == 0

    kept, dropped, labeled = suppress_provider_spans(text, spans, policy="label", provider_label="PROVIDER")
    assert kept[0]["entity_group"] == "PROVIDER"
    assert dropped == 0
    assert labeled == 1


def test_provider_suppression_patient_not_dropped() -> None:
    text = "Patient: John Smith"
    start = text.index("John")
    end = start + len("John Smith")
    spans = [{"start": start, "end": end, "entity_group": "PERSON", "score": 0.9}]

    kept, dropped, labeled = suppress_provider_spans(text, spans, policy="drop")
    assert len(kept) == 1
    assert dropped == 0
    assert labeled == 0


def test_load_records_from_json_list(tmp_path: Path) -> None:
    records = [{"note_text": "alpha"}, {"note_text": "beta"}]
    path = tmp_path / "records.json"
    path.write_text(json.dumps(records), encoding="utf-8")

    loaded = load_records_from_json(path)
    assert len(loaded) == 2
    assert loaded[0]["note_text"] == "alpha"

