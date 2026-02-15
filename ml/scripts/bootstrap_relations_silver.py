#!/usr/bin/env python3
"""Bootstrap a "silver" relations dataset from bundle outputs (Phase 8).

Inputs:
- One or more JSON files containing `POST /api/v1/process_bundle` responses.
  (The repo may not include these fixtures; point --input at your local exports.)

Outputs:
- JSONL tasks suitable for a fast approve/reject loop (e.g., Prodigy `mark --view-id choice`).

Safety:
- Never prints note text.
- Treats all inputs as potentially sensitive even if scrubbed; log only counts/paths.

Optional:
- `--use-llm` can add additional relation proposals from an LLM. This is OFF by default and
  refuses to run in offline/stub mode unless `--llm-allow-stub` is set.
"""

from __future__ import annotations

import argparse
import json
import hashlib
import os
import sys
from pathlib import Path
from typing import Any, Iterable

# Ensure repo root is importable when running as a file.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import BaseModel, Field  # noqa: E402

from app.agents.aggregator.timeline_aggregator import LinkProposal  # noqa: E402
from app.agents.relation_extraction.shadow_mode import (  # noqa: E402
    merge_relations_shadow_mode,
)


def _iter_json_files(input_path: Path, pattern: str) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return
    if not input_path.exists() or not input_path.is_dir():
        return
    yield from sorted(input_path.glob(pattern))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _as_list(value: Any) -> list[Any] | None:
    return value if isinstance(value, list) else None


def _edge_tasks(
    *,
    case_id: str,
    source_path: str,
    entities_by_id: dict[str, dict[str, Any]],
    edges: Iterable[LinkProposal],
    edge_source: str,
    seen_edge_ids: set[str] | None = None,
) -> Iterable[dict[str, Any]]:
    options = [
        {"id": "accept", "text": "Accept"},
        {"id": "reject", "text": "Reject"},
    ]
    for edge in edges:
        src = entities_by_id.get(str(edge.entity_id)) or {}
        dst = entities_by_id.get(str(edge.linked_to_id)) or {}
        text = f"{src.get('label','?')}  ->({edge.relation})->  {dst.get('label','?')}"
        edge_key = f"{case_id}|{edge.entity_id}|{edge.relation}|{edge.linked_to_id}"
        edge_id = hashlib.sha256(edge_key.encode("utf-8")).hexdigest()[:16]
        if seen_edge_ids is not None:
            if edge_id in seen_edge_ids:
                continue
            seen_edge_ids.add(edge_id)
        yield {
            "_view_id": "choice",
            "text": text,
            "options": options,
            "meta": {
                "edge_id": edge_id,
                "case_id": case_id,
                "source_path": source_path,
                "edge_source": edge_source,
                "relation": edge.relation,
                "confidence": float(edge.confidence),
                "source_entity_id": str(edge.entity_id),
                "target_entity_id": str(edge.linked_to_id),
                "source_kind": str(src.get("kind") or ""),
                "target_kind": str(dst.get("kind") or ""),
            },
            "edge": edge.model_dump(),
            "source_entity": src,
            "target_entity": dst,
        }


class _LLMProposalBundle(BaseModel):
    proposals: list[LinkProposal] = Field(default_factory=list)


