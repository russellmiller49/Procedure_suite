#!/usr/bin/env python3
"""
Post-process granular NER training data to disambiguate stent mentions.

Why:
- The granular NER model uses `DEV_STENT` for airway stent placement-related mentions.
- In many notes, "stent" is mentioned but NOT deployed (e.g., "no stent placed"), or is simply
  present from a prior procedure (e.g., "stent in place", "stents are in good position").

This script:
1) Relabels `DEV_STENT` spans to `NEG_STENT` when the text explicitly says a stent was NOT used.
2) Optionally relabels `DEV_STENT` spans to `CTX_STENT_PRESENT` for "stent in place/good position"
   style mentions in notes with no stent intervention (no placement/removal/exchange/migration).
3) Optionally adds missing `NEG_STENT` spans for explicit negation phrases like "no stent placed".

It is intentionally conservative:
- `NEG_STENT` is reserved for absence (e.g., "no stent", "stent not indicated").
- Stent manipulation (removed/exchanged/migrated) is kept as `DEV_STENT`.
- `CTX_STENT_PRESENT` is only applied when the note has no stent intervention evidence.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_INPUT = Path("data/ml_training/granular_ner/ner_dataset_all.jsonl")
DEFAULT_OUTPUT = Path("data/ml_training/granular_ner/ner_dataset_all.neg_stent.jsonl")
DEFAULT_REPORT = Path("reports/neg_stent_labeling_report.json")

PRESENT_STENT_LABEL = "CTX_STENT_PRESENT"

STENT_ABSENCE_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\bno\s+(?:airway\s+)?(?P<stent>stents?)\b", re.IGNORECASE),
    re.compile(r"\bwithout\s+(?:an?\s+)?(?P<stent>stents?)\b", re.IGNORECASE),
    re.compile(
        r"\b(?P<stent>stents?)\s+not\s+(?:placed|deployed|inserted|needed|required|indicated)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bno\s+(?P<stent>stents?)\s+(?:was\s+)?(?:placed|deployed|inserted)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?P<stent>stents?)\s+(?:was\s+)?(?:declined|refused)\b", re.IGNORECASE),
    re.compile(r"\b(?:declined|refused)\s+(?:a|an|any)\s+(?P<stent>stents?)\b", re.IGNORECASE),
)

HISTORICAL_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\bstent\s+in\s+place\b", re.IGNORECASE),
    re.compile(r"\bstents?\s+.*\bgood\s+position\b", re.IGNORECASE),
    re.compile(r"\bexisting\s+stent\b", re.IGNORECASE),
    re.compile(r"\bprior\s+stent\b", re.IGNORECASE),
    re.compile(r"\bprevious\s+stent\b", re.IGNORECASE),
    re.compile(r"\bstent\s+(?:was\s+)?noted\b", re.IGNORECASE),
    re.compile(r"\bstent\s+(?:is|was)\s+present\b", re.IGNORECASE),
    re.compile(r"\bstent\s+check\b", re.IGNORECASE),
)

# Used only for the note-level "any positive placement exists" guard.
POSITIVE_PLACEMENT_VERBS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdeployed\b", re.IGNORECASE),
    re.compile(r"\bdeployment\b", re.IGNORECASE),
    re.compile(r"\bplaced\b", re.IGNORECASE),
    re.compile(r"\bplacement\b", re.IGNORECASE),
    re.compile(r"\binsert(?:ed|ion)\b", re.IGNORECASE),
)

NEGATION_GUARD_WORDS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\bno\b", re.IGNORECASE),
    re.compile(r"\bnot\b", re.IGNORECASE),
    re.compile(r"\bwithout\b", re.IGNORECASE),
    re.compile(r"\bdeclin(?:ed|es)\b", re.IGNORECASE),
    re.compile(r"\brefus(?:ed|es)\b", re.IGNORECASE),
)

STENT_INTERVENTION_PATTERNS: Tuple[re.Pattern[str], ...] = (
    # Stent -> verb (generous window)
    re.compile(
        r"\bstents?\b.{0,60}\b(?:"
        r"removed|removal|retriev(?:ed|al)|extract(?:ed|ion)|exchang(?:ed|e)|"
        r"revis(?:ed|ion)|reposition(?:ed|ing)|"
        r"migrat(?:ed|ion)|malposition(?:ed)?|dislodg(?:ed|ement)"
        r")\b",
        re.IGNORECASE,
    ),
    # Verb -> stent (very tight / object-like; avoids 'bronchoscope was removed ... stent ...')
    re.compile(
        r"\b(?:remove|removed|retriev(?:e|ed)|extract(?:ed)?|exchange(?:d)?|"
        r"revise(?:d)?|reposition(?:ed)?|dislodge(?:d)?)\b\s+(?:the\s+)?stents?\b",
        re.IGNORECASE,
    ),
)


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    ap.add_argument("--write", action="store_true", help="Write updated dataset JSONL to --output.")
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only the first N records (debug).",
    )
    ap.add_argument(
        "--context-window",
        type=int,
        default=140,
        help="Chars on each side of a span used for local context (default: 140).",
    )
    ap.add_argument(
        "--no-add-missing",
        action="store_true",
        help="Disable adding NEG_STENT spans for explicit 'no stent' phrases.",
    )
    ap.add_argument(
        "--no-label-present",
        action="store_true",
        help=f"Disable relabeling 'stent in place' mentions to {PRESENT_STENT_LABEL}.",
    )
    return ap.parse_args(argv)


def _iter_jsonl(path: Path, *, limit: int | None = None) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if limit is not None and idx > limit:
                return
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _entity_key_for(record: Dict[str, Any]) -> str | None:
    if isinstance(record.get("entities"), list):
        return "entities"
    if isinstance(record.get("spans"), list):
        return "spans"
    return None


def _record_id(record: Dict[str, Any]) -> str:
    return str(record.get("id") or record.get("note_id") or "unknown_id")


def _normalize_span(span: Any, text: str) -> Tuple[int | None, int | None, str | None]:
    if isinstance(span, dict):
        start = span.get("start")
        end = span.get("end")
        if start is None:
            start = span.get("start_char", span.get("start_offset"))
        if end is None:
            end = span.get("end_char", span.get("end_offset"))
        label = span.get("label")
        try:
            start_i = int(start) if start is not None else None
            end_i = int(end) if end is not None else None
        except (TypeError, ValueError):
            start_i = None
            end_i = None
        if start_i is None or end_i is None:
            return None, None, label
        if start_i < 0 or end_i < start_i or end_i > len(text):
            return None, None, label
        return start_i, end_i, label

    if isinstance(span, list) and len(span) >= 3:
        try:
            start_i = int(span[0])
            end_i = int(span[1])
        except (TypeError, ValueError):
            return None, None, None
        label = span[2]
        if start_i < 0 or end_i < start_i or end_i > len(text):
            return None, None, label
        return start_i, end_i, label

    return None, None, None


def _set_span_label(span: Any, new_label: str) -> bool:
    if isinstance(span, dict):
        if not new_label:
            return False
        span["label"] = new_label
        return True
    if isinstance(span, list) and len(span) >= 3:
        span[2] = new_label
        return True
    return False


def _overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)


def _span_overlaps_any(start: int, end: int, spans: List[Tuple[int, int]]) -> bool:
    return any(_overlaps(start, end, s, e) for s, e in spans)


def _any_pattern(pats: Tuple[re.Pattern[str], ...], text: str) -> bool:
    return any(p.search(text) for p in pats)


def _find_absent_stent_mentions(text: str) -> List[Tuple[int, int, str]]:
    mentions: List[Tuple[int, int, str]] = []
    for pat in STENT_ABSENCE_PATTERNS:
        for m in pat.finditer(text):
            try:
                s = m.start("stent")
                e = m.end("stent")
            except IndexError:
                continue
            if s < 0 or e <= s:
                continue
            mentions.append((s, e, pat.pattern))
    return mentions


def _note_has_positive_stent_placement(text: str, absent_mentions: List[Tuple[int, int, str]]) -> bool:
    text_low = text.lower()
    absent_spans = [(s, e) for s, e, _ in absent_mentions]
    for match in re.finditer(r"\bstents?\b", text_low):
        w_start = max(0, match.start() - 40)
        w_end = min(len(text_low), match.end() + 120)
        window = text_low[w_start:w_end]

        if _span_overlaps_any(match.start(), match.end(), absent_spans):
            continue
        if any(v.search(window) for v in POSITIVE_PLACEMENT_VERBS) and not any(
            g.search(window) for g in NEGATION_GUARD_WORDS
        ):
            return True
    return False


def _note_has_stent_intervention(text: str, absent_mentions: List[Tuple[int, int, str]]) -> bool:
    if _note_has_positive_stent_placement(text, absent_mentions):
        return True
    return _any_pattern(STENT_INTERVENTION_PATTERNS, text)


@dataclass(frozen=True)
class _Change:
    record_id: str
    start: int
    end: int
    old_label: str
    new_label: str
    reason: str
    span_text: str
    context: str


@dataclass(frozen=True)
class _Addition:
    record_id: str
    start: int
    end: int
    label: str
    span_text: str
    context: str
    pattern: str


def process_record(
    record: Dict[str, Any],
    *,
    context_window: int,
    add_missing: bool,
    label_present: bool,
) -> Tuple[Dict[str, Any], List[_Change], List[_Addition]]:
    key = _entity_key_for(record)
    if key is None:
        return record, [], []

    text = record.get("text") or ""
    if not isinstance(text, str) or not text:
        return record, [], []

    entities = record.get(key) or []
    if not isinstance(entities, list) or not entities:
        return record, [], []

    rid = _record_id(record)
    absent_mentions = _find_absent_stent_mentions(text)
    absent_spans = [(s, e) for s, e, _ in absent_mentions]
    note_has_intervention = _note_has_stent_intervention(text, absent_mentions)

    changes: List[_Change] = []
    additions: List[_Addition] = []

    existing_spans: List[Tuple[int, int]] = []
    for ent in entities:
        s, e, _ = _normalize_span(ent, text)
        if s is not None and e is not None:
            existing_spans.append((s, e))

    # 1) Relabel existing DEV_STENT -> NEG_STENT (explicit absence)
    # 2) Relabel existing DEV_STENT -> CTX_STENT_PRESENT (stent in place, no intervention)
    for ent in entities:
        start, end, label = _normalize_span(ent, text)
        if label != "DEV_STENT" or start is None or end is None:
            continue

        ctx_start = max(0, start - context_window)
        ctx_end = min(len(text), end + context_window)
        ctx = text[ctx_start:ctx_end].replace("\n", " ")

        new_label: Optional[str] = None
        reason: Optional[str] = None

        if _span_overlaps_any(start, end, absent_spans):
            new_label = "NEG_STENT"
            reason = "explicit_absence"
        elif label_present and (not note_has_intervention) and _any_pattern(HISTORICAL_PATTERNS, ctx):
            new_label = PRESENT_STENT_LABEL
            reason = "present_no_intervention"

        if new_label and new_label != label:
            if _set_span_label(ent, new_label):
                changes.append(
                    _Change(
                        record_id=rid,
                        start=start,
                        end=end,
                        old_label=label,
                        new_label=new_label,
                        reason=reason or "unknown",
                        span_text=text[start:end],
                        context=ctx,
                    )
                )

    # 3) Add missing NEG_STENT spans for explicit absence phrases
    if add_missing:
        seen_absent: set[tuple[int, int]] = set()
        for s, e, pattern in absent_mentions:
            if e > len(text):
                continue
            if (s, e) in seen_absent:
                continue
            seen_absent.add((s, e))
            if _span_overlaps_any(s, e, existing_spans):
                continue

            ctx_start = max(0, s - context_window)
            ctx_end = min(len(text), e + context_window)
            ctx = text[ctx_start:ctx_end].replace("\n", " ")

            entities.append(
                {
                    "label": "NEG_STENT",
                    "start": s,
                    "end": e,
                    "text": text[s:e],
                }
            )
            existing_spans.append((s, e))
            additions.append(
                _Addition(
                    record_id=rid,
                    start=s,
                    end=e,
                    label="NEG_STENT",
                    span_text=text[s:e],
                    context=ctx,
                    pattern=pattern,
                )
            )

    # Keep entities stable-ish: only resort if we have dict spans with start/end.
    # (List spans are already positional and mixed formats exist in the repo.)
    def _sort_key(ent: Any) -> int:
        s, _, _ = _normalize_span(ent, text)
        return s if s is not None else 0

    record[key] = sorted(entities, key=_sort_key)
    return record, changes, additions


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError(f"Input JSONL not found: {args.input}")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)

    all_changes: List[Dict[str, Any]] = []
    all_additions: List[Dict[str, Any]] = []
    total_records = 0
    total_dev_stent_spans = 0

    out_f = args.output.open("w", encoding="utf-8") if args.write else None
    try:
        for record in _iter_jsonl(args.input, limit=args.limit):
            total_records += 1

            key = _entity_key_for(record)
            if key and isinstance(record.get(key), list):
                for ent in record[key]:
                    _, _, label = _normalize_span(ent, record.get("text") or "")
                    if label == "DEV_STENT":
                        total_dev_stent_spans += 1

            updated, changes, additions = process_record(
                record,
                context_window=int(args.context_window),
                add_missing=not bool(args.no_add_missing),
                label_present=not bool(args.no_label_present),
            )

            if args.write and out_f is not None:
                out_f.write(json.dumps(updated) + "\n")

            all_changes.extend([c.__dict__ for c in changes])
            all_additions.extend([a.__dict__ for a in additions])
    finally:
        if out_f is not None:
            out_f.close()

    relabel_to_neg = sum(1 for c in all_changes if c.get("new_label") == "NEG_STENT")
    relabel_to_present = sum(1 for c in all_changes if c.get("new_label") == PRESENT_STENT_LABEL)

    report = {
        "input": str(args.input),
        "output": str(args.output) if args.write else None,
        "present_label": None if args.no_label_present else PRESENT_STENT_LABEL,
        "total_records": total_records,
        "total_dev_stent_spans_seen": total_dev_stent_spans,
        "dev_stent_relabelled_total": len(all_changes),
        "dev_stent_relabelled_to_neg_stent": relabel_to_neg,
        "dev_stent_relabelled_to_present_label": relabel_to_present,
        "neg_stent_added": len(all_additions),
        "changes": all_changes,
        "additions": all_additions,
        "notes": [
            "This script is heuristic; review the report JSON before regenerating BIO.",
            "NEG_STENT is intended for explicit stent absence (no stent placed/needed/indicated).",
            "Stent removal/exchange/migration is intentionally NOT labeled as NEG_STENT.",
        ],
    }

    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"[neg_stent] records={total_records} dev_stent_spans={total_dev_stent_spans}")
    print(
        f"[neg_stent] relabelled_total={len(all_changes)} "
        f"to_neg={relabel_to_neg} to_present={relabel_to_present} "
        f"added_neg={len(all_additions)}"
    )
    print(f"[neg_stent] report: {args.report}")
    if args.write:
        print(f"[neg_stent] wrote:  {args.output}")
    else:
        print("[neg_stent] dry-run (no dataset written); pass --write to write --output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
