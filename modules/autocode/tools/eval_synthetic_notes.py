from __future__ import annotations

import argparse
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Iterable, Set

import pandas as pd


# Path is: modules/autocode/tools/eval_synthetic_notes.py -> tools -> autocode -> modules -> repo_root
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.autocode.coder import EnhancedCPTCoder


DEFAULT_OUTPUT = Path("analysis/synthetic_notes_eval.txt")
DEFAULT_DETAILED = Path("analysis/synthetic_notes_eval_detailed.txt")
DEFAULT_DATA = Path("data/synthetic_notes_with_CPT_cleaned.csv")


def parse_codes(raw: object) -> Set[str]:
    """
    Normalize a CSV field to a set of CPT strings without leading '+'.
    Handles comma- or semicolon-separated strings or iterables.
    """
    if raw is None:
        return set()
    if isinstance(raw, float) and pd.isna(raw):
        return set()
    if isinstance(raw, (list, tuple, set)):
        iterable: Iterable[str] = (str(x) for x in raw)
    else:
        iterable = str(raw).replace(";", ",").split(",")
    return {item.strip().lstrip("+") for item in iterable if item.strip()}


def load_truth_codes(row: pd.Series) -> Set[str]:
    """
    Prefer the cleaned column when available, fall back to the raw verified column,
    and as a last resort use codes_list.
    """
    for field in ("verified_cpt_codes_clean", "verified_cpt_codes", "codes_list"):
        if field in row and pd.notna(row[field]):
            codes = parse_codes(row[field])
            if codes:
                return codes
    return set()


def evaluate(
    data_path: Path,
    output_path: Path,
    coder: EnhancedCPTCoder,
    focus_codes: set[str],
    detailed_output: Path | None = None,
    baseline: Path | None = None,
) -> None:
    df = pd.read_csv(data_path)

    per_code = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    exact_matches = 0
    total = 0
    fp_counter: Counter[str] = Counter()
    fn_counter: Counter[str] = Counter()

    for _, row in df.iterrows():
        note_text = row.get("note_text", "")
        truth = load_truth_codes(row)

        result = coder.code_procedure(
            {"note_text": note_text, "locality": "00", "setting": "facility"}
        )
        predicted = {c.get("cpt", "").lstrip("+") for c in result.get("codes", []) if c.get("cpt")}

        if predicted == truth:
            exact_matches += 1
        total += 1

        # tallies
        for code in predicted:
            if code in truth:
                per_code[code]["tp"] += 1
            else:
                per_code[code]["fp"] += 1
                fp_counter[code] += 1
        for code in truth:
            if code not in predicted:
                per_code[code]["fn"] += 1
                fn_counter[code] += 1

    lines = []
    lines.append(f"Dataset: {data_path}")
    lines.append(f"Total notes: {total}")
    lines.append(f"Exact match: {exact_matches}/{total} ({exact_matches/total:.1%})")
    lines.append("")
    lines.append("Per-code metrics (precision / recall / F1):")

    all_codes = set(per_code.keys()) | focus_codes
    per_code_rows = []
    for code in sorted(all_codes):
        stats = per_code[code]
        tp, fp, fn = stats["tp"], stats["fp"], stats["fn"]
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
        support = tp + fn
        per_code_rows.append(
            {
                "code": code,
                "support": support,
                "precision": prec,
                "recall": rec,
                "f1": f1,
                "fp": fp,
                "fn": fn,
            }
        )
        lines.append(
            f"- {code}: support={support}, precision={prec:.2f}, recall={rec:.2f}, f1={f1:.2f}, fp={fp}, fn={fn}"
        )

    lines.append("")
    lines.append("Top false-positive codes:")
    for code, count in fp_counter.most_common(5):
        lines.append(f"- {code}: {count} FP")

    lines.append("")
    lines.append("Top false-negative codes:")
    for code, count in fn_counter.most_common(5):
        lines.append(f"- {code}: {count} FN")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))
    print(f"Wrote evaluation report to {output_path}")

    if detailed_output:
        sorted_rows = sorted(
            per_code_rows,
            key=lambda r: (r["precision"], -r["support"]),
        )
        focus_set = {"31627", "31631", "31652", "31653", "31654"}

        det_lines = []
        det_lines.append(f"Dataset: {data_path}")
        det_lines.append("Per-code metrics sorted by lowest precision then highest support:")
        det_lines.append("code | support | precision | recall | f1 | fp | fn")
        for row in sorted_rows:
            det_lines.append(
                f"{row['code']} | {row['support']} | {row['precision']:.2f} | {row['recall']:.2f} | {row['f1']:.2f} | {row['fp']} | {row['fn']}"
            )

        det_lines.append("")
        det_lines.append("Focus codes (nav/stent/EBUS):")
        for row in sorted_rows:
            if row["code"] in focus_set:
                det_lines.append(
                    f"{row['code']}: support={row['support']}, precision={row['precision']:.2f}, recall={row['recall']:.2f}, f1={row['f1']:.2f}, fp={row['fp']}, fn={row['fn']}"
                )

        if baseline and baseline.exists():
            det_lines.append("")
            det_lines.append(f"Comparison vs baseline ({baseline}):")
            baseline_metrics = parse_baseline(baseline)
            for code in sorted(focus_set):
                current = next((r for r in per_code_rows if r["code"] == code), None)
                prior = baseline_metrics.get(code)
                if not current or not prior:
                    continue
                det_lines.append(
                    f"{code}: precision {prior['precision']:.2f} -> {current['precision']:.2f} (Δ {current['precision']-prior['precision']:+.2f}), "
                    f"recall {prior['recall']:.2f} -> {current['recall']:.2f} (Δ {current['recall']-prior['recall']:+.2f})"
                )

        detailed_output.parent.mkdir(parents=True, exist_ok=True)
        detailed_output.write_text("\n".join(det_lines))
        print(f"Wrote detailed report to {detailed_output}")


def parse_baseline(path: Path) -> dict[str, dict[str, float]]:
    """
    Parse baseline metrics from a prior eval report that includes
    lines formatted like:
    - 31627: support=27, precision=0.17, recall=1.00, f1=0.29, fp=132, fn=0
    """
    metrics: dict[str, dict[str, float]] = {}
    if not path.exists():
        return metrics
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        try:
            code_part, rest = line[2:].split(":", 1)
            parts = rest.split(",")
            parsed = {}
            for p in parts:
                if "=" not in p:
                    continue
                key, val = p.strip().split("=", 1)
                try:
                    parsed[key] = float(val)
                except ValueError:
                    continue
            if parsed:
                metrics[code_part.strip()] = parsed
        except ValueError:
            continue
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate EnhancedCPTCoder on synthetic notes.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Path to synthetic notes CSV")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to write evaluation summary report",
    )
    parser.add_argument(
        "--detailed-output",
        type=Path,
        default=DEFAULT_DETAILED,
        help="Path to write detailed per-code metrics",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Optional baseline report to compare focus-code precision/recall deltas",
    )
    args = parser.parse_args()

    focus_codes = {
        "31641",
        "31628",
        "31630",
        "31652",
        "31653",
        "31624",
        "31623",
        "31645",
        "32550",
        "32555",
        "32602",
    }

    coder = EnhancedCPTCoder()
    evaluate(
        args.data,
        args.output,
        coder,
        focus_codes,
        detailed_output=args.detailed_output,
        baseline=args.baseline,
    )


if __name__ == "__main__":
    main()
