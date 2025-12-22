#!/usr/bin/env python3
"""Post-hoc sanitizer for distilled PHI labels (silver)."""

from __future__ import annotations

import argparse
import json
import logging
import re
import string
import sys
from pathlib import Path
from typing import Iterable

sys.path.append(".")
try:
    from modules.phi.adapters.phi_redactor_hybrid import (
        ANATOMICAL_TERMS,
        DEVICE_MANUFACTURERS,
        PROTECTED_DEVICE_NAMES,
        CLINICAL_ALLOW_LIST,
    )
except Exception:  # pragma: no cover - fallback for isolated execution
    ANATOMICAL_TERMS = {
        "left upper lobe",
        "right upper lobe",
        "lul",
        "rul",
        "rll",
        "lll",
        "4r",
        "10r",
        "11r",
        "7",
    }
    DEVICE_MANUFACTURERS = {"dumon", "olympus", "cook", "boston scientific"}
    PROTECTED_DEVICE_NAMES = {"pleurx", "zephyr", "spiration"}
    CLINICAL_ALLOW_LIST = set()

DEFAULT_IN_PATH = Path("data/ml_training/distilled_phi_labels.jsonl")
DEFAULT_OUT_PATH = Path("data/ml_training/distilled_phi_CLEANED.jsonl")

GEO_LABELS = {"GEO", "STREET", "CITY", "LOCATION", "ADDRESS", "ZIPCODE", "BUILDINGNUM"}
GEO_STREET_LABELS = {"GEO", "STREET"}
DEVICE_KEYWORDS = ("stent", "valve")
CPT_CUES = {"cpt", "code", "codes", "billing", "submitted", "justification", "rvu", "coding", "icd", "procedure"}
ADDRESS_CUES = {"address", "addr", "street", "city", "zip", "zipcode", "state"}
US_STATE_CODES = {
    "al",
    "ak",
    "az",
    "ar",
    "ca",
    "co",
    "ct",
    "de",
    "fl",
    "ga",
    "hi",
    "id",
    "il",
    "in",
    "ia",
    "ks",
    "ky",
    "la",
    "me",
    "md",
    "ma",
    "mi",
    "mn",
    "ms",
    "mo",
    "mt",
    "ne",
    "nv",
    "nh",
    "nj",
    "nm",
    "ny",
    "nc",
    "nd",
    "oh",
    "ok",
    "or",
    "pa",
    "ri",
    "sc",
    "sd",
    "tn",
    "tx",
    "ut",
    "vt",
    "va",
    "wa",
    "wv",
    "wi",
    "wy",
    "dc",
}

LN_STATION_RE = re.compile(r"^\d{1,2}[rl](?:[is])?$", re.IGNORECASE)

logger = logging.getLogger("sanitize_dataset")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    lowered = text.lower().strip()
    lowered = lowered.strip(string.punctuation)
    return re.sub(r"\s+", " ", lowered)


def build_protected_set(terms: set[str]) -> set[str]:
    protected = set()
    for term in terms:
        if not isinstance(term, str):
            continue
        normalized = normalize_text(term)
        if normalized:
            protected.add(normalized)
    return protected


PROTECTED_SET_GEO = build_protected_set(
    set(ANATOMICAL_TERMS)
    | set(DEVICE_MANUFACTURERS)
    | set(PROTECTED_DEVICE_NAMES)
    | set(CLINICAL_ALLOW_LIST)
)
PROTECTED_SET_PERSON = build_protected_set(
    set(ANATOMICAL_TERMS) | set(DEVICE_MANUFACTURERS) | set(PROTECTED_DEVICE_NAMES)
)


def init_stats() -> dict[str, int]:
    return {
        "entities_wiped": 0,
        "wiped_protected_geo": 0,
        "wiped_ln_station": 0,
        "wiped_device_keyword": 0,
        "wiped_protected_person": 0,
        "wiped_cpt_wordpieces": 0,
        "wiped_cpt_tokens": 0,
        "wiped_protected_geo_wordpieces": 0,
        "wiped_protected_person_wordpieces": 0,
        "wiped_ln_station_wordpieces": 0,
    }


def get_entity_label(tag: str) -> str:
    if not tag or tag == "O":
        return "O"
    if "-" in tag:
        return tag.split("-", 1)[1]
    return tag


def get_entity_text(tokens: list[str], tags: list[str], start_index: int) -> tuple[str, int]:
    label = get_entity_label(tags[start_index])
    idx = start_index
    parts: list[str] = []
    while idx < len(tokens):
        tag = tags[idx]
        if idx != start_index:
            if not tag.startswith("I-") or get_entity_label(tag) != label:
                break
        token = tokens[idx]
        if token.startswith("##"):
            parts.append(token[2:])
        else:
            if parts:
                parts.append(" ")
            parts.append(token)
        idx += 1
    return "".join(parts), idx


