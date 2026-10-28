#!/usr/bin/env python3
# ruff: noqa: E402 -- Bootstrap the isolated package without installing the development application.
"""Export only offline inference assets, preserving development checkpoints."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT / "packages/ip_registry_engine/src"),
    str(ROOT / "packages/ip_registry_contracts/src"),
]
from ip_registry_engine.local_ner import LABELS


def build(checkpoint, annotations, destination):
    if destination.exists():
        raise ValueError("Model candidate already exists; use a new version")
    annotation = json.loads(annotations.read_text())
    if annotation.get("review_status") not in {"lexical_concordance_reviewed", "adjudicated"}:
        raise ValueError("Annotation review is required before packaging")
    destination.mkdir(parents=True)
    for name in (
        "config.json",
        "model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "vocab.txt",
        "label_map.json",
    ):
        path = checkpoint / name
        if path.is_file():
            shutil.copyfile(path, destination / name)
    manifest = {
        "format": 1,
        "registry_profile": "robotic_ebus_v1",
        "engine_version": "0.2.0",
        "labels": LABELS,
        "clinical_qualification": "pending",
        "acceptance_status": "independent_field_evaluation_required",
        "annotation_method": annotation["annotation_method"],
        "independent_gold": annotation["independent_gold"],
        "training_manifest_sha256": hashlib.sha256(annotations.read_bytes()).hexdigest(),
        "corpus_manifest_sha256": annotation["corpus_manifest_sha256"],
        "base_model": annotation["base_model"],
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "training_split": "train",
        "selection_split": "validation",
        "heldout_split": "test",
        "files": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in destination.iterdir()
            if p.is_file()
        },
    }
    (destination / "focused-model-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {
                "model_candidate": str(destination),
                "clinical_qualification": "pending",
                "assets": len(manifest["files"]),
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.checkpoint, args.annotations, args.output)
