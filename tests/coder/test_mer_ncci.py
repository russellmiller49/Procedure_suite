"""MER and NCCI interactions for the coder."""

from __future__ import annotations

import copy
import json

from modules.coder.engine import CoderEngine
from modules.common import knowledge as knowledge_mod
from modules.common.rules_engine.mer import Code, apply_mer


def test_mer_secondary_discount_applies() -> None:
    codes = [
        Code(cpt="31652", allowed_amount=400.0, is_add_on=False),
        Code(cpt="31628", allowed_amount=250.0, is_add_on=False),
        Code(cpt="+31654", allowed_amount=150.0, is_add_on=True),
    ]
    summary = apply_mer(codes)
    assert summary.primary_code == "31652"
    secondary = next(adj for adj in summary.adjustments if adj.cpt == "31628")
    assert secondary.role == "secondary"
    assert secondary.allowed == 125.0


def test_stent_dilation_same_site_drops_dilation() -> None:
    note = """
    PROCEDURE:
    Therapeutic bronchoscopy with airway stent placed in the right mainstem bronchus.
    Balloon dilation of the right mainstem bronchus was also completed.
    """
    result = CoderEngine().run(note)
    cpts = {code.cpt for code in result.codes}
    assert "31636" in cpts
    assert "31630" not in cpts
    assert any(action.pair == ("31636", "31630") for action in result.ncci_actions)
    assert any(action.rule == "stent_bundling" for action in result.ncci_actions)


def test_stent_dilation_distinct_sites_get_modifier() -> None:
    note = """
    PROCEDURE:
    Rigid bronchoscopy with stent placed in the right mainstem bronchus.
    Balloon dilation performed in the left upper lobe for atelectasis.
    """
    result = CoderEngine().run(note)
    dilation = next(code for code in result.codes if code.cpt == "31630")
    assert {"59", "XS"}.issubset(set(dilation.modifiers))
    assert any(action.rule == "distinct_site_modifier" for action in result.ncci_actions)


def test_sedation_requires_complete_documentation() -> None:
    note = """
    SEDATION:
    Procedural sedation provided by the bronchoscopist.
    """
    result = CoderEngine().run(note)
    assert "99152" not in {code.cpt for code in result.codes}
    assert any("documentation incomplete" in warning for warning in result.warnings)


def test_mer_uses_rvus_from_knowledge() -> None:
    allowed = knowledge_mod.total_rvu("31627")
    summary = apply_mer([Code(cpt="31627")])
    assert summary.adjustments[0].allowed == allowed


def test_hot_reload_updates_sedation_rules(tmp_path, monkeypatch) -> None:
    note = """
    SEDATION:
    Moderate sedation provided by the bronchoscopist. Independent RN observer present.
    Start: 10:00  Stop: 10:30.
    Anesthesia: General anesthesia support present.
    """

    result_default = CoderEngine().run(note)
    assert "99152" not in {code.cpt for code in result_default.codes}
    assert any(action.rule == "sedation_blocker" for action in result_default.ncci_actions)

    custom_path = _write_custom_knowledge(
        tmp_path,
        mutate=lambda data: data["bundling_rules"].__setitem__("sedation_blockers", []),
    )
    monkeypatch.setenv(knowledge_mod.KNOWLEDGE_ENV_VAR, str(custom_path))
    knowledge_mod.reset_cache()

    result_override = CoderEngine().run(note)
    assert "99152" in {code.cpt for code in result_override.codes}

    monkeypatch.delenv(knowledge_mod.KNOWLEDGE_ENV_VAR, raising=False)
    knowledge_mod.reset_cache()


def _write_custom_knowledge(tmp_path, mutate) -> str:
    data = copy.deepcopy(knowledge_mod.get_knowledge())
    mutate(data)
    path = tmp_path / "kb.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)
