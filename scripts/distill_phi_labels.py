#!/usr/bin/env python3
"""Distill PHI labels from a teacher model into student-tokenized BIO labels."""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_IN_DIR = Path("data/knowledge/golden_extractions")
DEFAULT_OUT_PATH = Path("data/ml_training/distilled_phi_labels.jsonl")
DEFAULT_TEACHER_MODEL = Path("data/models/hf/piiranha-v1-detect-personal-information")
DEFAULT_STUDENT_TOKENIZER = "distilbert-base-uncased"

PROVIDER_PREFIXES = (
    "SURGEON:",
    "ATTENDING:",
    "PROCEDURALIST:",
    "REFERRING",
    "PHYSICIAN:",
    "PROVIDER:",
)
PROVIDER_CREDENTIALS = ("MD", "DO", "PHD", "FCCP", "FACP")
NAME_LABEL_HINTS = (
    "GIVENNAME",
    "SURNAME",
    "USERNAME",
    "FIRSTNAME",
    "LASTNAME",
    "PERSON",
    "NAME",
    "PATIENT",
)
LABEL_MAPPING_STANDARD = {
    "GIVENNAME": "PATIENT",
    "SURNAME": "PATIENT",
    "USERNAME": "PATIENT",
    "STREETNAME": "GEO",
    "BUILDINGNUM": "GEO",
    "ZIPCODE": "GEO",
    "CITY": "GEO",
}
DEGREE_SYMBOL = "\u00b0"
STREET_SUFFIXES = {
    "st",
    "street",
    "rd",
    "road",
    "ave",
    "avenue",
    "blvd",
    "boulevard",
    "dr",
    "drive",
    "ln",
    "lane",
    "ct",
    "court",
    "pl",
    "place",
    "pkwy",
    "parkway",
    "cir",
    "circle",
    "trl",
    "trail",
    "way",
    "hwy",
    "highway",
    "ste",
    "suite",
    "unit",
    "#",
    "apt",
    "apartment",
}
US_STATE_CODES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
}
GEO_CANDIDATES = {"STREETNAME", "CITY", "ZIPCODE", "BUILDINGNUM", "ADDRESS", "LOCATION"}

try:
    from modules.phi.adapters.phi_redactor_hybrid import (
        ANATOMICAL_TERMS,
        DEVICE_MANUFACTURERS,
        PROTECTED_DEVICE_NAMES,
        CLINICAL_ALLOW_LIST,
    )
except Exception:  # pragma: no cover - fallback for isolated execution
    ANATOMICAL_TERMS = set()
    DEVICE_MANUFACTURERS = set()
    PROTECTED_DEVICE_NAMES = set()
    CLINICAL_ALLOW_LIST = set()

PROTECTED_WORDS = {
    term.strip().lower()
    for term in (
        list(ANATOMICAL_TERMS)
        + list(DEVICE_MANUFACTURERS)
        + list(PROTECTED_DEVICE_NAMES)
        + list(CLINICAL_ALLOW_LIST)
    )
    if isinstance(term, str) and term.strip()
}
PROTECTED_GEO_TERMS = PROTECTED_WORDS.copy()
PROTECTED_PERSON_VETO_TERMS = {
    term.strip().lower()
    for term in (
        list(ANATOMICAL_TERMS)
        + list(DEVICE_MANUFACTURERS)
        + list(PROTECTED_DEVICE_NAMES)
    )
    if isinstance(term, str) and term.strip()
}

logger = logging.getLogger("distill_phi")


def window_text(text: str, window_chars: int, overlap_chars: int) -> list[tuple[int, int, str]]:
    if not text or window_chars <= 0:
        return []
    overlap_chars = max(0, overlap_chars)
    step = max(window_chars - overlap_chars, 1)
    windows: list[tuple[int, int, str]] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + window_chars, text_len)
        windows.append((start, end, text[start:end]))
        if end >= text_len:
            break
        start += step
    return windows


def _span_label(span: dict[str, Any]) -> str:
    for key in ("entity_group", "entity", "label"):
        value = span.get(key)
        if value:
            return str(value)
    return "PHI"


