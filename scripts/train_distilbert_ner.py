#!/usr/bin/env python3
"""
Train a biomedical BERT NER (token classification) model from pre-tokenized WordPiece tokens + BIO tags.

Expected JSONL schema per line:
{
  "tokens": ["du", "##mon", ...],          # WordPiece tokens
  "ner_tags": ["O", "B-ID", "I-ID", ...],  # BIO strings aligned to tokens
  ... (other fields ignored)
}

This script DOES NOT re-tokenize the text. It converts tokens -> input_ids via tokenizer.convert_tokens_to_ids().
That keeps your hard-won alignment intact.

Outputs:
- model + tokenizer saved to --output-dir
- label mapping saved to --output-dir/label_map.json
"""

import argparse
import json
import os
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple

import torch
import torch.nn as nn
from torch.utils.data import Dataset
from collections import Counter

from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    DataCollatorForTokenClassification,
    Trainer,
    TrainingArguments,
)

ALLOWED_LABEL_TYPES: Set[str] = {
    "ANAT_LN_STATION",
    "PROC_ACTION",
    "PROC_METHOD",
    "DEV_STENT",
    "DEV_VALVE",
    "OBS_ROSE",
}


class WeightedLossTrainer(Trainer):
    """Custom Trainer that applies class weights to handle label imbalance."""

    def __init__(self, class_weights: torch.Tensor | None = None, **kwargs):
        super().__init__(**kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        if self.class_weights is not None:
            loss_fct = nn.CrossEntropyLoss(
                weight=self.class_weights.to(logits.device),
                ignore_index=-100,
            )
        else:
            loss_fct = nn.CrossEntropyLoss(ignore_index=-100)

        # Reshape for cross entropy: (batch * seq_len, num_labels)
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))

        return (loss, outputs) if return_outputs else loss


def compute_class_weights(rows: list, label2id: dict, smoothing: float = 0.1) -> torch.Tensor:
    """Compute inverse frequency class weights with smoothing."""
    label_counts = Counter()
    for row in rows:
        for tag in row.get("ner_tags", []):
            norm_tag = normalize_tag(tag)
            label_id = label2id.get(norm_tag, label2id["O"])
            label_counts[label_id] += 1

    num_labels = len(label2id)
    total = sum(label_counts.values())

    weights = []
    for i in range(num_labels):
        count = label_counts.get(i, 1)
        # Inverse frequency with smoothing to avoid extreme weights
        weight = (total / (num_labels * count)) ** smoothing
        weights.append(weight)

    # Normalize so mean weight is 1.0
    weights_tensor = torch.tensor(weights, dtype=torch.float32)
    weights_tensor = weights_tensor / weights_tensor.mean()

    return weights_tensor

# Optional but recommended for evaluation:
# pip install seqeval
try:
    import evaluate  # type: ignore
    from seqeval.metrics import classification_report
    _HAVE_EVALUATE = True
except Exception:
    _HAVE_EVALUATE = False
    classification_report = None


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def read_jsonl(path: str, limit: int | None = None) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_label_maps(
    rows: List[Dict[str, Any]],
    allowed_categories: Set[str] | None = None,
) -> Tuple[List[str], Dict[str, int], Dict[int, str]]:
    if allowed_categories:
        label_set = set(allowed_categories)
    else:
        label_set = set()
        for r in rows:
            for t in r.get("ner_tags", []):
                if t and t != "O":
                    label_set.add(t.split("-", 1)[-1])
    # Always include "O" category for mapping convenience
    categories = ["O"] + sorted(label_set)

    # Expand to BIO labels:
    label_list = ["O"]
    for cat in categories:
        if cat == "O":
            continue
        label_list.extend([f"B-{cat}", f"I-{cat}"])

    label2id = {lbl: i for i, lbl in enumerate(label_list)}
    id2label = {i: lbl for lbl, i in label2id.items()}
    return label_list, label2id, id2label


