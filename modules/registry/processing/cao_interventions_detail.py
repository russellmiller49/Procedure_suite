"""Deterministic backstop extraction for central airway obstruction (CAO) site detail.

The v3 registry schema supports `registry.granular_data.cao_interventions_detail[]`
as a per-site structure for:
- location (Trachea, LMS/RMS/BI, lobar, etc.)
- pre/post obstruction percent or diameter
- modalities applied (APC, electrocautery snare, cryoextraction, balloon dilation, etc.)

Model-driven extraction can miss these fields; this module provides a conservative
regex-based extractor that only emits values explicitly supported by the note text.
"""

from __future__ import annotations

import re
from typing import Any


_CAO_HINT_RE = re.compile(
    r"(?i)\b(?:"
    r"central\s+airway|airway\s+obstruction|trache(?:a|al)|mainstem\s+obstruction|"
    r"debulk(?:ing)?|tumou?r\s+ablation|endoluminal\s+tumou?r|recanaliz|"
    r"airway\s+stent|y-?stent|tracheomalacia|bronchomalacia|rigid\s+bronchos"
    r")\b"
)

_POST_CUE_RE = re.compile(
    r"(?i)\b(?:"
    r"at\s+the\s+end|end\s+of\s+the\s+procedure|at\s+conclusion|finally|"
    r"post[-\s]?(?:procedure|intervention|treatment|op)|"
    r"after\s+(?:debulk|dilat|ablat|treat|interven)|"
    r"improv(?:ed|ement)\s+to|reduc(?:ed)?\s+to|decreas(?:ed)?\s+to"
    r")\b"
)

_SENTENCE_SPLIT_RE = re.compile(r"(?:\n+|(?<=[.!?])\s+)")

_LOCATION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Tracheostomy tube lumen", re.compile(r"(?i)\btracheostomy\s+tube\b.{0,80}?\blumen\b")),
    ("Trachea", re.compile(r"(?i)\btrachea\b")),
    ("Carina", re.compile(r"(?i)\b(?:main\s+carina|carina)\b")),
    ("RMS", re.compile(r"(?i)\bright\s+main(?:\s*|-)?stem\b|\bRMS\b")),
    ("LMS", re.compile(r"(?i)\bleft\s+main(?:\s*|-)?stem\b|\bLMS\b")),
    ("BI", re.compile(r"(?i)\bbronchus\s+intermedius\b|\bBI\b")),
    ("Lingula", re.compile(r"(?i)\blingula\b")),
    ("RUL", re.compile(r"(?i)\bright\s+upper\s+lobe\b|\bRUL\b")),
    ("RML", re.compile(r"(?i)\bright\s+middle\s+lobe\b|\bRML\b")),
    ("RLL", re.compile(r"(?i)\bright\s+lower\s+lobe\b|\bRLL\b")),
    ("LUL", re.compile(r"(?i)\bleft\s+upper\s+lobe\b|\bLUL\b")),
    ("LLL", re.compile(r"(?i)\bleft\s+lower\s+lobe\b|\bLLL\b")),
)

_MODALITY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("APC", re.compile(r"(?i)\bapc\b|argon\s+plasma")),
    ("Electrocautery - snare", re.compile(r"(?i)\belectrocautery\s+snare\b|\bhot\s+snare\b|\bsnare\b")),
    ("Electrocautery - knife", re.compile(r"(?i)\b(?:electrocautery|cautery)\s+(?:knife|needle\s*knife)\b")),
    ("Electrocautery - probe", re.compile(r"(?i)\b(?:electrocautery|cautery)\s+(?:probe|bicap|coag(?:ulation)?\s+probe)\b")),
    ("Cryoextraction", re.compile(r"(?i)\bcryo\s*extraction\b|\bcryoextraction\b")),
    ("Cryotherapy - contact", re.compile(r"(?i)\bcryotherap\w*\b|\bcryoprobe\b")),
    ("Laser", re.compile(r"(?i)\blaser\b|nd:yag|yag\b")),
    ("Microdebrider", re.compile(r"(?i)\bmicrodebrider\b")),
    ("Mechanical debulking", re.compile(r"(?i)\bmechanical\b.{0,30}\bdebulk|\bdebulk\w*\b|\bcore\s*out\b|\brig(?:id)?\s+coring\b")),
    ("Balloon dilation", re.compile(r"(?i)\bballoon\b.{0,40}\b(dilat|dilatation|dilation)\b|\bcre\s+balloon\b")),
    ("Suctioning", re.compile(r"(?i)\bsuction(?:ed|ing)?\b|\baspirat(?:e|ion)\b")),
    ("Iced saline lavage", re.compile(r"(?i)\b(?:cold|iced)\s+saline\b|\bsaline\s+flush")),
    ("Epinephrine instillation", re.compile(r"(?i)\bepinephrine\b")),
    ("Tranexamic acid instillation", re.compile(r"(?i)\btranexamic\b|\btxa\b")),
)

