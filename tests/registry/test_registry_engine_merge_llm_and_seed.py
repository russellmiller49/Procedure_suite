from modules.registry.engine import RegistryEngine


def test_merge_llm_and_seed_preserves_existing_ml_findings():
    llm_data = {
        "procedures_performed": {
            "tbna": {"performed": True},
            "brushings": {"performed": True},
            "linear_ebus": {"performed": True, "stations_sampled": ["4R"]},
        }
    }
    seed_data = {
        "procedures_performed": {
            "mechanical_debulking": {"performed": True},
            "linear_ebus": {"performed": True, "stations_sampled": ["11L"]},
        }
    }

    merged = RegistryEngine._merge_llm_and_seed(llm_data, seed_data)

    assert merged["procedures_performed"]["tbna"]["performed"] is True
    assert merged["procedures_performed"]["brushings"]["performed"] is True
    assert merged["procedures_performed"]["mechanical_debulking"]["performed"] is True
    # Non-empty lists should not be overridden by deterministic seeds.
    assert merged["procedures_performed"]["linear_ebus"]["stations_sampled"] == ["4R"]


def test_merge_llm_and_seed_allows_seed_to_flip_performed_true():
    llm_data = {"procedures_performed": {"mechanical_debulking": {"performed": False}}}
    seed_data = {"procedures_performed": {"mechanical_debulking": {"performed": True}}}

    merged = RegistryEngine._merge_llm_and_seed(llm_data, seed_data)

    assert merged["procedures_performed"]["mechanical_debulking"]["performed"] is True
