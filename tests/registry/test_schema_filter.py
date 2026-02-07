from __future__ import annotations

from app.registry.schema_filter import filter_schema_properties


def test_schema_filtering_keeps_universal_fields():
    schema_props = {
        "patient_mrn": {"type": "string"},  # universal
        "ebus_scope_brand": {"type": "string"},  # EBUS
        "nav_platform": {"type": "string"},  # NAVIGATION
    }

    # No gating (None) -> include all
    out = filter_schema_properties(schema_props, None)
    assert set(out.keys()) == {"patient_mrn", "ebus_scope_brand", "nav_platform"}

    # Empty set -> only universal fields
    out = filter_schema_properties(schema_props, set())
    assert set(out.keys()) == {"patient_mrn"}


def test_schema_filtering_respects_active_families():
    schema_props = {
        "patient_mrn": {"type": "string"},  # universal
        "ebus_scope_brand": {"type": "string"},  # EBUS
        "nav_platform": {"type": "string"},  # NAVIGATION
    }

    out = filter_schema_properties(schema_props, {"EBUS"})
    assert set(out.keys()) == {"patient_mrn", "ebus_scope_brand"}

    out = filter_schema_properties(schema_props, {"NAVIGATION"})
    assert set(out.keys()) == {"patient_mrn", "nav_platform"}


