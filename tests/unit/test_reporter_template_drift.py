from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _tracked_files(root: Path) -> dict[str, Path]:
    files = {path.name: path for path in root.glob("*.j2")}
    schema = root / "template_schema.json"
    if schema.exists():
        files[schema.name] = schema
    return files


def test_reporter_macro_knowledge_mirror_is_in_sync() -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "modules" / "reporting" / "templates" / "macros"
    mirror = root / "data" / "knowledge" / "Reporter_jinja2"

    source_files = _tracked_files(source)
    mirror_files = _tracked_files(mirror)

    missing = sorted(name for name in source_files if name not in mirror_files)
    extra = sorted(name for name in mirror_files if name not in source_files)
    changed = sorted(
        name
        for name in set(source_files).intersection(mirror_files)
        if source_files[name].read_bytes() != mirror_files[name].read_bytes()
    )

    assert not missing, f"Reporter macro mirror missing files: {missing}"
    assert not extra, f"Reporter macro mirror has extra files: {extra}"
    assert not changed, f"Reporter macro mirror files differ: {changed}"


def test_addon_template_generation_check_has_no_drift() -> None:
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "generate_addon_templates.py"
    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Addon template generation check failed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
