#!/usr/bin/env python3
"""
Apply platinum PHI redactions to golden JSONs for registry ML training.

This script takes platinum PHI spans (character-level) and applies [REDACTED]
replacements to the note_text fields in golden JSON files, producing
PHI-scrubbed training data for the registry ML model.

Usage: python scripts/apply_platinum_redactions.py

Critical Safety Feature:
- Text snippet verification ensures span offsets match actual text before redacting
- Mismatches are logged and skipped to prevent corrupted output
"""

import argparse
import importlib.util
import json
import logging
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PHIRedactor = None
RedactionConfig = None
INLINE_PHYSICIAN_RE = None
PHYSICIAN_CREDENTIAL_RE = None
PHYSICIAN_HEADER_RE = None
SIGNATURE_RE = None


def _load_phi_redactor_hybrid() -> None:
    """Load `modules/phi/adapters/phi_redactor_hybrid.py` without importing `modules.phi` (avoids optional deps)."""
    global PHIRedactor, RedactionConfig
    global INLINE_PHYSICIAN_RE, PHYSICIAN_CREDENTIAL_RE, PHYSICIAN_HEADER_RE, SIGNATURE_RE
    if PHIRedactor is not None and RedactionConfig is not None:
        return

    module_path = ROOT / "modules" / "phi" / "adapters" / "phi_redactor_hybrid.py"
    if not module_path.exists():
        return

    try:
        spec = importlib.util.spec_from_file_location("_phi_redactor_hybrid", module_path)
        if spec is None or spec.loader is None:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:  # pragma: no cover
        return

    PHIRedactor = getattr(mod, "PHIRedactor", None)
    RedactionConfig = getattr(mod, "RedactionConfig", None)
    INLINE_PHYSICIAN_RE = getattr(mod, "INLINE_PHYSICIAN_RE", None)
    PHYSICIAN_CREDENTIAL_RE = getattr(mod, "PHYSICIAN_CREDENTIAL_RE", None)
    PHYSICIAN_HEADER_RE = getattr(mod, "PHYSICIAN_HEADER_RE", None)
    SIGNATURE_RE = getattr(mod, "SIGNATURE_RE", None)


STANDARD_REDACTION_TOKEN = "[REDACTED]"

# Matches angle-bracket placeholders like <PERSON>, <DATE_TIME>, <MRN>, <LOCATION>, etc.
ANGLE_TOKEN_RE = re.compile(r"<[A-Z][A-Z0-9_]*>")
# Matches bracketed placeholders like [Name] or [Patient Name]
BRACKET_NAME_TOKEN_RE = re.compile(r"\[(?:patient\s+)?name\]", re.IGNORECASE)
# Matches type-specific placeholders from PHIRedactor (e.g., [REDACTED_DATE])
TYPED_REDACTION_RE = re.compile(r"\[REDACTED_[A-Z0-9_]+\]")
# Matches honorific + last name (patient narrative mentions)
HONORIFIC_NAME_RE = re.compile(
    r"(?i)\b(?P<title>mr|mrs|ms|miss)\.?\s+(?P<name>[A-Z][a-z]+(?:[-'][A-Za-z]+)?(?:\s+[A-Z][a-z]+){0,2})"
)
PROVIDER_SUFFIX_RE = re.compile(r"(?i)\s*,?\s*(?:MD|DO|RN|PA|NP|CRNA|FNP|FCCP|FACP|PHD)\b")
INLINE_LOCATION_LABEL_RE = re.compile(
    r"(?i)\b(?P<label>location|facility|hospital|institution|site|center)"
    r"(?P<sep>\s*[:\-]\s*)"
    r"(?P<value>[^\n\r|]+)"
)
CITY_STATE_RE = re.compile(r"\b[A-Z][a-z]+,\s*[A-Z]{2}\b")
ZIP_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")
FACILITY_KEYWORDS = (
    "medical",
    "hospital",
    "center",
    "clinic",
    "regional",
    "university",
    "health",
    "memorial",
    "institute",
    "campus",
    "va",
    "st.",
    "saint",
)


def standardize_redaction_tokens(text: str) -> str:
    """Normalize all PHI placeholders to the single token [REDACTED]."""
    if not text:
        return text
    text = TYPED_REDACTION_RE.sub(STANDARD_REDACTION_TOKEN, text)
    text = BRACKET_NAME_TOKEN_RE.sub(STANDARD_REDACTION_TOKEN, text)
    text = ANGLE_TOKEN_RE.sub(STANDARD_REDACTION_TOKEN, text)
    return text


def redact_honorific_names(text: str) -> str:
    if not text:
        return text

    def _replace(match: re.Match) -> str:
        tail = text[match.end() : match.end() + 24]
        if PROVIDER_SUFFIX_RE.search(tail):
            return match.group(0)
        return STANDARD_REDACTION_TOKEN

    return HONORIFIC_NAME_RE.sub(_replace, text)


