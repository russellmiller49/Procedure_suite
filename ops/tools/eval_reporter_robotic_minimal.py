#!/usr/bin/env python3
"""Strict reporter smoke and source-slot evaluation for short robotic/EBUS prompts.

Run from the repository root. Uses the real registry seed path with the same
offline defaults as the standard baseline evaluator. This supplements, rather
than replaces, the shared extraction/CPT quality gates.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def observed_slots(bundle: dict) -> dict:
    def data(kind):
        return [p["data"] for p in bundle["procedures"] if p["proc_type"] == kind]

    return {
        "no_stent": not data("airway_stent_placement"),
        "tbna_counts": [
            p.get("samples_collected") for p in data("transbronchial_needle_aspiration")
        ],
        "cryo_counts": [p.get("num_samples") for p in data("transbronchial_cryobiopsy")],
        "brush_counts": [p.get("samples_collected") for p in data("bronchial_brushings")],
        "node_passes": {
            s["station_name"].upper(): s.get("passes")
            for p in data("ebus_tbna")
            for s in p["stations"]
        },
        "survey_only": bool(data("ebus_survey")) and not data("ebus_tbna"),
        "elastography_used": any(
            p.get("elastography_used") for p in data("ebus_tbna") + data("ebus_survey")
        ),
        "node_elastography": {
            s["station_name"].upper(): s["elastography_pattern"]
            for p in data("ebus_tbna") + data("ebus_survey")
            for s in p["stations"]
            if s.get("elastography_pattern")
        },
        "bal": [
            [p.get("lung_segment"), p.get("instilled_volume_cc"), p.get("returned_volume_cc")]
            for p in data("bal")
        ],
        "ebus_needle_gauge": [p.get("needle_gauge") for p in data("ebus_tbna")],
        "registration": [p.get("registration_method") for p in data("robotic_navigation")],
        "ct_attestation": any(p.get("physician_interpreted") for p in data("cbct_cact_fusion")),
        "anesthesia": (bundle.get("anesthesia") or {}).get("description"),
        "ebl": bundle.get("estimated_blood_loss"),
        "complications": bundle.get("complications_text"),
        "closing_text": bundle.get("closing_text"),
        "first_block": min(
            (p for p in bundle["procedures"] if p.get("sequence") is not None),
            key=lambda p: p["sequence"],
            default={},
        ).get("proc_type"),
    }


def check_slots(bundle: dict, expected: dict) -> list[dict]:
    actual = observed_slots(bundle)
    return [
        {"slot": key, "expected": value, "actual": actual[key]}
        for key, value in expected.items()
        if value != actual[key]
    ]


# Opening words of each PROCEDURE IN DETAIL block (short-prompt prose branch)
# and of each PROCEDURE header line, keyed by procedure type.
DETAIL_ANCHORS = {
    "robotic_navigation": r"Robotic navigation bronchoscopy was performed",
    "radial_ebus_survey": r"Radial EBUS was performed",
    "cbct_cact_fusion": r"Cone Beam CT was performed",
    "tool_in_lesion_confirmation": r"Tool-in-lesion was confirmed",
    "transbronchial_needle_aspiration": r"Transbronchial needle aspiration was performed",
    "transbronchial_lung_biopsy": r"Transbronchial biopsy was performed",
    "transbronchial_cryobiopsy": r"Transbronchial cryobiopsy was performed",
    "bronchial_brushings": r"Transbronchial brushing was performed",
    "bal": r"Bronchoalveolar lavage was performed",
    "fiducial_marker_placement": r"A fiducial marker",
    "ebus_tbna": r"Linear EBUS-TBNA",
    "ebus_survey": r"Linear EBUS survey",
}
HEADER_ANCHORS = {
    "robotic_navigation": r"Robotic navigational bronchoscopy",
    "radial_ebus_survey": r"Radial EBUS localization",
    "cbct_cact_fusion": r"Cone-beam CT imaging",
    "tool_in_lesion_confirmation": r"Tool-in-lesion confirmation",
    "transbronchial_needle_aspiration": r"(?:Transbronchial needle aspiration|TBNA) of",
    "transbronchial_lung_biopsy": r"Transbronchial forceps biopsy of",
    "transbronchial_cryobiopsy": r"Transbronchial Cryobiopsy",
    "bronchial_brushings": r"Bronchial brushings",
    "bal": r"Bronchoalveolar lavage",
    "fiducial_marker_placement": r"Fiducial marker placement",
    "ebus_tbna": r"(?:Linear EBUS-TBNA|Endobronchial Ultrasound-Guided)",
    "ebus_survey": r"Linear EBUS lymph node survey",
}
_NAVIGATION = {"robotic_navigation"}
_LOCALIZATION = {"radial_ebus_survey", "cbct_cact_fusion", "tool_in_lesion_confirmation"}
_TISSUE = {
    "transbronchial_needle_aspiration",
    "transbronchial_lung_biopsy",
    "transbronchial_cryobiopsy",
}
_NODAL = {"ebus_tbna", "ebus_survey"}


def _section(markdown: str, start: str, ends: tuple[str, ...]) -> str:
    import re

    begin = re.search(r"(?m)^" + start + r"[ \t]*$", markdown)
    if not begin:
        return ""
    body = markdown[begin.end() :]
    stops = [m.start() for end in ends if (m := re.search(r"(?m)^" + end, body))]
    return body[: min(stops)] if stops else body


def _blocks(text: str, anchors: dict[str, str]) -> list[str]:
    """Procedure types in the order their blocks/lines appear (repeats kept)."""
    import re

    found = [
        (m.start(), kind)
        for kind, pattern in anchors.items()
        for m in re.finditer(r"(?m)^" + pattern, text)
    ]
    return [kind for _, kind in sorted(found)]


def _first_occurrence(kinds: list[str]) -> list[str]:
    return list(dict.fromkeys(kinds))


def observed_order(markdown: str) -> dict:
    detail = _section(
        markdown, "PROCEDURE IN DETAIL", ("ESTIMATED BLOOD LOSS", "SPECIMENS", "IMPRESSION")
    )
    header = _section(markdown, "PROCEDURE", ("ANESTHESIA", "FINDINGS", "PROCEDURE IN DETAIL"))
    return {
        "detail_blocks": _blocks(detail, DETAIL_ANCHORS),
        "header_lines": _blocks(header, HEADER_ANCHORS),
    }


def check_order(markdown: str, expected: dict | None = None) -> list[str]:
    """Workflow-order failures in a rendered short-prompt report.

    The invariants hold in all eleven source operative reports: navigation,
    then localization, then tissue sampling; a fiducial marker after tissue
    sampling; nodal EBUS after the peripheral target work. Brushing/lavage
    order relative to the marker and to EBUS varies in the sources, so it is
    only checked when a case supplies an explicit ``detail_order``.
    """
    expected = expected or {}
    order = observed_order(markdown)
    blocks = order["detail_blocks"]
    failures = []

    def first(kinds):
        return min((i for i, kind in enumerate(blocks) if kind in kinds), default=None)

    def last(kinds):
        return max((i for i, kind in enumerate(blocks) if kind in kinds), default=None)

    nav, loc, tissue = first(_NAVIGATION), first(_LOCALIZATION), first(_TISSUE)
    marker, nodal = first({"fiducial_marker_placement"}), first(_NODAL)
    peripheral_last = last(_NAVIGATION | _LOCALIZATION | _TISSUE | {"fiducial_marker_placement"})
    if nav is not None and any(x is not None and x < nav for x in (loc, tissue, marker)):
        failures.append("navigation is not the first peripheral step")
    if loc is not None and tissue is not None and loc > tissue:
        failures.append("localization follows tissue sampling")
    if marker is not None:
        if (nav is not None and marker < nav) or (loc is not None and marker < loc):
            failures.append("fiducial precedes navigation/localization")
        if tissue is not None and marker < tissue:
            failures.append("fiducial precedes tissue sampling")
    if expected.get("ebus_first"):
        # Only an explicit "EBUS first" selection may move the nodal block ahead.
        if nodal != 0:
            failures.append("nodal EBUS is not first despite the EBUS-first selection")
    elif nodal is not None and peripheral_last is not None and nodal < peripheral_last:
        failures.append("nodal EBUS precedes peripheral target work")

    detail_first = _first_occurrence(blocks)
    header_first = _first_occurrence(order["header_lines"])
    shared = set(detail_first) & set(header_first)
    if [k for k in header_first if k in shared] != [k for k in detail_first if k in shared]:
        failures.append("PROCEDURE list order differs from PROCEDURE IN DETAIL")

    if "detail_order" in expected and blocks != expected["detail_order"]:
        failures.append(f"detail order {blocks} != expected {expected['detail_order']}")
    return failures


def check_rendered(bundle: dict, markdown: str) -> list[str]:
    """Facts held in the bundle that never reached PROCEDURE IN DETAIL."""
    import re

    detail = _section(
        markdown, "PROCEDURE IN DETAIL", ("ESTIMATED BLOOD LOSS", "SPECIMENS", "IMPRESSION")
    )
    failures = []
    for proc in bundle["procedures"]:
        kind, data = proc["proc_type"], proc["data"]
        anchor = DETAIL_ANCHORS.get(kind)
        if anchor and not re.search(r"(?m)^" + anchor, detail):
            failures.append(f"{kind} block not rendered")
        if kind in _NODAL:
            for station in data.get("stations", []):
                if station["station_name"] not in detail:
                    failures.append(f"station {station['station_name']} not rendered")
                pattern = station.get("elastography_pattern")
                if pattern and pattern not in detail:
                    failures.append(f"station {station['station_name']} {pattern} not rendered")
            if data.get("elastography_used") and "elastography" not in detail:
                failures.append("elastography not rendered")
        gauge = data.get("needle_gauge")
        if kind == "transbronchial_needle_aspiration" and gauge and gauge not in detail:
            failures.append(f"needle gauge {gauge} not rendered")
    return failures


def check_ebus_warning_review(flags: list[dict], review: dict) -> list[str]:
    if not review:
        return []
    warnings = [f for f in flags if f["code"] == "EBUS_DETAILS_UNSPECIFIED"]
    failures = []
    if bool(warnings) != review["remaining_warning"]:
        failures.append("EBUS warning presence differs from source review")
    if warnings and warnings[0]["metadata"].get("missing_details") != review.get("missing_details"):
        failures.append("EBUS warning reasons differ from source review")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "tests/fixtures/reporting/robotic_ebus_minimal_prompts.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifacts-dir", type=Path)
    parser.add_argument(
        "--existing-artifacts",
        type=Path,
        help="Score saved bundles/summary without rerunning inference",
    )
    args = parser.parse_args()
    payload = json.loads(args.input.read_text())
    if not args.existing_artifacts:
        from ops.tools.eval_reporter_prompt_baseline import configure_eval_env

        configure_eval_env()
        from app.registry.application.registry_service import RegistryService
        from app.reporting.seed_inputs import ReporterSeedInputs
        from app.reporting.seed_pipeline import (
            run_reporter_seed_pipeline,
            seed_outcome_from_registry_result,
        )

        service = RegistryService()
    else:
        saved = {
            r["id"]: r for r in json.loads((args.existing_artifacts / "summary.json").read_text())
        }
    rows = []
    for row in payload["cases"]:
        try:
            if args.existing_artifacts:
                bundle = json.loads((args.existing_artifacts / (row["id"] + ".json")).read_text())
                markdown = (args.existing_artifacts / (row["id"] + ".md")).read_text()
                fallback = saved[row["id"]]["fallback"]
                flags = saved[row["id"]]["flags"]
            else:
                # Only prompt_text (and, when a case supplies them, the builder's
                # structured selections) enter the pipeline; expectations stay here.
                text = row["prompt_text"]
                result = service.extract_fields(text)
                out = run_reporter_seed_pipeline(
                    seed_outcome_from_registry_result(result, masked_seed_text=text),
                    note_text=text,
                    strict=True,
                    debug_enabled=False,
                    structured_inputs=(
                        ReporterSeedInputs.model_validate(row["structured_inputs"])
                        if row.get("structured_inputs")
                        else None
                    ),
                )
                bundle = out.bundle.model_dump(mode="json")
                markdown = out.markdown
                fallback = out.render_fallback_used
                flags = [
                    f
                    for f in out.quality_flags
                    if str(f.get("source", "")).startswith("quality_gate")
                ]
                if args.artifacts_dir:
                    args.artifacts_dir.mkdir(parents=True, exist_ok=True)
                    (args.artifacts_dir / (row["id"] + ".json")).write_text(
                        json.dumps(bundle, indent=2) + "\n"
                    )
                    (args.artifacts_dir / (row["id"] + ".md")).write_text(out.markdown)
            failures = check_slots(bundle, row.get("expected", {}))
            rows.append(
                {
                    "id": row["id"],
                    "render_fallback_used": fallback,
                    "slot_failures": failures,
                    "order_failures": check_order(markdown, row.get("expected_order")),
                    "render_failures": check_rendered(bundle, markdown),
                    "observed_order": observed_order(markdown),
                    "warning_review_failures": check_ebus_warning_review(
                        flags, row.get("ebus_warning_review", {})
                    ),
                    "observed": observed_slots(bundle),
                    "quality_flags": flags,
                }
            )
        except Exception as exc:
            rows.append({"id": row["id"], "error": str(exc)})
    summary = {
        "cases": len(rows),
        "errors": sum("error" in r for r in rows),
        "strict_render_fallbacks": sum(r.get("render_fallback_used", False) for r in rows),
        "slot_checks": sum(len(r.get("expected", {})) for r in payload["cases"]),
        "slot_failures": sum(len(r.get("slot_failures", [])) for r in rows),
        "order_failures": sum(len(r.get("order_failures", [])) for r in rows),
        "render_failures": sum(len(r.get("render_failures", [])) for r in rows),
        "warning_reviews": sum("ebus_warning_review" in r for r in payload["cases"]),
        "warning_review_failures": sum(len(r.get("warning_review_failures", [])) for r in rows),
        "cases_with_slot_failures": sum(bool(r.get("slot_failures")) for r in rows),
        "quality_flag_counts": dict(
            Counter(f["code"] for r in rows for f in r.get("quality_flags", []))
        ),
    }
    report = {
        "schema_version": "reporter_robotic_minimal_fidelity.v2",
        "source_sha256": payload["source_sha256"],
        "seed_strategy": "registry_extract_fields",
        "summary": summary,
        "cases": rows,
        "limitations": [
            "Order checks cover workflow invariants and curated dictation orders; "
            "render checks cover block presence, stations, elastography and needle gauge.",
            "Source-slot checks cover curated facts; "
            "successful rendering is not complete clinical validation.",
            "Extraction may fall back when model artifacts are unavailable; "
            "inspect the runtime log.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return int(
        bool(
            summary["errors"]
            or summary["strict_render_fallbacks"]
            or summary["slot_failures"]
            or summary["order_failures"]
            or summary["render_failures"]
            or summary["warning_review_failures"]
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
