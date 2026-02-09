#!/usr/bin/env python3
"""Distill reporter prompt/completion pairs into prompt->ProcedureBundle targets."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

# IMPORTANT: apply reproducibility/offline defaults *before* importing `app.*`.
# `app.common.llm` loads `.env` at import time unless `PROCSUITE_SKIP_DOTENV=1`,
# and OpenAI calls can occur unless `OPENAI_OFFLINE=1`.
#
# These are set with `setdefault` so callers can override via shell env.
_EARLY_DEFAULTS: dict[str, str] = {
    "PROCSUITE_SKIP_DOTENV": "1",
    "PROCSUITE_PIPELINE_MODE": "extraction_first",
    "REGISTRY_SELF_CORRECT_ENABLED": "0",
    "REGISTRY_LLM_FALLBACK_ON_COVERAGE_FAIL": "0",
    "PROCSUITE_FAST_MODE": "1",
    # Use deterministic extraction (no LLM-dependent engine).
    "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
    # Defensive: if any LLM-backed codepath is reached, force the stub.
    "REGISTRY_USE_STUB_LLM": "1",
    # Distillation should be deterministic/offline and fast. Disable RAW-ML auditing
    # (it loads `data/models/cpt_classifier.pkl` and is expensive per-row).
    "REGISTRY_AUDITOR_SOURCE": "disabled",
    "LLM_PROVIDER": "openai_compat",
    "OPENAI_OFFLINE": "1",
    "GEMINI_OFFLINE": "1",
}
for _k, _v in _EARLY_DEFAULTS.items():
    os.environ.setdefault(_k, _v)

# Allow running as a file (python ml/scripts/...) without installing the package.
# When executed by filename, Python sets sys.path[0] to this script's directory
# (ml/scripts), which would otherwise prevent `import app` from working.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.registry.application.registry_service import RegistryService
from app.reporting.engine import build_procedure_bundle_from_extraction
from ml.lib.reporter_bundle_codec import rough_token_len_for_payload
from proc_schemas.coding import FinalCode

DEFAULT_INPUT_DIR = Path("data/ml_training/reporter_prompt/v1")
DEFAULT_OUTPUT_DIR = Path("data/ml_training/reporter_prompt/v1")
SPLITS = ("train", "val", "test")

DATE_LINE_RE = re.compile(r"(?im)^\s*DATE OF PROCEDURE\s*:\s*(.+)$")

INDICATION_LINE_RE = re.compile(r"(?im)^\s*INDICATION\s+FOR\s+OPERATION\s*:?\s*(.*)$")

HARD_WARNING_PATTERNS = (
    "SILENT_FAILURE",
    "COVERAGE_FAIL",
    "REGISTRY_LLM_TIMEOUT_FALLBACK_TO_ENGINE",
)


@dataclass
class DistilledRow:
    row: dict[str, Any]
    rejected: bool
    rejection_reasons: list[str]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--splits",
        nargs="*",
        default=list(SPLITS),
        help="Splits to process (default: train val test)",
    )
    parser.add_argument(
        "--version",
        default="v3",
        choices=["v2", "v3"],
        help="Registry draft version for completeness scoring.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=250,
        help="Print a progress line every N rows per split (default: 250). Set 0 to disable.",
    )
    return parser.parse_args(argv)


def configure_reproducible_env() -> dict[str, str]:
    defaults = {
        "PROCSUITE_SKIP_DOTENV": "1",
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_SELF_CORRECT_ENABLED": "0",
        "REGISTRY_LLM_FALLBACK_ON_COVERAGE_FAIL": "0",
        "PROCSUITE_FAST_MODE": "1",
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        "REGISTRY_USE_STUB_LLM": "1",
        "REGISTRY_AUDITOR_SOURCE": "disabled",
        "LLM_PROVIDER": "openai_compat",
        "OPENAI_OFFLINE": "1",
        "GEMINI_OFFLINE": "1",
    }
    applied: dict[str, str] = {}
    for key, value in defaults.items():
        if key not in os.environ:
            os.environ[key] = value
            applied[key] = value
    return applied


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _parse_date_from_completion(text: str) -> date | None:
    m = DATE_LINE_RE.search(text or "")
    if not m:
        return None

    raw = m.group(1).strip()
    if not raw:
        return None
    if raw in {"[Date]", "Date", "Unknown", "[REDACTED]", "REDACTED"}:
        return None

    fmts = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%m/%d/%y",
        "%m-%d-%y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%B %d %Y",
        "%b %d %Y",
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    # Common scrubbed form: Month Day (no year). Treat as a sentinel year for
    # completeness gating only (this metadata does not flow into training targets).
    fmts_no_year = [
        "%B %d",
        "%b %d",
    ]
    for fmt in fmts_no_year:
        try:
            parsed = datetime.strptime(raw, fmt)
            return date(2000, parsed.month, parsed.day)
        except ValueError:
            continue

    m_num = re.match(r"^\s*(\d{1,2})[/-](\d{1,2})\s*$", raw)
    if m_num:
        month = int(m_num.group(1))
        day = int(m_num.group(2))
        if 1 <= month <= 12 and 1 <= day <= 31:
            return date(2000, month, day)
    return None


def _normalize_gender_to_sex(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower()
    if normalized in {"m", "male"}:
        return "M"
    if normalized in {"f", "female"}:
        return "F"
    if normalized in {"o", "other", "nonbinary", "non-binary"}:
        return "O"
    return None


def build_procedure_metadata(record_dict: dict[str, Any], completion_text: str) -> dict[str, Any]:
    patient_demographics = record_dict.get("patient_demographics")
    if not isinstance(patient_demographics, dict):
        patient_demographics = {}

    clinical_context = record_dict.get("clinical_context")
    if not isinstance(clinical_context, dict):
        clinical_context = {}

    procedure_setting = record_dict.get("procedure_setting")
    if not isinstance(procedure_setting, dict):
        procedure_setting = {}

    age_val = patient_demographics.get("age")
    if age_val is None:
        age_val = patient_demographics.get("age_years")

    indication = clinical_context.get("primary_indication") or clinical_context.get("indication") or ""
    if not str(indication or "").strip():
        extracted = extract_indication_from_completion(completion_text)
        if extracted:
            indication = extracted

    date_val = _parse_date_from_completion(completion_text)

    procedure_families = record_dict.get("procedure_families")
    if isinstance(procedure_families, list) and procedure_families:
        procedure_type = str(procedure_families[0])
    else:
        procedure_type = ""

    return {
        "patient": {
            "patient_id": patient_demographics.get("patient_id") or "",
            "mrn": patient_demographics.get("mrn") or "",
            "age": age_val,
            "sex": _normalize_gender_to_sex(patient_demographics.get("gender")),
        },
        "procedure": {
            "procedure_date": date_val.isoformat() if date_val else None,
            "procedure_type": procedure_type,
            "indication": str(indication or "").strip(),
            "urgency": "routine",
            "operator": str(procedure_setting.get("attending") or "").strip(),
            "facility": str(procedure_setting.get("location") or "").strip(),
        },
    }

def extract_indication_from_completion(text: str) -> str | None:
    """Best-effort indication extraction from canonical reporter completion text."""
    if not text:
        return None

    lines = str(text).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    header_idx: int | None = None
    inline_body: str | None = None
    for idx, line in enumerate(lines):
        m = INDICATION_LINE_RE.match(line or "")
        if m:
            header_idx = idx
            rest = (m.group(1) or "").strip()
            if rest:
                inline_body = rest
            break
    if header_idx is None:
        # Fallback: sometimes templates inline INDICATION on the DATE line.
        m_inline = re.search(r"(?is)\bINDICATION\s+FOR\s+OPERATION\b\s*:?\s*(.{0,500})", text)
        if not m_inline:
            return None
        candidate = m_inline.group(1)
        candidate = re.split(
            r"(?im)\b(?:CONSENT|PREOPERATIVE\s+DIAGNOSIS|POSTOPERATIVE\s+DIAGNOSIS|PROCEDURE)\b",
            candidate,
            maxsplit=1,
        )[0]
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if not candidate:
            return None
        m = re.search(r"(?i)\bpresents with\s+([^.\n]{3,200})", candidate)
        return (m.group(1).strip() if m else candidate)

    # Grab the next few non-empty lines until the next obvious section header.
    body: list[str] = []
    if inline_body:
        body.append(inline_body)
    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped:
            if body:
                break
            continue
        if stripped.isupper() and len(stripped) >= 6:
            break
        body.append(stripped)
        if len(body) >= 3:
            break

    if not body:
        return None
    joined = " ".join(body)

    m = re.search(r"(?i)\bpresents with\s+([^.\n]{3,200})", joined)
    if m:
        return m.group(1).strip()
    return joined.strip()


def strip_source_text_keys(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, child in value.items():
            if key == "source_text":
                continue
            out[key] = strip_source_text_keys(child)
        return out
    if isinstance(value, list):
        return [strip_source_text_keys(item) for item in value]
    return value


def prepare_bundle_target(bundle: Any) -> dict[str, Any]:
    payload = bundle.model_dump(
        exclude_none=True,
        exclude_unset=True,
        exclude_defaults=True,
    )
    payload.pop("free_text_hint", None)
    payload = strip_source_text_keys(payload)
    return payload


def _has_hard_warning(warnings: list[str]) -> bool:
    upper = "\n".join(warnings).upper()
    return any(pattern in upper for pattern in HARD_WARNING_PATTERNS)


def _build_final_codes(proc_id: str, cpt_codes: list[str]) -> list[FinalCode]:
    return [
        FinalCode(
            code=str(code),
            source="extraction_first",
            procedure_id=proc_id,
        )
        for code in cpt_codes
    ]

_COMPLETENESS_REQUIRED_DEDUCTIONS = {
    "patient.patient_id or patient.mrn": 2.0,
    "procedure.procedure_date": 1.5,
    "procedure.indication": 1.0,
}

_SCRUBBED_ALLOWED_MISSING_FIELDS = {
    "patient.patient_id or patient.mrn",
    "procedure.procedure_date",
}


def _completeness_accept(
    *,
    completeness_score: float,
    missing_fields: list[str],
) -> tuple[bool, list[str], float]:
    """Return (accepted, exceptions_used, adjusted_score).

    Completeness in `RegistryService.build_draft_entry()` penalizes missing patient ID,
    procedure date, and indication. In scrubbed training data, patient identifiers
    and dates are often intentionally absent; we therefore compute an adjusted score
    that adds back their fixed deductions, but still keeps procedure-specific
    completeness deductions (EBUS stations, stent details, etc.).
    """
    if completeness_score >= 0.8:
        return True, [], completeness_score

    missing = set(missing_fields or [])
    if not missing:
        return False, [], completeness_score

    exceptions_used: list[str] = []
    added = 0.0
    for field in sorted(missing & _SCRUBBED_ALLOWED_MISSING_FIELDS):
        added += float(_COMPLETENESS_REQUIRED_DEDUCTIONS.get(field, 0.0))
        exceptions_used.append(field)

    # Only allow exceptions when *all* missing fields are from the allowed scrubbed set.
    if not missing.issubset(_SCRUBBED_ALLOWED_MISSING_FIELDS):
        return False, [], completeness_score

    # Reverse the normalized score back into a 0-10 scale to add back fixed deductions.
    adjusted = min(1.0, max(0.0, (float(completeness_score) * 10.0 + added) / 10.0))
    if adjusted >= 0.8:
        return True, exceptions_used, adjusted

    return False, [], adjusted


def process_row(
    row: dict[str, Any],
    *,
    split: str,
    registry_service: RegistryService,
    draft_version: str,
) -> DistilledRow:
    row_id = str(row.get("id") or "")
    prompt_text = str(row.get("prompt_text") or "").strip()
    completion_raw = str(row.get("completion_raw") or "").strip()
    completion_canonical = str(row.get("completion_canonical") or "").strip()

    rejection_reasons: list[str] = []

    if not row_id:
        rejection_reasons.append("missing_id")
    if not prompt_text:
        rejection_reasons.append("missing_prompt_text")
    if not completion_canonical:
        rejection_reasons.append("missing_completion_canonical")

    if rejection_reasons:
        return DistilledRow(
            row={
                "id": row_id or "<missing>",
                "split": split,
                "note_family": row.get("note_family"),
                "rejection_reasons": sorted(set(rejection_reasons)),
            },
            rejected=True,
            rejection_reasons=sorted(set(rejection_reasons)),
        )

    try:
        extraction = registry_service.extract_fields_extraction_first(completion_canonical)
    except Exception as exc:
        reasons = ["extraction_failed"]
        return DistilledRow(
            row={
                "id": row_id,
                "split": split,
                "note_family": row.get("note_family"),
                "rejection_reasons": reasons,
                "error": str(exc),
            },
            rejected=True,
            rejection_reasons=reasons,
        )

    warnings = [str(item) for item in (extraction.warnings or [])]
    audit_warnings = [str(item) for item in (extraction.audit_warnings or [])]

    if _has_hard_warning(warnings) or _has_hard_warning(audit_warnings):
        rejection_reasons.append("hard_warning_present")

    if extraction.validation_errors:
        rejection_reasons.append("validation_errors_present")

    record_dict = extraction.record.model_dump(exclude_none=True)
    # Use unnormalized completion text for metadata parsing so procedure dates
    # are preserved for completeness scoring.
    metadata_source_text = completion_raw or completion_canonical
    procedure_metadata = build_procedure_metadata(record_dict, metadata_source_text)

    final_codes = _build_final_codes(proc_id=row_id, cpt_codes=[str(c) for c in extraction.cpt_codes or []])

    completeness_score = 0.0
    completeness_score_adjusted = 0.0
    missing_fields: list[str] = []
    completeness_exceptions: list[str] = []

    try:
        draft = registry_service.build_draft_entry(
            procedure_id=row_id,
            final_codes=final_codes,
            procedure_metadata=procedure_metadata,
            version=draft_version,
        )
        completeness_score = float(draft.completeness_score)
        completeness_score_adjusted = completeness_score
        missing_fields = list(draft.missing_fields or [])

        accepted, completeness_exceptions, completeness_score_adjusted = _completeness_accept(
            completeness_score=completeness_score,
            missing_fields=missing_fields,
        )
        if not accepted:
            rejection_reasons.append("completeness_below_threshold")
    except Exception as exc:
        rejection_reasons.append("completeness_scoring_failed")
        return DistilledRow(
            row={
                "id": row_id,
                "split": split,
                "note_family": row.get("note_family"),
                "rejection_reasons": sorted(set(rejection_reasons)),
                "error": str(exc),
                "warnings": warnings,
                "audit_warnings": audit_warnings,
            },
            rejected=True,
            rejection_reasons=sorted(set(rejection_reasons)),
        )

    try:
        bundle = build_procedure_bundle_from_extraction(
            extraction.record,
            source_text=completion_canonical,
        )
        bundle_target_json = prepare_bundle_target(bundle)
        target_token_len = rough_token_len_for_payload(bundle_target_json)
    except Exception as exc:
        # Don't let a single bad normalization edge-case kill the whole distillation run.
        rejection_reasons.append("bundle_build_failed")
        return DistilledRow(
            row={
                "id": row_id,
                "split": split,
                "note_family": row.get("note_family"),
                "source_file": row.get("source_file"),
                "rejection_reasons": sorted(set(rejection_reasons)),
                "error": f"{type(exc).__name__}: {exc}",
                "warnings": warnings,
                "audit_warnings": audit_warnings,
                "validation_errors": [str(item) for item in (extraction.validation_errors or [])],
            },
            rejected=True,
            rejection_reasons=sorted(set(rejection_reasons)),
        )

    output_row = {
        "id": row_id,
        "split": split,
        "note_family": row.get("note_family"),
        "source_file": row.get("source_file"),
        "prompt_text": prompt_text,
        "completion_canonical": completion_canonical,
        "bundle_target_json": bundle_target_json,
        "target_token_len": target_token_len,
        "derived_cpt_codes": [str(c) for c in extraction.cpt_codes or []],
        "completeness_score": round(completeness_score, 4),
        "completeness_score_adjusted": round(completeness_score_adjusted, 4),
        "missing_fields": missing_fields,
        "completeness_patient_id_exception": "patient.patient_id or patient.mrn" in completeness_exceptions,
        "completeness_procedure_date_exception": "procedure.procedure_date" in completeness_exceptions,
        "completeness_exceptions": completeness_exceptions,
        "warnings": warnings,
        "audit_warnings": audit_warnings,
        "validation_errors": [str(item) for item in (extraction.validation_errors or [])],
    }

    rejected = bool(rejection_reasons)
    if rejected:
        output_row["rejection_reasons"] = sorted(set(rejection_reasons))

    return DistilledRow(
        row=output_row,
        rejected=rejected,
        rejection_reasons=sorted(set(rejection_reasons)),
    )


def _compute_token_budget(token_lengths: list[int]) -> dict[str, Any]:
    if not token_lengths:
        return {
            "accepted_rows": 0,
            "p99_target_tokens": 0,
            "p99_target_tokens_to_next_128": 0,
            "max_target_length": 0,
            "overflow_rate": 0.0,
            "enable_short_key_codec": False,
        }

    ordered = sorted(token_lengths)
    idx = max(0, ceil(0.99 * len(ordered)) - 1)
    p99 = int(ordered[idx])
    p99_next_128 = int(ceil(max(1, p99) / 128.0) * 128)
    max_target_length = int(min(1536, ceil(1.1 * p99_next_128)))

    overflow_count = sum(1 for value in ordered if value > max_target_length)
    overflow_rate = float(overflow_count / len(ordered))

    return {
        "accepted_rows": len(ordered),
        "p99_target_tokens": p99,
        "p99_target_tokens_to_next_128": p99_next_128,
        "max_target_length": max_target_length,
        "overflow_rate": round(overflow_rate, 6),
        "enable_short_key_codec": overflow_rate > 0.02,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    applied_env = configure_reproducible_env()

    # Distillation can emit extremely noisy per-row warnings (e.g., validation pruning).
    # Silence the loudest loggers so the run doesn't look "frozen" and doesn't waste
    # time flooding stdout/stderr. This does NOT affect returned warnings stored in rows.
    logging.getLogger("registry_engine").setLevel(logging.ERROR)
    logging.getLogger("common.llm").setLevel(logging.ERROR)
    logging.getLogger("ml_coder.predictor").setLevel(logging.ERROR)
    logging.getLogger("keyword_guard").setLevel(logging.ERROR)
    logging.getLogger("app.infra.nlp_warmup").setLevel(logging.ERROR)
    logging.getLogger("ner.inference").setLevel(logging.ERROR)
    logging.getLogger("coder.parallel_pathway").setLevel(logging.ERROR)
    logging.getLogger("registry_model_provider").setLevel(logging.ERROR)
    logging.getLogger("registry.inference_pytorch").setLevel(logging.ERROR)
    logging.getLogger("ml_coder.registry_predictor").setLevel(logging.ERROR)

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    registry_service = RegistryService()

    split_summaries: dict[str, Any] = {}
    all_token_lengths: list[int] = []

    for split in args.splits:
        split = str(split).strip().lower()
        if split not in SPLITS:
            raise ValueError(f"Unsupported split {split!r}; expected one of {SPLITS}")

        input_path = args.input_dir / f"reporter_prompt_{split}.jsonl"
        if not input_path.exists():
            raise FileNotFoundError(f"Split input not found: {input_path}")

        rows = load_jsonl(input_path)
        accepted_rows: list[dict[str, Any]] = []
        rejected_rows: list[dict[str, Any]] = []

        rejection_counter: dict[str, int] = {}

        total_rows = len(rows)
        progress_every = int(getattr(args, "progress_every", 0) or 0)
        for idx, row in enumerate(rows, start=1):
            distilled = process_row(
                row,
                split=split,
                registry_service=registry_service,
                draft_version=args.version,
            )
            if distilled.rejected:
                rejected_rows.append(distilled.row)
                for reason in distilled.rejection_reasons:
                    rejection_counter[reason] = rejection_counter.get(reason, 0) + 1
            else:
                accepted_rows.append(distilled.row)
                all_token_lengths.append(int(distilled.row.get("target_token_len") or 0))
            if progress_every > 0 and (idx % progress_every == 0 or idx == total_rows):
                print(
                    f"Split {split}: processed {idx}/{total_rows} "
                    f"accepted={len(accepted_rows)} rejected={len(rejected_rows)}"
                )

        accepted_path = output_dir / f"prompt_to_bundle_{split}.jsonl"
        rejected_path = output_dir / f"prompt_to_bundle_{split}_rejected.jsonl"

        write_jsonl(accepted_path, accepted_rows)
        write_jsonl(rejected_path, rejected_rows)

        split_token_audit = _compute_token_budget(
            [int(row.get("target_token_len") or 0) for row in accepted_rows]
        )

        split_summaries[split] = {
            "input_path": str(input_path),
            "accepted_path": str(accepted_path),
            "rejected_path": str(rejected_path),
            "rows_total": len(rows),
            "rows_accepted": len(accepted_rows),
            "rows_rejected": len(rejected_rows),
            "rejection_reasons": dict(sorted(rejection_counter.items())),
            "token_audit": split_token_audit,
        }

        print(
            f"Split {split}: accepted={len(accepted_rows)} rejected={len(rejected_rows)} "
            f"(output: {accepted_path.name})"
        )

    global_token_audit = _compute_token_budget(all_token_lengths)

    manifest = {
        "dataset_contract": "prompt_to_bundle.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(args.input_dir),
        "output_dir": str(output_dir),
        "draft_version": args.version,
        "environment_defaults_applied": applied_env,
        "quality_gate": {
            "hard_warning_patterns": list(HARD_WARNING_PATTERNS),
            "completeness_threshold": 0.8,
            "completeness_allowed_missing_fields": sorted(_SCRUBBED_ALLOWED_MISSING_FIELDS),
            "completeness_adjusted_for_scrubbed_fields": True,
        },
        "splits": split_summaries,
        "global_token_audit": global_token_audit,
        "recommended_training": {
            "enable_short_key_codec": global_token_audit["enable_short_key_codec"],
            "max_target_length": global_token_audit["max_target_length"],
        },
    }

    manifest_path = output_dir / "prompt_to_bundle_distill_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote distillation manifest: {manifest_path}")
    print(
        "Token audit: "
        f"p99={global_token_audit['p99_target_tokens']} "
        f"max_target_length={global_token_audit['max_target_length']} "
        f"codec={global_token_audit['enable_short_key_codec']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
