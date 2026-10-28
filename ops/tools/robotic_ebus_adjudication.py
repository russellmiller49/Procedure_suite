#!/usr/bin/env python3
# ruff: noqa: E402 -- CLI repository bootstrap.
"""Blinded, source-bound synthetic adjudication and independent qualification.

Only the reviewer/ directory is distributed. Coordinator files, predictions and
previous labels must stay hidden. No artifact from this synthetic corpus can
establish clinical validation or authorize clinical release.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import secrets
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ops.tools.prepare_robotic_ebus_corpus import clinical_fingerprint, normalized

SPLITS = ("train", "validation", "test", "regression")
FIELDS = {
    "ebus.short_axis_mm": ("station", "short_axis_mm"),
    "ebus.sampled_station": ("station", "sampled"),
    "ebus.observed_not_sampled": ("station", "observed_not_sampled"),
    "ebus.station_pass_count": ("station", "pass_count"),
    "localization.modality": ("target", "localization"),
    "safety.immediate": ("procedure", "safety"),
}
MODALITIES = {
    "radial_EBUS",
    "2D_fluoroscopy",
    "fixed_CBCT",
    "mobile_CBCT",
    "CBCT_unspecified",
    "digital_tomosynthesis",
    "augmented_fluoroscopy",
    "conventional_CT",
    "cone_beam_overlay",
    "other",
}
STATIONS = {
    "2R",
    "2L",
    "3A",
    "3P",
    "4R",
    "4L",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10R",
    "10L",
    "11R",
    "11L",
    "11Rs",
    "11Ri",
    "12R",
    "12L",
}
LOBES = {"RUL", "RML", "RLL", "LUL", "LLL", "Lingula"}
CSV_COLUMNS = {
    "reviews": [
        "case_id",
        "reviewer_id",
        "clinical_expertise",
        "blinded",
        "independent",
        "completed_at",
        "resolution_notes",
    ],
    "fields": ["case_id", "field", "status", "notes"],
    "spans": ["case_id", "span_id", "start", "end", "text", "label", "normalized", "assertion"],
    "relationships": ["case_id", "relationship_id", "field", "source_span_id", "target_span_id"],
}
DEFAULT_EXPOSED = ROOT / "data/knowledge/robotic_ebus_v1/reviewed_eval_selection.json"


def digest(value):
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path, columns):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != columns:
            raise ValueError(f"Invalid columns: {path.name}")
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"Malformed CSV: {path.name}")
    return rows


def load_corpus(corpus):
    manifest = json.loads((corpus / "split_manifest.json").read_text())
    if manifest.get("profile") != "robotic_ebus_v1":
        raise ValueError("Wrong corpus profile")
    rows, families, fingerprints = {}, defaultdict(set), defaultdict(set)
    for split in SPLITS:
        path = corpus / f"{split}.jsonl"
        if digest(path.read_bytes()) != manifest["artifacts"][path.name]:
            raise ValueError(f"Corpus artifact changed: {path.name}")
        for line in path.read_text().splitlines():
            row = json.loads(line)
            key = row["document_id"]
            if key in rows or row["split"] != split or digest(row["text"]) != row["text_sha256"]:
                raise ValueError("Duplicate document, wrong split or stale source digest")
            if not row["family_id"] or manifest["splits"].get(row["family_id"]) != split:
                raise ValueError("Family assignment differs from frozen manifest")
            if row.get("prior_training_overlap") and split != "regression":
                raise ValueError("Prior training overlap outside regression")
            rows[key] = row
            families[row["family_id"]].add(split)
            for fingerprint in (digest(normalized(row["text"])), clinical_fingerprint(row["text"])):
                fingerprints[fingerprint].add(split)
    if any(len(splits) > 1 for splits in [*families.values(), *fingerprints.values()]):
        raise ValueError("Family/scenario fingerprint crosses splits")
    if len(rows) != manifest["documents"] or set(families) != set(manifest["splits"]):
        raise ValueError("Corpus inventory differs from manifest")
    return rows


def known_exposed(rows):
    # The checked-in pilot was used in engineering iterations and cannot be reset.
    gold = json.loads(DEFAULT_EXPOSED.read_text())
    exposed = {r["family_id"] for r in rows.values() if r["split"] != "test"}
    exposed.update(
        rows[c["document_id"]]["family_id"] for c in gold["cases"] if c["document_id"] in rows
    )
    exposure_path = DEFAULT_EXPOSED.with_name("qualification_exposure.json")
    if exposure_path.exists():
        exposure = json.loads(exposure_path.read_text())
        for event in exposure["events"]:
            exposed.update(rows[key]["family_id"] for key in event["document_ids"] if key in rows)
    return exposed


SCENARIO_COLUMNS = [
    "document_id",
    "family_id",
    "split",
    "scenario_id",
    "status",
    "reviewer_id",
    "engineering_exposed",
]


def audit_scenarios(rows, path):
    records = read_csv(path, SCENARIO_COLUMNS)
    if len(records) != len(rows) or {r["document_id"] for r in records} != set(rows):
        raise ValueError("Scenario audit must cover every corpus document exactly once")
    groups, family_scenarios = defaultdict(set), defaultdict(set)
    exposed, unresolved = set(), []
    by_document = {}
    known = known_exposed(rows)
    for record in records:
        row = rows[record["document_id"]]
        scenario = record["scenario_id"].strip()
        if (record["family_id"], record["split"]) != (row["family_id"], row["split"]):
            raise ValueError("Scenario audit cannot reassign frozen splits or families")
        if not scenario or record["status"] not in {"pending", "reviewed"}:
            raise ValueError("Missing scenario or invalid review status")
        if record["engineering_exposed"] not in {"true", "false"}:
            raise ValueError("Exposure must be explicit")
        if row["family_id"] in known and record["engineering_exposed"] != "true":
            raise ValueError("Known exposure cannot be cleared")
        if record["status"] != "reviewed" or not record["reviewer_id"].strip():
            unresolved.append(row["document_id"])
        groups[scenario].add(row["split"])
        family_scenarios[row["family_id"]].add(scenario)
        if record["engineering_exposed"] == "true":
            exposed.add(scenario)
        by_document[row["document_id"]] = record
    if any(len(values) != 1 for values in family_scenarios.values()):
        raise ValueError("A family cannot be divided into multiple scenarios")
    if any(len(values) != 1 for values in groups.values()):
        raise ValueError("Scenario leakage across frozen splits; create a new corpus version")
    # Exact/cosmetic duplicates cannot acquire different semantic scenario IDs.
    fingerprints = defaultdict(set)
    for key, row in rows.items():
        fingerprints[clinical_fingerprint(row["text"])].add(by_document[key]["scenario_id"])
    if any(len(values) != 1 for values in fingerprints.values()):
        raise ValueError("Equivalent source fingerprints have inconsistent scenario assignments")
    return {
        "complete": not unresolved,
        "pending_documents": len(unresolved),
        "scenario_count": len(groups),
        "exposed_scenarios": sorted(exposed),
        "documents": by_document,
        "sha256": digest(path.read_bytes()),
    }


def packet(corpus, output):
    rows = load_corpus(corpus)
    if output.exists():
        raise ValueError("Packet already exists; use a new version to preserve review history")
    reviewer, private = output / "reviewer", output / "coordinator"
    reviewer.mkdir(parents=True)
    private.mkdir()
    exposed = known_exposed(rows)
    # A proposed family-level scenario is deliberately NOT a completed semantic audit.
    scenarios = [
        {
            "document_id": key,
            "family_id": r["family_id"],
            "split": r["split"],
            "scenario_id": r["family_id"],
            "status": "pending",
            "reviewer_id": "",
            "engineering_exposed": str(r["family_id"] in exposed).lower(),
        }
        for key, r in sorted(rows.items())
    ]
    write_csv(private / "scenarios.csv", SCENARIO_COLUMNS, scenarios)
    cases, mapping = [], {}
    selected = [r for r in rows.values() if r["split"] == "test"]
    secrets.SystemRandom().shuffle(selected)
    for row in selected:
        case_id = "C-" + secrets.token_hex(8)
        cases.append({"case_id": case_id, "text": row["text"]})
        mapping[case_id] = {k: row[k] for k in ("document_id", "family_id", "text_sha256")}
    write_csv(reviewer / "cases.csv", ["case_id", "text"], cases)
    for name, columns in CSV_COLUMNS.items():
        initial = []
        if name == "reviews":
            initial = [
                {key: case["case_id"] if key == "case_id" else "" for key in columns}
                for case in cases
            ]
        if name == "fields":
            initial = [
                {"case_id": case["case_id"], "field": field, "status": "pending", "notes": ""}
                for case in cases
                for field in FIELDS
            ]
        write_csv(reviewer / f"{name}.csv", columns, initial)
    instructions = """# Blinded source adjudication — robotic_ebus_v1

