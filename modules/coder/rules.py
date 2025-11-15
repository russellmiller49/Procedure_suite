"""Bundling and edit logic for the coder pipeline."""

from __future__ import annotations

from typing import Iterable, Sequence, Tuple

from modules.common.rules_engine import ncci

from .schema import BundleDecision, CodeDecision, DetectedIntent

SURGICAL_CODES = {
    "31627",
    "31628",
    "+31632",
    "31630",
    "31636",
    "31652",
    "31653",
    "+31654",
}

DIAGNOSTIC_CODES = {"31622"}
STENT_CODES = {"31631", "31636", "+31637"}
DILATION_CODES = {"31630"}
RADIAL_CODES = {"+31654"}
LINEAR_CODES = {"31652", "31653"}
SEDATION_CODES = {"99152", "99153"}


def apply_rules(
    codes: Sequence[CodeDecision], intents: Sequence[DetectedIntent]
) -> tuple[list[CodeDecision], list[BundleDecision], list[str]]:
    """Apply bundling, exclusivity, and NCCI edits."""

    working = list(codes)
    actions: list[BundleDecision] = []
    warnings: list[str] = []

    working, nav_actions = _enforce_navigation_requirement(working, intents)
    actions.extend(nav_actions)

    working, radial_actions = _enforce_radial_requirements(working, intents)
    actions.extend(radial_actions)

    working, sedation_actions, sedation_warnings = _resolve_sedation_conflicts(working, intents)
    actions.extend(sedation_actions)
    warnings.extend(sedation_warnings)

    working, stent_actions = _resolve_stent_dilation(working)
    actions.extend(stent_actions)

    working, diag_actions = _resolve_diagnostic_with_surgical(working)
    actions.extend(diag_actions)

    working, excision_actions = _resolve_31640_31641(working)
    actions.extend(excision_actions)

    return working, actions, warnings


def _enforce_navigation_requirement(
    codes: list[CodeDecision], intents: Sequence[DetectedIntent]
) -> tuple[list[CodeDecision], list[BundleDecision]]:
    nav_present = any(intent.intent == "navigation" for intent in intents)
    if nav_present:
        return codes, []

    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    for code in codes:
        if code.cpt == "31627":
            actions.append(
                BundleDecision(
                    pair=("31627", "NAV"),
                    action="drop 31627",
                    reason="Navigation add-on requires documentation of navigation start",
                )
            )
            continue
        filtered.append(code)
    return filtered, actions


def _enforce_radial_requirements(
    codes: list[CodeDecision], intents: Sequence[DetectedIntent]
) -> tuple[list[CodeDecision], list[BundleDecision]]:
    has_tblb = any(intent.intent == "tblb_lobe" for intent in intents)
    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    for code in codes:
        if code.cpt in RADIAL_CODES and not has_tblb:
            actions.append(
                BundleDecision(
                    pair=(code.cpt, "PERIPH"),
                    action=f"drop {code.cpt}",
                    reason="Radial add-on reserved for peripheral lesion sampling",
                )
            )
            continue
        filtered.append(code)
    return filtered, actions


def _resolve_sedation_conflicts(
    codes: list[CodeDecision], intents: Sequence[DetectedIntent]
) -> tuple[list[CodeDecision], list[BundleDecision], list[str]]:
    has_anesthesia = any(intent.intent == "anesthesia" for intent in intents)
    if not has_anesthesia:
        return codes, [], []

    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    warnings: list[str] = []
    for code in codes:
        if code.cpt in SEDATION_CODES:
            actions.append(
                BundleDecision(
                    pair=(code.cpt, "ANES"),
                    action=f"drop {code.cpt}",
                    reason="Sedation not billed when separate anesthesia present",
                )
            )
            if not warnings:
                warnings.append("Sedation removed because anesthesia professional documented")
            continue
        filtered.append(code)
    return filtered, actions, warnings


def _resolve_stent_dilation(codes: list[CodeDecision]) -> tuple[list[CodeDecision], list[BundleDecision]]:
    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    stents = [code for code in codes if code.cpt in STENT_CODES]

    for code in codes:
        if code.cpt not in DILATION_CODES:
            filtered.append(code)
            continue
        site = (code.context or {}).get("site")
        matching_stent = next(
            (stent for stent in stents if (stent.context or {}).get("site") == site and site),
            None,
        )
        if matching_stent:
            actions.append(
                BundleDecision(
                    pair=(matching_stent.cpt, code.cpt),
                    action=f"drop {code.cpt}",
                    reason="Stent placement bundles dilation when same segment",
                )
            )
            continue
        if stents and ncci.allow_with_modifier(stents[0].cpt, code.cpt):
            code.context.setdefault("needs_distinct_modifier", True)
            actions.append(
                BundleDecision(
                    pair=(stents[0].cpt, code.cpt),
                    action=f"allow {code.cpt} with modifier",
                    reason="Distinct airway segment",
                )
            )
        filtered.append(code)
    return filtered, actions


def _resolve_diagnostic_with_surgical(
    codes: list[CodeDecision],
) -> tuple[list[CodeDecision], list[BundleDecision]]:
    has_surgical = any(code.cpt in SURGICAL_CODES for code in codes)
    if not has_surgical:
        return codes, []

    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    for code in codes:
        if code.cpt in DIAGNOSTIC_CODES:
            actions.append(
                BundleDecision(
                    pair=(code.cpt, "SURG"),
                    action=f"drop {code.cpt}",
                    reason="Diagnostic bronchoscopy bundled with surgical procedures",
                )
            )
            continue
        filtered.append(code)
    return filtered, actions


def _resolve_31640_31641(
    codes: list[CodeDecision],
) -> tuple[list[CodeDecision], list[BundleDecision]]:
    keep_31641 = any(code.cpt == "31641" for code in codes)
    if not keep_31641:
        return codes, []

    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    for code in codes:
        if code.cpt == "31640":
            actions.append(
                BundleDecision(
                    pair=("31641", "31640"),
                    action="drop 31640",
                    reason="Higher-valued modality 31641 reported",
                )
            )
            continue
        filtered.append(code)
    return filtered, actions
