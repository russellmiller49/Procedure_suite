#!/usr/bin/env python3
# ruff: noqa: E402 -- Put the repository root on sys.path before importing it.
"""Build the synthetic sample notes for the robotic bronchoscopy + EBUS demo page.

    python ops/tools/build_robotic_ebus_demo_samples.py

Writes data/knowledge/robotic_ebus_v1/demo/samples.json. Two notes are
hand-written (the lead case and the sandbox fixture). The rest come from the
truth-first generator with seeds that lie outside every eval corpus, so each
has gold by construction and none of them is an eval document. Output is
deterministic: the same script and seeds give the same file.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "packages/ip_registry_contracts/src"),
    str(ROOT / "packages/ip_registry_engine/src"),
]

from ip_registry_engine.focused import stable_id

from ops.tools.robotic_ebus_truth.build_split import GENERATOR_VERSION, compact
from ops.tools.robotic_ebus_truth.gold import build_gold, plan_statements
from ops.tools.robotic_ebus_truth.scenarios import TRAPS, sample_scenario
from ops.tools.robotic_ebus_truth.template_writer import render
from ops.tools.robotic_ebus_truth.verify import unsupported_values

DEMO_DIR = ROOT / "data/knowledge/robotic_ebus_v1/demo"
CORPORA = ROOT / "data/ml_training/robotic_ebus_v1"
PLACEHOLDER = "[REDACTED]"
# The generator's all-caps title line trips the browser redactor's name detector
# ("SYNTHETIC TRAINING" is flagged as a patient name). The demo samples carry this
# header instead; evidence offsets are shifted to match.
GENERATOR_HEADER = "SYNTHETIC TRAINING NOTE - NOT FOR CLINICAL USE"
DEMO_HEADER = "Synthetic note for software demonstration only; no real patient."

HANDWRITTEN = [
    {
        "id": "lead-combined-4r-7-11l",
        "path": DEMO_DIR / "lead_case.txt",
        "title": "Combined case: lung nodule biopsy, 4R and 7 sampled, 11L surveyed",
        "teaching_point": (
            "One peripheral target sampled with two tools, two nodal stations sampled and a "
            "third only surveyed. The surveyed station must not count as sampled."
        ),
        "platform": "Ion",
        "components": ["robotic_bronchoscopy", "linear_ebus"],
        "style": "handwritten",
        "traps": ["surveyed_not_sampled"],
        "expected": {
            "stations_sampled": ["4R", "7"],
            "stations_surveyed_only": ["11L"],
            "codes": ["31627", "31628", "31629", "31652", "31654"],
        },
    },
    {
        "id": "sandbox-monarch-7-sampled-4r-not",
        "path": ROOT / "tests/fixtures/registry_workbench/rebus_demo_procedure.txt",
        "title": "Monarch case with cone-beam CT confirmation and one station not sampled",
        "teaching_point": (
            "Tool-in-lesion is confirmed by cone-beam CT, pass counts are aggregate, and "
            "station 4R is seen but not sampled for a stated reason."
        ),
        "platform": "Monarch",
        "components": ["robotic_bronchoscopy", "linear_ebus"],
        "style": "handwritten",
        "traps": ["surveyed_not_sampled"],
        "expected": {
            "stations_sampled": ["7"],
            "stations_surveyed_only": ["4R"],
            "codes": ["31627", "31629", "31652", "31654"],
        },
    },
]

# (seed, style, id, title). Teaching points come from the generator's trap catalog.
GENERATED = [
    (
        20270001,
        "sectioned",
        "monarch-ebus-surveyed-complication",
        "Monarch and EBUS: a station seen but not sampled, and a complication",
    ),
    (
        20270004,
        "dictation",
        "ebus-only-complications-denied",
        "EBUS staging only: complications are explicitly denied",
    ),
    (
        20270015,
        "fielded",
        "monarch-radial-only-size-in-cm",
        "Monarch: tool-in-lesion claimed from radial EBUS, size given in centimetres",
    ),
    (
        20270023,
        "markdown",
        "galaxy-ebus-planned-not-done",
        "Galaxy: EBUS staging was planned but not performed",
    ),
    (
        20270011,
        "messy",
        "ion-ebus-prior-procedure-in-history",
        "Ion and EBUS, rough dictation: stations from a prior procedure appear in the history",
    ),
    # Seed 20270021 confirmed the needle tip in the lesion and then took forceps
    # biopsies only; a reader (and the model) cannot tell what was verified. In this
    # one a needle pass follows the needle check. (Seed 20270037 was passed over:
    # the browser redactor flags its sentence-initial "Fluoroscopy" as an identifier.)
    (
        20270028,
        "sectioned",
        "ion-plain-peripheral",
        "Ion: a straightforward peripheral nodule case",
    ),
]


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _check_text(sample_id: str, text: str) -> str:
    text = text.replace("\r\n", "\n")
    if PLACEHOLDER in text:
        raise SystemExit(f"{sample_id}: sample text must not contain {PLACEHOLDER}")
    if any(ord(ch) > 0xFFFF for ch in text):
        raise SystemExit(f"{sample_id}: characters outside the BMP break browser offsets")
    return text


def _demo_header(sample_id: str, text: str, evidence: dict) -> tuple[str, dict]:
    """Swap the generator's title line for the demo header and shift evidence to match."""
    if not text.startswith(GENERATOR_HEADER + "\n"):
        raise SystemExit(f"{sample_id}: unexpected generator header")
    shift = len(DEMO_HEADER) - len(GENERATOR_HEADER)
    new_text = DEMO_HEADER + text[len(GENERATOR_HEADER) :]
    shifted = {}
    for path, (start, end, assertion) in evidence.items():
        if start < len(GENERATOR_HEADER):
            raise SystemExit(f"{sample_id}: evidence inside the header line")
        if new_text[start + shift : end + shift] != text[start:end]:
            raise SystemExit(f"{sample_id}: evidence shift mismatch at {path}")
        shifted[path] = [start + shift, end + shift, assertion]
    return new_text, shifted


