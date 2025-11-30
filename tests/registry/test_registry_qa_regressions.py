import os
from textwrap import dedent

import pytest

from modules.registry.engine import RegistryEngine
from modules.registry.postprocess import VALID_EBUS_STATIONS


@pytest.fixture
def engine():
    os.environ["REGISTRY_USE_STUB_LLM"] = "true"
    return RegistryEngine()


def test_bal_and_single_station_ebus_no_hallucinated_station(engine):
    note = dedent(
        """
        Initial Airway Inspection Findings:
        Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius , and Left Mainstem from mucus.

        Bronchial alveolar lavage was performed at Anterior Segment of RUL (RB3). Instilled 60 cc of NS, suction returned with 20 cc of NS. Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

        EBUS-Findings
        Indications: Diagnostic
        Technique:
        All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled.

        Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 22-gauge Needle and 19-gauge Needle.

        Lymph Nodes/Sites Inspected: 4R (lower paratracheal) node

        Overall ROSE Diagnosis: Positive for malignancy
        """
    )

    record = engine.run(note)

    assert "EBUS" in record.procedure_families
    assert "BAL" in record.procedure_families
    stations = set(record.linear_ebus_stations or [])
    assert stations == {"4R"}
    detail_stations = {d["station"] for d in (record.ebus_stations_detail or [])}
    assert detail_stations == {"4R"}
    assert record.bronch_num_tbbx is None
    assert record.bronch_tbbx_tool is None


def test_stent_removal_with_multistation_ebus_keeps_valid_stations(engine):
    note = dedent(
        """
        After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
        Airway exam notable for metallic stent in the BI widely patent though with moderate thick secretions within it.
        The foreign body (stent) was grasped with rat tooth forceps and removed en bloc and sent for pathology.

        EBUS-Findings
        Lymph Nodes/Sites Inspected: 4R (lower paratracheal) node
        4L (lower paratracheal) node
        7 (subcarinal) node
        11Rs lymph node
        11Ri lymph node
        11L lymph node
        12R lymph node deep in the RML airway
        Overall ROSE Diagnosis: Suggestive of benign-appearing lymphoid tissue
        """
    )

    record = engine.run(note)

    assert "STENT" in record.procedure_families
    assert "CAO" in record.procedure_families
    stations = set((record.ebus_stations_sampled or []) + (record.linear_ebus_stations or []))
    assert stations  # should capture at least the explicitly sampled stations
    assert stations.issubset(VALID_EBUS_STATIONS)
    assert "2R" not in stations  # guard against 12R -> 2R clipping


def test_navigation_aborted_tbna_does_not_invent_station_seven(engine):
    note = dedent(
        """
        Indications: right lower lobe nodule
        Navigational catheter mis-registered; converted to conventional bronchoscopy.
        A concentric EBUS view was seen but station numbers were not documented.
        TBNAs were obtained and ROSE showed lymphocytes.
        """
    )

    record = engine.run(note)
    stations = set(record.linear_ebus_stations or [])
    assert "7" not in stations
    assert stations.issubset(VALID_EBUS_STATIONS)


def test_y_stent_cao_case_does_not_add_ebus_stations(engine):
    note = dedent(
        """
        PROCEDURE PERFORMED: Rigid bronchoscopy with tumor debulking and silicone tracheobronchial Y-stent placement
        Sedation: General Anesthesia
        Indication: Airway obstruction/hemoptysis
        The stent was deployed in the trachea and mainstem bronchi. No EBUS or lymph node sampling was performed.
        """
    )

    record = engine.run(note)

    assert "STENT" in record.procedure_families
    assert "CAO" in record.procedure_families
    assert not record.linear_ebus_stations
    assert not record.ebus_stations_sampled
    assert not record.ebus_stations_detail


def test_pleural_thoracoscopy_resets_airway_stent_state(engine):
    note = dedent(
        """
        Procedure Name: Medical Thoracoscopy (pleuroscopy) with parietal pleural biopsies
        Indications: Left sided pleural effusion
        The pleural entry site was identified and trocars were placed. Multiple pleural biopsies obtained.
        No airway stents were placed or manipulated.
        """
    )

    record = engine.run(note)

    assert "THORACOSCOPY" in record.procedure_families or "PLEURAL" in record.procedure_families
    assert record.stent_type is None
    assert record.stent_location is None
    assert record.cao_location is None
