"""Heuristics for navigation target and cryobiopsy site extraction.

These helpers are used as a deterministic backstop when model-driven extraction
misses per-target/per-site granularity in complex navigation cases.
"""

from __future__ import annotations

import re
from typing import Any


_TARGET_HEADER_RE = re.compile(
    r"(?im)^\s*(?P<header>"
    r"(?:(?:RIGHT|LEFT)\s+(?:UPPER|MIDDLE|LOWER)\s+LOBE\s+TARGET)"
    r"|(?:RUL|RML|RLL|LUL|LLL|LINGULA)\s+TARGET"
    r")\s*:?\s*$"
)

_TARGET_LOBE_FROM_HEADER: dict[str, str] = {
    "RIGHT UPPER LOBE TARGET": "RUL",
    "RIGHT MIDDLE LOBE TARGET": "RML",
    "RIGHT LOWER LOBE TARGET": "RLL",
    "LEFT UPPER LOBE TARGET": "LUL",
    "LEFT LOWER LOBE TARGET": "LLL",
    "RUL TARGET": "RUL",
    "RML TARGET": "RML",
    "RLL TARGET": "RLL",
    "LUL TARGET": "LUL",
    "LLL TARGET": "LLL",
    "LINGULA TARGET": "Lingula",
}

_ENGAGE_LOCATION_RE = re.compile(
    r"(?is)\bengage(?:d)?\s+the\s+(?P<segment>[^.\n]{3,160}?)\s+of\s+(?:the\s+)?(?P<lobe>RUL|RML|RLL|LUL|LLL|LINGULA)\s*"
    r"\((?P<bronchus>[^)]+)\)"
)

_TARGET_LESION_SIZE_CM_RE = re.compile(r"(?is)\btarget\s+lesion\b[^.\n]{0,80}\b(\d+(?:\.\d+)?)\s*cm\b")
_TARGET_LESION_SIZE_MM_RE = re.compile(r"(?is)\btarget\s+lesion\b[^.\n]{0,80}\b(\d+(?:\.\d+)?)\s*mm\b")

_REBUS_VIEW_RE = re.compile(r"(?is)\bradial\s+ebus\b[^.\n]{0,240}\b(concentric|eccentric|adjacent|not visualized)\b")

_FIDUCIAL_SENTENCE_RE = re.compile(r"(?i)\b(fiducial(?:\s+marker)?s?\b[^\n]{0,260})")
_FIDUCIAL_ACTION_RE = re.compile(r"(?i)\b(?:plac(?:ed|ement)|deploy\w*|position\w*|insert\w*)\b")
_NEGATION_RE = re.compile(r"(?i)\b(?:no|not|without|denies|deny)\b")

_CRYO_RE = re.compile(r"(?i)\btransbronchial\s+cryo(?:biopsy|biopsies)\b|\bcryobiops(?:y|ies)\b|\bTBLC\b")
_CRYO_PROBE_SIZE_RE = re.compile(r"(?i)\b(\d(?:\.\d)?)\s*mm\s*cryo\s*probe\b")
_CRYO_FREEZE_RE = re.compile(r"(?i)\bfreeze\s+time\b[^.\n]{0,40}\b(\d{1,2})\s*seconds?\b")
_TOTAL_SAMPLES_RE = re.compile(r"(?i)\btotal\s+(\d{1,2})\s+samples?\b")


def _canonical_header(value: str) -> str:
    raw = (value or "").strip().upper()
    raw = re.sub(r"\s+", " ", raw)
    return raw


def _normalize_lobe(value: str | None) -> str | None:
    if value is None:
        return None
    upper = str(value).strip().upper()
    if upper in {"RUL", "RML", "RLL", "LUL", "LLL"}:
        return upper
    if upper == "LINGULA":
        return "Lingula"
    return None


def _coerce_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _first_line_containing(text: str, pattern: re.Pattern[str]) -> str | None:
    for line in (text or "").splitlines():
        if pattern.search(line):
            return line.strip() or None
    return None


def _fiducial_in_section(section_text: str) -> tuple[bool, str | None]:
    """Return (placed, details) based on a conservative fiducial placement check."""
    match = _FIDUCIAL_SENTENCE_RE.search(section_text or "")
    if not match:
        return False, None
    sentence = (match.group(1) or "").strip()
    if not sentence:
        return False, None
    if not _FIDUCIAL_ACTION_RE.search(sentence):
        return False, None
    if _NEGATION_RE.search(sentence):
        return False, None
    return True, sentence


