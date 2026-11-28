#!/usr/bin/env python3
# ruff: noqa: E402 -- Compare the isolated candidate with the development runtime.
"""Compare real runtime outputs on source-reviewed fields and relationships.

Scores include support and unresolved coverage. Weak NER labels are never a gold
field reference. Pilot families were excluded from NER training. Once exposed for
engineering regression review, they cannot establish independent qualification.
"""

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "packages/ip_registry_contracts/src"),
    str(ROOT / "packages/ip_registry_engine/src"),
]
from ip_registry_contracts.models import ExtractionRequest
from ip_registry_engine.engine import LocalDeterministicProvider
from ops.tools.robotic_ebus_adjudication import coverage, load_corpus


def focused_facts(payload):
    out = defaultdict(set)
    value = payload.get("proposal", {})
    for procedure in value.get("procedures", []):
        if procedure["performance"] in {"performed", "attempted"}:
            out["procedures.started"].add(procedure["category"])
    for target in value.get("targets", []):
        lobe = target.get("lobe")
        if target.get("site") == "lung" and lobe:
            out["target.lobe"].add(lobe)
            if target.get("max_diameter_mm") is not None:
                out["target.max_diameter_mm"].add(f"{lobe}:{target['max_diameter_mm']:g}")
            if target.get("bronchus_sign_present") is not None:
                out["target.bronchus_sign"].add(
                    f"{lobe}:{str(target['bronchus_sign_present']).lower()}"
                )
        station = target.get("iaslc_station")
        if station and target.get("sampling_attempted") is True:
            out["ebus.sampled_station"].add(station)
        if station and target.get("needle_pass_count") is not None:
            out["ebus.station_pass_count"].add(f"{station}:{target['needle_pass_count']}")
        if station and target.get("short_axis_mm") is not None:
            out["ebus.short_axis_mm"].add(f"{station}:{target['short_axis_mm']:g}")
    for survey in value.get("station_surveys", []):
        if survey.get("station_sampled") is False and survey.get("station_visualized") is True:
            out["ebus.observed_not_sampled"].add(survey["iaslc_station"])
    for event in value.get("localization_events", []):
        out["localization.modality"].add(event["localization_modality"])
    if value.get("complication_assessment") in {"present", "absent"}:
        out["safety.immediate"].add(value["complication_assessment"])
    return out


def baseline_facts(value):
    out = defaultdict(set)
    pp = value.get("procedures_performed") or {}
    equipment = value.get("equipment") or {}
    granular = value.get("granular_data") or {}
    # A generic navigation flag alone must never be relabeled robotic.
    if (pp.get("navigational_bronchoscopy") or {}).get("performed") and equipment.get(
        "navigation_platform"
    ) in {"Ion", "Monarch", "Galaxy"}:
        out["procedures.started"].add("robotic_bronchoscopy")
    linear = pp.get("linear_ebus") or {}
    if linear.get("performed"):
        out["procedures.started"].add("linear_ebus")
    for station in linear.get("stations_sampled") or value.get("ebus_stations_sampled") or []:
        out["ebus.sampled_station"].add(str(station))
    for target in granular.get("navigation_targets") or []:
        lobe = target.get("target_lobe")
        if lobe:
            out["target.lobe"].add(lobe)
            if target.get("lesion_size_mm") is not None:
                out["target.max_diameter_mm"].add(f"{lobe}:{target['lesion_size_mm']:g}")
            if target.get("bronchus_sign") in {"Present", "Absent"}:
                out["target.bronchus_sign"].add(
                    f"{lobe}:{str(target['bronchus_sign'] == 'Present').lower()}"
                )
    for target in (
        granular.get("linear_ebus_stations_detail") or value.get("ebus_stations_detail") or []
    ):
        station = target.get("station")
        if station and target.get("number_of_passes") is not None:
            out["ebus.station_pass_count"].add(f"{station}:{target['number_of_passes']}")
        if station and target.get("short_axis_mm") is not None:
            out["ebus.short_axis_mm"].add(f"{station}:{target['short_axis_mm']:g}")
    if (pp.get("radial_ebus") or {}).get("performed"):
        out["localization.modality"].add("radial_EBUS")
    if equipment.get("fluoroscopy_used"):
        out["localization.modality"].add("2D_fluoroscopy")
    if equipment.get("cbct_used"):
        out["localization.modality"].add("CBCT_unspecified")
    complications = value.get("complications") or {}
    if complications.get("complication_occurred") is not None:
        out["safety.immediate"].add(
            "present" if complications["complication_occurred"] else "absent"
        )
    return out


def metrics(tp, fp, fn):
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "support": tp + fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
    }


