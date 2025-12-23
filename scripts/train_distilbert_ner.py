#!/usr/bin/env python3
"""
Train a DistilBERT NER (token classification) model from pre-tokenized WordPiece tokens + BIO tags.

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
from typing import Any, Dict, List, Tuple

import torch
from torch.utils.data import Dataset

from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    DataCollatorForTokenClassification,
    Trainer,
    TrainingArguments,
)

# Optional but recommended for evaluation:
# pip install seqeval
try:
    import evaluate  # type: ignore
    _HAVE_EVALUATE = True
except Exception:
    _HAVE_EVALUATE = False


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


def build_label_maps(rows: List[Dict[str, Any]]) -> Tuple[List[str], Dict[str, int], Dict[int, str]]:
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
        return None

    seqeval = evaluate.load("seqeval")

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
        # Return the common aggregate numbers
        return {
            "precision": results.get("overall_precision", 0.0),
            "recall": results.get("overall_recall", 0.0),
            "f1": results.get("overall_f1", 0.0),
            "accuracy": results.get("overall_accuracy", 0.0),
        }

    return compute_metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl")
    ap.add_argument("--model", default="distilbert-base-uncased")
    ap.add_argument("--output-dir", default="artifacts/phi_distilbert_ner")
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
    args = ap.parse_args()

    set_seed(args.seed)

    rows = read_jsonl(args.data, limit=args.limit)
    if not rows:
        raise RuntimeError(f"No rows loaded from {args.data}")

    label_list, label2id, id2label = build_label_maps(rows)

    os.makedirs(args.output_dir, exist_ok=True)
    with open(os.path.join(args.output_dir, "label_map.json"), "w") as f:
        json.dump(
            {"label_list": label_list, "label2id": label2id, "id2label": {str(k): v for k, v in id2label.items()}},
            f,
            indent=2,
        )

    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)

    train_rows, eval_rows = split_train_eval(rows, eval_ratio=args.eval_ratio, seed=args.seed)

    train_ds = WordPieceNERDataset(train_rows, tokenizer, label2id, max_length=args.max_length)
    eval_ds = WordPieceNERDataset(eval_rows, tokenizer, label2id, max_length=args.max_length)

    model = AutoModelForTokenClassification.from_pretrained(
        args.model,
        num_labels=len(label_list),
        id2label=id2label,
        label2id=label2id,
    )

    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer, padding=True)

    compute_metrics = build_compute_metrics(id2label)

    # --- Build TrainingArguments with backwards/forwards compatibility ---
    # Some transformers versions use `evaluation_strategy`, others use `eval_strategy`.
    # We'll try evaluation_strategy first, then fall back.
    eval_mode = "steps" if len(eval_rows) > 0 else "no"

    training_args_kwargs: dict[str, object] = dict(
        output_dir=args.output_dir,
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
        load_best_model_at_end=True if len(eval_rows) > 0 else False,
        fp16=args.fp16,
        bf16=args.bf16,
        report_to="none",
        no_cuda=False,
        use_mps_device=True,
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

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds if len(eval_rows) > 0 else None,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

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