def line_bounds(text: str, idx: int) -> tuple[int, int]:
    if not text:
        return 0, 0
    idx = max(0, min(idx, len(text)))
    line_start = text.rfind("\n", 0, idx)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1
    line_end = text.find("\n", idx)
    if line_end == -1:
        line_end = len(text)
    return line_start, line_end


def normalize_entity_group(entity_group: str, schema: str, provider_label: str) -> str:
    if schema == "piiranha":
        return entity_group
    if entity_group == provider_label:
        return provider_label
    if schema == "standard":
        mapped = LABEL_MAPPING_STANDARD.get(entity_group)
        if mapped is not None:
            return mapped
        mapped = LABEL_MAPPING_STANDARD.get(entity_group.upper())
        if mapped is not None:
            return mapped
        return entity_group
    return entity_group


def _span_text(text: str, start: int, end: int) -> str:
    if not text:
        return ""
    start = max(0, min(start, len(text)))
    end = max(start, min(end, len(text)))
    return text[start:end]


def _line_text(text: str, idx: int) -> str:
    start, end = line_bounds(text, idx)
    return text[start:end]


def _line_has_cpt_keyword(line: str) -> bool:
    if re.search(r"\bCPT\b", line, re.IGNORECASE):
        return True
    if re.search(r"\bCODE\b", line, re.IGNORECASE) and not re.search(r"\bZIP\s+CODE\b", line, re.IGNORECASE):
        return True
    return False


def is_protected_clinical_span(span_text: str) -> bool:
    s = span_text.lower().strip().strip(".,;:()[]{}")
    if not s:
        return False
    if s in PROTECTED_WORDS:
        return True
    if " lobe" in s or s.endswith(" lobe"):
        return True
    if re.fullmatch(r"\d{1,2}[LR](?:[is])?", span_text.strip(), re.IGNORECASE):
        return True
    if span_text.strip() == "7":
        return True
    if re.fullmatch(r"[LRlr][Bb]\d{1,2}", span_text.strip()):
        return True
    return False


def is_protected_for_geo(span_text: str) -> bool:
    s = span_text.lower().strip().strip(".,;:()[]{}")
    if not s:
        return False
    if s in PROTECTED_GEO_TERMS:
        return True
    return is_protected_clinical_span(span_text)


def is_protected_for_person(span_text: str) -> bool:
    s = span_text.lower().strip().strip(".,;:()[]{}")
    if not s:
        return False
    if s in PROTECTED_PERSON_VETO_TERMS:
        return True
    if re.fullmatch(r"\d{1,2}[LR](?:[is])?", span_text.strip(), re.IGNORECASE):
        return True
    if span_text.strip() == "7":
        return True
    if re.fullmatch(r"[LRlr][Bb]\d{1,2}", span_text.strip()):
        return True
    return False


def _is_station_adjacent_digits(window_text: str, start: int, end: int) -> bool:
    span = window_text[start:end].strip()
    if not span.isdigit():
        return False
    next_idx = end
    if next_idx >= len(window_text):
        return False
    return window_text[next_idx].upper() in {"R", "L"}


def looks_like_real_address(span_text: str, line_text: str) -> bool:
    if not span_text:
        return False
    line = (line_text or "").strip()
    low_line = line.lower()
    if any(f" {suffix}" in low_line for suffix in STREET_SUFFIXES):
        return True
    state_pattern = "|".join(US_STATE_CODES)
    if re.search(rf"\b[A-Za-z .'-]+,\s*(?:{state_pattern})\b", line):
        return True
    if re.search(r"\b\d{5}(?:-\d{4})?\b", line) and re.search(rf"\b(?:{state_pattern})\b", line):
        return True
    if any(header in low_line for header in ("address:", "addr:", "street:", "city:", "zip:", "zipcode:", "state:")):
        return True
    return False


def _is_geo_or_zip_label(tag: str) -> bool:
    if tag == "O":
        return False
    upper = tag.upper()
    return "ZIPCODE" in upper or "GEO" in upper


