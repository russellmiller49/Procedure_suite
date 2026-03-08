from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Literal

from rapidfuzz.fuzz import partial_ratio

from app.common.spans import Span
from app.registry.deterministic_extractors import (
    AIRWAY_DILATION_PATTERNS,
    CHEST_TUBE_PATTERNS,
    IPC_PATTERNS,
    RIGID_BRONCHOSCOPY_PATTERNS,
    THERAPEUTIC_ASPIRATION_PATTERNS,
    extract_airway_stent,
)
from app.registry.schema import RegistryRecord
from app.registry.schema.ip_v3_extraction import IPRegistryV3, ProcedureEvent


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_WS_RE = re.compile(r"\s+")
_CHECKBOX_RE = re.compile(r"(?:^\s*0\s*[—\-]\s*|\[[ xX]?\]|[☐☑☒])", re.IGNORECASE)
_CPT_RE = re.compile(r"\b(?:[37]\d{4}|32\d{3})\b")
_STENT_TOKEN_RE = re.compile(r"\bstent(?:ing|s)?\b", re.IGNORECASE)
_STENT_NEGATION_WINDOW_RE = re.compile(
    r"\b(?:"
    r"no\s+(?:appropriate|suitable)\s+landing\s+point"
    r"|no\s+landing\s+point"
    r"|no\s+appropriate\s+place\b[^.\n]{0,80}\bstent(?:ing|s)?\b"
    r"|not\s+(?:safe|possible|feasible)\b[^.\n]{0,80}\bstent(?:ing|s)?\b"
    r"|unable\s+to\b[^.\n]{0,80}\bstent(?:ing|s)?\b"
    r"|could\s+not\b[^.\n]{0,80}\bstent(?:ing|s)?\b"
    r"|decid(?:ed|ing)\b[^.\n]{0,80}\b(?:against|to\s+not)\b[^.\n]{0,80}\bstent(?:ing|s)?\b"
    r"|decision\b[^.\n]{0,80}\bto\s+not\b[^.\n]{0,80}\bstent(?:ing|s)?\b"
    r"|abandon(?:ed|ing)?\b[^.\n]{0,80}\bstent(?:ing|s)?\b"
    r"|abort(?:ed|ing)?\b[^.\n]{0,80}\bstent(?:ing|s)?\b"
    r")\b",
    re.IGNORECASE,
)
_SECTION_INLINE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 /()_-]{1,60})\s*:\s*(.*)$")
_SECTION_ONLY_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 /()_-]{1,60})\s*:\s*$")

_NARRATIVE_SECTIONS = {
    "procedure in detail",
    "description of procedure",
    "procedure description",
    "technique",
    "operative note",
    "procedure details",
    "detail",
}
_FINDINGS_SECTIONS = {"findings", "eus-b findings", "ebus findings"}
_IMPRESSION_SECTIONS = {"impression", "conclusion"}
_HISTORY_PLAN_SECTIONS = {
    "hpi",
    "history",
    "history of present illness",
    "assessment",
    "plan",
    "indication",
    "indications",
    "reason for procedure",
}
_HEADER_METADATA_SECTIONS = {
    "procedure",
    "procedures",
    "procedure(s)",
    "pre/post dx",
    "pre op diagnosis",
    "post op diagnosis",
    "anesthesia",
    "estimated blood loss",
    "disposition",
}
_DISALLOWED_CPT_SOURCE_TYPES = {
    "template_checkbox",
    "menu_or_code_block",
    "history_or_plan",
    "device_status_only",
    "header_or_metadata",
    "impression",
}
_STATUS_ONLY_STENT_RE = re.compile(
    r"(?i)\b(?:known|existing|previously\s+placed|prior)\b[^.\n]{0,80}\bstent\b|"
    r"\bstent\b[^.\n]{0,80}\b(?:patent|well[-\s]?seated|well positioned|good position|remained in good position|in good position|stable)\b|"
    r"\b(?:patency|position)\s+(?:evaluated|reassessed)\b"
)
_STENT_ACTION_RE = re.compile(
    r"(?i)\b(?:stent\b[^.\n]{0,60}\b(?:placed|deployed|inserted|removed|exchanged|repositioned|revised)|"
    r"(?:placed|deployed|inserted|removed|exchanged|repositioned|revised)\b[^.\n]{0,60}\bstent)\b"
)
_PERIPHERAL_TARGET_RE = re.compile(
    r"(?i)\b(?:lesion|nodule|mass|target|peripheral|rul|rml|rll|lul|lll|lingula|segment|subsegment|lung)\b"
)
_EBUS_STATION_RE = re.compile(
    r"(?i)\b(?:station\s+\d+[a-z]?|2r|2l|4r|4l|7|10[rl]|11[rl](?:s|i)?|12[rl]|mediastinal|hilar|lymph\s+node|nodal)\b"
)
_LINEAR_EBUS_RE = re.compile(r"(?i)\b(?:linear\s+ebus|ebus[-\s]?tbna|convex\s+probe\s+ebus|cp-?ebus)\b")
_TBNA_ACTION_RE = re.compile(r"(?i)\b(?:tbna|fna|needle\s+aspirat(?:e|ion)|passes?|sampled|biops(?:y|ies|ied))\b")
_BAL_ACTION_RE = re.compile(
    r"(?i)\b(?:bronchoalveolar lavage|bal)\b[^.\n]{0,80}\b(?:performed|obtained|sent|done)\b|"
    r"\b(?:performed|obtained|done)\b[^.\n]{0,80}\b(?:bronchoalveolar lavage|bal)\b"
)
_WLL_RE = re.compile(r"(?i)\b(?:whole lung lavage|wll)\b")
_CRYO_ACTION_RE = re.compile(
    r"(?i)\b(?:transbronchial\s+cryobiops(?:y|ies)|cryobiops(?:y|ies)|freeze\s+time|cryoprobe)\b"
)
_CRYO_OBTAINED_RE = re.compile(r"(?i)\b(?:obtained|performed|sample(?:s|d)?|biops(?:y|ies))\b")
_CRYO_SAMPLE_COUNT_RE = re.compile(
    r"(?i)\b(?:\d+|one|two|three|four|five|six)\s+cryobiops(?:y|ies)\b|\b(?:1\.1|1\.7|1\.9|2\.4)\s*mm\s+probe\b"
)
_CRYO_NEGATED_RE = re.compile(
    r"(?i)\b(?:no|not|without)\b[^.\n]{0,40}\b(?:transbronchial\s+cryobiops(?:y|ies)|cryobiops(?:y|ies)|cryoprobe)\b"
    r"|\b(?:transbronchial\s+cryobiops(?:y|ies)|cryobiops(?:y|ies)|cryoprobe)\b[^.\n]{0,40}\b(?:not\s+performed|was\s+not\s+performed|not\s+done|deferred|aborted)\b"
)
_FORCEPS_BIOPSY_RE = re.compile(r"(?i)\bforceps\s+biops(?:y|ies)\b")
_CAO_ACTION_RE = re.compile(
    r"(?i)\b(?:debulk(?:ed|ing)?|mechanical debulking|tumou?r removed|tumou?r debulking|recanalization|ablat(?:ed|ion)|destruct(?:ion|ed)|treated)\b"
)
_CAO_TARGET_RE = re.compile(r"(?i)\b(?:tumou?r|lesion|mass|obstruction|airway)\b")
_TOOL_ONLY_RE = re.compile(r"(?i)\b(?:snare|forceps|cryoprobe|apc|argon plasma coagulation|laser|electrocautery)\b")
_IPC_TARGET_RE = re.compile(
    r"(?i)\b(?:pleurx|aspira|ipc|indwelling\s+pleural\s+catheter|tunneled\s+pleural\s+catheter|tunnelled\s+pleural\s+catheter)\b"
)
_CHEST_TUBE_TARGET_RE = re.compile(r"(?i)\b(?:chest\s+tube|tube\s+thoracostomy|pigtail|wayne)\b")
_PLEURAL_REMOVAL_RE = re.compile(
    r"(?i)\b(?:removed intact|catheter removed|removal today|cuff dissected free|d/?c chest tube|chest tube removed|removal of .*chest tube|pleurx removal|indwelling pleural catheter removal|exchange(?:d)? over a wire|catheter exchanged)\b"
)
_PLEURAL_INSERTION_RE = re.compile(
    r"(?i)\b(?:placed|inserted|placement|new catheter inserted|new chest tube placed)\b"
)
_BLVR_REMOVAL_RE = re.compile(r"(?i)\b(?:valve removal|valves? removed|removed \d+ .* valves?|remove(?:d)? .*valves?)\b")
_BLVR_EXCHANGE_RE = re.compile(r"(?i)\b(?:exchange|exchanged|replaced with|removed .* and replaced)\b")
_BLVR_PLACEMENT_RE = re.compile(r"(?i)\b(?:valves? (?:placed|deployed|inserted)|placed .* valves?|deployed .* valves?)\b")
_THERMAL_ACTION_RE = re.compile(r"(?i)\b(?:ablat(?:ed|ion)|destruct(?:ion|ed)|coagulat(?:ed|ion)|treated)\b")
_CAO_NEGATED_RE = re.compile(
    r"(?i)\b(?:not used|were not used|no tumou?r debulking|no tumou?r destruction|no ablation|no resection|not performed)\b"
)