These are synthetic documents. Reviewing them does not validate clinical use.
Distribute only this reviewer directory. Make two separate copies for two clinical
reviewers; neither sees model outputs, weak labels, generator metadata, split or
family assignments, earlier pilot answers, or the other reviewer's annotations.
Source notes are verbatim: names/platforms and outcome claims inside a note remain
source content, not verified clinical truth. Do not infer hidden generator outcomes.

Open packet.html for selectable source text and Unicode code-point offsets (start
inclusive, end exclusive, matching Python). Edit UTF-8 CSV files with the exact
headers. cases.csv must remain unchanged; do not normalize whitespace or newlines.
Prefer a text/CSV editor; do not enable spreadsheet formulas in source notes.

reviews.csv: for every case supply reviewer_id, clinical_expertise (nonempty),
blinded=true, independent=true/false (independent means no development/tuning role
or prior access to model/pilot answers), completed_at (ISO 8601 with timezone).
fields.csv: one row per case/field. Replace pending with documented, reviewed_empty
(no supported fact), unknown, or conflict. Explain unknown/conflict in notes. An
empty annotation table alone is never evidence of a completed negative review.

spans.csv: unique span_id within case; exact source start/end/text; label and
normalized value; assertion affirmed, negated or uncertain. Labels/normalization:
station = IASLC token; target = lobe (RUL/RML/RLL/LUL/LLL/Lingula); procedure =
procedure; short_axis_mm = positive millimetres (include explicit 'short axis' in
the quote; generic node size is not short-axis); pass_count = positive integer;
sampled = sampled; observed_not_sampled = observed_not_sampled; localization =
radial_EBUS/2D_fluoroscopy/fixed_CBCT/mobile_CBCT/CBCT_unspecified/digital_tomosynthesis/augmented_fluoroscopy/conventional_CT/
cone_beam_overlay/other;
safety = present/absent (absent requires negated assertion). Do not collapse two
same-lobe targets: mark localization conflict when this projection is ambiguous.
All documented relationships require affirmed evidence, except negated absent safety.

