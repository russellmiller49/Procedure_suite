import os

import pytest

from modules.registry.engine import RegistryEngine


@pytest.fixture
def engine():
    os.environ["REGISTRY_USE_STUB_LLM"] = "true"
    return RegistryEngine()


def test_ebus_pass_counts_and_elastography(engine):
    note = """
    PROCEDURE: EBUS with TBNA

    TECHNIQUE:
    Linear EBUS performed. Station 4R sampled with three passes using a 22G needle.
    Station 7 sampled with two passes. Elastography demonstrated predominantly blue pattern.
    """
    record = engine.run(note)

    assert "EBUS" in record.procedure_families
    assert record.linear_ebus_stations and set(record.linear_ebus_stations) >= {"4R", "7"}
    assert record.ebus_needle_gauge == "22G"
    assert record.ebus_elastography_pattern is not None

    detail_by_station = {d["station"]: d for d in (record.ebus_stations_detail or []) if d.get("station")}
    assert detail_by_station.get("4R", {}).get("passes") == 3
    assert detail_by_station.get("7", {}).get("passes") == 2