EVIDENCE_REQUIRED: dict[str, str] = {
    # HARD: flip performed=false when unsupported
    "procedures_performed.airway_dilation.performed": "HARD",
    "procedures_performed.bal.performed": "HARD",
    "procedures_performed.peripheral_tbna.performed": "HARD",
    "procedures_performed.transbronchial_cryobiopsy.performed": "HARD",
    "procedures_performed.mechanical_debulking.performed": "HARD",
    "procedures_performed.cryotherapy.performed": "HARD",
    "procedures_performed.thermal_ablation.performed": "HARD",
    "pleural_procedures.chest_tube.performed": "HARD",
    "pleural_procedures.ipc.performed": "HARD",
    # airway_stent is HARD only when not "Assessment only"
    "procedures_performed.airway_stent.performed": "HARD",
    # REVIEW: keep but require manual review
    "procedures_performed.rigid_bronchoscopy.performed": "REVIEW",
}


@dataclass(frozen=True)
class NoteLine:
    start: int
    end: int
    text: str
    section: str


@dataclass(frozen=True)
class TypedEvidenceSupport:
    text: str
    start: int
    end: int
    line_text: str
    section: str
    source_type: Literal[
        "narrative_procedure",
        "findings",
        "impression",
        "template_checkbox",
        "menu_or_code_block",
        "history_or_plan",
        "device_status_only",
        "header_or_metadata",
    ]


def normalize_text(text: str) -> str:
    """Normalize text for robust substring matching.

    - lowercase
    - remove punctuation (keep a-z, 0-9)
    - collapse whitespace to single spaces
    """
    lowered = (text or "").lower()
    no_punct = _NON_ALNUM_RE.sub(" ", lowered)
    collapsed = _WS_RE.sub(" ", no_punct).strip()
    return collapsed


def verify_registry(registry: IPRegistryV3, full_source_text: str) -> IPRegistryV3:
    """Verify and anchor event evidence quotes against the full source note text.

    For each procedure event, attempt to:
    1) Anchor the quote to exact offsets in the note text (preferred), updating
       `evidence.quote` to the exact substring from the note and populating
       `evidence.start/end`.
    2) Fall back to normalized containment verification when offsets cannot be
       determined, clearing any pre-filled offsets to avoid misleading spans.

    Events whose evidence quote cannot be verified are dropped.
    """

    from app.evidence.quote_anchor import anchor_quote
    from app.registry.schema.ip_v3_extraction import EvidenceSpan

    full_text = full_source_text or ""
    normalized_source = normalize_text(full_text)

    kept: list[ProcedureEvent] = []
    for event in registry.procedures:
        evidence = getattr(event, "evidence", None)
        quote = getattr(evidence, "quote", None) if evidence is not None else None
        quote_clean = (str(quote) if quote is not None else "").strip()
        if not quote_clean:
            continue

        anchored = anchor_quote(full_text, quote_clean)
        if anchored.span is not None:
            updated = event.model_copy(deep=True)
            if updated.evidence is None:
                updated.evidence = EvidenceSpan(
                    quote=anchored.span.text,
                    start=anchored.span.start,
                    end=anchored.span.end,
                )
            else:
                updated.evidence.quote = anchored.span.text
                updated.evidence.start = anchored.span.start
                updated.evidence.end = anchored.span.end
            kept.append(updated)
            continue

        normalized_quote = normalize_text(quote_clean)
        if normalized_quote and normalized_quote in normalized_source:
            updated = event.model_copy(deep=True)
            if updated.evidence is not None:
                updated.evidence.start = None
                updated.evidence.end = None
            kept.append(updated)

    return registry.model_copy(update={"procedures": kept})


