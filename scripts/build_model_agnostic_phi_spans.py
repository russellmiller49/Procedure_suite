#!/usr/bin/env python3
"""Build model-agnostic PHI character spans using the hybrid redactor."""

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

try:
    from modules.phi.adapters.phi_redactor_hybrid import (
        ANATOMICAL_TERMS,
        CLINICAL_ALLOW_LIST,
        DEVICE_MANUFACTURERS,
        PROTECTED_DEVICE_NAMES,
        PHIRedactor,
        RedactionConfig,
    )
except Exception:  # pragma: no cover - fallback for isolated execution
    ANATOMICAL_TERMS = set()
    CLINICAL_ALLOW_LIST = set()
    DEVICE_MANUFACTURERS = set()
    PROTECTED_DEVICE_NAMES = set()
    PHIRedactor = None  # type: ignore[assignment]
    RedactionConfig = None  # type: ignore[assignment]
from scripts.distill_phi_labels import (
    derive_id_base,
    extract_note_text,
    line_bounds,
    load_records_from_json,
)

DEFAULT_IN_DIR = Path("data/knowledge/golden_extractions")
DEFAULT_OUT_PATH = Path("data/ml_training/phi_platinum_spans.jsonl")

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

LABEL_MAP_STANDARD = {
    "PATIENT_NAME": "PATIENT",
    "PATIENT_NAME_MENTION": "PATIENT",
    "PATIENT_IDENTIFIER": "ID",
    "MEDICAL_RECORD_NUMBER": "ID",
    "MRN": "ID",
    "SSN": "ID",
    "SOCIAL_SECURITY_NUMBER": "ID",
    "DOB": "DATE",
    "DATE_OF_BIRTH": "DATE",
    "DATE": "DATE",
    "AGE_OVER_89": "AGE",
    "AGE": "AGE",
    "FACILITY": "HOSPITAL",
    "FACILITY_NAME": "HOSPITAL",
    "HOSPITAL_NAME": "HOSPITAL",
    "LOCATION": "GEO",
    "ADDRESS": "GEO",
    "ZIPCODE": "GEO",
    "CITY": "GEO",
    "PHONE": "PHONE",
    "PHONE_NUMBER": "PHONE",
    "EMAIL": "CONTACT",
    "EMAIL_ADDRESS": "CONTACT",
    "PHYSICIAN_NAME": "PROVIDER",
    "DOCTOR_NAME": "PROVIDER",
}

logger = logging.getLogger("phi_platinum")

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
PROTECTED_PERSON_VETO_TERMS = {
    term.strip().lower()
    for term in (list(ANATOMICAL_TERMS) + list(DEVICE_MANUFACTURERS) + list(PROTECTED_DEVICE_NAMES))
    if isinstance(term, str) and term.strip()
}

DEVICE_KEYWORDS = ("stent", "valve")

STATION_RE = re.compile(r"^\d{1,2}[LR](?:[is])?$", re.IGNORECASE)
SEGMENT_RE = re.compile(r"^[LR][Bb]\d{1,2}$", re.IGNORECASE)


def _map_label(entity_type: str, schema: str) -> str:
    if schema != "standard":
        return entity_type
    mapped = LABEL_MAP_STANDARD.get(entity_type)
    if mapped is not None:
        return mapped
    mapped = LABEL_MAP_STANDARD.get(entity_type.upper())
    if mapped is not None:
        return mapped
    return entity_type


def _line_text(text: str, idx: int) -> str:
    start, end = line_bounds(text, idx)
    return text[start:end]


def _is_station_adjacent_digits(text: str, start: int, end: int) -> bool:
    span = text[start:end].strip()
    if not span.isdigit():
        return False
    next_idx = end
    if next_idx >= len(text):
        return False
    return text[next_idx].upper() in {"R", "L"}


def _normalize_span_text(span_text: str) -> str:
    return span_text.lower().strip().strip(".,;:()[]{}")


def _contains_device_keyword(span_text: str) -> bool:
    normalized = _normalize_span_text(span_text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in DEVICE_KEYWORDS)


def _has_station_hint(line_text: str) -> bool:
    if not line_text:
        return False
    return bool(
        re.search(r"\bstation(s)?\b", line_text, re.IGNORECASE)
        or re.search(r"\bstn\b", line_text, re.IGNORECASE)
        or re.search(r"\bnodes?\b", line_text, re.IGNORECASE)
        or re.search(r"\bln\b", line_text, re.IGNORECASE)
        or re.search(r"\blymph\b", line_text, re.IGNORECASE)
        or re.search(r"\bsampled\b", line_text, re.IGNORECASE)
        or re.search(r"\btbna\b", line_text, re.IGNORECASE)
        or re.search(r"\bebus\b", line_text, re.IGNORECASE)
    )


def _is_ln_station(span_text: str, line_text: str) -> bool:
    stripped = span_text.strip()
    if not stripped:
        return False
    if STATION_RE.fullmatch(stripped):
        return True
    if stripped == "7" and _has_station_hint(line_text):
        return True
    return False


