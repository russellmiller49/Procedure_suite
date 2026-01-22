#!/usr/bin/env python3
"""Clean existing distilled PHI JSONL by removing obvious false positives."""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from scripts.distill_phi_labels import (
    DEGREE_SYMBOL,
    LABEL_MAPPING_STANDARD,
    line_bounds,
    normalize_entity_group,
    repair_bio,
    wipe_cpt_subword_labels,
    wipe_ln_station_labels,
)

logger = logging.getLogger("clean_distilled_phi")


def _load_tokenizer(name_or_path: str):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(name_or_path)


def _span_text(text: str, start: int, end: int) -> str:
    if not text:
        return ""
    start = max(0, min(start, len(text)))
    end = max(start, min(end, len(text)))
    return text[start:end]


def _line_text(text: str, idx: int) -> str:
    start, end = line_bounds(text, idx)
    return text[start:end]


def _looks_like_temp(span_text: str, line_text: str) -> bool:
    if re.fullmatch(r"\d{2,3}(?:\.\d+)?\s*[cCfF]", span_text.strip()):
        return True
    line_lower = line_text.lower()
    if any(token in line_lower for token in ("temp", "temperature", "degrees")):
        return True
    if DEGREE_SYMBOL in line_text:
        return True
    return False


def _iter_entities(ner_tags: list[str], offsets: list[tuple[int, int]]) -> list[tuple[int, int, str]]:
    entities: list[tuple[int, int, str]] = []
    current_label = None
    start_idx = None
    end_idx = None
    for idx, tag in enumerate(ner_tags):
        if tag == "O":
            if current_label is not None:
                entities.append((start_idx, end_idx, current_label))
                current_label = None
                start_idx = None
                end_idx = None
            continue
        if tag.startswith("B-"):
            if current_label is not None:
                entities.append((start_idx, end_idx, current_label))
            current_label = tag[2:]
            start_idx = idx
            end_idx = idx
            continue
        if tag.startswith("I-"):
            label = tag[2:]
            if current_label == label and start_idx is not None:
                end_idx = idx
            else:
                if current_label is not None:
                    entities.append((start_idx, end_idx, current_label))
                current_label = label
                start_idx = idx
                end_idx = idx
    if current_label is not None:
        entities.append((start_idx, end_idx, current_label))
    return entities


def _apply_refinery_to_tags(
    text: str,
    tokens: list[str],
    offsets: list[tuple[int, int]],
    ner_tags: list[str],
    *,
    drop_zipcode_if_cpt: bool,
    drop_buildingnum_if_temp: bool,
) -> list[str]:
    cleaned = list(ner_tags)
    entities = _iter_entities(cleaned, offsets)
    for start_idx, end_idx, label in entities:
        if start_idx is None or end_idx is None:
            continue
        span_start = offsets[start_idx][0]
        span_end = offsets[end_idx][1]
        span_text = _span_text(text, span_start, span_end)
        line_text = _line_text(text, span_start)
        label_upper = label.upper()
        if drop_zipcode_if_cpt and label_upper in {"ZIPCODE", "GEO"}:
            if re.fullmatch(r"\d{5}", span_text.strip()):
                if re.search(r"\bCPT\b", line_text, re.IGNORECASE):
                    for idx in range(start_idx, end_idx + 1):
                        cleaned[idx] = "O"
                elif re.search(r"\bCODE\b", line_text, re.IGNORECASE) and not re.search(
                    r"\bZIP\s+CODE\b",
                    line_text,
                    re.IGNORECASE,
                ):
                    for idx in range(start_idx, end_idx + 1):
                        cleaned[idx] = "O"
        if drop_buildingnum_if_temp and label_upper in {"BUILDINGNUM", "GEO"}:
            span_end = offsets[end_idx][1]
            tail = text[span_end : min(len(text), span_end + 4)]
            if _looks_like_temp(span_text, line_text) or re.match(
                rf"\s*(?:{DEGREE_SYMBOL}\s*)?[cCfF](?![a-zA-Z])",
                tail,
            ):
                for idx in range(start_idx, end_idx + 1):
                    cleaned[idx] = "O"
    return cleaned