def wipe_cpt_subword_labels(
    tokens: list[str],
    labels: list[str],
    *,
    cpt_codes_set: set[str] | None = None,
    text: str | None = None,
    offsets: list[tuple[int, int]] | None = None,
    stats: dict[str, int] | None = None,
) -> list[str]:
    if not tokens or not labels or len(tokens) != len(labels):
        return labels
    cpt_codes_set = cpt_codes_set or set()
    updated = list(labels)
    for idx in range(len(tokens) - 1):
        curr = tokens[idx]
        nxt = tokens[idx + 1]
        if not curr.isdigit():
            continue
        if not nxt.startswith("##"):
            continue
        combined = curr + nxt[2:]
        if not re.fullmatch(r"\d{5}", combined):
            continue
        is_cpt = combined in cpt_codes_set
        if not is_cpt and text is not None and offsets is not None and idx < len(offsets):
            line = _line_text(text, offsets[idx][0])
            if _line_has_cpt_keyword(line):
                is_cpt = True
        if not is_cpt:
            continue
        if not (_is_geo_or_zip_label(updated[idx]) or _is_geo_or_zip_label(updated[idx + 1])):
            continue
        if stats is not None:
            stats["cpt_subword_wipes_applied"] += 1
            tokens_wiped = 0
            if updated[idx] != "O":
                tokens_wiped += 1
            if updated[idx + 1] != "O":
                tokens_wiped += 1
            stats["cpt_subword_tokens_wiped"] += tokens_wiped
        updated[idx] = "O"
        updated[idx + 1] = "O"
    return updated


def repair_bio(tags: list[str]) -> list[str]:
    if not tags:
        return tags
    repaired = list(tags)
    prev_label = "O"
    for idx, tag in enumerate(repaired):
        if tag == "O":
            prev_label = "O"
            continue
        if not tag.startswith(("B-", "I-")):
            prev_label = "O"
            continue
        label = tag[2:]
        if tag.startswith("I-") and (prev_label == "O" or prev_label != label):
            repaired[idx] = f"B-{label}"
        prev_label = repaired[idx][2:] if repaired[idx] != "O" else "O"
    return repaired


def wipe_ln_station_labels(
    tokens: list[str],
    labels: list[str],
    *,
    stats: dict[str, int] | None = None,
) -> list[str]:
    if not tokens or not labels or len(tokens) != len(labels):
        return labels
    updated = list(labels)
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "7":
            if "GEO" in updated[i].upper():
                if stats is not None:
                    stats["ln_station_wipes_applied"] += 1
                    stats["ln_station_tokens_wiped"] += 1
                updated[i] = "O"
            i += 1
            continue

        if token.isdigit() and i + 1 < len(tokens):
            next_token = tokens[i + 1].lower()
            if next_token in {"##r", "##l", "##ri", "##rs", "##li", "##ls"}:
                wiped = 0
                if "GEO" in updated[i].upper():
                    updated[i] = "O"
                    wiped += 1
                if "GEO" in updated[i + 1].upper():
                    updated[i + 1] = "O"
                    wiped += 1
                if i + 2 < len(tokens) and tokens[i + 2].lower() in {"##i", "##s"}:
                    if "GEO" in updated[i + 2].upper():
                        updated[i + 2] = "O"
                        wiped += 1
                    i += 3
                else:
                    i += 2
                if wiped and stats is not None:
                    stats["ln_station_wipes_applied"] += 1
                    stats["ln_station_tokens_wiped"] += wiped
                continue
        i += 1
    return updated


def _drop_zipcode_if_cpt_context(
    label: str,
    text: str,
    start: int,
    end: int,
    cpt_codes_set: set[str],
    enabled: bool,
) -> bool:
    if not enabled or label.upper() != "ZIPCODE":
        return False
    span_text = _span_text(text, start, end).strip()
    if not re.fullmatch(r"\d{5}", span_text):
        return False
    if span_text in cpt_codes_set:
        return True
    line = _line_text(text, start)
    return _line_has_cpt_keyword(line)