def _is_segment(span_text: str) -> bool:
    return bool(SEGMENT_RE.fullmatch(span_text.strip()))


def _looks_like_lobe_phrase(span_text: str) -> bool:
    lowered = span_text.lower()
    return " lobe" in lowered or lowered.endswith(" lobe")


def is_protected_for_geo(span_text: str, line_text: str) -> bool:
    normalized = _normalize_span_text(span_text)
    if not normalized:
        return False
    if normalized in PROTECTED_WORDS:
        return True
    if _looks_like_lobe_phrase(normalized):
        return True
    if _is_ln_station(span_text, line_text):
        return True
    if _is_segment(span_text):
        return True
    return False


def is_protected_for_person(span_text: str, line_text: str) -> bool:
    normalized = _normalize_span_text(span_text)
    if not normalized:
        return False
    if normalized in PROTECTED_PERSON_VETO_TERMS:
        return True
    if _looks_like_lobe_phrase(normalized):
        return True
    if _is_ln_station(span_text, line_text):
        return True
    if _is_segment(span_text):
        return True
    return False


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


def _line_has_cpt_keyword(line_text: str) -> bool:
    if re.search(r"\bCPT\b", line_text, re.IGNORECASE):
        return True
    if re.search(r"\bCODE\b", line_text, re.IGNORECASE) and not re.search(
        r"\bZIP\s+CODE\b", line_text, re.IGNORECASE
    ):
        return True
    cues = ("codes submitted", "billing", "code justification", "coding", "rvu")
    low = line_text.lower()
    return any(cue in low for cue in cues)


def looks_like_cpt(span_text: str, line_text: str) -> bool:
    if not span_text or not re.fullmatch(r"\d{5}", span_text.strip()):
        return False
    if re.search(r"\bzip(?:\s+code)?\b", line_text, re.IGNORECASE):
        return False
    return _line_has_cpt_keyword(line_text)


def looks_like_temperature(span_text: str, text: str, start: int, end: int, line_text: str) -> bool:
    if not span_text:
        return False
    stripped = span_text.strip()
    temp_pattern = r"\d{2,3}(?:\.\d+)?\s*(?:[cCfF]|" + re.escape(DEGREE_SYMBOL) + r"[cCfF])"
    if re.fullmatch(temp_pattern, stripped):
        return True
    if re.fullmatch(r"\d+(?:\.\d+)?", stripped):
        tail = text[end : min(len(text), end + 4)]
        if re.match(rf"\s*(?:{DEGREE_SYMBOL}\s*)?[cCfF](?![a-zA-Z])", tail):
            return True
        low_line = line_text.lower()
        if any(token in low_line for token in ("temp", "temperature", "degrees")):
            return True
        if DEGREE_SYMBOL in line_text:
            return True
    return False


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


def filter_detections(
    note_text: str,
    detections: list[dict[str, Any]],
    *,
    label_schema: str,
    provider_policy: str,
    provider_label: str,
    counters: dict[str, int],
) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    for det in detections:
        if not isinstance(det, dict):
            continue
        start = int(det.get("start", 0))
        end = int(det.get("end", 0))
        if start >= end:
            continue
        raw_label = str(det.get("type", ""))
        label = _map_label(raw_label, label_schema)
        span_text = det.get("text") or note_text[start:end]
        line_text = _line_text(note_text, start)

        if provider_policy == "drop" and (
            label == provider_label
            or (_is_name_like_label(raw_label) and _is_provider_context(note_text, start, end))
        ):
            counters["spans_dropped_provider"] += 1
            continue
        if provider_policy == "label" and _is_name_like_label(raw_label) and _is_provider_context(note_text, start, end):
            label = provider_label

        is_geo = label == "GEO"
        is_person = label in {"PATIENT", provider_label}

        if is_geo and looks_like_cpt(span_text, line_text):
            counters["spans_dropped_cpt"] += 1
            continue
        if is_geo and looks_like_temperature(span_text, note_text, start, end, line_text):
            counters["spans_dropped_temperature"] += 1
            continue

        if is_geo:
            if _is_station_adjacent_digits(note_text, start, end):
                counters["spans_dropped_station_adjacent_digits"] += 1
                continue
            if _is_ln_station(span_text, line_text):
                counters["spans_dropped_ln_station"] += 1
                continue
            if _contains_device_keyword(span_text):
                counters["spans_dropped_device_keyword"] += 1
                continue
            if is_protected_for_geo(span_text, line_text):
                counters["spans_dropped_protected_geo"] += 1
                continue
            if not looks_like_real_address(span_text, line_text):
                counters["spans_dropped_unplausible_address"] += 1
                continue

        if is_person:
            if _is_station_adjacent_digits(note_text, start, end):
                counters["spans_dropped_station_adjacent_digits"] += 1
                continue
            if is_protected_for_person(span_text, line_text):
                counters["spans_dropped_protected_person"] += 1
                continue

        spans.append({"start": start, "end": end, "label": label, "text": span_text})
    return spans