def _corpus_seed_ranges() -> list[range]:
    """Seed ranges of the truth-first corpora, read from their manifests only."""
    ranges = []
    for manifest in sorted(CORPORA.glob("corpus_truth_*/manifest.json")):
        data = json.loads(manifest.read_text())
        ranges.append(range(int(data["seed"]), int(data["seed"]) + int(data["families"])))
    return ranges


def handwritten() -> list[dict]:
    out = []
    for item in HANDWRITTEN:
        text = _check_text(item["id"], item["path"].read_text())
        out.append(
            {
                **{k: v for k, v in item.items() if k != "path"},
                "source": "handwritten",
                "text": text,
                "text_sha256": _sha(text),
                "gold": None,
            }
        )
    return out


def generated() -> list[dict]:
    taken = _corpus_seed_ranges()
    out = []
    for seed, style, sample_id, title in GENERATED:
        if any(seed in r for r in taken):
            raise SystemExit(f"seed {seed} belongs to an eval corpus")
        scenario = sample_scenario(seed)
        stated = plan_statements(scenario, seed)
        text, spans = render(scenario, stated, style, seed)
        problems = unsupported_values(scenario, stated, spans, text)
        if problems or not text:
            raise SystemExit(f"{sample_id}: generator problems {problems[:5]}")
        document_id = stable_id(scenario.family_id, f"demo:doc:{style}")
        revision = build_gold(
            scenario, stated, spans, text, document_id=document_id, digest=_sha(text)
        )
        values, evidence = compact(revision)
        text, evidence = _demo_header(sample_id, text, evidence)
        text = _check_text(sample_id, text)
        points = [TRAPS[t] for t in scenario.traps] or [
            "No traps: the facts are stated plainly, so this shows the baseline behaviour."
        ]
        out.append(
            {
                "id": sample_id,
                "title": title,
                "teaching_point": " ".join(points),
                "platform": scenario.platform,
                "components": list(scenario.components),
                "style": style,
                "traps": scenario.traps,
                "source": "truth_first",
                "generator": {"version": GENERATOR_VERSION, "seed": seed},
                "text": text,
                "text_sha256": _sha(text),
                "gold": {"document_id": document_id, "revision": values, "evidence": evidence},
            }
        )
    return out


def main() -> None:
    samples = handwritten() + generated()
    if len({s["id"] for s in samples}) != len(samples):
        raise SystemExit("duplicate sample ids")
    payload = {
        "version": 1,
        "profile": "robotic_ebus_v1",
        "placeholder": PLACEHOLDER,
        "policy": "Synthetic notes only. None of these is an eval document.",
        "samples": samples,
    }
    target = DEMO_DIR / "samples.json"
    target.write_text(json.dumps(payload, indent=1, sort_keys=True, default=str) + "\n")
    for s in samples:
        print(f"{s['id']:44s} {len(s['text']):5d} chars  {s['style']:11s} {','.join(s['traps'])}")
    print(f"wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
