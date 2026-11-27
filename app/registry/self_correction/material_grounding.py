"""Ground self-correction patches for mechanical debulking in the note text.

CPT 31640 is derived only when ``mechanical_debulking.material_type == "tumor"``. A judge
patch may switch debulking on, but the material type is never taken from the judge: it is
re-derived here from the procedure-detail clause that contains the judge's verbatim evidence
quote, using the same classifier as the deterministic extractor. "tumor" additionally needs the
tumor noun to be what the action was done to (object or passive subject of the verb). Anything
that cannot be anchored, is negated, or is plan/history wording grounds to "unknown", which
keeps 31640 suppressed. A material already known before the patch is never replaced.
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
_UNKNOWN_MATERIALS = {None, "", "unknown"}

# Clause boundaries: sentence punctuation, newline and ";" -- but not a period between digits.
_CLAUSE_BOUNDARY_RE = re.compile(r"[!?\n;]|(?<!\d)\.|\.(?!\d)")

_TUMOR_NOUN = r"(?:tumou?rs?|mass(?:es)?|lesions?|neoplasms?|carcinoma|malignancy)"
_ACTION_VERB = (
    r"(?:debulk\w*|excis\w*|resect\w*|remov\w*|cored|coring|core\s+out|snared|shaved|"
    r"microdebrided|extract\w*|cleared|recanaliz\w*|ablat\w*)"
)
# Gap words between an action and its object; conjunctions/clause pivots break the link.
_LINK_GAP_WORD = r"(?:(?!(?:and|or|then|after|before|while|but|was|were|is|are)\b)[\w-]+,?\s+)"
_LINK_GAP_CHARS = r"(?:(?!\b(?:and|after|before|then|while|but)\b)[^;\n]){0,60}?"
_TUMOR_ACTION_LINK_RE = re.compile(
    rf"(?i)"
    # passive: "the (exophytic) tumor ... was debulked"
    rf"\b{_TUMOR_NOUN}\b{_LINK_GAP_CHARS}\b(?:was|were|being|been)\s+(?:\w+\s+){{0,2}}?{_ACTION_VERB}\b"
    # active / nominal: "debulking of an obstructing endobronchial tumor", "excised the mass"
    rf"|\b{_ACTION_VERB}\s+(?:of\s+)?(?:the\s+|an?\s+)?{_LINK_GAP_WORD}{{0,4}}{_TUMOR_NOUN}\b"
    # compound noun: "tumor excision", "tumor debulking"
    rf"|\b{_TUMOR_NOUN}\s+(?:excision|debulking|resection|removal|coring|ablation)\b"
)
_NEGATED_TISSUE_RE = re.compile(
    rf"(?i)\b(?:no|not|without|negative\s+for|free\s+of)\b[^;\n]{{0,40}}\b{_TUMOR_NOUN}\b"
)
_PLAN_RE = re.compile(
    r"(?i)\b(?:will|plan(?:ned|s)?|recommend(?:ed|s)?|consider(?:ed)?|future|follow[- ]?up|"
    r"surveillance|if\s+needed|scheduled)\b"
)
_HISTORY_PREFIX_RE = re.compile(
    r"(?i)(?:^\s*(?:history|hx|pmh|indication)s?\b|\b(?:s/p|status\s+post|previously)\b)"
)
_HISTORY_DATE_RE = re.compile(r"(?i)\b(?:years?\s+ago|in\s+(?:19|20)\d\d)\b")


def _patch_touches_debulking(patch: list[dict[str, Any]]) -> bool:
    return any(
        isinstance(op, dict) and str(op.get("path") or "").startswith(_DEBULKING_PATH_PREFIX)
        for op in patch or []
    )


def _locate_quote(text: str, quote: str) -> tuple[int, int] | None:
    tokens = [re.escape(tok) for tok in (quote or "").strip().rstrip(".").split() if tok]
    if not tokens:
        return None
    match = re.search(r"\s+".join(tokens), text, flags=re.IGNORECASE)
    return (match.start(), match.end()) if match else None


def _clause_span(text: str, start: int, end: int) -> str:
    left = 0
    for boundary in _CLAUSE_BOUNDARY_RE.finditer(text, 0, start):
        left = boundary.end()
    right_match = _CLAUSE_BOUNDARY_RE.search(text, max(end, start))
    right = right_match.start() if right_match else len(text)
    return text[left:right]


def ground_material_type_from_quote(note_text: str, evidence_quote: str) -> str:
    """Return the debulking material type supported by the anchored evidence quote."""
    procedure_text, _used_detail = _preferred_procedure_detail_text(note_text or "")
    procedure_text = _strip_cpt_definition_lines(procedure_text or "")
    span = _locate_quote(procedure_text, evidence_quote)
    if span is None:
        return "unknown"
    clause = _clause_span(procedure_text, *span)
    material = infer_debulking_material_type(clause)
    if material != "tumor":
        return material

    link = _TUMOR_ACTION_LINK_RE.search(clause)
    if link is None:
        return "unknown"
    before_action = clause[: link.start()]
    if _PLAN_RE.search(before_action) or _HISTORY_PREFIX_RE.search(before_action):
        return "unknown"
    if _PLAN_RE.search(link.group(0)) or _HISTORY_DATE_RE.search(clause):
        return "unknown"
    if _NEGATED_TISSUE_RE.search(clause):
        return "unknown"
    return "tumor"


def _debulking(record: RegistryRecord | None) -> Any:
    procedures = record.procedures_performed if record is not None else None
    return getattr(procedures, "mechanical_debulking", None) if procedures else None


def ground_mechanical_debulking_material(
    record: RegistryRecord,
    *,
    patch: list[dict[str, Any]],
    evidence_quote: str,
    note_text: str,
    original_record: RegistryRecord | None = None,
) -> tuple[RegistryRecord, str | None]:
    """Set ``mechanical_debulking.material_type`` on a patched record from the evidence quote.

    Applies only when the patch touches mechanical debulking and the patched record marks it
    performed. A material that was known before the patch is kept (any judge-written value is
    reverted); the quote only fills a missing/"unknown" material. Returns the record and a
    warning describing what was done, if anything.
    """
    if not _patch_touches_debulking(patch):
        return record, None
    debulking = _debulking(record)
    if debulking is None or getattr(debulking, "performed", None) is not True:
        return record, None

    pre_patch = getattr(_debulking(original_record), "material_type", None)
    current = getattr(debulking, "material_type", None)
    grounded = ground_material_type_from_quote(note_text, evidence_quote)

    warning: str | None
    if pre_patch in _UNKNOWN_MATERIALS:
        target = grounded
        warning = (
            "SELF_CORRECT_MATERIAL_GROUNDED: mechanical_debulking.material_type="
            f"{grounded} (patch value {current!r} replaced from evidence quote)"
        )
    else:
        target = pre_patch
        if grounded not in _UNKNOWN_MATERIALS and grounded != pre_patch:
            warning = (
                "SELF_CORRECT_MATERIAL_CONFLICT: kept pre-patch mechanical_debulking.material_type="
                f"{pre_patch}; evidence quote suggests {grounded}"
            )
        elif current != pre_patch:
            warning = (
                "SELF_CORRECT_MATERIAL_GROUNDED: kept pre-patch mechanical_debulking.material_type="
                f"{pre_patch} (patch value {current!r} reverted)"
            )
        else:
            warning = None

    if current == target:
        return record, warning if warning and "CONFLICT" in warning else None

    record_dict = record.model_dump()
    record_dict["procedures_performed"]["mechanical_debulking"]["material_type"] = target
    return RegistryRecord(**record_dict), warning