relationships.csv: unique relationship_id within case; field is one of the six
fields.csv names; source_span_id references station for all EBUS fields, target
for localization, or procedure for safety. target_span_id references the matching
value label (short_axis_mm, sampled, observed_not_sampled, pass_count, localization,
safety). Include evidence of the action and target; tools alone are insufficient.

A third clinical adjudicator receives the two completed blinded submissions and
creates a separate final set of the same four CSVs. Retain original reviews. The
adjudicator uses a distinct reviewer_id, records blinded=true (still blinded to
model outputs), and explains each disagreement in resolution_notes. A coordinator
imports all three sets. Never manufacture reviewer identities or completed reviews.
"""
    (reviewer / "README.md").write_text(instructions, encoding="utf-8")
    articles = "".join(
        f'<article><h2>{c["case_id"]}</h2><pre data-case="{c["case_id"]}">'
        f"{html.escape(c['text']).replace(chr(13), '&#13;')}</pre></article>"
        for c in cases
    )
    page = (
        """<!doctype html><html lang="en"><meta charset="utf-8"><title>Blinded source review</title>
<style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:0 24px;color:#182635}
pre{white-space:pre-wrap;line-height:1.5;background:#f3f6f8;padding:20px}article{break-after:page}
output{display:block;position:sticky;top:0;background:#fff4cc;
 padding:16px;border:1px solid #ab9200;white-space:pre-wrap}
@media print{output{display:none}}</style><h1>Blinded source review</h1><p>
Synthetic source documents — no clinical validation.
Read <a href="README.md">review instructions</a>. Select source text
to get exact code-point offsets.
No annotations are prefilled.</p>
<output id="selection">Select a source span.</output>"""
        + articles
        + """<script>
document.addEventListener('selectionchange',()=>{
const s=getSelection();if(!s.rangeCount||s.isCollapsed)return;
const r=s.getRangeAt(0),p=r.startContainer.parentElement.closest('pre');
if(!p||!p.contains(r.endContainer))return;
const before=document.createRange();before.selectNodeContents(p);
before.setEnd(r.startContainer,r.startOffset);
const start=Array.from(before.toString()).length,text=r.toString();
document.getElementById('selection').textContent=JSON.stringify({case_id:p.dataset.case,start:start,end:start+Array.from(text).length,text:text},null,2);
});</script></html>"""
    )
    (reviewer / "packet.html").write_text(page, encoding="utf-8")
    manifest = {
        "schema_version": "robotic_ebus.blinded_packet.v1",
        "synthetic_only": True,
        "corpus_manifest_sha256": digest((corpus / "split_manifest.json").read_bytes()),
        "cases": mapping,
        "cases_csv_sha256": digest((reviewer / "cases.csv").read_bytes()),
        "reviewer_packet_sha256": digest((reviewer / "packet.html").read_bytes()),
        "annotation_status": "pending_clinical_adjudication",
    }
    save(private / "packet_manifest.json", manifest)
    return {"documents": len(cases), "synthetic_only": True, "clinical_validation": False}


def load_packet(corpus, packet_dir):
    rows = load_corpus(corpus)
    manifest = json.loads((packet_dir / "coordinator/packet_manifest.json").read_text())
    if (
        manifest.get("schema_version") != "robotic_ebus.blinded_packet.v1"
        or manifest.get("synthetic_only") is not True
    ):
        raise ValueError("Unsupported packet provenance")
    if manifest["corpus_manifest_sha256"] != digest((corpus / "split_manifest.json").read_bytes()):
        raise ValueError("Packet corpus changed")
    if digest((packet_dir / "reviewer/cases.csv").read_bytes()) != manifest["cases_csv_sha256"]:
        raise ValueError("Packet source CSV changed")
    if (
        digest((packet_dir / "reviewer/packet.html").read_bytes())
        != manifest["reviewer_packet_sha256"]
    ):
        raise ValueError("Packet source HTML changed")
    cases = read_csv(packet_dir / "reviewer/cases.csv", ["case_id", "text"])
    if len(cases) != len(manifest["cases"]) or {c["case_id"] for c in cases} != set(
        manifest["cases"]
    ):
        raise ValueError("Packet case inventory mismatch")
    document_ids = []
    for case in cases:
        binding = manifest["cases"][case["case_id"]]
        row = rows[binding["document_id"]]
        document_ids.append(row["document_id"])
        if (
            any(binding[k] != row[k] for k in binding)
            or case["text"] != row["text"]
            or row["split"] != "test"
        ):
            raise ValueError("Stale case binding or non-test case")
    if len(set(document_ids)) != len(document_ids):
        raise ValueError("Duplicate packet document")
    return rows, manifest


def validate_span(span, text):
    try:
        start, end = int(span["start"]), int(span["end"])
    except ValueError as exc:
        raise ValueError("Span offsets must be integers") from exc
    if not 0 <= start < end <= len(text) or text[start:end] != span["text"]:
        raise ValueError("Span offset/text mismatch")
    label, value = span["label"], span["normalized"]
    if span["assertion"] not in {"affirmed", "negated", "uncertain"}:
        raise ValueError("Invalid assertion")
    allowed = {
        "station": STATIONS,
        "target": LOBES,
        "procedure": {"procedure"},
        "sampled": {"sampled"},
        "observed_not_sampled": {"observed_not_sampled"},
        "localization": MODALITIES,
        "safety": {"present", "absent"},
    }
    if label in allowed:
        if value not in allowed[label]:
            raise ValueError("Invalid normalized span value")
    elif label == "pass_count":
        if not re.fullmatch(r"[1-9][0-9]*", value):
            raise ValueError("Pass count must be a positive integer")
    elif label == "short_axis_mm":
        if not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value) or float(value) <= 0:
            raise ValueError("Short axis must be a positive finite millimetre value")
        if not re.search(r"short[\s-]*axis", span["text"], re.I):
            raise ValueError("Explicit short-axis source evidence required")
    else:
        raise ValueError("Unknown span label")


def load_review(directory, rows, manifest):
    data = {
        name: read_csv(directory / f"{name}.csv", columns) for name, columns in CSV_COLUMNS.items()
    }
    cases = manifest["cases"]
    result = {
        case_id: {"spans": {}, "relationships": {}, "fields": {}, "review": None}
        for case_id in cases
    }
    for name, records in data.items():
        for record in records:
            case_id = record["case_id"]
            if case_id not in cases:
                raise ValueError("Unknown review case")
            entry = result[case_id]
            if name == "reviews":
                if entry["review"] is not None:
                    raise ValueError("Duplicate case review")
                if not record["reviewer_id"].strip() or not record["clinical_expertise"].strip():
                    raise ValueError("Clinical reviewer identity/expertise required")
                if record["blinded"] != "true" or record["independent"] not in {"true", "false"}:
                    raise ValueError("Blinding and independence must be explicitly attested")
                try:
                    timestamp = datetime.fromisoformat(record["completed_at"])
                    if timestamp.tzinfo is None:
                        raise ValueError("timezone required")
                except ValueError as exc:
                    raise ValueError("Review completion timestamp with timezone required") from exc
                entry["review"] = record
                continue
            key = record[
                {"spans": "span_id", "relationships": "relationship_id", "fields": "field"}[name]
            ]
            if not key or key in entry[name]:
                raise ValueError("Duplicate or missing annotation ID")
            entry[name][key] = record
            if name == "spans":
                validate_span(record, rows[cases[case_id]["document_id"]]["text"])
    for entry in result.values():
        if entry["review"] is None or set(entry["fields"]) != set(FIELDS):
            raise ValueError("Every case requires a review and all critical fields")
        expected, links = defaultdict(set), defaultdict(set)
        for relation in entry["relationships"].values():
            field = relation["field"]
            if field not in FIELDS:
                raise ValueError("Unknown relationship field")
            source = entry["spans"].get(relation["source_span_id"])
            target = entry["spans"].get(relation["target_span_id"])
            if source is None or target is None:
                raise ValueError("Dangling or cross-case relationship")
            if (source["label"], target["label"]) != FIELDS[field]:
                raise ValueError("Invalid relationship endpoint types")
            assertion = (
                "negated"
                if field == "safety.immediate" and target["normalized"] == "absent"
                else "affirmed"
            )
            if source["assertion"] != "affirmed" or target["assertion"] != assertion:
                raise ValueError(
                    "Uncertain/negated evidence cannot support this documented relationship"
                )
            value = target["normalized"]
            if field == "ebus.short_axis_mm":
                value = f"{float(value):g}"
            anchor = source["normalized"]
            fact = (
                f"{anchor}:{value}"
                if field in {"ebus.short_axis_mm", "ebus.station_pass_count"}
                else anchor
                if field.startswith("ebus.")
                else value
            )
            link = anchor + "|" + value
            if link in links[field]:
                raise ValueError("Duplicate semantic relationship")
            expected[field].add(fact)
            links[field].add(link)
        for field, record in entry["fields"].items():
            status = record["status"]
            if status not in {"documented", "reviewed_empty", "unknown", "conflict"}:
                raise ValueError("Pending/invalid field review")
            if (status == "documented") != bool(expected[field]):
                raise ValueError("Field status does not match supported relationships")
            if status in {"unknown", "conflict"} and not record["notes"].strip():
                raise ValueError("Unresolved field requires an explanation")
        if expected["ebus.sampled_station"] & expected["ebus.observed_not_sampled"]:
            raise ValueError("A station cannot be both sampled and observed-not-sampled")
        if len(expected["safety.immediate"]) > 1:
            raise ValueError("Conflicting safety assertions must remain unresolved")
        entry["expected"] = {k: sorted(v) for k, v in expected.items()}
        entry["expected_relationships"] = {k: sorted(v) for k, v in links.items()}
    return result


def semantic_review(entry):
    # Ignore arbitrary local span IDs, but compare actual evidence and missingness.
    return {
        "spans": sorted(
            tuple(v[k] for k in CSV_COLUMNS["spans"] if k not in {"case_id", "span_id"})
            for v in entry["spans"].values()
        ),
        "fields": {k: v["status"] for k, v in entry["fields"].items()},
        "relationships": entry["expected_relationships"],
    }


def import_reviews(corpus, packet_dir, review_a, review_b, adjudication, output):
    if output is not None and output.exists():
        raise ValueError("Imported adjudication already exists; use a new version")
    rows, manifest = load_packet(corpus, packet_dir)
    reviews = [
        load_review(directory, rows, manifest) for directory in (review_a, review_b, adjudication)
    ]
    identities = [
        {v["review"]["reviewer_id"].strip().casefold() for v in review.values()}
        for review in reviews
    ]
    if any(identities[i] & identities[j] for i in range(3) for j in range(i)):
        raise ValueError("Two reviewers and a distinct adjudicator are required")
    cases, disagreements = [], 0
    for case_id, binding in manifest["cases"].items():
        a, b, final = [review[case_id] for review in reviews]
        different = semantic_review(a) != semantic_review(b)
        changed = semantic_review(final) != semantic_review(a) or semantic_review(
            final
        ) != semantic_review(b)
        if changed and not final["review"]["resolution_notes"].strip():
            raise ValueError("Adjudication changes/disagreements require resolution notes")
        disagreements += int(different)
        cases.append(
            {
                "case_id": case_id,
                **binding,
                "split": rows[binding["document_id"]]["split"],
                "reviews": [r[case_id]["review"] for r in reviews],
                "disagreement": different,
                "fields": final["fields"],
                "spans": list(final["spans"].values()),
                "relationships": list(final["relationships"].values()),
                "expected": final["expected"],
                "expected_relationships": final["expected_relationships"],
            }
        )
    result = {
        "schema_version": "robotic_ebus.adjudication.v1",
        "synthetic_only": True,
        "clinical_validation": False,
        "annotation_status": "clinician_adjudicated_synthetic",
        "corpus_manifest_sha256": manifest["corpus_manifest_sha256"],
        "packet_manifest_sha256": digest(
            (packet_dir / "coordinator/packet_manifest.json").read_bytes()
        ),
        "review_inputs": {
            role: {
                f"{name}.csv": digest((directory / f"{name}.csv").read_bytes())
                for name in CSV_COLUMNS
            }
            for role, directory in zip(
                ("review_a", "review_b", "adjudication"),
                (review_a, review_b, adjudication),
                strict=True,
            )
        },
        "disagreements": disagreements,
        "cases": cases,
    }
    if output is not None:
        save(output, result)
    return result


def coverage(cases):
    counts = {
        field: {
            "positive_facts": 0,
            "positive_documents": 0,
            "positive_families": set(),
            "unresolved_documents": 0,
        }
        for field in FIELDS
    }
    safety = Counter()
    for case in cases:
        for field in FIELDS:
            values = case.get("expected", {}).get(field, [])
            counts[field]["positive_facts"] += len(values)
            counts[field]["positive_documents"] += bool(values)
            if values:
                counts[field]["positive_families"].add(case.get("family_id", case["document_id"]))
            if case.get("fields", {}).get(field, {}).get("status") in {
                "pending",
                "unknown",
                "conflict",
            }:
                counts[field]["unresolved_documents"] += 1
        safety.update(case.get("expected", {}).get("safety.immediate", []))
    for value in counts.values():
        value["positive_families"] = len(value["positive_families"])
    return {
        "fields": counts,
        "safety_present": safety["present"],
        "safety_absent": safety["absent"],
        "all_required_positive_coverage": all(v["positive_facts"] > 0 for v in counts.values())
        and safety["present"] > 0
        and safety["absent"] > 0,
    }


def readiness(corpus, packet_dir, output):
    rows, manifest = load_packet(corpus, packet_dir)
    audit = audit_scenarios(rows, packet_dir / "coordinator/scenarios.csv")
    pilot = json.loads(DEFAULT_EXPOSED.read_text())
    for case in pilot["cases"]:
        if case["document_id"] in rows:
            case["family_id"] = rows[case["document_id"]]["family_id"]
    eligible = [
        binding["document_id"]
        for binding in manifest["cases"].values()
        if audit["documents"][binding["document_id"]]["scenario_id"]
        not in audit["exposed_scenarios"]
    ]
    report = {
        "schema_version": "robotic_ebus.qualification_readiness.v1",
        "synthetic_only": True,
        "clinical_validation": False,
        "promotion_allowed": False,
        "corpus_manifest_sha256": manifest["corpus_manifest_sha256"],
        "packet_documents": len(manifest["cases"]),
        "potentially_unexposed_documents": len(eligible),
        "scenario_audit": {k: v for k, v in audit.items() if k != "documents"},
        "exposed_pilot_coverage": coverage(pilot["cases"]),
        "blocked_reasons": [
            "clinical_adjudication_pending",
            "synthetic_is_not_clinical_validation",
            "independent_candidate_and_baseline_qualification_pending",
            "format_qualification_pending",
        ],
    }
    if not eligible:
        report["blocked_reasons"].append("no_unexposed_qualification_cases")
    if not audit["complete"]:
        report["blocked_reasons"].append("semantic_scenario_audit_pending")
    if not report["exposed_pilot_coverage"]["all_required_positive_coverage"]:
        report["blocked_reasons"].append("exposed_pilot_missing_required_positive_coverage")
    save(output, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["packet", "import", "readiness"])
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--review-a", type=Path)
    parser.add_argument("--review-b", type=Path)
    parser.add_argument("--adjudication", type=Path)
    parser.add_argument("--require-acceptance", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "packet":
            result = packet(args.corpus, args.output)
        else:
            if args.packet is None:
                parser.error("--packet is required")
            if args.command == "import":
                if any(x is None for x in (args.review_a, args.review_b, args.adjudication)):
                    parser.error("--review-a, --review-b and --adjudication are required")
                result = import_reviews(
                    args.corpus,
                    args.packet,
                    args.review_a,
                    args.review_b,
                    args.adjudication,
                    args.output,
                )
            else:
                result = readiness(args.corpus, args.packet, args.output)
    except (ValueError, KeyError, OSError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k
                in {
                    "documents",
                    "packet_documents",
                    "synthetic_only",
                    "clinical_validation",
                    "promotion_allowed",
                    "blocked_reasons",
                    "annotation_status",
                    "disagreements",
                }
            }
        )
    )
    return 2 if args.require_acceptance and not result.get("promotion_allowed", False) else 0


if __name__ == "__main__":
    raise SystemExit(main())