def _normalize_ner_tags(ner_tags: list[str], schema: str, provider_label: str) -> list[str]:
    if schema != "standard":
        return ner_tags
    normalized = []
    for tag in ner_tags:
        if tag == "O":
            normalized.append(tag)
            continue
        prefix, label = tag.split("-", 1)
        mapped = normalize_entity_group(label, schema, provider_label)
        normalized.append(f"{prefix}-{mapped}")
    return normalized


def _tokenize_for_offsets(text: str, tokenizer, max_length: int | None = None):
    encoded = tokenizer(
        text,
        return_offsets_mapping=True,
        truncation=True,
        max_length=max_length,
    )
    tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"])
    offsets = [tuple(pair) for pair in encoded.get("offset_mapping", [])]
    filtered_tokens = []
    filtered_offsets = []
    for token, (start, end) in zip(tokens, offsets):
        if start == end:
            continue
        filtered_tokens.append(token)
        filtered_offsets.append((start, end))
    return filtered_tokens, filtered_offsets


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean distilled PHI JSONL output")
    parser.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=Path("data/ml_training/distilled_phi_labels.jsonl"),
    )
    parser.add_argument(
        "--out",
        dest="out_path",
        type=Path,
        default=Path("data/ml_training/distilled_phi_labels.cleaned.jsonl"),
    )
    parser.add_argument("--student-tokenizer", type=str, default="distilbert-base-uncased")
    parser.add_argument("--label-schema", choices=["teacher", "standard"], default="standard")
    parser.add_argument(
        "--drop-zipcode-if-cpt",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--drop-buildingnum-if-temp",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--provider-label", type=str, default="PROVIDER")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    tokenizer = _load_tokenizer(args.student_tokenizer)

    cleaned_count = 0
    total = 0
    args.out_path.parent.mkdir(parents=True, exist_ok=True)

    with args.in_path.open("r", encoding="utf-8") as in_f, args.out_path.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            line = line.strip()
            if not line:
                continue
            total += 1
            record = json.loads(line)
            text = record.get("text", "")
            tokens = record.get("tokens", [])
            ner_tags = record.get("ner_tags", [])
            offsets = record.get("offsets") or record.get("offset_mapping")

            if not text or not tokens or not ner_tags:
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                continue

            if offsets is None:
                tok_tokens, tok_offsets = _tokenize_for_offsets(
                    text,
                    tokenizer,
                    max_length=len(tokens) + 2,
                )
                if tok_tokens != tokens:
                    logger.warning("Token mismatch; skipping refinery for record %s", record.get("id"))
                    cleaned_tags = _normalize_ner_tags(ner_tags, args.label_schema, args.provider_label)
                    record["ner_tags"] = cleaned_tags
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    continue
                offsets = tok_offsets

            cleaned_tags = _apply_refinery_to_tags(
                text,
                tokens,
                offsets,
                ner_tags,
                drop_zipcode_if_cpt=args.drop_zipcode_if_cpt,
                drop_buildingnum_if_temp=args.drop_buildingnum_if_temp,
            )
            cleaned_tags = _normalize_ner_tags(cleaned_tags, args.label_schema, args.provider_label)
            cleaned_tags = wipe_cpt_subword_labels(
                tokens,
                cleaned_tags,
                text=text,
                offsets=offsets,
            )
            cleaned_tags = wipe_ln_station_labels(tokens, cleaned_tags)
            cleaned_tags = repair_bio(cleaned_tags)

            if cleaned_tags != ner_tags:
                cleaned_count += 1
            record["ner_tags"] = cleaned_tags
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("Processed %s records", total)
    logger.info("Cleaned %s records", cleaned_count)
    logger.info("Output: %s", args.out_path)
    logger.info("Label schema: %s", args.label_schema)
    if args.label_schema == "standard":
        logger.info("Standard label mapping keys: %s", sorted(LABEL_MAPPING_STANDARD))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
