from types import SimpleNamespace

import pytest

from modules.registry.engine import RegistryEngine


class _StubExtractor:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def extract(self, _text, _sections, context=None):  # type: ignore[no-untyped-def]
        return SimpleNamespace(value=self._payload)


def test_invalid_enum_list_items_do_not_drop_registry_section(caplog: pytest.LogCaptureFixture) -> None:
    engine = RegistryEngine(
        llm_extractor=_StubExtractor(
            {
                "granular_data": {
                    "navigation_targets": [
                        {
                            "target_number": 1,
                            "target_location_text": "RUL nodule",
                            "sampling_tools_used": ["Needle", None],
                        }
                    ]
                }
            }
        )
    )

    with caplog.at_level("WARNING"):
        record = engine.run("PROCEDURE: Navigational bronchoscopy performed.")

    dumped = record.model_dump()
    assert dumped.get("granular_data") is not None

    nav_targets = dumped["granular_data"]["navigation_targets"]
    assert nav_targets[0]["sampling_tools_used"] == ["Needle"]

    assert any(
        "sampling_tools_used" in rec.message and "Dropped" in rec.message for rec in caplog.records
    )


def test_pruning_warning_includes_paths_and_error_summary(caplog: pytest.LogCaptureFixture) -> None:
    engine = RegistryEngine(
        llm_extractor=_StubExtractor({"patient_demographics": {"height_cm": ["175 cm"]}})
    )

    with caplog.at_level("WARNING"):
        _ = engine.run("PROCEDURE: Bronchoscopy performed.")

    pruning_logs = [rec.message for rec in caplog.records if "validation required pruning" in rec.message]
    assert pruning_logs

    message = pruning_logs[0]
    assert "patient_demographics.height_cm" in message
    assert "Pruned:" in message
    assert "Error summary:" in message
