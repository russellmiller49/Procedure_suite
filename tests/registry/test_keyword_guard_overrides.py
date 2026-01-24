from __future__ import annotations

from modules.registry.schema import RegistryRecord
from modules.registry.self_correction.keyword_guard import apply_required_overrides


def test_apply_required_overrides_does_not_force_peripheral_tbna_from_ebus_station_list() -> None:
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"linear_ebus": {"performed": True, "stations_sampled": ["11L"]}}}
    )
    note_text = (
        "Linear EBUS: Multiple EBUS-TBNA passes were obtained from the following station(s):\n\n"
        "11L (abnormally large lymph node versus mass)\n"
    )
    updated, warnings = apply_required_overrides(note_text, record)

    pp = updated.procedures_performed
    assert pp is not None
    assert pp.peripheral_tbna is None or pp.peripheral_tbna.performed is not True
    assert not any("peripheral/lung tbna" in w.lower() for w in warnings)

