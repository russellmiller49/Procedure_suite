#!/usr/bin/env python3
"""Post-hoc label normalization for silver PHI distillation output.

Goal: map a potentially-granular (and occasionally noisy) label schema into a small,
stable client-training schema:

- PATIENT
- DATE
- GEO
- ID
- CONTACT
- O
"""

from __future__ import annotations

import argparse
import json
import logging
from collections import Counter
from pathlib import Path
from typing import Literal

DEFAULT_IN_PATH = Path("data/ml_training/distilled_phi_CLEANED.jsonl")
DEFAULT_OUT_PATH = Path("data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl")

logger = logging.getLogger("normalize_phi_labels")

PasswordPolicy = Literal["id", "drop"]


def get_category(tag: str) -> str:
    if not tag or tag == "O":
        return "O"
    if "-" in tag:
        return tag.split("-", 1)[1]
    return tag


def repair_bio(tags: list[str]) -> list[str]:
    repaired = list(tags)
    for idx, tag in enumerate(repaired):
        if not tag.startswith("I-"):
            continue
        label = get_category(tag)
        if idx == 0:
            repaired[idx] = f"B-{label}"
            continue
        prev_tag = repaired[idx - 1]
        if prev_tag == "O" or get_category(prev_tag) != label:
            repaired[idx] = f"B-{label}"
    return repaired


_DIRECT_CATEGORY_MAP: dict[str, str] = {
    "PATIENT": "PATIENT",
    "GEO": "GEO",
    "STREET": "GEO",
    "DATEOFBIRTH": "DATE",
    "DATE": "DATE",
    "TELEPHONENUM": "CONTACT",
    "EMAIL": "CONTACT",
    "USERNAME": "PATIENT",
    "SOCIALNUM": "ID",
    "DRIVERLICENSENUM": "ID",
    "IDCARDNUM": "ID",
    "ACCOUNTNUM": "ID",
    "TAXNUM": "ID",
}

_OBVIOUS_ID_CATEGORIES: set[str] = {
    "PASSPORT",
    "SSN",
    "MEDICALRECORDNUM",
    "MRN",
    "CREDITCARD",
    "CREDITCARDNUM",
    "BANKACCOUNTNUM",
    "ROUTINGNUM",
    "VIN",
}


def _normalize_category(category: str, *, password_policy: PasswordPolicy) -> str | None:
    category_upper = category.upper()
    if category_upper == "PASSWORD":
        if password_policy == "drop":
            return None
        return "ID"
    if category_upper in _DIRECT_CATEGORY_MAP:
        return _DIRECT_CATEGORY_MAP[category_upper]
    if category_upper in _OBVIOUS_ID_CATEGORIES:
        return "ID"
    if "NUM" in category_upper:
        return "ID"
    return category_upper


def normalize_tags(tags: list[str], *, password_policy: PasswordPolicy = "id") -> tuple[list[str], Counter, Counter, int, int]:
    before = Counter()
    after = Counter()
    password_mapped = 0
    password_dropped = 0

    out: list[str] = []
    for tag in tags:
        if tag == "O":
            out.append(tag)
            continue

        if "-" in tag:
            prefix, category = tag.split("-", 1)
            prefix = prefix.upper()
        else:
            prefix, category = "B", tag

        category_upper = category.upper()
        before[category_upper] += 1

        normalized_category = _normalize_category(category_upper, password_policy=password_policy)
        if normalized_category is None:
            out.append("O")
            password_dropped += 1
            continue

        if category_upper == "PASSWORD" and normalized_category == "ID":
            password_mapped += 1

        after[normalized_category] += 1
        out.append(f"{prefix}-{normalized_category}")

    repaired = repair_bio(out)
    return repaired, before, after, password_mapped, password_dropped


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize silver PHI BIO labels into a small stable schema")
    parser.add_argument("--in", dest="in_path", type=Path, default=DEFAULT_IN_PATH)
    parser.add_argument("--out", dest="out_path", type=Path, default=DEFAULT_OUT_PATH)
    parser.add_argument("--password-policy", choices=("id", "drop"), default="id")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not args.in_path.exists():
        logger.error("Input file does not exist: %s", args.in_path)
        return 1

    lines_processed = 0
    lines_changed = 0
    category_before = Counter()
    category_after = Counter()
    password_mapped = 0
    password_dropped = 0

    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    with args.in_path.open("r", encoding="utf-8") as in_f, args.out_path.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            lines_processed += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                out_f.write(line)
                continue
            if not isinstance(record, dict):
                out_f.write(line)
                continue

            tags = record.get("ner_tags")
            if not isinstance(tags, list):
                out_f.write(line)
                continue

            normalized, before, after, pw_mapped, pw_dropped = normalize_tags(
                tags, password_policy=args.password_policy
            )
            category_before.update(before)
            category_after.update(after)
            password_mapped += pw_mapped
            password_dropped += pw_dropped

            if normalized != tags:
                lines_changed += 1
                record = dict(record)
                record["ner_tags"] = normalized
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Lines processed: %s", lines_processed)
    logger.info("Lines changed: %s", lines_changed)
    logger.info("Password mapped: %s", password_mapped)
    logger.info("Password dropped: %s", password_dropped)
    logger.info("Top categories before: %s", category_before.most_common(20))
    logger.info("Top categories after: %s", category_after.most_common(20))
    logger.info("Output: %s", args.out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

