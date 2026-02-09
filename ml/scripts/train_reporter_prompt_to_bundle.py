#!/usr/bin/env python3
"""Train seq2seq reporter prompt->ProcedureBundle model."""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Allow running as a file (python ml/scripts/...) without installing the package.
# When executed by filename, Python sets sys.path[0] to this script's directory
# (ml/scripts), which would otherwise prevent `import ml` from working.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import torch
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from ml.lib.reporter_bundle_codec import encode_bundle_keys_v1
from ml.lib.reporter_json_parse import parse_and_validate_bundle

DEFAULT_TRAIN = Path("data/ml_training/reporter_prompt/v1/prompt_to_bundle_train.jsonl")
DEFAULT_VAL = Path("data/ml_training/reporter_prompt/v1/prompt_to_bundle_val.jsonl")
DEFAULT_MANIFEST = Path("data/ml_training/reporter_prompt/v1/prompt_to_bundle_distill_manifest.json")
DEFAULT_OUTPUT_DIR = Path("artifacts/reporter_prompt_bundle_v1")
DEFAULT_MAX_TARGET_LENGTH = 1536

# `google/flan-t5-*` sentencepiece vocab cannot represent `{`/`}`; they become `<unk>`.
# Use T5 extra_id tokens as reversible placeholders during training/eval.
_T5_JSON_OBJ_OPEN = "<extra_id_0>"
_T5_JSON_OBJ_CLOSE = "<extra_id_1>"


@dataclass
class TrainingExample:
    prompt_text: str
    target_payload: dict[str, Any]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument("--val", type=Path, default=DEFAULT_VAL)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model-name", default="google/flan-t5-large")
    parser.add_argument("--max-source-length", type=int, default=512)
    parser.add_argument("--max-target-length", type=int, default=DEFAULT_MAX_TARGET_LENGTH)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--train-batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--gradient-accumulation", type=int, default=8)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--early-stopping-patience", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--drop-long-targets",
        type=str.lower,
        choices=["true", "false"],
        default="true",
        help="Drop examples whose gold target exceeds max_target_length instead of truncating (recommended).",
    )
    parser.add_argument(
        "--fp16",
        type=str.lower,
        choices=["auto", "true", "false"],
        default="auto",
        help="Enable fp16 mixed precision. Use 'false' if you see NaN/Inf loss.",
    )
    parser.add_argument(
        "--bf16",
        type=str.lower,
        choices=["auto", "true", "false"],
        default="auto",
        help="Enable bf16 mixed precision (more stable than fp16 on bf16-capable GPUs).",
    )
    parser.add_argument(
        "--use-short-key-codec",
        type=str.lower,
        choices=["auto", "true", "false"],
        default="auto",
        help="Whether to encode target keys before training.",
    )
    return parser.parse_args(argv)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_examples(path: Path) -> list[TrainingExample]:
    raw_rows = load_jsonl(path)
    examples: list[TrainingExample] = []
    for row in raw_rows:
        prompt = str(row.get("prompt_text") or "").strip()
        payload = row.get("bundle_target_json")
        if not prompt or not isinstance(payload, dict):
            continue
        examples.append(TrainingExample(prompt_text=prompt, target_payload=payload))
    if not examples:
        raise RuntimeError(f"No valid training examples in {path}")
    return examples


def resolve_codec_setting(choice: str, manifest_path: Path) -> tuple[bool, dict[str, Any] | None]:
    manifest: dict[str, Any] | None = None
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if choice == "true":
        return True, manifest
    if choice == "false":
        return False, manifest

    if manifest:
        recommended = (
            manifest.get("recommended_training", {})
            .get("enable_short_key_codec")
        )
        if isinstance(recommended, bool):
            return recommended, manifest

    return False, manifest


def resolve_target_length(cli_value: int, manifest: dict[str, Any] | None) -> int:
    # Manifest recommendation is advisory; allow explicit CLI overrides.
    if manifest and cli_value == DEFAULT_MAX_TARGET_LENGTH:
        recommended = manifest.get("recommended_training", {}).get("max_target_length")
        if isinstance(recommended, int) and recommended > 0:
            return recommended
    return cli_value


