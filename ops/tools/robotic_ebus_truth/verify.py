"""Check that every gold value is readable in the sentence that states it.

``unsupported_values`` is deterministic and runs on every document. For notes a
model wrote, ``VERIFIER_*`` defines an independent check: a second call sees the
note and the fact statements (never the generator plan) and labels each fact
supported, contradicted or ambiguous, and lists registry facts it finds that are
not in the list. A document is accepted only if both checks pass.
"""

from __future__ import annotations

import re
from typing import Any

from ops.tools.robotic_ebus_truth.scenarios import LOBES, Scenario

# Words that must appear (any one) in the quote for an enum value to count as stated.
ENUM_WORDS: dict[str, tuple[str, ...]] = {
    **{lobe: (text,) for lobe, (text, _) in LOBES.items()},
    "lung": ("lesion", "nodule", "target"),
    "lymph_node": ("station",),
    "solid": ("solid",),
    "part_solid": ("part-solid", "part solid"),
    "ground_glass": ("ground-glass", "ground glass"),
    "cavitary": ("cavitary",),
    "male": ("male", " man"),
    "female": ("female", "woman"),
    "never": ("never",),
    "former": ("former",),
    "current": ("current",),
    "general": ("general",),
    "moderate": ("moderate",),
    "ETT": ("endotracheal", "ETT"),
    "LMA": ("laryngeal mask", "LMA"),
    "natural_airway": ("natural airway",),
    "mm": ("mm",),
    "LMA_size": ("size",),
    "diagnosis": ("diagnosis",),
    "staging": ("staging",),
    "diagnosis_and_staging": ("diagnosis",),
    "robotic_bronchoscopy": ("robotic",),
    "linear_ebus": ("EBUS",),
    "performed": ("performed",),
    "attempted": ("attempted",),
    "not_performed": ("not performed",),
    "completed": ("completed",),
    "aborted_after_start": ("aborted",),
    "not_started": ("not started",),
    "Ion": ("Ion",),
    "Monarch": ("Monarch",),
    "Galaxy": ("Galaxy",),
    "reached_and_sampled": ("reached",),
    "aborted": ("not reached", "aborted"),
    "not_reached_not_sampled": ("did not reach", "not reached"),
    "radial_EBUS": ("radial",),
    "concentric": ("concentric",),
    "eccentric": ("eccentric",),
    "adjacent": ("adjacent",),
    "mobile_CBCT": ("mobile cone-beam",),
    "fixed_CBCT": ("fixed cone-beam",),
    "CBCT_unspecified": ("cone-beam",),
    "digital_tomosynthesis": ("tomosynthesis",),
    "2D_fluoroscopy": ("fluoroscopy",),
    "TIL": ("within the lesion", "tool-in-lesion"),
    "prebiopsy": ("before sampling",),
    "touching": ("touching",),
    "actual_lesion": ("lesion",),
    "needle_tip": ("needle tip",),
    "sampling_tool": ("needle",),
    "volumetric_imaging": ("cone-beam",),
    "tomosynthesis": ("tomosynthesis",),
    "aggregate_reported": ("passes", "biopsies", "brushings", "aspiration", "TBNA", "cryobiopsy"),
    "single_pass": ("Pass",),
    "aspiration_needle": ("needle",),
    "forceps": ("forceps",),
    "cryoprobe": ("cryoprobe", "cryobiopsy"),
    "brush": ("brushings",),
    "cytology": ("cytology",),
    "histology": ("histology",),
    "attributed": ("target", "station"),
    "confirmed": ("Specimen",),
    "initial_staging": ("initial",),
    "targeted_diagnosis": ("targeted",),
    "restaging": ("restaging",),
    "systematic": ("systematic",),
    "targeted": ("targeted",),
    "EBUS": ("EBUS",),
    "pneumothorax": ("pneumothorax",),
    "bleeding": ("bleeding",),
    "present": ("occurred",),
    "absent": ("no ",),
    "immediate": ("immediately",),
    "left": ("left",),
    "right": ("right",),
    "home": ("home",),
    "observation": ("observation",),
    "inpatient": ("admitted",),
}
TRUE_WORDS = {
    "planned": ("planned",),
    "prespecified_biopsy_target": ("prespecified",),
    "bronchus_sign_present": ("bronchus",),
    "pet_avid": ("FDG-avid",),
    "diagnostic_attempted": ("navigated", "navigation"),
    "sampling_attempted": (
        "sampled",
        "aspiration",
        "biopsies",
        "brushings",
        "TBNA",
        "Pass",
        "cryobiopsy",
    ),
    "specimen_obtained": ("Specimen",),
    "rose_used": ("ROSE",),
    "rose_adequate": ("adequate",),
    "rose_performed": ("ROSE",),
    "station_surveyed": ("visualized",),
    "station_visualized": ("visualized",),
    "station_sampled": ("sampled",),
    "size_axis_explicit": ("short axis",),
    "target_reached_operational": ("reached",),
    "navigation_success_system_reported": ("reached",),
    "lesion_visible": ("view", "lesion"),
    "sampling_tool_present": ("needle",),
    "final_prebiopsy_confirmation": ("before sampling",),
    "systematic_exam_complete": ("complete",),
    "pleural_intervention": ("chest tube",),
}
FALSE_WORDS = ("no ", "not ", "without", "did not", "inadequate")