_LESION_MORPHOLOGY_RE = re.compile(
    r"(?i)\b(?:polypoid|fungating|exophytic|necrotic|granulation|web|stenos(?:is|ed))\b"
)
_LESION_COUNT_RE = re.compile(
    r"(?i)(?:\(|\b)?(?P<count>>\s*\d{1,3}|\d{1,3})\)?[^.\n]{0,40}\blesions?\b"
)

_OBSTRUCTION_PCT_AFTER_LOC_RE = re.compile(
    r"(?i)\b(?P<loc>[^.]{0,80}?)\b(?:was|were|is|are|remained|remains)?\s*"
    r"(?:only\s+)?(?:about|around|approximately|approx\.?)?\s*"
    r"(?P<pct>\d{1,3})\s*%\s*"
    r"(?:obstruct(?:ed|ion)?|occlud(?:ed|ing|e)?|stenos(?:is|ed)|narrow(?:ing|ed)?|block(?:ed|ing)?)\b"
    r"(?!\s+of\b)"
)
_OBSTRUCTION_PCT_BEFORE_LOC_RE = re.compile(
    r"(?i)\b(?:about|around|approximately|approx\.?)?\s*(?P<pct>\d{1,3})\s*%\s*"
    r"(?:obstruct(?:ion)?|obstructed|occlud(?:ed|ing|e)?|stenos(?:is|ed)|narrow(?:ing|ed)?|block(?:ed|ing)?)"
    r"(?:\s+(?:of|in|at)\s+(?:the\s+)?)"
    r"(?P<loc>[^.]{3,80})"
)
_BLOCKING_PCT_RE = re.compile(
    r"(?i)\bblocking\b[^%]{0,40}?(?P<pct>\d{1,3})\s*%\s*(?:of\s+(?:the\s+)?)?(?:airway|lumen)\b"
)
_OCCLUDING_PCT_RE = re.compile(
    r"(?i)\b(?:occluding|occluded)\b[^%]{0,40}?(?P<pct>\d{1,3})\s*%\s*"
    r"(?:of\s+(?:the\s+)?)?(?P<loc>[^.]{3,80})"
)
_PCT_OPEN_RE = re.compile(
    r"(?i)\b(?P<pct>\d{1,3})\s*%\s*(?:open|patent|recanaliz(?:ed|ation))\b"
)
_COMPLETE_OBSTRUCTION_OF_RE = re.compile(
    r"(?i)\b(?:complete(?:ly)?|total)\s+(?:obstruction|occlusion)\b\s+of\s+(?:the\s+)?"
    r"(?P<loc>[^,.;\n]{3,80}?)(?=\s+(?:and|with|to|from|,|\\.|;|$))"
)
_COMPLETELY_OBSTRUCTED_RE = re.compile(
    r"(?i)\b(?:was|were|remained|remains)\s+(?:still\s+)?(?:completely|totally)\s+(?:obstructed|occluded|blocked)\b"
)

_STENT_PLACED_RE = re.compile(
    r"(?i)\b(?:stent|y-?stent)\b.{0,80}\b(?:placed|placement|deploy(?:ed)?|deployed|inserted)\b"
)
_STENT_NEGATION_CUES_RE = re.compile(
    r"(?i)\b(?:"
    r"considered|discussion|reluctan|declin|defer(?:red)?|not\s+placed|no\s+stent|"
    r"unable|not\s+possible|unsuccessful|"
    r"advocat(?:e|ing)\s+for|would\s+(?:recommend|consider)|if\s+i\s+need"
    r")\b"
)
_STENT_DEPLOY_DECISION_RE = re.compile(r"(?i)\b(?:decision|decided)\b.{0,80}\bdeploy\b")


def _maybe_unescape_newlines(text: str) -> str:
    raw = text or ""
    if not raw.strip():
        return raw
    if "\n" in raw or "\r" in raw:
        return raw
    if "\\n" not in raw and "\\r" not in raw:
        return raw
    return raw.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")


def _infer_location(value: str) -> str | None:
    raw = (value or "").strip()
    if not raw:
        return None
    for canonical, pattern in _LOCATION_PATTERNS:
        if pattern.search(raw):
            return canonical
    return None


def _infer_location_last(value: str) -> str | None:
    raw = (value or "").strip()
    if not raw:
        return None
    best_loc: str | None = None
    best_pos = -1
    for canonical, pattern in _LOCATION_PATTERNS:
        for match in pattern.finditer(raw):
            if match.start() >= best_pos:
                best_pos = match.start()
                best_loc = canonical
    return best_loc


