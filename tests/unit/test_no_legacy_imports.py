"""Guardrail tests to prevent reintroduction of legacy imports.

These tests scan the active codebase (modules/api, modules/coder/application,
modules/coder/adapters) to ensure no legacy imports are accidentally added.

The legacy code has been migrated:
- proc_autocode/ -> modules/autocode/
- proc_report/ -> modules/reporting/
- proc_registry/ -> modules/registry/legacy/

Active code should use the new module paths.
"""

import os
from pathlib import Path


# Directories to scan for legacy imports
ACTIVE_DIRECTORIES = [
    "modules/api",
    "modules/coder/application",
    "modules/coder/adapters",
    "modules/domain",
    "modules/infra",
]

# Legacy strings that should NOT appear in active code
LEGACY_STRINGS = [
    # Old proc_autocode imports - now at app.autocode
    "from proc_autocode.coder import",
    "from proc_autocode import",
    "import proc_autocode.coder",
    "proc_autocode.ip_kb",
    # Old proc_report imports - now at app.reporting
    "from proc_report import",
    "from proc_report.engine import",
    "import proc_report",
    # Old proc_registry imports - now at app.registry.legacy
    "from proc_registry import",
    "import proc_registry",
    # Deprecated internal modules
    "from app.coder.llm_coder import",  # Should use adapters/llm/gemini_advisor
    "from app.coder.engine import",  # Should use application/coding_service
]

# Files that are explicitly allowed to have legacy references (for deprecation notices)
ALLOWED_FILES = [
    "modules/coder/llm_coder.py",  # Has deprecation warning
    "modules/coder/engine.py",  # Has deprecation warning
]


def get_project_root() -> Path:
    """Get the project root directory."""
    # This test file is at tests/unit/test_no_legacy_imports.py
    # Project root is 3 levels up
    return Path(__file__).parent.parent.parent


def test_no_legacy_imports_in_api():
    """Ensure modules/api does not import legacy proc_autocode code."""
    project_root = get_project_root()
    api_dir = project_root / "modules" / "api"

    if not api_dir.exists():
        return  # Skip if directory doesn't exist

    violations = []

    for py_file in api_dir.rglob("*.py"):
        rel_path = str(py_file.relative_to(project_root))

        if rel_path in ALLOWED_FILES:
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for legacy_string in LEGACY_STRINGS:
            if legacy_string in content:
                violations.append(f"{rel_path}: contains '{legacy_string}'")

    assert not violations, (
        "Legacy imports found in modules/api/:\n" + "\n".join(violations) +
        "\n\nPlease use the new hexagonal architecture instead:\n"
        "- CodingService from app.coder.application.coding_service\n"
        "- LLMAdvisorPort from app.coder.adapters.llm.gemini_advisor\n"
        "- JsonKnowledgeBaseAdapter from app.coder.adapters.persistence"
    )


def test_no_legacy_imports_in_application():
    """Ensure modules/coder/application does not import legacy code."""
    project_root = get_project_root()
    app_dir = project_root / "modules" / "coder" / "application"

    if not app_dir.exists():
        return  # Skip if directory doesn't exist

    violations = []

    for py_file in app_dir.rglob("*.py"):
        rel_path = str(py_file.relative_to(project_root))

        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for legacy_string in LEGACY_STRINGS:
            if legacy_string in content:
                violations.append(f"{rel_path}: contains '{legacy_string}'")

    assert not violations, (
        "Legacy imports found in modules/coder/application/:\n" + "\n".join(violations) +
        "\n\nThe application layer should only use domain interfaces and ports."
    )


def test_no_legacy_imports_in_adapters():
    """Ensure modules/coder/adapters does not import legacy code."""
    project_root = get_project_root()
    adapters_dir = project_root / "modules" / "coder" / "adapters"

    if not adapters_dir.exists():
        return  # Skip if directory doesn't exist

    violations = []

    for py_file in adapters_dir.rglob("*.py"):
        rel_path = str(py_file.relative_to(project_root))

        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for legacy_string in LEGACY_STRINGS:
            if legacy_string in content:
                violations.append(f"{rel_path}: contains '{legacy_string}'")

    assert not violations, (
        "Legacy imports found in modules/coder/adapters/:\n" + "\n".join(violations) +
        "\n\nAdapters should implement domain ports, not import legacy code."
    )


def test_no_legacy_imports_in_domain():
    """Ensure modules/domain does not import legacy code."""
    project_root = get_project_root()
    domain_dir = project_root / "modules" / "domain"

    if not domain_dir.exists():
        return  # Skip if directory doesn't exist

    violations = []

    for py_file in domain_dir.rglob("*.py"):
        rel_path = str(py_file.relative_to(project_root))

        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for legacy_string in LEGACY_STRINGS:
            if legacy_string in content:
                violations.append(f"{rel_path}: contains '{legacy_string}'")

    assert not violations, (
        "Legacy imports found in modules/domain/:\n" + "\n".join(violations) +
        "\n\nDomain layer should be pure and not depend on any infrastructure."
    )


def test_coding_service_uses_ports_not_concrete():
    """Verify CodingService uses LLMAdvisorPort, not concrete LLM implementations."""
    project_root = get_project_root()
    coding_service_file = project_root / "modules" / "coder" / "application" / "coding_service.py"

    if not coding_service_file.exists():
        return  # Skip if file doesn't exist

    content = coding_service_file.read_text(encoding="utf-8")

    # Should use the port abstraction
    assert "LLMAdvisorPort" in content or "llm_advisor" in content, (
        "CodingService should depend on LLMAdvisorPort or llm_advisor parameter"
    )

    # Should NOT directly import concrete LLM implementations
    concrete_imports = [
        "from app.coder.llm_coder import",
        "import app.coder.llm_coder",
        "from app.common.llm import GeminiLLM",
    ]

    violations = []
    for bad_import in concrete_imports:
        if bad_import in content:
            violations.append(bad_import)

    assert not violations, (
        f"CodingService should not directly import concrete LLM implementations:\n"
        f"{violations}\n\n"
        "Use dependency injection via LLMAdvisorPort instead."
    )


def test_kb_uses_domain_interfaces():
    """Verify KB usage goes through domain interfaces, not legacy ip_kb."""
    project_root = get_project_root()
    coding_service_file = project_root / "modules" / "coder" / "application" / "coding_service.py"

    if not coding_service_file.exists():
        return  # Skip if file doesn't exist

    content = coding_service_file.read_text(encoding="utf-8")

    legacy_kb_imports = [
        "from proc_autocode.ip_kb",
        "import proc_autocode.ip_kb",
        "from app.autocode.ip_kb",
        "import app.autocode.ip_kb",
    ]

    violations = []
    for bad_import in legacy_kb_imports:
        if bad_import in content:
            violations.append(bad_import)

    assert not violations, (
        f"CodingService should not import legacy KB:\n{violations}\n\n"
        "Use KnowledgeBaseRepository interface from app.domain.knowledge_base instead."
    )