def extract_navigation_targets(note_text: str) -> list[dict[str, Any]]:
    """Extract per-target navigation data from common '... LOBE TARGET' headings.

    Returns a list of dicts compatible with granular_data.navigation_targets.
    """
    text = note_text or ""
    if not text.strip():
        return []

    matches = list(_TARGET_HEADER_RE.finditer(text))
    if not matches:
        return []

    targets: list[dict[str, Any]] = []
    for idx, match in enumerate(matches):
        header_raw = match.group("header") or ""
        header = _canonical_header(header_raw)
        section_start = match.end()
        section_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        section = text[section_start:section_end] if section_end > section_start else ""

        lobe = _TARGET_LOBE_FROM_HEADER.get(header)

        segment: str | None = None
        location_text: str | None = None

        engage = _ENGAGE_LOCATION_RE.search(section)
        if engage:
            segment = (engage.group("segment") or "").strip() or None
            lobe = _normalize_lobe(engage.group("lobe")) or lobe
            bronchus = (engage.group("bronchus") or "").strip()
            if segment and lobe and bronchus:
                location_text = f"{segment} of {lobe} ({bronchus})"
            elif segment and lobe:
                location_text = f"{segment} of {lobe}"

        if not location_text and lobe:
            # Prefer a meaningful sentence when present; otherwise fall back to the header lobe.
            target_line = _first_line_containing(section, re.compile(r"(?i)\btarget\s+lesion\b"))
            location_text = target_line or f"{lobe} target"

        lesion_size_mm: float | None = None
        cm = _TARGET_LESION_SIZE_CM_RE.search(section)
        if cm:
            lesion_size_mm = _coerce_float(cm.group(1))
            if lesion_size_mm is not None:
                lesion_size_mm *= 10.0
        else:
            mm = _TARGET_LESION_SIZE_MM_RE.search(section)
            if mm:
                lesion_size_mm = _coerce_float(mm.group(1))

        rebus_view: str | None = None
        rebus_match = _REBUS_VIEW_RE.search(section)
        if rebus_match:
            view = (rebus_match.group(1) or "").strip().title()
            rebus_view = view or None

        fiducial_placed, fiducial_details = _fiducial_in_section(section)

        target: dict[str, Any] = {
            "target_number": idx + 1,
            "target_location_text": location_text or "Unknown target",
        }
        if lobe:
            target["target_lobe"] = lobe
        if segment:
            target["target_segment"] = segment
        if lesion_size_mm is not None:
            target["lesion_size_mm"] = lesion_size_mm
        if rebus_view is not None:
            target["rebus_used"] = True
            target["rebus_view"] = rebus_view
        if fiducial_placed:
            target["fiducial_marker_placed"] = True
        if fiducial_details:
            target["fiducial_marker_details"] = fiducial_details

        # Light-touch sampling hints (used for downstream aggregation).
        cryo_match = _CRYO_RE.search(section)
        if cryo_match:
            target.setdefault("sampling_tools_used", []).append("Cryoprobe")
            window = section[cryo_match.start() : cryo_match.start() + 600]
            samples = _TOTAL_SAMPLES_RE.search(window)
            if samples:
                try:
                    target["number_of_cryo_biopsies"] = int(samples.group(1))
                except Exception:
                    pass

        tbna_match = re.search(r"(?i)\btransbronchial\s+needle\s+aspiration\b|\btbna\b", section)
        if tbna_match:
            target.setdefault("sampling_tools_used", []).append("Needle")
            window = section[tbna_match.start() : tbna_match.start() + 600]
            samples = _TOTAL_SAMPLES_RE.search(window)
            if samples:
                try:
                    target["number_of_needle_passes"] = int(samples.group(1))
                except Exception:
                    pass

        targets.append(target)

    return targets


def extract_cryobiopsy_sites(note_text: str) -> list[dict[str, Any]]:
    """Extract per-site cryobiopsy details from target sections.

    Returns a list of dicts compatible with granular_data.cryobiopsy_sites.
    """
    text = note_text or ""
    if not text.strip():
        return []

    targets = extract_navigation_targets(text)
    if not targets:
        return []

    sites: list[dict[str, Any]] = []
    for target in targets:
        lobe = _normalize_lobe(target.get("target_lobe"))
        if not lobe:
            continue

        # Pull the section associated with this target by re-finding it; keep logic simple and
        # only use per-target cryo flags already detected in extract_navigation_targets.
        if "Cryoprobe" not in (target.get("sampling_tools_used") or []):
            continue

        # Best-effort parse by scanning the whole note for cryo details; when multiple targets
        # exist, these are often uniform (probe size/freeze time).
        probe_size = None
        probe = _CRYO_PROBE_SIZE_RE.search(text)
        if probe:
            probe_size = _coerce_float(probe.group(1))
        freeze = None
        freeze_match = _CRYO_FREEZE_RE.search(text)
        if freeze_match:
            try:
                freeze = int(freeze_match.group(1))
            except Exception:
                freeze = None

        biopsies = target.get("number_of_cryo_biopsies")
        if biopsies is not None:
            try:
                biopsies = int(biopsies)
            except Exception:
                biopsies = None

        site: dict[str, Any] = {
            "site_number": len(sites) + 1,
            "lobe": lobe,
        }
        segment = target.get("target_segment")
        if isinstance(segment, str) and segment.strip():
            site["segment"] = segment.strip()
        if probe_size in {1.1, 1.7, 1.9, 2.4}:
            site["probe_size_mm"] = probe_size
        if isinstance(freeze, int):
            site["freeze_time_seconds"] = freeze
        if isinstance(biopsies, int):
            site["number_of_biopsies"] = biopsies
        sites.append(site)

    return sites


__all__ = ["extract_navigation_targets", "extract_cryobiopsy_sites"]
