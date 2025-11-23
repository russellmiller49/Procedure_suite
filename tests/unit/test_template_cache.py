from pathlib import Path

from proc_report.engine import default_template_registry


def _write_template(dir_path: Path, body: str) -> None:
    (dir_path / "sample.j2").write_text(body, encoding="utf-8")
    (dir_path / "sample.yaml").write_text(
        "\n".join(
            [
                "id: sample",
                "label: Sample",
                "category: test",
                "cpt_hints: []",
                "schema_id: test_schema",
                "output_section: PROCEDURE_DETAILS",
                "template_path: sample.j2",
                "proc_types: [test_proc]",
                "required_fields: []",
                "optional_fields: []",
            ]
        ),
        encoding="utf-8",
    )


def test_template_registry_cache_invalidation(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    _write_template(template_dir, "Sample template v1")

    first = default_template_registry(template_root=template_dir)
    second = default_template_registry(template_root=template_dir)
    assert first is second

    # Modify the template config to trigger cache invalidation
    _write_template(template_dir, "Sample template v2")
    third = default_template_registry(template_root=template_dir)
    assert third is not first
    assert len(third) == 1