def _normalized_contains(haystack: str, needle: str) -> bool:
    if not haystack or not needle:
        return False
    return normalize_text(needle) in normalize_text(haystack)


def _verify_quote_in_text(quote: str, full_text: str, *, fuzzy_threshold: int = 85) -> bool:
    quote_clean = (quote or "").strip()
    if not quote_clean:
        return False
    if quote_clean in (full_text or ""):
        return True
    lowered_quote = quote_clean.lower()
    lowered_text = (full_text or "").lower()
    if lowered_quote in lowered_text:
        return True
    if _normalized_contains(full_text or "", quote_clean):
        return True

    normalized_quote = normalize_text(quote_clean)
    if len(normalized_quote) < 12:
        return False

    score = partial_ratio(normalized_quote, normalize_text(full_text or ""))
    return score >= fuzzy_threshold


def _normalize_section_name(raw: str) -> str:
    value = re.sub(r"\s+", " ", str(raw or "").strip().lower())
    return value.rstrip(":")


def _build_note_lines(full_text: str) -> list[NoteLine]:
    lines: list[NoteLine] = []
    current_section = ""
    offset = 0
    for raw_line in (full_text or "").splitlines(keepends=True):
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        line_section = current_section
        inline = _SECTION_INLINE_RE.match(line)
        if inline:
            candidate = _normalize_section_name(inline.group(1))
            if candidate in (
                _NARRATIVE_SECTIONS
                | _FINDINGS_SECTIONS
                | _IMPRESSION_SECTIONS
                | _HISTORY_PLAN_SECTIONS
                | _HEADER_METADATA_SECTIONS
            ):
                current_section = candidate
                line_section = candidate
        else:
            header = _SECTION_ONLY_RE.match(line)
            if header:
                candidate = _normalize_section_name(header.group(1))
                current_section = candidate
                line_section = candidate
        lines.append(NoteLine(start=offset, end=offset + len(line), text=line, section=line_section))
        offset += len(raw_line)
    return lines


def _line_for_pos(lines: list[NoteLine], pos: int) -> NoteLine | None:
    for line in lines:
        if line.start <= pos <= line.end:
            return line
    return lines[-1] if lines else None


def _locate_quote(full_text: str, quote: str) -> tuple[int, int] | None:
    needle = str(quote or "").strip()
    if not needle:
        return None
    idx = (full_text or "").find(needle)
    if idx >= 0:
        return idx, idx + len(needle)
    lowered_text = (full_text or "").lower()
    lowered_quote = needle.lower()
    idx = lowered_text.find(lowered_quote)
    if idx >= 0:
        return idx, idx + len(needle)
    return None


def _classify_source_type(line: NoteLine | None) -> Literal[
    "narrative_procedure",
    "findings",
    "impression",
    "template_checkbox",
    "menu_or_code_block",
    "history_or_plan",
    "device_status_only",
    "header_or_metadata",
]:
    if line is None:
        return "header_or_metadata"
    line_text = line.text.strip()
    lower = line_text.lower()
    section = _normalize_section_name(line.section)
    if _CHECKBOX_RE.search(line_text):
        return "template_checkbox"
    if _STATUS_ONLY_STENT_RE.search(line_text):
        return "device_status_only"
    if section in _HISTORY_PLAN_SECTIONS or re.search(r"(?i)\b(?:history of|plan to|planned|possible|prior|previously)\b", line_text):
        return "history_or_plan"
    if section in _IMPRESSION_SECTIONS:
        return "impression"
    if section in _FINDINGS_SECTIONS:
        return "findings"
    if (
        section in _HEADER_METADATA_SECTIONS
        or _CPT_RE.search(line_text)
        or "\t" in line_text
        or lower.startswith(("* ", "- ", "0-", "1 "))
    ):
        if section in {"procedure", "procedures", "procedure(s)"} and re.search(r"(?i)\boptional\b", line_text):
            return "menu_or_code_block"
        if section in _NARRATIVE_SECTIONS:
            return "narrative_procedure"
        return "menu_or_code_block" if section in {"procedure", "procedures", "procedure(s)"} else "header_or_metadata"
    if section in _NARRATIVE_SECTIONS:
        return "narrative_procedure"
    if section in _HEADER_METADATA_SECTIONS:
        return "header_or_metadata"
    return "narrative_procedure"


def _typed_support_from_span(full_text: str, lines: list[NoteLine], text: str, start: int, end: int) -> TypedEvidenceSupport:
    line = _line_for_pos(lines, start)
    return TypedEvidenceSupport(
        text=text,
        start=start,
        end=end,
        line_text=(line.text.strip() if line else text.strip()),
        section=(line.section if line else ""),
        source_type=_classify_source_type(line),
    )


def _collect_typed_supports(
    record: RegistryRecord,
    full_text: str,
    field_path: str,
    prefixes: list[str],
    anchor_patterns: list[str],
) -> list[TypedEvidenceSupport]:
    lines = _build_note_lines(full_text)
    supports: list[TypedEvidenceSupport] = []
    seen: set[tuple[int, int, str]] = set()

    for prefix in prefixes:
        evidence = getattr(record, "evidence", None) or {}
        spans = evidence.get(prefix) if isinstance(evidence, dict) else None
        if not isinstance(spans, list):
            continue
        for span in spans:
            if not isinstance(span, Span):
                continue
            text = (span.text or "").strip()
            if not text:
                continue
            start = int(span.start) if span.start is not None else None
            end = int(span.end) if span.end is not None else None
            if start is None or end is None:
                located = _locate_quote(full_text, text)
                if located is None:
                    continue
                start, end = located
            key = (start, end, text)
            if key in seen:
                continue
            seen.add(key)
            supports.append(_typed_support_from_span(full_text, lines, text, start, end))

    for pattern in anchor_patterns:
        for match in re.finditer(pattern, full_text or "", re.IGNORECASE):
            text = (match.group(0) or "").strip()
            if not text:
                continue
            key = (int(match.start()), int(match.end()), text)
            if key in seen:
                continue
            seen.add(key)
            supports.append(
                _typed_support_from_span(
                    full_text,
                    lines,
                    text,
                    int(match.start()),
                    int(match.end()),
                )
            )

    supports.sort(key=lambda item: (item.start, item.end, item.text))
    return supports


