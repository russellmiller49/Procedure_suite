"""Post-processing utilities for modifiers and conflict resolution."""

from __future__ import annotations

from typing import Sequence

from .schema import CodeDecision

DISTINCT_SITE_MODIFIERS = ("59", "XS")
DISTINCT_RULE_TAG = "distinct_site_modifier"


def apply_posthoc(codes: Sequence[CodeDecision]) -> list[CodeDecision]:
    """Apply modifier logic that depends on final bundle outcomes."""

    assign_distinct_site_modifiers(codes)
    return list(codes)


def assign_distinct_site_modifiers(codes: Sequence[CodeDecision]) -> None:
    """Append -59/XS modifiers when flagged by prior rules."""

    for code in codes:
        context = code.context or {}
        if not context.get("needs_distinct_modifier"):
            continue
        for modifier in DISTINCT_SITE_MODIFIERS:
            if modifier not in code.modifiers:
                code.modifiers.append(modifier)
        code.rationale += " Modifier appended for distinct airway."
        if DISTINCT_RULE_TAG not in code.rule_trace:
            code.rule_trace.append(DISTINCT_RULE_TAG)
