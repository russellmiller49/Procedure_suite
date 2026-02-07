#!/usr/bin/env python3
"""Sanitize platinum PHI spans with protected clinical term vetoes."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.build_model_agnostic_phi_spans import (  # noqa: E402
    _contains_device_keyword,
    _is_ln_station,
    _line_text,
    is_protected_for_geo,
    is_protected_for_person,
    looks_like_cpt,
    looks_like_real_address,
)

DEFAULT_IN_PATH = Path("data/ml_training/phi_platinum_spans.jsonl")
DEFAULT_OUT_PATH = Path("data/ml_training/phi_platinum_spans_CLEANED.jsonl")

GEO_LABELS = {"GEO", "STREET", "CITY", "LOCATION", "ADDRESS", "ZIPCODE", "BUILDINGNUM"}

logger = logging.getLogger("sanitize_platinum_spans")


def init_counters() -> dict[str, int]:
    return {
        "records_processed": 0,
        "records_changed": 0,
        "spans_seen": 0,
        "spans_kept": 0,
        "spans_dropped_protected_geo": 0,
        "spans_dropped_protected_person": 0,
        "spans_dropped_unplausible_address": 0,
        "spans_dropped_ln_station": 0,
        "spans_dropped_device_keyword": 0,
        "spans_dropped_cpt": 0,
    }


def should_drop_span(span: dict[str, Any], note_text: str, counters: dict[str, int]) -> bool:
    label = str(span.get("label", "")).upper()
    start = int(span.get("start", 0))
    end = int(span.get("end", 0))
    if start >= end:
        return True
    span_text = span.get("text")
    if not isinstance(span_text, str):
        span_text = note_text[start:end]
    line_text = _line_text(note_text, start)

    if label in GEO_LABELS:
        if looks_like_cpt(span_text, line_text) and not looks_like_real_address(span_text, line_text):
            counters["spans_dropped_cpt"] += 1
            return True
        if _is_ln_station(span_text, line_text):
            counters["spans_dropped_ln_station"] += 1
            return True
        if _contains_device_keyword(span_text):
            counters["spans_dropped_device_keyword"] += 1
            return True
        if is_protected_for_geo(span_text, line_text):
            counters["spans_dropped_protected_geo"] += 1
            return True
        if not looks_like_real_address(span_text, line_text):
            counters["spans_dropped_unplausible_address"] += 1
            return True

    if label == "PATIENT":
        if is_protected_for_person(span_text, line_text):
            counters["spans_dropped_protected_person"] += 1
            return True

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize platinum PHI spans")
    parser.add_argument("--in", dest="in_path", type=Path, default=DEFAULT_IN_PATH)
    parser.add_argument("--out", dest="out_path", type=Path, default=DEFAULT_OUT_PATH)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.in_path.exists():
        logger.error("Input file does not exist: %s", args.in_path)
        return 1

    counters = init_counters()
    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    with args.in_path.open("r", encoding="utf-8") as in_f, args.out_path.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                out_f.write(line)
                continue
            if not isinstance(record, dict):
                out_f.write(line)
                continue

            counters["records_processed"] += 1
            note_text = record.get("text") or ""
            spans = record.get("spans") or []
            if not isinstance(spans, list):
                out_f.write(line)
                continue

            new_spans = []
            for span in spans:
                if not isinstance(span, dict):
                    continue
                counters["spans_seen"] += 1
                if should_drop_span(span, note_text, counters):
                    continue
                new_spans.append(span)

            counters["spans_kept"] += len(new_spans)
            if len(new_spans) != len(spans):
                counters["records_changed"] += 1
                record = dict(record)
                record["spans"] = new_spans
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Records processed: %s", counters["records_processed"])
    logger.info("Records changed: %s", counters["records_changed"])
    logger.info("Spans seen: %s", counters["spans_seen"])
    logger.info("Spans kept: %s", counters["spans_kept"])
    logger.info("Spans dropped (protected geo): %s", counters["spans_dropped_protected_geo"])
    logger.info("Spans dropped (protected person): %s", counters["spans_dropped_protected_person"])
    logger.info("Spans dropped (LN station): %s", counters["spans_dropped_ln_station"])
    logger.info("Spans dropped (device keyword): %s", counters["spans_dropped_device_keyword"])
    logger.info("Spans dropped (CPT): %s", counters["spans_dropped_cpt"])
    logger.info("Spans dropped (unplausible address): %s", counters["spans_dropped_unplausible_address"])
    logger.info("Output: %s", args.out_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
