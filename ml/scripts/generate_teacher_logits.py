#!/usr/bin/env python3
"""Generate teacher logits for distillation from a trained registry model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

from ml.lib.ml_coder.distillation_io import load_label_fields_json
from ml.lib.ml_coder.registry_label_schema import compute_encounter_id


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _pick_text(obj: dict[str, Any]) -> str:
    return str(obj.get("note_text") or obj.get("text") or obj.get("note") or obj.get("raw_text") or "").strip()


def _pick_id(obj: dict[str, Any], text: str) -> str:
    for key in ("encounter_id", "id", "note_id"):
        value = obj.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return compute_encounter_id(text)


def iter_jsonl(path: Path):
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield line_num, obj


def encode_head_tail(
    tokenizer,
    texts: list[str],
    *,
    max_length: int,
    head_tokens: int,
    tail_tokens: int,
) -> dict[str, torch.Tensor]:
    cls_id = int(tokenizer.cls_token_id)
    sep_id = int(tokenizer.sep_token_id)
    pad_id = int(tokenizer.pad_token_id)
    content_max = max_length - 2

    batch_ids: list[list[int]] = []
    for text in texts:
        ids = tokenizer(text, add_special_tokens=False, truncation=False)["input_ids"]
        if len(ids) > content_max:
            ids = ids[:head_tokens] + ids[-tail_tokens:]
        full = [cls_id] + ids + [sep_id]
        if len(full) < max_length:
            full = full + [pad_id] * (max_length - len(full))
        else:
            full = full[:max_length]
        batch_ids.append(full)

    input_ids = torch.tensor(batch_ids, dtype=torch.long)
    attention_mask = (input_ids != pad_id).long()
    return {"input_ids": input_ids, "attention_mask": attention_mask}


class TeacherModel(nn.Module):
    def __init__(self, model_dir: Path, num_labels: int) -> None:
        super().__init__()
        self.base = AutoModel.from_pretrained(str(model_dir))
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.base.config.hidden_size, num_labels)
        state = torch.load(model_dir / "classifier.pt", map_location="cpu")
        self.classifier.load_state_dict(state)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        out = self.base(input_ids=input_ids, attention_mask=attention_mask)
        pooled = self.dropout(out.last_hidden_state[:, 0, :])
        return self.classifier(pooled)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-dir", type=Path, required=True, help="Teacher model directory")
    p.add_argument("--input-jsonl", type=Path, required=True, help="JSONL with note text + IDs")
    p.add_argument(
        "--label-fields",
        type=Path,
        default=None,
        help="Ordered label list JSON (default: <model-dir>/label_fields.json)",
    )
    p.add_argument("--out", type=Path, required=True, help="Output .npz path")
    p.add_argument(
        "--meta-out",
        type=Path,
        default=None,
        help="Optional meta JSON sidecar (default: alongside --out)",
    )
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--max-length", type=int, default=512)
    p.add_argument("--head-tokens", type=int, default=382)
    p.add_argument("--tail-tokens", type=int, default=128)
    p.add_argument("--dtype", choices=["float16", "float32"], default="float16")
    p.add_argument("--device", type=str, default=None, help="cuda|cpu (default: auto)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    model_dir = args.model_dir
    if not model_dir.exists():
        raise SystemExit(f"Model dir not found: {model_dir}")

    label_fields_path = args.label_fields or (model_dir / "label_fields.json")
    label_fields = load_label_fields_json(label_fields_path)

    classifier_path = model_dir / "classifier.pt"
    if not classifier_path.exists():
        raise SystemExit(f"Missing classifier weights: {classifier_path}")

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    tokenizer_dir = model_dir / "tokenizer"
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir if tokenizer_dir.exists() else model_dir))

    model = TeacherModel(model_dir=model_dir, num_labels=len(label_fields))
    model.to(device)
    model.eval()

    ids: list[str] = []
    logits_chunks: list[np.ndarray] = []

    batch_texts: list[str] = []
    batch_ids: list[str] = []

    def flush():
        if not batch_texts:
            return
        enc = encode_head_tail(
            tokenizer,
            batch_texts,
            max_length=int(args.max_length),
            head_tokens=int(args.head_tokens),
            tail_tokens=int(args.tail_tokens),
        )
        with torch.no_grad():
            batch_logits = model(enc["input_ids"].to(device), enc["attention_mask"].to(device))
        logits_chunks.append(batch_logits.detach().cpu().numpy())
        ids.extend(batch_ids)
        batch_texts.clear()
        batch_ids.clear()

    for _line_num, obj in tqdm(iter_jsonl(args.input_jsonl), desc="Reading notes"):
        text = _pick_text(obj)
        if not text:
            continue
        eid = _pick_id(obj, text)
        batch_texts.append(text)
        batch_ids.append(eid)
        if len(batch_texts) >= int(args.batch_size):
            flush()

    flush()

    if not ids:
        raise SystemExit("No valid notes found in input JSONL.")

    logits = np.vstack(logits_chunks)
    if args.dtype == "float16":
        logits = logits.astype(np.float16)
    else:
        logits = logits.astype(np.float32)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out, ids=np.array(ids), logits=logits, label_fields=np.array(label_fields))

    meta_out = args.meta_out or args.out.with_name("teacher_logits_meta.json")
    meta = {
        "model_dir": str(model_dir),
        "classifier_sha256": _sha256_file(classifier_path)[:16],
        "label_fields_sha256": _sha256_file(Path(label_fields_path))[:16],
        "n": int(logits.shape[0]),
        "l": int(logits.shape[1]),
        "dtype": str(logits.dtype),
        "input_jsonl": str(args.input_jsonl),
    }
    meta_out.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote logits: {args.out} (N={logits.shape[0]}, L={logits.shape[1]})")
    print(f"Wrote meta: {meta_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