def normalize_id2label(raw: Dict[Any, Any]) -> Dict[int, str]:
    id2label: Dict[int, str] = {}
    for key, value in raw.items():
        try:
            idx = int(key)
        except (TypeError, ValueError):
            continue
        id2label[idx] = str(value)
    return id2label


def normalize_label2id(raw: Dict[Any, Any]) -> Dict[str, int]:
    label2id: Dict[str, int] = {}
    for key, value in raw.items():
        try:
            label2id[str(key)] = int(value)
        except (TypeError, ValueError):
            continue
    return label2id


def load_label_map_from_dir(model_dir: str) -> Tuple[List[str], Dict[str, int], Dict[int, str]] | None:
    label_map_path = os.path.join(model_dir, "label_map.json")
    if not os.path.exists(label_map_path):
        return None
    with open(label_map_path, "r") as f:
        data = json.load(f)
    label_list = data.get("label_list")
    label2id = normalize_label2id(data.get("label2id", {}))
    id2label = normalize_id2label(data.get("id2label", {}))
    if not label_list and id2label:
        label_list = [id2label[i] for i in sorted(id2label)]
    if id2label and not label2id:
        label2id = {v: k for k, v in id2label.items()}
    if label2id and not id2label:
        id2label = {v: k for k, v in label2id.items()}
    if not label_list:
        return None
    return label_list, label2id, id2label


def label_maps_from_model(model: Any) -> Tuple[List[str], Dict[str, int], Dict[int, str]] | None:
    if model is None or not hasattr(model, "config"):
        return None
    id2label = normalize_id2label(getattr(model.config, "id2label", {}) or {})
    if id2label:
        label_list = [id2label[i] for i in sorted(id2label)]
        label2id = {v: k for k, v in id2label.items()}
        return label_list, label2id, id2label
    label2id = normalize_label2id(getattr(model.config, "label2id", {}) or {})
    if label2id:
        id2label = {v: k for k, v in label2id.items()}
        label_list = [id2label[i] for i in sorted(id2label)]
        return label_list, label2id, id2label
    return None


def resolve_label_maps(
    rows: List[Dict[str, Any]],
    model: Any | None = None,
    model_dir: str | None = None,
) -> Tuple[List[str], Dict[str, int], Dict[int, str]]:
    from_dir = load_label_map_from_dir(model_dir) if model_dir else None
    if from_dir:
        return from_dir
    from_model = label_maps_from_model(model)
    if from_model:
        return from_model
    return build_label_maps(rows)


def normalize_tag(tag: str) -> str:
    # Accept already-normalized BIO tags; treat unknown as O to be safe.
    if not tag:
        return "O"
    if tag == "O":
        return "O"
    if "-" not in tag:
        return "O"
    prefix, cat = tag.split("-", 1)
    if prefix not in ("B", "I"):
        return "O"
    return f"{prefix}-{cat}"


def apply_label_allowlist(
    rows: List[Dict[str, Any]],
    allowed_categories: Set[str],
) -> List[Dict[str, Any]]:
    filtered_rows: List[Dict[str, Any]] = []
    for row in rows:
        tags = row.get("ner_tags") or []
        if not tags:
            filtered_rows.append(row)
            continue
        filtered_tags: List[str] = []
        for tag in tags:
            normalized = normalize_tag(tag)
            if normalized == "O":
                filtered_tags.append("O")
                continue
            _, category = normalized.split("-", 1)
            if category in allowed_categories:
                filtered_tags.append(normalized)
            else:
                filtered_tags.append("O")
        if filtered_tags == tags:
            filtered_rows.append(row)
        else:
            updated = dict(row)
            updated["ner_tags"] = filtered_tags
            filtered_rows.append(updated)
    return filtered_rows


def truncate_to_max(tokens: List[str], tags: List[str], max_wordpieces: int) -> Tuple[List[str], List[str]]:
    # max_wordpieces excludes [CLS]/[SEP]; we add those later
    if len(tokens) <= max_wordpieces:
        return tokens, tags
    return tokens[:max_wordpieces], tags[:max_wordpieces]


