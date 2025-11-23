from proc_report.engine import apply_patch_result
from proc_report.inference import InferenceEngine
from proc_schemas.clinical.common import EncounterInfo, PatientInfo, ProcedureBundle, ProcedureInput, SedationInfo


def test_inference_engine_sets_anesthesia_from_sedation():
    bundle = ProcedureBundle(
        patient=PatientInfo(name="Inference Case"),
        encounter=EncounterInfo(date="2024-05-01"),
        procedures=[ProcedureInput(proc_type="test_proc", schema_id="test_schema", data={})],
        sedation=SedationInfo(description="propofol infusion"),
        anesthesia=None,
    )
    engine = InferenceEngine()
    result = engine.infer_bundle(bundle)
    updated = apply_patch_result(bundle, result)

    assert updated.anesthesia is not None
    assert updated.anesthesia.type == "Deep Sedation / TIVA"
    assert any("propofol" in note.lower() for note in result.notes)
