"""Deterministic chest radiograph (CXR) / pleural ultrasound event extractor.

Post-procedure radiographs are the most common ancillary study after IP
procedures (pneumothorax checks after biopsy, effusion re-accumulation after
drainage, device/stent position). This extractor produces the same
``imaging_snapshot`` shape as the CT/PET extractors plus structured
post-procedure findings (pneumothorax / effusion presence, side, trend, and
device position).
"""

from __future__ import annotations

import re
from typing import Any

from app.registry.aggregation.imaging.parse_common import build_snapshot
from app.registry.aggregation.sanitize import compact_text


_PTX_NEG_RE = re.compile(
    r"\b(?:no|without|negative\s+for)\b[^.\n;]{0,40}\bpneumothora(?:x|ces)\b"
    r"|\bpneumothorax\b[^.\n;]{0,40}\b(?:has\s+)?resolved\b",
    re.IGNORECASE,
)
_PTX_POS_RE = re.compile(r"\bpneumothora(?:x|ces)\b", re.IGNORECASE)
_HYDRO_PTX_RE = re.compile(r"\bhydropneumothorax\b", re.IGNORECASE)

_EFFUSION_NEG_RE = re.compile(
    r"\b(?:no|without|negative\s+for)\b[^.\n;]{0,50}\b(?:pleural\s+)?effusions?\b"
    r"|\beffusions?\b[^.\n;]{0,40}\b(?:has\s+)?resolved\b",
    re.IGNORECASE,
)
_EFFUSION_POS_RE = re.compile(r"\b(?:pleural\s+)?effusions?\b", re.IGNORECASE)

_SIDE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bbilateral\b", re.IGNORECASE), "Bilateral"),
    (re.compile(r"\b(?:left|left[-\s]sided)\b", re.IGNORECASE), "Left"),
    (re.compile(r"\b(?:right|right[-\s]sided)\b", re.IGNORECASE), "Right"),
)

_TREND_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bresolved|resolution\b", re.IGNORECASE), "Resolved"),
    (re.compile(r"\b(?:new|interval\s+development)\b", re.IGNORECASE), "New"),
    (re.compile(r"\b(?:decreased|smaller|improv\w+|reduced|interval\s+decrease)\b", re.IGNORECASE), "Decreased"),
    (re.compile(r"\b(?:increased|larger|worsen\w+|enlarg\w+|interval\s+increase)\b", re.IGNORECASE), "Increased"),
    (re.compile(r"\b(?:stable|unchanged|similar)\b", re.IGNORECASE), "Stable"),
)

_DEVICE_SENTENCE_RE = re.compile(
    r"[^.\n;]*\b(?:stent|chest\s+tube|pigtail|pleural\s+catheter|pleurx|ipc|valve|"
    r"tracheostomy\s+tube|endotracheal\s+tube|ett|drain)\b[^.\n;]*",
    re.IGNORECASE,
)
_DEVICE_POSITION_CUE_RE = re.compile(
    r"\b(?:in\s+(?:good|satisfactory|unchanged|stable|appropriate|expected)\s+position|"
    r"well[-\s]positioned|position\s+(?:is\s+)?(?:satisfactory|stable|unchanged|appropriate)|"
    r"malposition\w*|migrat\w+|dislodg\w+|kink\w+|tip\s+(?:at|in|near|projects?)\b)",
    re.IGNORECASE,
)

_POST_PROCEDURE_CUE_RE = re.compile(
    r"\b(?:post[-\s]?procedure|post[-\s]?biopsy|post[-\s]?bronch\w*|status\s+post|s/p|"
    r"following\s+(?:the\s+)?(?:procedure|biopsy|bronchoscopy|thoracentesis|placement))\b",
    re.IGNORECASE,
)

_LUNG_REEXPANSION_RE = re.compile(
    r"\b(?:full|complete)\s+(?:lung\s+)?re-?expansion\b|\blung\s+(?:is\s+)?re-?expanded\b",
    re.IGNORECASE,
)


