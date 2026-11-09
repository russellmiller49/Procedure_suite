"""Deterministic note writer: one sentence per stated group, exact spans recorded.

Styles imitate the corpus layouts (sectioned headings, markdown labels, fielded
Provation-like lines, plain dictation) plus a messy dictation with typos and
abbreviations. Value-bearing words (numbers, stations, lobes, modalities, tools,
negations) are never perturbed, so every gold value stays readable.
"""

from __future__ import annotations

import random
from typing import Any, Callable

from ops.tools.robotic_ebus_truth.scenarios import Scenario

STYLES = ("sectioned", "markdown", "fielded", "dictation", "messy")
SECTION_OF_KIND = {
    "demographics": "indication",
    "indication": "indication",
    "history": "indication",
    "asa": "anesthesia",
    "anesthesia": "anesthesia",
    "procedure": "procedures",
    "platform": "robotic",
    "target": "robotic",
    "navigation": "robotic",
    "radial": "robotic",
    "volumetric": "robotic",
    "fluoroscopy": "robotic",
    "acquisition": "robotic",
    "single_pass": "robotic",
    "rose": "robotic",
    "specimen": "robotic",
    "ebus_session": "ebus",
    "station": "ebus",
    "node_sampling": "ebus",
    "node_rose": "ebus",
    "node_specimen": "ebus",
    "complications": "complications",
    "duration": "disposition",
    "disposition": "disposition",
}
SECTION_TITLES = {
    "indication": "Indication",
    "anesthesia": "Anesthesia",
    "procedures": "Procedures",
    "robotic": "Robotic navigation and sampling",
    "ebus": "Linear EBUS",
    "complications": "Complications",
    "disposition": "Disposition",
}
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}
TOOL_NAMES = {
    "aspiration_needle": "needle aspirates",
    "forceps": "forceps biopsies",
    "cryoprobe": "cryobiopsies",
    "brush": "brushings",
}
PURPOSE = {
    "initial_staging": "initial mediastinal staging",
    "targeted_diagnosis": "targeted nodal diagnosis",
    "restaging": "mediastinal restaging",
}
PROTECTED = {
    "not",
    "no",
    "but",
    "without",
    "right",
    "left",
    "upper",
    "middle",
    "lower",
    "lobe",
    "lingula",
    "station",
    "concentric",
    "eccentric",
    "adjacent",
    "solid",
    "part-solid",
    "ground-glass",
    "cavitary",
    "radial",
    "cone-beam",
    "tomosynthesis",
    "fluoroscopy",
    "needle",
    "forceps",
    "cryoprobe",
    "cryobiopsy",
    "brushings",
    "pneumothorax",
    "bleeding",
    "general",
    "moderate",
    "endotracheal",
    "laryngeal",
    "male",
    "female",
    "never",
    "former",
    "current",
    "ion",
    "monarch",
    "galaxy",
    "rose",
    "ebus",
    "tbna",
    "specimen",
    "target",
    "tool-in-lesion",
    "adequate",
    "inadequate",
    "systematic",
    "targeted",
    "complete",
    "planned",
    "aborted",
    "reached",
    "sampled",
    "visualized",
    "prespecified",
    "fdg-avid",
    "attempted",
    "completed",
    "performed",
    "observation",
    "home",
    "admitted",
    "discharged",
    "within",
    "touching",
    "mobile",
    "fixed",
    "digital",
    "augmented",
    "immediately",
    "chest",
    "tube",
}
ABBREVIATIONS = {
    "patient": "pt",
    "with": "w/",
    "and": "&",
    "procedure": "proc",
    "approximately": "approx",
}


def _count(n: int, rng: random.Random) -> str:
    return NUMBER_WORDS.get(n, str(n)) if rng.random() < 0.4 else str(n)


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _demographics(r: dict, rng: random.Random) -> str:
    parts = []
    if "age_sex" in r:
        parts.append(f"{r['age_sex']['age']}-year-old {r['age_sex']['sex']}")
    if "smoking" in r:
        s = r["smoking"]
        parts.append(
            "never smoker"
            if s["status"] == "never"
            else f"{s['status']} smoker ({s['pack_years']} pack-years)"
        )
    if rng.random() < 0.5:
        return "Patient: " + ", ".join(parts) + "."
    article = "an" if parts[0][:1] == "8" or parts[0].startswith(("11", "18")) else "a"
    return f"The patient is {article} " + ", ".join(parts) + "."