def redact_inline_locations(text: str) -> str:
    if not text:
        return text

    def _replace(match: re.Match) -> str:
        label = match.group("label")
        sep = match.group("sep") or ": "
        value = (match.group("value") or "").strip()
        value_lower = value.lower()
        should_redact = (
            STANDARD_REDACTION_TOKEN in value
            or CITY_STATE_RE.search(value) is not None
            or ZIP_RE.search(value) is not None
            or any(keyword in value_lower for keyword in FACILITY_KEYWORDS)
        )
        if not should_redact:
            return match.group(0)
        return f"{label}{sep}{STANDARD_REDACTION_TOKEN}"

    return INLINE_LOCATION_LABEL_RE.sub(_replace, text)


def post_process_redactions(text: str) -> str:
    if not text:
        return text
    text = standardize_redaction_tokens(text)
    text = redact_honorific_names(text)
    text = redact_inline_locations(text)
    return standardize_redaction_tokens(text)


def _merge_spans(spans: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not spans:
        return []
    spans = sorted(spans)
    merged: List[List[int]] = []
    for start, end in spans:
        if start >= end:
            continue
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(s, e) for s, e in merged]


def find_physician_name_spans(text: str) -> List[Tuple[int, int]]:
    """Return (start, end) spans of physician/provider names to protect from redaction."""
    spans: List[Tuple[int, int]] = []
    if not text:
        return spans

    _load_phi_redactor_hybrid()

    regexes = []
    if PHYSICIAN_HEADER_RE is not None:
        regexes.append((PHYSICIAN_HEADER_RE, 1))
    if INLINE_PHYSICIAN_RE is not None:
        regexes.append((INLINE_PHYSICIAN_RE, 1))
    if SIGNATURE_RE is not None:
        regexes.append((SIGNATURE_RE, 1))
    if PHYSICIAN_CREDENTIAL_RE is not None:
        regexes.append((PHYSICIAN_CREDENTIAL_RE, 1))

    # Fallback: protect obvious "Dr. Lastname" patterns
    if not regexes:
        fallback = re.compile(r"(?i)\b(?:dr\.|doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})")
        regexes.append((fallback, 1))

    for regex, group in regexes:
        for match in regex.finditer(text):
            try:
                start, end = match.start(group), match.end(group)
            except IndexError:
                start, end = match.start(), match.end()
            spans.append((start, end))

    return _merge_spans(spans)


def _overlaps_any(start: int, end: int, protected_spans: List[Tuple[int, int]]) -> bool:
    for p_start, p_end in protected_spans:
        if start < p_end and end > p_start:
            return True
    return False


_EVIDENCE_REDACTOR = None


def get_evidence_redactor():
    """Use regex-only PHIRedactor to scrub nested evidence values (fast, no model downloads)."""
    global _EVIDENCE_REDACTOR
    if _EVIDENCE_REDACTOR is not None:
        return _EVIDENCE_REDACTOR

    _load_phi_redactor_hybrid()

    if PHIRedactor is None or RedactionConfig is None:
        return None
    config = RedactionConfig(
        redact_patient_names=True,
        redact_mrn=True,
        redact_dob=True,
        redact_procedure_dates=True,
        redact_facilities=True,
        redact_ages_over_89=True,
        protect_physician_names=True,
        protect_device_names=True,
        protect_anatomical_terms=True,
    )
    _EVIDENCE_REDACTOR = PHIRedactor(config=config, use_ner_model=False)
    return _EVIDENCE_REDACTOR


def scrub_text_value(value: str, source_id: str) -> str:
    if not value:
        return value
    redactor = get_evidence_redactor()
    if redactor is None or len(value) < 4:
        return post_process_redactions(value)
    try:
        scrubbed, _audit = redactor.scrub(value)
    except Exception:
        scrubbed = value
    return post_process_redactions(scrubbed)


def scrub_nested_values(value: Any, source_id: str) -> Any:
    """Recursively scrub strings inside nested structures."""
    if isinstance(value, str):
        return scrub_text_value(value, source_id)
    if isinstance(value, list):
        return [scrub_nested_values(v, source_id) for v in value]
    if isinstance(value, dict):
        return {k: scrub_nested_values(v, source_id) for k, v in value.items()}
    return value


def apply_redactions(text: str, spans: List[Dict[str, Any]], source_id: str) -> str:
    """
    Replace PHI spans with [REDACTED], processing in reverse order to maintain offsets.

    Args:
        text: Original note text
        spans: List of span dicts with start, end, label, text
        source_id: Identifier for logging (e.g., "golden_001.json:0")

    Returns:
        Text with PHI spans replaced by [REDACTED]
    """
    if not spans:
        return text

    physician_spans = find_physician_name_spans(text)

    # Sort spans by start position descending (apply from end to avoid offset shifts)
    sorted_spans = sorted(spans, key=lambda s: s["start"], reverse=True)

    result = list(text)  # Mutable character list

    for span in sorted_spans:
        start, end = span["start"], span["end"]
        span_text = span.get("text", "")

        # Bounds check
        if start < 0 or end > len(result) or start >= end:
            logger.warning(f"Invalid span bounds in {source_id}: {start}:{end}. Skipping.")
            continue

        # CRITICAL: Don't redact physician/provider names
        if physician_spans and _overlaps_any(start, end, physician_spans):
            continue

        # Safety Check: Verify text at offsets matches span text
        # (Handles slight misalignments or file version mismatches)
        target_text = "".join(result[start:end])

        if span_text and target_text != span_text:
            # Allow for minor whitespace differences, otherwise warn
            if target_text.strip() != span_text.strip():
                logger.warning(
                    f"Offset mismatch in {source_id}: "
                    f"Expected '{span_text[:50]}...', found '{target_text[:50]}...' at {start}:{end}. Skipping."
                )
                continue

        # Replacement strategy: always use the standard token
        replacement = STANDARD_REDACTION_TOKEN

        # Replace slice
        result[start:end] = list(replacement)

    return "".join(result)


