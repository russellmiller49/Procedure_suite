#!/usr/bin/env python3
# ruff: noqa: E402 -- Bootstrap the isolated package without installing the development application.
"""Source-verified weak annotation proposals, never independent gold evidence.

The concordance must be reviewed before training. These three lexical labels retain
the existing ontology; target links, assertion, axes and outcomes need field review.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT / "packages/ip_registry_engine/src"),
    str(ROOT / "packages/ip_registry_contracts/src"),
]
from ip_registry_engine.focused import prepare_text

PATTERNS = {
    "ANAT_LN_STATION": r"\b(?:station|stn|staion)\s*(?P<entity>(?:2|4|10|11|12)[RL]|3[AP]|[5-9])\b",
    "PROC_ACTION": r"\b(?P<entity>sampled|performed|advanced|navigated|aborted|repositioned|redirected|docked|introduced|obtained|biopsied)\b",
    "OBS_ROSE": r"\b(?P<entity>ROSE|rapid on[- ]site evaluation)\b",
}


def prepare(corpus, output, model):
    from transformers import AutoTokenizer

    if output.exists():
        raise ValueError("Use a new annotation version; do not overwrite reviewed spans")
    output.mkdir(parents=True)
    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True, trust_remote_code=False)
    concordance = {key: {} for key in PATTERNS}
    inventory = {}
    for split in ("train", "validation", "test", "regression"):
        annotations = []
        bio = []
        for line in (corpus / (split + ".jsonl")).read_text().splitlines():
            row = json.loads(line)
            text = row["text"]
            masked = prepare_text(text)
            spans = []
            for label, pattern in PATTERNS.items():
                for match in re.finditer(pattern, masked, re.I):
                    start, end = match.span("entity")
                    spans.append(
                        {"start": start, "end": end, "text": text[start:end], "label": label}
                    )
                    surface = text[start:end]
                    concordance[label][surface] = concordance[label].get(surface, 0) + 1
            annotations.append(
                {
                    "document_id": row["document_id"],
                    "family_id": row["family_id"],
                    "source_sha256": row["text_sha256"],
                    "split": split,
                    "spans": spans,
                    "annotation_status": "source_verified_weak_labels",
                    "review_status": "pending_concordance_review",
                    "excluded_labels": [
                        "hidden_outcomes",
                        "target_relationships",
                        "assertion",
                        "clinical_adequacy",
                    ],
                }
            )
            # Test/regression labels never enter model fitting or selection.
            if split not in {"train", "validation"}:
                continue
            encoded = tokenizer(masked, add_special_tokens=False, return_offsets_mapping=True)
            offsets = encoded["offset_mapping"]
            tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"])
            tags = ["O"] * len(tokens)
            for span in spans:
                indices = [
                    i
                    for i, (start, end) in enumerate(offsets)
                    if end > start and start >= span["start"] and end <= span["end"]
                ]
                for j, index in enumerate(indices):
                    tags[index] = ("B-" if j == 0 else "I-") + span["label"]
            for start in range(0, len(tokens), 240):
                bio.append(
                    {
                        "id": row["document_id"] + ":" + str(start),
                        "family_id": row["family_id"],
                        "tokens": tokens[start : start + 240],
                        "ner_tags": tags[start : start + 240],
                        "annotation_status": "source_verified_weak_labels",
                    }
                )
        (output / (split + ".spans.jsonl")).write_text(
            "".join(json.dumps(row) + "\n" for row in annotations)
        )
        if bio:
            (output / (split + ".bio.jsonl")).write_text(
                "".join(json.dumps(row) + "\n" for row in bio)
            )
        inventory[split] = {"documents": len(annotations), "chunks": len(bio)}
    manifest = {
        "version": "0.2.0",
        "profile": "robotic_ebus_v1",
        "base_model": model,
        "synthetic_only": True,
        "clinical_reviewed": False,
        "annotation_method": "source_verified_lexical_weak_labels",
        "independent_gold": False,
        "review_status": "pending_concordance_review",
        "corpus_manifest_sha256": hashlib.sha256(
            (corpus / "split_manifest.json").read_bytes()
        ).hexdigest(),
        "inventory": inventory,
        "concordance": concordance,
        "files": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob("*.jsonl")
        },
    }
    (output / "annotation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--model", default="microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext"
    )
    args = parser.parse_args()
    prepare(args.corpus, args.output, args.model)
