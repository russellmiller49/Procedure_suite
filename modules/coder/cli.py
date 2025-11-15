"""Typer CLI for running the coder pipeline."""

from __future__ import annotations

import json

import typer

from modules.common.text_io import load_note

from .engine import CoderEngine

app = typer.Typer(help="Run the procedure suite CPT coder.")


@app.command()
def run(note: str, json_output: bool = typer.Option(False, "--json", help="Emit JSON output.")) -> None:
    """Run the coder against NOTE (path or raw text)."""

    text = load_note(note)
    engine = CoderEngine()
    result = engine.run(text)

    if json_output:
        typer.echo(json.dumps(result.model_dump(), indent=2))
        return

    typer.echo("CPT Decisions:")
    for code in result.codes:
        mods = f" ({','.join(code.modifiers)})" if code.modifiers else ""
        typer.echo(f"- {code.cpt}{mods}: {code.description}")
    if result.warnings:
        typer.echo("Warnings:")
        for warning in result.warnings:
            typer.echo(f"  - {warning}")


def main() -> None:  # pragma: no cover - Typer entry point
    app()


if __name__ == "__main__":  # pragma: no cover - CLI module
    main()

