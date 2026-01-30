"""Deterministic extraction + safe overrides for disease burden numeric fields.

Goal: prevent LLM numeric hallucinations from entering the production registry
record when the note contains an unambiguous deterministic value.

Current targets (v3 schema):
- clinical_context.lesion_size_mm
- clinical_context.suv_max
- granular_data.cao_interventions_detail[].pre_obstruction_pct / post_obstruction_pct
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from modules.common.spans import Span
from modules.registry.processing.cao_interventions_detail import (
    extract_cao_interventions_detail_with_candidates,
)
from modules.registry.schema import RegistryRecord


@dataclass(frozen=True)
class ExtractedNumeric:
    value: float
    span: Span


_MULTI_DIM_RE = re.compile(r"(?i)\b\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?\s*(?:cm|mm)\b")

_LESION_SIZE_TERM_BEFORE_RE = re.compile(
    r"(?i)\b(?:lesion|nodule|mass|tumou?r)\b"
    r"(?:\s+(?:is|was))?"
    r"(?:\s+(?:measuring|measures|measure|measured|sized|size|diameter(?:\s+of)?))?"
    r"[^0-9]{0,20}"
    r"(?P<num>\d+(?:\.\d+)?)\s*(?P<unit>cm|mm)\b"
)
_LESION_SIZE_TERM_AFTER_RE = re.compile(
    r"(?i)\b(?P<num>\d+(?:\.\d+)?)\s*(?P<unit>cm|mm)\b"
    r"(?:\s+(?:spiculated|solid|part-?solid|ground-?glass|cavitary|calcified|fdg-?avid|pet-?avid))?"
    r"\s+(?:lesion|nodule|mass|tumou?r)\b"
)

_SUV_RE = re.compile(
    r"(?i)\bSUV(?:\s*max(?:imum)?|\s*max)?\b[^0-9]{0,12}(?P<num>\d+(?:\.\d+)?)"
)


def _maybe_unescape_newlines(raw: str) -> str:
    if not raw:
        return ""
    if ("\n" not in raw and "\r" not in raw) and ("\\n" in raw or "\\r" in raw):
        return raw.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")
    return raw


def _coerce_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mm_from(value: float, unit: str) -> float:
    return value * 10.0 if unit.lower() == "cm" else value


def _unique_value(values: list[float], *, places: int = 1) -> float | None:
    if not values:
        return None
    normalized = [round(float(v), places) for v in values]
    uniques = sorted({v for v in normalized})
    if len(uniques) == 1:
        return uniques[0]
    return None


def extract_unambiguous_lesion_size_mm(note_text: str) -> tuple[ExtractedNumeric | None, list[str]]:
    """Return a deterministic lesion size in mm when a single value is supported."""
    text = _maybe_unescape_newlines(note_text or "")
    if not text.strip():
        return None, []

    candidates: list[ExtractedNumeric] = []

    for pattern in (_LESION_SIZE_TERM_AFTER_RE, _LESION_SIZE_TERM_BEFORE_RE):
        for match in pattern.finditer(text):
            snippet = match.group(0)
            # Exclude dimension strings like "2.5 x 1.7 cm" near the match.
            window = text[max(0, match.start() - 40) : min(len(text), match.end() + 40)]
            if _MULTI_DIM_RE.search(window):
                continue
            raw_num = match.group("num")
            raw_unit = match.group("unit")
            num = _coerce_float(raw_num)
            if num is None:
                continue
            value_mm = _mm_from(num, raw_unit)
            if value_mm <= 0 or value_mm > 500:
                continue
            candidates.append(
                ExtractedNumeric(
                    value=value_mm,
                    span=Span(text=snippet.strip(), start=match.start(), end=match.end()),
                )
            )

    if not candidates:
        return None, []

    unique = _unique_value([c.value for c in candidates], places=1)
    if unique is None:
        unique_values = sorted({round(c.value, 1) for c in candidates})
        return None, [f"AMBIGUOUS_DISEASE_BURDEN: lesion_size_mm candidates={unique_values}"]

    best = next((c for c in candidates if round(c.value, 1) == unique), candidates[0])
    return ExtractedNumeric(value=unique, span=best.span), []


def extract_unambiguous_suv_max(note_text: str) -> tuple[ExtractedNumeric | None, list[str]]:
    """Return a deterministic SUV max when a single value is supported."""
    text = _maybe_unescape_newlines(note_text or "")
    if not text.strip():
        return None, []

    candidates: list[ExtractedNumeric] = []
    for match in _SUV_RE.finditer(text):
        raw_num = match.group("num")
        num = _coerce_float(raw_num)
        if num is None:
            continue
        if num < 0 or num > 100:
            continue
        snippet = match.group(0)
        candidates.append(
            ExtractedNumeric(
                value=float(num),
                span=Span(text=snippet.strip(), start=match.start(), end=match.end()),
            )
        )

    if not candidates:
        return None, []

    unique = _unique_value([c.value for c in candidates], places=1)
    if unique is None:
        unique_values = sorted({round(c.value, 1) for c in candidates})
        return None, [f"AMBIGUOUS_DISEASE_BURDEN: suv_max candidates={unique_values}"]

    best = next((c for c in candidates if round(c.value, 1) == unique), candidates[0])
    return ExtractedNumeric(value=unique, span=best.span), []


def apply_disease_burden_overrides(
    record_in: RegistryRecord,
    *,
    note_text: str,
) -> tuple[RegistryRecord, list[str]]:
    """Override disease-burden numeric fields when deterministic extraction is unambiguous."""
    warnings: list[str] = []
    if record_in is None:
        return RegistryRecord(), warnings

    record_data = record_in.model_dump()

    # ----------------------------
    # Clinical context (lesion size, SUV max)
    # ----------------------------
    clinical = record_data.get("clinical_context") or {}
    if not isinstance(clinical, dict):
        clinical = {}

    evidence = record_data.get("evidence") or {}
    if not isinstance(evidence, dict):
        evidence = {}

    lesion, lesion_warnings = extract_unambiguous_lesion_size_mm(note_text)
    warnings.extend(lesion_warnings)
    if lesion is not None:
        old = clinical.get("lesion_size_mm")
        old_val: float | None
        try:
            old_val = None if old is None else float(old)
        except (TypeError, ValueError):
            old_val = None

        if old_val is None or round(old_val, 1) != round(lesion.value, 1):
            if old_val is not None:
                warnings.append(
                    f"OVERRIDE_LLM_NUMERIC: clinical_context.lesion_size_mm {round(old_val, 1)} -> {round(lesion.value, 1)}"
                )
            clinical["lesion_size_mm"] = lesion.value
            evidence.setdefault("clinical_context.lesion_size_mm", []).append(lesion.span)

    suv, suv_warnings = extract_unambiguous_suv_max(note_text)
    warnings.extend(suv_warnings)
    if suv is not None:
        old = clinical.get("suv_max")
        old_val: float | None
        try:
            old_val = None if old is None else float(old)
        except (TypeError, ValueError):
            old_val = None

        if old_val is None or round(old_val, 1) != round(suv.value, 1):
            if old_val is not None:
                warnings.append(
                    f"OVERRIDE_LLM_NUMERIC: clinical_context.suv_max {round(old_val, 1)} -> {round(suv.value, 1)}"
                )
            clinical["suv_max"] = suv.value
            evidence.setdefault("clinical_context.suv_max", []).append(suv.span)

    if clinical:
        record_data["clinical_context"] = clinical
    if evidence:
        record_data["evidence"] = evidence

    # ----------------------------
    # CAO detail backstop (obstruction %)
    # ----------------------------
    parsed_cao, cao_candidates = extract_cao_interventions_detail_with_candidates(note_text)
    if parsed_cao:
        granular = record_data.get("granular_data")
        if granular is None or not isinstance(granular, dict):
            granular = {}

        existing_raw = granular.get("cao_interventions_detail")
        existing: list[dict[str, Any]] = []
        if isinstance(existing_raw, list):
            existing = [dict(item) for item in existing_raw if isinstance(item, dict)]

        def _key(item: dict[str, Any]) -> str:
            return str(item.get("location") or "").strip()

        by_loc: dict[str, dict[str, Any]] = {}
        order: list[str] = []
        for item in existing:
            loc = _key(item)
            if not loc:
                continue
            if loc not in by_loc:
                order.append(loc)
            by_loc[loc] = item

        modified = False
        for item in parsed_cao:
            if not isinstance(item, dict):
                continue
            loc = _key(item)
            if not loc:
                continue

            existing_item = by_loc.get(loc)
            created = False
            if existing_item is None:
                existing_item = {"location": loc}
                created = True

            changed_any = False
            for field in ("pre_obstruction_pct", "post_obstruction_pct"):
                value = item.get(field)
                if value is None:
                    continue
                try:
                    pct_int = max(0, min(100, int(value)))
                except (TypeError, ValueError):
                    continue

                candidate_set = cao_candidates.get(loc, {}).get(field)
                if not isinstance(candidate_set, set) or len(candidate_set) != 1 or pct_int not in candidate_set:
                    if isinstance(candidate_set, set) and len(candidate_set) > 1:
                        warnings.append(
                            "AMBIGUOUS_DISEASE_BURDEN: "
                            f"granular_data.cao_interventions_detail[{loc}].{field} candidates={sorted(candidate_set)}"
                        )
                    elif isinstance(candidate_set, set):
                        warnings.append(
                            "AMBIGUOUS_DISEASE_BURDEN: "
                            f"granular_data.cao_interventions_detail[{loc}].{field} candidates=[]"
                        )
                    else:
                        warnings.append(
                            "AMBIGUOUS_DISEASE_BURDEN: "
                            f"granular_data.cao_interventions_detail[{loc}].{field} candidates=<unavailable>"
                        )
                    continue

                existing_val = existing_item.get(field)
                if existing_val is None:
                    existing_item[field] = pct_int
                    changed_any = True
                    continue
                try:
                    existing_pct = int(existing_val)
                except (TypeError, ValueError):
                    existing_pct = None

                if existing_pct is None or existing_pct != pct_int:
                    if existing_pct is not None:
                        warnings.append(
                            f"OVERRIDE_LLM_NUMERIC: granular_data.cao_interventions_detail[{loc}].{field} {existing_pct} -> {pct_int}"
                        )
                    existing_item[field] = pct_int
                    changed_any = True

            if created:
                if changed_any:
                    by_loc[loc] = existing_item
                    order.append(loc)
                    modified = True
            else:
                if changed_any:
                    by_loc[loc] = existing_item
                    modified = True

        if modified:
            merged = [by_loc[loc] for loc in order if loc in by_loc]
            granular["cao_interventions_detail"] = merged
            record_data["granular_data"] = granular

    try:
        return RegistryRecord(**record_data), warnings
    except ValidationError as exc:
        warnings.append(f"DISEASE_BURDEN_OVERRIDE_FAILED: {type(exc).__name__}")
        return record_in, warnings


__all__ = [
    "ExtractedNumeric",
    "extract_unambiguous_lesion_size_mm",
    "extract_unambiguous_suv_max",
    "apply_disease_burden_overrides",
]
