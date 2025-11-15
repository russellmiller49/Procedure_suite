"""MER and NCCI interactions for the coder."""

from modules.coder.engine import CoderEngine
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


def test_stent_dilation_distinct_sites_get_modifier() -> None:
    note = """
    PROCEDURE:
    Rigid bronchoscopy with stent placed in the right mainstem bronchus.
    Balloon dilation performed in the left upper lobe for atelectasis.
    """
    result = CoderEngine().run(note)
    dilation = next(code for code in result.codes if code.cpt == "31630")
    assert {"59", "XS"}.issubset(set(dilation.modifiers))
    assert any("modifier" in action.action for action in result.ncci_actions)
