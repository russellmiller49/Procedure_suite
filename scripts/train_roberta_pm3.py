#!/usr/bin/env python3
"""Train RoBERTa-PM-M3-Voc-distill for multi-label registry procedure classification.

This script trains the RoBERTa-base-PM-M3-Voc-distill model from Facebook's bio-lm project
for predicting registry procedure flags from clinical procedure notes. Key features:

- Head + Tail truncation to preserve both procedure and complication sections
- pos_weight calculation for severe class imbalance
- Per-class threshold optimization on validation set
- Mixed precision training (fp16) for RTX 4070 Ti

Model: RoBERTa-base-PM-M3-Voc-distill (local)
- From Facebook Research bio-lm project (https://github.com/facebookresearch/bio-lm)
- Trained on PubMed + MIMIC-III with domain-specific vocabulary (PM-M3-Voc)
- Knowledge distillation from larger models for improved performance
- Local path: data/models/RoBERTa-base-PM-M3-Voc-distill/RoBERTa-base-PM-M3-Voc-distill-hf/

Usage:
    python scripts/train_biomed_roberta.py
    python scripts/train_biomed_roberta.py --batch-size 32 --epochs 10
    python scripts/train_biomed_roberta.py --evaluate-only --model-dir data/models/roberta_pm3_registry
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm
from transformers import (
    AutoConfig,
    AutoModel,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class TrainingConfig:
    """Configuration for RoBERTa-PM-M3-Voc-distill training."""

    # Model - Facebook bio-lm RoBERTa with PubMed+MIMIC vocabulary (local download)
    model_name: str = "data/models/RoBERTa-base-PM-M3-Voc-distill/RoBERTa-base-PM-M3-Voc-distill-hf"

    # Data paths (updated for data/ml_training flat files)
    train_csv: Path = field(default_factory=lambda: Path("data/ml_training/registry_train.csv"))
    val_csv: Path = field(default_factory=lambda: Path("data/ml_training/registry_val.csv"))
    test_csv: Path = field(default_factory=lambda: Path("data/ml_training/registry_test.csv"))
    label_fields_json: Path = field(default_factory=lambda: Path("data/ml_training/registry_label_fields_pm3.json"))
    output_dir: Path = field(default_factory=lambda: Path("data/models/roberta_pm3_registry"))

    # Tokenization
    max_length: int = 512
    head_tokens: int = 382  # First N tokens to keep (512 - 128 - 2 for [CLS]/[SEP])
    tail_tokens: int = 128  # Last N tokens to keep

    # Training hyperparameters
    batch_size: int = 16
    learning_rate: float = 2e-5
    num_epochs: int = 5
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0

    # Hardware
    fp16: bool = True
    device: str = field(default_factory=lambda: "cuda" if torch.cuda.is_available() else "cpu")

    # Class imbalance
    pos_weight_cap: float = 100.0  # Cap pos_weight to prevent instability

    # Validation
    val_split: float = 0.1  # Split training data for threshold optimization

    # Logging
    logging_steps: int = 50
    eval_steps: int = 500
    save_steps: int = 1000


# ============================================================================
# Data Loading and Preprocessing
# ============================================================================

def load_label_fields(path: Path) -> list[str]:
    """Load label field names from JSON file."""
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)

def load_registry_csv(path: Path, required_labels: list[str] = None) -> tuple[list[str], np.ndarray, list[str]]:
    """Load registry training/test CSV file.

    Args:
        path: Path to CSV file with note_text and label columns
        required_labels: Optional list of label columns to enforce order/presence.
                        If provided, returns y with columns in this specific order.

    Returns:
        Tuple of (texts, labels_matrix, label_names)
    """
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(f"Registry training file {path} is empty.")

    if "note_text" not in df.columns:
        raise ValueError(f"Registry training file {path} missing required 'note_text' column.")

    # Extract texts
    texts = df["note_text"].fillna("").astype(str).tolist()

    # Determine Label Columns
    if required_labels:
        # Enforce exact columns from training set (or JSON)
        label_cols = required_labels
        # Check for missing columns
        missing = [col for col in label_cols if col not in df.columns]
        if missing:
            print(f"WARNING: Missing columns in {path}, filling with 0: {missing}")
            for col in missing:
                df[col] = 0
    else:
        # Infer columns (Training Phase)
        metadata_cols = {
            "note_text",
            "verified_cpt_codes",
            "source_file",
            "original_split",
            "group_id",
            "style_type",
            "original_index",
        }

        label_cols = []
        skipped_cols = []

        # Only keep binary numeric columns as labels to avoid metadata leakage
        for col in df.columns:
            if col in metadata_cols:
                continue
            numeric = pd.to_numeric(df[col], errors="coerce")
            unique_vals = set(numeric.dropna().unique().tolist())
            if unique_vals and unique_vals.issubset({0, 1}):
                label_cols.append(col)
            else:
                skipped_cols.append(col)

        if skipped_cols:
            print(f"Skipping non-label columns (non-binary values): {skipped_cols}")

        # Sort for consistency
        label_cols.sort()

    if not label_cols:
        raise ValueError(f"Registry training file {path} has no label columns.")

    # Extract label matrix in correct order, coercing safely to ints
    label_df = df[label_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    # Warn and clamp any unexpected values outside {0,1}
    coerced = []
    for col in label_cols:
        unique_vals = set(label_df[col].unique().tolist())
        if not unique_vals.issubset({0, 1}):
            coerced.append(col)
            label_df[col] = label_df[col].clip(0, 1)
    if coerced:
        print(f"WARNING: Clamped non-binary label values to [0,1] for columns: {coerced}")

    y = label_df.astype(int).to_numpy()

    print(f"Loaded {len(texts)} samples with {len(label_cols)} labels from {path}")
    return texts, y, label_cols


class HeadTailTokenizer:
    """Tokenizer with Head + Tail truncation strategy.

    Clinical notes often have procedures at the top but complications and
    disposition at the bottom. Standard truncation loses the end, missing
    critical information. This tokenizer keeps:
    - First `head_tokens` tokens (procedures, indication)
    - Last `tail_tokens` tokens (complications, plan)
    """

    def __init__(
        self,
        tokenizer,
        max_length: int = 512,
        head_tokens: int = 382,
        tail_tokens: int = 128,
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.head_tokens = head_tokens
        self.tail_tokens = tail_tokens

    def __call__(self, text: str) -> dict[str, torch.Tensor]:
        """Tokenize with Head + Tail truncation.

        Args:
            text: Input clinical note text

        Returns:
            Dict with input_ids, attention_mask, token_type_ids
        """
        # First tokenize without truncation to get full length
        tokens = self.tokenizer(
            text,
            add_special_tokens=False,
            truncation=False,
            return_tensors="pt",
        )
        input_ids = tokens["input_ids"][0]

        # Apply Head + Tail if text is too long
        content_max = self.max_length - 2  # Reserve for [CLS] and [SEP]

        if len(input_ids) > content_max:
            # Take head_tokens from start and tail_tokens from end
            head_ids = input_ids[: self.head_tokens]
            tail_ids = input_ids[-self.tail_tokens :]
            input_ids = torch.cat([head_ids, tail_ids])

        # Add special tokens and pad
        cls_id = self.tokenizer.cls_token_id
        sep_id = self.tokenizer.sep_token_id
        pad_id = self.tokenizer.pad_token_id

        # Ensure input_ids is long type for consistency
        input_ids = input_ids.long()

        # Build final sequence: [CLS] + tokens + [SEP] + padding
        # Explicitly use dtype=torch.long to prevent type mismatches
        full_ids = torch.cat([
            torch.tensor([cls_id], dtype=torch.long),
            input_ids,
            torch.tensor([sep_id], dtype=torch.long),
        ])

        # Pad to max_length
        pad_length = self.max_length - len(full_ids)
        if pad_length > 0:
            full_ids = torch.cat([full_ids, torch.full((pad_length,), pad_id, dtype=torch.long)])

        # Create attention mask (1 for real tokens, 0 for padding)
        attention_mask = (full_ids != pad_id).long()

        return {
            "input_ids": full_ids.long(),  # Ensure final output is int64
            "attention_mask": attention_mask.long(),
        }


class RegistryDataset(Dataset):
    """PyTorch Dataset for multi-label registry classification."""

    def __init__(
        self,
        texts: list[str],
        labels: np.ndarray,
        tokenizer: HeadTailTokenizer,
    ):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer(text)

        return {
            # Force input_ids to Long (int64) to prevent type mismatch in collation
            "input_ids": encoding["input_ids"].long(),
            # Force attention_mask to Long
            "attention_mask": encoding["attention_mask"].long(),
            # Keep labels as Float for BCEWithLogitsLoss
            "labels": torch.tensor(label, dtype=torch.float32),
        }


# ============================================================================
# Model Definition
# ============================================================================

class BiomedBERTMultiLabel(nn.Module):
    """BiomedBERT with multi-label classification head.

    Uses BCEWithLogitsLoss with pos_weight for class imbalance handling.
    """

    def __init__(
        self,
        model_name: str,
        num_labels: int,
        pos_weight: torch.Tensor | None = None,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.config = AutoConfig.from_pretrained(model_name)
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.config.hidden_size, num_labels)

        # Register pos_weight as buffer (not a parameter)
        if pos_weight is not None:
            self.register_buffer("pos_weight", pos_weight)
        else:
            self.pos_weight = None

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        """Forward pass.

        Args:
            input_ids: Token IDs [batch, seq_len]
            attention_mask: Attention mask [batch, seq_len]
            labels: Multi-hot labels [batch, num_labels] (optional)

        Returns:
            Dict with 'logits' and optionally 'loss'
        """
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)

        # Use [CLS] token representation
        pooled = outputs.last_hidden_state[:, 0, :]
        pooled = self.dropout(pooled)
        logits = self.classifier(pooled)

        result = {"logits": logits}

        if labels is not None:
            loss_fn = nn.BCEWithLogitsLoss(pos_weight=self.pos_weight)
            result["loss"] = loss_fn(logits, labels)

        return result

    def save_pretrained(self, path: Path):
        """Save model and config to directory."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save BERT weights
        self.bert.save_pretrained(path)

        # Save classifier weights separately
        torch.save(self.classifier.state_dict(), path / "classifier.pt")

        # Save pos_weight if present
        if self.pos_weight is not None:
            torch.save(self.pos_weight, path / "pos_weight.pt")

    @classmethod
    def from_pretrained(cls, path: Path, num_labels: int) -> "BiomedBERTMultiLabel":
        """Load model from directory."""
        path = Path(path)

        # Load pos_weight if present
        pos_weight_path = path / "pos_weight.pt"
        pos_weight = torch.load(pos_weight_path) if pos_weight_path.exists() else None

        # Create model
        model = cls(
            model_name=str(path),
            num_labels=num_labels,
            pos_weight=pos_weight,
        )

        # Load classifier weights
        classifier_path = path / "classifier.pt"
        if classifier_path.exists():
            model.classifier.load_state_dict(torch.load(classifier_path))

        return model


