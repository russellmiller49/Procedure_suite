#!/usr/bin/env python3
"""
Patch a training JSONL file using audit violations, turning offending spans into "O".
"""

import argparse
import json
from typing import Any, Dict, Iterable, List, Tuple


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-in", default="data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl")
    ap.add_argument("--audit-report", default="artifacts/phi_distilbert_ner/audit_report.json")
    ap.add_argument("--data-out", default="data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl")
    return ap


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    return build_arg_parser().parse_args(argv)


def resolve_record_id(row: Dict[str, Any], fallback: int) -> str:
    record_id = row.get("id") or row.get("id_base") or row.get("record_index") or fallback
    return str(record_id)


def load_patches(report_path: str) -> Dict[str, List[Tuple[int, int, str]]]:
    with open(report_path, "r") as f:
        report = json.load(f)
    patches: Dict[str, List[Tuple[int, int, str]]] = {}
    for ex in report.get("examples", []):
        record_id = str(ex.get("id", ""))
        if not record_id:
            continue
        token_index = int(ex.get("token_index", 0))
        span_len = int(ex.get("span_len", 1))
        kind = str(ex.get("type", "unknown"))
        patches.setdefault(record_id, []).append((token_index, span_len, kind))
    return patches


def iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main() -> None:
    args = parse_args()
    patches = load_patches(args.audit_report)
    if not patches:
        raise RuntimeError(f"No examples found in audit report: {args.audit_report}")

    modified_records = 0
    modified_spans = 0
    skipped_spans = 0
    modified_by_type: Dict[str, int] = {}

    with open(args.data_out, "w") as fout:
        for idx, row in enumerate(iter_jsonl(args.data_in)):
            record_id = resolve_record_id(row, idx)
            spans = patches.get(record_id, [])
            if spans:
                tags = row.get("ner_tags") or []
                if not isinstance(tags, list):
                    tags = []
                before = list(tags)
                for token_index, span_len, kind in spans:
                    if token_index < 0 or token_index >= len(tags):
                        skipped_spans += 1
                        continue
                    end = min(len(tags), token_index + max(span_len, 1))
                    for i in range(token_index, end):
                        tags[i] = "O"
                    modified_spans += 1
                    modified_by_type[kind] = modified_by_type.get(kind, 0) + 1
                if tags != before:
                    modified_records += 1
                row["ner_tags"] = tags
            fout.write(json.dumps(row) + "\n")

    print(f"Patched records: {modified_records}")
    print(f"Patched spans: {modified_spans}")
    if skipped_spans:
        print(f"Skipped spans (out of range): {skipped_spans}")
    print(f"Patched by type: {modified_by_type}")


if __name__ == "__main__":
    main()
