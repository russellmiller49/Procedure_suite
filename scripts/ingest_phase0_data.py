#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from modules.registry.schema.ip_v3 import (
    EvidenceSpan,
    IPRegistryV3,
    LesionDetails,
    Outcomes,
    ProcedureEvent,
    ProcedureTarget,
)


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value)) or (isinstance(value, str) and not value.strip())


def _get_str(row: pd.Series, column: str) -> str | None:
    if column not in row:
        return None
    value = row[column]
    if _is_missing(value):
        return None
    return str(value)


def _get_float(row: pd.Series, column: str) -> float | None:
    if column not in row:
        return None
    value = row[column]
    if _is_missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_json_value(row: pd.Series, column: str) -> Any | None:
    raw = _get_str(row, column)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _parse_json_list(row: pd.Series, column: str) -> list[str]:
    value = _parse_json_value(row, column)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if not _is_missing(item)]
    return []


def row_to_event(row: pd.Series) -> ProcedureEvent:
    target = ProcedureTarget(
        anatomy_type=_get_str(row, "target.anatomy_type"),
        lobe=_get_str(row, "target.location.lobe"),
        segment=_get_str(row, "target.location.segment"),
        station=_get_str(row, "target.station"),
    )

    lesion = LesionDetails(
        lesion_type=_get_str(row, "lesion.type"),
        size_mm=_get_float(row, "lesion.size_mm"),
    )

    outcomes = Outcomes(
        airway_lumen_pre=_get_str(row, "outcomes.airway.lumen_pre"),
        airway_lumen_post=_get_str(row, "outcomes.airway.lumen_post"),
        symptoms=_get_str(row, "outcomes.symptoms"),
        pleural=_get_str(row, "outcomes.pleural"),
        complications=_get_str(row, "outcomes.complications"),
    )

    evidence_quote = _get_str(row, "evidence_quote")
    evidence = EvidenceSpan(quote=evidence_quote) if evidence_quote else None

    return ProcedureEvent(
        event_id=str(row["event_id"]),
        type=str(row["type"]),
        method=_get_str(row, "method"),
        target=target,
        lesion=lesion,
        devices=_parse_json_list(row, "devices_json"),
        specimens=_parse_json_list(row, "specimens_json"),
        outcomes=outcomes,
        evidence=evidence,
        measurements=_parse_json_value(row, "measurements_json"),
        findings=_parse_json_value(row, "findings_json"),
        stent_size=_get_str(row, "stent.size"),
        stent_material_or_brand=_get_str(row, "stent.material_or_brand"),
        catheter_size_fr=_get_float(row, "catheter.size_fr"),
    )


def _default_index_csv(events_csv: Path) -> Path:
    candidate = events_csv.parent / "Note_Index.csv"
    if candidate.exists():
        return candidate
    candidate = events_csv.parent / "note_index.csv"
    if candidate.exists():
        return candidate
    return events_csv.parent / "Note_Index.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest Phase 0 granular CSVs into V3 golden JSON registry files.")
    parser.add_argument(
        "--events-csv",
        type=Path,
        default=Path("data/registry_granular/csvs/V3_Procedure_events.csv"),
        help="Path to V3_Procedure_events.csv",
    )
    parser.add_argument(
        "--index-csv",
        type=Path,
        default=None,
        help="Path to Note_Index.csv (or note_index.csv); default searches next to events CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/knowledge/golden_registry_v3"),
        help="Directory to write {note_id}.json files",
    )
    args = parser.parse_args()

    events_csv: Path = args.events_csv
    index_csv: Path = args.index_csv or _default_index_csv(events_csv)
    output_dir: Path = args.output_dir

    if not events_csv.exists():
        raise FileNotFoundError(f"Events CSV not found: {events_csv}")
    if not index_csv.exists():
        raise FileNotFoundError(f"Index CSV not found: {index_csv}")

    output_dir.mkdir(parents=True, exist_ok=True)

    events_df = pd.read_csv(events_csv)
    index_df = pd.read_csv(index_csv)

    if "note_id" not in events_df.columns:
        raise ValueError(f"Events CSV missing required column 'note_id': {events_csv}")
    if "note_id" not in index_df.columns or "source_file" not in index_df.columns:
        raise ValueError(f"Index CSV must include 'note_id' and 'source_file': {index_csv}")

    note_id_to_source = (
        index_df[["note_id", "source_file"]].dropna(subset=["note_id"]).astype({"note_id": str}).set_index("note_id")[
            "source_file"
        ]
    ).to_dict()

    written = 0
    for note_id, group in events_df.groupby("note_id", dropna=True):
        note_id_str = str(note_id)
        source_filename = str(note_id_to_source.get(note_id_str, f"{note_id_str}.txt"))

        procedures = [row_to_event(row) for _, row in group.iterrows()]
        registry = IPRegistryV3(note_id=note_id_str, source_filename=source_filename, procedures=procedures)

        out_path = output_dir / f"{note_id_str}.json"
        out_path.write_text(json.dumps(registry.model_dump(mode="json"), indent=2, sort_keys=True) + "\n")
        written += 1

    print(f"Wrote {written} registry files to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
