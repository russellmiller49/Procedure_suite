"""Judge module for proposing registry self-corrections (Phase 6)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from modules.common.llm import LLMService
from modules.registry.schema import RegistryRecord


class PatchProposal(BaseModel):
    rationale: str
    json_patch: list[dict[str, Any]]
    evidence_quote: str


class RegistryCorrectionJudge:
    def __init__(self, llm: LLMService | None = None) -> None:
        self.llm = llm or LLMService(task="judge")

    def propose_correction(
        self,
        note_text: str,
        record: RegistryRecord,
        discrepancy: str,
        *,
        focused_procedure_text: str | None = None,
    ) -> PatchProposal | None:
        """Ask LLM if the discrepancy warrants a correction.

        Returns a PatchProposal if a fix is high-confidence, else None.
        """
        system_prompt = (
            "You are a strict clinical registry auditor. "
            "Your job is to fix MISSING data in a registry record based on a specific discrepancy.\n"
            "Rules:\n"
            "1. Only fix what is explicitly missing/wrong based on the discrepancy.\n"
            "2. You must provide a JSON Patch (RFC 6902) to apply the fix.\n"
            "3. You must provide a VERBATIM quote that proves the fix. "
            "If FOCUSED PROCEDURE TEXT is provided, the quote must come from that section.\n"
            "4. If the evidence is ambiguous or weak, return null (do not fix).\n"
            "5. Do NOT hallucinate quotes. The quote must exist exactly in the text.\n"
        )

        focused_section = ""
        if focused_procedure_text is not None and focused_procedure_text.strip():
            focused_section = f"""
FOCUSED PROCEDURE TEXT (preferred evidence source):
{focused_procedure_text}
"""

        user_prompt = f"""
RAW NOTE TEXT:
{note_text}
{focused_section}

Current Registry Record (JSON):
{record.model_dump_json(exclude_none=True)}

Discrepancy Detected:
{discrepancy}

Task:
If the discrepancy represents a valid omission that is CLEARLY supported by the text, generate a JSON patch to fix it.
Return JSON with keys: "rationale", "json_patch", "evidence_quote".
"""
        try:
            response = self.llm.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=PatchProposal,
                temperature=0.0,
            )
            return response
        except Exception:
            return None


__all__ = ["PatchProposal", "RegistryCorrectionJudge"]