# ============================================================================
# Training Utilities
# ============================================================================

def calculate_pos_weight(
    labels: np.ndarray,
    cap: float = 100.0,
) -> torch.Tensor:
    """Calculate pos_weight for BCEWithLogitsLoss from training labels.

    Formula: pos_weight[i] = num_negative / num_positive for each label

    This upweights rare positive classes to address class imbalance.

    Args:
        labels: Label matrix of shape (n_samples, n_labels)
        cap: Maximum weight to prevent instability (default: 100x)

    Returns:
        Tensor of shape (num_labels,) with pos_weight values
    """
    n_samples = labels.shape[0]
    weights = []

    for i in range(labels.shape[1]):
        pos = labels[:, i].sum()
        neg = n_samples - pos

        if pos == 0:
            weight = cap  # All negative, use max weight
        else:
            weight = neg / pos

        weights.append(min(weight, cap))

    return torch.tensor(weights, dtype=torch.float32)


def find_optimal_thresholds(
    labels: np.ndarray,
    probs: np.ndarray,
    label_names: list[str],
    threshold_range: tuple[float, float, float] = (0.1, 0.9, 0.05),
) -> dict[str, float]:
    """Find F1-maximizing threshold for each label.

    Args:
        labels: Ground truth labels [n_samples, n_labels]
        probs: Predicted probabilities [n_samples, n_labels]
        label_names: List of label names
        threshold_range: (start, stop, step) for threshold search

    Returns:
        Dict mapping label names to optimal thresholds
    """
    thresholds = {}
    start, stop, step = threshold_range

    for i, label in enumerate(label_names):
        best_f1, best_thresh = 0.0, 0.5

        # Skip if no positive examples
        if labels[:, i].sum() == 0:
            thresholds[label] = 0.5
            continue

        for thresh in np.arange(start, stop, step):
            preds = (probs[:, i] >= thresh).astype(int)
            try:
                f1 = f1_score(labels[:, i], preds, zero_division=0)
                if f1 > best_f1:
                    best_f1, best_thresh = f1, float(thresh)
            except Exception:
                continue

        thresholds[label] = best_thresh
        # Optional: Print verbose threshold info
        # print(f"  {label}: threshold={best_thresh:.2f}, F1={best_f1:.3f}")

    return thresholds