def _indication(r: dict, rng: random.Random) -> str:
    return f"Indication: {r['indication']['text']}."


def _history(r: dict, rng: random.Random) -> str:
    h = r["history"]
    return (
        f"History: prior bronchoscopy in {h['year']} with EBUS sampling of station {h['station']} "
        "was nondiagnostic."
    )


def _asa(r: dict, rng: random.Random) -> str:
    return f"ASA class {ROMAN[r['asa']['asa']]}."


def _anesthesia(r: dict, rng: random.Random) -> str:
    a = r["anesthesia"]
    if a["type"] == "moderate":
        return "Moderate sedation was used with a natural airway."
    if a["device"] == "ETT":
        size = f"{a['size']:.1f}"
        article = "an" if size.startswith(("8", "11", "18")) else "a"
        return f"General anesthesia via {article} {size} mm endotracheal tube."
    return f"General anesthesia with a size {int(a['size'])} laryngeal mask airway."


def _procedure(r: dict, rng: random.Random) -> str:
    if "robotic" in r:
        if r["robotic"]["aborted"]:
            return (
                "Robotic-assisted bronchoscopy was attempted as planned but aborted after it started "
                "because the target could not be reached."
            )
        return "Robotic-assisted bronchoscopy was performed as planned and completed."
    if "ebus" in r:
        return "Linear EBUS-TBNA was performed as planned and completed."
    return "Linear EBUS staging was planned but was not started and was not performed (deferred)."


def _platform(r: dict, rng: random.Random) -> str:
    return f"The {r['platform']['platform']} robotic platform was used for navigation."


def _target(r: dict, rng: random.Random) -> str:
    ident = r["identity"]
    n = ident["number"]
    descriptor = []
    if "size" in r:
        size = r["size"]["size"]
        descriptor.append(f"{size / 10:.1f} cm" if r["size"]["cm"] else f"{size} mm")
    if "attenuation" in r:
        descriptor.append(r["attenuation"]["attenuation"])
    where = (
        f"the {r['segment']['segment']} of the {ident['lobe']}"
        if "segment" in r
        else f"the {ident['lobe']}"
    )
    lesion = " ".join(descriptor + ["lesion"])
    sentences = [f"Target {n} was a {lesion} in {where}."]
    if "bronchus" in r:
        sentences.append(
            "A bronchus sign was present."
            if r["bronchus"]["present"]
            else "There was no bronchus sign."
        )
    if "pet" in r:
        pet = r["pet"]
        sentences.append(
            f"It was FDG-avid (SUVmax {pet['suv']})."
            if pet["avid"]
            else "It was not FDG-avid on PET."
        )
    if "prespecified" in r:
        sentences.append(f"Target {n} was the prespecified biopsy target.")
    if "not_sampled" in r:
        sentences.append(f"Target {n} was not sampled because it was not reached.")
    return " ".join(sentences)


def _navigation(r: dict, rng: random.Random) -> str:
    run = r["run"]
    n = run["number"]
    if run["reached"]:
        lead = "On the second attempt, the" if run["attempt"] == 2 else "The"
        return f"{lead} robotic catheter was navigated to target {n}, and the target was reached and sampled."
    if run["attempts"] == 2 and run["attempt"] == 1:
        return f"The first navigation attempt to target {n} did not reach the target because {run['reason']}."
    return (
        f"Navigation to target {n} was attempted, but {run['reason']}; the target was not reached."
    )


def _radial(r: dict, rng: random.Random) -> str:
    view = r["radial"]["view"]
    article = "an" if view[0] in "aeiou" else "a"
    if r["radial"]["claim_til"]:
        return f"Radial EBUS showed {article} {view} view, confirming tool-in-lesion."
    return f"Radial EBUS showed {article} {view} view."


def _volumetric(r: dict, rng: random.Random) -> str:
    e = r["event"]
    if e["til"]:
        return f"{_cap(e['modality'])} confirmed the {e['component']} within the lesion before sampling (tool-in-lesion)."
    return f"{_cap(e['modality'])} showed the catheter touching the lesion."


def _fluoroscopy(r: dict, rng: random.Random) -> str:
    return "Fluoroscopy was used during sampling."