def iter_wordpiece_spans(tokens: list[str]) -> Iterable[tuple[int, int, str, str]]:
    idx = 0
    while idx < len(tokens):
        start = idx
        parts: list[str] = []
        token = tokens[idx]
        if token.startswith("##"):
            parts.append(token[2:])
        else:
            parts.append(token)
        idx += 1
        while idx < len(tokens) and tokens[idx].startswith("##"):
            parts.append(tokens[idx][2:])
            idx += 1
        combined = "".join(parts)
        yield start, idx, combined.lower(), combined


def _context_window(tokens: list[str], start: int, end: int, window_size: int = 10) -> tuple[list[str], list[str]]:
    left = max(0, start - window_size)
    right = min(len(tokens), end + window_size)
    raw_tokens = [tokens[idx] for idx in range(left, right)]
    normalized = [token.replace("##", "").lower() for token in raw_tokens]
    cue_tokens = [tok.strip(string.punctuation) for tok in normalized if tok.strip(string.punctuation)]
    return normalized, cue_tokens


def _has_cpt_context(tokens: list[str], start: int, end: int) -> bool:
    normalized, cue_tokens = _context_window(tokens, start, end)
    if any(tok in CPT_CUES for tok in cue_tokens):
        return True
    for idx, token in enumerate(normalized[:-1]):
        if token in {"code", "codes", "cpt"} and normalized[idx + 1] in {":", "("}:
            return True
    return False


def _is_address_like(tokens: list[str], start: int, end: int) -> bool:
    _, cue_tokens = _context_window(tokens, start, end)
    if any(tok in ADDRESS_CUES for tok in cue_tokens):
        return True
    if any(tok in US_STATE_CODES for tok in cue_tokens):
        return True
    return False


def _is_entity_start(index: int, tags: list[str]) -> bool:
    tag = tags[index]
    if tag == "O":
        return False
    if tag.startswith("B-"):
        return True
    if tag.startswith("I-"):
        if index == 0:
            return True
        prev_tag = tags[index - 1]
        if prev_tag == "O":
            return True
        return get_entity_label(prev_tag) != get_entity_label(tag)
    return True


def _is_ln_station(entity_lower: str) -> bool:
    compact = entity_lower.replace(" ", "")
    if not compact:
        return False
    if LN_STATION_RE.fullmatch(compact):
        return True
    return compact == "7"


def _has_device_keyword(entity_lower: str) -> bool:
    return any(keyword in entity_lower for keyword in DEVICE_KEYWORDS)


def _wipe_span(tags: list[str], start: int, end: int) -> None:
    for idx in range(start, end):
        tags[idx] = "O"


def _has_geo_tag(span_tags: list[str]) -> bool:
    return any("GEO" in tag for tag in span_tags)


def _has_location_tag(span_tags: list[str]) -> bool:
    return any(
        "GEO" in tag or "STREET" in tag or "CITY" in tag
        for tag in span_tags
    )


def _has_person_tag(span_tags: list[str]) -> bool:
    return any("PATIENT" in tag for tag in span_tags)


def _apply_wordpiece_sanitizer(tokens: list[str], tags: list[str], stats: dict[str, int]) -> list[str]:
    new_tags = list(tags)
    for start, end, combined_lower, combined_raw in iter_wordpiece_spans(tokens):
        span_tags = new_tags[start:end]
        if not span_tags:
            continue
        if all(tag == "O" for tag in span_tags):
            continue

        normalized = normalize_text(combined_raw)
        span_has_geo = _has_geo_tag(span_tags)
        span_has_location = _has_location_tag(span_tags)
        span_has_person = _has_person_tag(span_tags)
        span_has_any = any(tag != "O" for tag in span_tags)

        is_cpt_candidate = bool(re.fullmatch(r"\d{5}", combined_lower))
        if is_cpt_candidate and span_has_geo:
            has_cpt_context = _has_cpt_context(tokens, start, end)
            address_like = _is_address_like(tokens, start, end)
            if has_cpt_context or not address_like:
                _wipe_span(new_tags, start, end)
                stats["wiped_cpt_wordpieces"] += 1
                stats["wiped_cpt_tokens"] += end - start
                continue

        compact = normalized.replace(" ", "")
        if span_has_geo and (LN_STATION_RE.fullmatch(compact) or compact == "7"):
            _wipe_span(new_tags, start, end)
            stats["wiped_ln_station_wordpieces"] += 1
            continue

        if normalized in PROTECTED_SET_PERSON and (span_has_person or span_has_geo or span_has_location or span_has_any):
            _wipe_span(new_tags, start, end)
            stats["wiped_protected_person_wordpieces"] += 1
            continue

        if normalized in PROTECTED_SET_GEO and span_has_location:
            _wipe_span(new_tags, start, end)
            stats["wiped_protected_geo_wordpieces"] += 1

    return new_tags


