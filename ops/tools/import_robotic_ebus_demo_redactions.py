#!/usr/bin/env python3
"""Record the redacted text the real browser redactor produces for each demo sample.

    python ops/tools/import_robotic_ebus_demo_redactions.py --capture capture.json --worker module

The demo serves stored results only for these exact texts, so they must come
from the redactor in a browser, not from Python. Capture them on the demo page
(``ops/tools/run_robotic_ebus_demo.py``): for each sample run detection, note the
detected spans, apply, and hash the redacted text. ``capture.json`` is a list of
``{"id", "spans": [[start, end], ...], "original_sha", "redacted_sha"}``.

This tool re-applies the spans to the stored sample text with the same rule the
page uses (merge overlaps, one fixed placeholder) and refuses to write unless
both hashes match what the browser reported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "data/knowledge/robotic_ebus_v1/demo"
PLACEHOLDER = "[REDACTED]"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _normalise(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip()


def apply(text: str, spans: list[list[int]]) -> str:
    merged: list[list[int]] = []
    for start, end in sorted(s for s in spans if 0 <= s[0] < s[1] <= len(text)):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    for start, end in reversed(merged):
        text = text[:start] + PLACEHOLDER + text[end:]
    return text


def redacts(source: str, variant: dict) -> bool:
    """True when the variant is ``source`` with passages replaced by the placeholder."""
    position = 0
    for fragment in variant["text"].split(PLACEHOLDER):
        found = source.find(fragment, position)
        if found < 0:
            return False
        position = found + len(fragment)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--worker", required=True, choices=["module", "legacy"])
    args = parser.parse_args()

    samples = {s["id"]: s for s in json.loads((DEMO_DIR / "samples.json").read_text())["samples"]}
    target = DEMO_DIR / "redactions.json"
    data = json.loads(target.read_text()) if target.exists() else {"version": 1, "redactions": {}}
    redactions: dict[str, list[dict]] = data["redactions"]
    for item in json.loads(args.capture.read_text()):
        sample = samples[item["id"]]
        if _sha(sample["text"]) != item["original_sha"]:
            raise SystemExit(f"{item['id']}: the browser scanned a different sample text")
        redacted = _normalise(apply(sample["text"], item["spans"]))
        digest = _sha(redacted)
        if digest != item["redacted_sha"]:
            raise SystemExit(f"{item['id']}: redacted text does not match the browser's")
        variants = [v for v in redactions.get(item["id"], []) if v["sha256"] != digest]
        same = [v for v in redactions.get(item["id"], []) if v["sha256"] == digest]
        workers = sorted({args.worker, *(w for v in same for w in v["worker"].split("+"))})
        entry = {"worker": "+".join(workers), "sha256": digest, "text": redacted}
        # The module worker is what most browsers run, so its text is listed first.
        redactions[item["id"]] = [entry, *variants] if "module" in workers else [*variants, entry]
        print(f"{item['id']:44s} {entry['worker']:14s} {len(item['spans'])} span(s)")
    # Drop samples that no longer exist and variants recorded from an earlier sample text.
    for sample_id in list(redactions):
        if sample_id not in samples:
            del redactions[sample_id]
            continue
        current = [v for v in redactions[sample_id] if redacts(samples[sample_id]["text"], v)]
        for stale in (v for v in redactions[sample_id] if v not in current):
            print(f"{sample_id:44s} dropped a variant of an earlier text ({stale['sha256'][:10]})")
        redactions[sample_id] = current
    target.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    print(f"wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