def _drop_buildingnum_if_temperature(
    label: str,
    text: str,
    start: int,
    end: int,
    enabled: bool,
) -> bool:
    if not enabled or label.upper() != "BUILDINGNUM":
        return False
    span_text = _span_text(text, start, end).strip()
    if re.fullmatch(r"\d{2,3}(?:\.\d+)?\s*[cCfF]", span_text):
        return True
    if re.fullmatch(r"\d+(?:\.\d+)?", span_text):
        tail = text[end : min(len(text), end + 4)]
        if re.match(rf"\s*(?:{DEGREE_SYMBOL}\s*)?[cCfF](?![a-zA-Z])", tail):
            return True
    line = _line_text(text, start)
    line_lower = line.lower()
    if any(token in line_lower for token in ("temp", "temperature", "degrees")):
        return True
    if DEGREE_SYMBOL in line:
        return True
    return False


def refine_teacher_spans(
    window_text: str,
    spans: list[dict[str, Any]],
    *,
    cpt_codes_set: set[str],
    enable_refinery: bool,
    drop_zipcode_if_cpt: bool,
    drop_buildingnum_if_temp: bool,
    provider_policy: str,
    provider_label: str,
    label_schema: str,
    stats: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    _ = provider_policy
    refined: list[dict[str, Any]] = []
    for span in spans:
        label = _span_label(span)
        start = int(span.get("start", 0))
        end = int(span.get("end", 0))
        if enable_refinery:
            if _drop_zipcode_if_cpt_context(label, window_text, start, end, cpt_codes_set, drop_zipcode_if_cpt):
                if stats is not None:
                    stats["spans_dropped_cpt_zipcode"] += 1
                continue
            if _drop_buildingnum_if_temperature(label, window_text, start, end, drop_buildingnum_if_temp):
                if stats is not None:
                    stats["spans_dropped_temp_buildingnum"] += 1
                continue
        if label.upper() in GEO_CANDIDATES:
            span_text = _span_text(window_text, start, end)
            line = _line_text(window_text, start)
            if _is_station_adjacent_digits(window_text, start, end):
                if stats is not None:
                    stats["spans_dropped_station_adjacent_digits"] += 1
                continue
            if is_protected_for_geo(span_text):
                if stats is not None:
                    stats["spans_dropped_protected_geo"] += 1
                continue
            if not looks_like_real_address(span_text, line):
                if stats is not None:
                    stats["spans_dropped_unplausible_address"] += 1
                continue
        if label.upper() in NAME_LABEL_HINTS or "NAME" in label.upper() or "PERSON" in label.upper():
            span_text = _span_text(window_text, start, end)
            if _is_station_adjacent_digits(window_text, start, end):
                if stats is not None:
                    stats["spans_dropped_station_adjacent_digits"] += 1
                continue
            if is_protected_for_person(span_text):
                if stats is not None:
                    stats["spans_dropped_protected_person"] += 1
                continue
        normalized = normalize_entity_group(label, label_schema, provider_label)
        updated = dict(span)
        updated["entity_group"] = normalized
        refined.append(updated)
    return refined


def _is_name_like_label(label: str) -> bool:
    upper = label.upper()
    if upper in NAME_LABEL_HINTS:
        return True
    return "NAME" in upper or "PERSON" in upper


def _is_provider_context(text: str, start: int, end: int) -> bool:
    line_start = text.rfind("\n", 0, start)
    if line_start == -1:
        line_start = 0
    prefix = text[line_start:start]
    prefix_upper = prefix.upper()
    if any(token in prefix_upper for token in PROVIDER_PREFIXES):
        return True
    if re.search(r"\bDR\.?\s*$", prefix.strip(), re.IGNORECASE):
        return True
    tail = text[end : min(len(text), end + 40)]
    if re.search(r"\b(" + "|".join(PROVIDER_CREDENTIALS) + r")\b", tail, re.IGNORECASE):
        return True
    return False


def suppress_provider_spans(
    text: str,
    spans: list[dict[str, Any]],
    policy: str = "drop",
    provider_label: str = "PROVIDER",
) -> tuple[list[dict[str, Any]], int, int]:
    kept: list[dict[str, Any]] = []
    dropped = 0
    labeled = 0
    for span in spans:
        label = _span_label(span)
        if _is_name_like_label(label) and _is_provider_context(text, span["start"], span["end"]):
            if policy == "drop":
                dropped += 1
                continue
            if policy == "label":
                updated = dict(span)
                updated["entity_group"] = provider_label
                kept.append(updated)
                labeled += 1
                continue
        kept.append(span)
    return kept, dropped, labeled


def _best_overlapping_span(
    token_start: int,
    token_end: int,
    spans: list[dict[str, Any]],
) -> dict[str, Any] | None:
    best = None
    best_overlap = 0
    best_score = float("-inf")
    for span in spans:
        overlap = min(token_end, span["end"]) - max(token_start, span["start"])
        if overlap <= 0:
            continue
        score = float(span.get("score", 0.0))
        if overlap > best_overlap or (overlap == best_overlap and score > best_score):
            best = span
            best_overlap = overlap
            best_score = score
    return best


def align_spans_to_bio_labels(
    text: str,
    spans: list[dict[str, Any]],
    offsets: list[tuple[int, int]],
    tokens: list[str],
) -> tuple[list[str], list[str]]:
    filtered_tokens: list[str] = []
    filtered_offsets: list[tuple[int, int]] = []
    for token, (start, end) in zip(tokens, offsets):
        if start == end:
            continue
        filtered_tokens.append(token)
        filtered_offsets.append((start, end))

    tags: list[str] = []
    prev_label: str | None = None
    for (start, end) in filtered_offsets:
        best = _best_overlapping_span(start, end, spans)
        if best is None:
            tags.append("O")
            prev_label = None
            continue
        label = _span_label(best)
        if prev_label != label:
            tags.append(f"B-{label}")
        else:
            tags.append(f"I-{label}")
        prev_label = label

    return filtered_tokens, tags


def coerce_records(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        return [record for record in obj if isinstance(record, dict)]
    if isinstance(obj, dict):
        for key in ("records", "items", "data"):
            items = obj.get(key)
            if isinstance(items, list):
                return [record for record in items if isinstance(record, dict)]
        list_values = [value for value in obj.values() if isinstance(value, list)]
        if len(list_values) == 1:
            return [record for record in list_values[0] if isinstance(record, dict)]
        if any(key in obj for key in ("note_text", "report_text", "text")):
            return [obj]
    return []


def load_records_from_json(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        logger.warning("Skipping %s: JSON decode error: %s", path, exc)
        return []
    except OSError as exc:
        logger.warning("Skipping %s: %s", path, exc)
        return []

    records = coerce_records(data)
    if records:
        return records

    if isinstance(data, dict):
        logger.warning(
            "Skipping %s: unsupported JSON structure; keys=%s",
            path,
            sorted(data.keys()),
        )
    else:
        logger.warning("Skipping %s: unsupported JSON structure", path)
    return records


def extract_note_text(record: dict[str, Any]) -> str:
    for key in ("note_text", "report_text", "text"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _extract_codes_from_value(value: Any) -> set[str]:
    codes: set[str] = set()
    if value is None:
        return codes
    if isinstance(value, (int, float)):
        value = str(int(value))
    if isinstance(value, str):
        for match in re.findall(r"\b\d{5}\b", value):
            codes.add(match)
        return codes
    if isinstance(value, list):
        for item in value:
            codes.update(_extract_codes_from_value(item))
        return codes
    if isinstance(value, dict):
        for item in value.values():
            codes.update(_extract_codes_from_value(item))
        return codes
    return codes


def _extract_codes_from_text_sections(text: str) -> set[str]:
    codes: set[str] = set()
    if not text:
        return codes
    if "\\n" in text:
        text = text.replace("\\r\\n", "\n").replace("\\n", "\n")
    cues = (
        "codes submitted",
        "billing",
        "code justification",
        "coding",
        "rvu",
        "cpt",
    )
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        low = line.lower()
        if not any(cue in low for cue in cues):
            continue
        codes.update(re.findall(r"\b\d{5}\b", line))
        if ":" not in line:
            continue
        for j in range(idx + 1, min(len(lines), idx + 11)):
            next_line = lines[j]
            if not next_line.strip():
                break
            if j != idx + 1 and next_line.strip().endswith(":"):
                break
            codes.update(re.findall(r"\b\d{5}\b", next_line))
    return codes


def extract_procedure_codes(record: dict[str, Any], full_text: str) -> set[str]:
    codes: set[str] = set()
    for key in ("cpt_codes", "billing_codes", "procedure_codes", "codes"):
        if key in record:
            codes.update(_extract_codes_from_value(record.get(key)))
    registry_entry = record.get("registry_entry")
    if isinstance(registry_entry, dict):
        billing = registry_entry.get("billing")
        if billing is not None:
            codes.update(_extract_codes_from_value(billing))
    codes.update(_extract_codes_from_text_sections(full_text))
    return {code.strip() for code in codes if code and code.strip()}


def derive_id_base(record: dict[str, Any], input_path: Path, record_index: int) -> str:
    meta = record.get("synthetic_metadata")
    if isinstance(meta, dict):
        sid_source = meta.get("source_file")
        sid_idx = meta.get("original_index")
        if sid_source and sid_idx is not None:
            return f"{Path(str(sid_source)).name}:{sid_idx}"

    for key in ("procedure_id", "id"):
        value = record.get(key)
        if value:
            return str(value)

    return f"{input_path.name}:{record_index}"


def _resolve_device(device: str) -> int | "torch.device":
    if device == "cpu":
        return -1
    try:
        import torch
    except ImportError:
        return -1
    if device == "cuda":
        return 0 if torch.cuda.is_available() else -1
    if device == "mps":
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        return -1
    return -1


def _load_teacher_pipeline(model_path: Path, device: str):
    from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

    model = AutoModelForTokenClassification.from_pretrained(str(model_path), local_files_only=True)
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
    return pipeline(
        "token-classification",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple",
        device=_resolve_device(device),
    )


def _load_student_tokenizer(name_or_path: str):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(name_or_path)


def _tokenized_tokens(tokenized: Any, tokenizer) -> list[str]:
    if hasattr(tokenized, "tokens"):
        return list(tokenized.tokens())
    input_ids = tokenized.get("input_ids", [])
    if isinstance(input_ids, list) and input_ids:
        return tokenizer.convert_ids_to_tokens(input_ids)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Distill PHI labels from teacher to student tokens")
    parser.add_argument("--in-dir", type=Path, default=DEFAULT_IN_DIR)
    parser.add_argument("--glob", type=str, default="*.json")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_PATH)
    parser.add_argument("--teacher-model", type=Path, default=DEFAULT_TEACHER_MODEL)
    parser.add_argument("--student-tokenizer", type=str, default=DEFAULT_STUDENT_TOKENIZER)
    parser.add_argument("--device", type=str, choices=["cpu", "cuda", "mps"], default="cpu")
    parser.add_argument("--window-chars", type=int, default=2000)
    parser.add_argument("--overlap-chars", type=int, default=200)
    parser.add_argument("--max-student-tokens", type=int, default=512)
    parser.add_argument("--limit-notes", type=int, default=None)
    parser.add_argument("--min-score", type=float, default=None)
    parser.add_argument("--provider-policy", choices=["keep", "drop", "label"], default="drop")
    parser.add_argument("--provider-label", type=str, default="PROVIDER")
    parser.add_argument(
        "--enable-refinery",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--label-schema",
        choices=["piiranha", "standard"],
        default="standard",
    )
    parser.add_argument(
        "--drop-zipcode-if-cpt",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--drop-buildingnum-if-temp",
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    in_dir = args.in_dir
    if not in_dir.exists():
        logger.error("Input directory does not exist: %s", in_dir)
        return 1

    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(in_dir.glob(args.glob))
    if not files:
        logger.warning("No files matched %s in %s", args.glob, in_dir)
        return 0

    logger.info("Loading teacher model from %s", args.teacher_model)
    teacher_pipeline = _load_teacher_pipeline(args.teacher_model, args.device)
    teacher_max_length = getattr(teacher_pipeline.tokenizer, "model_max_length", None)
    if teacher_max_length is None or teacher_max_length > 100000:
        teacher_max_length = args.max_student_tokens
    teacher_pipeline.tokenizer.model_max_length = teacher_max_length
    logger.info("Loading student tokenizer %s", args.student_tokenizer)
    student_tokenizer = _load_student_tokenizer(args.student_tokenizer)

    counters = {
        "files_scanned": 0,
        "records_seen": 0,
        "notes_processed": 0,
        "records_processed": 0,
        "windows_emitted": 0,
        "spans_dropped": 0,
        "spans_total": 0,
        "spans_dropped_provider": 0,
        "spans_dropped_cpt_zipcode": 0,
        "spans_dropped_temp_buildingnum": 0,
        "spans_dropped_protected_geo": 0,
        "spans_dropped_protected_person": 0,
        "spans_dropped_station_adjacent_digits": 0,
        "spans_dropped_unplausible_address": 0,
        "spans_kept": 0,
        "provider_spans_labeled": 0,
        "qc_geo_letter_tokens": 0,
        "cpt_subword_wipes_applied": 0,
        "cpt_subword_tokens_wiped": 0,
        "ln_station_wipes_applied": 0,
        "ln_station_tokens_wiped": 0,
    }

    from tqdm import tqdm

    progress = tqdm(desc="records")

    with out_path.open("w", encoding="utf-8") as out_f:
        stop = False
        for path in files:
            counters["files_scanned"] += 1
            records = load_records_from_json(path)
            for record_index, record in enumerate(records):
                counters["records_seen"] += 1
                progress.update(1)
                if args.limit_notes is not None and counters["notes_processed"] >= args.limit_notes:
                    stop = True
                    break
                if not isinstance(record, dict):
                    continue
                try:
                    note_text = extract_note_text(record)
                    if not note_text:
                        continue

                    counters["notes_processed"] += 1
                    counters["records_processed"] += 1
                    id_base = derive_id_base(record, path, record_index)
                    windows = window_text(note_text, args.window_chars, args.overlap_chars)
                    procedure_codes_set = extract_procedure_codes(record, note_text)

                    for window_start, window_end, window_chunk in windows:
                        try:
                            teacher_spans = teacher_pipeline(window_chunk)
                        except Exception as exc:
                            logger.warning("Teacher failed on %s:%s: %s", path, record_index, exc)
                            continue

                        spans: list[dict[str, Any]] = []
                        for span in teacher_spans or []:
                            try:
                                start = int(span.get("start", 0))
                                end = int(span.get("end", 0))
                            except Exception:
                                continue
                            if start >= end:
                                continue
                            score = float(span.get("score", 0.0))
                            if args.min_score is not None and score < args.min_score:
                                counters["spans_dropped"] += 1
                                continue
                            spans.append(
                                {
                                    "start": start + window_start,
                                    "end": end + window_start,
                                    "entity_group": _span_label(span),
                                    "score": score,
                                    "word": span.get("word", ""),
                                }
                            )

                        local_spans = [
                            {
                                **span,
                                "start": span["start"] - window_start,
                                "end": span["end"] - window_start,
                            }
                            for span in spans
                        ]
                        counters["spans_total"] += len(local_spans)
                        local_spans, dropped, labeled = suppress_provider_spans(
                            window_chunk,
                            local_spans,
                            policy=args.provider_policy,
                            provider_label=args.provider_label,
                        )
                        counters["spans_dropped_provider"] += dropped
                        counters["provider_spans_labeled"] += labeled
                        local_spans = refine_teacher_spans(
                            window_chunk,
                            local_spans,
                            cpt_codes_set=procedure_codes_set,
                            enable_refinery=args.enable_refinery,
                            drop_zipcode_if_cpt=args.drop_zipcode_if_cpt,
                            drop_buildingnum_if_temp=args.drop_buildingnum_if_temp,
                            provider_policy=args.provider_policy,
                            provider_label=args.provider_label,
                            label_schema=args.label_schema,
                            stats=counters,
                        )

                        tokenized = student_tokenizer(
                            window_chunk,
                            return_offsets_mapping=True,
                            truncation=True,
                            max_length=args.max_student_tokens,
                        )
                        offsets = [tuple(pair) for pair in tokenized.get("offset_mapping", [])]
                        tokens = _tokenized_tokens(tokenized, student_tokenizer)
                        if not offsets or not tokens:
                            continue

                        filtered_tokens, ner_tags = align_spans_to_bio_labels(
                            window_chunk,
                            local_spans,
                            offsets,
                            tokens,
                        )
                        if not filtered_tokens:
                            continue
                        filtered_offsets = [
                            (start, end)
                            for (start, end), token in zip(offsets, tokens)
                            if start != end
                        ]
                        ner_tags = wipe_cpt_subword_labels(
                            filtered_tokens,
                            ner_tags,
                            cpt_codes_set=procedure_codes_set,
                            text=window_chunk,
                            offsets=filtered_offsets,
                            stats=counters,
                        )
                        ner_tags = wipe_ln_station_labels(
                            filtered_tokens,
                            ner_tags,
                            stats=counters,
                        )
                        ner_tags = repair_bio(ner_tags)
                        counters["spans_kept"] += len(local_spans)
                        for token, tag in zip(filtered_tokens, ner_tags):
                            if not tag.endswith("GEO"):
                                continue
                            token_lower = token.lower()
                            if re.search(r"[a-z]", token_lower) and re.search(r"\d", token_lower):
                                counters["qc_geo_letter_tokens"] += 1
                            elif token_lower in {"c", "f", "##c", "##f"}:
                                counters["qc_geo_letter_tokens"] += 1

                        output = {
                            "id": f"{id_base}:{window_start}",
                            "id_base": id_base,
                            "source_path": str(path),
                            "record_index": record_index,
                            "window_start": window_start,
                            "window_end": window_end,
                            "text": window_chunk,
                            "tokens": filtered_tokens,
                            "ner_tags": ner_tags,
                            "teacher_model": str(args.teacher_model),
                            "student_tokenizer": args.student_tokenizer,
                            "label_schema": args.label_schema,
                            "origin": "piiranha-distilled",
                        }
                        out_f.write(json.dumps(output, ensure_ascii=False) + "\n")
                        counters["windows_emitted"] += 1
                except Exception as exc:
                    logger.warning("Skipping record %s:%s: %s", path, record_index, exc)
                    continue
            if stop:
                break

    progress.close()

    logger.info("Files scanned: %s", counters["files_scanned"])
    logger.info("Records seen: %s", counters["records_seen"])
    logger.info("Records processed: %s", counters["records_processed"])
    logger.info("Notes processed: %s", counters["notes_processed"])
    logger.info("Windows emitted: %s", counters["windows_emitted"])
    logger.info("Spans dropped (score): %s", counters["spans_dropped"])
    logger.info("Spans total: %s", counters["spans_total"])
    logger.info("Spans dropped (provider): %s", counters["spans_dropped_provider"])
    logger.info("Spans dropped (CPT as ZIPCODE): %s", counters["spans_dropped_cpt_zipcode"])
    logger.info("Spans dropped (temp as BUILDINGNUM): %s", counters["spans_dropped_temp_buildingnum"])
    logger.info("Spans dropped (protected geo): %s", counters["spans_dropped_protected_geo"])
    logger.info("Spans dropped (protected person): %s", counters["spans_dropped_protected_person"])
    logger.info(
        "Spans dropped (station adjacent digits): %s",
        counters["spans_dropped_station_adjacent_digits"],
    )
    logger.info("Spans dropped (unplausible address): %s", counters["spans_dropped_unplausible_address"])
    logger.info("Spans kept: %s", counters["spans_kept"])
    logger.info("CPT subword wipes applied: %s", counters["cpt_subword_wipes_applied"])
    logger.info("CPT subword tokens wiped: %s", counters["cpt_subword_tokens_wiped"])
    logger.info("LN station wipes applied: %s", counters["ln_station_wipes_applied"])
    logger.info("LN station tokens wiped: %s", counters["ln_station_tokens_wiped"])
    logger.info("Provider spans labeled: %s", counters["provider_spans_labeled"])
    logger.info("Label schema: %s", args.label_schema)
    logger.info("Output: %s", out_path)
    if counters["qc_geo_letter_tokens"] > 0:
        logger.warning(
            "QC warning: %s GEO-labeled tokens include letter markers; consider expanding refinery rules.",
            counters["qc_geo_letter_tokens"],
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
