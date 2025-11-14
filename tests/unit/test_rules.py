from proc_autocode import rules
from proc_schemas.procedure_report import ProcedureReport, ProcedureCore, TargetSpecimen


def test_rule_engine_maps_ebus_codes():
    core = ProcedureCore(
        type="ebus_tbna",
        stations_sampled=["7", "4R"],
        targets=[TargetSpecimen(segment="7", guidance="radial_ebus", specimens={"fna": 3})],
    )
    report = ProcedureReport(procedure_core=core, intraop={"sedation_minutes": 20})
    features = rules.derive_features(report)
    rulebook = rules.load_rulebook()
    hits = rules.evaluate_rules(report, features, rulebook)
    cpts = {hit.cpt for hit in hits}
    assert "31652" in cpts
    assert "99152" in cpts
