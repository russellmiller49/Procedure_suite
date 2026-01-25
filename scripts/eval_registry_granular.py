#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from modules.common.exceptions import LLMError
from modules.registry.pipelines.v3_pipeline import run_v3_extraction
from modules.registry.schema.ip_v3_extraction import IPRegistryV3, ProcedureEvent


def _norm(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value.lower() if value else None


def _event_key(event: ProcedureEvent) -> tuple[str, str | None, str | None]:
    station = _norm(event.target.station if event.target else None)
    lobe = _norm(event.target.lobe if event.target else None)
    return (_norm(event.type) or "", station, lobe)


@dataclass(frozen=True)
class ScoreResult:
    tp: int
    fp: int
    fn: int

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        if denom == 0:
            return 1.0 if self.fn == 0 else 0.0
        return self.tp / denom

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        if denom == 0:
            return 1.0
        return self.tp / denom


class RegistryGranularScorer:
    def score(self, gold: IPRegistryV3, pred: IPRegistryV3) -> tuple[ScoreResult, dict]:
        gold_counts = Counter(_event_key(e) for e in gold.procedures)
        pred_counts = Counter(_event_key(e) for e in pred.procedures)

        tp = sum(min(gold_counts[k], pred_counts.get(k, 0)) for k in gold_counts)
        gold_total = sum(gold_counts.values())
        pred_total = sum(pred_counts.values())
        fp = pred_total - tp
        fn = gold_total - tp

        missing = []
        extra = []
        for k, c in (gold_counts - pred_counts).items():
            missing.append({"key": list(k), "count": c})
        for k, c in (pred_counts - gold_counts).items():
            extra.append({"key": list(k), "count": c})

        details = {
            "gold_event_count": gold_total,
            "pred_event_count": pred_total,
            "missing": missing,
            "extra": extra,
        }
        return ScoreResult(tp=tp, fp=fp, fn=fn), details


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate registry granular extraction against V3 golden JSONs.")
    parser.add_argument(
        "--gold-dir",
        type=Path,
        default=Path("data/knowledge/golden_registry_v3"),
        help="Directory containing gold {note_id}.json files",
    )
    parser.add_argument(
        "--notes-dir",
        type=Path,
        default=Path("data/registry_granular/notes"),
        help="Directory containing raw note .txt files",
    )
    parser.add_argument(
        "--errors-out",
        type=Path,
        default=Path("reports/registry_granular_errors.jsonl"),
        help="Path to write per-note error details (JSONL)",
    )
    args = parser.parse_args()

    gold_dir: Path = args.gold_dir
    notes_dir: Path = args.notes_dir
    errors_out: Path = args.errors_out

    if not gold_dir.exists():
        raise FileNotFoundError(f"Gold dir not found: {gold_dir}")
    if not notes_dir.exists():
        raise FileNotFoundError(f"Notes dir not found: {notes_dir}")

    errors_out.parent.mkdir(parents=True, exist_ok=True)

    scorer = RegistryGranularScorer()

    gold_paths = sorted(gold_dir.glob("*.json"))
    if not gold_paths:
        raise FileNotFoundError(f"No gold JSON files found in: {gold_dir}")

    totals = ScoreResult(tp=0, fp=0, fn=0)
    evaluated = 0
    extraction_errors = 0

    with errors_out.open("w", encoding="utf-8") as f:
        for gold_path in gold_paths:
            gold = IPRegistryV3.model_validate_json(gold_path.read_text())
            note_path = notes_dir / gold.source_filename
            if not note_path.exists():
                f.write(
                    json.dumps(
                        {
                            "note_id": gold.note_id,
                            "gold_path": str(gold_path),
                            "error": "note_file_missing",
                            "expected_note_path": str(note_path),
                        }
                    )
                    + "\n"
                )
                continue

            note_text = note_path.read_text(encoding="utf-8", errors="replace")
            error: dict | None = None
            try:
                pred = run_v3_extraction(note_text)
            except LLMError as exc:
                extraction_errors += 1
                error = {"type": "llm_error", "message": str(exc)[:500]}
                pred = IPRegistryV3(note_id=gold.note_id, source_filename=gold.source_filename, procedures=[])
            except Exception as exc:  # noqa: BLE001
                extraction_errors += 1
                error = {"type": type(exc).__name__, "message": str(exc)[:500]}
                pred = IPRegistryV3(note_id=gold.note_id, source_filename=gold.source_filename, procedures=[])
            pred = pred.model_copy(update={"note_id": gold.note_id, "source_filename": gold.source_filename})

            score, details = scorer.score(gold, pred)
            totals = ScoreResult(tp=totals.tp + score.tp, fp=totals.fp + score.fp, fn=totals.fn + score.fn)
            evaluated += 1

            f.write(
                json.dumps(
                    {
                        "note_id": gold.note_id,
                        "source_filename": gold.source_filename,
                        "extraction_error": error,
                        "score": {"tp": score.tp, "fp": score.fp, "fn": score.fn},
                        "precision": score.precision,
                        "recall": score.recall,
                        **details,
                    }
                )
                + "\n"
            )

    print(f"Evaluated notes: {evaluated} / {len(gold_paths)}")
    print(f"Micro precision: {totals.precision:.3f} (tp={totals.tp}, fp={totals.fp})")
    print(f"Micro recall:    {totals.recall:.3f} (tp={totals.tp}, fn={totals.fn})")
    if extraction_errors:
        print(f"Notes with extraction errors: {extraction_errors}")
    print(f"Wrote errors: {errors_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
