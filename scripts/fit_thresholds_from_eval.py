#!/usr/bin/env python3
"""
Fit per-code thresholds from validation metrics.

This script analyzes model evaluation metrics and computes optimal thresholds
for the ternary case difficulty classification (HIGH_CONF / GRAY_ZONE / LOW_CONF).

For each code:
- Picks an upper threshold that achieves target precision (e.g. >= 0.9)
- Uses a global lower threshold (e.g. 0.4) for gray zone boundary

Usage:
    python scripts/fit_thresholds_from_eval.py [--metrics PATH] [--output PATH]
    python scripts/fit_thresholds_from_eval.py --target-precision 0.85
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import typer

from modules.common.logger import get_logger
from modules.ml_coder.thresholds import THRESHOLDS_PATH, Thresholds
from modules.ml_coder.training import MLB_PATH, PIPELINE_PATH
from modules.ml_coder.utils import clean_cpt_codes

logger = get_logger("fit_thresholds")

app = typer.Typer(help="Fit per-code thresholds from evaluation metrics.")


def compute_precision_at_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
) -> float:
    """Compute precision at a given probability threshold."""
    y_pred = (y_prob >= threshold).astype(int)
    tp = ((y_pred == 1) & (y_true == 1)).sum()
    fp = ((y_pred == 1) & (y_true == 0)).sum()
    if tp + fp == 0:
        return 1.0  # No predictions, perfect precision by default
    return tp / (tp + fp)


def find_threshold_for_precision(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_precision: float = 0.9,
    min_threshold: float = 0.5,
    max_threshold: float = 0.95,
    step: float = 0.05,
) -> float:
    """Find the lowest threshold that achieves target precision."""
    for thresh in np.arange(min_threshold, max_threshold + step, step):
        prec = compute_precision_at_threshold(y_true, y_prob, thresh)
        if prec >= target_precision:
            return float(thresh)
    return max_threshold


def fit_thresholds_from_test_data(
    test_csv: Path,
    model_path: Path,
    mlb_path: Path,
    target_precision: float = 0.9,
    default_upper: float = 0.7,
    default_lower: float = 0.4,
) -> Thresholds:
    """
    Fit per-code thresholds from test data predictions.

    Args:
        test_csv: Path to test CSV with note_text and verified_cpt_codes
        model_path: Path to trained pipeline
        mlb_path: Path to MultiLabelBinarizer
        target_precision: Target precision for upper threshold
        default_upper: Default upper threshold if code has too few samples
        default_lower: Global lower threshold

    Returns:
        Thresholds object with per-code upper thresholds
    """
    logger.info("Loading model from %s", model_path)
    pipeline = joblib.load(model_path)
    mlb = joblib.load(mlb_path)

    logger.info("Loading test data from %s", test_csv)
    df = pd.read_csv(test_csv)
    df = df.dropna(subset=["note_text", "verified_cpt_codes"])
    df["note_text"] = df["note_text"].astype(str)
    df["verified_cpt_codes"] = df["verified_cpt_codes"].apply(clean_cpt_codes)

    texts = df["note_text"].tolist()
    labels = df["verified_cpt_codes"].tolist()

    logger.info("Running predictions on %d samples", len(texts))
    y_prob = pipeline.predict_proba(texts)
    y_true = mlb.transform(labels)

    per_code: dict[str, float] = {}

    for i, code in enumerate(mlb.classes_):
        code_true = y_true[:, i]
        code_prob = y_prob[:, i]

        # Only fit threshold if we have enough positive samples
        n_positive = code_true.sum()
        if n_positive < 3:
            logger.debug(
                "Code %s has only %d positive samples, using default threshold",
                code,
                n_positive,
            )
            per_code[code] = default_upper
            continue

        thresh = find_threshold_for_precision(
            code_true,
            code_prob,
            target_precision=target_precision,
            min_threshold=default_lower,
            max_threshold=0.95,
        )

        actual_precision = compute_precision_at_threshold(code_true, code_prob, thresh)
        logger.info(
            "Code %s: threshold=%.2f, precision=%.3f (n=%d)",
            code,
            thresh,
            actual_precision,
            n_positive,
        )
        per_code[code] = thresh

    return Thresholds(
        upper=default_upper,
        lower=default_lower,
        per_code=per_code,
    )


def analyze_metrics_file(
    metrics_path: Path,
    target_precision: float = 0.9,
    default_upper: float = 0.7,
    default_lower: float = 0.4,
) -> Thresholds:
    """
    Derive thresholds from pre-computed metrics file.

    This is a simpler approach that uses evaluation metrics
    to set thresholds based on observed performance.
    """
    logger.info("Loading metrics from %s", metrics_path)
    with open(metrics_path) as f:
        metrics = json.load(f)

    per_code: dict[str, float] = {}
    code_metrics = metrics.get("per_code", {})

    for code, data in code_metrics.items():
        precision = data.get("precision", 0.0)
        support = data.get("support", 0)

        # If current precision at 0.5 threshold is below target,
        # we need a higher threshold for high-confidence predictions
        if precision < target_precision and support >= 3:
            # Estimate: raise threshold proportionally to precision gap
            adjustment = (target_precision - precision) / target_precision
            new_thresh = min(0.5 + adjustment * 0.4, 0.9)
            per_code[code] = round(new_thresh, 2)
            logger.info(
                "Code %s: precision=%.2f < target, setting threshold=%.2f",
                code,
                precision,
                new_thresh,
            )
        elif precision >= target_precision:
            # Good precision at 0.5, can use default or slightly lower
            per_code[code] = default_upper
            logger.info(
                "Code %s: precision=%.2f >= target, using default threshold=%.2f",
                code,
                precision,
                default_upper,
            )
        else:
            # Low support, use default
            per_code[code] = default_upper

    return Thresholds(
        upper=default_upper,
        lower=default_lower,
        per_code=per_code,
    )


@app.command()
def main(
    test_csv: Path = typer.Option(
        Path("data/ml_training/test.csv"),
        "--test-csv",
        help="Path to test CSV file",
    ),
    metrics_path: Path = typer.Option(
        Path("data/models/metrics.json"),
        "--metrics",
        help="Path to evaluation metrics JSON (used if test CSV not available)",
    ),
    output_path: Path = typer.Option(
        THRESHOLDS_PATH,
        "--output",
        help="Output path for thresholds JSON",
    ),
    target_precision: float = typer.Option(
        0.9,
        "--target-precision",
        help="Target precision for high-confidence threshold",
    ),
    default_upper: float = typer.Option(
        0.7,
        "--default-upper",
        help="Default upper threshold",
    ),
    default_lower: float = typer.Option(
        0.4,
        "--default-lower",
        help="Default lower threshold (gray zone boundary)",
    ),
    use_metrics_only: bool = typer.Option(
        False,
        "--metrics-only",
        help="Use metrics file instead of re-running predictions",
    ),
) -> None:
    """Fit per-code thresholds from validation data."""
    model_path = PIPELINE_PATH
    mlb_path = MLB_PATH

    if use_metrics_only or not model_path.exists():
        if not metrics_path.exists():
            typer.echo(f"Error: Metrics file not found at {metrics_path}", err=True)
            raise typer.Exit(1)
        thresholds = analyze_metrics_file(
            metrics_path,
            target_precision=target_precision,
            default_upper=default_upper,
            default_lower=default_lower,
        )
    else:
        if not test_csv.exists():
            typer.echo(f"Error: Test CSV not found at {test_csv}", err=True)
            raise typer.Exit(1)
        thresholds = fit_thresholds_from_test_data(
            test_csv,
            model_path,
            mlb_path,
            target_precision=target_precision,
            default_upper=default_upper,
            default_lower=default_lower,
        )

    thresholds.to_json(output_path)
    logger.info("Saved thresholds to %s", output_path)

    # Summary
    typer.echo(f"\nThresholds saved to {output_path}")
    typer.echo(f"  Global upper: {thresholds.upper}")
    typer.echo(f"  Global lower: {thresholds.lower}")
    typer.echo(f"  Per-code overrides: {len(thresholds.per_code)}")

    # Show per-code thresholds
    if thresholds.per_code:
        typer.echo("\nPer-code upper thresholds:")
        for code, thresh in sorted(thresholds.per_code.items()):
            typer.echo(f"  {code}: {thresh:.2f}")


if __name__ == "__main__":
    app()
