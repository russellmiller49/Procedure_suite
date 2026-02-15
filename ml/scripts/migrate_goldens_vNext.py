#!/usr/bin/env python3
"""Migrate legacy golden fixtures to vNext evidence-quote fixtures (pending review).

Phase 4 goal (AI_ARCHITECTURE_UPGRADE_GUIDE_UPDATED):
- Create vNext fixtures that store quote context (prefix/quote/suffix) without spans.
- Produce an HTML diff report for human approval.

Safety:
- Never modifies legacy goldens.
- Never prints note text (only ids/counts).
- Treats all input as potentially sensitive even if scrubbed.

This script is designed to run even when legacy fixtures aren't present in the repo;
point --input-dir at your local golden directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")
_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


def _safe_filename(raw: str, *, max_len: int = 160) -> str:
    cleaned = _SAFE_FILENAME_RE.sub("_", (raw or "").strip()).strip("._-")
    if not cleaned:
        cleaned = "unknown"
    if len(cleaned) <= max_len:
        return cleaned
    # Preserve uniqueness with a hash suffix.
    digest = hashlib.sha1(cleaned.encode("utf-8")).hexdigest()[:10]  # noqa: S324 - non-crypto use
    return f"{cleaned[: max_len - 12]}__{digest}"


def _normalize_code(code: str) -> str:
    raw = (code or "").strip()
    if not raw:
        return ""
    return raw.lstrip("+").strip()


def _iter_fixture_files(input_dir: Path, pattern: str) -> Iterable[Path]:
    if input_dir.is_file():
        yield input_dir
        return
    if not input_dir.exists() or not input_dir.is_dir():
        return
    yield from sorted(input_dir.glob(pattern))


def _load_entries(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    if isinstance(data, dict):
        # Some datasets wrap entries under a key.
        for key in ("entries", "records", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return [d for d in value if isinstance(d, dict)]
        return [data]
    raise ValueError(f"Unrecognized fixture JSON shape in {path}")


def _extract_note_text(entry: dict[str, Any]) -> str:
    for key in ("note_text", "note", "text", "raw_text"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _extract_note_id(entry: dict[str, Any]) -> str | None:
    registry = entry.get("registry_entry")
    if isinstance(registry, dict):
        for key in ("patient_mrn", "note_id", "patient_id"):
            value = registry.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    for key in ("note_id", "noteId", "id"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_expected_codes(entry: dict[str, Any]) -> list[str]:
    for key in ("cpt_codes", "codes", "expected_codes"):
        value = entry.get(key)
        if isinstance(value, list):
            out: list[str] = []
            for item in value:
                if isinstance(item, str):
                    norm = _normalize_code(item)
                    if norm:
                        out.append(norm)
            return sorted(set(out))
    return []


def _word_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in _WORD_RE.finditer(text or "")]


def _context_three_words(text: str, start: int, end: int) -> tuple[str, str]:
    """Return (prefix_3_words, suffix_3_words) around [start,end)."""
    spans = _word_spans(text)
    if not spans:
        return "", ""

    # Find the first word whose end is > start, and the first word whose start is >= end.
    prev_words: list[str] = []
    next_words: list[str] = []

    # Build prefix words (last 3 words fully before start).
    for s, e in spans:
        if e <= start:
            prev_words.append(text[s:e])
        else:
            break
    prefix = " ".join(prev_words[-3:]).strip()

    # Build suffix words (first 3 words fully after end).
    for s, e in spans:
        if s >= end:
            next_words.append(text[s:e])
            if len(next_words) >= 3:
                break
    suffix = " ".join(next_words[:3]).strip()
    return prefix, suffix


def _looks_like_leaf_evidence_dict(value: dict[str, Any]) -> bool:
    keys = set(value.keys())
    interesting = {"quote", "text", "snippet", "rationale", "span", "start", "end"}
    return bool(keys.intersection(interesting))


@dataclass(frozen=True)
class LegacyEvidenceItem:
    path: str
    legacy: Any
    legacy_text: str


def _iter_legacy_evidence_items(value: Any, *, path: str) -> Iterable[LegacyEvidenceItem]:
    if isinstance(value, str):
        s = value.strip()
        if s:
            yield LegacyEvidenceItem(path=path, legacy=value, legacy_text=s)
        return

    if isinstance(value, dict):
        if _looks_like_leaf_evidence_dict(value):
            # Prefer the most "rationale-like" string for display.
            legacy_text = ""
            for key in ("rationale", "quote", "text", "snippet"):
                v = value.get(key)
                if isinstance(v, str) and v.strip():
                    legacy_text = v.strip()
                    break
            if not legacy_text:
                legacy_text = json.dumps(value, ensure_ascii=False, sort_keys=True)
            yield LegacyEvidenceItem(path=path, legacy=value, legacy_text=legacy_text)
            return

        for k, v in value.items():
            child_path = f"{path}/{k}"
            yield from _iter_legacy_evidence_items(v, path=child_path)
        return

    if isinstance(value, list):
        for idx, item in enumerate(value):
            yield from _iter_legacy_evidence_items(item, path=f"{path}/{idx}")
        return


def _extract_span_from_legacy_obj(legacy: Any) -> tuple[int, int] | None:
    """Best-effort extract (start,end) from a legacy evidence object."""
    if not isinstance(legacy, dict):
        return None

    # Common shapes: {"span":[s,e]} or {"start":s,"end":e} or {"start":...,"stop":...}
    span = legacy.get("span")
    if isinstance(span, list | tuple) and len(span) == 2:
        try:
            s = int(span[0])
            e = int(span[1])
            if e > s >= 0:
                return s, e
        except Exception:
            return None

    for a, b in (("start", "end"), ("start", "stop"), ("begin", "end")):
        if a in legacy and b in legacy:
            try:
                s = int(legacy[a])
                e = int(legacy[b])
                if e > s >= 0:
                    return s, e
            except Exception:
                return None

    return None


def _extract_quote_from_legacy_obj(legacy: Any) -> str | None:
    if isinstance(legacy, str):
        return legacy.strip() or None
    if not isinstance(legacy, dict):
        return None
    for key in ("quote", "text", "snippet"):
        v = legacy.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _extract_rationale_from_legacy_obj(legacy: Any, fallback: str) -> str:
    if isinstance(legacy, dict):
        v = legacy.get("rationale")
        if isinstance(v, str) and v.strip():
            return v.strip()
    return (fallback or "").strip()


def _build_llm_windows(text: str, rationale: str, *, max_total_chars: int = 3500) -> str:
    """Build a reduced context for LLM (best-effort) by keyword windows."""
    doc = text or ""
    rat = (rationale or "").strip()
    if not doc or not rat:
        return doc[:max_total_chars]

    tokens = [
        t.lower()
        for t in re.findall(r"[A-Za-z0-9]{4,}", rat)
        if t.lower() not in {"performed", "procedure", "patient", "report", "noted", "not", "none"}
    ]
    tokens = list(dict.fromkeys(tokens))[:12]
    if not tokens:
        return doc[:max_total_chars]

    doc_lower = doc.lower()
    hits: list[int] = []
    for tok in tokens:
        idx = doc_lower.find(tok)
        if idx >= 0:
            hits.append(idx)
    if not hits:
        return doc[:max_total_chars]

    windows: list[tuple[int, int]] = []
    for idx in sorted(hits)[:24]:
        s = max(0, idx - 420)
        e = min(len(doc), idx + 420)
        windows.append((s, e))

    # Merge overlaps.
    merged: list[tuple[int, int]] = []
    for s, e in sorted(windows):
        if not merged or s > merged[-1][1]:
            merged.append((s, e))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))

    out_chunks: list[str] = []
    total = 0
    for s, e in merged:
        chunk = doc[s:e]
        if total + len(chunk) > max_total_chars:
            remaining = max_total_chars - total
            if remaining <= 0:
                break
            chunk = chunk[:remaining]
        out_chunks.append(chunk)
        total += len(chunk)
        if total >= max_total_chars:
            break

    return "\n...\n".join(out_chunks)


@dataclass(frozen=True)
class MigratedEvidenceItem:
    path: str
    legacy_text: str
    draft: dict[str, Any] | None
    method: str
    warnings: list[str]


def _migrate_evidence_item(
    *,
    item: LegacyEvidenceItem,
    note_text: str,
    use_llm: bool,
    anchor_quote_fn: Callable[[str, str], Any],
) -> MigratedEvidenceItem:
    warnings: list[str] = []
    legacy_obj = item.legacy
    rationale = _extract_rationale_from_legacy_obj(legacy_obj, item.legacy_text)

    span = _extract_span_from_legacy_obj(legacy_obj)
    if span:
        s, e = span
        if 0 <= s < e <= len(note_text):
            quote = note_text[s:e]
            prefix, suffix = _context_three_words(note_text, s, e)
            draft = {
                "rationale": rationale,
                "prefix_3_words": prefix,
                "exact_quote": quote,
                "suffix_3_words": suffix,
            }
            return MigratedEvidenceItem(
                path=item.path,
                legacy_text=item.legacy_text,
                draft=draft,
                method="span",
                warnings=warnings,
            )
        warnings.append("legacy span out of bounds")

    quote_candidate = _extract_quote_from_legacy_obj(legacy_obj)
    if quote_candidate:
        anchored = anchor_quote_fn(note_text, quote_candidate)
        if anchored.span is not None:
            s = int(anchored.span.start)
            e = int(anchored.span.end)
            prefix, suffix = _context_three_words(note_text, s, e)
            draft = {
                "rationale": rationale,
                "prefix_3_words": prefix,
                "exact_quote": anchored.span.text,
                "suffix_3_words": suffix,
            }
            method = f"anchor_{anchored.method.value}"
            if anchored.method.value != "exact":
                warnings.append(f"anchored via {anchored.method.value}")
            return MigratedEvidenceItem(
                path=item.path,
                legacy_text=item.legacy_text,
                draft=draft,
                method=method,
                warnings=warnings,
            )
        warnings.append("quote not anchorable")

    # LLM-assisted quote rewrite (optional).
    if use_llm:
        try:
            from app.common.llm import LLMService  # imported lazily to avoid side effects
            from proc_schemas.registry.ip_vnext_draft import EvidenceQuoteDraft

            llm = LLMService(task="structurer")
            windows = _build_llm_windows(note_text, rationale)
            system_prompt = (
                "You are migrating legacy evidence rationales into exact evidence quotes.\n"
                "Rules:\n"
                "- Return ONLY JSON matching the schema.\n"
                "- exact_quote MUST be copied verbatim from the provided redacted text.\n"
                "- Choose the shortest quote that directly supports the rationale.\n"
                "- prefix_3_words and suffix_3_words must be words from the redacted text "
                "adjacent to the quote.\n"
            )
            user_prompt = (
                f"LEGACY_RATIONALE:\n{rationale}\n\n"
                "REDACTED_TEXT_SNIPPETS:\n"
                f"{windows}\n"
            )
            draft_model = llm.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=EvidenceQuoteDraft,
                temperature=0.0,
            )

            # Trust only the quote; recompute context to ensure fidelity.
            candidate_quote = (draft_model.exact_quote or "").strip()
            if candidate_quote and candidate_quote in note_text:
                s = note_text.find(candidate_quote)
                e = s + len(candidate_quote)
                prefix, suffix = _context_three_words(note_text, s, e)
                draft = {
                    "rationale": (draft_model.rationale or rationale).strip() or rationale,
                    "prefix_3_words": prefix,
                    "exact_quote": candidate_quote,
                    "suffix_3_words": suffix,
                    "confidence": draft_model.confidence.value if draft_model.confidence else None,
                }
                return MigratedEvidenceItem(
                    path=item.path,
                    legacy_text=item.legacy_text,
                    draft=draft,
                    method="llm",
                    warnings=warnings,
                )
            warnings.append("llm_quote_not_substring")
        except Exception as exc:
            warnings.append(f"llm_failed:{type(exc).__name__}")

    return MigratedEvidenceItem(
        path=item.path,
        legacy_text=item.legacy_text,
        draft=None,
        method="unmigrated",
        warnings=warnings,
    )


def _html_escape(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _write_html_report(
    *,
    report_path: Path,
    cases: Sequence[dict[str, Any]],
    stats: dict[str, Any],
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[str] = []
    for case in cases:
        note_id = str(case.get("note_id") or "")
        case_id = str(case.get("case_id") or "")
        source = str(case.get("source_file") or "")
        migrated = case.get("migrated_evidence") or []
        migrated_count = sum(1 for m in migrated if isinstance(m, dict) and m.get("draft"))
        total_count = len(migrated) if isinstance(migrated, list) else 0

        items_html: list[str] = []
        for m in migrated:
            if not isinstance(m, dict):
                continue
            path = _html_escape(str(m.get("path") or ""))
            method = _html_escape(str(m.get("method") or ""))
            warnings = m.get("warnings") or []
            if isinstance(warnings, list):
                warnings_str = ", ".join(str(w) for w in warnings)
            else:
                warnings_str = str(warnings)
            warnings_html = (
                f" · <span class='warn'>{_html_escape(warnings_str)}</span>" if warnings_str else ""
            )

            legacy_text = _html_escape(str(m.get("legacy_text") or ""))
            draft = m.get("draft")
            if isinstance(draft, dict):
                prefix = _html_escape(str(draft.get("prefix_3_words") or ""))
                quote = _html_escape(str(draft.get("exact_quote") or ""))
                suffix = _html_escape(str(draft.get("suffix_3_words") or ""))
                rationale = _html_escape(str(draft.get("rationale") or ""))
                draft_html = (
                    f"<div class='draft'>"
                    f"<div><b>rationale</b>: {rationale}</div>"
                    f"<div><b>prefix</b>: {prefix}</div>"
                    f"<div><b>quote</b>: <code>{quote}</code></div>"
                    f"<div><b>suffix</b>: {suffix}</div>"
                    f"</div>"
                )
            else:
                draft_html = "<div class='draft missing'>(unmigrated)</div>"

            meta_html = (
                f"<div class='meta'><code>{path}</code> · <span class='method'>{method}</span>"
                f"{warnings_html}</div>"
            )
            items_html.append(
                "<div class='evi'>"
                f"{meta_html}"
                f"<div class='legacy'><b>legacy</b>: {legacy_text}</div>"
                f"{draft_html}"
                "</div>"
            )

        title = _html_escape(note_id or case_id)
        source_html = _html_escape(source)
        header_html = (
            f"<h2>{title} <span class='subtle'>({migrated_count}/{total_count} migrated) · "
            f"{source_html}</span></h2>"
        )
        rows.append(
            "<section class='case'>"
            f"{header_html}"
            + "".join(items_html)
            + "</section>"
        )

    cases_count = int(stats.get("cases", 0))
    evidence_count = int(stats.get("evidence_items", 0))
    migrated_count = int(stats.get("migrated_items", 0))
    html_lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8"/>',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>',
        "  <title>vNext Golden Migration Report</title>",
        "  <style>",
        "    body {",
        "      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;",
        "      margin: 16px;",
        "      color: #0f172a;",
        "    }",
        "    h1 { margin: 0 0 8px 0; font-size: 18px; }",
        "    .subtle { color: #64748b; font-weight: 400; font-size: 12px; }",
        "    .summary {",
        "      padding: 10px 12px;",
        "      background: #f8fafc;",
        "      border: 1px solid #e2e8f0;",
        "      border-radius: 10px;",
        "      margin-bottom: 14px;",
        "    }",
        "    .case {",
        "      border: 1px solid #e2e8f0;",
        "      border-radius: 12px;",
        "      padding: 12px;",
        "      margin-bottom: 12px;",
        "    }",
        "    .case h2 { margin: 0 0 10px 0; font-size: 14px; }",
        "    .evi { border-top: 1px solid #e2e8f0; padding-top: 10px; margin-top: 10px; }",
        "    .meta { font-size: 12px; color: #334155; margin-bottom: 4px; }",
        "    .legacy, .draft { font-size: 12px; line-height: 1.4; }",
        "    code { background: #0b1220; color: #e2e8f0; padding: 2px 6px; border-radius: 6px; }",
        "    .method { color: #0f766e; }",
        "    .warn { color: #b45309; }",
        "    .draft.missing { color: #b91c1c; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <h1>vNext Golden Migration Report</h1>",
        '  <div class="summary">',
        (
            f"    <div><b>Cases</b>: {cases_count} · <b>Evidence items</b>: {evidence_count} · "
            f"<b>Migrated</b>: {migrated_count}</div>"
        ),
        (
            "    <div class=\"subtle\">Review pending fixtures, then move approved JSON files "
            "from <code>.../pending/</code> to <code>.../approved/</code>.</div>"
        ),
        (
            "    <div class=\"subtle\">Report generated by "
            "<code>ml/scripts/migrate_goldens_vNext.py</code>. Re-run to refresh.</div>"
        ),
        "  </div>",
        f"  {''.join(rows)}",
        "</body>",
        "</html>",
        "",
    ]
    report_path.write_text("\n".join(html_lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Migrate legacy golden fixtures to vNext (pending review)."
    )
    p.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_final"),
        help="Directory containing legacy golden_*.json (arrays) OR a single JSON file.",
    )
    p.add_argument(
        "--pattern",
        type=str,
        default="golden_*.json",
        help="Glob pattern for fixture files when --input-dir is a directory.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_vNext/pending"),
        help="Directory to write per-case pending vNext fixtures.",
    )
    p.add_argument(
        "--report-path",
        type=Path,
        default=Path("data/knowledge/golden_extractions_vNext/migration_report.html"),
        help="Path to write the HTML diff report.",
    )
    p.add_argument(
        "--stats-path",
        type=Path,
        default=Path("data/knowledge/golden_extractions_vNext/migration_stats.json"),
        help="Path to write a small JSON stats summary.",
    )
    p.add_argument("--limit", type=int, default=0, help="Max cases to migrate (0 = no limit).")
    p.add_argument(
        "--use-llm",
        action="store_true",
        help=(
            "Enable LLM-assisted quote rewrite for evidence items that can't be migrated "
            "deterministically."
        ),
    )
    p.add_argument(
        "--llm-allow-stub",
        action="store_true",
        help="Allow running with stub LLM (not recommended; only for wiring tests).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    fixture_files = list(_iter_fixture_files(args.input_dir, args.pattern))
    if not fixture_files:
        print(f"migrate_goldens_vNext: no fixture files found under {args.input_dir}; skipping.")
        return 0

    from app.evidence.quote_anchor import anchor_quote

    use_llm = bool(args.use_llm)
    if use_llm and not args.llm_allow_stub:
        # Avoid accidental stub usage which would create nonsense quotes.
        if os.getenv("OPENAI_OFFLINE") or os.getenv("GEMINI_OFFLINE") or os.getenv(
            "REGISTRY_USE_STUB_LLM"
        ):
            print(
                "migrate_goldens_vNext: LLM appears offline/stubbed; re-run with "
                "--llm-allow-stub to force."
            )
            return 2
        provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        if provider == "openai_compat" and not os.getenv("OPENAI_API_KEY"):
            print(
                "migrate_goldens_vNext: OPENAI_API_KEY not set; refusing LLM migration without "
                "--llm-allow-stub."
            )
            return 2
        if provider == "gemini" and not os.getenv("GEMINI_API_KEY"):
            print(
                "migrate_goldens_vNext: GEMINI_API_KEY not set; refusing LLM migration without "
                "--llm-allow-stub."
            )
            return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)

    migrated_cases: list[dict[str, Any]] = []
    cases = 0
    evidence_items = 0
    migrated_items = 0

    for path in fixture_files:
        try:
            entries = _load_entries(path)
        except Exception as exc:
            print(f"migrate_goldens_vNext: failed to load {path}: {type(exc).__name__}")
            continue

        for idx, entry in enumerate(entries):
            note_text = _extract_note_text(entry)
            if not note_text.strip():
                continue

            note_id = _extract_note_id(entry)
            expected_codes = _extract_expected_codes(entry)

            registry_entry = entry.get("registry_entry")
            legacy_evidence = None
            if isinstance(registry_entry, dict):
                legacy_evidence = registry_entry.get("evidence")

            if legacy_evidence is not None:
                legacy_items = list(
                    _iter_legacy_evidence_items(legacy_evidence, path="/registry_entry/evidence")
                )
            else:
                legacy_items = []

            migrated_evidence: list[dict[str, Any]] = []
            for legacy_item in legacy_items:
                evidence_items += 1
                migrated = _migrate_evidence_item(
                    item=legacy_item,
                    note_text=note_text,
                    use_llm=use_llm,
                    anchor_quote_fn=anchor_quote,
                )
                if migrated.draft is not None:
                    migrated_items += 1
                migrated_evidence.append(
                    {
                        "path": migrated.path,
                        "legacy_text": migrated.legacy_text,
                        "draft": migrated.draft,
                        "method": migrated.method,
                        "warnings": migrated.warnings,
                    }
                )

            case_id = _safe_filename(f"{note_id or 'unknown'}__{path.name}__{idx}")
            out_path = args.output_dir / f"{case_id}.json"

            # Keep registry_entry but drop legacy evidence to reduce duplication/noise.
            registry_no_evidence: dict[str, Any] | None = None
            if isinstance(registry_entry, dict):
                registry_no_evidence = {k: v for k, v in registry_entry.items() if k != "evidence"}

            case_obj = {
                "schema_version": "vnext_fixture_v1",
                "case_id": case_id,
                "note_id": note_id,
                "source_file": path.name,
                "source_record_index": idx,
                "note_text": note_text,
                "expected_cpt_codes": expected_codes,
                "registry_entry": registry_no_evidence,
                "migrated_evidence": migrated_evidence,
            }

            out_path.write_text(
                json.dumps(case_obj, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            migrated_cases.append(
                {
                    "case_id": case_obj.get("case_id"),
                    "note_id": case_obj.get("note_id"),
                    "source_file": case_obj.get("source_file"),
                    "migrated_evidence": case_obj.get("migrated_evidence"),
                }
            )

            cases += 1
            if args.limit and cases >= int(args.limit):
                break
        if args.limit and cases >= int(args.limit):
            break

    stats = {
        "cases": cases,
        "evidence_items": evidence_items,
        "migrated_items": migrated_items,
        "input_dir": str(args.input_dir),
        "output_dir": str(args.output_dir),
        "use_llm": use_llm,
    }
    args.stats_path.parent.mkdir(parents=True, exist_ok=True)
    args.stats_path.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_html_report(report_path=args.report_path, cases=migrated_cases, stats=stats)

    print(
        f"migrate_goldens_vNext: cases={cases} evidence_items={evidence_items} "
        f"migrated_items={migrated_items}"
    )
    print(f"migrate_goldens_vNext: output_dir={args.output_dir}")
    print(f"migrate_goldens_vNext: report={args.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
