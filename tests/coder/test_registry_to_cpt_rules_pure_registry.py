import inspect


def test_deterministic_registry_to_cpt_rules_do_not_accept_note_text() -> None:
    # Legacy import path remains supported via shim (Phase 3).
    from data.rules import coding_rules

    sig = inspect.signature(coding_rules.derive_all_codes)
    assert "note_text" not in sig.parameters, "deterministic CPT rules must not accept note_text"
    assert len(sig.parameters) == 1, "deterministic CPT rules must accept a single RegistryRecord"

