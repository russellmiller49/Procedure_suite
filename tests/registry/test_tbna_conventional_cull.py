from __future__ import annotations

from app.registry.postprocess import cull_tbna_conventional_against_ebus_sampling
from app.registry.schema import RegistryRecord


def test_cull_tbna_conventional_when_linear_ebus_sampled_and_tbna_has_no_sites() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {"performed": True, "stations_sampled": ["2L"]},
                "tbna_conventional": {"performed": True},
            }
        }
    )

    warnings = cull_tbna_conventional_against_ebus_sampling(record, "EBUS-TBNA of station 2L performed.")
    assert any("Culled tbna_conventional" in w for w in warnings)

    assert record.procedures_performed is not None
    assert record.procedures_performed.tbna_conventional is not None
    assert record.procedures_performed.tbna_conventional.performed is False


def test_cull_tbna_conventional_does_not_cull_when_tbna_has_distinct_non_station_site() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {"performed": True, "stations_sampled": ["2L"]},
                "tbna_conventional": {"performed": True, "stations_sampled": ["lung lesion"]},
            }
        }
    )

    warnings = cull_tbna_conventional_against_ebus_sampling(record, "Transbronchial needle aspiration of lung lesion.")
    assert not warnings

    assert record.procedures_performed is not None
    assert record.procedures_performed.tbna_conventional is not None
    assert record.procedures_performed.tbna_conventional.performed is True

