from proc_schemas.procedure_report import ProcedureReport, ProcedureCore, TargetSpecimen


def test_procedure_report_instantiation():
    core = ProcedureCore(
        type="ebus_tbna",
        laterality="right",
        stations_sampled=["7", "4R"],
        targets=[
            TargetSpecimen(segment="7", guidance="radial_ebus", specimens={"fna": 3}),
            TargetSpecimen(segment="4R", guidance="radial_ebus", specimens={"fna": 3}),
        ],
        devices={"scope": "ebus"},
    )
    report = ProcedureReport(procedure_core=core)
    assert report.procedure_core.type == "ebus_tbna"
    assert len(report.procedure_core.targets) == 2
