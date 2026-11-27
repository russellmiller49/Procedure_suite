"""Field profile for review pages: schema, section titles and dictionary help.

Kept free of database imports so pages that never touch the workbench store
(the public demo) can serve the same profile.
"""

from __future__ import annotations

from typing import Any

from ip_registry_contracts.launch import PROFILE, VERSION
from ip_registry_contracts.models import ClinicalRevision

from app.registry_workbench.extraction.contract_spec import dictionary_fields

SECTION_TITLES = {
    "procedures": "Procedure components",
    "case_details": "Case and anesthesia",
    "targets": "Lung and nodal targets",
    "ebus_sessions": "Linear EBUS examination",
    "station_surveys": "Stations surveyed and sampled",
    "navigation_runs": "Robotic navigation",
    "localization_events": "Localization and tool confirmation",
    "sampling_acquisitions": "Sampling acquisitions",
    "specimens": "Specimens and attribution",
    "sampling_specimen_links": "Acquisition-to-specimen links",
    "pathology_results": "Pathology and amendments",
    "complications": "Immediate and interval complications",
    "follow_up": "30-day safety",
}


def profile() -> dict[str, Any]:
    help_text = {}
    for path, entry in dictionary_fields().items():
        help_text[path] = {
            key: entry.get(source)
            for key, source in (
                ("definition", "definition"),
                ("units", "contract_units"),
                ("applies", "required_when"),
                ("notes", "validation_notes"),
                ("tier", "collection_tier"),
                ("capture", "capture_method"),
            )
            if entry.get(source)
        }
    return {
        "registry_profile": PROFILE,
        "schema_version": VERSION,
        "schema": ClinicalRevision.model_json_schema(),
        "sections": SECTION_TITLES,
        "help": help_text,
    }


__all__ = ["SECTION_TITLES", "profile"]
