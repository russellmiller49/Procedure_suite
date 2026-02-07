import os

import pytest

from app.registry.engine import RegistryEngine


@pytest.fixture
def engine():
    os.environ["REGISTRY_USE_STUB_LLM"] = "true"
    return RegistryEngine()


def test_thoracentesis_heuristics(engine):
    note = """
    PROCEDURE: Ultrasound-guided thoracentesis

    TECHNIQUE:
    Patient positioned sitting. Ultrasound used to identify a large right pleural effusion.
    18G needle inserted at the 7th intercostal space mid-axillary line.
    Approximately 1.5 L of serous fluid was drained and sent for studies.
    Opening pressure measured at 18 cm H2O.
    """
    record = engine.run(note)

    assert record.pleural_procedure_type == "Thoracentesis"
    assert record.pleural_guidance == "Ultrasound"
    assert record.pleural_side == "Right"
    assert record.pleural_intercostal_space == "7th"
    assert record.pleural_volume_drained_ml in (1500, 1500.0)
    assert record.pleural_fluid_appearance == "Serous"
    assert record.pleural_opening_pressure_measured is True
    assert record.pleural_opening_pressure_cmh2o in (18, 18.0)


def test_chest_tube_removal_and_ipc_exchange(engine):
    note = """
    PROCEDURE: Chest tube removal and IPC exchange

    TECHNIQUE:
    Prior right chest tube was removed without complication.
    Existing tunneled pleural catheter (PleurX) was exchanged over a wire.
    Drainage performed until output slowed.
    """
    record = engine.run(note)

    # Chest tube removal should be detected from the removal verb
    assert record.pleural_procedure_type in ("Chest Tube Removal", "Tunneled Catheter Exchange")
    # IPC exchange should normalize to tunneled catheter exchange
    assert record.pleural_guidance is None or record.pleural_guidance == "Blind"
    assert record.procedure_families is not None
    assert "PLEURAL" in record.procedure_families
