# CODEX Implementation Plan — Registry “Diamond Loop” (Model‑Assisted Annotation)

This document is a **Codex execution brief** for implementing an end‑to‑end human‑in‑the‑loop workflow that improves the **Registry multi‑label procedure classifier** using Prodigy and disagreement sampling.

It is designed to fit the repo’s current architecture:
- **Extraction‑First** trajectory (Text → Registry → Deterministic CPT), while still supporting the current hybrid production modes.
- Existing **PHI Prodigy workflow** patterns (prepare → annotate → export → finetune/retrain) as an implementation template.
- Existing **Registry ML audit** concept (compare ML vs deterministic/CPT‑derived signals) to drive smarter sampling.

---

## Outcomes (Definition of Done)

After completing this plan, the repo will support:

1. **Prepare**: generate a Prodigy JSONL for multi‑label classification (“choice” UI) with **pre‑checked boxes** from pipeline/model predictions.
2. **Annotate**: run Prodigy with checkbox UI over those tasks.
3. **Export**: convert Prodigy annotations back to a training CSV compatible with `scripts/train_roberta.py`.
4. **Merge (Tier 0)**: incorporate **human** labels into the registry training data pipeline as a highest‑priority source (above structured/CPT/keyword tiers).
5. **Retrain**: train the model with:
   - head+tail truncation
   - class imbalance handling
   - per‑label threshold optimization
   - optional sample‑confidence weighting (downweight tier‑3 keyword hydration)
6. **Repeat**: iterate batches using disagreement / uncertainty sampling until performance stabilizes.

---

## Critical Constraints / Non‑Negotiables

- **Single Source of Truth for label schema**: one module defines the canonical 29 registry boolean flags and their ordering. No duplicated label lists in scripts/services.
- **Do not rely on LLM calls** to prepare Prodigy batches. The batch prep must be offline‑friendly.
- **Do not change** the public API contracts unless required; add internal helpers/modules first.
- Use repo tooling: `make test`, Ruff, mypy. Keep changes minimal and well‑tested.

---

## 0) Inventory / Where Things Already Exist

Before coding, Codex should locate and read:
- `scripts/train_roberta.py` (existing registry multi‑label training)
- `modules/ml_coder/registry_data_prep.py`, `modules/ml_coder/label_hydrator.py` (3‑tier hydration + dedup)
- `modules/registry/application/registry_service.py` (hybrid + extraction‑first flows)
- `modules/registry/audit/*` (audit / discrepancy logic)
- `scripts/prodigy_prepare_phi_batch.py` and `scripts/prodigy_export_corrections.py` (existing Prodigy workflow patterns)
- `Makefile` (existing Prodigy targets and variable conventions)

---

## 1) Create a Canonical Registry Label Schema Module (29 flags)

### 1.1 Add file
Create:
- `modules/ml_coder/registry_label_schema.py`

### 1.2 Implement exports
- `REGISTRY_LABELS: list[str]` — **exactly 29** flags, in the canonical training order.
- `REGISTRY_LABEL_TITLES: dict[str, str]` — human‑readable display strings for Prodigy options.
- `def prodigy_options() -> list[dict[str, str]]` returning:
  - `[{"id": "<label_id>", "text": "<label_title>"} ...]`
- `def validate_schema() -> None` which asserts:
  - len == 29
  - no duplicates
  - all keys in titles match labels
  - titles are non‑empty

### 1.3 Refactor usage sites (no hard‑coded label lists)
Update any module/script that hardcodes the 29 labels to import from `modules.ml_coder.registry_label_schema`.

Common likely files:
- `scripts/train_roberta.py`
- `modules/ml_coder/registry_training.py`
- `modules/ml_coder/thresholds.py` (if it contains label lists)
- Any batch prep/export scripts created below

### 1.4 Tests
Add:
- `tests/ml_coder/test_registry_label_schema.py`
  - `test_registry_label_schema_valid()` calls `validate_schema()`
  - `test_registry_label_schema_count()` asserts 29

---

## 2) Registry Prodigy Batch Prep (choice UI with pre‑checked labels)

### 2.1 Add file
Create:
- `scripts/prodigy_prepare_registry_batch.py`

### 2.2 CLI interface
Use Typer (repo standard for CLIs), with args:
- `--input-file` (JSONL by default; accept `note_text|text|note`)
- `--output-file`
- `--limit` (optional)
- `--strategy` (`disagreement`, `uncertainty`, `random`, `rare_boost`) default `disagreement`
- `--manifest` path (default `data/ml_training/registry_prodigy_manifest.json`)
- `--seed` (default 42)
- `--model-dir` optional:
  - if provided, load the RoBERTa/BERT registry model for predictions
  - if omitted, allow a “CPT‑only prefill” mode (still usable)