def _append_modality(site: dict[str, Any], modality: str) -> None:
    apps = site.get("modalities_applied")
    if not isinstance(apps, list):
        apps = []
        site["modalities_applied"] = apps
    for existing in apps:
        if isinstance(existing, dict) and existing.get("modality") == modality:
            return
    apps.append({"modality": modality})


def extract_cao_interventions_detail(note_text: str) -> list[dict[str, Any]]:
    """Extract CAO site detail into v3 granular format.

    Returns a list of dicts compatible with granular_data.cao_interventions_detail.
    """
    text = _maybe_unescape_newlines(note_text or "")
    if not text.strip():
        return []
    if not _CAO_HINT_RE.search(text):
        return []

    sites: dict[str, dict[str, Any]] = {}
    current_location: str | None = None
    post_context_remaining = 0
    fallback_location = "Trachea" if re.search(r"(?i)\btrachea\b", text) else None

    def _get_site(loc: str) -> dict[str, Any]:
        if loc not in sites:
            sites[loc] = {"location": loc}
        return sites[loc]

    def _assign_pct(loc: str, pct: int, *, is_post: bool) -> None:
        pct_int = max(0, min(100, int(pct)))
        site = _get_site(loc)
        if is_post:
            existing = site.get("post_obstruction_pct")
            if existing is None:
                site["post_obstruction_pct"] = pct_int
            else:
                site["post_obstruction_pct"] = min(int(existing), pct_int)
        else:
            existing = site.get("pre_obstruction_pct")
            if existing is None:
                site["pre_obstruction_pct"] = pct_int
            else:
                site["pre_obstruction_pct"] = max(int(existing), pct_int)

    for raw_sentence in _SENTENCE_SPLIT_RE.split(text):
        sentence = (raw_sentence or "").strip()
        if not sentence:
            continue

        is_post = post_context_remaining > 0
        if _POST_CUE_RE.search(sentence):
            post_context_remaining = max(post_context_remaining, 3)
            is_post = True

        # Determine location context for sentences with no explicit location on the match.
        locations_in_sentence = []
        for canonical, pattern in _LOCATION_PATTERNS:
            if pattern.search(sentence):
                locations_in_sentence.append(canonical)
        if locations_in_sentence:
            current_location = locations_in_sentence[0]

        # 1) Percent obstruction with explicit location group (loc before percent).
        for match in _OBSTRUCTION_PCT_AFTER_LOC_RE.finditer(sentence):
            loc_group = match.group("loc") or ""
            loc = _infer_location(loc_group) or current_location
            if not loc and fallback_location and re.search(r"(?i)\b(?:airway|lumen)\b", loc_group):
                loc = fallback_location
            if not loc:
                continue
            try:
                pct = int(match.group("pct"))
            except Exception:
                continue
            _assign_pct(loc, pct, is_post=is_post)

        # 2) Percent obstruction with explicit location group (percent before location).
        for match in _OBSTRUCTION_PCT_BEFORE_LOC_RE.finditer(sentence):
            loc_group = match.group("loc") or ""
            loc = _infer_location(loc_group) or current_location
            if not loc and fallback_location and re.search(r"(?i)\b(?:airway|lumen)\b", loc_group):
                loc = fallback_location
            if not loc:
                continue
            try:
                pct = int(match.group("pct"))
            except Exception:
                continue
            _assign_pct(loc, pct, is_post=is_post)

        # 3) "Blocking 90% of the airway" (no explicit obstruction token after percent).
        for match in _BLOCKING_PCT_RE.finditer(sentence):
            loc = current_location or fallback_location
            if not loc and len(locations_in_sentence) == 1:
                loc = locations_in_sentence[0]
            if not loc:
                continue
            try:
                pct = int(match.group("pct"))
            except Exception:
                continue
            _assign_pct(loc, pct, is_post=is_post)

            # Preserve dynamic collapse context for clinician readability.
            if re.search(r"(?i)\b(?:exhalation|inhalation)\b", sentence):
                site = _get_site(loc)
                existing = (site.get("notes") or "").strip()
                snippet = sentence
                if len(snippet) > 320:
                    snippet = snippet[:320].rsplit(" ", 1)[0].strip()
                note_val = f"{existing}; {snippet}" if existing else snippet
                site["notes"] = note_val

        # 3b) "Occluding 80% of the tracheostomy tube lumen" patterns.
        for match in _OCCLUDING_PCT_RE.finditer(sentence):
            loc = _infer_location(match.group("loc") or "") or current_location
            if not loc and fallback_location and re.search(r"(?i)\b(?:airway|lumen)\b", match.group("loc") or ""):
                loc = fallback_location
            if not loc:
                continue
            try:
                pct = int(match.group("pct"))
            except Exception:
                continue
            _assign_pct(loc, pct, is_post=is_post)

        # 4) Percent open/patent -> obstruction = 100 - patency (usually post).
        for match in _PCT_OPEN_RE.finditer(sentence):
            loc = current_location or fallback_location
            if not loc and len(locations_in_sentence) == 1:
                loc = locations_in_sentence[0]
            if not loc:
                continue
            try:
                patency = int(match.group("pct"))
            except Exception:
                continue
            if not (0 <= patency <= 100):
                continue
            obstruction = 100 - patency
            _assign_pct(loc, obstruction, is_post=True)

        # 5) Complete obstruction/occlusion with explicit "of <location>" (multi-hit).
        for match in _COMPLETE_OBSTRUCTION_OF_RE.finditer(sentence):
            loc = _infer_location(match.group("loc") or "") or current_location
            if not loc:
                continue
            _assign_pct(loc, 100, is_post=is_post)

        # 6) "... remained completely obstructed" patterns (handles multi-location sentences).
        for match in _COMPLETELY_OBSTRUCTED_RE.finditer(sentence):
            prefix = sentence[max(0, match.start() - 140) : match.start()]
            loc = _infer_location_last(prefix) or current_location
            if not loc:
                continue
            _assign_pct(loc, 100, is_post=is_post)

        # Modalities + stent placement: attach to the best location context available.
        target_locations = locations_in_sentence or ([current_location] if current_location else [])
        target_locations = [loc for loc in target_locations if loc]
        lesion_locations = target_locations or ([fallback_location] if fallback_location else [])
        lesion_locations = [loc for loc in lesion_locations if loc]

        if lesion_locations:
            # Lesion morphology/count backstop (helps capture disease burden in templated notes).
            if _LESION_MORPHOLOGY_RE.search(sentence) and re.search(r"(?i)\b(?:lesion|lesions|tumou?r|mass)\b", sentence):
                m = _LESION_MORPHOLOGY_RE.search(sentence)
                morph = (m.group(0) if m else "").strip()
                if morph:
                    for loc in lesion_locations:
                        site = _get_site(loc)
                        if not site.get("lesion_morphology"):
                            site["lesion_morphology"] = morph.capitalize()

            count_match = _LESION_COUNT_RE.search(sentence)
            if count_match:
                raw_count = (count_match.group("count") or "").strip()
                if raw_count:
                    count_text = re.sub(r"\s+", "", raw_count)
                    for loc in lesion_locations:
                        site = _get_site(loc)
                        existing = str(site.get("lesion_count_text") or "").strip()
                        if not existing:
                            site["lesion_count_text"] = count_text
                        elif count_text not in existing:
                            site["lesion_count_text"] = f"{existing}; {count_text}"

        if target_locations:
            for modality, pattern in _MODALITY_PATTERNS:
                if pattern.search(sentence):
                    for loc in target_locations:
                        _append_modality(_get_site(loc), modality)

        if _STENT_PLACED_RE.search(sentence):
            negated = bool(_STENT_NEGATION_CUES_RE.search(sentence))
            if negated and _STENT_DEPLOY_DECISION_RE.search(sentence):
                negated = False

            stent_locations = list(target_locations)
            if not stent_locations and not negated:
                if re.search(r"(?i)\by-?stent\b", sentence):
                    stent_locations = ["Carina"]
                elif fallback_location:
                    stent_locations = [fallback_location]
                else:
                    stent_locations = ["Trachea"]

            for loc in stent_locations:
                site = _get_site(loc)
                if negated:
                    if site.get("stent_placed_at_site") is None:
                        site["stent_placed_at_site"] = False
                else:
                    site["stent_placed_at_site"] = True

        if post_context_remaining > 0:
            post_context_remaining -= 1

    # Return in stable order (proximal → distal-ish).
    priority = {"Tracheostomy tube lumen": 0, "Trachea": 1, "Carina": 2, "RMS": 3, "LMS": 4, "BI": 5}

    def sort_key(item: dict[str, Any]) -> tuple[int, str]:
        loc = str(item.get("location") or "")
        return (priority.get(loc, 100), loc)

    details = list(sites.values())
    details.sort(key=sort_key)
    filtered: list[dict[str, Any]] = []
    for item in details:
        if item.get("pre_obstruction_pct") is not None:
            filtered.append(item)
            continue
        if item.get("post_obstruction_pct") is not None:
            filtered.append(item)
            continue
        if item.get("stent_placed_at_site") is True:
            filtered.append(item)
            continue
    return filtered
