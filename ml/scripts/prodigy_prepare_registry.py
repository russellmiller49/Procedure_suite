#!/usr/bin/env python3
"""Prepare a Prodigy JSONL batch for registry procedure flag annotation (multi-label).

Emits Prodigy `textcat`-compatible tasks with the canonical registry procedure labels.
Labels are prefilled (cats set to 1) using available heuristics:
- structured registry entry booleans (if present)
- CPT-derived flags (if `cpt_codes` present)
- ML predictor (ONNX bundle if present, otherwise sklearn fallback)

Includes smart sampling (uncertainty/disagreement/rarity), manifest-based
de-duplication, and split leakage guards via CSV exclusion lists.

Output task format:
  {"text": "...", "cats": {"label_a": 0/1, ...}, "_view_id": "textcat", "meta": {...}}
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

# Add repo root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.lib.ml_coder.registry_label_schema import (  # noqa: E402, I001
    REGISTRY_LABELS,
    compute_encounter_id,
)
from app.registry.application.cpt_registry_mapping import aggregate_registry_fields  # noqa: E402
from app.registry.v2_booleans import extract_v2_booleans  # noqa: E402

logger = logging.getLogger(__name__)


DEFAULT_MANIFEST = Path("data/ml_training/prodigy_registry_manifest.json")
DEFAULT_EXCLUDE = [
    Path("data/ml_training/registry_val.csv"),
    Path("data/ml_training/registry_test.csv"),
]
DEFAULT_TRAIN_CSV = Path("data/ml_training/registry_train.csv")
DEFAULT_MODEL_DIR = Path("data/models/registry_runtime")


def _utc_now_iso() -> str:
    tz = getattr(datetime, "UTC", timezone.utc)  # noqa: UP017
    return datetime.now(tz).isoformat()


def _normalize_text(text: str) -> str:
    return (text or "").strip()


def encounter_id_for_text(text: str) -> str:
    return compute_encounter_id(_normalize_text(text))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _safe_json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _parse_cpt_codes(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        parts = [p.strip() for p in value.replace(",", " ").split() if p.strip()]
        return parts
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if item is None:
                continue
            out.append(str(item).strip())
        return [c for c in out if c]
    return [str(value).strip()] if str(value).strip() else []


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Skipping invalid JSON at %s:%d", path, line_num)
                continue
            if isinstance(obj, dict):
                yield obj


def get_note_text(obj: Mapping[str, Any]) -> str:
    text = obj.get("note_text") or obj.get("note") or obj.get("text") or ""
    return _normalize_text(str(text))


def build_cats(
    labels: list[str],
    positives: Iterable[str] = (),
) -> dict[str, int]:
    cats = {label: 0 for label in labels}
    for label in positives:
        if label in cats:
            cats[label] = 1
    return cats


def load_excluded_encounter_ids(exclude_csv_paths: Iterable[Path]) -> set[str]:
    excluded: set[str] = set()
    for path in exclude_csv_paths:
        if not path or not Path(path).exists():
            continue
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "note_text" not in (reader.fieldnames or []):
                continue
            for row in reader:
                note_text = _normalize_text(str(row.get("note_text") or ""))
                if note_text:
                    excluded.add(encounter_id_for_text(note_text))
    return excluded


def load_manifest_encounter_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = _load_json(path)
    except Exception:
        return set()
    if not isinstance(data, dict):
        return set()

    # v1 preferred format: {"version": 1, "seen_encounter_ids": [...]}
    seen = data.get("seen_encounter_ids")
    if isinstance(seen, list):
        return {str(x) for x in seen if isinstance(x, str) and x.strip()}

    # legacy format: {"items": {"<id>": {...}}, ...}
    items = data.get("items")
    if isinstance(items, dict):
        return {k for k in items.keys() if isinstance(k, str) and k.strip()}

    return set()


def update_manifest(
    path: Path,
    added_encounter_ids: Iterable[str],
    batch_meta: dict[str, Any],
) -> None:
    payload: dict[str, Any]
    if path.exists():
        try:
            payload = _load_json(path)
        except Exception:
            payload = {}
    else:
        payload = {}

    if not isinstance(payload, dict):
        payload = {}

    now = _utc_now_iso()

    seen = payload.get("seen_encounter_ids")
    if not isinstance(seen, list):
        seen = []
    seen_set = {str(x) for x in seen if isinstance(x, str)}
    for eid in added_encounter_ids:
        if isinstance(eid, str) and eid.strip():
            seen_set.add(eid)
    payload["seen_encounter_ids"] = sorted(seen_set)

    # Legacy support: if the file already uses "items", keep it updated.
    items = payload.get("items")
    if isinstance(items, dict):
        for eid in added_encounter_ids:
            if not isinstance(eid, str) or not eid.strip():
                continue
            existing = items.get(eid)
            if isinstance(existing, dict):
                existing["last_seen_at"] = now
            else:
                items[eid] = {"first_seen_at": now, "last_seen_at": now}
        payload["items"] = items

    payload.setdefault("batches", [])
    if isinstance(payload["batches"], list):
        payload["batches"].append({"created_at": now, **batch_meta})

    payload["updated_at"] = now
    if "created_at" not in payload:
        payload["created_at"] = now
    payload.setdefault("version", 1)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _thresholds_version(path: Path | None) -> str | None:
    if not path or not path.exists():
        return None
    try:
        data = path.read_bytes()
    except Exception:
        return None
    digest = hashlib.sha256(data).hexdigest()[:12]
    return f"{path.name}:{digest}"


@dataclass
class LoadedPredictor:
    backend: str
    thresholds: dict[str, float]
    thresholds_path: Path | None

    def predict_proba(self, note_text: str) -> dict[str, float]:
        raise NotImplementedError


class SklearnPredictor(LoadedPredictor):
    def __init__(self) -> None:
        from ml.lib.ml_coder.registry_predictor import RegistryMLPredictor

        self._predictor = RegistryMLPredictor()
        super().__init__(
            backend="sklearn",
            thresholds=self._predictor.thresholds,
            thresholds_path=Path("data/models/registry_thresholds.json"),
        )

    def predict_proba(self, note_text: str) -> dict[str, float]:
        preds = self._predictor.predict_proba(note_text)
        return {p.field: float(p.probability) for p in preds}


class ONNXBundlePredictor(LoadedPredictor):
    def __init__(self, model_dir: Path) -> None:
        onnx_path = None
        for candidate in ("registry_model_int8.onnx", "registry_model.onnx"):
            p = model_dir / candidate
            if p.exists():
                onnx_path = p
                break
        if onnx_path is None:
            raise FileNotFoundError(
                "Missing ONNX model (registry_model_int8.onnx/registry_model.onnx)"
            )

        label_path = None
        for candidate in ("label_order.json", "registry_label_fields.json"):
            p = model_dir / candidate
            if p.exists():
                label_path = p
                break
        if label_path is None:
            raise FileNotFoundError(
                "Missing label_order.json/registry_label_fields.json in model dir"
            )

        thresholds_path = model_dir / "thresholds.json"
        thresholds: dict[str, float] = {}
        if thresholds_path.exists():
            raw = _load_json(thresholds_path)
            if isinstance(raw, dict):
                parsed: dict[str, float] = {}
                for k, v in raw.items():
                    if not isinstance(k, str):
                        continue
                    if isinstance(v, int | float):
                        parsed[k] = float(v)
                        continue
                    if isinstance(v, dict) and "threshold" in v:
                        t = v.get("threshold")
                        if isinstance(t, int | float):
                            parsed[k] = float(t)
                thresholds = parsed

        labels_raw = _load_json(label_path)
        if not isinstance(labels_raw, list) or not all(isinstance(x, str) for x in labels_raw):
            raise ValueError(f"Invalid labels file: {label_path}")
        self._model_labels = list(labels_raw)

        tokenizer_dir = model_dir / "tokenizer"
        if not tokenizer_dir.exists():
            raise FileNotFoundError("Missing tokenizer/ directory in model dir")

        # Lazy imports so the script stays importable without ONNX deps.
        import numpy as np
        import onnxruntime as ort
        from transformers import AutoTokenizer

        self._np = np
        self._session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        self._tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir), local_files_only=True)

        self._input_names = [i.name for i in self._session.get_inputs()]
        super().__init__(
            backend="onnx",
            thresholds=thresholds,
            thresholds_path=thresholds_path if thresholds_path.exists() else None,
        )

    def predict_proba(self, note_text: str) -> dict[str, float]:
        text = _normalize_text(note_text)
        if not text:
            return {}

        tokens = self._tokenizer(
            text,
            truncation=True,
            max_length=512,
            padding="max_length",
            return_tensors="np",
        )

        feed: dict[str, Any] = {}
        for name in self._input_names:
            if name in tokens:
                feed[name] = tokens[name].astype(self._np.int64)
            elif name == "token_type_ids":
                feed[name] = self._np.zeros_like(tokens["input_ids"]).astype(self._np.int64)

        outputs = self._session.run(None, feed)
        if not outputs:
            return {}

        logits = outputs[0]
        if hasattr(logits, "shape") and len(getattr(logits, "shape", ())) == 2:
            logits = logits[0]

        probs = 1.0 / (1.0 + self._np.exp(-logits))
        probs = probs.tolist()
        return {label: float(prob) for label, prob in zip(self._model_labels, probs, strict=False)}


class TorchBundlePredictor(LoadedPredictor):
    def __init__(self, model_dir: Path) -> None:
        # Lazy import so the script stays runnable without torch/transformers.
        from app.registry.inference_pytorch import TorchRegistryPredictor

        predictor = TorchRegistryPredictor(bundle_dir=model_dir)
        if not predictor.available:
            raise RuntimeError("PyTorch bundle predictor unavailable")

        self._predictor = predictor
        thresholds_path = model_dir / "thresholds.json"
        super().__init__(
            backend="pytorch",
            thresholds=predictor.thresholds,
            thresholds_path=thresholds_path if thresholds_path.exists() else None,
        )

    def predict_proba(self, note_text: str) -> dict[str, float]:
        preds = self._predictor.predict_proba(note_text)
        return {p.field: float(p.probability) for p in preds}


def load_predictor(model_dir: Path) -> LoadedPredictor:
    try:
        return ONNXBundlePredictor(model_dir)
    except Exception as exc:
        logger.info("ONNX predictor unavailable (%s); trying PyTorch bundle", exc)
    try:
        return TorchBundlePredictor(model_dir)
    except Exception as exc:
        logger.info("PyTorch predictor unavailable (%s); falling back to sklearn", exc)
    return SklearnPredictor()


def derive_cpt_flags(cpt_codes: list[str], labels: list[str]) -> dict[str, int] | None:
    if not cpt_codes:
        return None
    nested = aggregate_registry_fields(cpt_codes, version="v2")
    flags = extract_v2_booleans(nested)
    return {label: int(flags.get(label, 0)) for label in labels}


def derive_structured_flags(obj: Mapping[str, Any], labels: list[str]) -> dict[str, int] | None:
    for key in ("registry_entry", "registry", "extraction"):
        value = obj.get(key)
        if isinstance(value, dict):
            flags = extract_v2_booleans(value)
            return {label: int(flags.get(label, 0)) for label in labels}
    return None

def _bools_from_probs(
    probs: Mapping[str, float],
    thresholds: Mapping[str, float],
    labels: list[str],
    threshold_mode: str,
    global_threshold: float,
) -> dict[str, int]:
    out: dict[str, int] = {}
    for label in labels:
        p = float(probs.get(label, 0.0))
        t = float(global_threshold if threshold_mode == "global" else thresholds.get(label, 0.5))
        out[label] = 1 if p >= t else 0
    return out


def uncertainty_score(
    probs: Mapping[str, float],
    thresholds: Mapping[str, float],
    labels: list[str],
    threshold_mode: str,
    global_threshold: float,
    window: float = 0.15,
) -> float:
    if not labels:
        return 0.0
    best = 0.0
    for label in labels:
        p = float(probs.get(label, 0.0))
        t = float(global_threshold if threshold_mode == "global" else thresholds.get(label, 0.5))
        margin = abs(p - t)
        score = max(0.0, window - margin) / window
        if score > best:
            best = score
    return best


def disagreement_score(
    ml_bools: Mapping[str, int],
    cpt_bools: Mapping[str, int] | None,
    labels: list[str],
) -> float:
    if not labels or not cpt_bools:
        return 0.0
    mismatches = 0
    for label in labels:
        if int(ml_bools.get(label, 0)) != int(cpt_bools.get(label, 0)):
            mismatches += 1
    return float(mismatches)


def rarity_bonus(
    ml_bools: Mapping[str, int],
    label_counts: Mapping[str, int] | None,
    labels: list[str],
) -> float:
    if not labels or not label_counts:
        return 0.0
    weights = {label: 1.0 / float(int(label_counts.get(label, 0)) + 1) for label in labels}
    denom = sum(weights.values()) or 1.0
    num = sum(weights[label] for label in labels if int(ml_bools.get(label, 0)) == 1)
    return float(num / denom)


def compute_label_counts(train_csv: Path, labels: list[str]) -> dict[str, int]:
    if not train_csv.exists():
        return {label: 0 for label in labels}
    try:
        import pandas as pd
    except Exception:
        return {label: 0 for label in labels}

    df = pd.read_csv(train_csv)
    counts: dict[str, int] = {}
    for label in labels:
        if label not in df.columns:
            counts[label] = 0
            continue
        col = pd.to_numeric(df[label], errors="coerce").fillna(0)
        counts[label] = int(col.clip(0, 1).sum())
    return counts


def sampling_score(
    strategy: str,
    unc: float,
    dis: float,
    rar: float,
    has_cpt: bool,
) -> float:
    if strategy == "random":
        return 0.0
    if strategy == "uncertainty":
        return float(unc)
    if strategy == "disagreement":
        return float(dis)
    if strategy == "rare_boost":
        return float(rar)
    if strategy == "hybrid":
        if has_cpt:
            return float(0.6 * dis + 0.3 * unc + 0.1 * rar)
        return float(0.9 * unc + 0.1 * rar)
    raise ValueError(f"Unknown strategy: {strategy}")


def build_ml_top(
    probs: Mapping[str, float],
    thresholds: Mapping[str, float],
    labels: list[str],
    threshold_mode: str,
    global_threshold: float,
    top_k: int = 8,
) -> list[dict[str, Any]]:
    scored = []
    for label in labels:
        p = float(probs.get(label, 0.0))
        t = float(global_threshold if threshold_mode == "global" else thresholds.get(label, 0.5))
        scored.append((p, label, t))
    scored.sort(reverse=True, key=lambda x: x[0])
    out: list[dict[str, Any]] = []
    for p, label, t in scored[:top_k]:
        out.append({"id": label, "prob": p, "threshold": t, "is_positive": p >= t})
    return out


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-file",
        type=Path,
        required=True,
        help="Input JSONL of unlabeled notes",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        required=True,
        help="Output Prodigy JSONL batch file",
    )
    parser.add_argument("--count", type=int, default=200, help="Number of tasks to emit")
    parser.add_argument(
        "--strategy",
        choices=["random", "uncertainty", "disagreement", "rare_boost", "hybrid"],
        default="hybrid",
        help="Sampling strategy",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Manifest JSON for de-dup",
    )
    parser.add_argument(
        "--exclude-csv",
        type=Path,
        action="append",
        default=list(DEFAULT_EXCLUDE),
        help="CSV with note_text column to exclude (repeatable)",
    )
    parser.add_argument("--label-fields", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=DEFAULT_TRAIN_CSV,
        help="Train CSV used for rarity bonuses (optional)",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help="Registry runtime dir for ONNX bundle (fallback to sklearn if missing)",
    )
    parser.add_argument(
        "--threshold-mode",
        choices=["per_label", "global"],
        default="per_label",
        help="Threshold mode for accept pre-checks",
    )
    parser.add_argument(
        "--global-threshold",
        type=float,
        default=0.5,
        help="Global threshold when enabled",
    )
    parser.add_argument(
        "--display-name-overrides",
        type=Path,
        default=None,
        help="Optional JSON mapping of label id -> display text",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args(argv)

    labels = list(REGISTRY_LABELS)

    excluded_ids = load_excluded_encounter_ids(args.exclude_csv)
    manifest_ids = load_manifest_encounter_ids(args.manifest)
    blocked = excluded_ids | manifest_ids

    predictor = load_predictor(args.model_dir)
    label_counts = compute_label_counts(args.train_csv, labels)

    rng = random.Random(args.seed)

    candidates: list[tuple[float, float, dict[str, Any], str]] = []
    seen_in_input: set[str] = set()

    for obj in iter_jsonl(args.input_file):
        note_text = get_note_text(obj)
        if not note_text:
            continue

        encounter_id = encounter_id_for_text(note_text)
        if encounter_id in seen_in_input:
            continue
        seen_in_input.add(encounter_id)

        if encounter_id in blocked:
            continue

        probs_raw = predictor.predict_proba(note_text)
        probs = {label: float(probs_raw.get(label, 0.0)) for label in labels}

        ml_bools = _bools_from_probs(
            probs=probs,
            thresholds=predictor.thresholds,
            labels=labels,
            threshold_mode=args.threshold_mode,
            global_threshold=args.global_threshold,
        )

        structured_flags = derive_structured_flags(obj, labels)
        structured_accept = [
            label for label in labels if structured_flags and int(structured_flags.get(label, 0)) == 1
        ]

        cpt_codes = _parse_cpt_codes(obj.get("cpt_codes"))
        cpt_flags = derive_cpt_flags(cpt_codes, labels)
        cpt_accept = [label for label in labels if cpt_flags and int(cpt_flags.get(label, 0)) == 1]

        unc = uncertainty_score(
            probs=probs,
            thresholds=predictor.thresholds,
            labels=labels,
            threshold_mode=args.threshold_mode,
            global_threshold=args.global_threshold,
        )
        dis = disagreement_score(ml_bools=ml_bools, cpt_bools=cpt_flags, labels=labels)
        rar = rarity_bonus(ml_bools=ml_bools, label_counts=label_counts, labels=labels)

        score = sampling_score(args.strategy, unc=unc, dis=dis, rar=rar, has_cpt=bool(cpt_codes))
        if args.strategy == "random":
            score = rng.random()

        ml_accept = [label for label in labels if int(ml_bools.get(label, 0)) == 1]
        positives = sorted(set(ml_accept) | set(cpt_accept) | set(structured_accept))
        cats = build_cats(labels, positives=positives)

        ml_only = sorted(set(ml_accept) - set(cpt_accept))
        cpt_only = sorted(set(cpt_accept) - set(ml_accept))
        disagreement_count = len(ml_only) + len(cpt_only)
        tie_break = 0.0
        if ml_only:
            tie_break = max(float(probs.get(label, 0.0)) for label in ml_only)

        meta: dict[str, Any] = {
            "source": str(args.input_file.name),
            "encounter_id": encounter_id,
            "sampling_strategy": args.strategy,
            "sampling_score": float(score),
            "ml_backend": predictor.backend,
            "threshold_mode": args.threshold_mode,
            "global_threshold": float(args.global_threshold),
            "thresholds_version": _thresholds_version(predictor.thresholds_path),
            "ml_top": build_ml_top(
                probs=probs,
                thresholds=predictor.thresholds,
                labels=labels,
                threshold_mode=args.threshold_mode,
                global_threshold=args.global_threshold,
            ),
            "ml_accept": sorted(ml_accept),
            "cpt_accept": sorted(cpt_accept),
            "structured_accept": sorted(structured_accept),
            "ml_only": ml_only,
            "cpt_only": cpt_only,
            "disagreement_score": int(disagreement_count),
        }

        if cpt_codes:
            meta["cpt_codes"] = cpt_codes

        # Preserve identifier-ish fields if present
        for key in ("note_id", "encounter_id", "id"):
            if key in obj and obj.get(key) is not None:
                # Keep original IDs under distinct keys if needed.
                if key != "encounter_id":
                    meta[key] = obj.get(key)

        task = {
            "text": note_text,
            "cats": cats,
            "_view_id": "textcat",
            "meta": meta,
            "config": {"exclusive": False},
        }

        rank_secondary = rng.random()
        if args.strategy == "disagreement":
            rank_secondary = float(tie_break)
            score = float(disagreement_count)
        candidates.append((float(score), float(rank_secondary), task, encounter_id))

    if not candidates:
        logger.warning("No eligible notes found (after exclusions/manifest)")
        return 0

    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    chosen = candidates[: max(0, int(args.count))]

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_file, "w", encoding="utf-8") as f:
        for _, _, task, _ in chosen:
            cats = task.get("cats")
            if not isinstance(cats, dict) or set(cats.keys()) != set(labels):
                raise ValueError("Task cats must contain exactly the canonical labels")
            for k, v in cats.items():
                if k not in labels:
                    raise ValueError("Task cats contains unknown label")
                if int(v) not in (0, 1):
                    raise ValueError("Task cats values must be 0/1")
            f.write(_safe_json_dumps(task) + "\n")

    batch_ids = [h for _, _, _, h in chosen]
    update_manifest(
        args.manifest,
        batch_ids,
        batch_meta={
            "output_file": str(args.output_file),
            "input_file": str(args.input_file),
            "count": len(chosen),
            "strategy": args.strategy,
            "model_dir": str(args.model_dir),
        },
    )

    logger.info("Wrote %d tasks to %s", len(chosen), args.output_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
