"""Source-bearing, unlinked updates. Review supplies encounter-local target links."""

import re

from .aggregation.clinical.extract_clinical_update import extract_clinical_update_event
from .aggregation.pathology.extract_pathology import extract_pathology_event
from .focused import MODALITIES, prepare_text, segments


def evidence(request, start, end):
    return {
        "source_document_id": str(request.source_document_id),
        "source_digest": request.source_digest,
        "start": start,
        "end": end,
        "text": request.text[start:end],
        "confidence": 1.0,
    }


RESULT_NAME = (
    r"(?:(?:final|amended|corrected)\s+)?"
    r"(?:pathology|cytology|diagnosis|pathology\s+results?|cytology\s+results?|report)"
)
RESULT_PENDING = re.compile(
    rf"\b{RESULT_NAME}\s*:?[ \t]*(?:(?:is|are|remains?|was)\s+)?"
    r"(?:pending|awaited|not\s+(?:yet\s+)?(?:available|reported|finalized)|in\s+process)\b"
    rf"|\b(?:awaiting|pending)\s+(?:the\s+)?{RESULT_NAME}\b",
    re.I,
)
FINAL_RESULT = re.compile(
    r"\bfinal\s+(?:diagnosis|pathology|cytology)\s*"
    r"(?::|\b(?:showed|shows|demonstrated|demonstrates|is|was)\b)|"
    r"(?im:^\s*(?:final diagnosis|final pathology|final cytology)\s*$)",
    re.I,
)


def result_status(block, inherited=None):
    # Completion words within an explicitly pending result are not evidence that
    # the result exists. Pending molecular testing does not undo a final diagnosis.
    pending_only = re.match(
        r"\s*(?:(?:specimen\s+)?[A-Z][.) :]\s*)?(?:pending|awaiting)\b", block, re.I
    )
    if RESULT_PENDING.search(block) or pending_only:
        return "pending"
    # A negated amendment or a discussion of correction is not a result version.
    # Evaluate separate clauses so a negated prior amendment cannot suppress a
    # later explicit corrected diagnosis.
    for clause in re.split(r"[;\n.!?]|\b(?:but|however)\b", block, flags=re.I):
        amendment = re.search(
            r"\b(?:amended|corrected)\s+(?:final\s+)?(?:diagnosis|pathology|cytology|report|results?)\b"
            r"|\b(?:diagnosis|pathology|cytology|report|results?)\s+(?:(?:has been|was|is)\s+)?(?:amended|corrected)\b",
            clause, re.I,
        )
        if amendment and not re.search(r"\b(?:no|not|never|without)\b", clause[:amendment.end()], re.I):
            return "amended"
    if FINAL_RESULT.search(block):
        return "final"
    if re.search(r"pending|awaiting", block, re.I) and not inherited:
        return "pending"
    return inherited or "preliminary"


def pathology_update(request):
    text = prepare_text(request.text)
    # Preserve every specimen block and result version; never dedupe stations by latest text.
    headers = list(re.finditer(r"(?im)^\s*(?:specimen\s+)?([A-Z])[.) :]\s*(?=[A-Za-z])", text))
    boundaries = [m.start() for m in headers] if headers else [0]
    # Only document-level status before the first specimen may be inherited.
    # A final result in specimen A must not finalize specimen B.
    preamble = text[: boundaries[0]]
    inherited = result_status(preamble) if preamble.strip() else None
    if inherited == "preliminary":
        inherited = None
    candidates = []
    for i, start in enumerate(boundaries):
        end = boundaries[i + 1] if i + 1 < len(boundaries) else len(text)
        block = text[start:end]
        if not block.strip():
            continue
        observed = extract_pathology_event(block)
        status = result_status(block, inherited)
        # Ancillary-test adequacy cannot change the biopsy's diagnostic class.
        # Retain a clause when it explicitly also describes diagnostic adequacy.
        diagnostic = " ".join(
            sentence for _, _, sentence in segments(block)
            if not (
                re.search(r"\b(?:molecular|biomarker|NGS|PD-?L1|genomic)\b", sentence, re.I)
                and not re.search(r"\b(?:diagnosis|diagnostic|carcinoma|adenocarcinoma)\b", sentence, re.I)
            )
        )
        classification = None
        if re.search(r"non[- ]?diagnostic|insufficient", diagnostic, re.I):
            classification = "nondiagnostic"
        elif re.search(r"atypical|suspicious", diagnostic, re.I):
            classification = "atypical_or_suspicious"
        elif re.search(
            r"negative for malignan|no malignan|benign bronchial|macrophages", diagnostic, re.I
        ):
            classification = "nonspecific_benign"
        elif re.search(
            r"adenocarcinoma|squamous cell carcinoma|small cell carcinoma|positive for malignan",
            diagnostic,
            re.I,
        ):
            classification = "specific_malignant"
        elif re.search(r"granulomatous|hamartoma|organizing pneumonia", diagnostic, re.I):
            classification = "specific_benign"
        if status == "pending":
            classification = "pending"
        candidates.append(
            {
                "specimen_label": headers[i].group(1) if headers else None,
                "result_status": status,
                "index_result_class": classification,
                "diagnosis_text": block.strip()[:4096] if status != "pending" else None,
                "result_scope": None,
                "supersedes_pathology_result_id": None,
                "attribution_status": "requires_review",
                "observed_targets": observed,
                "evidence": evidence(request, start, min(end, start + 4096)),
            }
        )
    return {
        "unlinked_pathology": candidates,
        "review_requirements": [
            "specimen_target_attribution",
            "index_or_followup_scope",
            "amended_result_linkage",
        ],
        "extraction_version": "0.2.0",
    }


