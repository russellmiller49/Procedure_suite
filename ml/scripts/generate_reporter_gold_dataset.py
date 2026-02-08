#!/usr/bin/env python3
"""Generate pilot reporter golden notes from synthetic short notes.

This script builds a versioned dataset of candidate golden reports using:
1) Generator LLM pass
2) Judge LLM pass
3) Optional one-shot repair pass when judge requests revision

It writes candidates, accepted/rejected splits, metrics, and a manual review queue.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logger = logging.getLogger(__name__)

DATASET_VERSION = "v1"
DEFAULT_INPUT_DIR = Path("data/knowledge/patient_note_texts")
DEFAULT_OUTPUT_DIR = Path("data/ml_training/reporter_golden/v1")
DEFAULT_GENERATOR_PROMPT = Path("configs/prompts/reporter_gold_generator_v1.txt")
DEFAULT_JUDGE_PROMPT = Path("configs/prompts/reporter_gold_judge_v1.txt")
DEFAULT_SAMPLE_SIZE = 200
DEFAULT_SEED = 42

SYN_NOTE_RE = re.compile(r"^(?P<base>.+?)_syn_(?P<num>\d+)$")
PLACEHOLDER_RE = re.compile(r"\[([^\]\n]{1,80})\]")

REQUIRED_SECTION_HEADERS = [
    "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT",
    "INDICATION FOR OPERATION",
    "CONSENT",
    "PREOPERATIVE DIAGNOSIS",
    "POSTOPERATIVE DIAGNOSIS",
    "PROCEDURE",
    "ANESTHESIA",
    "MONITORING",
    "COMPLICATIONS",
    "PROCEDURE IN DETAIL",
    "IMPRESSION / PLAN",
]

FORBIDDEN_ARTIFACT_PATTERNS = {
    "jinja_open": re.compile(r"\{\{"),
    "jinja_close": re.compile(r"\}\}"),
    "literal_none": re.compile(r"\bNone\b"),
    "todo": re.compile(r"\bTODO\b", flags=re.IGNORECASE),
}

ALLOWED_PLACEHOLDERS = {
    "Date",
    "Name",
    "Patient Name",
    "Age",
    "Sex",
    "Name / Self, Referred",
    "Referred Physician Name",
    "General anesthesia / airway type",
    "General anesthesia / Deep sedation",
    "General anesthesia / Moderate Sedation",
    "Fellow name",
    "Supine",
    "analysis type",
    "Additional ICD-10 if applicable",
    "Additional ICD-10 if applicable, e.g., COPD/Emphysema",
    "pleural effusion/nodules",
}

CRITICAL_FLAG_EXACT = {
    "established_tracheostomy_route",
    "granular_data.navigation_targets[*].fiducial_marker_placed",
}
CRITICAL_FLAG_PREFIXES = ("procedures_performed.", "pleural_procedures.")


@dataclass(frozen=True)
class SourceRecord:
    source_file: str
    patient_base_id: str
    input_note_id: str
    input_text: str
    anchor_note_id: str
    anchor_text: str
    procedure_family: str = "other"


class GeneratorResponse(BaseModel):
    report_text: str


class JudgeResponse(BaseModel):
    factuality: float
    completeness: float
    style: float
    verdict: Literal["accept", "revise", "reject"]
    reasons: list[str] = Field(default_factory=list)
    critical_hallucination: bool = False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a pilot reporter golden dataset from synthetic short notes."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing patient-note JSON maps.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for generated dataset artifacts.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help="Number of _syn_* notes to process (default: 200).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for deterministic sampling and review queue.",
    )
    parser.add_argument(
        "--generator-prompt",
        type=Path,
        default=DEFAULT_GENERATOR_PROMPT,
        help="Prompt template path for generation.",
    )
    parser.add_argument(
        "--judge-prompt",
        type=Path,
        default=DEFAULT_JUDGE_PROMPT,
        help="Prompt template path for judging.",
    )
    parser.add_argument(
        "--review-pass-fraction",
        type=float,
        default=0.10,
        help="Fraction of accepted examples to add to manual review queue (default: 0.10).",
    )
    return parser.parse_args(argv)


def ensure_openai_compat_provider() -> None:
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    if provider != "openai_compat":
        raise RuntimeError(
            "LLM_PROVIDER must be 'openai_compat' for reporter gold generation. "
            f"Current value: {provider or '<unset>'}"
        )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_prompt_template(template: str, values: dict[str, str]) -> str:
    return template.format(**values)


def load_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_source_records(input_dir: Path) -> tuple[list[SourceRecord], list[dict[str, Any]]]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    records: list[SourceRecord] = []
    skipped: list[dict[str, Any]] = []

    for json_path in sorted(input_dir.glob("*.json")):
        try:
            payload = load_json_file(json_path)
        except Exception as exc:
            skipped.append(
                {
                    "source_file": json_path.name,
                    "reason": "parse_error",
                    "details": str(exc),
                }
            )
            continue

        if not isinstance(payload, dict):
            skipped.append(
                {
                    "source_file": json_path.name,
                    "reason": "invalid_format",
                    "details": "expected top-level object",
                }
            )
            continue

        for note_id, note_text in payload.items():
            if not isinstance(note_id, str):
                continue
            syn_match = SYN_NOTE_RE.match(note_id)
            if not syn_match:
                continue
            if not isinstance(note_text, str) or not note_text.strip():
                skipped.append(
                    {
                        "source_file": json_path.name,
                        "reason": "missing_input_text",
                        "input_note_id": note_id,
                    }
                )
                continue

            patient_base_id = syn_match.group("base")
            anchor_note_id = patient_base_id
            anchor_text = payload.get(anchor_note_id)
            if not isinstance(anchor_text, str) or not anchor_text.strip():
                skipped.append(
                    {
                        "source_file": json_path.name,
                        "reason": "missing_anchor",
                        "input_note_id": note_id,
                        "anchor_note_id": anchor_note_id,
                    }
                )
                continue

            records.append(
                SourceRecord(
                    source_file=json_path.name,
                    patient_base_id=patient_base_id,
                    input_note_id=note_id,
                    input_text=note_text.strip(),
                    anchor_note_id=anchor_note_id,
                    anchor_text=anchor_text.strip(),
                )
            )

    records.sort(key=lambda r: (r.source_file, r.input_note_id))
    return records, skipped


def collect_performed_flags(record_data: dict[str, Any]) -> set[str]:
    flags: set[str] = set()

    procs = record_data.get("procedures_performed")
    if isinstance(procs, dict):
        for name, payload in procs.items():
            if isinstance(payload, dict) and payload.get("performed") is True:
                flags.add(f"procedures_performed.{name}.performed")

    pleural = record_data.get("pleural_procedures")
    if isinstance(pleural, dict):
        for name, payload in pleural.items():
            if isinstance(payload, dict) and payload.get("performed") is True:
                flags.add(f"pleural_procedures.{name}.performed")

    if record_data.get("established_tracheostomy_route") is True:
        flags.add("established_tracheostomy_route")

    granular = record_data.get("granular_data")
    if isinstance(granular, dict):
        targets = granular.get("navigation_targets")
        if isinstance(targets, list):
            for target in targets:
                if isinstance(target, dict) and target.get("fiducial_marker_placed") is True:
                    flags.add("granular_data.navigation_targets[*].fiducial_marker_placed")
                    break

    return flags


def infer_family_from_flags(flags: set[str]) -> str:
    lowered = " ".join(sorted(flags)).lower()
    if any(path.startswith("pleural_procedures.") for path in flags):
        return "pleural"
    if any(token in lowered for token in ("rigid", "stent", "trach", "airway")):
        return "airway"
    if any(token in lowered for token in ("ebus_tbna", "ebus_ifb", "ebus_19g_fnb", "eusb")):
        return "ebus"
    if any(token in lowered for token in ("robotic", "navigation", "radial_ebus", "peripheral_tbna")):
        return "navigation"
    if any(token in lowered for token in ("bal", "bronchial", "biopsy", "tbna_conventional")):
        return "diagnostic_bronch"
    return "other"


def annotate_procedure_families(
    records: list[SourceRecord],
    registry_service: Any,
) -> list[SourceRecord]:
    annotated: list[SourceRecord] = []

    for rec in records:
        family = "other"
        try:
            record, _warnings, _meta = registry_service.extract_record(rec.input_text)
            record_data = record.model_dump(exclude_none=True)
            family = infer_family_from_flags(collect_performed_flags(record_data))
        except Exception as exc:
            logger.warning("Family inference failed for %s: %s", rec.input_note_id, exc)
            family = "other"

        annotated.append(
            SourceRecord(
                source_file=rec.source_file,
                patient_base_id=rec.patient_base_id,
                input_note_id=rec.input_note_id,
                input_text=rec.input_text,
                anchor_note_id=rec.anchor_note_id,
                anchor_text=rec.anchor_text,
                procedure_family=family,
            )
        )
    return annotated


def stratified_sample_records(records: list[SourceRecord], sample_size: int, seed: int) -> list[SourceRecord]:
    if sample_size <= 0:
        raise ValueError("sample_size must be > 0")
    if sample_size > len(records):
        raise ValueError(f"sample_size={sample_size} is larger than available records={len(records)}")

    rng = random.Random(seed)
    by_family: dict[str, list[SourceRecord]] = {}
    for rec in records:
        by_family.setdefault(rec.procedure_family or "other", []).append(rec)

    for family_records in by_family.values():
        rng.shuffle(family_records)

    family_order = sorted(by_family.keys(), key=lambda name: (-len(by_family[name]), name))
    selected: list[SourceRecord] = []

    while len(selected) < sample_size:
        progressed = False
        for family in family_order:
            if by_family[family]:
                selected.append(by_family[family].pop())
                progressed = True
                if len(selected) >= sample_size:
                    break
        if not progressed:
            break

    if len(selected) != sample_size:
        raise RuntimeError(f"Failed to sample exactly {sample_size} records; got {len(selected)}")

    selected.sort(key=lambda r: (r.procedure_family, r.source_file, r.input_note_id))
    return selected


def find_missing_sections(report_text: str) -> list[str]:
    upper = report_text.upper()
    return [header for header in REQUIRED_SECTION_HEADERS if header.upper() not in upper]


def find_forbidden_artifacts(report_text: str) -> list[str]:
    found: list[str] = []
    for name, pattern in FORBIDDEN_ARTIFACT_PATTERNS.items():
        if pattern.search(report_text):
            found.append(name)
    return found


def find_disallowed_placeholders(report_text: str) -> list[str]:
    placeholders = [match.group(1).strip() for match in PLACEHOLDER_RE.finditer(report_text)]
    disallowed = sorted({p for p in placeholders if p not in ALLOWED_PLACEHOLDERS})
    return disallowed


def _is_critical_flag(path: str) -> bool:
    if path in CRITICAL_FLAG_EXACT:
        return True
    return path.startswith(CRITICAL_FLAG_PREFIXES)


def _safe_cpt_overlap_ratio(source_cpt: set[str], generated_cpt: set[str]) -> float:
    if not source_cpt and not generated_cpt:
        return 1.0
    if not source_cpt:
        return 0.0
    overlap = len(source_cpt & generated_cpt)
    return float(overlap) / float(len(source_cpt))


def extract_flags_and_cpt(note_text: str, registry_service: Any) -> tuple[set[str], set[str], list[str]]:
    result = registry_service.extract_fields_extraction_first(note_text)
    record_data = result.record.model_dump(exclude_none=True)
    flags = collect_performed_flags(record_data)
    cpt_codes = {str(code) for code in (result.cpt_codes or [])}
    warnings = [str(w) for w in (result.warnings or [])]
    return flags, cpt_codes, warnings


def run_deterministic_checks(
    *,
    input_text: str,
    anchor_text: str,
    candidate_text: str,
    registry_service: Any,
) -> dict[str, Any]:
    missing_sections = find_missing_sections(candidate_text)
    forbidden_artifacts = find_forbidden_artifacts(candidate_text)
    disallowed_placeholders = find_disallowed_placeholders(candidate_text)

    input_flags, input_cpt, input_warnings = extract_flags_and_cpt(input_text, registry_service)
    anchor_flags, anchor_cpt, anchor_warnings = extract_flags_and_cpt(anchor_text, registry_service)
    generated_flags, generated_cpt, generated_warnings = extract_flags_and_cpt(candidate_text, registry_service)

    source_union_flags = input_flags | anchor_flags
    source_union_cpt = input_cpt | anchor_cpt
    generated_extra_flags = sorted(generated_flags - source_union_flags)
    critical_generated_extra_flags = sorted([p for p in generated_extra_flags if _is_critical_flag(p)])
    cpt_overlap_ratio = _safe_cpt_overlap_ratio(source_union_cpt, generated_cpt)

    checks = {
        "required_sections_present": len(missing_sections) == 0,
        "missing_sections": missing_sections,
        "forbidden_artifacts_found": forbidden_artifacts,
        "placeholder_policy_ok": len(disallowed_placeholders) == 0,
        "disallowed_placeholders": disallowed_placeholders,
        "source_input_performed_flags": sorted(input_flags),
        "source_anchor_performed_flags": sorted(anchor_flags),
        "source_union_performed_flags": sorted(source_union_flags),
        "generated_performed_flags": sorted(generated_flags),
        "generated_extra_flags": generated_extra_flags,
        "critical_generated_extra_flags": critical_generated_extra_flags,
        "source_union_cpt_codes": sorted(source_union_cpt),
        "generated_cpt_codes": sorted(generated_cpt),
        "cpt_overlap_ratio": round(cpt_overlap_ratio, 4),
        "cpt_overlap_count": len(source_union_cpt & generated_cpt),
        "input_extract_warnings": input_warnings,
        "anchor_extract_warnings": anchor_warnings,
        "generated_extract_warnings": generated_warnings,
    }
    return checks


def build_generator_user_prompt(
    prompt_template: str,
    *,
    input_text: str,
    anchor_text: str,
    repair_feedback: str = "",
) -> str:
    return render_prompt_template(
        prompt_template,
        {
            "input_text": input_text,
            "anchor_text": anchor_text,
            "repair_feedback": repair_feedback or "None",
        },
    )


def build_judge_user_prompt(
    prompt_template: str,
    *,
    input_text: str,
    anchor_text: str,
    candidate_report: str,
) -> str:
    return render_prompt_template(
        prompt_template,
        {
            "input_text": input_text,
            "anchor_text": anchor_text,
            "candidate_report": candidate_report,
        },
    )


def run_generation_pass(llm_service: Any, user_prompt: str) -> GeneratorResponse:
    return llm_service.generate_json(
        system_prompt=(
            "You are an interventional pulmonology operative report generator. "
            "Return only valid JSON."
        ),
        user_prompt=user_prompt,
        response_model=GeneratorResponse,
        temperature=0.0,
    )


def run_judge_pass(llm_service: Any, user_prompt: str) -> JudgeResponse:
    return llm_service.generate_json(
        system_prompt=(
            "You are a strict medical documentation QA judge. "
            "Return only valid JSON."
        ),
        user_prompt=user_prompt,
        response_model=JudgeResponse,
        temperature=0.0,
    )


def evaluate_acceptance(
    checks: dict[str, Any],
    judge: JudgeResponse,
) -> tuple[bool, list[str]]:
    reject_reasons: list[str] = []

    if not checks.get("required_sections_present", False):
        reject_reasons.append("missing_required_sections")
    if checks.get("forbidden_artifacts_found"):
        reject_reasons.append("forbidden_artifacts")
    if not checks.get("placeholder_policy_ok", False):
        reject_reasons.append("disallowed_placeholders")
    if checks.get("critical_generated_extra_flags"):
        reject_reasons.append("critical_performed_flag_hallucination")

    if float(judge.factuality) < 0.85:
        reject_reasons.append("judge_factuality_below_threshold")
    if float(judge.style) < 0.85:
        reject_reasons.append("judge_style_below_threshold")
    if float(judge.completeness) < 0.80:
        reject_reasons.append("judge_completeness_below_threshold")
    if judge.critical_hallucination:
        reject_reasons.append("judge_critical_hallucination")
    if judge.verdict == "reject":
        reject_reasons.append("judge_rejected")
    if judge.verdict == "revise":
        reject_reasons.append("judge_requested_revision")

    return len(reject_reasons) == 0, sorted(set(reject_reasons))


def _model_for_task(task: str) -> str:
    task_key = task.strip().lower()
    if task_key == "structurer":
        return (os.getenv("OPENAI_MODEL_STRUCTURER") or os.getenv("OPENAI_MODEL") or "").strip() or "unknown"
    if task_key == "judge":
        return (os.getenv("OPENAI_MODEL_JUDGE") or os.getenv("OPENAI_MODEL") or "").strip() or "unknown"
    return (os.getenv("OPENAI_MODEL") or "").strip() or "unknown"


def process_source_record(
    *,
    source: SourceRecord,
    generator_prompt_template: str,
    judge_prompt_template: str,
    generator_llm: Any,
    judge_llm: Any,
    registry_service: Any,
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    repair_feedback = ""
    final_report = ""
    final_checks: dict[str, Any] = {}
    final_judge: JudgeResponse | None = None

    max_attempts = 2
    for attempt_index in range(1, max_attempts + 1):
        generation_prompt = build_generator_user_prompt(
            generator_prompt_template,
            input_text=source.input_text,
            anchor_text=source.anchor_text,
            repair_feedback=repair_feedback,
        )
        generated = run_generation_pass(generator_llm, generation_prompt)
        final_report = generated.report_text.strip()

        checks = run_deterministic_checks(
            input_text=source.input_text,
            anchor_text=source.anchor_text,
            candidate_text=final_report,
            registry_service=registry_service,
        )
        judge_prompt = build_judge_user_prompt(
            judge_prompt_template,
            input_text=source.input_text,
            anchor_text=source.anchor_text,
            candidate_report=final_report,
        )
        judge = run_judge_pass(judge_llm, judge_prompt)

        attempts.append(
            {
                "attempt_index": attempt_index,
                "repair_feedback": repair_feedback,
                "report_text": final_report,
                "deterministic_checks": checks,
                "judge_scores": {
                    "factuality": float(judge.factuality),
                    "completeness": float(judge.completeness),
                    "style": float(judge.style),
                },
                "judge_verdict": judge.verdict,
                "judge_reasons": list(judge.reasons or []),
                "judge_critical_hallucination": bool(judge.critical_hallucination),
            }
        )

        final_checks = checks
        final_judge = judge

        if judge.verdict != "revise":
            break
        if attempt_index >= max_attempts:
            break

        repair_parts: list[str] = []
        if judge.reasons:
            repair_parts.append("Judge feedback: " + "; ".join(judge.reasons))
        if checks.get("missing_sections"):
            repair_parts.append("Missing sections: " + "; ".join(checks["missing_sections"]))
        if checks.get("critical_generated_extra_flags"):
            repair_parts.append(
                "Critical hallucinated performed flags: "
                + "; ".join(checks["critical_generated_extra_flags"])
            )
        if checks.get("disallowed_placeholders"):
            repair_parts.append(
                "Disallowed placeholders: " + "; ".join(checks["disallowed_placeholders"])
            )
        repair_feedback = " | ".join(repair_parts) or "Revise for improved factuality/completeness/style."

    if final_judge is None:
        raise RuntimeError(f"No judge result produced for {source.input_note_id}")

    accepted, reject_reasons = evaluate_acceptance(final_checks, final_judge)

    candidate_id = f"reporter_gold_{DATASET_VERSION}_{source.input_note_id}"
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "id": candidate_id,
        "dataset_version": DATASET_VERSION,
        "source_file": source.source_file,
        "patient_base_id": source.patient_base_id,
        "input_note_id": source.input_note_id,
        "anchor_note_id": source.anchor_note_id,
        "input_text": source.input_text,
        "anchor_text": source.anchor_text,
        "ideal_output_candidate": final_report,
        "procedure_family": source.procedure_family,
        "generator_model": _model_for_task("structurer"),
        "judge_model": _model_for_task("judge"),
        "deterministic_checks": final_checks,
        "judge_scores": {
            "factuality": float(final_judge.factuality),
            "completeness": float(final_judge.completeness),
            "style": float(final_judge.style),
        },
        "judge_verdict": final_judge.verdict,
        "accepted": accepted,
        "reject_reasons": reject_reasons,
        "judge_reasons": list(final_judge.reasons or []),
        "judge_critical_hallucination": bool(final_judge.critical_hallucination),
        "attempts": attempts,
        "created_at": now_iso,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_review_queue_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "id",
        "input_note_id",
        "patient_base_id",
        "accepted",
        "judge_verdict",
        "factuality",
        "completeness",
        "style",
        "reject_reasons",
        "review_reason",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            scores = row.get("judge_scores") or {}
            writer.writerow(
                {
                    "id": row.get("id"),
                    "input_note_id": row.get("input_note_id"),
                    "patient_base_id": row.get("patient_base_id"),
                    "accepted": bool(row.get("accepted")),
                    "judge_verdict": row.get("judge_verdict"),
                    "factuality": scores.get("factuality"),
                    "completeness": scores.get("completeness"),
                    "style": scores.get("style"),
                    "reject_reasons": ";".join(row.get("reject_reasons") or []),
                    "review_reason": row.get("review_reason", ""),
                }
            )


def build_review_queue(
    *,
    accepted_rows: list[dict[str, Any]],
    rejected_rows: list[dict[str, Any]],
    seed: int,
    pass_fraction: float,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    queue: list[dict[str, Any]] = []

    for row in rejected_rows:
        enriched = dict(row)
        enriched["review_reason"] = "auto_rejected"
        queue.append(enriched)

    if accepted_rows:
        n_sample = int(round(len(accepted_rows) * pass_fraction))
        n_sample = max(0, min(len(accepted_rows), n_sample))
        if n_sample > 0:
            sampled = rng.sample(accepted_rows, n_sample)
            for row in sampled:
                enriched = dict(row)
                enriched["review_reason"] = "pass_sample"
                queue.append(enriched)

    queue.sort(key=lambda r: (r.get("review_reason", ""), r.get("id", "")))
    return queue


def compute_metrics(
    *,
    total_available: int,
    sampled: list[SourceRecord],
    candidates: list[dict[str, Any]],
    accepted: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
) -> dict[str, Any]:
    by_family_total: dict[str, int] = {}
    by_family_sampled: dict[str, int] = {}
    for rec in sampled:
        by_family_sampled[rec.procedure_family] = by_family_sampled.get(rec.procedure_family, 0) + 1

    for row in candidates:
        fam = str(row.get("procedure_family") or "other")
        by_family_total[fam] = by_family_total.get(fam, 0) + 1

    accept_rate = float(len(accepted)) / float(len(candidates)) if candidates else 0.0

    return {
        "dataset_version": DATASET_VERSION,
        "total_available_records": total_available,
        "sampled_records": len(sampled),
        "candidate_count": len(candidates),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accept_rate": round(accept_rate, 4),
        "skipped_count": len(skipped),
        "sampled_by_family": by_family_sampled,
        "candidate_by_family": by_family_total,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def _build_registry_service() -> Any:
    from app.registry.application.registry_service import RegistryService

    return RegistryService()


def _build_llm_service(task: str) -> Any:
    from app.common.llm import LLMService

    return LLMService(task=task)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    ensure_openai_compat_provider()

    generator_prompt_template = read_text(args.generator_prompt)
    judge_prompt_template = read_text(args.judge_prompt)

    logger.info("Collecting source records from %s", args.input_dir)
    source_records, skipped = collect_source_records(args.input_dir)
    logger.info("Found %d source records (%d skipped)", len(source_records), len(skipped))

    if args.sample_size > len(source_records):
        raise ValueError(
            f"Requested sample size {args.sample_size} exceeds available records {len(source_records)}"
        )

    registry_service = _build_registry_service()
    logger.info("Annotating procedure families for stratified sampling")
    annotated = annotate_procedure_families(source_records, registry_service)
    sampled = stratified_sample_records(annotated, args.sample_size, args.seed)
    logger.info("Selected %d sampled records", len(sampled))

    generator_llm = _build_llm_service(task="structurer")
    judge_llm = _build_llm_service(task="judge")

    candidates: list[dict[str, Any]] = []
    for idx, source in enumerate(sampled, start=1):
        logger.info("[%d/%d] Processing %s", idx, len(sampled), source.input_note_id)
        try:
            candidate = process_source_record(
                source=source,
                generator_prompt_template=generator_prompt_template,
                judge_prompt_template=judge_prompt_template,
                generator_llm=generator_llm,
                judge_llm=judge_llm,
                registry_service=registry_service,
            )
            candidates.append(candidate)
        except Exception as exc:
            logger.exception("Processing failed for %s", source.input_note_id)
            skipped.append(
                {
                    "source_file": source.source_file,
                    "reason": "processing_error",
                    "input_note_id": source.input_note_id,
                    "details": str(exc),
                }
            )

    accepted = [row for row in candidates if row.get("accepted") is True]
    rejected = [row for row in candidates if row.get("accepted") is not True]

    accepted_export: list[dict[str, Any]] = []
    for row in accepted:
        out = dict(row)
        out["ideal_output"] = row.get("ideal_output_candidate", "")
        accepted_export.append(out)

    review_queue = build_review_queue(
        accepted_rows=accepted,
        rejected_rows=rejected,
        seed=args.seed,
        pass_fraction=float(args.review_pass_fraction),
    )
    metrics = compute_metrics(
        total_available=len(source_records),
        sampled=sampled,
        candidates=candidates,
        accepted=accepted,
        rejected=rejected,
        skipped=skipped,
    )

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates_path = output_dir / "reporter_gold_candidates.jsonl"
    accepted_path = output_dir / "reporter_gold_accepted.jsonl"
    rejected_path = output_dir / "reporter_gold_rejected.jsonl"
    metrics_path = output_dir / "reporter_gold_metrics.json"
    queue_jsonl_path = output_dir / "reporter_gold_review_queue.jsonl"
    queue_csv_path = output_dir / "reporter_gold_review_queue.csv"
    skipped_path = output_dir / "reporter_gold_skipped_manifest.jsonl"

    write_jsonl(candidates_path, candidates)
    write_jsonl(accepted_path, accepted_export)
    write_jsonl(rejected_path, rejected)
    write_json(metrics_path, metrics)
    write_jsonl(queue_jsonl_path, review_queue)
    write_review_queue_csv(queue_csv_path, review_queue)
    write_jsonl(skipped_path, skipped)

    logger.info("Wrote candidates: %s", candidates_path)
    logger.info("Wrote accepted:   %s", accepted_path)
    logger.info("Wrote rejected:   %s", rejected_path)
    logger.info("Wrote metrics:    %s", metrics_path)
    logger.info("Wrote review q:   %s", queue_jsonl_path)
    logger.info("Wrote skipped:    %s", skipped_path)
    logger.info(
        "Summary: sampled=%d accepted=%d rejected=%d skipped=%d accept_rate=%.2f%%",
        metrics["sampled_records"],
        metrics["accepted_count"],
        metrics["rejected_count"],
        metrics["skipped_count"],
        float(metrics["accept_rate"]) * 100.0,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
