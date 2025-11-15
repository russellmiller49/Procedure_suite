"""Typer CLI for registry extraction."""

from __future__ import annotations

import json

import typer

from modules.common.text_io import load_note

from .engine import RegistryEngine

app = typer.Typer(help="Run the registry extractor.")


@app.command()
def run(note: str, json_output: bool = typer.Option(False, "--json", help="Emit JSON output.")) -> None:
    text = load_note(note)
    engine = RegistryEngine()
    record = engine.run(text)
    if json_output:
        typer.echo(json.dumps(record.model_dump(), indent=2, default=str))
        return
    typer.echo("Registry Record:")
    typer.echo(record.model_dump_json(indent=2))


def main() -> None:  # pragma: no cover - CLI entrypoint
    app()


if __name__ == "__main__":
    main()

