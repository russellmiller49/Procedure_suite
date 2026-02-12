#!/usr/bin/env python3
"""Fine-tune a causal LLM to generate ProcedureBundle JSON from a reporter prompt.

This is an alternative to the T5 seq2seq trainer, intended for instruction-tuned
models like Llama 3. Uses Unsloth for memory-efficient QLoRA fine-tuning.

Example:
  python ml/scripts/train_reporter_prompt_to_bundle_unsloth.py \\
    --model-name unsloth/llama-3-8b-Instruct-bnb-4bit \\
    --train-batch-size 1 --eval-batch-size 1 \\
    --gradient-accumulation 16 \\
    --max-seq-length 2048 \\
    --output-dir artifacts/reporter_prompt_bundle_v1_llama3_8b_unsloth
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Allow running as a file (python ml/scripts/...) without installing the package.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

DEFAULT_TRAIN = Path("data/ml_training/reporter_prompt/v1/prompt_to_bundle_train.jsonl")
DEFAULT_VAL = Path("data/ml_training/reporter_prompt/v1/prompt_to_bundle_val.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/reporter_prompt_bundle_v1_llama_unsloth")

DEFAULT_MODEL_NAME = "unsloth/llama-3-8b-Instruct-bnb-4bit"
DEFAULT_MAX_SEQ_LENGTH = 2048


@dataclass(frozen=True)
class Example:
    prompt_text: str
    target_payload: dict[str, Any]


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def configure_training_env() -> dict[str, str]:
    """Avoid accidental network/LLM calls from unrelated imports."""
    forced = {
        "PROCSUITE_SKIP_DOTENV": "1",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "REGISTRY_USE_STUB_LLM": "1",
    }
    applied: dict[str, str] = {}
    for key, value in forced.items():
        if os.environ.get(key) != value:
            os.environ[key] = value
            applied[key] = value
    return applied


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument("--val", type=Path, default=DEFAULT_VAL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--max-seq-length", type=int, default=DEFAULT_MAX_SEQ_LENGTH)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--train-batch-size", type=int, default=1)
    parser.add_argument("--eval-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--drop-long-examples",
        type=str.lower,
        choices=["true", "false"],
        default="true",
        help="Drop examples whose prompt+target tokens exceed max_seq_length.",
    )
    parser.add_argument(
        "--bf16",
        type=str.lower,
        choices=["auto", "true", "false"],
        default="auto",
        help="Use bf16 mixed precision when available.",
    )
    parser.add_argument(
        "--fp16",
        type=str.lower,
        choices=["auto", "true", "false"],
        default="auto",
        help="Use fp16 mixed precision (fallback when bf16 not available).",
    )
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.0)
    parser.add_argument("--logging-steps", type=int, default=50)
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


def load_examples(path: Path) -> list[Example]:
    raw_rows = load_jsonl(path)
    out: list[Example] = []
    for row in raw_rows:
        prompt = str(row.get("prompt_text") or "").strip()
        payload = row.get("bundle_target_json")
        if not prompt or not isinstance(payload, dict):
            continue
        out.append(Example(prompt_text=prompt, target_payload=payload))
    if not out:
        raise RuntimeError(f"No valid examples in {path}")
    return out


def format_source_prompt(prompt_text: str) -> str:
    return (
        "Generate a valid ProcedureBundle JSON object from this clinical prompt. "
        "Return JSON only.\n\n"
        f"PROMPT:\n{prompt_text.strip()}"
    )


def format_target_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def format_chat_text(tokenizer: Any, *, prompt_text: str, target_json: str) -> str:
    system = "You are a clinical documentation structuring engine. Output JSON only."
    user = format_source_prompt(prompt_text)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
        {"role": "assistant", "content": target_json},
    ]
    if hasattr(tokenizer, "apply_chat_template") and getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    # Fallback if chat_template is missing.
    return f"{system}\n\n{user}\n\n{target_json}"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.train.exists():
        raise FileNotFoundError(f"Train dataset not found: {args.train}")
    if not args.val.exists():
        raise FileNotFoundError(f"Val dataset not found: {args.val}")

    applied_env = configure_training_env()

    try:
        from unsloth import FastLanguageModel
    except Exception as exc:
        raise RuntimeError(
            "Unsloth is required for this trainer. In your medparse env, install:\n"
            "  pip install -U bitsandbytes peft 'trl==0.24.0' 'datasets==4.3.0'\n"
            "  pip install unsloth unsloth_zoo --no-deps\n"
            "  pip install -U diffusers hf_transfer sentencepiece tyro msgspec cut_cross_entropy\n"
        ) from exc

    import torch
    from datasets import Dataset
    from trl import SFTTrainer
    from trl.trainer.sft_config import SFTConfig

    train_examples = load_examples(args.train)
    val_examples = load_examples(args.val)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model_name,
        max_seq_length=int(args.max_seq_length),
        dtype=None,
        load_in_4bit=True,
    )

    # Llama-style tokenizers often omit an explicit pad token.
    if getattr(tokenizer, "pad_token_id", None) is None and getattr(tokenizer, "eos_token_id", None) is not None:
        tokenizer.pad_token = tokenizer.eos_token

    model = FastLanguageModel.get_peft_model(
        model,
        r=int(args.lora_r),
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=int(args.lora_alpha),
        lora_dropout=float(args.lora_dropout),
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=int(args.seed),
    )

    def to_text_rows(examples: list[Example]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        dropped = 0
        drop_long = str(getattr(args, "drop_long_examples", "true")).strip().lower() == "true"

        for ex in examples:
            target_json = format_target_json(ex.target_payload)
            text = format_chat_text(tokenizer, prompt_text=ex.prompt_text, target_json=target_json)
            if drop_long:
                n_tokens = len(tokenizer(text, truncation=False).input_ids)
                if n_tokens > int(args.max_seq_length):
                    dropped += 1
                    continue
            rows.append({"text": text})
        return rows, dropped

    train_rows, dropped_train = to_text_rows(train_examples)
    val_rows, dropped_val = to_text_rows(val_examples)

    if not train_rows:
        raise RuntimeError("All training rows were dropped; increase --max-seq-length or disable --drop-long-examples.")
    if not val_rows:
        raise RuntimeError("All validation rows were dropped; increase --max-seq-length or disable --drop-long-examples.")

    train_ds = Dataset.from_list(train_rows)
    val_ds = Dataset.from_list(val_rows)

    bf16_choice = str(getattr(args, "bf16", "auto")).strip().lower()
    fp16_choice = str(getattr(args, "fp16", "auto")).strip().lower()

    if bf16_choice == "true":
        bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
        if not bf16:
            raise RuntimeError("--bf16 true requested, but bf16 is not supported on this device.")
    elif bf16_choice == "false":
        bf16 = False
    else:
        bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    if fp16_choice == "true":
        fp16 = True
    elif fp16_choice == "false":
        fp16 = False
    else:
        fp16 = torch.cuda.is_available() and not bf16

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = SFTConfig(
        output_dir=str(output_dir),
        overwrite_output_dir=True,
        num_train_epochs=float(args.epochs),
        per_device_train_batch_size=int(args.train_batch_size),
        per_device_eval_batch_size=int(args.eval_batch_size),
        gradient_accumulation_steps=int(args.gradient_accumulation),
        learning_rate=float(args.learning_rate),
        logging_steps=int(args.logging_steps),
        logging_strategy="steps",
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        bf16=bool(bf16),
        fp16=bool(fp16),
        report_to=[],
        seed=int(args.seed),
        optim="paged_adamw_8bit",
        dataset_text_field="text",
        max_length=int(args.max_seq_length),
        packing=False,
        remove_unused_columns=False,
    )

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        args=training_args,
    )

    trainer.train()
    eval_metrics = trainer.evaluate()

    trainer.model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    summary = {
        "model_name": args.model_name,
        "output_dir": str(output_dir),
        "train_rows": len(train_rows),
        "val_rows": len(val_rows),
        "dropped_long_examples": {"train": int(dropped_train), "val": int(dropped_val)},
        "max_seq_length": int(args.max_seq_length),
        "epochs": float(args.epochs),
        "learning_rate": float(args.learning_rate),
        "train_batch_size": int(args.train_batch_size),
        "eval_batch_size": int(args.eval_batch_size),
        "gradient_accumulation": int(args.gradient_accumulation),
        "bf16": bool(bf16),
        "fp16": bool(fp16),
        "lora": {"r": int(args.lora_r), "alpha": int(args.lora_alpha), "dropout": float(args.lora_dropout)},
        "environment_defaults_applied": applied_env,
        "eval_metrics": {k: float(v) for k, v in (eval_metrics or {}).items() if isinstance(v, (int, float))},
    }
    (output_dir / "training_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote training summary: {output_dir / 'training_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
