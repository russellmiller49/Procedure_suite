"""Typer CLI for registry extraction."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from modules.common.knowledge_cli import print_knowledge_info
from modules.common.text_io import load_note

from .engine import RegistryEngine
from .schema import RegistryRecord

app = typer.Typer(help="Run the registry extractor.")
console = Console()


@app.callback()
def _cli_entry(
    _: typer.Context,
    knowledge_info: bool = typer.Option(
        False,
        "--knowledge-info",
        help="Print knowledge metadata and exit.",
        is_eager=True,
    ),
) -> None:
    if knowledge_info:
        print_knowledge_info(console)
        raise typer.Exit()


@app.command()
def run(
    note: str,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
    explain: bool = typer.Option(False, "--explain", help="Show field evidence."),
) -> None:
    text = load_note(note)
    engine = RegistryEngine()
    result = engine.run(text, explain=explain)
    if isinstance(result, tuple):
        record, evidence = result
        record.evidence = evidence
    else:
        record = result
    if json_output:
        typer.echo(json.dumps(record.model_dump(), indent=2, default=str))
        if explain:
            _print_evidence(record)
        return

    _print_registry(record)
    if explain:
        _print_evidence(record)


def _print_registry(record: RegistryRecord) -> None:
    table = Table(title="Registry Record", show_lines=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    data = record.model_dump(exclude={"evidence"})
    for field, value in data.items():
        table.add_row(field, _format_value(value))
    console.print(table)


def _print_evidence(record: RegistryRecord) -> None:
    if not record.evidence:
        console.print("No evidence captured.")
        return
    table = Table(title="Evidence", show_lines=False)
    table.add_column("Field", style="cyan")
    table.add_column("Spans")
    for field, spans in record.evidence.items():
        formatted = [
            (
                f"{span.section or 'Unknown'}: “{span.text.strip()}” "
                f"({span.start}-{span.end})"
            )
            for span in spans
        ]
        table.add_row(field, "\n".join(formatted))
    console.print(table)


def _format_value(value: object) -> str:
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