def format_source_prompt(prompt_text: str) -> str:
    return (
        "Generate a valid ProcedureBundle JSON object from this clinical prompt. "
        "Return JSON only.\n\n"
        f"PROMPT:\n{prompt_text.strip()}"
    )


def format_target_text(payload: dict[str, Any], *, use_codec: bool) -> str:
    out = encode_bundle_keys_v1(payload) if use_codec else payload
    return json.dumps(out, ensure_ascii=False, separators=(",", ":"))


def _tokenizer_requires_json_brace_placeholders(tokenizer: Any) -> bool:
    unk_id = getattr(tokenizer, "unk_token_id", None)
    if unk_id is None:
        return False
    ids = tokenizer("{", add_special_tokens=False).input_ids
    if int(unk_id) not in {int(tok) for tok in ids}:
        return False
    vocab = tokenizer.get_vocab()
    return _T5_JSON_OBJ_OPEN in vocab and _T5_JSON_OBJ_CLOSE in vocab


def _encode_json_braces_for_tokenizer(text: str, *, use_placeholders: bool) -> str:
    if not use_placeholders:
        return text
    return text.replace("{", _T5_JSON_OBJ_OPEN).replace("}", _T5_JSON_OBJ_CLOSE)


def _bundle_cpt_set(payload: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    procedures = payload.get("procedures")
    if not isinstance(procedures, list):
        return out
    for proc in procedures:
        if not isinstance(proc, dict):
            continue
        cands = proc.get("cpt_candidates")
        if not isinstance(cands, list):
            continue
        for code in cands:
            value = str(code).strip()
            if value:
                out.add(value)
    return out


def _collect_performed_flags(value: Any, *, prefix: str, out: set[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            if key == "performed" and child is True:
                out.add(child_prefix)
            _collect_performed_flags(child, prefix=child_prefix, out=out)
        return

    if isinstance(value, list):
        list_prefix = f"{prefix}[*]" if prefix else "[*]"
        for child in value:
            _collect_performed_flags(child, prefix=list_prefix, out=out)


def _bundle_performed_flags(payload: dict[str, Any]) -> set[str]:
    flags: set[str] = set()
    procedures = payload.get("procedures")
    if not isinstance(procedures, list):
        return flags

    for proc in procedures:
        if not isinstance(proc, dict):
            continue
        proc_type = str(proc.get("proc_type") or "proc").strip()
        data = proc.get("data")
        if isinstance(data, dict):
            _collect_performed_flags(data, prefix=proc_type, out=flags)
    return flags


def _cpt_jaccard(gold: set[str], pred: set[str]) -> float:
    union = gold | pred
    if not union:
        return 1.0
    return float(len(gold & pred) / len(union))


def _flag_f1(gold: set[str], pred: set[str]) -> float:
    tp = len(gold & pred)
    fp = len(pred - gold)
    fn = len(gold - pred)
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    if precision + recall == 0:
        return 0.0
    return float(2.0 * precision * recall / (precision + recall))


def _avg(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


class Seq2SeqJSONDataset(Dataset):
    def __init__(
        self,
        *,
        examples: list[TrainingExample],
        tokenizer: Any,
        max_source_length: int,
        max_target_length: int,
        use_codec: bool,
        use_json_brace_placeholders: bool,
    ):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length
        self.use_codec = use_codec
        self.use_json_brace_placeholders = use_json_brace_placeholders

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        ex = self.examples[idx]
        source = format_source_prompt(ex.prompt_text)
        target = _encode_json_braces_for_tokenizer(
            format_target_text(ex.target_payload, use_codec=self.use_codec),
            use_placeholders=self.use_json_brace_placeholders,
        )

        source_tokens = self.tokenizer(
            source,
            truncation=True,
            max_length=self.max_source_length,
        )
        target_tokens = self.tokenizer(
            text_target=target,
            truncation=True,
            max_length=self.max_target_length,
        )

        labels = [
            tok if tok != self.tokenizer.pad_token_id else -100
            for tok in target_tokens["input_ids"]
        ]

        return {
            "input_ids": source_tokens["input_ids"],
            "attention_mask": source_tokens["attention_mask"],
            "labels": labels,
        }


def build_compute_metrics(tokenizer: Any):
    def compute_metrics(eval_pred):
        import numpy as np

        predictions, labels = eval_pred
        if isinstance(predictions, tuple):
            predictions = predictions[0]

        def _coerce_token_ids(value: Any) -> np.ndarray:
            arr = np.asarray(value)
            if arr.ndim == 3:
                # Logits -> token ids
                arr = arr.argmax(axis=-1)
            if arr.dtype == object:
                arr = np.asarray([[int(tok) for tok in row] for row in value], dtype=np.int64)
            else:
                arr = arr.astype(np.int64, copy=False)
            return arr

        pred_ids = _coerce_token_ids(predictions).copy()
        # Some trainer/generation paths pad with -100; tokenizer can't decode negatives.
        pred_ids[pred_ids < 0] = int(tokenizer.pad_token_id or 0)
        max_id = int(len(tokenizer) - 1)
        unk_id = int(tokenizer.unk_token_id if tokenizer.unk_token_id is not None else (tokenizer.pad_token_id or 0))
        pred_ids[pred_ids > max_id] = unk_id
        # Keep special tokens so `<extra_id_0>` placeholders survive decoding;
        # `ml.lib.reporter_json_parse` normalizes them back to `{`/`}`.
        pred_texts = tokenizer.batch_decode(pred_ids, skip_special_tokens=False)

        label_ids = _coerce_token_ids(labels).copy()
        label_ids[label_ids == -100] = int(tokenizer.pad_token_id or 0)
        label_ids[label_ids < 0] = int(tokenizer.pad_token_id or 0)
        label_ids[label_ids > max_id] = unk_id
        label_texts = tokenizer.batch_decode(label_ids, skip_special_tokens=False)

        parsed_pred = 0
        parsed_label = 0
        exact_payload_matches = 0
        cpt_scores: list[float] = []
        flag_scores: list[float] = []

        for pred_text, gold_text in zip(pred_texts, label_texts):
            pred_payload: dict[str, Any] | None = None
            gold_payload: dict[str, Any] | None = None

            try:
                _bundle_pred, pred_payload, _notes = parse_and_validate_bundle(pred_text, decode_codec=True)
                parsed_pred += 1
            except Exception:
                pred_payload = None

            try:
                _bundle_gold, gold_payload, _notes = parse_and_validate_bundle(gold_text, decode_codec=True)
                parsed_label += 1
            except Exception:
                gold_payload = None

            if pred_payload is not None and gold_payload is not None:
                if json.dumps(pred_payload, sort_keys=True, ensure_ascii=False) == json.dumps(
                    gold_payload,
                    sort_keys=True,
                    ensure_ascii=False,
                ):
                    exact_payload_matches += 1

                cpt_scores.append(
                    _cpt_jaccard(
                        _bundle_cpt_set(gold_payload),
                        _bundle_cpt_set(pred_payload),
                    )
                )
                flag_scores.append(
                    _flag_f1(
                        _bundle_performed_flags(gold_payload),
                        _bundle_performed_flags(pred_payload),
                    )
                )
            else:
                cpt_scores.append(0.0)
                flag_scores.append(0.0)

        total = max(1, len(pred_texts))
        avg_cpt_jaccard = _avg(cpt_scores)
        avg_performed_flag_f1 = _avg(flag_scores)
        avg_clinical_score = (avg_cpt_jaccard + avg_performed_flag_f1) / 2.0
        return {
            "bundle_parse_success_rate": parsed_pred / total,
            "gold_bundle_parse_rate": parsed_label / total,
            "exact_payload_match_rate": exact_payload_matches / total,
            "avg_cpt_jaccard": avg_cpt_jaccard,
            "avg_performed_flag_f1": avg_performed_flag_f1,
            "avg_clinical_score": avg_clinical_score,
        }

    return compute_metrics


def _drop_long_targets(
    examples: list[TrainingExample],
    *,
    tokenizer: Any,
    max_target_length: int,
    use_codec: bool,
    use_json_brace_placeholders: bool,
) -> tuple[list[TrainingExample], int]:
    kept: list[TrainingExample] = []
    dropped = 0
    for ex in examples:
        target = _encode_json_braces_for_tokenizer(
            format_target_text(ex.target_payload, use_codec=use_codec),
            use_placeholders=use_json_brace_placeholders,
        )
        token_ids = tokenizer(text_target=target, truncation=False).input_ids
        if len(token_ids) > max_target_length:
            dropped += 1
            continue
        kept.append(ex)
    return kept, dropped


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.train.exists():
        raise FileNotFoundError(f"Train dataset missing: {args.train}")
    if not args.val.exists():
        raise FileNotFoundError(f"Validation dataset missing: {args.val}")

    use_codec, manifest = resolve_codec_setting(args.use_short_key_codec, args.manifest)
    max_target_length = resolve_target_length(args.max_target_length, manifest)

    train_examples = load_examples(args.train)
    val_examples = load_examples(args.val)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    use_json_brace_placeholders = _tokenizer_requires_json_brace_placeholders(tokenizer)
    if use_json_brace_placeholders:
        print("Tokenizer lacks `{}` tokens; using T5 brace placeholders for JSON targets.", file=sys.stderr)

    drop_long_targets = str(getattr(args, "drop_long_targets", "true")).strip().lower() == "true"
    dropped_train = 0
    dropped_val = 0
    if drop_long_targets:
        train_examples, dropped_train = _drop_long_targets(
            train_examples,
            tokenizer=tokenizer,
            max_target_length=max_target_length,
            use_codec=use_codec,
            use_json_brace_placeholders=use_json_brace_placeholders,
        )
        val_examples, dropped_val = _drop_long_targets(
            val_examples,
            tokenizer=tokenizer,
            max_target_length=max_target_length,
            use_codec=use_codec,
            use_json_brace_placeholders=use_json_brace_placeholders,
        )
        print(
            f"Dropped long-target examples: train={dropped_train}, val={dropped_val} "
            f"(max_target_length={max_target_length})",
            file=sys.stderr,
        )
        if not train_examples:
            raise RuntimeError("All training examples exceeded max_target_length; increase --max-target-length.")
        if not val_examples:
            raise RuntimeError("All validation examples exceeded max_target_length; increase --max-target-length.")

    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)

    train_dataset = Seq2SeqJSONDataset(
        examples=train_examples,
        tokenizer=tokenizer,
        max_source_length=args.max_source_length,
        max_target_length=max_target_length,
        use_codec=use_codec,
        use_json_brace_placeholders=use_json_brace_placeholders,
    )
    val_dataset = Seq2SeqJSONDataset(
        examples=val_examples,
        tokenizer=tokenizer,
        max_source_length=args.max_source_length,
        max_target_length=max_target_length,
        use_codec=use_codec,
        use_json_brace_placeholders=use_json_brace_placeholders,
    )

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    fp16_choice = str(getattr(args, "fp16", "auto")).strip().lower()
    bf16_choice = str(getattr(args, "bf16", "auto")).strip().lower()

    if bf16_choice == "true":
        if not (torch.cuda.is_available() and torch.cuda.is_bf16_supported()):
            raise RuntimeError("--bf16 true requested, but bf16 is not supported on this device.")
        bf16 = True
    elif bf16_choice == "false":
        bf16 = False
    else:
        bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    if fp16_choice == "true":
        fp16 = True
    elif fp16_choice == "false":
        fp16 = False
    else:
        fp16 = torch.cuda.is_available()

    if bf16 and fp16:
        # Prefer bf16 for stability (wider exponent range).
        fp16 = False

    # transformers>=4.56 renamed `evaluation_strategy` -> `eval_strategy`.
    # Keep a small compatibility shim so this script works across versions.
    args_kwargs: dict[str, Any] = {
        "output_dir": str(output_dir),
        "overwrite_output_dir": True,
        "seed": args.seed,
        "num_train_epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "per_device_train_batch_size": args.train_batch_size,
        "per_device_eval_batch_size": args.eval_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation,
        "weight_decay": args.weight_decay,
        "predict_with_generate": True,
        "generation_max_length": max_target_length,
        "evaluation_strategy": "epoch",
        "save_strategy": "epoch",
        "logging_strategy": "steps",
        "logging_steps": 50,
        "save_total_limit": 2,
        "load_best_model_at_end": True,
        "metric_for_best_model": "avg_clinical_score",
        "greater_is_better": True,
        "fp16": fp16,
        "bf16": bf16,
        "remove_unused_columns": False,
        "report_to": [],
    }
    sig = inspect.signature(Seq2SeqTrainingArguments.__init__)
    if "evaluation_strategy" not in sig.parameters and "eval_strategy" in sig.parameters:
        args_kwargs["eval_strategy"] = args_kwargs.pop("evaluation_strategy")
    training_args = Seq2SeqTrainingArguments(**args_kwargs)

    trainer_kwargs: dict[str, Any] = {
        "model": model,
        "args": training_args,
        "train_dataset": train_dataset,
        "eval_dataset": val_dataset,
        "data_collator": DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model),
        "compute_metrics": build_compute_metrics(tokenizer),
        "callbacks": [EarlyStoppingCallback(early_stopping_patience=args.early_stopping_patience)],
    }
    # transformers>=4.56 renamed `tokenizer` -> `processing_class`.
    trainer_sig = inspect.signature(Seq2SeqTrainer.__init__)
    if "processing_class" in trainer_sig.parameters:
        trainer_kwargs["processing_class"] = tokenizer
    else:
        trainer_kwargs["tokenizer"] = tokenizer
    trainer = Seq2SeqTrainer(**trainer_kwargs)

    try:
        train_result = trainer.train()
    except torch.OutOfMemoryError as exc:
        # Provide actionable guidance instead of a giant stack trace.
        msg = (
            "CUDA out of memory during training.\n\n"
            "Common fixes (try in this order):\n"
            "  1) Make sure no other GPU jobs are running (check `nvidia-smi`).\n"
            "  2) Use a smaller model (e.g., google/flan-t5-base or google/flan-t5-small).\n"
            "  3) Reduce batch sizes to 1 and increase gradient accumulation.\n"
            "  4) Reduce max lengths (max_target_length is the biggest driver).\n\n"
            "Example command for 12GB GPUs:\n"
            "  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \\\n"
            "  python ml/scripts/train_reporter_prompt_to_bundle.py \\\n"
            "    --model-name google/flan-t5-base \\\n"
            "    --train-batch-size 1 --eval-batch-size 1 \\\n"
            "    --gradient-accumulation 16 \\\n"
            "    --max-source-length 384 \\\n"
            "    --max-target-length 768 \\\n"
            "    --bf16 true --fp16 false \\\n"
            "    --output-dir artifacts/reporter_prompt_bundle_v1_t5base_mt768\n"
        )
        print(msg, file=sys.stderr)
        raise
    eval_metrics = trainer.evaluate()

    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    summary = {
        "model_name": args.model_name,
        "output_dir": str(output_dir),
        "train_rows": len(train_examples),
        "val_rows": len(val_examples),
        "use_short_key_codec": use_codec,
        "use_json_brace_placeholders": use_json_brace_placeholders,
        "drop_long_targets": drop_long_targets,
        "dropped_long_targets": {"train": dropped_train, "val": dropped_val},
        "fp16": fp16,
        "bf16": bf16,
        "max_source_length": args.max_source_length,
        "max_target_length": max_target_length,
        "train_metrics": train_result.metrics,
        "eval_metrics": eval_metrics,
    }

    summary_path = output_dir / "training_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Training complete. Model saved to: {output_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