def _first_allowed_support(
    supports: list[TypedEvidenceSupport],
    validator: Callable[[TypedEvidenceSupport], bool] | None = None,
) -> TypedEvidenceSupport | None:
    for support in supports:
        if support.source_type in _DISALLOWED_CPT_SOURCE_TYPES:
            continue
        if validator is not None and not validator(support):
            continue
        return support
    return None


def _disallowed_source_warning(field_path: str, supports: list[TypedEvidenceSupport]) -> str | None:
    source_types = {support.source_type for support in supports}
    if "template_checkbox" in source_types:
        return f"SUPPRESSION_TEMPLATE_CHECKBOX: {field_path}"
    if "device_status_only" in source_types:
        return f"SUPPRESSION_DEVICE_STATUS_ONLY: {field_path}"
    if {"menu_or_code_block", "header_or_metadata"} & source_types:
        return f"SUPPRESSION_MENU_HEADER_LEAKAGE: {field_path}"
    if "history_or_plan" in source_types:
        return f"SUPPRESSION_HISTORY_PLAN_LEAKAGE: {field_path}"
    if "impression" in source_types:
        return f"SUPPRESSION_IMPRESSION_ONLY: {field_path}"
    return None


def _append_unique_warning(warnings: list[str], text: str) -> None:
    if text not in warnings:
        warnings.append(text)


def _evidence_texts_for_prefix(record: RegistryRecord, prefix: str) -> list[str]:
    evidence = getattr(record, "evidence", None) or {}
    if not isinstance(evidence, dict):
        return []

    texts: list[str] = []
    for key, spans in evidence.items():
        if not isinstance(key, str) or not key:
            continue
        if key != prefix and not key.startswith(prefix + "."):
            continue
        if not isinstance(spans, list):
            continue
        for span in spans:
            if not isinstance(span, Span):
                continue
            text = (span.text or "").strip()
            if text:
                texts.append(text)
    return texts


def _drop_evidence_prefix(record: RegistryRecord, prefix: str) -> None:
    evidence = getattr(record, "evidence", None)
    if not isinstance(evidence, dict) or not evidence:
        return
    to_drop = [k for k in evidence.keys() if isinstance(k, str) and (k == prefix or k.startswith(prefix + "."))]
    for key in to_drop:
        evidence.pop(key, None)


def _add_first_anchor_span(record: RegistryRecord, field_path: str, full_text: str, patterns: list[str]) -> bool:
    if not full_text or not patterns:
        return False
    for pat in patterns:
        match = re.search(pat, full_text, re.IGNORECASE)
        if not match:
            continue
        anchor_text = (match.group(0) or "").strip()
        if not anchor_text:
            continue
        record.evidence.setdefault(field_path, []).append(
            Span(
                text=anchor_text,
                start=int(match.start()),
                end=int(match.end()),
                confidence=0.9,
            )
        )
        return True
    return False


def _wipe_model_fields(obj: object, wipe_fields: dict[str, object]) -> None:
    if obj is None:
        return
    for name, value in wipe_fields.items():
        if hasattr(obj, name):
            setattr(obj, name, value)


def _find_therapeutic_aspiration_anchor(full_text: str) -> tuple[str, int, int] | None:
    text_lower = (full_text or "").lower()
    if not text_lower:
        return None

    def _match_negated(match: re.Match[str]) -> bool:
        start, end = match.start(), match.end()
        before = full_text[max(0, start - 30) : start]
        after = full_text[end : min(len(full_text), end + 80)]

        if re.search(r"(?i)\b(?:no|without)\b[^.\n]{0,20}$", before):
            return True

        if re.search(
            r"(?i)\b(?:not\s+(?:performed|done|attempted)|was\s+not\s+performed|declined|deferred|aborted)\b",
            after,
        ):
            return True

        return False

    for pattern in THERAPEUTIC_ASPIRATION_PATTERNS:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if not match:
            continue
        if _match_negated(match):
            continue
        return (match.group(0).strip(), match.start(), match.end())

    contextual_patterns = [
        r"\b(?:copious|large\s+amount\s+of|thick|tenacious|purulent|bloody|blood-tinged)\s+secretions?\b[^.]{0,80}\b(?:suction(?:ed|ing)|aspirat(?:ed|ion)|cleared|remov(?:ed|al))\b",
        r"\b(?:suction(?:ed|ing)|aspirat(?:ed|ion)|cleared|remov(?:ed|al))\b[^.]{0,80}\b(?:copious|large\s+amount\s+of|thick|tenacious|purulent|bloody|blood-tinged)\s+secretions?\b",
        r"\b(?:suction(?:ed|ing)|aspirat(?:ed|ion)|cleared|remov(?:ed|al))\b[^.]{0,80}\b(?:mucus\s+plug|clot|blood)\b",
        r"\b(?:mucus|mucous|secretions?|blood|clot(?:s)?|debris|fluid|plug(?:s)?)\b[^.]{0,80}\b(?:suction(?:ed|ing)?|aspirat(?:ed|ion|ing)?|clear(?:ed|ing)?)\b",
        r"\b(?:suction(?:ed|ing)?|aspirat(?:ed|ion|ing)?|clear(?:ed|ing)?)\b[^.]{0,80}\b(?:mucus|mucous|secretions?|blood|clot(?:s)?|debris|fluid|plug(?:s)?)\b",
        r"\b(?:airway|airways|trachea|bronch(?:us|i)?|tracheobronchial\s+tree)\b[^.]{0,120}\b(?:suction(?:ed|ing)?|aspirat(?:ed|ion|ing)?|clear(?:ed|ing)?)\b",
        r"\b(?:suction(?:ed|ing)?|aspirat(?:ed|ion|ing)?|clear(?:ed|ing)?)\b[^.]{0,120}\b(?:airway|airways|trachea|bronch(?:us|i)?|tracheobronchial\s+tree)\b",
    ]
    contextual_patterns.extend(
        [
            r"\bsecretions?\b[^.]{0,120}\b(?:suction(?:ed|ing)?|aspirat(?:ed|ion|ing)?|clear(?:ed|ing)?)\b",
            r"\b(?:suction(?:ed|ing)?|aspirat(?:ed|ion|ing)?|clear(?:ed|ing)?)\b[^.]{0,120}\bsecretions?\b",
        ]
    )

    for pattern in contextual_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if not match:
            continue
        if _match_negated(match):
            continue
        return (match.group(0).strip(), match.start(), match.end())

    return None


