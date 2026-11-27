"""Claude-written notes from the same statement plan, with verbatim quotes per fact.

Claude receives the stated facts as numbered statements (rendered by the template
writer) and a style exemplar from the training split, and returns the note plus a
verbatim quote for every statement. A document is accepted only when every quote
is found in the note, every value is readable in its quote, and the independent
verifier (verify.py) finds every statement supported and no extra registry fact.
Rejected documents are dropped, never patched.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from app.llm_extraction.anchoring import anchor
from ops.tools.robotic_ebus_truth.scenarios import Scenario
from ops.tools.robotic_ebus_truth.template_writer import group_sentences
from ops.tools.robotic_ebus_truth.verify import (
    VERIFIER_SCHEMA,
    VERIFIER_SYSTEM,
    unsupported_values,
    verifier_accepts,
    verifier_message,
)

ROOT = Path(__file__).resolve().parents[3]
TRAIN = ROOT / "data/ml_training/robotic_ebus_v1/corpus_20260914_v2/train.jsonl"

WRITER_SYSTEM = """\
You write synthetic interventional pulmonology procedure notes used to test registry extraction
software. Every note is fictional.

Write one procedure note that conveys every numbered statement you are given and no other clinical
fact about this procedure: no additional targets, stations, sizes, tools, pass counts, imaging,
ROSE results, specimens, complications or dispositions. Neutral boilerplate (consent, time-out,
monitoring, a normal airway inspection) is fine. Keep every number, station name, lobe, laterality,
negation and adequacy statement exactly as given; you may reword everything else and use the
requested style.

For each statement, return the shortest passage of your note that conveys it, copied character for
character from the note.
"""
WRITER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["note", "quotes"],
    "properties": {
        "note": {"type": "string"},
        "quotes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["fact_id", "quote"],
                "properties": {"fact_id": {"type": "string"}, "quote": {"type": "string"}},
            },
        },
    },
}
STYLE_GUIDES = {
    "narrative": "a complete operative report with section headings, written in full sentences",
    "dictation": "a dictated report in plain paragraphs without headings",
    "messy": (
        "a hurried dictation with common abbreviations and a few spelling errors in ordinary words; "
        "numbers, station names, lobes, laterality and negations stay exact"
    ),
}


def exemplar(platform: str, seed: int, limit: int = 1400) -> str:
    """A training-split note of the same platform, used for layout and tone only."""
    rows = [json.loads(line) for line in TRAIN.read_text().splitlines()]
    candidates = [
        r
        for r in rows
        if r.get("platform") == platform and "messy" not in " ".join(r["sources"]).lower()
    ]
    choice = random.Random(seed).choice(candidates or rows)
    return choice["text"][:limit]


def facts(scenario: Scenario, stated: set[str], seed: int) -> list[tuple[str, str, list[str]]]:
    """(fact id, statement, unit ids) for every stated sentence group."""
    return [
        (f"F{i}", sentence, ids)
        for i, (_, _, sentence, ids) in enumerate(
            group_sentences(scenario, stated, random.Random(seed)), 1
        )
    ]


def writer_message(
    scenario: Scenario, fact_list: list[tuple[str, str, list[str]]], *, style: str, example: str
) -> str:
    statements = "\n".join(f"[{fid}] {statement}" for fid, statement, _ in fact_list)
    return (
        f"Write the note as {STYLE_GUIDES[style]}. Start with the line "
        f"'SYNTHETIC TRAINING NOTE - NOT FOR CLINICAL USE' and a line 'Procedure date: "
        f"{scenario.event_date.isoformat()}'.\n\n"
        "Imitate the layout and tone of this example from a different case. Copy none of its clinical details:\n"
        f"<example>\n{example}\n</example>\n\n<statements>\n{statements}\n</statements>"
    )


def spans_from_quotes(
    text: str, quotes: list[dict[str, Any]], fact_list: list[tuple[str, str, list[str]]]
) -> tuple[dict[str, tuple[int, int]], list[str]]:
    by_id = {q["fact_id"]: q["quote"] for q in quotes}
    spans, missing = {}, []
    for fid, _, unit_ids in fact_list:
        found = anchor(text, by_id.get(fid, ""))
        if found is None:
            missing.append(fid)
            continue
        for uid in unit_ids:
            spans[uid] = (found.start, found.end)
    return spans, missing


def check_draft(scenario: Scenario, stated: set[str], fact_list, draft: dict[str, Any] | None):
    """Deterministic acceptance: (text, spans, problems)."""
    if not draft or not draft.get("note"):
        return None, {}, ["writer_failed"]
    text = draft["note"]
    spans, missing = spans_from_quotes(text, draft.get("quotes", []), fact_list)
    problems = [f"quote_not_found:{fid}" for fid in missing]
    problems += [
        f"unsupported:{uid}:{field}"
        for uid, field, _ in unsupported_values(scenario, stated, spans, text)
    ]
    return text, spans, problems


def write_online(
    client, scenario: Scenario, stated: set[str], *, style: str, seed: int
) -> dict[str, Any]:
    """Writer call, deterministic checks, then the independent verifier. Caller declares egress."""
    fact_list = facts(scenario, stated, seed)
    message = writer_message(
        scenario, fact_list, style=style, example=exemplar(scenario.platform, seed)
    )
    draft = client.complete_json(system=WRITER_SYSTEM, user=message, schema=WRITER_SCHEMA)
    text, spans, problems = check_draft(scenario, stated, fact_list, draft.parsed)
    cost = [draft.cost_usd or 0.0]
    if not problems:
        verdict = client.complete_json(
            system=VERIFIER_SYSTEM,
            user=verifier_message(text, [(fid, statement) for fid, statement, _ in fact_list]),
            schema=VERIFIER_SCHEMA,
        )
        cost.append(verdict.cost_usd or 0.0)
        _, problems = verifier_accepts(verdict.parsed, {fid for fid, _, _ in fact_list})
    return {
        "accepted": not problems,
        "text": text,
        "spans": spans,
        "problems": problems,
        "cost_usd": round(sum(cost), 6),
        "model": draft.model,
    }


__all__ = [
    "STYLE_GUIDES",
    "WRITER_SCHEMA",
    "WRITER_SYSTEM",
    "check_draft",
    "exemplar",
    "facts",
    "spans_from_quotes",
    "write_online",
    "writer_message",
]