def _acquisition(r: dict, rng: random.Random) -> str:
    t = r["tool"]
    passes = f" ({_count(r['passes']['passes'], rng)} passes)" if "passes" in r else ""
    if t["tool"] == "aspiration_needle":
        return f"Transbronchial needle aspiration was performed with a {t['gauge']}-gauge needle{passes}."
    if t["tool"] == "forceps":
        return f"Transbronchial forceps biopsies were obtained{passes}."
    if t["tool"] == "cryoprobe":
        return f"Transbronchial cryobiopsy was performed with a {t['size']} mm cryoprobe{passes}."
    return f"Bronchial brushings were obtained{passes}."


def _single_pass(r: dict, rng: random.Random) -> str:
    p = r["pass"]
    return f"Pass {p['number']}: {p['gauge']}-gauge needle aspiration of target {p['target']}."


def _rose(r: dict, rng: random.Random) -> str:
    x = r["rose"]
    return (
        f"ROSE of target {x['number']} showed {x['result']}; the sample was "
        f"{'adequate' if x['adequate'] else 'not adequate'}."
    )


def _specimen(r: dict, rng: random.Random) -> str:
    s = r["specimen"]
    tools = " and ".join(TOOL_NAMES[t] for t in s["tools"])
    return f"Specimen {s['label']}: {tools} from target {s['number']} ({s['specimen_type']})."


def _ebus_session(r: dict, rng: random.Random) -> str:
    s = r["session"]
    text = f"Linear EBUS was performed for {PURPOSE[s['purpose']]} using a {s['strategy']} sampling strategy."
    if "complete" in r:
        text += " The systematic nodal examination was complete."
    return text


def _station(r: dict, rng: random.Random) -> str:
    s = r["survey"]
    if s["sampled"]:
        text = f"Station {s['station']} was visualized on EBUS and sampled."
    else:
        text = (
            f"Station {s['station']} was visualized on EBUS but not sampled because {s['reason']}."
        )
    if "axis" in r:
        text += f" Station {s['station']} measured {r['axis']['size']} mm in short axis."
    return text


def _node_sampling(r: dict, rng: random.Random) -> str:
    n = r["needle"]
    return (
        f"Station {n['station']}: EBUS-guided TBNA with a {n['gauge']}-gauge needle, "
        f"{_count(n['passes'], rng)} passes."
    )


def _node_rose(r: dict, rng: random.Random) -> str:
    x = r["rose"]
    result = x["result"] if "adequa" in x["result"] else f"{x['result']}, adequate"
    return f"ROSE of station {x['station']}: {result}."


def _node_specimen(r: dict, rng: random.Random) -> str:
    s = r["specimen"]
    return f"Specimen {s['label']}: station {s['station']} aspirates (cytology)."


def _complications(r: dict, rng: random.Random) -> str:
    if "present" in r:
        p = r["present"]
        tail = (
            "treated with a small-bore chest tube"
            if p["tube"]
            else "managed with observation and no pleural intervention"
        )
        after = "the robotic biopsies" if p["robotic"] else "EBUS-TBNA"
        return f"A small {p['laterality']} pneumothorax occurred immediately after {after} and was {tail}."
    text = "No immediate complications."
    if "negated" in r:
        text += " There was no pneumothorax and no significant bleeding."
    return text


def _duration(r: dict, rng: random.Random) -> str:
    return f"Procedure duration: {r['duration']['minutes']} minutes."


def _disposition(r: dict, rng: random.Random) -> str:
    return {
        "home": "The patient was discharged home after recovery.",
        "observation": "The patient was admitted for overnight observation.",
        "inpatient": "The patient was admitted to the hospital.",
    }[r["disposition"]["disposition"]]


RENDERERS: dict[str, Callable[[dict, random.Random], str]] = {
    "demographics": _demographics,
    "indication": _indication,
    "history": _history,
    "asa": _asa,
    "anesthesia": _anesthesia,
    "procedure": _procedure,
    "platform": _platform,
    "target": _target,
    "navigation": _navigation,
    "radial": _radial,
    "volumetric": _volumetric,
    "fluoroscopy": _fluoroscopy,
    "acquisition": _acquisition,
    "single_pass": _single_pass,
    "rose": _rose,
    "specimen": _specimen,
    "ebus_session": _ebus_session,
    "station": _station,
    "node_sampling": _node_sampling,
    "node_rose": _node_rose,
    "node_specimen": _node_specimen,
    "complications": _complications,
    "duration": _duration,
    "disposition": _disposition,
}