def _stent_is_negated(full_text: str) -> bool:
    """Return True when stent mentions are explicitly negated (not performed)."""
    text = full_text or ""
    if not text:
        return False

    for match in _STENT_TOKEN_RE.finditer(text):
        start = max(0, match.start() - 220)
        end = min(len(text), match.end() + 220)
        window = text[start:end]
        if _STENT_NEGATION_WINDOW_RE.search(window):
            return True

    return False


def _supports_bal_action(support: TypedEvidenceSupport) -> bool:
    line = support.line_text or support.text
    return bool(_BAL_ACTION_RE.search(line)) and not _WLL_RE.search(line)


def _supports_peripheral_tbna_action(support: TypedEvidenceSupport) -> bool:
    line = support.line_text or support.text
    return bool(_TBNA_ACTION_RE.search(line) and _PERIPHERAL_TARGET_RE.search(line))


def _supports_cryobiopsy_action(support: TypedEvidenceSupport) -> bool:
    line = support.line_text or support.text
    return bool(
        _CRYO_ACTION_RE.search(line)
        and (_CRYO_OBTAINED_RE.search(line) or _CRYO_SAMPLE_COUNT_RE.search(line))
        and not _CRYO_NEGATED_RE.search(line)
    )


def _supports_cao_action(support: TypedEvidenceSupport) -> bool:
    line = support.line_text or support.text
    return bool(
        _CAO_ACTION_RE.search(line)
        and not _CAO_NEGATED_RE.search(line)
        and (_CAO_TARGET_RE.search(line) or _TOOL_ONLY_RE.search(line))
    )


def _supports_stent_action(support: TypedEvidenceSupport) -> bool:
    line = support.line_text or support.text
    return bool(_STENT_ACTION_RE.search(line))


def _supports_ipc_action(support: TypedEvidenceSupport) -> bool:
    line = support.line_text or support.text
    return bool(_IPC_TARGET_RE.search(line) and (_PLEURAL_INSERTION_RE.search(line) or _PLEURAL_REMOVAL_RE.search(line)))


def _supports_chest_tube_action(support: TypedEvidenceSupport) -> bool:
    line = support.line_text or support.text
    return bool(_CHEST_TUBE_TARGET_RE.search(line) and _PLEURAL_INSERTION_RE.search(line))


