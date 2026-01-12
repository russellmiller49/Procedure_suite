from __future__ import annotations

import re

from modules.common.sectionizer import SectionizerService


_PROCEDURE_FOCUS_HEADINGS: tuple[str, ...] = (
    "PROCEDURE",
    "FINDINGS",
    "IMPRESSION",
    "TECHNIQUE",
    "OPERATIVE REPORT",
)


_TARGET_HEADING_SET = {h.upper() for h in _PROCEDURE_FOCUS_HEADINGS}


def _normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).upper()


def _extract_target_sections_by_regex(note_text: str) -> dict[str, list[str]]:
    pattern = re.compile(r"^(?P<header>[A-Za-z][A-Za-z /_-]{0,80})\s*:\s*(?P<rest>.*)$", re.MULTILINE)
    matches = list(pattern.finditer(note_text))
    extracted: dict[str, list[str]] = {h: [] for h in _PROCEDURE_FOCUS_HEADINGS}
    if not matches:
        return extracted

    for idx, match in enumerate(matches):
        header = _normalize_heading(match.group("header"))
        if header not in _TARGET_HEADING_SET:
            continue

        body_start = match.start("rest")
        body_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(note_text)
        body = (note_text[body_start:body_end] or "").strip()
        if body:
            extracted[header].append(body)

    return extracted


def _dedupe_bodies(bodies: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for body in bodies:
        clean = (body or "").strip()
        if not clean:
            continue
        key = re.sub(r"\s+", " ", clean)
        if key in seen:
            continue
        seen.add(key)
        out.append(clean)
    return out


def get_procedure_focus(note_text: str) -> str:
    """Return a focused view of the note for procedure extraction.

    If no relevant section headings are found, returns the full original note text.
    """
    original = note_text or ""
    if not original.strip():
        return note_text

    extracted: dict[str, list[str]] = {h: [] for h in _PROCEDURE_FOCUS_HEADINGS}

    # 1) ParserAgent handles inline headings like "PROCEDURE: text..." well.
    try:
        from modules.agents.contracts import ParserIn
        from modules.agents.parser.parser_agent import ParserAgent

        parser_out = ParserAgent().run(ParserIn(note_id="", raw_text=original))
        for seg in getattr(parser_out, "segments", []) or []:
            seg_type = _normalize_heading(getattr(seg, "type", ""))
            if seg_type not in _TARGET_HEADING_SET:
                continue
            seg_text = (getattr(seg, "text", "") or "").strip()
            if seg_text:
                extracted[seg_type].append(seg_text)
    except Exception:
        pass

    # 2) Sectionizer handles isolated headings and formatting quirks.
    try:
        sectionizer = SectionizerService(headings=_PROCEDURE_FOCUS_HEADINGS)
        sections = sectionizer.sectionize(original)
        for section in sections:
            title = _normalize_heading(section.title or "")
            if title not in _TARGET_HEADING_SET:
                continue
            clean = (section.text or "").strip()
            if clean:
                extracted[title].append(clean)
    except Exception:
        pass

    # 3) Regex fallback for any remaining headings (including "OPERATIVE REPORT: ...").
    regex_extracted = _extract_target_sections_by_regex(original)
    for title, bodies in regex_extracted.items():
        for body in bodies:
            if body not in extracted[title]:
                extracted[title].append(body)

    for title in list(extracted.keys()):
        extracted[title] = _dedupe_bodies(extracted[title])

    focused_parts: list[str] = []
    for title in _PROCEDURE_FOCUS_HEADINGS:
        for text in extracted[title]:
            clean = (text or "").strip()
            if clean:
                focused_parts.append(f"{title}:\n{clean}")

    focused = "\n\n".join(focused_parts).strip()
    return focused if focused else note_text


__all__ = ["get_procedure_focus"]