def imaging_update(request):
    candidates = []
    for start, end, sentence in segments(prepare_text(request.text)):
        if re.search(r"not (?:obtained|used|performed)|\bno (?:CBCT|radial EBUS)", sentence, re.I):
            continue
        found = [name for name, pattern in MODALITIES if re.search(pattern, sentence, re.I)]
        if any(m in {"fixed_CBCT", "mobile_CBCT"} for m in found):
            found = [m for m in found if m != "CBCT_unspecified"]
        if "augmented_fluoroscopy" in found:
            found = [m for m in found if m != "2D_fluoroscopy"]
        for modality in found:
            candidates.append(
                {
                    "localization_modality": modality,
                    "source_order": len(candidates) + 1,
                    "tool_lesion_relationship": None,
                    "evidence": evidence(request, start, min(end, start + 4096)),
                }
            )
    return {
        "unlinked_imaging": candidates,
        "review_requirements": [
            "target_attribution",
            "actual_sampling_tool_confirmation",
            "event_order_across_documents",
        ],
        "extraction_version": "0.2.0",
    }


SAFETY_EVENTS = {
    "hospital_admission": r"hospital\s+(?:admissions?|hospitalizations?)",
    "icu_admission": r"ICU\s+(?:admissions?|stays?)",
    "ed_visit": r"(?:emergency\s+department|ED)\s+visits?",
    "readmission": r"readmissions?",
}
SAFETY_LIST_ITEM = "(?:" + "|".join([
    *SAFETY_EVENTS.values(), r"(?:procedure[- ]related\s+)?complications?", r"mechanical\s+ventilation",
]) + ")"
NEGATIVE_SAFETY_LIST = re.compile(
    r"\b(?:no|without|denies|denied)\s+" + SAFETY_LIST_ITEM
    + r"(?:\s*(?:,\s*(?:(?:and|or)\s+)?|\s+(?:and|or)\s+)" + SAFETY_LIST_ITEM + r")*\b", re.I,
)


def reconcile_negative_safety_lists(text, raw):
    # The bounded upstream extractor has a short negation window. A coordinated
    # negative list can extend beyond it, producing an ICU false positive.
    # Mask only explicit lists of supported safety events, then check for an
    # affirmative event elsewhere before preserving the documented absence.
    masked, negatives = list(text), set()
    for match in NEGATIVE_SAFETY_LIST.finditer(text):
        negatives.update(key for key, pattern in SAFETY_EVENTS.items() if re.search(pattern, match.group(), re.I))
        masked[match.start():match.end()] = " " * (match.end() - match.start())
    if not negatives:
        return raw, []
    remaining = extract_clinical_update_event("".join(masked), update_type="follow_up", relative_day_offset=None)["clinical_update"]
    conflicts = []
    for key in sorted(negatives):
        if remaining.get(key) is True:
            raw[key] = None
            conflicts.append(key)
        else:
            raw[key] = False
    return raw, conflicts


def clinical_update(request):
    text = prepare_text(request.text)
    raw = extract_clinical_update_event(text, update_type="follow_up", relative_day_offset=None)[
        "clinical_update"
    ]
    raw, conflicts = reconcile_negative_safety_lists(text, raw)
    offset = re.search(
        r"\b(?:post[- ]procedure day|postoperative day|POD|day)\s*(\d+)\b", text, re.I
    )
    day = int(offset.group(1)) if offset else None
    if day is not None and day > 30:
        return {
            "clinical_update": {},
            "review_requirements": ["outside_launch_followup"],
            "extraction_version": "0.2.0",
        }
    allowed = (
        "hospital_admission",
        "icu_admission",
        "ed_visit",
        "readmission",
        "deceased",
        "complication_text",
    )
    values = {key: raw.get(key) for key in allowed}
    values.update(
        relative_day_offset=day,
        window="days_0_7"
        if day is not None and day <= 7
        else "days_8_30"
        if day is not None
        else None,
        complete=None,
        complication_types=[
            x
            for x in raw.get("complication_types", [])
            if x in {"pneumothorax", "bleeding", "infection", "respiratory_failure"}
        ],
    )
    # A contact date or lack of a keyword does not establish completed ascertainment.
    return {
        "clinical_update": values,
        "conflicting_safety_findings": conflicts,
        "source_evidence": [
            evidence(request, start, min(end, start + 4096)) for start, end, _ in segments(text)
        ],
        "review_requirements": [
            "assessment_window",
            "complete_ascertainment",
            "component_attribution",
            *(["conflicting_safety_findings"] if conflicts else []),
        ],
        "extraction_version": "0.2.0",
    }
