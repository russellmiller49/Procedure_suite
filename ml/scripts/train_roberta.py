#!/usr/bin/env python3
"""Train BiomedBERT for multi-label registry procedure classification.

This script trains a transformer-based model for predicting registry procedure
flags from clinical procedure notes. Key features:

- Head + Tail truncation to preserve both procedure and complication sections
- pos_weight calculation for severe class imbalance
- Per-class threshold optimization on validation set
- Mixed precision training (fp16) for RTX 4070 Ti

Usage:
    python ml/scripts/train_roberta.py
    python ml/scripts/train_roberta.py --batch-size 32 --epochs 10
    python ml/scripts/train_roberta.py --evaluate-only --model-dir data/models/roberta_registry
"""

from __future__ import annotations

import argparse
import json
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

from ml.lib.ml_coder.distillation_io import (
    align_teacher_logits,
    load_teacher_logits_npz,
    validate_label_fields_match,
)
from ml.lib.ml_coder.registry_label_schema import DORMANT_LABELS, REGISTRY_LABELS, compute_encounter_id
from ml.lib.ml_coder.training_losses import AsymmetricLoss

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class TrainingConfig:
    """Configuration for BiomedBERT training."""

    # Model
    model_name: str = "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext"

    # Data paths (from ml/lib/ml_coder/data_prep.py)
    train_csv: Path = field(default_factory=lambda: Path("data/ml_training/registry_train.csv"))
    val_csv: Path = field(default_factory=lambda: Path("data/ml_training/registry_val.csv"))
    test_csv: Path = field(default_factory=lambda: Path("data/ml_training/registry_test.csv"))
    label_fields_json: Path = field(
        default_factory=lambda: Path("data/ml_training/registry_label_fields.json")
    )
    output_dir: Path = field(default_factory=lambda: Path("data/models/roberta_registry"))

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

    # Loss
    loss: str = "bce"  # "bce" | "asl"
    asl_gamma_neg: float = 4.0
    asl_gamma_pos: float = 1.0
    asl_clip: float = 0.05

    # Dormant labels (exclude from ML head)
    dormant_mode: str = "auto"  # "auto" | "schema" | "none"
    dormant_min_positives: int = 20

    # Distillation
    teacher_logits: Path | None = None
    distill_alpha: float = 0.5
    distill_temp: float = 2.0
    distill_loss: str = "mse"  # "mse" | "kl"

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

