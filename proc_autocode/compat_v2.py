"""Compatibility shims for V2 CLI expectations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from proc_schemas.billing import BillingResult
from proc_schemas.procedure_report import ProcedureReport
from proc_report.engine import compose_report_from_text

from .engine import autocode


@dataclass
class CodeResultV2:
    code: str
    code_type: str = "CPT"
    description: str = ""
    modifiers: List[str] = field(default_factory=list)


@dataclass
class CodingAnalysisV2:
    primary_codes: List[CodeResultV2]
    addon_codes: List[CodeResultV2]
    sedation_codes: List[CodeResultV2]
    warnings: List[str]
    missing_documentation: List[str]
    compliance_notes: List[str]
    facility_notes: List[str]


class ProcedureCodingEngine:
    def analyze_procedure_report(self, payload: str | ProcedureReport) -> CodingAnalysisV2:
        report = self._ensure_report(payload)
        billing = autocode(report)
        primary, addon, sedation = self._partition(billing)
        return CodingAnalysisV2(
            primary_codes=primary,
            addon_codes=addon,
            sedation_codes=sedation,
            warnings=[c.get("rationale", "") for c in billing.ncci_conflicts],
            missing_documentation=[],
            compliance_notes=[],
            facility_notes=[],
        )

    def _ensure_report(self, payload: str | ProcedureReport) -> ProcedureReport:
        if isinstance(payload, ProcedureReport):
            return payload
        report, _ = compose_report_from_text(payload, {})
        return report

    def _partition(self, billing: BillingResult) -> Tuple[List[CodeResultV2], List[CodeResultV2], List[CodeResultV2]]:
        primary, addon, sedation = [], [], []
        for line in billing.codes:
            target = primary
            if line.cpt.startswith("+" ) or line.cpt in {"31653", "99153"}:
                target = addon
            if line.cpt.startswith("9915"):
                target = sedation
            target.append(CodeResultV2(code=line.cpt, description=line.reason, modifiers=line.modifiers))
        return primary, addon, sedation


def format_coding_results(analysis: CodingAnalysisV2) -> str:
    lines = ["=" * 60, "PROCEDURAL CODING ANALYSIS", "=" * 60]
    if analysis.primary_codes:
        lines.append("\nPRIMARY CODES:")
        lines.extend(f"  - {c.code} {c.description}".rstrip() for c in analysis.primary_codes)
    if analysis.addon_codes:
        lines.append("\nADD-ON CODES:")
        lines.extend(f"  - {c.code} {c.description}".rstrip() for c in analysis.addon_codes)
    if analysis.sedation_codes:
        lines.append("\nSEDATION:")
        lines.extend(f"  - {c.code}" for c in analysis.sedation_codes)
    if analysis.warnings:
        lines.append("\nWARNINGS:")
        lines.extend(f"  - {w}" for w in analysis.warnings if w)
    lines.append("\nVerify against payer policies.")
    return "\n".join(lines)
