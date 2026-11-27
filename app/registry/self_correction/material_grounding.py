"""Ground self-correction patches for mechanical debulking in the note text.

CPT 31640 is derived only when ``mechanical_debulking.material_type == "tumor"``. A judge
patch may switch debulking on, but the material type is never taken from the judge: it is
re-derived here from the procedure-detail sentence(s) that contain the judge's verbatim
evidence quote, using the same classifier as the deterministic extractor. Anything that
cannot be anchored, is negated, or sits in history/plan wording grounds to "unknown", which
keeps 31640 suppressed.
"""

from __future__ import annotations

import re
from typing import Any

from app.registry.deterministic_extractors import (
    _preferred_procedure_detail_text,
    _strip_cpt_definition_lines,
    infer_debulking_material_type,
)
from app.registry.schema import RegistryRecord

_DEBULKING_PATH_PREFIX = "/procedures_performed/mechanical_debulking"

_SENTENCE_BOUNDARY_RE = re.compile(r"[.!?\n]")
_NEGATED_TISSUE_RE = re.compile(
    r"(?i)\b(?:no|not|without|negative\s+for|free\s+of)\b[^.\n]{0,40}\b(?:tumou?r|mass|lesion)\b"
)
_PLAN_RE = re.compile(
    r"(?i)\b(?:will|plan(?:ned|s)?|recommend(?:ed|s)?|consider(?:ed)?|future|follow[- ]?up|"
    r"surveillance|if\s+needed|scheduled)\b"
)
_HISTORY_RE = re.compile(
    r"(?i)(?:^\s*(?:history|hx|pmh|indication)s?\b|\b(?:s/p|status\s+post|years?\s+ago|"
    r"in\s+(?:19|20)\d\d|previously\s+(?:treated|resected|excised|debulked|removed))\b)"
)
# Action on tissue in this procedure; tools or tissue nouns alone do not qualify.
_TISSUE_ACTION_RE = re.compile(
    r"(?i)\b(?:debulk\w*|excis\w*|resect\w*|remov\w*|cored?|coring|snared|shav\w*|"
    r"microdebrid\w*|extract\w*|cleared|recanaliz\w*)\b"
)


def _patch_touches_debulking(patch: list[dict[str, Any]]) -> bool:
    return any(
        isinstance(op, dict) and str(op.get("path") or "").startswith(_DEBULKING_PATH_PREFIX)
        for op in patch or []
    )


def _locate_quote(text: str, quote: str) -> tuple[int, int] | None:
    tokens = [re.escape(tok) for tok in (quote or "").split() if tok]
    if not tokens:
        return None
    match = re.search(r"\s+".join(tokens), text, flags=re.IGNORECASE)
    return (match.start(), match.end()) if match else None


def _sentence_span(text: str, start: int, end: int) -> str:
    left = start
    while left > 0 and not _SENTENCE_BOUNDARY_RE.match(text[left - 1]):
        left -= 1
    boundary = _SENTENCE_BOUNDARY_RE.search(text, end)
    right = boundary.start() if boundary else len(text)
    return text[left:right]


def ground_material_type_from_quote(note_text: str, evidence_quote: str) -> str:
    """Return the debulking material type supported by the anchored evidence quote."""
    procedure_text, _used_detail = _preferred_procedure_detail_text(note_text or "")
    procedure_text = _strip_cpt_definition_lines(procedure_text or "")
    span = _locate_quote(procedure_text, evidence_quote)
    if span is None:
        return "unknown"
    sentence = _sentence_span(procedure_text, *span)
    if _PLAN_RE.search(sentence) or _HISTORY_RE.search(sentence):
        return "unknown"
    if not _TISSUE_ACTION_RE.search(sentence):
        return "unknown"
    material = infer_debulking_material_type(sentence)
    if material == "tumor" and _NEGATED_TISSUE_RE.search(sentence):
        return "unknown"
    return material


def ground_mechanical_debulking_material(
    record: RegistryRecord,
    *,
    patch: list[dict[str, Any]],
    evidence_quote: str,
    note_text: str,
) -> tuple[RegistryRecord, str | None]:
    """Overwrite ``mechanical_debulking.material_type`` with the quote-grounded value.

    Applies only when the patch touches mechanical debulking and the patched record marks it
    performed. Returns the (possibly updated) record and a warning describing the change.
    """
    if not _patch_touches_debulking(patch):
        return record, None
    procedures = record.procedures_performed
    debulking = getattr(procedures, "mechanical_debulking", None) if procedures else None
    if debulking is None or getattr(debulking, "performed", None) is not True:
        return record, None

    grounded = ground_material_type_from_quote(note_text, evidence_quote)
    current = getattr(debulking, "material_type", None)
    if current == grounded:
        return record, None

    record_dict = record.model_dump()
    record_dict["procedures_performed"]["mechanical_debulking"]["material_type"] = grounded
    updated = RegistryRecord(**record_dict)
    return updated, (
        "SELF_CORRECT_MATERIAL_GROUNDED: mechanical_debulking.material_type="
        f"{grounded} (patch value {current!r} replaced from evidence quote)"
    )
