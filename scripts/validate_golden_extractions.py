#!/usr/bin/env python3
"""
Validation harness for golden extractions using Gemini API.

Runs the coder and registry extraction pipeline on notes from the golden
extractions file and compares outputs against verified ground truth.
Generates detailed error analysis and improvement recommendations.

Usage:
    python scripts/validate_golden_extractions.py [--limit N] [--verbose] [--output DIR]
    python scripts/validate_golden_extractions.py --iterate  # Run iterative improvement loop

Environment:
    GOOGLE_API_KEY: Required for Gemini API calls
    CODER_USE_LLM_ADVISOR: Set to "true" to enable LLM advisor in coder
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Ensure local imports work when run as a script
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Load .env file before any other imports (override=True to prefer .env over shell)
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=True)
except ImportError:
    pass  # dotenv not installed, rely on shell environment

# Normalize API key env vars (project uses both GEMINI_API_KEY and GOOGLE_API_KEY)
if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from modules.api.dependencies import get_coding_service, reset_coding_service_cache
from modules.registry.engine import RegistryEngine
from modules.common.rvu_calc import RVUCalc
from observability.logging_config import get_logger

logger = get_logger("validate_golden")

# Default paths
GOLDEN_EXTRACTIONS_PATH = ROOT / "data" / "knowledge" / "golden_extractions" / "consolidated_verified_notes_v2_8_part_002.json"
OUTPUT_DIR = ROOT / "validation_results"


@dataclass
class CodeError:
    """Represents a CPT code mismatch."""
    code: str
    error_type: str  # "missing", "extra", "wrong_modifier"
    expected: Optional[str] = None
    actual: Optional[str] = None
    note_index: int = 0
    note_snippet: str = ""


@dataclass
class RegistryError:
    """Represents a registry field mismatch."""
    field: str
    expected: Any
    actual: Any
    error_type: str  # "missing", "wrong_value", "type_mismatch"
    note_index: int = 0
    semantic_match: bool = False  # For free-text fields


@dataclass
class RVUError:
    """Represents an RVU mismatch."""
    field: str  # "total_rvu", "work_rvu", etc.
    expected: float
    actual: float
    error_pct: float  # Percentage error
    note_index: int = 0


@dataclass
class ValidationResult:
    """Results for a single note validation."""
    note_index: int
    note_text: str

    # CPT code results
    expected_codes: list[str] = field(default_factory=list)
    predicted_codes: list[str] = field(default_factory=list)
    code_errors: list[CodeError] = field(default_factory=list)
    code_exact_match: bool = False

    # Registry results
    expected_registry: dict = field(default_factory=dict)
    predicted_registry: dict = field(default_factory=dict)
    registry_errors: list[RegistryError] = field(default_factory=list)
    registry_field_accuracy: float = 0.0

    # RVU results
    expected_rvu: dict = field(default_factory=dict)  # {total_rvu, work_rvu, ...}
    predicted_rvu: dict = field(default_factory=dict)
    rvu_errors: list[RVUError] = field(default_factory=list)
    rvu_exact_match: bool = False

    # Timing
    coder_latency_ms: float = 0.0
    registry_latency_ms: float = 0.0

    # Error details
    llm_error: Optional[str] = None


@dataclass
class AggregateMetrics:
    """Aggregate metrics across all notes."""
    # Code-level metrics
    code_precision: float = 0.0
    code_recall: float = 0.0
    code_f1: float = 0.0
    code_exact_match_rate: float = 0.0

    # Per-code breakdown
    per_code_metrics: dict[str, dict] = field(default_factory=dict)

    # Registry metrics
    registry_field_accuracy: float = 0.0
    per_field_accuracy: dict[str, float] = field(default_factory=dict)

    # RVU metrics
    rvu_total_mae: float = 0.0  # Mean Absolute Error for total RVU
    rvu_work_mae: float = 0.0   # Mean Absolute Error for work RVU
    rvu_total_mape: float = 0.0  # Mean Absolute Percentage Error for total RVU
    rvu_work_mape: float = 0.0   # Mean Absolute Percentage Error for work RVU
    rvu_exact_match_rate: float = 0.0  # Percentage with exact RVU match (within tolerance)
    rvu_notes_evaluated: int = 0  # Number of notes with RVU data

    # Error patterns
    common_code_errors: list[tuple[str, int]] = field(default_factory=list)
    common_field_errors: list[tuple[str, int]] = field(default_factory=list)

    # Timing
    avg_coder_latency_ms: float = 0.0
    avg_registry_latency_ms: float = 0.0
    total_notes: int = 0
    successful_notes: int = 0


# Fields that require semantic comparison (not exact match)
SEMANTIC_FIELDS = {
    "primary_indication",
    "final_diagnosis_prelim",
    "disposition",
    "follow_up_plan",
    "radiographic_findings",
    "ebus_rose_result",
    "cao_primary_modality",
    "blvr_chartis_result",
}

# Fields to skip in validation (metadata or not extractable from note)
SKIP_FIELDS = {
    "evidence",
    "metadata",
    "cpt_verification_errors",
    "cpt_validation_metadata",
    "patch_metadata",
    "source_file",
    "note_text",
    "procedure_families",
}


def normalize_code(code: Any) -> str:
    """Normalize CPT code to string, stripping + prefix."""
    code_str = str(code).strip()
    return code_str.lstrip("+")


# Global RVU calculator instance
_rvu_calc: RVUCalc | None = None


def get_rvu_calc() -> RVUCalc:
    """Get or create the RVU calculator."""
    global _rvu_calc
    if _rvu_calc is None:
        _rvu_calc = RVUCalc()
    return _rvu_calc


def extract_rvu_from_golden(entry: dict) -> dict:
    """Extract expected RVU values from golden entry's billing data."""
    registry = entry.get("registry_entry", {})
    billing = registry.get("billing", {})

    if not billing:
        return {}

    return {
        "total_rvu": billing.get("total_rvu", 0.0),
        "work_rvu": billing.get("work_rvu", 0.0),
        "practice_expense_rvu": billing.get("practice_expense_rvu", 0.0),
        "malpractice_rvu": billing.get("malpractice_rvu", 0.0),
    }