def main():
    parser = argparse.ArgumentParser(
        description="Apply platinum PHI redactions to golden JSONs for registry ML training."
    )
    parser.add_argument(
        "--spans",
        default="data/ml_training/phi_platinum_spans_CLEANED.jsonl",
        help="Input JSONL with platinum spans"
    )
    parser.add_argument(
        "--input-dir",
        default="data/knowledge/golden_extractions",
        help="Source golden JSONs directory"
    )
    parser.add_argument(
        "--output-dir",
        default="data/knowledge/golden_extractions_scrubbed",
        help="Destination for scrubbed JSONs"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log what would be done without writing files"
    )
    args = parser.parse_args()

    spans_path = Path(args.spans)
    if not spans_path.exists():
        logger.error(f"Spans file not found: {spans_path}")
        return 1

    # 1. Load all spans indexed by (filename, record_index)
    logger.info(f"Loading spans from {spans_path}...")
    spans_by_record: Dict[Tuple[str, int], List[Dict]] = {}

    with open(spans_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)

            # Keying logic: match how build_model_agnostic_phi_spans.py creates source_path
            # Extract just the filename (e.g., "golden_001.json")
            source_key = Path(rec["source_path"]).name
            record_idx = rec["record_index"]

            key = (source_key, record_idx)
            spans_by_record[key] = rec.get("spans", [])

    logger.info(f"Loaded spans for {len(spans_by_record)} records.")

    # 2. Process Golden JSONs
    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)

    if not in_dir.exists():
        logger.error(f"Input directory not found: {in_dir}")
        return 1

    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    files_processed = 0
    note_text_modified = 0
    records_total = 0
    spans_applied = 0
    evidence_values_modified = 0
    registry_fields_modified = 0

    json_files = sorted(in_dir.glob("*.json"))
    logger.info(f"Processing {len(json_files)} golden JSON files...")

    for json_path in json_files:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                records = json.load(f)

            modified_records = []

            for i, record in enumerate(records):
                records_total += 1
                key = (json_path.name, i)

                source_id = f"{json_path.name}:{i}"

                # 2a) note_text: apply platinum spans + fallback scrub + token standardization
                original_text = record.get("note_text", "")
                new_text = original_text
                spans = spans_by_record.get(key) or []
                if original_text and spans:
                    new_text = apply_redactions(original_text, spans, source_id)
                    spans_applied += len(spans)
                new_text = scrub_text_value(new_text, source_id)
                if new_text != original_text:
                    if not args.dry_run:
                        record["note_text"] = new_text
                    note_text_modified += 1

                # 2b) registry_entry: scrub narrative fields + evidence blocks
                registry_entry = record.get("registry_entry")
                if isinstance(registry_entry, dict):
                    registry_changed = False
                    evidence_changed = False
                    new_registry: Dict[str, Any] = {}
                    for field_key, field_val in registry_entry.items():
                        if field_key == "evidence":
                            new_val = scrub_nested_values(field_val, source_id)
                            if new_val != field_val:
                                evidence_changed = True
                        else:
                            new_val = scrub_nested_values(field_val, source_id)
                            if new_val != field_val:
                                registry_changed = True
                        new_registry[field_key] = new_val

                    if evidence_changed:
                        evidence_values_modified += 1
                        registry_changed = True
                    if registry_changed:
                        registry_fields_modified += 1
                        if not args.dry_run:
                            record["registry_entry"] = new_registry

                modified_records.append(record)

            # Write output (even if no redactions, to maintain set consistency)
            if not args.dry_run:
                out_path = out_dir / json_path.name
                with open(out_path, "w", encoding='utf-8') as f:
                    json.dump(modified_records, f, indent=2)

            files_processed += 1

        except Exception as e:
            logger.error(f"Error processing {json_path}: {e}")

    # Summary
    mode = "[DRY RUN] " if args.dry_run else ""
    logger.info(f"{mode}Complete. Processed {files_processed} files, {records_total} total records.")
    logger.info(f"{mode}Note text modified: {note_text_modified} records.")
    logger.info(f"{mode}Applied spans: {spans_applied}")
    logger.info(f"{mode}Registry entries modified: {registry_fields_modified}")
    logger.info(f"{mode}Evidence blocks modified: {evidence_values_modified}")
    if not args.dry_run:
        logger.info(f"Scrubbed data saved to: {out_dir}")

    return 0


if __name__ == "__main__":
    exit(main())