def repair_bio(tags: list[str]) -> list[str]:
    repaired = list(tags)
    for idx, tag in enumerate(repaired):
        if not tag.startswith("I-"):
            continue
        label = get_entity_label(tag)
        if idx == 0:
            repaired[idx] = f"B-{label}"
            continue
        prev_tag = repaired[idx - 1]
        if prev_tag == "O" or get_entity_label(prev_tag) != label:
            repaired[idx] = f"B-{label}"
    return repaired


def sanitize_record(
    tokens: list[str], tags: list[str], stats: dict[str, int] | None = None
) -> list[str]:
    if stats is None:
        stats = init_stats()
    if len(tokens) != len(tags):
        return list(tags)

    original_tags = list(tags)
    new_tags = _apply_wordpiece_sanitizer(tokens, tags, stats)
    idx = 0
    while idx < len(tokens):
        tag = new_tags[idx]
        if tag == "O":
            idx += 1
            continue
        if not _is_entity_start(idx, new_tags):
            idx += 1
            continue
        label = get_entity_label(tag)
        entity_text, next_idx = get_entity_text(tokens, new_tags, idx)
        entity_lower = normalize_text(entity_text)
        label_upper = label.upper()

        wipe_reason = None
        if label_upper in GEO_STREET_LABELS and _is_ln_station(entity_lower):
            wipe_reason = "wiped_ln_station"
        elif label_upper in GEO_STREET_LABELS and _has_device_keyword(entity_lower):
            wipe_reason = "wiped_device_keyword"
        elif label_upper in GEO_LABELS and entity_lower in PROTECTED_SET_GEO:
            wipe_reason = "wiped_protected_geo"
        elif label_upper == "PATIENT" and entity_lower in PROTECTED_SET_PERSON:
            wipe_reason = "wiped_protected_person"

        if wipe_reason:
            _wipe_span(new_tags, idx, next_idx)
            stats["entities_wiped"] += 1
            stats[wipe_reason] += 1

        idx = next_idx

    repaired = repair_bio(new_tags)
    if repaired != original_tags:
        return repaired
    return original_tags


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize distilled PHI labels (silver)")
    parser.add_argument("--in", dest="in_path", type=Path, default=DEFAULT_IN_PATH)
    parser.add_argument("--out", dest="out_path", type=Path, default=DEFAULT_OUT_PATH)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.in_path.exists():
        logger.error("Input file does not exist: %s", args.in_path)
        return 1

    stats = init_stats()
    lines_processed = 0
    lines_changed = 0

    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    with args.in_path.open("r", encoding="utf-8") as in_f, args.out_path.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            lines_processed += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                out_f.write(line)
                continue
            if not isinstance(record, dict):
                out_f.write(line)
                continue
            tokens = record.get("tokens")
            tags = record.get("ner_tags")
            if not isinstance(tokens, list) or not isinstance(tags, list):
                out_f.write(line)
                continue
            new_tags = sanitize_record(tokens, tags, stats)
            if new_tags != tags:
                lines_changed += 1
                record = dict(record)
                record["ner_tags"] = new_tags
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Lines processed: %s", lines_processed)
    logger.info("Lines changed: %s", lines_changed)
    logger.info("Entities wiped: %s", stats["entities_wiped"])
    logger.info("Wiped CPT wordpieces: %s", stats["wiped_cpt_wordpieces"])
    logger.info("Wiped CPT tokens: %s", stats["wiped_cpt_tokens"])
    logger.info("Wiped protected geo (wordpiece): %s", stats["wiped_protected_geo_wordpieces"])
    logger.info("Wiped protected person (wordpiece): %s", stats["wiped_protected_person_wordpieces"])
    logger.info("Wiped LN station (wordpiece): %s", stats["wiped_ln_station_wordpieces"])
    logger.info("Wiped protected geo: %s", stats["wiped_protected_geo"])
    logger.info("Wiped LN station: %s", stats["wiped_ln_station"])
    logger.info("Wiped device keyword: %s", stats["wiped_device_keyword"])
    logger.info("Wiped protected person: %s", stats["wiped_protected_person"])
    logger.info("Output: %s", args.out_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
