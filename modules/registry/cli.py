"""Typer CLI for registry extraction."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from modules.common.text_io import load_note

from .engine import RegistryEngine

app = typer.Typer(help="Run the registry extractor.")
console = Console()


@app.command()
def run(
    note: str,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
    explain: bool = typer.Option(False, "--explain", help="Show field evidence."),
) -> None:
    text = load_note(note)
    engine = RegistryEngine()
    record = engine.run(text)
    if json_output:
        typer.echo(json.dumps(record.model_dump(), indent=2, default=str))
        if explain:
            _print_evidence(record)
        return

    _print_registry(record)
    if explain:
        _print_evidence(record)


def _print_registry(record) -> None:
    table = Table(title="Registry Record", show_lines=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    data = record.model_dump(exclude={"evidence"})
    for field, value in data.items():
        table.add_row(field, _format_value(value))
    console.print(table)


def _print_evidence(record) -> None:
    if not record.evidence:
        console.print("No evidence captured.")
        return
    table = Table(title="Evidence", show_lines=False)
    table.add_column("Field", style="cyan")
    table.add_column("Spans")
    for field, spans in record.evidence.items():
        formatted = [
            f"{span.section or 'Unknown'}: “{span.text.strip()}” ({span.start}-{span.end})" for span in spans
        ]
        table.add_row(field, "\n".join(formatted))
    console.print(table)


def _format_value(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "—"
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def main() -> None:  # pragma: no cover - CLI entrypoint
    app()


if __name__ == "__main__":
    main()
