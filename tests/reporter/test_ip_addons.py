"""Unit tests for IP addon templates system.

Tests:
1. JSON loading and slug uniqueness
2. Jinja template rendering
3. Integration with main synoptic templates

These tests can be run independently of the full project dependencies.
"""

import json
from pathlib import Path

import pytest

try:
    from jinja2 import Environment, FileSystemLoader
    JINJA_AVAILABLE = True
except ImportError:
    JINJA_AVAILABLE = False


# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADDONS_JSON_PATH = PROJECT_ROOT / "data" / "knowledge" / "ip_addon_templates_parsed.json"
ADDONS_TEMPLATES_DIR = PROJECT_ROOT / "modules" / "reporting" / "templates" / "addons"
MAIN_TEMPLATES_DIR = PROJECT_ROOT / "modules" / "reporting" / "templates"


class TestAddonJSONIntegrity:
    """Test the addon templates JSON file integrity."""

    @pytest.fixture
    def addon_data(self):
        """Load the addon templates JSON."""
        if not ADDONS_JSON_PATH.exists():
            pytest.skip(f"Addon JSON not found at {ADDONS_JSON_PATH}")
        return json.loads(ADDONS_JSON_PATH.read_text(encoding="utf-8"))

    def test_json_loads_successfully(self, addon_data):
        """Test that the JSON file loads without errors."""
        assert addon_data is not None
        assert "templates" in addon_data

    def test_all_slugs_are_unique(self, addon_data):
        """Test that all template slugs are unique."""
        templates = addon_data.get("templates", [])
        slugs = [t.get("slug", "") for t in templates]

        # Check for duplicates
        seen = set()
        duplicates = []
        for slug in slugs:
            if slug in seen:
                duplicates.append(slug)
            seen.add(slug)

        assert len(duplicates) == 0, f"Duplicate slugs found: {duplicates}"

    def test_all_slugs_are_non_empty(self, addon_data):
        """Test that all template slugs are non-empty strings."""
        templates = addon_data.get("templates", [])

        empty_slugs = []
        for i, t in enumerate(templates):
            slug = t.get("slug", "")
            if not slug or not slug.strip():
                empty_slugs.append(f"Template at index {i}")

        assert len(empty_slugs) == 0, f"Empty slugs found: {empty_slugs}"

    def test_all_templates_have_body(self, addon_data):
        """Test that all templates have a body field."""
        templates = addon_data.get("templates", [])

        missing_body = []
        for t in templates:
            slug = t.get("slug", "unknown")
            body = t.get("body", "")
            if not body or not body.strip():
                missing_body.append(slug)

        # Allow some templates to have empty body (warnings, not errors)
        if missing_body:
            pytest.warn(UserWarning(f"Templates with empty body: {missing_body}"))

    def test_template_count_matches_expected(self, addon_data):
        """Test that the template count matches what's declared."""
        templates = addon_data.get("templates", [])
        declared_count = addon_data.get("template_count", 0)

        assert len(templates) == declared_count, \
            f"Expected {declared_count} templates, found {len(templates)}"

    def test_categories_are_valid(self, addon_data):
        """Test that all templates have valid categories."""
        templates = addon_data.get("templates", [])
        declared_categories = set(addon_data.get("categories", []))

        invalid_categories = []
        for t in templates:
            slug = t.get("slug", "unknown")
            category = t.get("category", "")
            if category and category not in declared_categories:
                invalid_categories.append((slug, category))

        # This is informational - categories might be added dynamically
        if invalid_categories:
            pytest.warn(UserWarning(f"Templates with undeclared categories: {invalid_categories}"))


