"""Self-correction helpers for registry extraction.

This package contains:
- Phase 6 guarded self-correction loop utilities (judge/validate/apply).
- Legacy prompt-improvement tooling used by scripts (lazy-imported).
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.registry.self_correction.prompt_improvement import RegistryErrorExample

from app.registry.self_correction.apply import SelfCorrectionApplyError, apply_patch_to_record
from app.registry.self_correction.judge import PatchProposal, RegistryCorrectionJudge
from app.registry.self_correction.types import (
    SelfCorrectionMetadata,
    SelfCorrectionTrigger,
)
from app.registry.self_correction.validation import (
    ALLOWED_PATHS,
    ALLOWED_PATH_PREFIXES,
    validate_proposal,
)


def get_allowed_values(field_name: str) -> list[str]:
    from app.registry.self_correction.prompt_improvement import get_allowed_values as _impl

    return _impl(field_name)


def load_errors(path: str, target_field: str, max_examples: int = 20) -> list["RegistryErrorExample"]:
    from app.registry.self_correction.prompt_improvement import load_errors as _impl

    return _impl(path, target_field, max_examples=max_examples)


def build_self_correction_prompt(
    field_name: str,
    instruction_text: str,
    errors: list["RegistryErrorExample"],
    allowed_values: list[str],
) -> str:
    from app.registry.self_correction.prompt_improvement import build_self_correction_prompt as _impl

    return _impl(field_name, instruction_text, errors, allowed_values)


def suggest_improvements_for_field(
    field_name: str, allowed_values: list[str], max_examples: int = 20
) -> dict[str, Any]:
    from app.registry.self_correction.prompt_improvement import (
        suggest_improvements_for_field as _impl,
    )

    return _impl(field_name, allowed_values, max_examples=max_examples)


__all__ = [
    "SelfCorrectionTrigger",
    "SelfCorrectionMetadata",
    "PatchProposal",
    "RegistryCorrectionJudge",
    "ALLOWED_PATHS",
    "ALLOWED_PATH_PREFIXES",
    "validate_proposal",
    "apply_patch_to_record",
    "SelfCorrectionApplyError",
    "get_allowed_values",
    "load_errors",
    "build_self_correction_prompt",
    "suggest_improvements_for_field",
]