class WordPieceNERDataset(Dataset):
    def __init__(
        self,
        rows: List[Dict[str, Any]],
        tokenizer: Any,
        label2id: Dict[str, int],
        max_length: int = 512,
    ):
        self.rows = rows
        self.tokenizer = tokenizer
        self.label2id = label2id
        self.max_wordpieces = max_length - 2  # reserve for [CLS]/[SEP]

        self.cls_id = tokenizer.cls_token_id
        self.sep_id = tokenizer.sep_token_id
        self.unk_id = tokenizer.unk_token_id

        if self.cls_id is None or self.sep_id is None:
            raise RuntimeError("Tokenizer must have CLS/SEP token ids.")

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        r = self.rows[idx]
        tokens: List[str] = r.get("tokens") or []
        tags: List[str] = r.get("ner_tags") or []

        if len(tokens) != len(tags):
            # Hard fail: alignment must be exact
            raise ValueError(f"tokens/ner_tags length mismatch at idx={idx}: {len(tokens)} vs {len(tags)}")

        tokens, tags = truncate_to_max(tokens, tags, self.max_wordpieces)

        # Convert tokens -> ids
        ids = self.tokenizer.convert_tokens_to_ids(tokens)
        # convert_tokens_to_ids returns int or None depending on tokenizer; normalize:
        input_ids = []
        for x in ids:
            if x is None or x == -1:
                input_ids.append(self.unk_id)
            else:
                input_ids.append(int(x))

        # Build labels aligned to tokens
        labels = []
        for t in tags:
            nt = normalize_tag(t)
            labels.append(self.label2id.get(nt, self.label2id["O"]))

        # Add special tokens; set their labels to -100 so loss ignores them
        input_ids = [self.cls_id] + input_ids + [self.sep_id]
        labels = [-100] + labels + [-100]
        attention_mask = [1] * len(input_ids)

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def split_train_eval(rows: List[Dict[str, Any]], eval_ratio: float, seed: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = random.Random(seed)
    rows_shuffled = rows[:]
    rng.shuffle(rows_shuffled)
    n_eval = int(len(rows_shuffled) * eval_ratio)
    eval_rows = rows_shuffled[:n_eval]
    train_rows = rows_shuffled[n_eval:]
    return train_rows, eval_rows


def build_compute_metrics(id2label: Dict[int, str]):
    if not _HAVE_EVALUATE:
        return None, "evaluate/seqeval not installed; metrics limited to eval_loss."
    try:
        seqeval = evaluate.load("seqeval")
    except Exception as exc:
        return None, f"seqeval unavailable ({exc}); metrics limited to eval_loss."

    def compute_metrics(p):
        predictions, labels = p
        preds = predictions.argmax(-1)

        true_predictions = []
        true_labels = []

        for pred_seq, lab_seq in zip(preds, labels):
            pred_tags = []
            lab_tags = []
            for p_id, l_id in zip(pred_seq, lab_seq):
                if l_id == -100:
                    continue
                pred_tags.append(id2label[int(p_id)])
                lab_tags.append(id2label[int(l_id)])
            true_predictions.append(pred_tags)
            true_labels.append(lab_tags)

        results = seqeval.compute(predictions=true_predictions, references=true_labels)

        # Print per-entity breakdown using seqeval's classification_report
        if classification_report is not None:
            has_entities = any(tag != "O" for seq in true_labels for tag in seq)
            has_predictions = any(tag != "O" for seq in true_predictions for tag in seq)
            if has_entities or has_predictions:
                print("\n" + "=" * 80)
                print("SEQEVAL PER-ENTITY REPORT (entity-level)")
                print(classification_report(true_labels, true_predictions, digits=4))
                print("=" * 80 + "\n")
            else:
                print("\n" + "=" * 80)
                print("SEQEVAL PER-ENTITY REPORT skipped (no entity labels in eval set)")
                print("=" * 80 + "\n")
        
        # Return the common aggregate numbers
        return {
            "precision": results.get("overall_precision", 0.0),
            "recall": results.get("overall_recall", 0.0),
            "f1": results.get("overall_f1", 0.0),
            "accuracy": results.get("overall_accuracy", 0.0),
        }

    return compute_metrics, None


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl")
    ap.add_argument("--train-data", default=None)
    ap.add_argument("--patched-data", default=None)
    ap.add_argument("--hard-negative-jsonl", default=None)
    ap.add_argument("--model", default="microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext")
    ap.add_argument("--resume-from", default=None)
    ap.add_argument("--output-dir", default="artifacts/phi_distilbert_ner")
    ap.add_argument("--model-dir", default=None)
    ap.add_argument("--eval-only", action="store_true")
    ap.add_argument("--eval-split", choices=["heldout", "all"], default="heldout")
    ap.add_argument("--max-length", type=int, default=512)
    ap.add_argument("--eval-ratio", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--limit", type=int, default=None)

    # training params
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--train-batch", type=int, default=16)
    ap.add_argument("--eval-batch", type=int, default=32)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--warmup-ratio", type=float, default=0.06)
    ap.add_argument("--fp16", action="store_true")
    ap.add_argument("--bf16", action="store_true")
    ap.add_argument("--save-steps", type=int, default=500)
    ap.add_argument("--eval-steps", type=int, default=500)
    ap.add_argument("--logging-steps", type=int, default=50)
    ap.add_argument("--class-weights", action="store_true", help="Use class weights for imbalanced labels")
    ap.add_argument("--weight-smoothing", type=float, default=0.3, help="Smoothing factor for class weights (0-1)")
    ap.add_argument("--cpu", action="store_true", help="Force CPU mode (disable MPS/CUDA)")
    ap.add_argument("--gradient-accumulation-steps", type=int, default=1, help="Number of gradient accumulation steps (reduces memory usage)")
    ap.add_argument("--gradient-checkpointing", action="store_true", help="Enable gradient checkpointing to save memory")
    ap.add_argument("--mps-high-watermark-ratio", type=float, default=None, help="MPS memory limit ratio (0.0=unlimited, default=auto)")
    return ap


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    return build_arg_parser().parse_args(argv)


def resolve_model_dir(args: argparse.Namespace) -> str:
    return args.model_dir or args.output_dir


def resolve_data_path(args: argparse.Namespace) -> str:
    if args.patched_data and args.hard_negative_jsonl:
        raise ValueError("Use only one of --patched-data or --hard-negative-jsonl.")
    if args.patched_data:
        return args.patched_data
    if args.hard_negative_jsonl:
        return args.hard_negative_jsonl
    return args.train_data or args.data


def resolve_resume_dir(args: argparse.Namespace) -> str | None:
    return args.resume_from


def validate_paths(args: argparse.Namespace, model_dir: str, data_path: str) -> None:
    if not os.path.isfile(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    if args.eval_only and not os.path.isdir(model_dir):
        raise FileNotFoundError(f"Model directory not found: {model_dir}")
    if args.resume_from and not os.path.isdir(args.resume_from):
        raise FileNotFoundError(f"Resume model directory not found: {args.resume_from}")


def main():
    args = parse_args()
    model_dir = resolve_model_dir(args)
    data_path = resolve_data_path(args)
    validate_paths(args, model_dir, data_path)

    set_seed(args.seed)

    # --- Device / CUDA / MPS visibility diagnostics ---
    # Hugging Face `Trainer` will automatically use CUDA or MPS when available.
    # --cpu flag forces CPU mode
    if args.cpu:
        cuda_available = False
        mps_available = False
        print(f"[device] --cpu flag set, forcing CPU mode | torch={torch.__version__}")
    else:
        cuda_available = torch.cuda.is_available()
        mps_available = torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False

    if cuda_available:
        try:
            device_name = torch.cuda.get_device_name(0)
        except Exception:
            device_name = "unknown"
        print(
            f"[device] cuda available: True | "
            f"torch={torch.__version__} | "
            f"cuda={torch.version.cuda} | "
            f"gpus={torch.cuda.device_count()} | "
            f"gpu0={device_name} | "
            f"fp16={bool(args.fp16)} | bf16={bool(args.bf16)}"
        )
    elif mps_available:
        print(
            f"[device] MPS (Apple Silicon) available: True | "
            f"torch={torch.__version__} | "
            f"Using Metal Performance Shaders for GPU acceleration"
        )
        # Set MPS high watermark ratio if specified
        if args.mps_high_watermark_ratio is not None:
            os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = str(args.mps_high_watermark_ratio)
            print(f"[device] MPS high watermark ratio set to: {args.mps_high_watermark_ratio}")
        # Verify MPS is actually working
        try:
            test_tensor = torch.zeros(1, device="mps")
            print(f"[device] MPS device verified: {test_tensor.device}")
        except Exception as e:
            print(f"[device] WARNING: MPS device test failed: {e}")
            mps_available = False
    else:
        print(
            f"[device] cuda available: False, mps available: False (CPU mode) | "
            f"torch={torch.__version__} | "
            f"fp16={bool(args.fp16)} | bf16={bool(args.bf16)}"
        )

    rows = read_jsonl(data_path, limit=args.limit)
    if not rows:
        raise RuntimeError(f"No rows loaded from {data_path}")
    rows = apply_label_allowlist(rows, ALLOWED_LABEL_TYPES)
    print(f"[data] Applied label allowlist: {', '.join(sorted(ALLOWED_LABEL_TYPES))}")

    # Determine device for model placement
    if args.cpu:
        device = torch.device("cpu")
    elif cuda_available:
        device = torch.device("cuda")
    elif mps_available:
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    
    print(f"[device] Model will be placed on: {device}")

    if args.eval_only:
        tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
        model = AutoModelForTokenClassification.from_pretrained(model_dir)
        model = model.to(device)  # Explicitly move to device
        label_list, label2id, id2label = resolve_label_maps(rows, model=model, model_dir=model_dir)
    else:
        resume_dir = resolve_resume_dir(args)
        if resume_dir:
            tokenizer = AutoTokenizer.from_pretrained(resume_dir, use_fast=True)
            model = AutoModelForTokenClassification.from_pretrained(resume_dir)
            model = model.to(device)  # Explicitly move to device
            label_list, label2id, id2label = resolve_label_maps(rows, model=model, model_dir=resume_dir)
        else:
            label_list, label2id, id2label = build_label_maps(rows, allowed_categories=ALLOWED_LABEL_TYPES)
            tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
            model = AutoModelForTokenClassification.from_pretrained(
                args.model,
                num_labels=len(label_list),
                id2label=id2label,
                label2id=label2id,
            )
            # Enable gradient checkpointing if requested (before moving to device)
            if args.gradient_checkpointing:
                if hasattr(model, "gradient_checkpointing_enable"):
                    model.gradient_checkpointing_enable()
                    print("[memory] Gradient checkpointing enabled")
            model = model.to(device)  # Explicitly move to device

        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "label_map.json"), "w") as f:
            json.dump(
                {"label_list": label_list, "label2id": label2id, "id2label": {str(k): v for k, v in id2label.items()}},
                f,
                indent=2,
            )
    
    # Verify model is on the correct device
    print(f"[device] Model is on device: {next(model.parameters()).device}")

    if args.eval_only:
        if args.eval_split == "all":
            eval_rows = rows
        else:
            _, eval_rows = split_train_eval(rows, eval_ratio=args.eval_ratio, seed=args.seed)
        train_rows = []
    else:
        train_rows, eval_rows = split_train_eval(rows, eval_ratio=args.eval_ratio, seed=args.seed)

    if args.eval_only and not eval_rows:
        raise RuntimeError("Eval split produced no rows. Adjust --eval-split/--eval-ratio/--limit.")

    train_ds = WordPieceNERDataset(train_rows, tokenizer, label2id, max_length=args.max_length) if train_rows else None
    eval_ds = WordPieceNERDataset(eval_rows, tokenizer, label2id, max_length=args.max_length)

    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer, padding=True)

    compute_metrics, metrics_note = build_compute_metrics(id2label)
    if metrics_note:
        print(f"[metrics] {metrics_note}")

    # --- Build TrainingArguments with backwards/forwards compatibility ---
    # Some transformers versions use `evaluation_strategy`, others use `eval_strategy`.
    # We'll try evaluation_strategy first, then fall back.
    eval_mode = "no" if args.eval_only else ("steps" if len(eval_rows) > 0 else "no")

    # Determine if we should use MPS (Apple Silicon GPU)
    # Update use_mps in case it was disabled due to device test failure
    use_mps = mps_available and not cuda_available and not args.cpu

    training_args_kwargs: dict[str, object] = dict(
        output_dir=model_dir if args.eval_only else args.output_dir,
        learning_rate=args.lr,
        per_device_train_batch_size=args.train_batch,
        per_device_eval_batch_size=args.eval_batch,
        num_train_epochs=args.epochs,
        weight_decay=args.weight_decay,
        warmup_ratio=args.warmup_ratio,
        eval_steps=args.eval_steps,
        save_steps=args.save_steps,
        logging_steps=args.logging_steps,
        save_total_limit=2,
        load_best_model_at_end=False if args.eval_only else (True if len(eval_rows) > 0 else False),
        fp16=args.fp16,
        bf16=args.bf16,
        report_to="none",
        use_mps_device=use_mps,
        use_cpu=args.cpu,  # Force CPU mode when --cpu flag is set (modern replacement for no_cuda)
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        gradient_checkpointing=args.gradient_checkpointing,
    )
    if compute_metrics and len(eval_rows) > 0:
        training_args_kwargs["metric_for_best_model"] = "f1"

    # Try common arg names across transformers versions
    try:
        training_args = TrainingArguments(
            evaluation_strategy=eval_mode,
            **training_args_kwargs,
        )
    except TypeError:
        training_args = TrainingArguments(
            eval_strategy=eval_mode,
            **training_args_kwargs,
        )

    # Compute class weights if requested
    class_weights = None
    if args.class_weights and train_rows:
        print("[training] Computing class weights for imbalanced labels...")
        class_weights = compute_class_weights(train_rows, label2id, smoothing=args.weight_smoothing)
        print(f"[training] Class weights: {class_weights.tolist()}")

    # Use WeightedLossTrainer if class weights are provided, otherwise standard Trainer
    trainer_cls = WeightedLossTrainer if class_weights is not None else Trainer
    trainer_kwargs = {
        "model": model,
        "args": training_args,
        "train_dataset": train_ds,
        "eval_dataset": eval_ds if len(eval_rows) > 0 else None,
        "data_collator": data_collator,
        "tokenizer": tokenizer,
        "compute_metrics": compute_metrics,
    }
    if class_weights is not None:
        trainer_kwargs["class_weights"] = class_weights

    trainer = trainer_cls(**trainer_kwargs)

    if args.eval_only:
        metrics = trainer.evaluate()
        metrics_path = os.path.join(model_dir, "eval_metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
        print(json.dumps(metrics, indent=2, sort_keys=True))
        return

    trainer.train()

    # Final eval + save
    if len(eval_rows) > 0:
        metrics = trainer.evaluate()
        with open(os.path.join(args.output_dir, "eval_metrics.json"), "w") as f:
            json.dump(metrics, f, indent=2)

    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    print(f"Saved model + tokenizer to: {args.output_dir}")
    print(f"Label map saved to: {os.path.join(args.output_dir, 'label_map.json')}")


if __name__ == "__main__":
    main()