def calculate_rvu_from_codes(codes: list[str]) -> dict:
    """Calculate RVU totals from a list of CPT codes."""
    rvu_calc = get_rvu_calc()

    total_rvu = 0.0
    work_rvu = 0.0
    pe_rvu = 0.0
    mp_rvu = 0.0

    for code in codes:
        # Normalize the code (remove + prefix)
        normalized = normalize_code(code)
        record = rvu_calc.lookup(normalized)

        if record:
            work_rvu += record.work_rvu
            total_rvu += record.total_facility_rvu
            # Note: RVURecord doesn't split PE and MP separately
            # We can estimate them as total - work for PE+MP combined
            pe_mp = record.total_facility_rvu - record.work_rvu
            pe_rvu += pe_mp * 0.8  # Rough estimate: PE is typically ~80% of non-work
            mp_rvu += pe_mp * 0.2  # MP is typically ~20% of non-work

    return {
        "total_rvu": round(total_rvu, 2),
        "work_rvu": round(work_rvu, 2),
        "practice_expense_rvu": round(pe_rvu, 2),
        "malpractice_rvu": round(mp_rvu, 2),
    }


def compare_rvu(expected: dict, predicted: dict, tolerance: float = 0.1) -> tuple[list[RVUError], bool]:
    """Compare expected vs predicted RVU values.

    Args:
        expected: Expected RVU dict from golden
        predicted: Predicted RVU dict from codes
        tolerance: Tolerance for "exact match" (default 0.1 RVU)

    Returns:
        Tuple of (list of RVUError, whether it's an exact match within tolerance)
    """
    errors = []

    if not expected:
        return errors, True  # No expected RVU to compare

    fields_to_check = ["total_rvu", "work_rvu"]
    all_match = True

    for field in fields_to_check:
        exp_val = expected.get(field, 0.0)
        pred_val = predicted.get(field, 0.0)

        if exp_val == 0 and pred_val == 0:
            continue

        abs_error = abs(pred_val - exp_val)
        pct_error = (abs_error / exp_val * 100) if exp_val > 0 else (100 if pred_val > 0 else 0)

        if abs_error > tolerance:
            all_match = False
            errors.append(RVUError(
                field=field,
                expected=exp_val,
                actual=pred_val,
                error_pct=pct_error,
            ))

    return errors, all_match


