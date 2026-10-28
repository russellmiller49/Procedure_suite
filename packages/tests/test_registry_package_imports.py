"""The vendored registry packages stay local-only: no network, LLM or app imports.

The clinical worker refuses cloud configuration; this keeps a cloud client from
ever being importable from the packages it runs.
"""

import ast
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "packages/ip_registry_contracts/src")]
from ip_registry_contracts.launch import ENTITY_MODELS, FieldProvenance  # noqa: E402
from ip_registry_contracts.models import ClinicalRevision, ProcedureEvent  # noqa: E402

SOURCES = sorted((ROOT / "packages").glob("*/src/**/*.py"))
FORBIDDEN = {
    "anthropic",
    "openai",
    "httpx",
    "httpx2",
    "requests",
    "urllib3",
    "aiohttp",
    "google",
    "boto3",
    "app",
}


def _imported_roots(path):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module.split(".")[0]


@pytest.mark.parametrize("path", SOURCES, ids=lambda p: str(p.relative_to(ROOT)))
def test_package_source_has_no_network_llm_or_app_imports(path):
    assert not FORBIDDEN & set(_imported_roots(path))


def test_launch_dictionary_schema_matches_live_contract():
    dictionary = json.loads(
        (ROOT / "data/knowledge/robotic_ebus_v1/launch_dictionary.json").read_text()
    )
    assert dictionary["clinical_schema"] == ClinicalRevision.model_json_schema()
    fields = {(entry["entity"], entry["field"]) for entry in dictionary["fields"]}
    models = {**ENTITY_MODELS, "procedures": ProcedureEvent, "field_provenance": FieldProvenance}
    live = {(entity, name) for entity, model in models.items() for name in model.model_fields}
    assert fields == live
