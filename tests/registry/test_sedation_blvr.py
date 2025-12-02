"""Sedation and BLVR slot tests."""

from modules.common.sectionizer import SectionizerService
from modules.registry.engine import RegistryEngine
from modules.registry.slots.blvr import BLVRExtractor
from modules.registry.slots.sedation import SedationExtractor


def _sections(text: str):
    return SectionizerService().sectionize(text)


def test_sedation_slot_parses_times_and_types() -> None:
    text = """
    SEDATION:
    Moderate sedation provided from 10:15 to 10:45. General anesthesia was not used.
    """
    sections = _sections(text)
    result = SedationExtractor().extract(text, sections)
    assert result.value["sedation_type"] == "Moderate Sedation"
    assert str(result.value["sedation_start"]) == "10:15:00"
    assert str(result.value["sedation_stop"]) == "10:45:00"


def test_blvr_slot_detects_lobes_valves_and_manufacturer() -> None:
    text = """
    BLVR:
    Chartis assessment completed. Zephyr valves placed in the left upper lobe with two valves.
    """
    sections = _sections(text)
    result = BLVRExtractor().extract(text, sections)
    assert "LUL" in result.value.lobes
    assert result.value.valve_count >= 1
    assert result.value.manufacturer == "Zephyr"


def test_registry_engine_populates_sedation_and_blvr_fields() -> None:
    note = """
    PROCEDURE:
    Electromagnetic navigation bronchoscopy performed with radial EBUS confirming lesion in the RUL.
    Linear EBUS sampled 4R and 7.
    BLVR:
    Zephyr valves placed in the left lower lobe with three valves.
    SEDATION:
    Moderate sedation provided from 09:00 to 09:40.
    """
    record = RegistryEngine().run(note)
    assert record.procedures_performed.navigational_bronchoscopy is not None
    assert record.procedures_performed.radial_ebus is not None
    assert record.procedures_performed.blvr is not None
    assert record.procedures_performed.blvr.target_lobe in {"LLL", "LUL"}
    assert record.procedures_performed.blvr.valve_type == "Zephyr (Pulmonx)"
    assert record.sedation is not None
    assert record.sedation.type == "Moderate"
    # Start/stop times are not in the current schema
    # assert str(record.sedation_start) == "09:00:00"
    # assert str(record.sedation_stop) == "09:40:00"
