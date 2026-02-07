#!/usr/bin/env python3
"""Export trained BiomedBERT model to ONNX and apply INT8 quantization.

This script converts the trained PyTorch model to ONNX format and applies
dynamic INT8 quantization for efficient CPU inference on Railway.

Results:
- Model size: ~440MB -> ~110MB
- Inference speed: ~3x faster
- Accuracy loss: < 1%

Usage:
    python ml/scripts/quantize_to_onnx.py --model-dir data/models/roberta_registry
    python ml/scripts/quantize_to_onnx.py --model-dir data/models/roberta_registry --validate
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch
import torch.nn as nn
from transformers import AutoConfig, AutoModel, AutoTokenizer

if TYPE_CHECKING:
    import onnxruntime as ort


# ============================================================================
# Model Definition (must match training script)
# ============================================================================

class BiomedBERTMultiLabel(nn.Module):
    """BiomedBERT with multi-label classification head."""

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

        if pos_weight is not None:
            self.register_buffer("pos_weight", pos_weight)
        else:
            self.pos_weight = None

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass returning logits only (no loss for inference)."""
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = outputs.last_hidden_state[:, 0, :]
        pooled = self.dropout(pooled)
        logits = self.classifier(pooled)
        return logits

    @classmethod
    def from_pretrained(cls, path: Path, num_labels: int) -> "BiomedBERTMultiLabel":
        """Load model from directory."""
        path = Path(path)

        # Load pos_weight if present
        pos_weight_path = path / "pos_weight.pt"
        pos_weight = torch.load(pos_weight_path, map_location="cpu") if pos_weight_path.exists() else None

        # Create model
        model = cls(
            model_name=str(path),
            num_labels=num_labels,
            pos_weight=pos_weight,
        )

        # Load classifier weights
        classifier_path = path / "classifier.pt"
        if classifier_path.exists():
            model.classifier.load_state_dict(torch.load(classifier_path, map_location="cpu"))

        return model


# ============================================================================
# ONNX Export
# ============================================================================

def export_to_onnx(
    model: BiomedBERTMultiLabel,
    output_path: Path,
    max_length: int = 512,
    opset_version: int = 14,
) -> None:
    """Export PyTorch model to ONNX format.

    Args:
        model: Trained BiomedBERT model
        output_path: Path for output ONNX file
        max_length: Maximum sequence length
        opset_version: ONNX opset version (14 for good RoBERTa/BERT compatibility)
    """
    model.eval()

    # Create dummy inputs
    batch_size = 1
    dummy_input_ids = torch.randint(0, 30522, (batch_size, max_length))
    dummy_attention_mask = torch.ones(batch_size, max_length, dtype=torch.long)

    # Export
    print(f"Exporting model to ONNX: {output_path}")

    torch.onnx.export(
        model,
        (dummy_input_ids, dummy_attention_mask),
        str(output_path),
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size"},
        },
        opset_version=opset_version,
        do_constant_folding=True,
        export_params=True,
    )

    # Verify export
    import onnx
    onnx_model = onnx.load(str(output_path))
    onnx.checker.check_model(onnx_model)
    print(f"  ONNX model verified successfully")

    # Print model size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Model size: {size_mb:.1f} MB")


# ============================================================================
# INT8 Quantization
# ============================================================================

def quantize_model(
    onnx_path: Path,
    output_path: Path,
) -> None:
    """Apply dynamic INT8 quantization to ONNX model.

    Uses dynamic quantization which quantizes weights to INT8 but keeps
    activations in FP32. This provides good speedup with minimal accuracy loss.

    Args:
        onnx_path: Path to unquantized ONNX model
        output_path: Path for quantized output
    """
    from onnxruntime.quantization import quantize_dynamic, QuantType

    print(f"Quantizing model: {onnx_path} -> {output_path}")

    quantize_dynamic(
        model_input=str(onnx_path),
        model_output=str(output_path),
        weight_type=QuantType.QUInt8,
        optimize_model=True,
    )

    # Print size comparison
    original_size = onnx_path.stat().st_size / (1024 * 1024)
    quantized_size = output_path.stat().st_size / (1024 * 1024)
    reduction = (1 - quantized_size / original_size) * 100

    print(f"  Original size: {original_size:.1f} MB")
    print(f"  Quantized size: {quantized_size:.1f} MB")
    print(f"  Size reduction: {reduction:.1f}%")


