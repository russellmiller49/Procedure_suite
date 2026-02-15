# Relations Prodigy Workflow (Phase 8)

This repo supports a human-in-the-loop workflow for improving **cross-document relation extraction** (e.g., lesion↔specimen linkage) using Prodigy’s `choice` UI over ledger-derived edges.

Key property: the workflow is **zero-knowledge friendly** — tasks are generated from the **entity ledger** (labels/attributes), not raw note text.

## 0) Prerequisite: collect bundle outputs (JSON)

Save one or more `POST /api/v1/process_bundle` responses as JSON files (locally). These files are your input corpus for task generation.

## 1) Prepare a Prodigy batch (accept / reject edges)

Make target:
```bash
make relations-prodigy-prepare \
  REL_PRODIGY_INPUT=/path/to/saved_bundle_outputs \
  REL_PRODIGY_PATTERN="*.json" \
  REL_PRODIGY_ML_THRESHOLD=0.85 \
  REL_PRODIGY_EDGE_SOURCES=merged
```

Direct script:
```bash
python ml/scripts/bootstrap_relations_silver.py \
  --input /path/to/saved_bundle_outputs \
  --pattern "*.json" \
  --output data/ml_training/relations_prodigy_batch.jsonl \
  --ml-threshold 0.85
```

Notes:
- This writes `_view_id="choice"` tasks suitable for `prodigy mark ... --view-id choice`.
- By default it uses heuristic + merged edges only (no LLM calls).
- Use `--edge-sources` to control which predictions become tasks (default `merged`; options: `merged`, `heuristic`, `ml`, `all`).
- Optional: add `--use-llm` to propose additional edges, but it will refuse to run in stub/offline mode unless `--llm-allow-stub` is set.

## 2) Annotate in Prodigy

Make target:
```bash
make relations-prodigy-annotate REL_PRODIGY_DATASET=relations_v1
```

## 3) Export Prodigy annotations → labeled edges JSONL (and optional CSV)

DB mode (recommended if Prodigy is installed/configured):
```bash
make relations-prodigy-export REL_PRODIGY_DATASET=relations_v1
```

Direct script:
```bash
python ml/scripts/prodigy_export_relations.py \
  --dataset relations_v1 \
  --output-jsonl data/ml_training/relations_human_edges.jsonl \
  --output-csv data/ml_training/relations_human_edges.csv
```

File mode (CI / shared export file):
```bash
python ml/scripts/prodigy_export_relations.py \
  --input-jsonl /path/to/prodigy_export.jsonl \
  --output-jsonl data/ml_training/relations_human_edges.jsonl
```

Output rows:
- `edge_id` (stable hash; last-write-wins on duplicates)
- `label` (`1` accepted / `0` rejected)
- plus `edge`, `source_entity`, `target_entity`, and `meta` fields for auditing

## 4) Evaluate accept/reject rates (shadow-mode comparison)

```bash
make relations-prodigy-eval \
  REL_PRODIGY_EVAL_INPUT=data/ml_training/relations_human_edges.jsonl
```

This writes `data/ml_training/relations_eval_report.json` and prints a JSON summary to stdout.

## 4) Next step (future): train + compare

Once you have `relations_human_edges.jsonl`, we can:
- compute acceptance rates by `edge_source` (`heuristic` vs `merged` vs `ml`)
- build a small offline classifier (feature-based or lightweight model) and run it in shadow mode
- tighten merge logic (thresholds, override policy) based on observed error modes