def _llm_proposals_for_case(
    *,
    entities: list[dict[str, Any]],
    heuristic_edges: list[LinkProposal],
) -> list[LinkProposal]:
    canonical = [e for e in entities if str(e.get("kind") or "") == "canonical_lesion"]
    if not canonical:
        return []

    missing: list[str] = []
    for e in entities:
        kind = str(e.get("kind") or "")
        eid = str(e.get("entity_id") or "")
        if not eid:
            continue
        if kind == "nav_target":
            has_link = any(
                edge.entity_id == eid and edge.relation == "linked_to_lesion"
                for edge in heuristic_edges
            )
            if not has_link:
                missing.append(eid)
        if kind == "specimen":
            has_link = any(
                edge.entity_id == eid and edge.relation == "specimen_from_lesion"
                for edge in heuristic_edges
            )
            if not has_link:
                missing.append(eid)

    if not missing:
        return []

    # Lazy import to avoid side effects when LLM mode is off.
    from app.common.llm import LLMService

    llm = LLMService(task="judge")
    system_prompt = (
        "You propose cross-document clinical relations from entity labels/attributes.\n"
        "Return ONLY JSON.\n"
        "Rules:\n"
        "- Use ONLY entity_ids provided.\n"
        "- Only propose relations:\n"
        "  - linked_to_lesion: nav_target -> canonical_lesion\n"
        "  - specimen_from_lesion: specimen -> canonical_lesion\n"
        "- confidence must be a number 0.0-1.0.\n"
        "- reasoning_short must be <= 12 words.\n"
        "- If you are not confident, omit the proposal.\n"
    )
    canonical_lesions = [
        {"entity_id": e.get("entity_id"), "label": e.get("label")} for e in canonical
    ]
    user_prompt = json.dumps(
        {
            "entities": entities,
            "missing_entity_ids": missing,
            "canonical_lesions": canonical_lesions,
        },
        ensure_ascii=False,
    )

    bundle = llm.generate_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=_LLMProposalBundle,
        temperature=0.0,
    )

    # Filter invalid ids defensively.
    valid_ids = {str(e.get("entity_id") or "") for e in entities if str(e.get("entity_id") or "")}
    out: list[LinkProposal] = []
    for p in bundle.proposals:
        if p.entity_id not in valid_ids or p.linked_to_id not in valid_ids:
            continue
        out.append(p)
    return out


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bootstrap silver relations tasks from bundle outputs.")
    p.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Directory containing JSON bundle outputs OR a single JSON file.",
    )
    p.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="Glob pattern when --input is a directory.",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("data/ml_training/relations_silver_tasks.jsonl"),
        help="Output JSONL path for tasks.",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max input files to process (0 = no limit).",
    )
    p.add_argument("--use-llm", action="store_true", help="Add optional LLM relation proposals.")
    p.add_argument(
        "--llm-allow-stub",
        action="store_true",
        help="Allow running in offline/stub LLM mode (not recommended).",
    )
    p.add_argument(
        "--ml-threshold",
        type=float,
        default=0.85,
        help="Confidence threshold for preferring ML edges during merge.",
    )
    p.add_argument(
        "--edge-sources",
        type=str,
        default="merged",
        help="Comma-separated sources to export: merged,heuristic,ml,all (default: merged).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    files = list(_iter_json_files(args.input, args.pattern))
    if not files:
        print(f"bootstrap_relations_silver: no inputs found under {args.input}; skipping.")
        return 0

    use_llm = bool(args.use_llm)
    if use_llm and not args.llm_allow_stub:
        if os.getenv("REGISTRY_USE_STUB_LLM"):
            print(
                "bootstrap_relations_silver: REGISTRY_USE_STUB_LLM is enabled; re-run with "
                "--llm-allow-stub to force."
            )
            return 2

        provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        if provider == "openai_compat":
            if os.getenv("OPENAI_OFFLINE") or not os.getenv("OPENAI_API_KEY"):
                print(
                    "bootstrap_relations_silver: OPENAI appears offline/unconfigured; re-run "
                    "with --llm-allow-stub to force."
                )
                return 2
        if provider == "gemini":
            if os.getenv("GEMINI_OFFLINE") or not os.getenv("GEMINI_API_KEY"):
                print(
                    "bootstrap_relations_silver: GEMINI appears offline/unconfigured; re-run "
                    "with --llm-allow-stub to force."
                )
                return 2
        if provider not in {"openai_compat", "gemini"}:
            print(
                "bootstrap_relations_silver: LLM appears offline/stubbed; re-run with "
                "--llm-allow-stub to force."
            )
            return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)

    tasks_written = 0
    files_used = 0

    with open(args.output, "w", encoding="utf-8") as out:
        for path in files:
            if args.limit and files_used >= int(args.limit):
                break
            files_used += 1

            try:
                obj = _load_json(path)
            except Exception:
                continue
            root = _as_dict(obj)
            if root is None:
                continue

            episode_id = str(root.get("episode_id") or "")
            zk_patient_id = str(root.get("zk_patient_id") or "")
            case_id = episode_id or zk_patient_id or path.stem

            ledger = _as_dict(root.get("entity_ledger")) or {}
            entities = _as_list(ledger.get("entities")) or []
            entities_by_id: dict[str, dict[str, Any]] = {}
            for e in entities:
                if not isinstance(e, dict):
                    continue
                eid = str(e.get("entity_id") or "")
                if eid:
                    entities_by_id[eid] = e

            # Prefer Phase 8 fields if present; otherwise fall back to ledger link_proposals.
            heur_edges_raw = root.get("relations_heuristic")
            if heur_edges_raw is None:
                heur_edges_raw = ledger.get("link_proposals")
            ml_edges_raw = root.get("relations_ml") or []

            heuristic_edges = [
                LinkProposal.model_validate(x)
                for x in (_as_list(heur_edges_raw) or [])
                if isinstance(x, dict)
            ]
            ml_edges = [
                LinkProposal.model_validate(x)
                for x in (_as_list(ml_edges_raw) or [])
                if isinstance(x, dict)
            ]

            valid_ids = set(entities_by_id.keys())
            heuristic_edges = [
                e
                for e in heuristic_edges
                if e.entity_id in valid_ids and e.linked_to_id in valid_ids
            ]
            ml_edges = [e for e in ml_edges if e.entity_id in valid_ids and e.linked_to_id in valid_ids]

            llm_edges: list[LinkProposal] = []
            if use_llm:
                llm_edges = _llm_proposals_for_case(
                    entities=list(entities_by_id.values()),
                    heuristic_edges=heuristic_edges,
                )

            shadow = merge_relations_shadow_mode(
                relations_heuristic=heuristic_edges,
                relations_ml=ml_edges + llm_edges,
                confidence_threshold=float(args.ml_threshold),
            )

            sources_raw = str(args.edge_sources or "").strip().lower()
            selected_sources: set[str]
            if not sources_raw or sources_raw == "merged":
                selected_sources = {"merged"}
            elif sources_raw == "all":
                selected_sources = {"merged", "heuristic", "ml"}
            else:
                selected_sources = {s.strip() for s in sources_raw.split(",") if s.strip()}
                selected_sources &= {"merged", "heuristic", "ml"}
                if not selected_sources:
                    selected_sources = {"merged"}

            edges_by_source: dict[str, list[LinkProposal]] = {
                "heuristic": list(heuristic_edges),
                "ml": list(ml_edges + llm_edges),
                "merged": list(shadow.relations),
            }
            seen_edge_ids: set[str] = set()
            for source in ("merged", "heuristic", "ml"):
                if source not in selected_sources:
                    continue
                for task in _edge_tasks(
                    case_id=case_id,
                    source_path=str(path),
                    entities_by_id=entities_by_id,
                    edges=edges_by_source[source],
                    edge_source=source,
                    seen_edge_ids=seen_edge_ids,
                ):
                    out.write(json.dumps(task, ensure_ascii=False) + "\n")
                    tasks_written += 1

    print(
        f"bootstrap_relations_silver: files={files_used} tasks={tasks_written} output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
