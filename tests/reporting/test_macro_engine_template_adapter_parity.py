from __future__ import annotations

from pathlib import Path

from proc_schemas.clinical import ProcedureBundle

from app.reporting.engine import ReporterEngine, default_schema_registry, default_template_registry
from app.reporting.macro_engine_template_adapter import MacroEngineTemplateAdapter, RenderContext


_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "reporting"


def _read_fixture(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def test_template_adapter_parity_thoracentesis() -> None:
    templates = default_template_registry()
    schemas = default_schema_registry()
    adapter = MacroEngineTemplateAdapter(templates, schemas)

    proc_payload = {
        "side": "left",
        "effusion_size": "moderate",
        "effusion_echogenicity": "anechoic",
        "loculations": None,
        "anesthesia_lidocaine_1_pct_ml": 5,
        "intercostal_space": "7th",
        "entry_location": "mid-axillary",
        "volume_removed_ml": 900,
        "fluid_appearance": "serous",
        "specimen_tests": ["cell count", "culture"],
        "cxr_ordered": True,
    }
    expected = _read_fixture("template_adapter_thoracentesis.md")
    rendered = adapter.render_template(
        "thoracentesis",
        proc_payload,
        context=RenderContext(render_style="builder"),
    )
    assert rendered.rstrip() == expected.rstrip()

    bundle = ProcedureBundle.model_validate(
        {"patient": {}, "encounter": {}, "procedures": [], "free_text_hint": ""}
    )
    engine = ReporterEngine(templates, schemas, render_style="builder")
    direct = engine._render_payload(templates.get("thoracentesis"), proc_payload, bundle)
    assert rendered == direct


def test_template_adapter_parity_ebus_tbna() -> None:
    templates = default_template_registry()
    schemas = default_schema_registry()
    adapter = MacroEngineTemplateAdapter(templates, schemas)

    proc_payload = {
        "needle_gauge": "22G",
        "stations": [
            {
                "station_name": "7",
                "passes": 5,
                "size_mm": 10,
                "echo_features": "round",
                "biopsy_tools": ["Vizishot"],
                "rose_result": "Atypical cells",
            }
        ],
        "overall_rose_diagnosis": "Suspicious for malignancy",
    }
    expected = _read_fixture("template_adapter_ebus_tbna.md")
    rendered = adapter.render_template(
        "ebus_tbna",
        proc_payload,
        context=RenderContext(render_style="builder"),
    )
    assert rendered.rstrip() == expected.rstrip()

    bundle = ProcedureBundle.model_validate(
        {"patient": {}, "encounter": {}, "procedures": [], "free_text_hint": ""}
    )
    engine = ReporterEngine(templates, schemas, render_style="builder")
    direct = engine._render_payload(templates.get("ebus_tbna"), proc_payload, bundle)
    assert rendered == direct

