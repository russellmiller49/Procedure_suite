#!/usr/bin/env python3
# ruff: noqa: E402 -- CLI repository bootstrap.
"""One-use independent synthetic qualification; clinical release always stays closed.

Validation is performed before inference. A corpus-local use ledger reserves the
entire test split before outputs become visible, including failed runs. Further
runs belong to engineering regression, never independent qualification.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ops.tools.robotic_ebus_adjudication import (
    FIELDS,
    audit_scenarios,
    coverage,
    digest,
    import_reviews,
    load_packet,
    save,
)


def relationship_facts(payload):
    """Attribute relations to station, lung lobe or procedure, never a free value."""
    out = defaultdict(set)
    proposal = payload.get("proposal", {})
    targets = {t["target_id"]: t for t in proposal.get("targets", [])}
    for target in targets.values():
        station = target.get("iaslc_station")
        if not station:
            continue
        if target.get("sampling_attempted") is True:
            out["ebus.sampled_station"].add(station + "|sampled")
        for key, field in (
            ("short_axis_mm", "ebus.short_axis_mm"),
            ("needle_pass_count", "ebus.station_pass_count"),
        ):
            if target.get(key) is not None:
                out[field].add(f"{station}|{target[key]:g}")
    for survey in proposal.get("station_surveys", []):
        if survey.get("station_sampled") is False and survey.get("station_visualized") is True:
            out["ebus.observed_not_sampled"].add(survey["iaslc_station"] + "|observed_not_sampled")
    # Ambiguous same-lobe targets cannot be silently collapsed into one relation.
    lobes = [t.get("lobe") for t in targets.values() if t.get("site") == "lung"]
    for event in proposal.get("localization_events", []):
        target = targets.get(event.get("target_id"), {})
        lobe = target.get("lobe")
        anchor = lobe if lobe and lobes.count(lobe) == 1 else "unresolved_target"
        out["localization.modality"].add(anchor + "|" + event["localization_modality"])
    safety = proposal.get("complication_assessment")
    if safety in {"present", "absent"}:
        out["safety.immediate"].add("procedure|" + safety)
    return out


def score(cases, actual, expected_key):
    from ops.tools.eval_robotic_ebus import metrics

    scores, failures = {}, []
    for field in FIELDS:
        tp = fp = fn = 0
        for case in cases:
            expected = set(case[expected_key].get(field, []))
            found = set(actual.get(case["document_id"], {}).get(field, []))
            tp += len(expected & found)
            fp += len(found - expected)
            fn += len(expected - found)
            if expected != found:
                failures.append(
                    {
                        "document_id": case["document_id"],
                        "field": field,
                        "missing": sorted(expected - found),
                        "extra": sorted(found - expected),
                    }
                )
        scores[field] = metrics(tp, fp, fn)
    return {"metrics": scores, "failures": failures}


def targets_met(report):
    return all(
        value["support"] > 0
        and (value["precision"] or 0) >= 0.98
        and (value["recall"] or 0) >= 0.95
        for value in report["metrics"].values()
    )


def model_identity(model_dir):
    path = model_dir / "focused-model-manifest.json"
    manifest = json.loads(path.read_text())
    if manifest.get("registry_profile") != "robotic_ebus_v1" or not manifest.get("files"):
        raise ValueError("Invalid candidate model manifest")
    for name, expected in manifest["files"].items():
        if Path(name).name != name or digest((model_dir / name).read_bytes()) != expected:
            raise ValueError("Candidate asset digest mismatch")
    return digest(path.read_bytes())


def qualification(
    corpus, packet_dir, gold_path, review_a, review_b, adjudication, model_dir, output
):
    if output.exists():
        raise ValueError("Qualification output already exists; preserve immutable results")
    rows, manifest = load_packet(corpus, packet_dir)
    audit = audit_scenarios(rows, packet_dir / "coordinator/scenarios.csv")
    # Re-import and compare content, not a caller-controlled 'adjudicated' boolean.
    rebuilt = import_reviews(corpus, packet_dir, review_a, review_b, adjudication, None)
    gold = json.loads(gold_path.read_text())
    if gold != rebuilt:
        raise ValueError("Adjudication differs from validated source review inputs")
    if not audit["complete"]:
        raise ValueError("Full semantic scenario review required before qualification")
    if any(r["independent"] != "true" for c in gold["cases"] for r in c["reviews"]):
        raise ValueError("Independent reviewers and adjudicator required")
    cases = [
        c
        for c in gold["cases"]
        if audit["documents"][c["document_id"]]["scenario_id"] not in audit["exposed_scenarios"]
    ]
    excluded = sorted({c["document_id"] for c in gold["cases"]} - {c["document_id"] for c in cases})
    if not cases:
        raise ValueError("No unexposed qualification cases")
    unresolved = [
        c["document_id"]
        for c in cases
        if any(f["status"] in {"unknown", "conflict"} for f in c["fields"].values())
    ]
    if unresolved:
        raise ValueError("Qualification fields remain unresolved")
    ledger = corpus / "independent_qualification_use.json"
    if ledger.exists():
        raise ValueError("Qualification split already exposed; use engineering regression")
    if not coverage(cases)["all_required_positive_coverage"]:
        raise ValueError(
            "Required positive field coverage, including present/absent safety, is missing"
        )
    model_sha = model_identity(model_dir)
    model_manifest = json.loads((model_dir / "focused-model-manifest.json").read_text())
    if (
        model_manifest.get("corpus_manifest_sha256") != manifest["corpus_manifest_sha256"]
        or model_manifest.get("training_split") != "train"
        or model_manifest.get("selection_split") != "validation"
        or model_manifest.get("heldout_split") != "test"
    ):
        raise ValueError("Candidate training/selection provenance does not match frozen splits")
    from ip_registry_contracts.models import ExtractionRequest
    from ip_registry_engine.engine import LocalDeterministicProvider

    from ops.tools.eval_robotic_ebus import baseline_facts, focused_facts

    provider = LocalDeterministicProvider(model_dir)
    if provider.ner is None:
        raise ValueError("Candidate NER unavailable; degraded inference is not qualification")
    # Reserve before any held-out inference, atomically. Keep even on failure.
    ledger = corpus / "independent_qualification_use.json"
    reservation = {
        "corpus_manifest_sha256": manifest["corpus_manifest_sha256"],
        "gold_sha256": digest(gold_path.read_bytes()),
        "model_manifest_sha256": model_sha,
        "scenario_audit_sha256": audit["sha256"],
        "reserved_at": datetime.now(UTC).isoformat(),
        "document_ids": sorted(c["document_id"] for c in cases),
        "policy": "All test material now exposed; never reuse for independent qualification",
    }
    with ledger.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(reservation, indent=2) + "\n")
    actual, relations, baseline, errors = {}, {}, {}, []
    baseline_error = None
    try:
        from app.registry.application.registry_service import RegistryService

        service = RegistryService()
        ner = getattr(getattr(service, "parallel_orchestrator", None), "ner_predictor", None)
        predictor = getattr(service, "_registry_ml_predictor", None)
        if not getattr(ner, "available", False) or not getattr(predictor, "available", False):
            raise ValueError("Baseline model dependencies unavailable")
    except Exception as exc:
        service = None
        baseline_error = type(exc).__name__
    for case in cases:
        row = rows[case["document_id"]]
        key = row["document_id"]
        try:
            result = provider.extract(
                ExtractionRequest(
                    job_id=uuid4(),
                    source_document_id=uuid4(),
                    source_digest=row["text_sha256"],
                    text=row["text"],
                    kind="procedure",
                )
            )
            inference = result.observations.get("inference", {})
            if (
                result.status != "proposed"
                or inference.get("ner_available") is not True
                or inference.get("model_manifest_digest") != model_sha
            ):
                raise ValueError("Candidate inference degraded or model identity changed")
            actual[key] = focused_facts(result.observations)
            relations[key] = relationship_facts(result.observations)
        except Exception as exc:
            errors.append({"document_id": key, "engine": "candidate", "error": type(exc).__name__})
        if service is not None:
            try:
                result = service.extract_fields_extraction_first(row["text"])
                value = result.registry if hasattr(result, "registry") else result.record
                baseline[key] = baseline_facts(value.model_dump())
            except Exception as exc:
                errors.append(
                    {"document_id": key, "engine": "baseline", "error": type(exc).__name__}
                )
    candidate_score = score(cases, actual, "expected")
    relation_score = score(cases, relations, "expected_relationships")
    baseline_score = score(cases, baseline, "expected")
    support = coverage(cases)
    preserved = service is not None and all(
        (candidate_score["metrics"][f][m] or 0) >= (baseline_score["metrics"][f][m] or 0)
        for f in FIELDS
        for m in ("precision", "recall")
    )
    checks = {
        "required_positive_coverage": support["all_required_positive_coverage"],
        "field_thresholds": targets_met(candidate_score),
        "relationship_thresholds": targets_met(relation_score),
        "baseline_preserved": preserved,
        "runtime_success": not errors and baseline_error is None,
    }
    blockers = [key for key, passed in checks.items() if not passed]
    report = {
        "schema_version": "robotic_ebus.independent_qualification.v1",
        "synthetic_only": True,
        "clinical_validation": False,
        "promotion_allowed": False,
        "independent_synthetic_qualification_passed": all(checks.values()),
        "precision_target": 0.98,
        "recall_target": 0.95,
        "binding": reservation,
        "source_code_sha256": {
            path.relative_to(ROOT).as_posix(): digest(path.read_bytes())
            for directory in (ROOT / "packages/ip_registry_engine/src", ROOT / "app/registry")
            for path in sorted(directory.rglob("*.py"))
        },
        "qualified_documents": len(cases),
        "excluded_exposed_documents": excluded,
        "coverage": support,
        "checks": checks,
        "candidate": candidate_score,
        "relationships": relation_score,
        "baseline": baseline_score,
        "errors": errors,
        "baseline_initialization_error": baseline_error,
        "blocked_reasons": blockers
        + [
            "synthetic_is_not_clinical_validation",
            "format_qualification_pending",
            "independent_operational_and_release_review_pending",
        ],
        "scope": (
            "Synthetic source text only; lobe-level localization attribution. "
            "No clinical or PDF/OCR qualification."
        ),
    }
    save(output, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "corpus",
        "packet",
        "gold",
        "review-a",
        "review-b",
        "adjudication",
        "model-dir",
        "output",
    ):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--require-acceptance", action="store_true")
    args = parser.parse_args(argv)
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
    try:
        report = qualification(
            args.corpus,
            args.packet,
            args.gold,
            args.review_a,
            args.review_b,
            args.adjudication,
            args.model_dir,
            args.output,
        )
    except (ValueError, KeyError, OSError) as exc:
        # Always emit a machine-readable failed gate (but never overwrite prior results).
        report = {
            "schema_version": "robotic_ebus.independent_qualification.v1",
            "promotion_allowed": False,
            "clinical_validation": False,
            "independent_synthetic_qualification_passed": False,
            "blocked_reasons": ["input_validation_failed"],
            "error": str(exc),
        }
        if not args.output.exists():
            save(args.output, report)
        print(json.dumps(report))
        return 2
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k in {"checks", "blocked_reasons", "promotion_allowed"}
            }
        )
    )
    return (
        2
        if args.require_acceptance or not report["independent_synthetic_qualification_passed"]
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
