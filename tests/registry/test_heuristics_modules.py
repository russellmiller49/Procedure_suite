from __future__ import annotations

from app.registry.constants import LINEAR_EBUS_PERFORMED, TBNA_CONVENTIONAL_PERFORMED
from app.registry.heuristics import (
    apply_heuristics,
    coverage_failures,
    reconcile_granular_validation_warnings,
)
from app.registry.schema import RegistryRecord


def test_apply_heuristics_runs_in_order_and_accumulates_warnings() -> None:
    calls: list[str] = []

    class H1:
        def apply(self, note_text: str, record: RegistryRecord) -> tuple[RegistryRecord, list[str]]:
            assert note_text == "note"
            calls.append("h1")
            return record, ["warn_1"]

    class H2:
        def apply(self, note_text: str, record: RegistryRecord) -> tuple[RegistryRecord, list[str]]:
            assert note_text == "note"
            calls.append("h2")
            return record, ["warn_2"]

    record = RegistryRecord()
    _, warnings = apply_heuristics(note_text="note", record=record, heuristics=(H1(), H2()))

    assert calls == ["h1", "h2"]
    assert warnings == ["warn_1", "warn_2"]


def test_reconcile_granular_validation_warnings_drops_stale_paths() -> None:
    stale_warning = f"conflict: {LINEAR_EBUS_PERFORMED}"
    retained_warning = f"conflict: {TBNA_CONVENTIONAL_PERFORMED}"

    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {"performed": False},
                "tbna_conventional": {"performed": True},
            },
            "granular_validation_warnings": [stale_warning, retained_warning, "generic warning"],
        }
    )

    cleaned, removed = reconcile_granular_validation_warnings(record)

    assert stale_warning in removed
    assert retained_warning in cleaned.granular_validation_warnings
    assert "generic warning" in cleaned.granular_validation_warnings


def test_coverage_failures_flags_missing_linear_ebus() -> None:
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"linear_ebus": {"performed": False}}}
    )

    failures = coverage_failures("EBUS Findings: station 7 sampled", record)

    assert "linear_ebus missing" in failures
