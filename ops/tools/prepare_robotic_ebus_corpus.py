#!/usr/bin/env python3
"""Inventory synthetic sources, bind renditions, and freeze leakage-aware splits.

This script never reads clinical/national stores. Generator metadata is retained
separately from document text, and is not automatically treated as a gold label.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import random
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
TEXT_KEYS = ("full_report_messy", "messy_report_text", "report_text", "full_report")
CLEAN_KEYS = ("clean_report_text", "full_report_clean")
MAX_MEMBER = 20_000_000


def sha(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def normalized(text):
    return re.sub(r"\s+", " ", text).strip().casefold()


def clinical_fingerprint(text):
    # Conservative grouping across cosmetic identifiers and platform swaps.
    text = normalized(text)
    text = re.sub(
        r"\b(?:ion|monarch|galaxy|noah|shape.sensing|electromagnetic)\b", " PLATFORM ", text
    )
    text = re.sub(r"\b(?:syn|ng|monarch|ion|lebus)[-_a-z]*[-_]\d+\b", " CASE ", text)
    return sha(re.sub(r"[^a-z0-9]+", " ", text).strip())


class Groups:
    def __init__(self):
        self.parent = {}

    def root(self, value):
        self.parent.setdefault(value, value)
        if self.parent[value] != value:
            self.parent[value] = self.root(self.parent[value])
        return self.parent[value]

    def join(self, left, right):
        a, b = self.root(left), self.root(right)
        self.parent[max(a, b)] = min(a, b)


def prepare(source, output, seed=20260914, overlap_paths=()):
    if output.exists() and (output / "split_manifest.json").exists():
        raise ValueError("Frozen corpus exists; use a new versioned output directory")
    inventory, documents, errors = [], [], []
    groups = Groups()
    seen_bytes, seen_text = {}, {}

    def add(text, locator, metadata=None, family=None, clean=None, regression=False):
        text = text.strip()
        if len(text) < 80:
            return
        digest = sha(text)
        identity = "doc:" + digest
        groups.root(identity)
        key = sha(normalized(text))
        for anchor in [
            "text:" + key,
            "scenario:" + clinical_fingerprint(text),
            family,
            "text:" + sha(normalized(clean)) if clean else None,
        ]:
            if anchor:
                groups.join(identity, anchor)
        if digest in seen_text:
            existing = documents[seen_text[digest]]
            existing["sources"].append(locator)
            existing["prior_training_overlap"] |= regression
            if metadata:
                existing["generator_metadata"].update(metadata)
            return
        seen_text[digest] = len(documents)
        platform = "linear_ebus"
        for name in ("Ion", "Monarch", "Galaxy"):
            if re.search(r"\b" + name + r"\b", text, re.I):
                platform = name
                break
        documents.append(
            {
                "document_id": digest[:24],
                "text_sha256": digest,
                "text": text,
                "sources": [locator],
                "family_anchor": family,
                "group_key": identity,
                "platform": platform,
                "generator_metadata": metadata or {},
                "annotation_status": "requires_evidence_review",
                "prior_training_overlap": regression,
            }
        )

    def parse(name, raw):
        digest = sha(raw)
        inventory.append(
            {
                "source": name,
                "bytes": len(raw),
                "sha256": digest,
                "format": Path(name).suffix.lower(),
            }
        )
        if digest in seen_bytes:
            inventory[-1]["duplicate_of"] = seen_bytes[digest]
            return
        seen_bytes[digest] = name
        suffix = Path(name).suffix.lower()
        try:
            if suffix == ".jsonl":
                for number, line in enumerate(raw.decode("utf-8-sig").splitlines(), 1):
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    text = next((row[k] for k in TEXT_KEYS if isinstance(row.get(k), str)), None)
                    if not text:
                        continue
                    parent = (
                        row.get("paired_clean_report_id")
                        or row.get("source_clean_report_id")
                        or row.get("case_id")
                        or row.get("report_id")
                    )
                    clean = next((row[k] for k in CLEAN_KEYS if isinstance(row.get(k), str)), None)
                    meta = {
                        k: v
                        for k, v in row.items()
                        if k not in TEXT_KEYS + CLEAN_KEYS and k != "noise_transformations"
                    }
                    add(
                        text,
                        f"{name}#L{number}",
                        meta,
                        "case:" + str(parent) if parent else None,
                        clean,
                    )
            elif suffix in {".txt", ".md"}:
                text = raw.decode("utf-8-sig", errors="replace")
                blocks = list(
                    re.finditer(
                        r"<<<NOTE ([^>]+)>>>.*?<<<BEGIN ORIGINAL NOTE TEXT>>>\s*(.*?)\s*<<<END ORIGINAL NOTE TEXT>>>",
                        text,
                        re.S,
                    )
                )
                if blocks:
                    for m in blocks:
                        add(
                            m.group(2),
                            name + "#" + m.group(1),
                            family="legacy:" + m.group(1),
                            regression=True,
                        )
                elif "individual_reports" in name:
                    add(text, name)
                # Markdown aggregate copies remain inventoried, never treated as one case.
            elif suffix == ".pdf":
                from pypdf import PdfReader

                reader = PdfReader(io.BytesIO(raw))
                inventory[-1]["pages"] = len(reader.pages)
                inventory[-1]["browser_pdf_validation"] = "pending"
                if "combined" in name.lower():
                    inventory[-1]["role"] = "multi_case_container"
                    return
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                if not text.strip():
                    inventory[-1]["requires_browser_ocr"] = True
                    return
                # Known multi-platform PDF series reuse the same case scenario.
                match = re.search(r"_(\d{2})\.pdf$", name, re.I)
                family = (
                    ("pdf_ebus:" if "ebus" in name.lower() else "pdf_robotic:")
                    + match.group(1).zfill(2)
                    if match
                    else None
                )
                add(text, name, family=family)
        except (ValueError, KeyError, UnicodeError, OSError) as exc:
            errors.append({"source": name, "error": type(exc).__name__})

    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        name = path.relative_to(source).as_posix()
        if path.suffix.lower() == ".zip":
            inventory.append(
                {
                    "source": name,
                    "bytes": path.stat().st_size,
                    "sha256": sha(path.read_bytes()),
                    "format": ".zip",
                }
            )
            with zipfile.ZipFile(path) as archive:
                for member in sorted(archive.infolist(), key=lambda m: m.filename):
                    if member.is_dir() or member.filename.startswith("__MACOSX/"):
                        continue
                    if member.file_size > MAX_MEMBER:
                        errors.append(
                            {"source": name + "!" + member.filename, "error": "member_size_limit"}
                        )
                        continue
                    if Path(member.filename).suffix.lower() in {
                        ".jsonl",
                        ".txt",
                        ".md",
                        ".pdf",
                        ".csv",
                        ".json",
                    }:
                        parse(name + "!" + member.filename, archive.read(member))
        elif path.stat().st_size <= MAX_MEMBER:
            parse(name, path.read_bytes())

    overlap_hashes = set()
    overlap_scanned = 0
    for directory in overlap_paths:
        paths = [directory] if directory.is_file() else directory.rglob("*.jsonl")
        for path in paths:
            if "robotic_ebus_v1" in path.parts:
                continue  # Do not audit a prepared rendition against its own source.
            if path.stat().st_size > 400_000_000:
                continue
            overlap_scanned += 1
            try:
                with path.open() as handle:
                    for line in handle:
                        try:
                            row = json.loads(line)
                        except ValueError:
                            continue
                        for key in (*TEXT_KEYS, *CLEAN_KEYS, "note", "note_text", "text"):
                            if isinstance(row.get(key), str):
                                overlap_hashes.add(sha(normalized(row[key])))
            except (UnicodeError, OSError):
                errors.append({"source": path.name, "error": "overlap_read_failed"})
    families = defaultdict(list)
    for row in documents:
        row["family_id"] = sha(groups.root(row.pop("group_key")))[:24]
        row["prior_training_overlap"] |= sha(normalized(row["text"])) in overlap_hashes
        families[row["family_id"]].append(row)
    rng = random.Random(seed)
    strata = defaultdict(list)
    for family, rows in families.items():
        if any(r["prior_training_overlap"] for r in rows):
            for row in rows:
                row["split"] = "regression"
        else:
            strata[rows[0]["platform"]].append(family)
    total = sum(len(names) for names in strata.values())
    quotas = {key: [int(len(names) * 0.7), int(len(names) * 0.15)] for key, names in strata.items()}
    for column, ratio in enumerate((0.7, 0.15)):
        remainder = round(total * ratio) - sum(q[column] for q in quotas.values())
        order = sorted(
            strata, key=lambda key: (-(len(strata[key]) * ratio - quotas[key][column]), key)
        )
        for key in order[:remainder]:
            quotas[key][column] += 1
    for key, names in sorted(strata.items()):
        names.sort()
        rng.shuffle(names)
        n_train, n_validation = quotas[key]
        for i, name in enumerate(names):
            split = (
                "train" if i < n_train else "validation" if i < n_train + n_validation else "test"
            )
            for row in families[name]:
                row["split"] = split
    output.mkdir(parents=True, exist_ok=True)
    for split in ("train", "validation", "test", "regression"):
        (output / (split + ".jsonl")).write_text(
            "".join(
                json.dumps(row, ensure_ascii=False) + "\n"
                for row in documents
                if row["split"] == split
            )
        )
    (output / "inventory.json").write_text(
        json.dumps({"files": inventory, "errors": errors}, indent=2) + "\n"
    )
    manifest = {
        "version": "0.2.0",
        "profile": "robotic_ebus_v1",
        "seed": seed,
        "ratios": [0.7, 0.15, 0.15],
        "documents": len(documents),
        "case_families": len(families),
        "document_counts": dict(Counter(r["split"] for r in documents)),
        "family_counts": dict(Counter(rows[0]["split"] for rows in families.values())),
        "splits": {family: rows[0]["split"] for family, rows in sorted(families.items())},
        "overlap_files_scanned": overlap_scanned,
        "annotation_status": "requires_evidence_review",
        "legacy_case_policy": "regression_only_due_to_prior_training_risk",
        "archive_errors": errors,
        "inventory_sha256": sha((output / "inventory.json").read_bytes()),
        "artifacts": {
            split + ".jsonl": sha((output / (split + ".jsonl")).read_bytes())
            for split in ("train", "validation", "test", "regression")
        },
    }
    (output / "split_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: v
                for k, v in manifest.items()
                if k not in {"splits", "artifacts", "archive_errors"}
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=20260914)
    parser.add_argument("--overlap", type=Path, action="append", default=[])
    args = parser.parse_args()
    prepare(args.source, args.output, args.seed, args.overlap)
