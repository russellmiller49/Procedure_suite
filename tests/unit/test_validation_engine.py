from jinja2 import Environment

from modules.reporting.engine import SchemaRegistry, TemplateMeta, TemplateRegistry
from modules.reporting.validation import ConsistencyCheckConfig, FieldConfig, ValidationEngine, WarnIfConfig
from proc_schemas.clinical import pleural as pleural_schemas
from proc_schemas.clinical.common import EncounterInfo, PatientInfo, ProcedureBundle, ProcedureInput


def _stub_template_registry(meta: TemplateMeta) -> TemplateRegistry:
    env = Environment()
    registry = TemplateRegistry(env)
    registry._register(meta)
    return registry


def _stub_schema_registry() -> SchemaRegistry:
    registry = SchemaRegistry()
    registry.register("thoracentesis_detailed_v1", pleural_schemas.ThoracentesisDetailed)
    return registry


def test_validation_engine_flags_missing_and_warns():
    meta = TemplateMeta(
        id="thoracentesis_detailed",
        label="Thoracentesis (Detailed)",
        category="pleural",
        cpt_hints=["32555"],
        schema_id="thoracentesis_detailed_v1",
        output_section="PROCEDURE_DETAILS",
        required_fields=[],
        optional_fields=[],
        template=Environment().from_string(""),
        proc_types=["thoracentesis_detailed"],
        critical_fields=[],
        recommended_fields=[],
        field_configs={
            "side": FieldConfig(path="side", required=True, critical=True),
            "fluid_appearance": FieldConfig(path="fluid_appearance", required=True, critical=True),
            "volume_removed_ml": FieldConfig(
                path="volume_removed_ml",
                required=True,
                critical=True,
                warn_if=WarnIfConfig(op="lt", value=100, message="Low drainage volume"),
            ),
            "cxr_ordered": FieldConfig(
                path="cxr_ordered",
                consistency_check=ConsistencyCheckConfig(
                    target="volume_removed_ml", message="Consider documenting post-procedure CXR"
                ),
            ),
        },
    )
    templates = _stub_template_registry(meta)
    schemas = _stub_schema_registry()

    bundle = ProcedureBundle(
        patient=PatientInfo(name="Case", age=60, sex="female"),
        encounter=EncounterInfo(date="2024-01-01", attending="Dr. Test"),
        procedures=[
            ProcedureInput(
                proc_type="thoracentesis_detailed",
                schema_id="thoracentesis_detailed_v1",
                proc_id="thoracentesis_detailed_1",
                data={
                    "side": "left",
                    "volume_removed_ml": 50,
                    "intercostal_space": "7th",
                    "entry_location": "mid-axillary",
                },
            )
        ],
    )

    engine = ValidationEngine(templates, schemas)
    issues = engine.list_missing_critical_fields(bundle)
    warnings = engine.apply_warn_if_rules(bundle)

    paths = {(issue.proc_id, issue.field_path) for issue in issues}
    assert ("thoracentesis_detailed_1", "fluid_appearance") in paths
    assert any("Low drainage volume" in msg for msg in warnings)
    assert any("CXR" in msg for msg in warnings)
