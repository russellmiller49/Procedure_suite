#!/usr/bin/env python3
"""Run fast PR or full nightly quality gates and emit comparable artifacts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.common.quality_gate_reports import build_report_delta, render_delta_markdown, write_json, write_text


PR_PYTEST_TARGETS = [
    "tests/registry/test_regression_pack.py",
    "tests/registry/test_quality_pass_runner.py",
    "tests/reporting/test_reporter_batch_regressions.py",
    "tests/quality/test_unified_quality_matrix.py",
    "tests/quality/test_precision_suppressions.py",
    "tests/quality/test_reporter_seed_dual_path_matrix.py",
    "tests/scripts/test_eval_golden.py",
    "tests/scripts/test_reporter_seed_eval_tools.py",
    "tests/api/test_report_seed_llm_findings.py",
    "tests/reporting/test_debug_notes_gating.py",
]

PR_EXTRACTION_INPUT = ROOT / "tests" / "fixtures" / "unified_quality_corpus.json"
PR_EXTRACTION_BASELINE = ROOT / "reports" / "unified_quality_corpus_extraction_baseline.json"
PR_REPORTER_INPUT = ROOT / "tests" / "fixtures" / "reporter_seed_eval_samples.json"
PR_REPORTER_LLM_FIXTURE = ROOT / "tests" / "fixtures" / "reporter_seed_eval_llm_fixture.json"
PR_REPORTER_BASELINE = ROOT / "reports" / "reporter_seed_registry_extract_fields_baseline.json"
PR_REPORTER_LLM_BASELINE = ROOT / "reports" / "reporter_seed_llm_findings_baseline.json"
PR_REPORTER_COMPARE_BASELINE = ROOT / "reports" / "reporter_seed_dual_path_compare.json"

FULL_REPORTER_INPUT = ROOT / "tests" / "fixtures" / "reporter_golden_dataset.json"
FULL_REPORTER_PROMPT_FIELD = "input_text"
FULL_REPORTER_LLM_FIXTURE = ROOT / "tests" / "fixtures" / "reporter_seed_eval_llm_fixture_full.json"
FULL_REPORTER_BASELINE = ROOT / "reports" / "reporter_seed_registry_extract_fields_full_baseline.json"
FULL_REPORTER_LLM_BASELINE = ROOT / "reports" / "reporter_seed_llm_findings_full_baseline.json"
FULL_REPORTER_COMPARE_BASELINE = ROOT / "reports" / "reporter_seed_dual_path_full_compare_baseline.json"


@dataclass(frozen=True)
class StepResult:
    name: str
    status: str
    command: list[str]
    stdout_path: str | None = None
    stderr_path: str | None = None
    output_path: str | None = None
    returncode: int | None = None
    error: str | None = None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", choices=["pr", "nightly"], required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--allow-online-llm",
        action="store_true",
        help="Permit live llm_findings calls instead of the frozen fixture path.",
    )
    return parser.parse_args(argv)


def _run_command(
    *,
    name: str,
    command: list[str],
    output_dir: Path,
    env: dict[str, str] | None = None,
) -> StepResult:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        env=env or os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )
    stdout_path = output_dir / f"{name}.stdout.txt"
    stderr_path = output_dir / f"{name}.stderr.txt"
    stdout_path.write_text(proc.stdout or "", encoding="utf-8")
    stderr_path.write_text(proc.stderr or "", encoding="utf-8")
    return StepResult(
        name=name,
        status="passed" if proc.returncode == 0 else "failed",
        command=command,
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        returncode=proc.returncode,
        error=None if proc.returncode == 0 else f"command failed with exit code {proc.returncode}",
    )


def _write_skip_artifact(path: Path, *, kind: str, reason: str, metadata: dict[str, Any] | None = None) -> None:
    write_json(
        path,
        {
            "schema_version": "procedure_suite.quality_gate.skip.v1",
            "kind": kind,
            "status": "skipped",
            "reason": reason,
            "metadata": metadata or {},
        },
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_extraction_gate(path: Path) -> None:
    payload = _load_json(path)
    summary = dict(payload.get("summary") or {})
    pass_rate = float(summary.get("pass_rate", 0.0))
    failed_cases = int(summary.get("failed_cases", 0))
    if failed_cases != 0 or pass_rate < 1.0:
        raise RuntimeError(f"Extraction fixture gate failed: failed_cases={failed_cases}, pass_rate={pass_rate}")


def _assert_reporter_seed_gate(path: Path) -> None:
    payload = _load_json(path)
    summary = dict(payload.get("summary") or {})
    failed_cases = int(summary.get("failed_cases", 0))
    forbidden_rate = float(summary.get("forbidden_artifact_case_rate", 0.0))
    if failed_cases != 0:
        raise RuntimeError(f"Reporter eval failed cases present in {path}: {failed_cases}")
    if forbidden_rate != 0.0:
        raise RuntimeError(f"Reporter eval forbidden artifacts present in {path}: rate={forbidden_rate}")


def _assert_compare_gate(path: Path) -> None:
    payload = _load_json(path)
    counts = dict(payload.get("counts") or {})
    mismatch_cases = int(counts.get("critical_presence_mismatch_cases", 0))
    right_worse_fallback_cases = int(counts.get("right_worse_fallback_cases", 0))
    if mismatch_cases != 0:
        raise RuntimeError(f"Reporter seed-path critical presence mismatches found: {mismatch_cases}")
    if right_worse_fallback_cases != 0:
        raise RuntimeError(f"Reporter challenger fallback regressed in {right_worse_fallback_cases} cases")


def _generate_full_llm_fixture(*, fixture_path: Path, output_dir: Path) -> StepResult:
    command = [
        sys.executable,
        str(ROOT / "ops" / "tools" / "build_reporter_seed_fixture.py"),
        "--input",
        str(FULL_REPORTER_INPUT),
        "--output",
        str(fixture_path),
        "--prompt-field",
        FULL_REPORTER_PROMPT_FIELD,
        "--completion-source",
        "completion_canonical",
    ]
    return _run_command(name="build_full_llm_fixture", command=command, output_dir=output_dir)


def _render_diff_sections(diff_jobs: list[tuple[str, Path, Path]]) -> list[str]:
    lines: list[str] = []
    for title, current_path, baseline_path in diff_jobs:
        if not current_path.exists():
            lines.append(f"### {title}")
            lines.append(f"- Current report missing: `{current_path}`")
            continue
        if not baseline_path.exists():
            lines.append(f"### {title}")
            lines.append(f"- Baseline missing: `{baseline_path}`")
            continue
        delta = build_report_delta(current_path=current_path, baseline_path=baseline_path)
        delta_path = current_path.with_name(f"{current_path.stem}.delta.json")
        write_json(delta_path, delta)
        lines.append(render_delta_markdown(delta, title=title))
    return lines


def _reporter_eval_command(
    *,
    script_name: str,
    input_path: Path,
    output_path: Path,
    prompt_field: str,
    seed_fixture: Path | None = None,
) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "ops" / "tools" / script_name),
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--prompt-field",
        prompt_field,
        "--strict",
    ]
    if seed_fixture is not None:
        command.extend(["--seed-fixture", str(seed_fixture)])
    return command


def _create_summary(
    *,
    tier: str,
    steps: list[StepResult],
    diff_sections: list[str],
    output_dir: Path,
) -> None:
    failed_steps = [step for step in steps if step.status == "failed"]
    lines = [
        f"## Quality Gates ({tier})",
        f"- Output directory: `{output_dir}`",
        f"- Passed steps: `{sum(1 for step in steps if step.status == 'passed')}`",
        f"- Failed steps: `{len(failed_steps)}`",
    ]
    for step in steps:
        lines.append(
            f"- `{step.name}`: `{step.status}`"
            + (f" (exit `{step.returncode}`)" if step.returncode is not None else "")
        )
    if diff_sections:
        lines.append("")
        lines.extend(diff_sections)
    write_text(output_dir / "summary.md", "\n".join(lines) + "\n")
    write_json(
        output_dir / "summary.json",
        {
            "schema_version": "procedure_suite.quality_gate.run.v1",
            "tier": tier,
            "output_dir": str(output_dir),
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "command": step.command,
                    "stdout_path": step.stdout_path,
                    "stderr_path": step.stderr_path,
                    "output_path": step.output_path,
                    "returncode": step.returncode,
                    "error": step.error,
                }
                for step in steps
            ],
        },
    )


def run_pr(output_dir: Path) -> int:
    steps: list[StepResult] = []
    pytest_command = [sys.executable, "-m", "pytest", "-q", *PR_PYTEST_TARGETS]
    steps.append(_run_command(name="focused_pytest", command=pytest_command, output_dir=output_dir))

    extraction_output = output_dir / "unified_quality_corpus_extraction.json"
    steps.append(
        _run_command(
            name="extraction_eval",
            command=[
                sys.executable,
                str(ROOT / "ml" / "scripts" / "eval_golden.py"),
                "--input",
                str(PR_EXTRACTION_INPUT),
                "--output",
                str(extraction_output),
                "--fail-under",
                "100",
            ],
            output_dir=output_dir,
        )
    )
    if steps[-1].status == "passed":
        _assert_extraction_gate(extraction_output)

    baseline_output = output_dir / "reporter_seed_registry_extract_fields.json"
    steps.append(
        _run_command(
            name="reporter_seed_registry_eval",
            command=_reporter_eval_command(
                script_name="eval_reporter_prompt_baseline.py",
                input_path=PR_REPORTER_INPUT,
                output_path=baseline_output,
                prompt_field="prompt_text",
            ),
            output_dir=output_dir,
        )
    )
    if steps[-1].status == "passed":
        _assert_reporter_seed_gate(baseline_output)

    llm_output = output_dir / "reporter_seed_llm_findings.json"
    steps.append(
        _run_command(
            name="reporter_seed_llm_eval",
            command=_reporter_eval_command(
                script_name="eval_reporter_prompt_llm_findings.py",
                input_path=PR_REPORTER_INPUT,
                output_path=llm_output,
                prompt_field="prompt_text",
                seed_fixture=PR_REPORTER_LLM_FIXTURE,
            ),
            output_dir=output_dir,
        )
    )
    if steps[-1].status == "passed":
        _assert_reporter_seed_gate(llm_output)

    compare_output = output_dir / "reporter_seed_compare.json"
    steps.append(
        _run_command(
            name="reporter_seed_compare",
            command=[
                sys.executable,
                str(ROOT / "ops" / "tools" / "compare_reporter_seed_paths.py"),
                "--left-report",
                str(baseline_output),
                "--right-report",
                str(llm_output),
                "--output",
                str(compare_output),
            ],
            output_dir=output_dir,
        )
    )
    if steps[-1].status == "passed":
        _assert_compare_gate(compare_output)

    diff_sections = _render_diff_sections(
        [
            ("Extraction Delta", extraction_output, PR_EXTRACTION_BASELINE),
            ("Reporter Baseline Delta", baseline_output, PR_REPORTER_BASELINE),
            ("Reporter LLM Delta", llm_output, PR_REPORTER_LLM_BASELINE),
            ("Reporter Compare Delta", compare_output, PR_REPORTER_COMPARE_BASELINE),
        ]
    )
    _create_summary(tier="pr", steps=steps, diff_sections=diff_sections, output_dir=output_dir)
    return 0 if all(step.status == "passed" for step in steps) else 1


def run_nightly(output_dir: Path, *, allow_online_llm: bool) -> int:
    steps: list[StepResult] = []
    pytest_command = [sys.executable, "-m", "pytest", "-q", *PR_PYTEST_TARGETS]
    steps.append(_run_command(name="focused_pytest", command=pytest_command, output_dir=output_dir))

    extraction_output = output_dir / "unified_quality_corpus_extraction_full.json"
    steps.append(
        _run_command(
            name="extraction_eval_full",
            command=[
                sys.executable,
                str(ROOT / "ml" / "scripts" / "eval_golden.py"),
                "--input",
                str(PR_EXTRACTION_INPUT),
                "--output",
                str(extraction_output),
                "--fail-under",
                "100",
            ],
            output_dir=output_dir,
        )
    )
    if steps[-1].status == "passed":
        _assert_extraction_gate(extraction_output)

    baseline_output = output_dir / "reporter_seed_registry_extract_fields_full.json"
    steps.append(
        _run_command(
            name="reporter_seed_registry_eval_full",
            command=_reporter_eval_command(
                script_name="eval_reporter_prompt_baseline.py",
                input_path=FULL_REPORTER_INPUT,
                output_path=baseline_output,
                prompt_field=FULL_REPORTER_PROMPT_FIELD,
            ),
            output_dir=output_dir,
        )
    )
    if steps[-1].status == "passed":
        _assert_reporter_seed_gate(baseline_output)

    llm_output = output_dir / "reporter_seed_llm_findings_full.json"
    if allow_online_llm:
        llm_command = _reporter_eval_command(
            script_name="eval_reporter_prompt_llm_findings.py",
            input_path=FULL_REPORTER_INPUT,
            output_path=llm_output,
            prompt_field=FULL_REPORTER_PROMPT_FIELD,
        )
    else:
        fixture_path = FULL_REPORTER_LLM_FIXTURE
        if fixture_path.exists():
            steps.append(
                StepResult(
                    name="build_full_llm_fixture",
                    status="passed",
                    command=[],
                    output_path=str(fixture_path),
                )
            )
        else:
            fixture_path = output_dir / FULL_REPORTER_LLM_FIXTURE.name
            fixture_step = _generate_full_llm_fixture(fixture_path=fixture_path, output_dir=output_dir)
            steps.append(fixture_step)
        if steps[-1].status != "passed":
            _write_skip_artifact(
                llm_output,
                kind="reporter_seed_eval",
                reason="failed to build frozen llm fixture",
                metadata={"fixture_path": str(fixture_path)},
            )
            llm_command = []
        else:
            llm_command = _reporter_eval_command(
                script_name="eval_reporter_prompt_llm_findings.py",
                input_path=FULL_REPORTER_INPUT,
                output_path=llm_output,
                prompt_field=FULL_REPORTER_PROMPT_FIELD,
                seed_fixture=fixture_path,
            )

    if llm_command:
        steps.append(
            _run_command(
                name="reporter_seed_llm_eval_full",
                command=llm_command,
                output_dir=output_dir,
            )
        )
        if steps[-1].status == "passed":
            _assert_reporter_seed_gate(llm_output)
    else:
        steps.append(
            StepResult(
                name="reporter_seed_llm_eval_full",
                status="failed",
                command=[],
                output_path=str(llm_output),
                error="llm evaluation command not constructed",
            )
        )

    compare_output = output_dir / "reporter_seed_compare_full.json"
    if baseline_output.exists() and llm_output.exists():
        steps.append(
            _run_command(
                name="reporter_seed_compare_full",
                command=[
                    sys.executable,
                    str(ROOT / "ops" / "tools" / "compare_reporter_seed_paths.py"),
                    "--left-report",
                    str(baseline_output),
                    "--right-report",
                    str(llm_output),
                    "--output",
                    str(compare_output),
                ],
                output_dir=output_dir,
            )
        )
        if steps[-1].status == "passed":
            _assert_compare_gate(compare_output)
    else:
        _write_skip_artifact(
            compare_output,
            kind="reporter_seed_compare",
            reason="baseline or llm reporter report missing",
            metadata={"left": str(baseline_output), "right": str(llm_output)},
        )
        steps.append(
            StepResult(
                name="reporter_seed_compare_full",
                status="failed",
                command=[],
                output_path=str(compare_output),
                error="comparison inputs missing",
            )
        )

    diff_sections = _render_diff_sections(
        [
            ("Extraction Delta", extraction_output, PR_EXTRACTION_BASELINE),
            ("Reporter Full Baseline Delta", baseline_output, FULL_REPORTER_BASELINE),
            ("Reporter Full LLM Delta", llm_output, FULL_REPORTER_LLM_BASELINE),
            ("Reporter Full Compare Delta", compare_output, FULL_REPORTER_COMPARE_BASELINE),
        ]
    )
    _create_summary(tier="nightly", steps=steps, diff_sections=diff_sections, output_dir=output_dir)
    return 0 if all(step.status == "passed" for step in steps) else 1


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.tier == "pr":
        return run_pr(output_dir)
    return run_nightly(output_dir, allow_online_llm=bool(args.allow_online_llm))


if __name__ == "__main__":
    raise SystemExit(main())
