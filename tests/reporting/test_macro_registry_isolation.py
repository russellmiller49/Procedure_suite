from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.reporting import macro_engine
from app.reporting.engine import ReporterEngine, TemplateRegistry, default_schema_registry
from app.reporting.macro_registry import Macro, MacroRegistry


def test_macro_registry_isolated_and_deterministic(tmp_path: Path) -> None:
    schema_path = tmp_path / "template_schema.json"
    schema = {
        "template_system": "test",
        "version": "0.0.0",
        "categories": {
            "01_minor_trach_laryngoscopy": {
                "description": "Test category",
                "macros": {
                    "minor_trach_bleeding": {
                        "cpt": "00000",
                        "params": ["side"],
                        "defaults": {"side": "left"},
                        "essential": ["side"],
                        "essential_labels": {"side": "Side"},
                    }
                },
            }
        },
    }
    schema_path.write_text(json.dumps(schema), encoding="utf-8")

    (tmp_path / "01_minor_trach_laryngoscopy.j2").write_text(
        "{% macro minor_trach_bleeding(side=None) -%}Bleeding side: {{ side }}{%- endmacro %}\n",
        encoding="utf-8",
    )

    registry = MacroRegistry(schema_path=schema_path, template_root=tmp_path)
    assert "minor_trach_bleeding" in macro_engine.list_macros(registry=registry)

    rendered_1 = macro_engine.render_macro("minor_trach_bleeding", registry=registry)
    rendered_2 = macro_engine.render_macro("minor_trach_bleeding", registry=registry)
    assert rendered_1 is not None
    assert rendered_1.strip() == "Bleeding side: left"
    assert rendered_1 == rendered_2

    bundle = {"procedures": [{"proc_type": "minor_trach_bleeding", "proc_id": "p1", "data": {"side": None}}]}
    validated = macro_engine.validate_essential_fields(bundle, registry=registry)
    assert validated["acknowledged_omissions"]["p1"] == ["Side"]


def test_macro_registry_can_be_injected_without_filesystem_templates(tmp_path: Path) -> None:
    registry = MacroRegistry(schema_path=tmp_path / "missing.json", template_root=tmp_path)
    registry.registry = {
        "fake": Macro(
            name="fake",
            category="fake_category",
            description="Fake category",
            cpt="12345",
            params=["value"],
            defaults={"value": "default"},
            required=False,
            essential=["value"],
            essential_labels={"value": "Value"},
            note=None,
            template_file="fake.j2",
            callable=lambda value=None: f"FAKE:{value}",
        )
    }
    registry.schema = {"categories": {"fake_category": {"description": "Fake category", "macros": {}}}}

    rendered = macro_engine.render_macro("fake", registry=registry)
    assert rendered == "FAKE:default"

    env = Environment(loader=FileSystemLoader(str(tmp_path)))
    templates = TemplateRegistry(env, root=tmp_path)
    engine = ReporterEngine(templates, default_schema_registry(), macro_registry=registry)
    assert engine.templates.env.globals["render_macro"]("fake") == "FAKE:default"
