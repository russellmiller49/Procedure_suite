from __future__ import annotations

from app.registry.audit.raw_ml_auditor import FLAG_TO_CPT_MAP
from app.registry.self_correction.keyword_guard import CPT_KEYWORDS, HIGH_CONF_BYPASS_CPTS


def test_keyword_guard_has_coverage_for_self_correct_allowlist_cpts() -> None:
    # Explicitly bounded CPT universe for self-correction gating.
    # Keep this list decision-complete and small; expand intentionally when
    # adding new self-correction targets.
    self_correct_allowlist = {
        # Bronchoscopy
        "31623",
        "31624",
        "31626",
        "31627",
        "31628",
        "31629",
        "31630",
        "31631",
        "31632",
        "31633",
        "31635",
        "31636",
        "31637",
        "31638",
        "31645",
        "31646",
        "31652",
        "31653",
        "31654",
        # BLVR
        "31647",
        "31648",
        "31649",
        "31651",
        # Pleural
        "32550",
        "32551",
        "32554",
        "32555",
        "32560",
        "32561",
        "32562",
        "32650",
    }

    omission_cpts = {cpt for cpts in FLAG_TO_CPT_MAP.values() for cpt in cpts}
    target_cpts = sorted(omission_cpts & self_correct_allowlist)

    missing = [
        cpt
        for cpt in target_cpts
        if (not CPT_KEYWORDS.get(cpt)) and (cpt not in HIGH_CONF_BYPASS_CPTS)
    ]
    assert not missing, f"Missing CPT_KEYWORDS coverage for: {missing}"