def load_golden_extractions(path: Path) -> list[dict]:
    """Load golden extractions from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def extract_codes_from_golden(entry: dict) -> list[str]:
    """Extract expected CPT codes from golden entry."""
    codes = entry.get("cpt_codes", [])
    return [normalize_code(c) for c in codes]


def extract_codes_from_suggestions(suggestions: list) -> list[str]:
    """Extract CPT codes from CodingService suggestions."""
    codes = []
    for s in suggestions:
        if hasattr(s, "code"):
            codes.append(normalize_code(s.code))
        elif isinstance(s, dict) and "code" in s:
            codes.append(normalize_code(s["code"]))
    return codes


def compare_codes(expected: list[str], predicted: list[str]) -> list[CodeError]:
    """Compare expected vs predicted codes and return errors."""
    expected_set = set(expected)
    predicted_set = set(predicted)

    errors = []

    # Missing codes (in expected but not predicted)
    for code in expected_set - predicted_set:
        errors.append(CodeError(
            code=code,
            error_type="missing",
            expected=code,
            actual=None,
        ))

    # Extra codes (in predicted but not expected)
    for code in predicted_set - expected_set:
        errors.append(CodeError(
            code=code,
            error_type="extra",
            expected=None,
            actual=code,
        ))

    return errors


def compare_registry_fields(
    expected: dict,
    predicted: dict,
    skip_fields: set[str] = SKIP_FIELDS,
    semantic_fields: set[str] = SEMANTIC_FIELDS,
) -> tuple[list[RegistryError], float]:
    """Compare registry fields and compute accuracy."""
    errors = []
    total_fields = 0
    correct_fields = 0

    # Get all fields from expected, excluding skip fields
    all_fields = set(expected.keys()) - skip_fields

    for field_name in all_fields:
        expected_val = expected.get(field_name)
        predicted_val = predicted.get(field_name)

        # Skip None/null comparisons if both are empty
        if expected_val is None and predicted_val is None:
            continue

        # Skip empty lists/dicts
        if expected_val in ([], {}, "") and predicted_val in ([], {}, None):
            continue

        total_fields += 1

        # Check for match
        is_match = False

        if field_name in semantic_fields:
            # For semantic fields, check if key terms overlap
            is_match = semantic_match(expected_val, predicted_val)
        else:
            # Exact match (with type normalization)
            is_match = values_match(expected_val, predicted_val)

        if is_match:
            correct_fields += 1
        else:
            error_type = "wrong_value"
            if predicted_val is None:
                error_type = "missing"
            elif type(expected_val) != type(predicted_val):
                error_type = "type_mismatch"

            errors.append(RegistryError(
                field=field_name,
                expected=expected_val,
                actual=predicted_val,
                error_type=error_type,
                semantic_match=field_name in semantic_fields,
            ))

    accuracy = correct_fields / total_fields if total_fields > 0 else 1.0
    return errors, accuracy


def semantic_match(expected: Any, actual: Any) -> bool:
    """Check if two values are semantically equivalent."""
    if expected is None and actual is None:
        return True
    if expected is None or actual is None:
        return False

    # Convert to lowercase strings for comparison
    exp_str = str(expected).lower()
    act_str = str(actual).lower()

    # Check for exact match
    if exp_str == act_str:
        return True

    # Check if one contains the other
    if exp_str in act_str or act_str in exp_str:
        return True

    # Check for key term overlap (at least 50% of words match)
    exp_words = set(exp_str.split())
    act_words = set(act_str.split())

    if not exp_words or not act_words:
        return False

    overlap = len(exp_words & act_words)
    min_words = min(len(exp_words), len(act_words))

    return overlap >= min_words * 0.5


def values_match(expected: Any, actual: Any) -> bool:
    """Check if two values match (with type normalization)."""
    if expected is None and actual is None:
        return True
    if expected is None or actual is None:
        return False

    # Normalize types
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(expected - actual) < 0.01

    if isinstance(expected, list) and isinstance(actual, list):
        return set(str(x) for x in expected) == set(str(x) for x in actual)

    if isinstance(expected, dict) and isinstance(actual, dict):
        return expected == actual

    return str(expected).lower().strip() == str(actual).lower().strip()


def validate_single_note(
    entry: dict,
    note_index: int,
    coding_service,
    registry_engine: RegistryEngine,
    use_llm: bool = True,
) -> ValidationResult:
    """Validate a single note against golden extraction."""
    note_text = entry.get("note_text", "")

    result = ValidationResult(
        note_index=note_index,
        note_text=note_text[:500] + "..." if len(note_text) > 500 else note_text,
        expected_codes=extract_codes_from_golden(entry),
        expected_registry=entry.get("registry_entry", {}),
    )

    try:
        # Run coder
        start = time.perf_counter()
        suggestions, llm_latency = coding_service.generate_suggestions(
            procedure_id=f"golden_{note_index}",
            report_text=note_text,
            use_llm=use_llm,
        )
        result.coder_latency_ms = (time.perf_counter() - start) * 1000
        result.predicted_codes = extract_codes_from_suggestions(suggestions)

        # Compare codes
        result.code_errors = compare_codes(result.expected_codes, result.predicted_codes)
        result.code_exact_match = len(result.code_errors) == 0

        # Compare RVU values
        result.expected_rvu = extract_rvu_from_golden(entry)
        if result.expected_rvu:  # Only calculate if golden has RVU data
            result.predicted_rvu = calculate_rvu_from_codes(result.predicted_codes)
            result.rvu_errors, result.rvu_exact_match = compare_rvu(
                result.expected_rvu, result.predicted_rvu
            )

    except Exception as e:
        result.llm_error = f"Coder error: {str(e)}"
        logger.error(f"Coder failed on note {note_index}: {e}")

    try:
        # Run registry extraction
        start = time.perf_counter()
        registry_result = registry_engine.run(note_text, explain=False, include_evidence=False)
        result.registry_latency_ms = (time.perf_counter() - start) * 1000

        if registry_result:
            result.predicted_registry = registry_result.model_dump() if hasattr(registry_result, "model_dump") else dict(registry_result)

        # Compare registry fields
        result.registry_errors, result.registry_field_accuracy = compare_registry_fields(
            result.expected_registry,
            result.predicted_registry,
        )

    except Exception as e:
        if result.llm_error:
            result.llm_error += f"; Registry error: {str(e)}"
        else:
            result.llm_error = f"Registry error: {str(e)}"
        logger.error(f"Registry extraction failed on note {note_index}: {e}")

    return result


def compute_aggregate_metrics(results: list[ValidationResult]) -> AggregateMetrics:
    """Compute aggregate metrics from validation results."""
    metrics = AggregateMetrics()

    if not results:
        return metrics

    metrics.total_notes = len(results)
    metrics.successful_notes = sum(1 for r in results if r.llm_error is None)

    # Code-level metrics
    all_expected = [set(r.expected_codes) for r in results]
    all_predicted = [set(r.predicted_codes) for r in results]

    total_tp = total_fp = total_fn = 0
    code_stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    for expected, predicted in zip(all_expected, all_predicted):
        for code in expected | predicted:
            if code in expected and code in predicted:
                total_tp += 1
                code_stats[code]["tp"] += 1
            elif code in predicted:
                total_fp += 1
                code_stats[code]["fp"] += 1
            else:
                total_fn += 1
                code_stats[code]["fn"] += 1

    metrics.code_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    metrics.code_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    metrics.code_f1 = 2 * metrics.code_precision * metrics.code_recall / (metrics.code_precision + metrics.code_recall) if (metrics.code_precision + metrics.code_recall) > 0 else 0.0
    metrics.code_exact_match_rate = sum(1 for r in results if r.code_exact_match) / len(results)

    # Per-code metrics
    for code, stats in code_stats.items():
        tp, fp, fn = stats["tp"], stats["fp"], stats["fn"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        metrics.per_code_metrics[code] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    # Registry metrics
    field_correct = defaultdict(int)
    field_total = defaultdict(int)

    for r in results:
        for err in r.registry_errors:
            field_total[err.field] += 1

        # Count correct fields
        checked_fields = set(r.expected_registry.keys()) - SKIP_FIELDS
        for field in checked_fields:
            field_total[field] += 1
            if not any(e.field == field for e in r.registry_errors):
                field_correct[field] += 1

    total_fields_checked = sum(field_total.values())
    total_correct = sum(field_correct.values())
    metrics.registry_field_accuracy = total_correct / total_fields_checked if total_fields_checked > 0 else 0.0

    for field in field_total:
        metrics.per_field_accuracy[field] = field_correct[field] / field_total[field] if field_total[field] > 0 else 0.0

    # RVU metrics
    rvu_results = [r for r in results if r.expected_rvu]  # Only notes with RVU data
    metrics.rvu_notes_evaluated = len(rvu_results)

    if rvu_results:
        # Calculate MAE and MAPE for total_rvu and work_rvu
        total_rvu_errors = []
        work_rvu_errors = []
        total_rvu_pct_errors = []
        work_rvu_pct_errors = []

        for r in rvu_results:
            exp_total = r.expected_rvu.get("total_rvu", 0.0)
            pred_total = r.predicted_rvu.get("total_rvu", 0.0)
            exp_work = r.expected_rvu.get("work_rvu", 0.0)
            pred_work = r.predicted_rvu.get("work_rvu", 0.0)

            total_rvu_errors.append(abs(pred_total - exp_total))
            work_rvu_errors.append(abs(pred_work - exp_work))

            if exp_total > 0:
                total_rvu_pct_errors.append(abs(pred_total - exp_total) / exp_total * 100)
            if exp_work > 0:
                work_rvu_pct_errors.append(abs(pred_work - exp_work) / exp_work * 100)

        metrics.rvu_total_mae = sum(total_rvu_errors) / len(total_rvu_errors) if total_rvu_errors else 0.0
        metrics.rvu_work_mae = sum(work_rvu_errors) / len(work_rvu_errors) if work_rvu_errors else 0.0
        metrics.rvu_total_mape = sum(total_rvu_pct_errors) / len(total_rvu_pct_errors) if total_rvu_pct_errors else 0.0
        metrics.rvu_work_mape = sum(work_rvu_pct_errors) / len(work_rvu_pct_errors) if work_rvu_pct_errors else 0.0
        metrics.rvu_exact_match_rate = sum(1 for r in rvu_results if r.rvu_exact_match) / len(rvu_results)

    # Common errors
    code_error_counts = defaultdict(int)
    field_error_counts = defaultdict(int)

    for r in results:
        for err in r.code_errors:
            key = f"{err.error_type}:{err.code}"
            code_error_counts[key] += 1
        for err in r.registry_errors:
            key = f"{err.error_type}:{err.field}"
            field_error_counts[key] += 1

    metrics.common_code_errors = sorted(code_error_counts.items(), key=lambda x: -x[1])[:20]
    metrics.common_field_errors = sorted(field_error_counts.items(), key=lambda x: -x[1])[:20]

    # Timing
    metrics.avg_coder_latency_ms = sum(r.coder_latency_ms for r in results) / len(results)
    metrics.avg_registry_latency_ms = sum(r.registry_latency_ms for r in results) / len(results)

    return metrics


def generate_improvement_recommendations(metrics: AggregateMetrics) -> list[str]:
    """Generate improvement recommendations based on validation results."""
    recommendations = []

    # Code-level recommendations
    if metrics.code_recall < 0.8:
        recommendations.append(
            f"⚠️ Code Recall is low ({metrics.code_recall:.1%}). "
            "Consider adding more keyword mappings or relaxing detection thresholds."
        )

    if metrics.code_precision < 0.8:
        recommendations.append(
            f"⚠️ Code Precision is low ({metrics.code_precision:.1%}). "
            "Consider tightening evidence requirements or adding negation patterns."
        )

    # Per-code issues
    low_recall_codes = [
        (code, m) for code, m in metrics.per_code_metrics.items()
        if m["recall"] < 0.5 and m["fn"] >= 2
    ]
    if low_recall_codes:
        codes_list = ", ".join(f"{code}({m['recall']:.0%})" for code, m in sorted(low_recall_codes, key=lambda x: x[1]["recall"])[:5])
        recommendations.append(
            f"🔍 Codes with low recall (often missed): {codes_list}. "
            "Add more keyword patterns or check for negation false positives."
        )

    low_precision_codes = [
        (code, m) for code, m in metrics.per_code_metrics.items()
        if m["precision"] < 0.5 and m["fp"] >= 2
    ]
    if low_precision_codes:
        codes_list = ", ".join(f"{code}({m['precision']:.0%})" for code, m in sorted(low_precision_codes, key=lambda x: x[1]["precision"])[:5])
        recommendations.append(
            f"🎯 Codes with low precision (often extra): {codes_list}. "
            "Add negative evidence patterns or stricter context requirements."
        )

    # Registry field recommendations
    low_accuracy_fields = [
        (field, acc) for field, acc in metrics.per_field_accuracy.items()
        if acc < 0.5
    ]
    if low_accuracy_fields:
        fields_list = ", ".join(f"{f}({a:.0%})" for f, a in sorted(low_accuracy_fields, key=lambda x: x[1])[:5])
        recommendations.append(
            f"📋 Registry fields with low accuracy: {fields_list}. "
            "Review extraction prompts or add field-specific postprocessors."
        )

    # RVU recommendations
    if metrics.rvu_notes_evaluated > 0:
        if metrics.rvu_exact_match_rate < 0.5:
            recommendations.append(
                f"💰 RVU exact match rate is low ({metrics.rvu_exact_match_rate:.1%}). "
                "This correlates with code accuracy - fix code prediction to improve RVU accuracy."
            )
        if metrics.rvu_total_mape > 20:
            recommendations.append(
                f"💰 Total RVU MAPE is high ({metrics.rvu_total_mape:.1f}%). "
                "Review commonly missed or extra codes that contribute high RVU values."
            )

    # Common error patterns
    if metrics.common_code_errors:
        top_errors = metrics.common_code_errors[:3]
        error_desc = "; ".join(f"{err}({count}x)" for err, count in top_errors)
        recommendations.append(
            f"🔄 Most common code errors: {error_desc}"
        )

    if not recommendations:
        recommendations.append("✅ All metrics look good! Consider expanding the test set.")

    return recommendations


def print_summary(metrics: AggregateMetrics, recommendations: list[str]):
    """Print validation summary to console."""
    print("\n" + "=" * 70)
    print("GOLDEN EXTRACTION VALIDATION SUMMARY")
    print("=" * 70)

    print(f"\n📊 Dataset: {metrics.total_notes} notes, {metrics.successful_notes} successful")

    print(f"\n🏷️  CPT Code Metrics:")
    print(f"    Exact Match Rate: {metrics.code_exact_match_rate:.1%}")
    print(f"    Precision:        {metrics.code_precision:.3f}")
    print(f"    Recall:           {metrics.code_recall:.3f}")
    print(f"    F1 Score:         {metrics.code_f1:.3f}")

    print(f"\n📋 Registry Field Metrics:")
    print(f"    Overall Accuracy: {metrics.registry_field_accuracy:.1%}")

    if metrics.rvu_notes_evaluated > 0:
        print(f"\n💰 RVU Metrics ({metrics.rvu_notes_evaluated} notes with billing data):")
        print(f"    Exact Match Rate: {metrics.rvu_exact_match_rate:.1%}")
        print(f"    Total RVU MAE:    {metrics.rvu_total_mae:.2f} RVU")
        print(f"    Work RVU MAE:     {metrics.rvu_work_mae:.2f} RVU")
        print(f"    Total RVU MAPE:   {metrics.rvu_total_mape:.1f}%")
        print(f"    Work RVU MAPE:    {metrics.rvu_work_mape:.1f}%")

    print(f"\n⏱️  Timing:")
    print(f"    Avg Coder Latency:    {metrics.avg_coder_latency_ms:.0f}ms")
    print(f"    Avg Registry Latency: {metrics.avg_registry_latency_ms:.0f}ms")

    if metrics.per_code_metrics:
        print(f"\n📈 Per-Code Performance (showing codes with issues):")
        print(f"    {'Code':<10} {'Prec':<8} {'Recall':<8} {'F1':<8} {'TP':<5} {'FP':<5} {'FN':<5}")
        print("    " + "-" * 50)

        # Show codes with any issues (F1 < 1.0)
        problem_codes = [
            (code, m) for code, m in metrics.per_code_metrics.items()
            if m["f1"] < 1.0 and (m["fp"] + m["fn"]) > 0
        ]
        for code, m in sorted(problem_codes, key=lambda x: x[1]["f1"])[:10]:
            print(f"    {code:<10} {m['precision']:.2f}     {m['recall']:.2f}     {m['f1']:.2f}     {m['tp']:<5} {m['fp']:<5} {m['fn']:<5}")

    print(f"\n💡 Recommendations:")
    for rec in recommendations:
        print(f"    {rec}")

    print("\n" + "=" * 70)


def save_results(
    results: list[ValidationResult],
    metrics: AggregateMetrics,
    recommendations: list[str],
    output_dir: Path,
):
    """Save validation results to JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed results
    results_data = []
    for r in results:
        results_data.append({
            "note_index": r.note_index,
            "expected_codes": r.expected_codes,
            "predicted_codes": r.predicted_codes,
            "code_exact_match": r.code_exact_match,
            "code_errors": [
                {"code": e.code, "type": e.error_type, "expected": e.expected, "actual": e.actual}
                for e in r.code_errors
            ],
            "registry_field_accuracy": r.registry_field_accuracy,
            "registry_errors": [
                {"field": e.field, "type": e.error_type, "expected": str(e.expected)[:200], "actual": str(e.actual)[:200]}
                for e in r.registry_errors
            ],
            "expected_rvu": r.expected_rvu,
            "predicted_rvu": r.predicted_rvu,
            "rvu_exact_match": r.rvu_exact_match,
            "rvu_errors": [
                {"field": e.field, "expected": e.expected, "actual": e.actual, "error_pct": e.error_pct}
                for e in r.rvu_errors
            ],
            "coder_latency_ms": r.coder_latency_ms,
            "registry_latency_ms": r.registry_latency_ms,
            "llm_error": r.llm_error,
        })

    results_path = output_dir / f"validation_results_{timestamp}.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)

    # Save summary metrics
    summary_path = output_dir / f"validation_summary_{timestamp}.json"
    summary = {
        "timestamp": timestamp,
        "total_notes": metrics.total_notes,
        "successful_notes": metrics.successful_notes,
        "code_metrics": {
            "precision": metrics.code_precision,
            "recall": metrics.code_recall,
            "f1": metrics.code_f1,
            "exact_match_rate": metrics.code_exact_match_rate,
        },
        "registry_metrics": {
            "field_accuracy": metrics.registry_field_accuracy,
        },
        "rvu_metrics": {
            "notes_evaluated": metrics.rvu_notes_evaluated,
            "exact_match_rate": metrics.rvu_exact_match_rate,
            "total_rvu_mae": metrics.rvu_total_mae,
            "work_rvu_mae": metrics.rvu_work_mae,
            "total_rvu_mape": metrics.rvu_total_mape,
            "work_rvu_mape": metrics.rvu_work_mape,
        },
        "per_code_metrics": metrics.per_code_metrics,
        "per_field_accuracy": metrics.per_field_accuracy,
        "common_code_errors": metrics.common_code_errors,
        "common_field_errors": metrics.common_field_errors,
        "timing": {
            "avg_coder_latency_ms": metrics.avg_coder_latency_ms,
            "avg_registry_latency_ms": metrics.avg_registry_latency_ms,
        },
        "recommendations": recommendations,
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n📁 Results saved to: {output_dir}")
    print(f"    - {results_path.name}")
    print(f"    - {summary_path.name}")


def run_validation(
    golden_path: Path = GOLDEN_EXTRACTIONS_PATH,
    output_dir: Path = OUTPUT_DIR,
    limit: Optional[int] = None,
    verbose: bool = False,
    use_llm: bool = True,
) -> tuple[AggregateMetrics, list[str]]:
    """Run the full validation pipeline."""

    # Check for API key
    if use_llm and not os.getenv("GOOGLE_API_KEY"):
        logger.warning("GOOGLE_API_KEY not set, LLM advisor will be disabled")
        use_llm = False

    # Enable LLM advisor for coder BEFORE initializing services
    if use_llm:
        os.environ["CODER_USE_LLM_ADVISOR"] = "true"
    else:
        os.environ["CODER_USE_LLM_ADVISOR"] = "false"

    # Load golden extractions
    print(f"📂 Loading golden extractions from: {golden_path}")
    entries = load_golden_extractions(golden_path)

    if limit:
        entries = entries[:limit]
    print(f"   Loaded {len(entries)} entries" + (f" (limited from full set)" if limit else ""))

    # Initialize services (reset cache to pick up env var changes)
    print("\n🔧 Initializing services...")
    reset_coding_service_cache()  # Reset to pick up CODER_USE_LLM_ADVISOR
    coding_service = get_coding_service()
    registry_engine = RegistryEngine()

    # Log LLM advisor status
    llm_status = "enabled" if coding_service.llm_advisor else "disabled (rules only)"
    print(f"   Coder LLM advisor: {llm_status}")
    print("   Services initialized")

    # Run validation
    print(f"\n🚀 Running validation on {len(entries)} notes...")
    results = []

    for i, entry in enumerate(entries):
        if verbose:
            print(f"   [{i+1}/{len(entries)}] Processing note...", end=" ")

        result = validate_single_note(
            entry=entry,
            note_index=i,
            coding_service=coding_service,
            registry_engine=registry_engine,
            use_llm=use_llm,
        )
        results.append(result)

        if verbose:
            status = "✓" if result.code_exact_match else "✗"
            errors = len(result.code_errors)
            print(f"{status} ({errors} code errors, {len(result.registry_errors)} field errors)")
        elif (i + 1) % 10 == 0:
            print(f"   Processed {i+1}/{len(entries)} notes...")

    # Compute metrics
    print("\n📊 Computing metrics...")
    metrics = compute_aggregate_metrics(results)
    recommendations = generate_improvement_recommendations(metrics)

    # Print summary
    print_summary(metrics, recommendations)

    # Save results
    save_results(results, metrics, recommendations, output_dir)

    return metrics, recommendations


def main():
    parser = argparse.ArgumentParser(
        description="Validate coder and registry extraction against golden extractions"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=None,
        help="Limit number of notes to validate"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-note results"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory for results"
    )
    parser.add_argument(
        "--golden-path",
        type=Path,
        default=GOLDEN_EXTRACTIONS_PATH,
        help="Path to golden extractions JSON"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM advisor (rules only)"
    )
    parser.add_argument(
        "--iterate",
        action="store_true",
        help="Run iterative improvement loop (experimental)"
    )

    args = parser.parse_args()

    if not args.golden_path.exists():
        print(f"❌ Error: Golden extractions file not found: {args.golden_path}")
        sys.exit(1)

    metrics, recommendations = run_validation(
        golden_path=args.golden_path,
        output_dir=args.output,
        limit=args.limit,
        verbose=args.verbose,
        use_llm=not args.no_llm,
    )

    # Return non-zero exit code if F1 is below threshold
    if metrics.code_f1 < 0.5:
        print("\n⚠️  Warning: F1 score below 0.5 threshold")
        sys.exit(1)


if __name__ == "__main__":
    main()
