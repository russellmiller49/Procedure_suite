from __future__ import annotations

import json
from pathlib import Path

from app.registry.audit.raw_ml_auditor import FLAG_TO_CPT_MAP
from app.registry.schema import RegistryRecord
from app.registry.self_correction import keyword_guard
from app.registry.self_correction.keyword_guard import HIGH_CONF_BYPASS_CPTS
from ops.tools import generate_cpt_keywords

# Not in the current KB master_code_index; explicit allowlist for coverage checks.
KEYWORD_COVERAGE_EXEMPT_CPTS = {"32400", "32405"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_generate_cpt_keywords_is_deterministic() -> None:
    root = _repo_root()
    mapping_a = generate_cpt_keywords.generate_cpt_keywords(repo_root=root)
    bytes_a = generate_cpt_keywords.serialize_mapping(mapping_a).encode("utf-8")

    mapping_b = generate_cpt_keywords.generate_cpt_keywords(repo_root=root)
    bytes_b = generate_cpt_keywords.serialize_mapping(mapping_b).encode("utf-8")

    assert bytes_a == bytes_b


def test_keyword_guard_merges_generated_keywords_without_regression(tmp_path: Path, monkeypatch) -> None:
    generated_path = tmp_path / "cpt_keywords.generated.json"
    generated_path.write_text(
        json.dumps(
            {
                "31624": ["lavage", "broncho alveolar lavage", "novel lavage cue"],
                "99999": ["custom procedure phrase"],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("REGISTRY_KEYWORD_GUARD_USE_GENERATED", "1")
    monkeypatch.setenv("REGISTRY_KEYWORD_GUARD_GENERATED_PATH", str(generated_path))

    effective = keyword_guard.get_effective_cpt_keywords(force_refresh=True)
    assert "bal" in effective["31624"]
    assert "novel lavage cue" in effective["31624"]
    assert effective["99999"] == ["custom procedure phrase"]

    ok, _reason = keyword_guard.keyword_guard_check(cpt="31624", evidence_text="Bronchoalveolar lavage was performed.")
    assert ok is True

    # Should remain stable with generated mapping enabled.
    warnings = keyword_guard.scan_for_omissions("Bronchial brushings were obtained.", RegistryRecord())
    assert isinstance(warnings, list)


def test_generated_keywords_cover_flag_to_cpt_targets(monkeypatch) -> None:
    monkeypatch.setenv("REGISTRY_KEYWORD_GUARD_USE_GENERATED", "1")
    monkeypatch.delenv("REGISTRY_KEYWORD_GUARD_GENERATED_PATH", raising=False)

    effective = keyword_guard.get_effective_cpt_keywords(force_refresh=True)
    omission_cpts = {cpt for cpts in FLAG_TO_CPT_MAP.values() for cpt in cpts}

    missing = sorted(
        cpt
        for cpt in omission_cpts
        if cpt not in effective and cpt not in HIGH_CONF_BYPASS_CPTS and cpt not in KEYWORD_COVERAGE_EXEMPT_CPTS
    )
    assert not missing, f"Missing effective keyword coverage for omission CPTs: {missing}"