def evaluate(corpus, gold_path, output, model_dir, baseline):
    corpus_rows = load_corpus(corpus)
    gold = json.loads(gold_path.read_text())
    for case in gold["cases"]:
        case["family_id"] = corpus_rows[case["document_id"]]["family_id"]
    manifest = corpus / "split_manifest.json"
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != gold["corpus_manifest_sha256"]:
        raise ValueError("Evaluation split changed")
    documents = {
        r["document_id"]: r
        for line in (corpus / "test.jsonl").read_text().splitlines()
        if (r := json.loads(line))
    }
    provider = LocalDeterministicProvider(model_dir)
    engines = {
        "candidate": lambda row: focused_facts(
            provider.extract(
                ExtractionRequest(
                    job_id=uuid4(),
                    source_document_id=uuid4(),
                    source_digest=row["text_sha256"],
                    text=row["text"],
                    kind="procedure",
                )
            ).observations
        )
    }
    if baseline:
        from app.registry.application.registry_service import RegistryService

        service = RegistryService()

        def run_baseline(row):
            result = service.extract_fields(row["text"])
            value = result.registry if hasattr(result, "registry") else result.record
            return baseline_facts(value.model_dump())

        engines["current_engine"] = run_baseline
    reports = {}
    for engine, extract in engines.items():
        aggregate = defaultdict(lambda: [0, 0, 0])
        cases = []
        for case in gold["cases"]:
            row = documents[case["document_id"]]
            try:
                actual = extract(row)
            except Exception as exc:
                cases.append({"document_id": row["document_id"], "error": type(exc).__name__})
                actual = {}
            failures = []
            for field in gold["critical_fields"]:
                expected = set(case["expected"].get(field, []))
                found = set(actual.get(field, []))
                counts = (len(expected & found), len(found - expected), len(expected - found))
                for key in (
                    "overall",
                    "field:" + field,
                    "platform:" + case["platform"],
                    "format:" + case["format"],
                    f"field_platform_format:{field}:{case['platform']}:{case['format']}",
                ):
                    aggregate[key] = [a + b for a, b in zip(aggregate[key], counts, strict=True)]
                if counts[1] or counts[2]:
                    failures.append(
                        {
                            "field": field,
                            "extra": sorted(found - expected),
                            "missing": sorted(expected - found),
                        }
                    )
            cases.append(
                {
                    "document_id": row["document_id"],
                    "family_id": row["family_id"],
                    "platform": case["platform"],
                    "format": case["format"],
                    "failures": failures,
                }
            )
        reports[engine] = {
            "metrics": {key: metrics(*values) for key, values in aggregate.items()},
            "cases": cases,
        }
    candidate = reports["candidate"]["metrics"]["overall"]
    targets = (candidate["precision"] or 0) >= 0.98 and (candidate["recall"] or 0) >= 0.95
    baseline_score = reports.get("current_engine", {}).get("metrics", {}).get("overall")
    field_targets = {
        field: bool((value["precision"] or 0) >= 0.98 and (value["recall"] or 0) >= 0.95)
        for field, value in reports["candidate"]["metrics"].items()
        if field.startswith("field:")
    }
    improves = bool(
        baseline_score
        and (candidate["precision"] or 0) >= (baseline_score["precision"] or 0)
        and (candidate["recall"] or 0) > (baseline_score["recall"] or 0)
    )
    report = {
        "schema_version": "robotic_ebus.engineering_eval.v1",
        "profile": "robotic_ebus_v1",
        "contract_version": "0.2.0",
        "corpus_manifest_sha256": gold["corpus_manifest_sha256"],
        "gold_sha256": hashlib.sha256(gold_path.read_bytes()).hexdigest(),
        "gold_review": gold["annotation_status"],
        "evaluation_use": "exposed_engineering_regression",
        "independent_qualification_evidence": False,
        "reviewed_documents": len(gold["cases"]),
        "test_documents": len(documents),
        "reviewed_families": len({documents[c["document_id"]]["family_id"] for c in gold["cases"]}),
        "model_available": provider.ner is not None,
        "model_manifest_sha256": getattr(provider.ner, "manifest_digest", None),
        "reports": reports,
        "acceptance": {
            "precision_target": 0.98,
            "recall_target": 0.95,
            "aggregate_targets_met": targets,
            "documented_critical_field_targets": field_targets,
            "all_documented_critical_field_targets_met": all(field_targets.values()),
            "improves_over_observed_baseline": improves,
            "all_required_fields_and_formats_reviewed": False,
            "required_positive_coverage": coverage(gold["cases"]),
            "promotion_allowed": False,
            "reason": "Full independently adjudicated field/relationship coverage, integrity and format qualification required; weak-label NER scores are not acceptance evidence.",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {"candidate": candidate, "baseline": baseline_score, "acceptance": report["acceptance"]}
        )
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument(
        "--require-acceptance",
        action="store_true",
        help="Exit nonzero until release acceptance is established",
    )
    args = parser.parse_args()
    for key, value in {
        "PROCSUITE_SKIP_DOTENV": "1",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
        "REGISTRY_USE_STUB_LLM": "1",
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        "REGISTRY_SCHEMA_VERSION": "v3",
    }.items():
        os.environ[key] = value
    result = evaluate(args.corpus, args.gold, args.output, args.model_dir, args.baseline)
    if args.require_acceptance and not result["acceptance"]["promotion_allowed"]:
        raise SystemExit(2)