def _swapped(a: str, b: str) -> bool:
    """True when b is a with one adjacent transposition (the messy style's typo)."""
    if len(a) != len(b) or a == b:
        return a == b
    diffs = [i for i, (x, y) in enumerate(zip(a, b, strict=True)) if x != y]
    return (
        len(diffs) == 2
        and diffs[1] == diffs[0] + 1
        and a[diffs[0]] == b[diffs[1]]
        and a[diffs[1]] == b[diffs[0]]
    )


def _present(phrase: str, text: str) -> bool:
    """Case-insensitive phrase presence, tolerating one transposition per word."""
    phrase, text = phrase.lower(), text.lower()
    if phrase in text:
        return True
    words = re.findall(r"[a-z0-9+\-]+", phrase)
    tokens = re.findall(r"[a-z0-9+\-]+", text)
    if not words:
        return False
    for i in range(len(tokens) - len(words) + 1):
        if all(_swapped(w, t) for w, t in zip(words, tokens[i : i + len(words)], strict=True)):
            return True
    return False


def _number_forms(value: float) -> list[str]:
    forms = [f"{value:g}"]
    if float(value).is_integer():
        n = int(value)
        forms += [
            str(n),
            {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}.get(
                n, str(n)
            ),
        ]
        if n >= 5:
            forms.append(f"{n / 10:.1f} cm")
    roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}
    if float(value).is_integer() and int(value) in roman:
        forms.append(f"class {roman[int(value)]}")
    return forms


def value_supported(field: str, value: Any, quote: str) -> bool:
    if isinstance(value, bool):
        if value:
            return (
                any(_present(w, quote) for w in TRUE_WORDS.get(field, ("",)) if w)
                or field not in TRUE_WORDS
            )
        return any(_present(w, quote) for w in FALSE_WORDS)
    if isinstance(value, (int, float)):
        return any(
            re.search(r"(?<![\d.])" + re.escape(form) + r"(?![\d])", quote, re.I)
            for form in _number_forms(value)
        )
    if field in {
        "indication",
        "rose_result",
        "reason_not_sampled",
        "navigation_failure_reason",
        "segment",
        "anatomic_label",
        "abort_reason",
        "reason_sampling_not_attempted",
    }:
        words = [w for w in re.findall(r"[a-z0-9+]+", str(value).lower()) if len(w) > 2]
        return bool(words) and sum(_present(w, quote) for w in words) / len(words) >= 0.6
    if field in {"specimen_label", "iaslc_station"}:
        return re.search(r"(?<![\w])" + re.escape(str(value)) + r"(?![\w])", quote) is not None
    return any(_present(w, quote) for w in ENUM_WORDS.get(str(value), (str(value),)))


def unsupported_values(
    scenario: Scenario, stated: set[str], spans: dict[str, tuple[int, int]], text: str
) -> list[tuple[str, str, Any]]:
    """(unit id, field, value) for every stated value its quote does not support."""
    problems = []
    for unit in scenario.units:
        if unit.id not in stated:
            continue
        if unit.id not in spans:
            problems.append((unit.id, "*", "missing quote"))
            continue
        start, end = spans[unit.id]
        quote = text[start:end]
        for _, _, field, value in unit.sets:
            if not value_supported(field, value, quote):
                problems.append((unit.id, field, value))
    return problems


VERIFIER_SYSTEM = """\
You check synthetic interventional pulmonology notes. You are given a note and a numbered list of
fact statements. For each statement say whether the note states it (supported), states something
incompatible with it (contradicted), or is unclear (ambiguous). Then list any registry-relevant fact
the note asserts about this procedure that no statement covers: a procedure, target, lymph node
station, size, navigation or imaging result, sampling tool, pass count, ROSE result, specimen, or
complication. Ignore boilerplate such as consent, time-out and airway inspection.
"""
VERIFIER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["facts", "extra_facts"],
    "properties": {
        "facts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["fact_id", "verdict"],
                "properties": {
                    "fact_id": {"type": "string"},
                    "verdict": {
                        "type": "string",
                        "enum": ["supported", "contradicted", "ambiguous"],
                    },
                },
            },
        },
        "extra_facts": {"type": "array", "items": {"type": "string"}},
    },
}


def verifier_message(text: str, facts: list[tuple[str, str]]) -> str:
    listing = "\n".join(f"[{fact_id}] {statement}" for fact_id, statement in facts)
    return f"<note>\n{text}\n</note>\n\n<statements>\n{listing}\n</statements>"


def verifier_accepts(result: dict[str, Any] | None, fact_ids: set[str]) -> tuple[bool, list[str]]:
    if not result:
        return False, ["verifier_failed"]
    verdicts = {f["fact_id"]: f["verdict"] for f in result.get("facts", [])}
    problems = [
        f"{fid}:{verdicts.get(fid, 'missing')}"
        for fid in sorted(fact_ids)
        if verdicts.get(fid) != "supported"
    ]
    problems += [f"extra:{fact}" for fact in result.get("extra_facts", [])]
    return not problems, problems


__all__ = [
    "VERIFIER_SCHEMA",
    "VERIFIER_SYSTEM",
    "unsupported_values",
    "value_supported",
    "verifier_accepts",
    "verifier_message",
]