# ============================================================================
# Validation
# ============================================================================

def validate_quantized_model(
    original_model: BiomedBERTMultiLabel,
    quantized_onnx_path: Path,
    tokenizer_path: Path,
    test_texts: list[str],
    test_labels: np.ndarray,
    label_names: list[str],
    thresholds: dict[str, float],
    max_length: int = 512,
) -> dict:
    """Compare quantized ONNX model against original PyTorch model.

    Args:
        original_model: Original PyTorch model
        quantized_onnx_path: Path to quantized ONNX model
        tokenizer_path: Path to tokenizer
        test_texts: List of test note texts
        test_labels: Test labels array
        label_names: List of label names
        thresholds: Per-label thresholds
        max_length: Maximum sequence length

    Returns:
        Dict with accuracy comparison metrics
    """
    import onnxruntime as ort
    from sklearn.metrics import f1_score

    print("\nValidating quantized model against original...")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path))

    # Load ONNX model
    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    onnx_session = ort.InferenceSession(
        str(quantized_onnx_path),
        sess_options=sess_options,
        providers=["CPUExecutionProvider"],
    )

    original_model.eval()

    # Run predictions
    pytorch_probs = []
    onnx_probs = []

    for text in test_texts[:100]:  # Sample for speed
        # Tokenize
        encoding = tokenizer(
            text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # PyTorch prediction
        with torch.no_grad():
            logits = original_model(
                encoding["input_ids"],
                encoding["attention_mask"],
            )
            probs = torch.sigmoid(logits).numpy()[0]
            pytorch_probs.append(probs)

        # ONNX prediction
        onnx_inputs = {
            "input_ids": encoding["input_ids"].numpy().astype(np.int64),
            "attention_mask": encoding["attention_mask"].numpy().astype(np.int64),
        }
        onnx_logits = onnx_session.run(None, onnx_inputs)[0]
        onnx_prob = 1 / (1 + np.exp(-onnx_logits[0]))  # Sigmoid
        onnx_probs.append(onnx_prob)

    pytorch_probs = np.array(pytorch_probs)
    onnx_probs = np.array(onnx_probs)

    # Compare predictions
    diff = np.abs(pytorch_probs - onnx_probs)
    max_diff = diff.max()
    mean_diff = diff.mean()

    print(f"  Max probability difference: {max_diff:.6f}")
    print(f"  Mean probability difference: {mean_diff:.6f}")

    # Apply thresholds and compare F1
    pytorch_preds = np.zeros_like(pytorch_probs)
    onnx_preds = np.zeros_like(onnx_probs)

    for i, label in enumerate(label_names):
        thresh = thresholds.get(label, 0.5)
        pytorch_preds[:, i] = (pytorch_probs[:, i] >= thresh).astype(int)
        onnx_preds[:, i] = (onnx_probs[:, i] >= thresh).astype(int)

    # Calculate F1 for both
    test_labels_subset = test_labels[:100]

    pytorch_f1 = f1_score(test_labels_subset.ravel(), pytorch_preds.ravel(), zero_division=0)
    onnx_f1 = f1_score(test_labels_subset.ravel(), onnx_preds.ravel(), zero_division=0)

    print(f"  PyTorch F1: {pytorch_f1:.4f}")
    print(f"  ONNX F1: {onnx_f1:.4f}")
    print(f"  F1 difference: {abs(pytorch_f1 - onnx_f1):.4f}")

    # Check if predictions match
    pred_match = (pytorch_preds == onnx_preds).all(axis=1).mean()
    print(f"  Prediction match rate: {pred_match * 100:.1f}%")

    return {
        "max_prob_diff": float(max_diff),
        "mean_prob_diff": float(mean_diff),
        "pytorch_f1": float(pytorch_f1),
        "onnx_f1": float(onnx_f1),
        "f1_diff": float(abs(pytorch_f1 - onnx_f1)),
        "prediction_match_rate": float(pred_match),
    }


# ============================================================================
# Main
# ============================================================================

def main():
    """Parse arguments and run export/quantization."""
    parser = argparse.ArgumentParser(
        description="Export and quantize BiomedBERT model to ONNX INT8"
    )

    parser.add_argument(
        "--model-dir",
        type=Path,
        required=True,
        help="Path to trained model directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("models"),
        help="Output directory for ONNX files (default: models/)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate quantized model against original",
    )
    parser.add_argument(
        "--test-csv",
        type=Path,
        default=Path("data/ml_training/registry_test.csv"),
        help="Test CSV for validation",
    )
    parser.add_argument(
        "--skip-full-export",
        action="store_true",
        help="Skip full ONNX export, only do quantization",
    )

    args = parser.parse_args()

    # Paths
    model_dir = args.model_dir
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    onnx_path = output_dir / "registry_model.onnx"
    quantized_path = output_dir / "registry_model_int8.onnx"
    tokenizer_path = model_dir / "tokenizer"

    # Load label fields
    label_fields_path = Path("data/ml_training/registry_label_fields.json")
    with open(label_fields_path) as f:
        label_names = json.load(f)
    num_labels = len(label_names)

    print(f"\n{'=' * 60}")
    print("ONNX Export and Quantization")
    print(f"{'=' * 60}")
    print(f"Model directory: {model_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Number of labels: {num_labels}")

    # Load model
    print("\nLoading PyTorch model...")
    model = BiomedBERTMultiLabel.from_pretrained(model_dir, num_labels)
    model.eval()

    # Export to ONNX
    if not args.skip_full_export:
        print("\n" + "=" * 40)
        print("Step 1: Export to ONNX")
        print("=" * 40)
        export_to_onnx(model, onnx_path)

    # Quantize
    print("\n" + "=" * 40)
    print("Step 2: INT8 Quantization")
    print("=" * 40)

    if onnx_path.exists():
        quantize_model(onnx_path, quantized_path)
    else:
        print(f"ERROR: ONNX model not found at {onnx_path}")
        return

    # Validate
    if args.validate:
        print("\n" + "=" * 40)
        print("Step 3: Validation")
        print("=" * 40)

        # Load test data
        import pandas as pd
        test_df = pd.read_csv(args.test_csv)
        test_texts = test_df["note_text"].fillna("").tolist()

        exclude_cols = {"note_text", "verified_cpt_codes"}
        label_cols = [c for c in test_df.columns if c not in exclude_cols]
        test_labels = test_df[label_cols].fillna(0).astype(int).to_numpy()

        # Load thresholds
        thresholds_path = model_dir.parent / "roberta_registry_thresholds.json"
        if thresholds_path.exists():
            with open(thresholds_path) as f:
                thresholds = json.load(f)
        else:
            thresholds = {name: 0.5 for name in label_names}

        validation_results = validate_quantized_model(
            original_model=model,
            quantized_onnx_path=quantized_path,
            tokenizer_path=tokenizer_path,
            test_texts=test_texts,
            test_labels=test_labels,
            label_names=label_names,
            thresholds=thresholds,
        )

        # Save validation results
        results_path = output_dir / "quantization_validation.json"
        with open(results_path, "w") as f:
            json.dump(validation_results, f, indent=2)
        print(f"\nValidation results saved to: {results_path}")

    # Copy tokenizer to output dir
    print("\n" + "=" * 40)
    print("Step 4: Copy Tokenizer")
    print("=" * 40)

    tokenizer_out = output_dir / "roberta_registry_tokenizer"
    if tokenizer_path.exists():
        import shutil
        if tokenizer_out.exists():
            shutil.rmtree(tokenizer_out)
        shutil.copytree(tokenizer_path, tokenizer_out)
        print(f"Tokenizer copied to: {tokenizer_out}")
    else:
        print(f"WARNING: Tokenizer not found at {tokenizer_path}")

    # Summary
    print(f"\n{'=' * 60}")
    print("Export Complete!")
    print(f"{'=' * 60}")
    print(f"ONNX model: {onnx_path}")
    print(f"Quantized model: {quantized_path}")
    print(f"Tokenizer: {tokenizer_out}")

    if quantized_path.exists():
        size_mb = quantized_path.stat().st_size / (1024 * 1024)
        print(f"\nFinal model size: {size_mb:.1f} MB")
        print("Ready for Railway deployment!")


if __name__ == "__main__":
    main()