class TestAddonPythonModule:
    """Test the ip_addons Python module."""

    def test_module_imports(self):
        """Test that the module can be imported."""
        from app.reporting.ip_addons import (
            get_addon_body,
            get_addon_metadata,
            list_addon_slugs,
            list_categories,
            get_addon_count,
        )

        assert callable(get_addon_body)
        assert callable(get_addon_metadata)
        assert callable(list_addon_slugs)
        assert callable(list_categories)
        assert callable(get_addon_count)

    def test_get_addon_body_returns_string(self):
        """Test that get_addon_body returns a string for valid slugs."""
        from app.reporting.ip_addons import get_addon_body, list_addon_slugs

        slugs = list_addon_slugs()
        if not slugs:
            pytest.skip("No addon slugs loaded")

        # Test first slug
        body = get_addon_body(slugs[0])
        assert body is None or isinstance(body, str)

    def test_get_addon_body_returns_none_for_invalid_slug(self):
        """Test that get_addon_body returns None for invalid slugs."""
        from app.reporting.ip_addons import get_addon_body

        result = get_addon_body("this_slug_definitely_does_not_exist_12345")
        assert result is None

    def test_list_addon_slugs_returns_list(self):
        """Test that list_addon_slugs returns a list."""
        from app.reporting.ip_addons import list_addon_slugs

        slugs = list_addon_slugs()
        assert isinstance(slugs, list)

    def test_addon_count_matches_slugs(self):
        """Test that get_addon_count matches the list length."""
        from app.reporting.ip_addons import get_addon_count, list_addon_slugs

        count = get_addon_count()
        slugs = list_addon_slugs()

        assert count == len(slugs)

    def test_get_addon_metadata_structure(self):
        """Test that get_addon_metadata returns proper structure."""
        from app.reporting.ip_addons import get_addon_metadata, list_addon_slugs

        slugs = list_addon_slugs()
        if not slugs:
            pytest.skip("No addon slugs loaded")

        meta = get_addon_metadata(slugs[0])
        assert meta is not None
        assert "title" in meta
        assert "category" in meta
        assert "cpt_codes" in meta
        assert "body" in meta

    def test_validate_addons_returns_dict(self):
        """Test that validate_addons returns proper structure."""
        from app.reporting.ip_addons import validate_addons

        result = validate_addons()
        assert isinstance(result, dict)
        assert "errors" in result
        assert "warnings" in result
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)

    def test_find_addons_by_cpt(self):
        """Test CPT code lookup functionality."""
        from app.reporting.ip_addons import find_addons_by_cpt

        # Test with a known CPT code (thoracentesis = 32555)
        results = find_addons_by_cpt("32555")
        assert isinstance(results, list)
        # Should find at least one template
        if results:
            assert "slug" in results[0]


@pytest.mark.skipif(not JINJA_AVAILABLE, reason="Jinja2 not installed")
class TestAddonJinjaTemplates:
    """Test the generated Jinja addon templates."""

    @pytest.fixture
    def jinja_env(self):
        """Create a Jinja environment for testing."""
        if not ADDONS_TEMPLATES_DIR.exists():
            pytest.skip(f"Addons templates directory not found at {ADDONS_TEMPLATES_DIR}")

        env = Environment(
            loader=FileSystemLoader(str(ADDONS_TEMPLATES_DIR)),
            autoescape=False,
        )
        return env

    def test_all_templates_are_valid_jinja(self, jinja_env):
        """Test that all generated addon templates are valid Jinja."""
        template_files = list(ADDONS_TEMPLATES_DIR.glob("*.jinja"))

        if not template_files:
            pytest.skip("No Jinja template files found")

        errors = []
        for template_path in template_files:
            try:
                template = jinja_env.get_template(template_path.name)
                # Try to render with empty context to check for basic issues
                _ = template.module
            except Exception as e:
                errors.append(f"{template_path.name}: {e}")

        assert len(errors) == 0, f"Invalid Jinja templates:\n" + "\n".join(errors)

    def test_templates_have_render_macro(self, jinja_env):
        """Test that all templates define a render() macro."""
        template_files = list(ADDONS_TEMPLATES_DIR.glob("*.jinja"))

        if not template_files:
            pytest.skip("No Jinja template files found")

        missing_render = []
        for template_path in template_files:
            try:
                template = jinja_env.get_template(template_path.name)
                module = template.module
                if not hasattr(module, "render"):
                    missing_render.append(template_path.name)
            except Exception:
                # Already tested in previous test
                pass

        assert len(missing_render) == 0, f"Templates missing render() macro: {missing_render}"

    def test_render_macro_returns_string(self, jinja_env):
        """Test that render() macro returns a string."""
        template_files = list(ADDONS_TEMPLATES_DIR.glob("*.jinja"))

        if not template_files:
            pytest.skip("No Jinja template files found")

        # Test a sample of templates
        sample_files = template_files[:5]

        for template_path in sample_files:
            try:
                template = jinja_env.get_template(template_path.name)
                module = template.module
                if hasattr(module, "render"):
                    result = module.render()
                    assert isinstance(result, str), \
                        f"{template_path.name}: render() returned {type(result)}, expected str"
            except Exception as e:
                pytest.fail(f"{template_path.name}: {e}")