def compute_metrics(
    labels: np.ndarray,
    probs: np.ndarray,
    thresholds: dict[str, float],
    label_names: list[str],
) -> dict[str, Any]:
    """Compute comprehensive metrics using per-class thresholds.

    Args:
        labels: Ground truth labels [n_samples, n_labels]
        probs: Predicted probabilities [n_samples, n_labels]
        thresholds: Per-label threshold dict
        label_names: List of label names

    Returns:
        Dict with macro_f1, micro_f1, per_label metrics
    """
    # Apply per-class thresholds
    preds = np.zeros_like(probs)
    for i, label in enumerate(label_names):
        thresh = thresholds.get(label, 0.5)
        preds[:, i] = (probs[:, i] >= thresh).astype(int)

    # Overall metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average=None, zero_division=0
    )

    macro_f1 = np.mean(f1)
    micro_f1 = f1_score(labels.ravel(), preds.ravel(), zero_division=0)

    # Per-label metrics
    per_label = {}
    for i, label in enumerate(label_names):
        per_label[label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "threshold": thresholds.get(label, 0.5),
            "support": int(labels[:, i].sum()),
        }

    # Identify rare classes (support < 50)
    rare_labels = [l for l in label_names if per_label[l]["support"] < 50]
    rare_f1 = np.mean([per_label[l]["f1"] for l in rare_labels]) if rare_labels else 0.0

    return {
        "macro_f1": float(macro_f1),
        "micro_f1": float(micro_f1),
        "rare_class_f1": float(rare_f1),
        "per_label": per_label,
    }