def main() -> int:
    parser = argparse.ArgumentParser(description="Build model-agnostic PHI spans from hybrid redactor")
    parser.add_argument("--in-dir", type=Path, default=DEFAULT_IN_DIR)
    parser.add_argument("--glob", type=str, default="*.json")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_PATH)
    parser.add_argument("--limit-notes", type=int, default=None)
    parser.add_argument(
        "--use-gliner",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--gliner-threshold", type=float, default=0.6)
    parser.add_argument("--label-schema", choices=["standard"], default="standard")
    parser.add_argument("--provider-policy", choices=["keep", "drop", "label"], default="drop")
    parser.add_argument("--provider-label", type=str, default="PROVIDER")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    in_dir = args.in_dir
    if not in_dir.exists():
        logger.error("Input directory does not exist: %s", in_dir)
        return 1

    files = sorted(in_dir.glob(args.glob))
    if not files:
        logger.warning("No files matched %s in %s", args.glob, in_dir)
        return 0

    if PHIRedactor is None or RedactionConfig is None:
        logger.error("PHI redactor dependencies are unavailable.")
        return 1

    config = RedactionConfig(
        gliner_threshold=args.gliner_threshold,
        protect_physician_names=True,
    )
    redactor = PHIRedactor(config=config, use_gliner=args.use_gliner)

    counters = {
        "files_scanned": 0,
        "records_seen": 0,
        "records_processed": 0,
        "detections_total": 0,
        "spans_emitted": 0,
        "spans_dropped_provider": 0,
        "spans_dropped_cpt": 0,
        "spans_dropped_temperature": 0,
        "spans_dropped_protected_geo": 0,
        "spans_dropped_protected_person": 0,
        "spans_dropped_ln_station": 0,
        "spans_dropped_device_keyword": 0,
        "spans_dropped_station_adjacent_digits": 0,
        "spans_dropped_unplausible_address": 0,
    }

    from tqdm import tqdm

    progress = tqdm(desc="records")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as out_f:
        stop = False
        for path in files:
            counters["files_scanned"] += 1
            records = load_records_from_json(path)
            for record_index, record in enumerate(records):
                counters["records_seen"] += 1
                progress.update(1)
                if args.limit_notes is not None and counters["records_processed"] >= args.limit_notes:
                    stop = True
                    break
                if not isinstance(record, dict):
                    continue
                try:
                    note_text = extract_note_text(record)
                    if not note_text:
                        continue
                    counters["records_processed"] += 1
                    id_base = derive_id_base(record, path, record_index)

                    _, audit = redactor.scrub(note_text)
                    detections = audit.get("detections", []) if isinstance(audit, dict) else []
                    counters["detections_total"] += len(detections)

                    spans = filter_detections(
                        note_text,
                        detections,
                        label_schema=args.label_schema,
                        provider_policy=args.provider_policy,
                        provider_label=args.provider_label,
                        counters=counters,
                    )
                    counters["spans_emitted"] += len(spans)

                    output = {
                        "id_base": id_base,
                        "source_path": str(path),
                        "record_index": record_index,
                        "text": note_text,
                        "spans": spans,
                        "label_schema": args.label_schema,
                        "origin": "hybrid_redactor_platinum",
                    }
                    out_f.write(json.dumps(output, ensure_ascii=False) + "\n")
                except Exception as exc:
                    logger.warning("Skipping record %s:%s: %s", path, record_index, exc)
                    continue
            if stop:
                break

    progress.close()

    logger.info("Files scanned: %s", counters["files_scanned"])
    logger.info("Records seen: %s", counters["records_seen"])
    logger.info("Records processed: %s", counters["records_processed"])
    logger.info("Detections total: %s", counters["detections_total"])
    logger.info("Spans emitted: %s", counters["spans_emitted"])
    logger.info("Spans dropped (provider): %s", counters["spans_dropped_provider"])
    logger.info("Spans dropped (CPT): %s", counters["spans_dropped_cpt"])
    logger.info("Spans dropped (temperature): %s", counters["spans_dropped_temperature"])
    logger.info("Spans dropped (protected geo): %s", counters["spans_dropped_protected_geo"])
    logger.info("Spans dropped (protected person): %s", counters["spans_dropped_protected_person"])
    logger.info("Spans dropped (LN station): %s", counters["spans_dropped_ln_station"])
    logger.info("Spans dropped (device keyword): %s", counters["spans_dropped_device_keyword"])
    logger.info(
        "Spans dropped (station adjacent digits): %s",
        counters["spans_dropped_station_adjacent_digits"],
    )
    logger.info("Spans dropped (unplausible address): %s", counters["spans_dropped_unplausible_address"])
    logger.info("Output: %s", args.out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