def _finding_sentences(text: str, pattern: re.Pattern[str]) -> list[str]:
    sentences = []
    for sentence in re.split(r"(?<=[.\n;])\s+", text or ""):
        if sentence.strip() and pattern.search(sentence):
            sentences.append(sentence.strip())
    return sentences


def _side_of(sentences: list[str]) -> str | None:
    for sentence in sentences:
        for pattern, label in _SIDE_PATTERNS:
            if pattern.search(sentence):
                return label
    return None


def _trend_of(sentences: list[str]) -> str | None:
    for sentence in sentences:
        for pattern, label in _TREND_PATTERNS:
            if pattern.search(sentence):
                return label
    return None


def extract_cxr_event(
    text: str,
    *,
    relative_day_offset: int | None,
    event_subtype: str | None,
    modality: str = "cxr",
) -> dict[str, Any]:
    qa_flags: list[str] = []
    clean = text or ""

    subtype = (event_subtype or "").strip().lower() or None
    if subtype is None and _POST_PROCEDURE_CUE_RE.search(clean):
        subtype = "post_procedure"

    # Pneumothorax: negation wins within its own sentence scope.
    ptx_sentences = _finding_sentences(clean, _PTX_POS_RE)
    ptx_neg_sentences = _finding_sentences(clean, _PTX_NEG_RE)
    pneumothorax: bool | None = None
    ptx_side = None
    ptx_trend = None
    if _HYDRO_PTX_RE.search(clean):
        pneumothorax = True
        ptx_sentences = ptx_sentences or _finding_sentences(clean, _HYDRO_PTX_RE)
    if ptx_sentences:
        positive_sentences = [s for s in ptx_sentences if not _PTX_NEG_RE.search(s)]
        if positive_sentences:
            pneumothorax = True
            ptx_side = _side_of(positive_sentences)
            ptx_trend = _trend_of(positive_sentences)
        elif ptx_neg_sentences:
            pneumothorax = False
            if any(re.search(r"(?i)\bresolved\b", s) for s in ptx_neg_sentences):
                ptx_trend = "Resolved"

    effusion_sentences = _finding_sentences(clean, _EFFUSION_POS_RE)
    pleural_effusion: bool | None = None
    effusion_side = None
    effusion_trend = None
    if effusion_sentences:
        positive_sentences = [s for s in effusion_sentences if not _EFFUSION_NEG_RE.search(s)]
        if positive_sentences:
            pleural_effusion = True
            effusion_side = _side_of(positive_sentences)
            effusion_trend = _trend_of(positive_sentences)
        else:
            pleural_effusion = False
            if any(re.search(r"(?i)\bresolved\b", s) for s in effusion_sentences):
                effusion_trend = "Resolved"

    device_position_text: str | None = None
    for sentence in _DEVICE_SENTENCE_RE.finditer(clean):
        if _DEVICE_POSITION_CUE_RE.search(sentence.group(0)):
            device_position_text = compact_text(sentence.group(0), max_chars=200) or None
            break

    if _LUNG_REEXPANSION_RE.search(clean) and pneumothorax is None:
        pneumothorax = False

    if pneumothorax is None and pleural_effusion is None and device_position_text is None:
        qa_flags.append("cxr_no_structured_findings")

    snapshot = build_snapshot(
        relative_day_offset=relative_day_offset,
        modality=modality,
        subtype=subtype,
        text=clean,
        qa_flags=qa_flags,
    )
    # Tumor-response semantics do not apply to post-procedure films.
    if subtype == "post_procedure":
        snapshot["response"] = None
    snapshot["pneumothorax"] = pneumothorax
    snapshot["pneumothorax_side"] = ptx_side
    snapshot["pneumothorax_trend"] = ptx_trend
    snapshot["pleural_effusion"] = pleural_effusion
    snapshot["effusion_side"] = effusion_side
    snapshot["effusion_trend"] = effusion_trend
    snapshot["device_position_text"] = device_position_text

    return {"imaging_snapshot": snapshot, "qa_flags": list(snapshot.get("qa_flags") or [])}


__all__ = ["extract_cxr_event"]