def load_registry_csv(
    path: Path,
    required_labels: list[str] | None = None,
) -> tuple[list[str], np.ndarray, list[str], np.ndarray, list[str]]:
    """Load registry training/test CSV file.

    Args:
        path: Path to CSV file with note_text and label columns
        required_labels: Optional list of label columns to enforce order/presence.
                        If provided, returns y with columns in this specific order.

    Returns:
        Tuple of (texts, labels_matrix, label_names, sample_weights, encounter_ids)
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

    # Stable IDs for distillation alignment (prefer encounter_id if present).
    if "encounter_id" in df.columns:
        encounter_ids = df["encounter_id"].fillna("").astype(str).str.strip().tolist()
    else:
        encounter_ids = ["" for _ in texts]
    for i, eid in enumerate(encounter_ids):
        if not eid:
            encounter_ids[i] = compute_encounter_id(texts[i])

    # Optional per-row confidence weighting (defaults to 1.0).
    if "label_confidence" in df.columns:
        weights = (
            pd.to_numeric(df["label_confidence"], errors="coerce")
            .fillna(1.0)
            .clip(0.0, 1.0)
            .astype(float)
            .to_numpy()
        )
    else:
        weights = np.ones(len(df), dtype=float)

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
    return texts, y, label_cols, weights.astype(np.float32), encounter_ids


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
        sample_weights: np.ndarray,
        tokenizer: HeadTailTokenizer,
        teacher_logits: np.ndarray | None = None,
        teacher_mask: np.ndarray | None = None,
    ):
        self.texts = texts
        self.labels = labels
        self.sample_weights = sample_weights
        self.tokenizer = tokenizer
        self.teacher_logits = teacher_logits
        self.teacher_mask = teacher_mask

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        text = self.texts[idx]
        label = self.labels[idx]
        weight = float(self.sample_weights[idx]) if idx < len(self.sample_weights) else 1.0

        encoding = self.tokenizer(text)

        item: dict[str, torch.Tensor] = {
            # Force input_ids to Long (int64) to prevent type mismatch in collation
            "input_ids": encoding["input_ids"].long(),
            # Force attention_mask to Long
            "attention_mask": encoding["attention_mask"].long(),
            # Keep labels as Float for BCEWithLogitsLoss
            "labels": torch.tensor(label, dtype=torch.float32),
            "sample_weight": torch.tensor(weight, dtype=torch.float32),
        }

        if self.teacher_logits is not None and self.teacher_mask is not None:
            item["teacher_logits"] = torch.tensor(self.teacher_logits[idx], dtype=torch.float32)
            item["teacher_mask"] = torch.tensor(float(self.teacher_mask[idx]), dtype=torch.float32)

        return item


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
        sample_weights: torch.Tensor | None = None,
        loss_fn: nn.Module | None = None,
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
            if loss_fn is None:
                loss_fn = nn.BCEWithLogitsLoss(pos_weight=self.pos_weight, reduction="none")
            loss_matrix = loss_fn(logits, labels)  # [batch, num_labels]
            per_sample = loss_matrix.mean(dim=1)  # mean over labels
            if sample_weights is not None:
                per_sample = per_sample * sample_weights
            result["loss"] = per_sample.mean()

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
    def from_pretrained(cls, path: Path, num_labels: int) -> BiomedBERTMultiLabel:
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
    rare_labels = [
        label_id for label_id in label_names if per_label[label_id]["support"] < 50
    ]
    rare_f1 = (
        np.mean([per_label[label_id]["f1"] for label_id in rare_labels])
        if rare_labels
        else 0.0
    )

    return {
        "macro_f1": float(macro_f1),
        "micro_f1": float(micro_f1),
        "rare_class_f1": float(rare_f1),
        "per_label": per_label,
    }


# ============================================================================
# Training Loop
# ============================================================================

def compute_distillation_loss(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    teacher_mask: torch.Tensor,
    *,
    temp: float,
    loss_type: str,
    sample_weights: torch.Tensor | None,
    eps: float = 1e-8,
) -> torch.Tensor:
    """Compute per-batch distillation loss with optional masking/row weighting."""
    t = float(temp)
    if t <= 0:
        raise ValueError("distill_temp must be > 0")

    s_scaled = student_logits / t
    t_scaled = teacher_logits / t

    if loss_type == "mse":
        per_label = (s_scaled - t_scaled) ** 2
    elif loss_type == "kl":
        p_s = torch.sigmoid(s_scaled).clamp(min=eps, max=1.0 - eps)
        p_t = torch.sigmoid(t_scaled).clamp(min=eps, max=1.0 - eps)
        per_label = p_t * torch.log(p_t / p_s) + (1.0 - p_t) * torch.log((1.0 - p_t) / (1.0 - p_s))
    else:
        raise ValueError(f"Unknown distill_loss: {loss_type}")

    per_sample = per_label.mean(dim=1) * teacher_mask
    if sample_weights is not None:
        per_sample = per_sample * sample_weights
    return per_sample.mean()


def train_epoch(
    model: BiomedBERTMultiLabel,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    config: TrainingConfig,
    epoch: int,
    *,
    loss_fn: nn.Module,
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
        sample_weights = batch.get("sample_weight")
        if sample_weights is not None:
            sample_weights = sample_weights.to(config.device)
        teacher_logits = batch.get("teacher_logits")
        teacher_mask = batch.get("teacher_mask")
        if teacher_logits is not None:
            teacher_logits = teacher_logits.to(config.device)
        if teacher_mask is not None:
            teacher_mask = teacher_mask.to(config.device)

        # Forward pass with mixed precision
        with torch.amp.autocast("cuda", enabled=config.fp16):
            outputs = model(
                input_ids,
                attention_mask,
                labels,
                sample_weights=sample_weights,
                loss_fn=loss_fn,
            )
            loss = outputs["loss"]
            if teacher_logits is not None and float(config.distill_alpha) > 0.0:
                mask = (
                    teacher_mask
                    if teacher_mask is not None
                    else torch.ones((labels.shape[0],), dtype=torch.float32, device=config.device)
                )
                distill = compute_distillation_loss(
                    outputs["logits"],
                    teacher_logits,
                    mask,
                    temp=float(config.distill_temp),
                    loss_type=str(config.distill_loss),
                    sample_weights=sample_weights,
                )
                alpha = float(config.distill_alpha)
                t = float(config.distill_temp)
                loss = (1.0 - alpha) * loss + alpha * (t * t) * distill

            loss = loss / config.gradient_accumulation_steps

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
    *,
    loss_fn: nn.Module,
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
            sample_weights = batch.get("sample_weight")
            if sample_weights is not None:
                sample_weights = sample_weights.to(config.device)

            outputs = model(
                input_ids,
                attention_mask,
                labels,
                sample_weights=sample_weights,
                loss_fn=loss_fn,
            )

            probs = torch.sigmoid(outputs["logits"]).cpu().numpy()
            all_probs.append(probs)
            all_labels.append(batch["labels"].numpy())

            total_loss += outputs["loss"].item()
            num_batches += 1

    all_probs = np.vstack(all_probs)
    all_labels = np.vstack(all_labels)
    avg_loss = total_loss / num_batches

    return all_labels, all_probs, avg_loss


def train(config: TrainingConfig) -> dict[str, Any]:
    """Main training function.

    Args:
        config: Training configuration

    Returns:
        Dict with final metrics and paths to saved artifacts
    """
    print(f"\n{'=' * 60}")
    print("BiomedBERT Registry Classifier Training")
    print(f"{'=' * 60}")
    print(f"Model: {config.model_name}")
    print(f"Device: {config.device}")
    print(f"FP16: {config.fp16}")
    print(f"Batch size: {config.batch_size}")
    print(f"Learning rate: {config.learning_rate}")
    print(f"Epochs: {config.num_epochs}")
    print(f"{'=' * 60}\n")

    # --- 1. Load Training Data (canonical label schema) ---
    print("\nLoading training data...")
    schema_labels = list(REGISTRY_LABELS)
    train_texts, train_labels_full, _, train_weights, train_ids = load_registry_csv(
        config.train_csv,
        required_labels=schema_labels,
    )
    print(f"Using canonical label order ({len(schema_labels)} labels): {schema_labels[:5]}...")

    # --- 2. Update Label Definition JSON ---
    # This keeps downstream scripts (quantization, inference) in sync
    print(f"Updating label definition file: {config.label_fields_json}")
    config.label_fields_json.parent.mkdir(parents=True, exist_ok=True)
    with open(config.label_fields_json, "w") as f:
        json.dump(schema_labels, f, indent=2)
    # Also emit into the model output dir for deployable bundles.
    labels_json = json.dumps(schema_labels, indent=2) + "\n"
    (config.output_dir / "registry_label_fields.json").write_text(labels_json)
    (config.output_dir / "label_order.json").write_text(labels_json)

    # --- 3. Load Test Data (Enforcing Training Schema) ---
    print("\nLoading test data...")
    test_texts, test_labels_full, _, test_weights, test_ids = load_registry_csv(
        config.test_csv,
        required_labels=schema_labels,
    )
    print(f"Test samples: {len(test_texts)}")

    # --- Load Validation Data ---
    if config.val_csv and config.val_csv.exists():
        print(f"\nLoading validation data from {config.val_csv}...")
        val_texts, val_labels_full, _, val_weights, val_ids = load_registry_csv(
            config.val_csv,
            required_labels=schema_labels,
        )
        print(f"Using explicit validation set: {len(val_texts)} samples")
    else:
        print(
            f"\nNo validation file found at {config.val_csv}. "
            f"Performing random split ({config.val_split})..."
        )
        (
            train_texts,
            val_texts,
            train_labels_full,
            val_labels_full,
            train_weights,
            val_weights,
            train_ids,
            val_ids,
        ) = train_test_split(
            train_texts,
            train_labels_full,
            train_weights,
            train_ids,
            test_size=config.val_split,
            random_state=42,
            stratify=None,  # Multi-label doesn't support stratify directly
        )
    print(f"Training samples: {len(train_texts)}")
    print(f"Validation samples: {len(val_texts)}")

    # --- 4. Select active (non-dormant) labels for the ML head ---
    dormant: set[str]
    if config.dormant_mode == "schema":
        dormant = set(DORMANT_LABELS)
    elif config.dormant_mode == "auto":
        dormant = set(DORMANT_LABELS)
        min_pos = max(0, int(config.dormant_min_positives))
        counts = train_labels_full.sum(axis=0).astype(int)
        for label, count in zip(schema_labels, counts.tolist()):
            if count < min_pos:
                dormant.add(label)
    elif config.dormant_mode == "none":
        dormant = set()
    else:
        raise ValueError(f"Unknown dormant_mode: {config.dormant_mode}")

    label_names = [l for l in schema_labels if l not in dormant]
    if not label_names:
        raise ValueError("No active labels selected; adjust dormant settings.")

    active_idx = [schema_labels.index(l) for l in label_names]
    train_labels = train_labels_full[:, active_idx]
    val_labels = val_labels_full[:, active_idx]
    test_labels = test_labels_full[:, active_idx]
    num_labels = len(label_names)

    print(f"\nDormant mode: {config.dormant_mode}")
    if dormant:
        dormant_sorted = [l for l in schema_labels if l in dormant]
        print(f"Dormant labels (excluded from ML head): {len(dormant_sorted)}")
        print(f"  e.g. {dormant_sorted[:10]}")
    print(f"Active labels (ML head): {num_labels}")
    print(f"  e.g. {label_names[:10]}")

    # Calculate pos_weight for class imbalance
    print("\nCalculating pos_weight for class imbalance...")
    pos_weight = calculate_pos_weight(train_labels, cap=config.pos_weight_cap)
    print(f"pos_weight range: [{pos_weight.min():.2f}, {pos_weight.max():.2f}]")

    # Show most imbalanced classes
    weight_idx = pos_weight.argsort(descending=True)[:5]
    print("Most imbalanced classes:")
    for idx in weight_idx:
        print(f"  {label_names[idx]}: weight={pos_weight[idx]:.1f}x")

    # Initialize tokenizer with Head + Tail strategy
    print("\nInitializing tokenizer with Head + Tail truncation...")
    base_tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    tokenizer = HeadTailTokenizer(
        base_tokenizer,
        max_length=config.max_length,
        head_tokens=config.head_tokens,
        tail_tokens=config.tail_tokens,
    )

    # Optional: distillation alignment (teacher logits for a subset of train IDs).
    train_teacher_logits = None
    train_teacher_mask = None
    if config.teacher_logits is not None:
        teacher = load_teacher_logits_npz(config.teacher_logits)
        validate_label_fields_match(teacher.label_fields, label_names)
        train_teacher_logits, train_teacher_mask = align_teacher_logits(train_ids, teacher, dtype=np.float32)
        covered = float(train_teacher_mask.mean()) if train_teacher_mask.size else 0.0
        print(
            f"\nLoaded teacher logits from {config.teacher_logits} "
            f"(coverage={covered:.3f}, alpha={config.distill_alpha}, temp={config.distill_temp}, loss={config.distill_loss})"
        )

    # Create datasets
    print("\nCreating datasets...")
    train_dataset = RegistryDataset(
        train_texts,
        train_labels,
        train_weights,
        tokenizer,
        teacher_logits=train_teacher_logits,
        teacher_mask=train_teacher_mask,
    )
    val_dataset = RegistryDataset(val_texts, val_labels, val_weights, tokenizer)
    test_dataset = RegistryDataset(test_texts, test_labels, test_weights, tokenizer)

    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size * 2,
        shuffle=False,
        num_workers=4,
        pin_memory=True,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size * 2,
        shuffle=False,
        num_workers=4,
        pin_memory=True,
    )

    # Initialize model
    print("\nInitializing model...")
    model = BiomedBERTMultiLabel(
        model_name=config.model_name,
        num_labels=num_labels,
        pos_weight=pos_weight.to(config.device),
    )
    model.to(config.device)

    # Loss function selection (element-wise reduction="none" to preserve per-row weighting).
    pos_weight_device = pos_weight.to(config.device)
    if config.loss == "bce":
        loss_fn: nn.Module = nn.BCEWithLogitsLoss(pos_weight=pos_weight_device, reduction="none").to(config.device)
    elif config.loss == "asl":
        loss_fn = AsymmetricLoss(
            gamma_neg=config.asl_gamma_neg,
            gamma_pos=config.asl_gamma_pos,
            clip=config.asl_clip,
            pos_weight=pos_weight_device,
        ).to(config.device)
    else:
        raise ValueError(f"Unknown loss: {config.loss}")

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")

    # Initialize optimizer and scheduler
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )

    total_steps = len(train_loader) * config.num_epochs
    warmup_steps = int(total_steps * config.warmup_ratio)

    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps,
    )

    # Training loop
    print(f"\nStarting training for {config.num_epochs} epochs...")
    print(f"Total steps: {total_steps}, Warmup steps: {warmup_steps}")

    best_val_f1 = -1.0
    best_epoch = 0

    for epoch in range(config.num_epochs):
        print(f"\n{'=' * 40}")
        print(f"Epoch {epoch + 1}/{config.num_epochs}")
        print(f"{'=' * 40}")

        # Train
        train_loss = train_epoch(model, train_loader, optimizer, scheduler, config, epoch, loss_fn=loss_fn)
        print(f"Training loss: {train_loss:.4f}")

        # Evaluate on validation set
        print("\nEvaluating on validation set...")
        val_labels_arr, val_probs, val_loss = evaluate(model, val_loader, config, loss_fn=loss_fn)

        # Find optimal thresholds on validation set
        print("\nOptimizing per-class thresholds...")
        thresholds = find_optimal_thresholds(val_labels_arr, val_probs, label_names)

        # Compute metrics with optimized thresholds
        val_metrics = compute_metrics(val_labels_arr, val_probs, thresholds, label_names)

        print("\nValidation Results:")
        print(f"  Loss: {val_loss:.4f}")
        print(f"  Macro F1: {val_metrics['macro_f1']:.4f}")
        print(f"  Micro F1: {val_metrics['micro_f1']:.4f}")
        print(f"  Rare Class F1: {val_metrics['rare_class_f1']:.4f}")

        # Save best model
        if val_metrics["macro_f1"] > best_val_f1:
            best_val_f1 = val_metrics["macro_f1"]
            best_epoch = epoch + 1
            print("\n  New best model! Saving checkpoint...")

            # Save model
            model.save_pretrained(config.output_dir)

            # Save tokenizer
            base_tokenizer.save_pretrained(config.output_dir / "tokenizer")

            # Save thresholds
            thresholds_path = config.output_dir.parent / "roberta_registry_thresholds.json"
            with open(thresholds_path, "w") as f:
                json.dump(thresholds, f, indent=2)

            # Also save a bundle-friendly thresholds.json in the model dir that includes val F1.
            thresholds_with_f1 = {
                label: {
                    "threshold": float(thresholds.get(label, 0.5)),
                    "val_f1": float(val_metrics["per_label"][label]["f1"]),
                }
                for label in label_names
            }
            (config.output_dir / "thresholds.json").write_text(
                json.dumps(thresholds_with_f1, indent=2, sort_keys=False) + "\n"
            )
            (config.output_dir / "label_fields.json").write_text(
                json.dumps(label_names, indent=2, sort_keys=False) + "\n"
            )
            (config.output_dir / "dormant_labels.json").write_text(
                json.dumps([l for l in schema_labels if l in dormant], indent=2, sort_keys=False) + "\n"
            )

    print(f"\n{'=' * 60}")
    print(f"Training complete! Best epoch: {best_epoch}, Best Macro F1: {best_val_f1:.4f}")
    print(f"{'=' * 60}")

    # Final evaluation on test set
    print("\nFinal evaluation on test set...")

    # Load best model
    model = BiomedBERTMultiLabel.from_pretrained(config.output_dir, num_labels)
    model.to(config.device)

    # Load best thresholds
    thresholds_path = config.output_dir.parent / "roberta_registry_thresholds.json"
    with open(thresholds_path) as f:
        thresholds = json.load(f)

    # Evaluate
    test_labels_arr, test_probs, test_loss = evaluate(model, test_loader, config, loss_fn=loss_fn)
    test_metrics = compute_metrics(test_labels_arr, test_probs, thresholds, label_names)

    print("\nTest Set Results:")
    print(f"  Loss: {test_loss:.4f}")
    print(f"  Macro F1: {test_metrics['macro_f1']:.4f}")
    print(f"  Micro F1: {test_metrics['micro_f1']:.4f}")
    print(f"  Rare Class F1: {test_metrics['rare_class_f1']:.4f}")

    # Print per-label metrics
    print("\nPer-label metrics:")
    for label in label_names:
        m = test_metrics["per_label"][label]
        print(
            f"  {label}: P={m['precision']:.3f} R={m['recall']:.3f} "
            f"F1={m['f1']:.3f} (n={m['support']})"
        )

    # Save final metrics (legacy location + model-dir copy for bundles)
    metrics_path = config.output_dir.parent / "roberta_registry_metrics.json"
    final_metrics = {
        "best_epoch": best_epoch,
        "best_val_macro_f1": best_val_f1,
        "test_metrics": test_metrics,
        "config": {
            "model_name": config.model_name,
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "num_epochs": config.num_epochs,
            "max_length": config.max_length,
            "head_tokens": config.head_tokens,
            "tail_tokens": config.tail_tokens,
            "loss": config.loss,
            "asl_gamma_neg": float(config.asl_gamma_neg),
            "asl_gamma_pos": float(config.asl_gamma_pos),
            "asl_clip": float(config.asl_clip),
            "dormant_mode": config.dormant_mode,
            "dormant_min_positives": int(config.dormant_min_positives),
            "schema_labels": schema_labels,
            "active_labels": label_names,
            "dormant_labels": [l for l in schema_labels if l in dormant],
            "teacher_logits": str(config.teacher_logits) if config.teacher_logits is not None else None,
            "distill_alpha": float(config.distill_alpha),
            "distill_temp": float(config.distill_temp),
            "distill_loss": str(config.distill_loss),
        },
    }
    with open(metrics_path, "w") as f:
        json.dump(final_metrics, f, indent=2)
    (config.output_dir / "metrics.json").write_text(json.dumps(final_metrics, indent=2) + "\n")

    print("\nArtifacts saved:")
    print(f"  Model: {config.output_dir}")
    print(f"  Thresholds: {thresholds_path}")
    print(f"  Metrics: {metrics_path}")

    # Check if targets met
    print(f"\n{'=' * 60}")
    print("TARGET EVALUATION:")
    print(f"{'=' * 60}")
    targets_met = True

    if test_metrics["macro_f1"] >= 0.90:
        print(f"  [PASS] Macro F1: {test_metrics['macro_f1']:.4f} >= 0.90")
    else:
        print(f"  [FAIL] Macro F1: {test_metrics['macro_f1']:.4f} < 0.90")
        targets_met = False

    if test_metrics["micro_f1"] >= 0.92:
        print(f"  [PASS] Micro F1: {test_metrics['micro_f1']:.4f} >= 0.92")
    else:
        print(f"  [FAIL] Micro F1: {test_metrics['micro_f1']:.4f} < 0.92")
        targets_met = False

    if test_metrics["rare_class_f1"] >= 0.85:
        print(f"  [PASS] Rare Class F1: {test_metrics['rare_class_f1']:.4f} >= 0.85")
    else:
        print(f"  [FAIL] Rare Class F1: {test_metrics['rare_class_f1']:.4f} < 0.85")
        targets_met = False

    if targets_met:
        print("\n  SUCCESS! All targets met. Proceed to Phase 3 (Rules Engine).")
    else:
        print("\n  TARGETS NOT MET. Consider Phase 2 (Teacher-Student Distillation).")

    return final_metrics


def _load_thresholds_for_labels(path: Path, labels: list[str]) -> dict[str, float]:
    if not path.exists():
        return {l: 0.5 for l in labels}
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        return {l: 0.5 for l in labels}
    thresholds: dict[str, float] = {}
    for l in labels:
        v = data.get(l, 0.5)
        if isinstance(v, dict) and "threshold" in v:
            thresholds[l] = float(v["threshold"])
        else:
            thresholds[l] = float(v)
    return thresholds


def evaluate_only(model_dir: Path, config: TrainingConfig) -> dict[str, Any]:
    label_fields_path = model_dir / "label_fields.json"
    if not label_fields_path.exists():
        raise SystemExit(f"Missing label_fields.json in model dir: {model_dir}")

    label_names = json.loads(label_fields_path.read_text())
    if not isinstance(label_names, list) or not all(isinstance(x, str) for x in label_names):
        raise SystemExit(f"Invalid label_fields.json in model dir: {model_dir}")

    thresholds = _load_thresholds_for_labels(model_dir / "thresholds.json", label_names)

    # Load test data aligned to the model head.
    test_texts, test_labels, _, test_weights, _ = load_registry_csv(config.test_csv, required_labels=label_names)

    base_tokenizer = AutoTokenizer.from_pretrained(str((model_dir / "tokenizer") if (model_dir / "tokenizer").exists() else config.model_name))
    tokenizer = HeadTailTokenizer(
        base_tokenizer,
        max_length=config.max_length,
        head_tokens=config.head_tokens,
        tail_tokens=config.tail_tokens,
    )
    test_dataset = RegistryDataset(test_texts, test_labels, test_weights, tokenizer)
    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size * 2,
        shuffle=False,
        num_workers=0,
    )

    model = BiomedBERTMultiLabel.from_pretrained(model_dir, num_labels=len(label_names))
    model.to(config.device)

    pos_weight = getattr(model, "pos_weight", None)
    if isinstance(pos_weight, torch.Tensor):
        pos_weight = pos_weight.to(config.device)
    loss_fn: nn.Module = nn.BCEWithLogitsLoss(pos_weight=pos_weight, reduction="none").to(config.device)

    test_labels_arr, test_probs, test_loss = evaluate(model, test_loader, config, loss_fn=loss_fn)
    test_metrics = compute_metrics(test_labels_arr, test_probs, thresholds, label_names)

    print("\nTest Set Results:")
    print(f"  Loss: {test_loss:.4f}")
    print(f"  Macro F1: {test_metrics['macro_f1']:.4f}")
    print(f"  Micro F1: {test_metrics['micro_f1']:.4f}")
    print(f"  Rare Class F1: {test_metrics['rare_class_f1']:.4f}")
    return {"test_metrics": test_metrics, "thresholds": thresholds, "labels": label_names}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train BiomedBERT for registry procedure classification")

    # Data paths (from ml/lib/ml_coder/data_prep.py)
    parser.add_argument(
        "--train-csv",
        type=Path,
        default=Path("data/ml_training/registry_train.csv"),
        help="Path to training CSV",
    )
    parser.add_argument(
        "--val-csv",
        type=Path,
        default=Path("data/ml_training/registry_val.csv"),
        help="Path to validation CSV (optional, overrides automatic split)",
    )
    parser.add_argument(
        "--test-csv",
        type=Path,
        default=Path("data/ml_training/registry_test.csv"),
        help="Path to test CSV",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/models/roberta_registry"),
        help="Output directory for model artifacts",
    )

    # Training hyperparameters
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Batch size (default: 16)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
        help="Number of training epochs (default: 5)",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=2e-5,
        help="Learning rate (default: 2e-5)",
    )
    parser.add_argument(
        "--no-fp16",
        action="store_true",
        help="Disable mixed precision training",
    )

    # Model
    parser.add_argument(
        "--model-name",
        type=str,
        default="microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext",
        help="HuggingFace model name",
    )

    parser.add_argument(
        "--loss",
        choices=["bce", "asl"],
        default="bce",
        help="Loss function (default: bce)",
    )
    parser.add_argument("--asl-gamma-neg", type=float, default=4.0)
    parser.add_argument("--asl-gamma-pos", type=float, default=1.0)
    parser.add_argument("--asl-clip", type=float, default=0.05)

    parser.add_argument(
        "--dormant-mode",
        choices=["auto", "schema", "none"],
        default="auto",
        help="Dormant label strategy (exclude ultra-rare labels from ML head)",
    )
    parser.add_argument(
        "--dormant-min-positives",
        type=int,
        default=20,
        help="Minimum positives required to remain active when --dormant-mode=auto",
    )

    parser.add_argument(
        "--teacher-logits",
        type=Path,
        default=None,
        help="NPZ file with teacher logits for distillation (optional)",
    )
    parser.add_argument("--distill-alpha", type=float, default=0.5)
    parser.add_argument("--distill-temp", type=float, default=2.0)
    parser.add_argument("--distill-loss", choices=["mse", "kl"], default="mse")

    # Evaluation only
    parser.add_argument(
        "--evaluate-only",
        action="store_true",
        help="Only evaluate existing model (no training)",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        help="Model directory for evaluation (required with --evaluate-only)",
    )

    return parser


def main():
    """Parse arguments and run training."""
    parser = build_arg_parser()
    args = parser.parse_args()

    # Create config
    config = TrainingConfig(
        model_name=args.model_name,
        train_csv=args.train_csv,
        val_csv=args.val_csv,
        test_csv=args.test_csv,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        learning_rate=args.lr,
        fp16=not args.no_fp16,
        loss=str(args.loss),
        asl_gamma_neg=float(args.asl_gamma_neg),
        asl_gamma_pos=float(args.asl_gamma_pos),
        asl_clip=float(args.asl_clip),
        dormant_mode=str(args.dormant_mode),
        dormant_min_positives=int(args.dormant_min_positives),
        teacher_logits=args.teacher_logits,
        distill_alpha=float(args.distill_alpha),
        distill_temp=float(args.distill_temp),
        distill_loss=str(args.distill_loss),
    )

    # Ensure output directory exists
    config.output_dir.mkdir(parents=True, exist_ok=True)

    # Run training or evaluation
    if args.evaluate_only:
        if not args.model_dir:
            parser.error("--model-dir required with --evaluate-only")
        evaluate_only(args.model_dir, config)
    else:
        train(config)


if __name__ == "__main__":
    main()
