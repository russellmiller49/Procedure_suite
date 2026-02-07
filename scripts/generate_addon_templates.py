#!/usr/bin/env python3
"""Generate Jinja addon template files from ip_addon_templates_parsed.json.

This script reads the parsed addon templates JSON and generates individual
Jinja template files in the templates/addons/ directory.

Each generated file contains:
- A comment header with title, category, and CPT codes
- A render() macro that returns the template body
"""

import argparse
import json
import re
from pathlib import Path


def sanitize_filename(slug: str) -> str:
    """Ensure slug is valid as a filename."""
    # Remove any characters that aren't alphanumeric, underscore, or hyphen
    return re.sub(r"[^a-zA-Z0-9_-]", "_", slug)


def escape_jinja_chars(text: str) -> str:
    """Escape any Jinja-like syntax in the body text.

    Since we're putting raw text into a Jinja template, we need to ensure
    any {{ or {% sequences don't get interpreted as Jinja.
    """
    # Replace any accidental Jinja-like syntax
    text = text.replace("{{", "{ {")
    text = text.replace("}}", "} }")
    text = text.replace("{%", "{ %")
    text = text.replace("%}", "% }")
    return text


def generate_template_file(template: dict, output_dir: Path) -> Path:
    """Generate a single Jinja template file for an addon.

    Args:
        template: Dict with slug, title, category, cpt_codes, body
        output_dir: Directory to write the template file to

    Returns:
        Path to the generated file
    """
    slug = template.get("slug", "")
    title = template.get("title", "")
    category = template.get("category", "")
    cpt_codes = template.get("cpt_codes", [])
    body = template.get("body", "")

    if not slug:
        raise ValueError("Template missing slug")

    filename = f"{sanitize_filename(slug)}.jinja"
    filepath = output_dir / filename

    # Format CPT codes for comment
    cpt_str = ", ".join(str(c) for c in cpt_codes) if cpt_codes else "None"

    # Escape the body text
    escaped_body = escape_jinja_chars(body)

    # Generate the Jinja template content using {# #} for Jinja2 comments
    content = f'''{{#
  file: templates/addons/{filename}
  Title: {title}
  Category: {category}
  CPT: {cpt_str}
#}}
{{% macro render(ctx=None) -%}}
{escaped_body}
{{%- endmacro %}}
'''

    filepath.write_text(content, encoding="utf-8")
    return filepath


def _parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Generate addon Jinja templates from addon JSON.")
    parser.add_argument(
        "--json-path",
        type=Path,
        default=project_root / "data" / "knowledge" / "ip_addon_templates_parsed.json",
        help="Path to addon templates JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "modules" / "reporting" / "templates" / "addons",
        help="Directory where addon .jinja files are written.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write files; fail if generated output differs from existing files.",
    )
    return parser.parse_args()


def _render_template_content(template: dict, filename: str) -> str:
    title = template.get("title", "")
    category = template.get("category", "")
    cpt_codes = template.get("cpt_codes", [])
    body = template.get("body", "")
    cpt_str = ", ".join(str(c) for c in cpt_codes) if cpt_codes else "None"
    escaped_body = escape_jinja_chars(body)
    return f'''{{#
  file: templates/addons/{filename}
  Title: {title}
  Category: {category}
  CPT: {cpt_str}
#}}
{{% macro render(ctx=None) -%}}
{escaped_body}
{{%- endmacro %}}
'''


def _planned_outputs(templates: list[dict]) -> dict[str, str]:
    outputs: dict[str, str] = {}
    for template in templates:
        slug = template.get("slug", "")
        if not slug:
            continue
        filename = f"{sanitize_filename(slug)}.jinja"
        outputs[filename] = _render_template_content(template, filename)
    return outputs


def _write_init_file(output_dir: Path) -> None:
    init_path = output_dir / "__init__.py"
    init_content = '''"""Auto-generated addon templates.

These Jinja templates were generated from ip_addon_templates_parsed.json.
Each template provides a render(ctx=None) macro for inclusion in procedure reports.
"""

# This file intentionally left mostly empty.
# Templates are loaded via the Jinja environment, not Python imports.
'''
    init_path.write_text(init_content, encoding="utf-8")


def _check_mode(output_dir: Path, planned: dict[str, str]) -> int:
    existing = {path.name: path for path in output_dir.glob("*.jinja")} if output_dir.exists() else {}
    missing = sorted(name for name in planned if name not in existing)
    extra = sorted(name for name in existing if name not in planned)
    changed: list[str] = []

    for name in sorted(set(planned).intersection(existing)):
        current_text = existing[name].read_text(encoding="utf-8")
        if current_text != planned[name]:
            changed.append(name)

    if not (missing or extra or changed):
        print("Addon templates are up to date.")
        return 0

    print("Addon template drift detected.")
    if missing:
        print("Missing files:")
        for name in missing:
            print(f"  - {name}")
    if extra:
        print("Extra files:")
        for name in extra:
            print(f"  - {name}")
    if changed:
        print("Changed files:")
        for name in changed:
            print(f"  - {name}")
    return 1


def main() -> int:
    args = _parse_args()
    json_path = args.json_path.resolve()
    output_dir = args.output_dir.resolve()

    print(f"Loading templates from: {json_path}")
    if not json_path.exists():
        print(f"ERROR: JSON file not found at {json_path}")
        return 1

    data = json.loads(json_path.read_text(encoding="utf-8"))
    templates = data.get("templates", [])
    print(f"Found {len(templates)} templates")

    planned = _planned_outputs(templates)
    if args.check:
        return _check_mode(output_dir, planned)

    output_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    errors = []
    for template in templates:
        try:
            filepath = generate_template_file(template, output_dir)
            generated.append(filepath.name)
            print(f"  Generated: {filepath.name}")
        except Exception as e:
            slug = template.get("slug", "unknown")
            errors.append(f"{slug}: {e}")
            print(f"  ERROR generating {slug}: {e}")

    print(f"\nGenerated {len(generated)} template files in {output_dir}")
    if errors:
        print(f"Errors: {len(errors)}")
        for err in errors:
            print(f"  - {err}")
        return 1

    _write_init_file(output_dir)
    print(f"Updated {output_dir / '__init__.py'}")
    return 0


if __name__ == "__main__":
    exit(main())
