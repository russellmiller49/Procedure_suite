"""Tests for EBUS and TBLB slot extractors."""

from modules.common.sectionizer import SectionizerService
from modules.registry.slots.ebus import EbusExtractor
from modules.registry.slots.tblb import TBLBExtractor


def _sections(text: str):
    return SectionizerService().sectionize(text)


def test_ebus_slot_detects_navigation_radial_and_stations() -> None:
    text = """
    PROCEDURE:
    Electromagnetic navigation bronchoscopy performed with ENB guidance.
    Radial EBUS probe confirmed lesion; stations 4R and station 7 sampled.
    """
    sections = _sections(text)
    result = EbusExtractor().extract(text, sections)
    assert result.value["navigation"] is True
    assert result.value["radial"] is True
    assert set(result.value["stations"]) == {"4R", "7"}
    assert result.confidence >= 0.6


def test_tblb_slot_extracts_lobes() -> None:
    text = """
    FINDINGS:
    Multiple biopsies were obtained from the right upper lobe (RUL) and left lower lobe.
    """
    sections = _sections(text)
    result = TBLBExtractor().extract(text, sections)
    assert set(result.value) == {"RUL", "LLL"}
    assert result.evidence