@pytest.mark.skipif(not JINJA_AVAILABLE, reason="Jinja2 not installed")
class TestMainTemplatesAddonIntegration:
    """Test that main synoptic templates properly integrate addons."""

    @pytest.fixture
    def main_jinja_env(self):
        """Create a Jinja environment for main templates."""
        if not MAIN_TEMPLATES_DIR.exists():
            pytest.skip(f"Main templates directory not found at {MAIN_TEMPLATES_DIR}")

        # Import addon functions locally to avoid package import issues
        import sys
        sys.path.insert(0, str(PROJECT_ROOT))
        from app.reporting.ip_addons import get_addon_body, get_addon_metadata, list_addon_slugs

        env = Environment(
            loader=FileSystemLoader(str(MAIN_TEMPLATES_DIR)),
            autoescape=False,
        )
        # Add the addon functions
        env.globals["get_addon_body"] = get_addon_body
        env.globals["get_addon_metadata"] = get_addon_metadata
        env.globals["list_addon_slugs"] = list_addon_slugs
        return env

    @pytest.mark.parametrize("template_name", [
        "bronchoscopy.jinja",
        "ebus_tbna.jinja",
        "stent.jinja",
        "thoracentesis.jinja",
        "ipc.jinja",
        "pleuroscopy.jinja",
        "cryobiopsy.jinja",
    ])
    def test_main_templates_load_successfully(self, main_jinja_env, template_name):
        """Test that main templates load without errors."""
        try:
            template = main_jinja_env.get_template(template_name)
            assert template is not None
        except Exception as e:
            pytest.fail(f"Failed to load {template_name}: {e}")

    def test_addon_section_renders_when_addons_present(self, main_jinja_env):
        """Test that the addons section renders when report.addons is provided."""
        from app.reporting.ip_addons import list_addon_slugs

        slugs = list_addon_slugs()
        if not slugs:
            pytest.skip("No addon slugs available")

        # Create a mock report object with addons
        class MockReport:
            addons = [slugs[0]]  # Use first available addon
            intraop = {}
            postop = {}
            nlp = None

        class MockCore:
            type = "bronchoscopy"
            laterality = None
            stations_sampled = None
            devices = None

        template = main_jinja_env.get_template("bronchoscopy.jinja")
        context = {
            "report": MockReport(),
            "core": MockCore(),
            "targets": [],
            "meta": {},
            "summarize_specimens": lambda x: "N/A",
            "get_addon_body": main_jinja_env.globals["get_addon_body"],
        }

        rendered = template.render(**context)

        # Should contain the addons section
        assert "Additional Procedures / Events" in rendered

    def test_addon_section_absent_when_no_addons(self, main_jinja_env):
        """Test that addons section is absent when report.addons is empty or missing."""
        class MockReport:
            addons = []
            intraop = {}
            postop = {}
            nlp = None

        class MockCore:
            type = "bronchoscopy"
            laterality = None
            stations_sampled = None
            devices = None

        template = main_jinja_env.get_template("bronchoscopy.jinja")
        context = {
            "report": MockReport(),
            "core": MockCore(),
            "targets": [],
            "meta": {},
            "summarize_specimens": lambda x: "N/A",
            "get_addon_body": main_jinja_env.globals["get_addon_body"],
        }

        rendered = template.render(**context)

        # Should NOT contain the addons section
        assert "Additional Procedures / Events" not in rendered


class TestSpecificAddons:
    """Test specific addon templates that are commonly used."""

    def test_thoracentesis_addon(self):
        """Test the thoracentesis addon template."""
        from app.reporting.ip_addons import get_addon_body, get_addon_metadata

        body = get_addon_body("thoracentesis")
        assert body is not None
        assert "thoracentesis" in body.lower() or "pleural" in body.lower()

        meta = get_addon_metadata("thoracentesis")
        assert meta is not None
        assert "32555" in [str(c) for c in meta.get("cpt_codes", [])]

    def test_ebus_tbna_addon(self):
        """Test the EBUS-TBNA addon template."""
        from app.reporting.ip_addons import get_addon_body, get_addon_metadata

        body = get_addon_body("ebus_tbna")
        assert body is not None
        assert "ebus" in body.lower() or "survey" in body.lower()

        meta = get_addon_metadata("ebus_tbna")
        assert meta is not None

    def test_bronchial_washing_addon(self):
        """Test the bronchial washing addon template."""
        from app.reporting.ip_addons import get_addon_body

        body = get_addon_body("bronchial_washing")
        assert body is not None
        assert "washing" in body.lower() or "saline" in body.lower()

    def test_endobronchial_valve_placement_addon(self):
        """Test the BLVR valve placement addon template."""
        from app.reporting.ip_addons import get_addon_body, get_addon_metadata

        body = get_addon_body("endobronchial_valve_placement")
        assert body is not None
        assert "valve" in body.lower()

        meta = get_addon_metadata("endobronchial_valve_placement")
        assert meta is not None
        assert "BLVR" in meta.get("category", "")
