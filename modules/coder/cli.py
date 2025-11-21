"""Typer CLI for running the coder pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from modules.common.knowledge_cli import print_knowledge_info
from modules.common.text_io import load_note
from modules.ml_coder.training import MLB_PATH, PIPELINE_PATH, train_model

from .engine import CoderEngine

app = typer.Typer(help="Run the procedure suite CPT coder.")
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


@app.command("train-ml")
def train_ml(
    csv_path: Path = typer.Argument(..., exists=True, readable=True, help="Path to the training CSV")
) -> None:
    """Train the ML classifier using the provided dataset."""

    try:
        train_model(csv_path)
    except Exception as exc:  # pragma: no cover - CLI surface area
        typer.secho(f"ML training failed: {exc}", err=True)
        raise typer.Exit(code=1)

    console.print(
        f"[green]ML artifacts saved to[/green] {PIPELINE_PATH} and {MLB_PATH}"
    )


@app.command()
def run(
    note: str,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
    explain: bool = typer.Option(False, "--explain", help="Show rule trace and MER math."),
    allow_weak_sedation_docs: bool = typer.Option(
        False,
        "--allow-weak-sedation-docs",
        help="Emit sedation codes even when start/stop times or an observer statement are missing.",
    ),
) -> None:
    """Run the coder against NOTE (path or raw text)."""

    text = load_note(note)
    engine = CoderEngine(allow_weak_sedation_docs=allow_weak_sedation_docs)
    result = engine.run(text)

    if json_output:
        typer.echo(json.dumps(result.model_dump(), indent=2))
        if explain:
            _print_explain(result)
        return

    _print_summary(result)
    if explain:
        _print_explain(result)


def _print_summary(result) -> None:
    table = Table(title="CPT Decisions", show_lines=False)
    table.add_column("CPT", style="cyan", no_wrap=True)
    table.add_column("Description")
    table.add_column("Confidence", justify="right")
    table.add_column("Evidence")

    for code in result.codes:
        mods = f" ({','.join(code.modifiers)})" if code.modifiers else ""
        evidence = _format_evidence(code.evidence)
        table.add_row(
            f"{code.cpt}{mods}",
            code.description,
            f"{code.confidence:.2f}",
            evidence,
        )
    console.print(table)

    if result.warnings:
        console.print(Panel("\n".join(result.warnings), title="Warnings", style="yellow"))


def _print_explain(result) -> None:
    trace = Table(title="Rule Trace", show_lines=False)
    trace.add_column("CPT", style="cyan", no_wrap=True)
    trace.add_column("Rules Fired")
    for code in result.codes:
        trace.add_row(code.cpt, ", ".join(code.rule_trace) or "—")
    console.print(trace)

    if result.ncci_actions:
        actions = Table(title="Bundling & NCCI Actions", show_lines=False)
        actions.add_column("Pair")
        actions.add_column("Action")
        actions.add_column("Reason")
        actions.add_column("Rule")
        for action in result.ncci_actions:
            pair = " + ".join(action.pair)
            actions.add_row(pair, action.action, action.reason, action.rule or "—")
        console.print(actions)

    mer_summary = result.mer_summary or {}
    adjustments = mer_summary.get("adjustments") or []
    if adjustments:
        mer_table = Table(title="MER Allowables", show_lines=False)
        mer_table.add_column("CPT", style="cyan")
        mer_table.add_column("Role")
        mer_table.add_column("Allowed", justify="right")
        mer_table.add_column("Reduction", justify="right")
        for row in adjustments:
            mer_table.add_row(
                row.get("cpt", ""),
                row.get("role", ""),
                f"{row.get('allowed', 0):.2f}",
                f"{row.get('reduction', 0):.2f}",
            )
        console.print(mer_table)


def _format_evidence(spans) -> str:
    if not spans:
        return "—"
    first = spans[0]
    snippet = first.text.strip().replace("\n", " ")
    section = first.section or "Unknown"
    summary = f"{section}: “{snippet}” ({first.start}-{first.end})"
    if len(spans) > 1:
        summary += f" [+{len(spans) - 1} more]"
    return summary


def main() -> None:  # pragma: no cover - Typer entry point
    app()


if __name__ == "__main__":  # pragma: no cover - CLI module
    main()