def verify_evidence_integrity(record: RegistryRecord, full_note_text: str) -> tuple[RegistryRecord, list[str]]:
    """Apply Python-side guardrails against hallucinated performed events/details.

    This is intentionally conservative: if a high-risk performed=true procedure
    cannot be supported by extractable evidence, it is flipped to performed=false
    and dependent details are wiped.
    """

    warnings: list[str] = []
    full_text = full_note_text or ""

    procedures = getattr(record, "procedures_performed", None)
    pleural = getattr(record, "pleural_procedures", None)
    if procedures is None:
        return record, warnings

    def _prefixes_for(field_path: str) -> list[str]:
        return [field_path, field_path.rsplit(".", 1)[0]]

    def _drop_prefixes(field_path: str) -> None:
        for prefix in _prefixes_for(field_path):
            _drop_evidence_prefix(record, prefix)

    def _typed_supports(field_path: str, anchor_patterns: list[str]) -> list[TypedEvidenceSupport]:
        return _collect_typed_supports(
            record,
            full_text,
            field_path,
            _prefixes_for(field_path),
            anchor_patterns,
        )

    def _hard_suppress(
        *,
        field_path: str,
        obj: object,
        suppression_warning: str,
        wipe_fields: dict[str, object] | None = None,
    ) -> None:
        if obj is None:
            return
        setattr(obj, "performed", False)
        if wipe_fields:
            _wipe_model_fields(obj, wipe_fields)
        _drop_prefixes(field_path)
        _append_unique_warning(warnings, suppression_warning)
        _append_unique_warning(warnings, f"EVIDENCE_HARD_FAIL: {field_path}")

    # ------------------------------------------------------------------
    # High-risk: therapeutic aspiration (frequent false-positives)
    # ------------------------------------------------------------------
    ta = getattr(procedures, "therapeutic_aspiration", None)
    if getattr(ta, "performed", None) is True:
        prefixes = [
            "procedures_performed.therapeutic_aspiration",
            "therapeutic_aspiration",
        ]
        candidate_quotes: list[str] = []
        for prefix in prefixes:
            candidate_quotes.extend(_evidence_texts_for_prefix(record, prefix))

        verified = any(_verify_quote_in_text(q, full_text) for q in candidate_quotes)
        if not verified:
            anchor = _find_therapeutic_aspiration_anchor(full_text)
            if anchor is not None:
                anchor_text, start, end = anchor
                record.evidence.setdefault("procedures_performed.therapeutic_aspiration.performed", []).append(
                    Span(text=anchor_text, start=start, end=end)
                )
                verified = True

        if not verified:
            setattr(ta, "performed", False)
            for dependent_field in ("material", "location"):
                if hasattr(ta, dependent_field):
                    setattr(ta, dependent_field, None)
            for prefix in prefixes:
                _drop_evidence_prefix(record, prefix)
            warnings.append("WIPED_VERIFICATION_FAILED: procedures_performed.therapeutic_aspiration")

    # ------------------------------------------------------------------
    # High-risk: hallucinated percutaneous trach device name (e.g., Portex)
    # ------------------------------------------------------------------
    trach = getattr(procedures, "percutaneous_tracheostomy", None)
    device_name = getattr(trach, "device_name", None)
    if isinstance(device_name, str) and device_name.strip():
        if not _normalized_contains(full_text, device_name):
            setattr(trach, "device_name", None)
            warnings.append("WIPED_DEVICE_NAME_NOT_IN_TEXT: procedures_performed.percutaneous_tracheostomy.device_name")

    bal = getattr(procedures, "bal", None)
    peripheral_tbna = getattr(procedures, "peripheral_tbna", None)
    cryobiopsy = getattr(procedures, "transbronchial_cryobiopsy", None)
    mechanical_debulking = getattr(procedures, "mechanical_debulking", None)
    cryotherapy = getattr(procedures, "cryotherapy", None)
    thermal_ablation = getattr(procedures, "thermal_ablation", None)
    blvr = getattr(procedures, "blvr", None)
    stent = getattr(procedures, "airway_stent", None)
    rigid = getattr(procedures, "rigid_bronchoscopy", None)
    airway_dilation = getattr(procedures, "airway_dilation", None)
    chest_tube = getattr(pleural, "chest_tube", None) if pleural is not None else None
    ipc = getattr(pleural, "ipc", None) if pleural is not None else None

    # ------------------------------------------------------------------
    # High-risk: airway stent false positives (keyword present but explicitly not performed)
    # ------------------------------------------------------------------
    if getattr(stent, "performed", None) is True:
        seed = extract_airway_stent(full_text) if full_text.strip() else {}
        action_supported = bool(seed.get("airway_stent", {}).get("performed") is True)
        if not action_supported and _stent_is_negated(full_text):
            setattr(stent, "performed", False)
            wipe_fields = {
                "action": None,
                "stent_type": None,
                "stent_brand": None,
                "diameter_mm": None,
                "length_mm": None,
                "location": None,
                "indication": None,
                "deployment_successful": None,
                "airway_stent_removal": False,
            }
            for field_name, value in wipe_fields.items():
                if hasattr(stent, field_name):
                    setattr(stent, field_name, value)
            _drop_prefixes("procedures_performed.airway_stent.performed")
            warnings.append("NEGATION_GUARD: procedures_performed.airway_stent")

    # ------------------------------------------------------------------
    # Targeted source-typed suppressions / downgrades
    # ------------------------------------------------------------------
    if getattr(stent, "performed", None) is True:
        stent_supports = _typed_supports(
            "procedures_performed.airway_stent.performed",
            [r"\bairway\s+stent\b", r"\bstent\b"],
        )
        if _first_allowed_support(stent_supports, validator=_supports_stent_action) is None and any(
            support.source_type == "device_status_only" or _STATUS_ONLY_STENT_RE.search(support.line_text or support.text)
            for support in stent_supports
        ):
            if hasattr(stent, "action"):
                setattr(stent, "action", "Assessment only")
            if hasattr(stent, "action_type"):
                setattr(stent, "action_type", "assessment_only")
            if hasattr(stent, "airway_stent_removal"):
                setattr(stent, "airway_stent_removal", False)
            if hasattr(stent, "deployment_successful"):
                setattr(stent, "deployment_successful", None)
            _append_unique_warning(warnings, "SUPPRESSION_DEVICE_STATUS_ONLY: procedures_performed.airway_stent.performed")
            _append_unique_warning(
                warnings,
                "AUTO_CORRECTED: airway_stent downgraded to Assessment only due to device status-only evidence.",
            )

    if getattr(peripheral_tbna, "performed", None) is True:
        tbna_supports = _typed_supports(
            "procedures_performed.peripheral_tbna.performed",
            [r"\b(?:tbna|fna|needle\s+aspirat(?:e|ion)|passes?|sampled)\b"],
        )
        if _first_allowed_support(tbna_supports, validator=_supports_peripheral_tbna_action) is None:
            nodal_only = any(
                _TBNA_ACTION_RE.search(support.line_text or support.text)
                and (
                    _EBUS_STATION_RE.search(support.line_text or support.text)
                    or _LINEAR_EBUS_RE.search(support.line_text or support.text)
                )
                for support in tbna_supports
            ) or bool((_EBUS_STATION_RE.search(full_text) or _LINEAR_EBUS_RE.search(full_text)) and _TBNA_ACTION_RE.search(full_text))
            if nodal_only:
                _hard_suppress(
                    field_path="procedures_performed.peripheral_tbna.performed",
                    obj=peripheral_tbna,
                    suppression_warning="SUPPRESSION_EBUS_TBNA_CONTAMINATION: procedures_performed.peripheral_tbna.performed",
                    wipe_fields={
                        "targets_sampled": None,
                        "needle_gauge": None,
                        "passes_per_station": None,
                        "passes_per_target": None,
                        "location": None,
                    },
                )

    if getattr(bal, "performed", None) is True:
        bal_supports = _typed_supports(
            "procedures_performed.bal.performed",
            [r"\b(?:bronchoalveolar\s+lavage|bal)\b", r"\bwhole\s+lung\s+lavage\b", r"\bwll\b"],
        )
        if _first_allowed_support(bal_supports, validator=_supports_bal_action) is None and _WLL_RE.search(full_text):
            _hard_suppress(
                field_path="procedures_performed.bal.performed",
                obj=bal,
                suppression_warning="SUPPRESSION_WLL_NOT_BAL: procedures_performed.bal.performed",
                wipe_fields={
                    "location": None,
                    "volume_instilled_ml": None,
                    "return_volume_ml": None,
                },
            )

    if getattr(cryobiopsy, "performed", None) is True:
        cryo_supports = _typed_supports(
            "procedures_performed.transbronchial_cryobiopsy.performed",
            [r"\b(?:transbronchial\s+cryobiops(?:y|ies)|cryobiops(?:y|ies)|cryoprobe|freeze\s+time)\b"],
        )
        if _first_allowed_support(cryo_supports, validator=_supports_cryobiopsy_action) is None:
            forceps_context = any(_FORCEPS_BIOPSY_RE.search(support.line_text or support.text) for support in cryo_supports) or bool(
                _FORCEPS_BIOPSY_RE.search(full_text)
            )
            if forceps_context:
                _hard_suppress(
                    field_path="procedures_performed.transbronchial_cryobiopsy.performed",
                    obj=cryobiopsy,
                    suppression_warning=(
                        "SUPPRESSION_CRYO_FORCEPS_DISAMBIGUATION: "
                        "procedures_performed.transbronchial_cryobiopsy.performed"
                    ),
                    wipe_fields={
                        "locations_biopsied": None,
                        "probe_size_mm": None,
                        "freeze_time_seconds": None,
                        "number_of_biopsies": None,
                    },
                )

    for field_path, obj, anchor_patterns, wipe_fields in (
        (
            "procedures_performed.mechanical_debulking.performed",
            mechanical_debulking,
            [r"\b(?:mechanical\s+debulking|debulk(?:ed|ing)?|rigid\s+coring)\b", r"\b(?:snare|forceps)\b"],
            {"location": None, "indication": None},
        ),
        (
            "procedures_performed.cryotherapy.performed",
            cryotherapy,
            [r"\b(?:cryotherap\w*|cryoextraction|cryodebridement|cryoprobe)\b"],
            {"location": None, "indication": None},
        ),
        (
            "procedures_performed.thermal_ablation.performed",
            thermal_ablation,
            [r"\b(?:apc|argon\s+plasma\s+coagulation|laser|electrocautery)\b", r"\b(?:ablat(?:ed|ion)|destruct(?:ion|ed))\b"],
            {"location": None, "indication": None, "modality": None},
        ),
    ):
        if getattr(obj, "performed", None) is not True:
            continue
        cao_supports = _typed_supports(field_path, anchor_patterns)
        if _first_allowed_support(cao_supports, validator=_supports_cao_action) is not None:
            continue
        tool_only_context = any(_TOOL_ONLY_RE.search(support.line_text or support.text) for support in cao_supports) or bool(
            _TOOL_ONLY_RE.search(full_text)
        )
        if tool_only_context or _CAO_NEGATED_RE.search(full_text):
            _hard_suppress(
                field_path=field_path,
                obj=obj,
                suppression_warning=f"SUPPRESSION_TOOL_WITHOUT_ACTION: {field_path}",
                wipe_fields=wipe_fields,
            )

    if getattr(chest_tube, "performed", None) is True:
        if _PLEURAL_REMOVAL_RE.search(full_text) and not _PLEURAL_INSERTION_RE.search(full_text):
            _hard_suppress(
                field_path="pleural_procedures.chest_tube.performed",
                obj=chest_tube,
                suppression_warning="SUPPRESSION_PLEURAL_REMOVAL_INVERSION: pleural_procedures.chest_tube.performed",
                wipe_fields={
                    "action": None,
                    "side": None,
                    "indication": None,
                    "tube_type": None,
                    "tube_size_fr": None,
                    "guidance": None,
                },
            )

    if getattr(ipc, "performed", None) is True:
        if _PLEURAL_REMOVAL_RE.search(full_text) and not _PLEURAL_INSERTION_RE.search(full_text):
            _append_unique_warning(warnings, "SUPPRESSION_PLEURAL_REMOVAL_INVERSION: pleural_procedures.ipc.performed")
            prior_action = str(getattr(ipc, "action", "") or "").strip()
            if hasattr(ipc, "action"):
                setattr(ipc, "action", "Removal")

    if getattr(blvr, "performed", None) is True:
        has_blvr_removal = bool(_BLVR_REMOVAL_RE.search(full_text))
        has_blvr_exchange = bool(_BLVR_EXCHANGE_RE.search(full_text))
        has_blvr_placement = bool(_BLVR_PLACEMENT_RE.search(full_text))
        if has_blvr_removal:
            prior_type = str(getattr(blvr, "procedure_type", "") or "").strip()
            if hasattr(blvr, "procedure_type"):
                setattr(blvr, "procedure_type", "Valve removal")
            if prior_type != "Valve removal":
                _append_unique_warning(warnings, "SUPPRESSION_BLVR_EXCHANGE_NOT_INITIAL: procedures_performed.blvr.procedure_type")
        if has_blvr_exchange and has_blvr_removal:
            _append_unique_warning(warnings, "NEEDS_REVIEW: BLVR_EXCHANGE_AMBIGUOUS: procedures_performed.blvr.procedure_type")

    # ------------------------------------------------------------------
    # Evidence-required enforcement (HARD vs REVIEW)
    # ------------------------------------------------------------------
    def _enforce_boolean(
        *,
        field_path: str,
        obj: object,
        policy: str,
        anchor_patterns: list[str],
        validator: Callable[[TypedEvidenceSupport], bool] | None = None,
        wipe_fields: dict[str, object] | None = None,
        skip_if: bool = False,
    ) -> None:
        nonlocal warnings
        if skip_if:
            return
        if obj is None or not hasattr(obj, "performed"):
            return
        if getattr(obj, "performed", None) is not True:
            return

        supports = _typed_supports(field_path, anchor_patterns)
        verified = _first_allowed_support(supports, validator=validator) is not None

        if not verified and field_path == "pleural_procedures.ipc.performed":
            ipc_header_fallback = bool(
                re.search(r"(?is)\bprocedure\s*:\s*[^\n]{0,240}\b32552\b", full_text)
                or re.search(r"(?i)\b32552\b", full_text)
                or re.search(r"(?i)\bRemoval\s+of\s+indwelling\s+tunneled\s+pleural\s+catheter\b", full_text)
            )
            if ipc_header_fallback:
                verified = True
                if hasattr(obj, "action") and not str(getattr(obj, "action", "") or "").strip():
                    setattr(obj, "action", "Removal")
                _add_first_anchor_span(
                    record,
                    field_path,
                    full_text,
                    [
                        r"(?i)\bRemoval\s+of\s+indwelling\s+tunneled\s+pleural\s+catheter\b",
                        r"(?i)\b32552\b",
                    ],
                )

        if verified:
            return

        suppression_warning = _disallowed_source_warning(field_path, supports)
        if suppression_warning:
            _append_unique_warning(warnings, suppression_warning)
            if suppression_warning == f"SUPPRESSION_TEMPLATE_CHECKBOX: {field_path}":
                _append_unique_warning(warnings, f"CHECKBOX_NEGATIVE: forcing {field_path}=false")

        if policy == "REVIEW":
            _append_unique_warning(warnings, f"NEEDS_REVIEW: EVIDENCE_MISSING: {field_path}")
            return

        setattr(obj, "performed", False)
        if wipe_fields:
            _wipe_model_fields(obj, wipe_fields)
        _drop_prefixes(field_path)
        _append_unique_warning(warnings, f"EVIDENCE_HARD_FAIL: {field_path}")

    _enforce_boolean(
        field_path="procedures_performed.airway_dilation.performed",
        obj=airway_dilation,
        policy=EVIDENCE_REQUIRED["procedures_performed.airway_dilation.performed"],
        anchor_patterns=AIRWAY_DILATION_PATTERNS,
        wipe_fields={
            "location": None,
            "etiology": None,
            "method": None,
            "balloon_diameter_mm": None,
            "pre_dilation_diameter_mm": None,
            "post_dilation_diameter_mm": None,
        },
    )
    _enforce_boolean(
        field_path="procedures_performed.bal.performed",
        obj=bal,
        policy=EVIDENCE_REQUIRED["procedures_performed.bal.performed"],
        anchor_patterns=[r"\b(?:bronchoalveolar\s+lavage|bal)\b", r"\bwhole\s+lung\s+lavage\b", r"\bwll\b"],
        validator=_supports_bal_action,
        wipe_fields={
            "location": None,
            "volume_instilled_ml": None,
            "return_volume_ml": None,
        },
    )
    _enforce_boolean(
        field_path="procedures_performed.peripheral_tbna.performed",
        obj=peripheral_tbna,
        policy=EVIDENCE_REQUIRED["procedures_performed.peripheral_tbna.performed"],
        anchor_patterns=[r"\b(?:tbna|fna|needle\s+aspirat(?:e|ion)|passes?|sampled)\b"],
        validator=_supports_peripheral_tbna_action,
        wipe_fields={
            "targets_sampled": None,
            "needle_gauge": None,
            "passes_per_station": None,
            "passes_per_target": None,
            "location": None,
        },
    )
    _enforce_boolean(
        field_path="procedures_performed.transbronchial_cryobiopsy.performed",
        obj=cryobiopsy,
        policy=EVIDENCE_REQUIRED["procedures_performed.transbronchial_cryobiopsy.performed"],
        anchor_patterns=[r"\b(?:transbronchial\s+cryobiops(?:y|ies)|cryobiops(?:y|ies)|cryoprobe|freeze\s+time)\b"],
        validator=_supports_cryobiopsy_action,
        wipe_fields={
            "locations_biopsied": None,
            "probe_size_mm": None,
            "freeze_time_seconds": None,
            "number_of_biopsies": None,
        },
    )
    _enforce_boolean(
        field_path="procedures_performed.mechanical_debulking.performed",
        obj=mechanical_debulking,
        policy=EVIDENCE_REQUIRED["procedures_performed.mechanical_debulking.performed"],
        anchor_patterns=[r"\b(?:mechanical\s+debulking|debulk(?:ed|ing)?|rigid\s+coring)\b", r"\b(?:snare|forceps)\b"],
        validator=_supports_cao_action,
        wipe_fields={"location": None, "indication": None},
    )
    _enforce_boolean(
        field_path="procedures_performed.cryotherapy.performed",
        obj=cryotherapy,
        policy=EVIDENCE_REQUIRED["procedures_performed.cryotherapy.performed"],
        anchor_patterns=[r"\b(?:cryotherap\w*|cryoextraction|cryodebridement|cryoprobe)\b"],
        validator=_supports_cao_action,
        wipe_fields={"location": None, "indication": None},
    )
    _enforce_boolean(
        field_path="procedures_performed.thermal_ablation.performed",
        obj=thermal_ablation,
        policy=EVIDENCE_REQUIRED["procedures_performed.thermal_ablation.performed"],
        anchor_patterns=[r"\b(?:apc|argon\s+plasma\s+coagulation|laser|electrocautery)\b", r"\b(?:ablat(?:ed|ion)|destruct(?:ion|ed))\b"],
        validator=lambda support: bool(
            _THERMAL_ACTION_RE.search(support.line_text or support.text)
            and _CAO_TARGET_RE.search(support.line_text or support.text)
        ),
        wipe_fields={"location": None, "indication": None, "modality": None},
    )
    _enforce_boolean(
        field_path="pleural_procedures.chest_tube.performed",
        obj=chest_tube,
        policy=EVIDENCE_REQUIRED["pleural_procedures.chest_tube.performed"],
        anchor_patterns=CHEST_TUBE_PATTERNS,
        validator=_supports_chest_tube_action,
        wipe_fields={
            "action": None,
            "side": None,
            "indication": None,
            "tube_type": None,
            "tube_size_fr": None,
            "guidance": None,
        },
    )
    _enforce_boolean(
        field_path="pleural_procedures.ipc.performed",
        obj=ipc,
        policy=EVIDENCE_REQUIRED["pleural_procedures.ipc.performed"],
        anchor_patterns=IPC_PATTERNS,
        validator=_supports_ipc_action,
        wipe_fields={
            "action": None,
            "side": None,
            "catheter_brand": None,
            "indication": None,
            "tunneled": None,
        },
    )

    stent_action = str(getattr(stent, "action", "") or "").strip().lower() if stent is not None else ""
    stent_assessment_only = stent_action.startswith("assessment")
    _enforce_boolean(
        field_path="procedures_performed.airway_stent.performed",
        obj=stent,
        policy=EVIDENCE_REQUIRED["procedures_performed.airway_stent.performed"],
        anchor_patterns=[r"\bairway\s+stent\b", r"\bstent\b"],
        validator=_supports_stent_action,
        wipe_fields={
            "action": None,
            "stent_type": None,
            "stent_brand": None,
            "diameter_mm": None,
            "length_mm": None,
            "location": None,
            "indication": None,
            "deployment_successful": None,
            "airway_stent_removal": False,
        },
        skip_if=stent_assessment_only,
    )
    _enforce_boolean(
        field_path="procedures_performed.rigid_bronchoscopy.performed",
        obj=rigid,
        policy=EVIDENCE_REQUIRED["procedures_performed.rigid_bronchoscopy.performed"],
        anchor_patterns=RIGID_BRONCHOSCOPY_PATTERNS,
        wipe_fields={
            "rigid_scope_size": None,
            "indication": None,
            "jet_ventilation_used": None,
        },
    )

    return record, warnings


__all__ = ["normalize_text", "verify_registry", "verify_evidence_integrity"]