# ============================================================================
# Training Loop
# ============================================================================

def train_epoch(
    model: BiomedBERTMultiLabel,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    config: TrainingConfig,
    epoch: int,
) -> float:
    """Train for one epoch.

    Returns:
        Average training loss for the epoch
    """
    model.train()
    total_loss = 0.0
    num_batches = 0

    # Mixed precision scaler (use new API to avoid deprecation warnings)
    scaler = torch.amp.GradScaler("cuda", enabled=config.fp16)

    progress_bar = tqdm(dataloader, desc=f"Epoch {epoch + 1}")

    for step, batch in enumerate(progress_bar):
        input_ids = batch["input_ids"].to(config.device)
        attention_mask = batch["attention_mask"].to(config.device)
        labels = batch["labels"].to(config.device)

        # Forward pass with mixed precision
        with torch.amp.autocast("cuda", enabled=config.fp16):
            outputs = model(input_ids, attention_mask, labels)
            loss = outputs["loss"] / config.gradient_accumulation_steps

        # Backward pass
        scaler.scale(loss).backward()

        if (step + 1) % config.gradient_accumulation_steps == 0:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.max_grad_norm)
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            optimizer.zero_grad()

        total_loss += loss.item() * config.gradient_accumulation_steps
        num_batches += 1

        # Update progress bar
        if step % config.logging_steps == 0:
            avg_loss = total_loss / num_batches
            progress_bar.set_postfix({"loss": f"{avg_loss:.4f}"})

    return total_loss / num_batches


def evaluate(
    model: BiomedBERTMultiLabel,
    dataloader: DataLoader,
    config: TrainingConfig,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Evaluate model and return predictions.

    Returns:
        Tuple of (all_labels, all_probs, avg_loss)
    """
    model.eval()
    all_probs = []
    all_labels = []
    total_loss = 0.0
    num_batches = 0

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch["input_ids"].to(config.device)
            attention_mask = batch["attention_mask"].to(config.device)
            labels = batch["labels"].to(config.device)

            outputs = model(input_ids, attention_mask, labels)

            probs = torch.sigmoid(outputs["logits"]).cpu().numpy()
            all_probs.append(probs)
            all_labels
