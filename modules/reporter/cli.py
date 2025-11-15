"""CLI for structured report generation and rendering."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from modules.common.text_io import load_note

from .engine import ReportEngine
from .schema import StructuredReport

app = typer.Typer(help="Reporter CLI")


@app.command("gen")
def generate(
    from_free_text: str = typer.Option(..., "--from-free-text", help="Source note path or text"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
) -> None:
    note = load_note(from_free_text)
    engine = ReportEngine()
    report = engine.from_free_text(note)
    if json_output:
        typer.echo(report.model_dump_json(indent=2))
    else:
        typer.echo(report.summary())


@app.command("render")
def render(
    report_path: Path = typer.Argument(..., exists=True),
    template: str = typer.Option("bronchoscopy", "--template", help="Template key or filename"),
) -> None:
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    if isinstance(payload, str):
        payload = json.loads(payload)
    report = StructuredReport(**payload)
    engine = ReportEngine()
    report = engine.validate_and_autofix(report)
    output = engine.render(report, template=template)
    typer.echo(output)


def main() -> None:  # pragma: no cover - CLI entry point
    app()


if __name__ == "__main__":  # pragma: no cover - CLI
    main()