def group_sentences(
    scenario: Scenario, stated: set[str], rng: random.Random
) -> list[tuple[str, str, str, list[str]]]:
    """(group, kind, sentence, unit ids) in render order for every group with a stated unit."""
    out = []
    for group in scenario.groups:
        members = [u for u in scenario.units if u.group == group and u.id in stated]
        if not members:
            continue
        roles: dict[str, Any] = {u.role: u.params for u in members}
        kind = members[0].kind
        if kind == "target" and "identity" not in roles:
            continue
        out.append((group, kind, RENDERERS[kind](roles, rng), [u.id for u in members]))
    return out


def _messy(sentence: str, rng: random.Random) -> str:
    def swap(word: str) -> str:
        core = word.strip(".,;:()")
        lower = core.lower()
        if lower in ABBREVIATIONS and rng.random() < 0.5:
            return word.replace(core, ABBREVIATIONS[lower])
        if len(core) >= 7 and lower not in PROTECTED and core.isalpha() and rng.random() < 0.12:
            i = rng.randrange(1, len(core) - 2)
            typo = core[:i] + core[i + 1] + core[i] + core[i + 2 :]
            return word.replace(core, typo)
        return word

    return " ".join(swap(w) for w in sentence.split(" "))


def render(
    scenario: Scenario, stated: set[str], style: str, seed: int
) -> tuple[str, dict[str, tuple[int, int]]]:
    """Return the note text and, for every stated unit, the span of its sentence."""
    rng = random.Random(seed)
    sentences = group_sentences(scenario, stated, rng)
    if style == "messy":
        sentences = [(g, k, _messy(s, rng), ids) for g, k, s, ids in sentences]
    # Platform sentences lead the robotic section.
    sentences.sort(
        key=lambda item: (item[1] != "platform") if SECTION_OF_KIND[item[1]] == "robotic" else 0
    )
    by_section: dict[str, list[tuple[str, list[str]]]] = {}
    for _, kind, sentence, ids in sentences:
        by_section.setdefault(SECTION_OF_KIND[kind], []).append((sentence, ids))
    title = (
        "EBUS Procedure Report"
        if scenario.platform == "linear_ebus"
        else "Robotic Bronchoscopy Procedure Report"
    )
    text = f"SYNTHETIC TRAINING NOTE - NOT FOR CLINICAL USE\n{title}\nProcedure date: {scenario.event_date.isoformat()}\n"
    spans: dict[str, tuple[int, int]] = {}

    def emit(prefix: str, sentence: str, ids: list[str], suffix: str) -> None:
        nonlocal text
        text += prefix
        start = len(text)
        text += sentence
        for uid in ids:
            spans[uid] = (start, start + len(sentence))
        text += suffix

    for section in SECTION_TITLES:
        items = by_section.get(section)
        if not items:
            continue
        title = SECTION_TITLES[section]
        if style == "sectioned":
            text += f"\n{title.upper()}\n"
            for i, (sentence, ids) in enumerate(items):
                emit("" if i == 0 else " ", sentence, ids, "")
            text += "\n"
        elif style == "markdown":
            text += f"\n## {title}\n" if section in {"robotic", "ebus"} else f"\n**{title}:** "
            for i, (sentence, ids) in enumerate(items):
                emit("" if i == 0 else " ", sentence, ids, "")
            text += "\n"
        elif style == "fielded":
            text += f"\n{title}:\n"
            bullets = section in {"robotic", "ebus"}
            for i, (sentence, ids) in enumerate(items):
                emit(
                    "- " if bullets else ("" if i == 0 else " "),
                    sentence,
                    ids,
                    "\n" if bullets else "",
                )
            if not bullets:
                text += "\n"
        else:  # dictation and messy: paragraphs, no headings
            text += "\n"
            for i, (sentence, ids) in enumerate(items):
                emit("" if i == 0 else " ", sentence, ids, "")
            text += "\n"
    return text, spans


__all__ = ["RENDERERS", "STYLES", "group_sentences", "render"]
