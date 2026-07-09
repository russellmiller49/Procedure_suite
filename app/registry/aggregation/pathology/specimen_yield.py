"""Per-specimen pathology yield extraction.

Splits a pathology report into specimen blocks (reusing the final-diagnosis
block conventions of ``extract_pathology``) and classifies each specimen's
sampling modality (TBNA vs brushing vs washing vs biopsy family) and result
category, so the registry can answer "which sampling modality made the
diagnosis" per case.
"""

from __future__ import annotations

import re
from typing import Any

from app.registry.aggregation.outcomes_rollup import classify_diagnostic_yield
from app.registry.aggregation.pathology.normalize import find_station_tokens
from app.registry.aggregation.sanitize import compact_text


_SPECIMEN_TYPE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # Order matters: more specific modalities first.
    (re.compile(r"\btransbronchial\s+cryobiops|cryobiops", re.IGNORECASE), "cryobiopsy"),
    (re.compile(r"\btransbronchial\s+(?:lung\s+)?biops|\btbbx\b|\btblb\b", re.IGNORECASE), "transbronchial_biopsy"),
    (re.compile(r"\bendobronchial\s+biops|\bebbx\b", re.IGNORECASE), "endobronchial_biopsy"),
    (re.compile(r"\bpleural?\s+biops|\bparietal\s+pleura\b[^\n]{0,40}\bbiops", re.IGNORECASE), "pleural_biopsy"),
    (re.compile(r"\bcore\s+(?:needle\s+)?biops", re.IGNORECASE), "core_biopsy"),
    (re.compile(r"\b(?:ebus[-\s]?)?(?:tbna|fna)\b|needle\s+aspirat", re.IGNORECASE), "tbna"),
    (re.compile(r"\bbrush(?:ing)?s?\b", re.IGNORECASE), "brushing"),
    (re.compile(r"\bbronchoalveolar\s+lavage\b|\bbal\b", re.IGNORECASE), "bal"),
    (re.compile(r"\bwash(?:ing)?s?\b", re.IGNORECASE), "washing"),
    (re.compile(r"\bpleural\s+fluid\b|\beffusion\s+cytology\b", re.IGNORECASE), "pleural_fluid"),
    (re.compile(r"\bbiops(?:y|ies)\b", re.IGNORECASE), "biopsy_nos"),
)

_SPECIMEN_LABEL_RE = re.compile(r"(?im)^\s*(?:part\s+)?([A-Z]|\d{1,2})[.):]\s+")

_YIELD_RANK = {"Malignant": 3, "Benign-specific": 2, "Unknown": 1, "Nondiagnostic": 0}


def _specimen_type(block: str) -> str:
    for pattern, label in _SPECIMEN_TYPE_PATTERNS:
        if pattern.search(block):
            return label
    return "other"


def _split_labeled_blocks(text: str) -> list[tuple[str | None, str]]:
    """Split into (label, block) pairs on 'A. ...' / '1) ...' specimen markers."""
    value = text or ""
    matches = list(_SPECIMEN_LABEL_RE.finditer(value))
    if not matches:
        stripped = value.strip()
        return [(None, stripped)] if stripped else []
    blocks: list[tuple[str | None, str]] = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(value)
        block = value[match.end() : end].strip()
        if block:
            blocks.append((str(match.group(1)).upper(), block))
    return blocks


def extract_specimen_yields(text: str) -> dict[str, Any]:
    """Return per-specimen yield records for a pathology report."""
    from app.registry.aggregation.pathology.extract_pathology import (
        _split_prefer_final_diagnosis_blocks,  # noqa: PLC2701 - shared block conventions
    )

    qa_flags: list[str] = []
    specimen_results: list[dict[str, Any]] = []

    # Prefer the FINAL DIAGNOSIS section (same convention as extract_pathology),
    # but keep the label association when explicit specimen markers exist.
    _blocks, using_final = _split_prefer_final_diagnosis_blocks(text or "")
    section_text = text or ""
    if using_final:
        heading = re.search(r"(?im)^[ \t]*FINAL\s+DIAGNOSIS\b.*$", section_text)
        if heading:
            section_text = section_text[heading.end() :]

    for label, block in _split_labeled_blocks(section_text):
        specimen_type = _specimen_type(block)
        result_category = classify_diagnostic_yield(block)
        stations = find_station_tokens(block)
        first_line = block.splitlines()[0] if block.splitlines() else block
        specimen_results.append(
            {
                "specimen_label": label,
                "specimen_type": specimen_type,
                "station": stations[0] if stations else None,
                "site_text": compact_text(first_line, max_chars=120) or None,
                "result_category": result_category,
                "diagnosis_text": compact_text(block, max_chars=220) or None,
            }
        )

    if len(specimen_results) == 1 and specimen_results[0].get("specimen_label") is None:
        # Unlabeled single-block reports carry little per-specimen signal; only
        # keep them when a sampling modality is identifiable.
        if specimen_results[0]["specimen_type"] == "other":
            specimen_results = []

    if not specimen_results:
        qa_flags.append("no_specimen_blocks_found")

    return {"specimen_results": specimen_results, "qa_flags": sorted(set(qa_flags))}


def best_yield_from_specimens(specimen_results: list[dict[str, Any]] | None) -> str | None:
    """Case-level yield from per-specimen results (best result wins)."""
    best: str | None = None
    for item in specimen_results or []:
        if not isinstance(item, dict):
            continue
        category = item.get("result_category")
        if not isinstance(category, str) or category not in _YIELD_RANK:
            continue
        if best is None or _YIELD_RANK[category] > _YIELD_RANK[best]:
            best = category
    return best


__all__ = ["best_yield_from_specimens", "extract_specimen_yields"]