### 2.3 Prefill signals (two weak labelers)
The goal is **checkbox pre‑population** and **smart sampling**.

Implement two independent signals:
1) **ML signal**:
   - If a registry model is available, run it to get per‑label probabilities.
   - Convert to `ml_accept` using per‑label thresholds if present (e.g., `thresholds.json`).
   - Else use default threshold 0.5.

2) **Deterministic/CPT signal**:
   - Use the existing deterministic derivation/mapping logic (no LLM):
     - If your input examples contain CPT codes, map CPT → procedure flags.
     - If not, you may run the hybrid coder in **offline / rules‑only** mode if available; otherwise skip.
   - Convert to `cpt_accept`.

Prefill rule:
- `accept = sorted(set(ml_accept) | set(cpt_accept))`

Include in `meta`:
- `ml_accept`, `cpt_accept`
- `ml_only`, `cpt_only`
- `disagreement_score`
- any available CPT codes (if present in input)

### 2.4 Sampling strategies
Implement `score(example)`:
- `disagreement`: `len(ml_only) + len(cpt_only)` (primary), tie‑break by max ML prob among `ml_only`.
- `uncertainty`: sum over labels of proximity to threshold (e.g., `1 - abs(p - t)` for labels near their thresholds).
- `random`: shuffle.
- `rare_boost`: oversample notes with predicted positives for rare labels (compute rarity from training prevalence if available).

Sampling must:
- avoid repeats using manifest (see 2.5)
- log summary counts (how many selected, top disagreements, etc.)

### 2.5 Manifest / dedup
Store a stable ID per note to avoid re‑sampling:
- `encounter_id = sha256(note_text)[:16]` (or reuse existing encounter_id helper if present)
Manifest JSON structure:
```json
{
  "version": 1,
  "seen_encounter_ids": ["...", "..."]
}
```
Only emit tasks not already in `seen_encounter_ids`.

### 2.6 Output task format
For each task, write JSONL:
```json
{
  "text": "...",
  "options": [{"id": "...", "text": "..."}, ...],
  "accept": ["label_a", "label_b"],
  "meta": {
    "encounter_id": "...",
    "strategy": "disagreement",
    "ml_only": [...],
    "cpt_only": [...],
    "ml_accept": [...],
    "cpt_accept": [...],
    "disagreement_score": 3
  }
}
```

### 2.7 Makefile targets
Add to Makefile (mirror PHI targets):
- `REG_PRODIGY_COUNT ?= 200`
- `REG_PRODIGY_DATASET ?= registry_v1`
- `REG_PRODIGY_INPUT_FILE ?= data/training/raw_unlabeled_notes.jsonl` (choose a sensible default)
- `REG_PRODIGY_BATCH_FILE ?= data/ml_training/registry_prodigy_batch.jsonl`
- `REG_PRODIGY_MODEL_DIR ?= data/models/registry_runtime` (or `artifacts/registry_bert`)

Targets:
- `registry-prodigy-prepare` (runs prepare script)
- `registry-prodigy-annotate` (runs Prodigy `mark` with `--view-id choice`)
- `registry-prodigy-export` (runs export script below)

Example annotate command:
```bash
prodigy mark ${REG_PRODIGY_DATASET} ${REG_PRODIGY_BATCH_FILE} --view-id choice
```
(Use `$(PRODIGY_PYTHON)` consistent with repo.)

---

## 3) Registry Prodigy Export (Proggy → CSV with 29 binary columns)

### 3.1 Add file
Create:
- `scripts/prodigy_export_registry.py`

### 3.2 CLI interface
Args:
- `--dataset` (required)
- `--output-csv` (required)
- `--output-jsonl` (optional)
- `--label-source` default `"human"`
- `--label-confidence` default `1.0`

### 3.3 Export logic
For each Prodigy record:
- `note_text = task["text"]`
- `accept = task.get("accept", [])`
- Create a row with:
  - `note_text`
  - `encounter_id` (recompute the same way as prepare script)
  - `label_source="human"`
  - `label_confidence=1.0`
  - 29 label columns from `REGISTRY_LABELS` as 0/1 (1 iff label in accept)

Deduplicate by encounter_id, keeping the latest occurrence (last write wins).

### 3.4 Tests
Add `tests/scripts/test_prodigy_export_registry.py`:
- roundtrip minimal example: input Prodigy JSON dict → exported CSV row has correct columns and values.

---

## 4) Merge Human Labels Into Training Data as “Tier 0”

Your registry training prep already does 3‑tier hydration + priority‑based dedup. Add **human** as the highest tier.

### 4.1 Preferred implementation (Tier 0 inside data prep)
Modify:
- `modules/ml_coder/registry_data_prep.py` (or wherever `prepare_registry_training_splits()` loads records)

Add:
- Optional input `human_labels_csv: Path | None`
- If file exists, load it first, tag `label_source="human"`, set priority above structured.

Priority order should become:
```
human (priority=4) > structured (3) > cpt (2) > keyword (1)
```

Ensure dedup keeps human labels when encounter_id/note_text duplicates exist.

### 4.2 Guard against leakage
If your split is grouped by encounter_id, merging before split is safe.
If you merge after split, you risk leaking note variants across splits — avoid.

### 4.3 Makefile support
Add:
- `registry-prep-with-human` target that passes the human CSV into the data prep stage and writes new `registry_train/val/test.csv`.

---

## 5) Upgrade Training Script (`scripts/train_roberta.py`) to Support Loop

The repo already intends:
- `Golden JSONs → registry_data_prep.py → train_roberta.py → ONNX`  
so we adapt `train_roberta.py` to be “Diamond Loop ready”.

### 5.1 Required features
- **Head + Tail truncation** (e.g., 384 + 128 = 512) for long notes.
- **Imbalance handling**:
  - `BCEWithLogitsLoss(pos_weight=...)` computed from training split
  - cap very large weights to prevent instability (e.g., max 100)
- **Per‑label threshold optimization**:
  - compute best F1 per label on validation set
  - write `thresholds.json` mapping label → threshold + val_f1
- **Artifact outputs** in `--output-dir`:
  - HF model + tokenizer
  - `registry_label_fields.json`
  - `thresholds.json`

### 5.2 Repo‑specific enhancement: sample weighting by label_confidence
Because training CSV rows already include `label_confidence` from the hydration tiers, implement:
- loss per sample * `label_confidence`
- use `reduction="none"` then weight and mean

This improves early learning by downweighting keyword‑hydrated labels.

### 5.3 Optional: add `--model-name` default
Use medical domain model:
- default: `microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext`

### 5.4 Tests
Add or extend:
- `tests/ml_coder/test_training_pipeline.py` or a new test to confirm:
  - thresholds.json created
  - label_fields file created
  - training runs 1 mini epoch on tiny fixture (mocked / fast)

---

## 6) Documentation Fixups

### 6.1 Fix “30 procedure columns” → “29”
There is a doc/table that claims “[30 procedure columns]”. Update to 29 and ideally link to `REGISTRY_LABELS` list.

### 6.2 Add docs page
Add:
- `docs/REGISTRY_PRODIGY_WORKFLOW.md`

Include:
- commands
- file paths
- how to run disagreement sampling
- how to retrain and export thresholds

---

## 7) Validation Checklist (Run These Commands)

Minimal:
```bash
make lint
make typecheck
pytest tests/ml_coder/test_registry_label_schema.py -v
pytest tests/scripts/test_prodigy_export_registry.py -v
```

Smoke:
```bash
# 1) Prepare a tiny batch
python scripts/prodigy_prepare_registry_batch.py --input-file <RAW_NOTES.jsonl> --output-file /tmp/reg_batch.jsonl --limit 5

# 2) Run Prodigy UI
prodigy mark registry_v1 /tmp/reg_batch.jsonl --view-id choice

# 3) Export
python scripts/prodigy_export_registry.py --dataset registry_v1 --output-csv /tmp/registry_human.csv

# 4) Merge and create new splits
make registry-prep-with-human HUMAN_REGISTRY_CSV=/tmp/registry_human.csv

# 5) Train baseline
python scripts/train_roberta.py --train-csv data/ml_training/registry_train.csv --val-csv data/ml_training/registry_val.csv --output-dir artifacts/registry_bert --epochs 1
```

---

## Notes / Implementation Tips

- Prefer reusing existing helper functions (encounter_id hashing, model runtime dirs, threshold loader) if they already exist.
- Keep Prodigy scripts “offline safe” (no LLM calls).
- If `PRODIGY_PYTHON` is configured to run Prodigy inside conda, keep it consistent.

---

## Recommended Batch Cadence

- Start with 200–300 disagreement samples.
- Iterate until:
  - macro F1 plateaus,
  - rare label F1 improves,
  - and disagreement rate drops.

---

## Quick Reference: Files to Add / Change

**Add**
- `modules/ml_coder/registry_label_schema.py`
- `scripts/prodigy_prepare_registry_batch.py`
- `scripts/prodigy_export_registry.py`
- `tests/ml_coder/test_registry_label_schema.py`
- `tests/scripts/test_prodigy_export_registry.py`
- `docs/REGISTRY_PRODIGY_WORKFLOW.md`

**Change**
- `scripts/train_roberta.py`
- `modules/ml_coder/registry_data_prep.py` (Tier‑0 human merge)
- `Makefile` (registry prodigy targets)
- any docs mentioning “30 labels”

