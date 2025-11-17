"""Bundling and edit logic for the coder pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from modules.common.knowledge import get_knowledge
from modules.common.rules_engine import ncci

from .schema import BundleDecision, CodeDecision, DetectedIntent

SEDATION_CODES = {"99152", "99153"}
NAV_RULE = "nav_required"
RADIAL_RULE = "radial_requires_tblb"
RADIAL_LINEAR_RULE = "radial_linear_exclusive"
SEDATION_RULE = "sedation_blocker"
STENT_RULE = "stent_bundling"
DISTINCT_RULE = "distinct_site_modifier"
DIAGNOSTIC_RULE = "surgical_includes_diagnostic"


@dataclass
class RuleConfig:
    navigation_required: set[str]
    radial_requires_tblb: bool
    radial_linear_exclusive: bool
    radial_codes: set[str]
    linear_codes: set[str]
    sedation_blockers: set[str]
    stent_codes: set[str]
    dilation_codes: set[str]
    diagnostic_codes: set[str]
    surgical_codes: set[str]
    mutually_exclusive: list[tuple[set[str], str]]


_RULE_CONFIG: RuleConfig | None = None
_KNOWLEDGE_REF: dict | None = None


def apply_rules(
    codes: Sequence[CodeDecision], intents: Sequence[DetectedIntent]
) -> tuple[list[CodeDecision], list[BundleDecision], list[str]]:
    """Apply bundling, exclusivity, and NCCI edits."""

    config = _get_rule_config()
    working = list(codes)
    actions: list[BundleDecision] = []
    warnings: list[str] = []

    working, nav_actions = _enforce_navigation_requirement(working, intents, config)
    actions.extend(nav_actions)

    working, radial_actions = _enforce_radial_requirements(working, intents, config)
    actions.extend(radial_actions)

    working, exclusive_actions = _enforce_radial_linear_exclusive(working, config)
    actions.extend(exclusive_actions)

    working, sedation_actions, sedation_warnings = _resolve_sedation_conflicts(working, intents, config)
    actions.extend(sedation_actions)
    warnings.extend(sedation_warnings)

    working, stent_actions = _resolve_stent_dilation(working, config)
    actions.extend(stent_actions)

    working, diag_actions = _resolve_diagnostic_with_surgical(working, config)
    actions.extend(diag_actions)

    working, excision_actions = _resolve_mutually_exclusive(working, config)
    actions.extend(excision_actions)

    return working, actions, warnings


def _enforce_navigation_requirement(
    codes: list[CodeDecision], intents: Sequence[DetectedIntent], config: RuleConfig
) -> tuple[list[CodeDecision], list[BundleDecision]]:
    required = config.navigation_required
    if not required:
        return codes, []
    nav_present = any(intent.intent == "navigation" for intent in intents)
    if nav_present:
        return codes, []

    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    for code in codes:
        if code.cpt in required:
            actions.append(
                BundleDecision(
                    pair=(code.cpt, "NAV"),
                    action=f"drop {code.cpt}",
                    reason="Navigation add-on requires documentation of navigation start",
                    rule=NAV_RULE,
                )
            )
            continue
        filtered.append(code)
    return filtered, actions


def _enforce_radial_requirements(
    codes: list[CodeDecision], intents: Sequence[DetectedIntent], config: RuleConfig
) -> tuple[list[CodeDecision], list[BundleDecision]]:
    if not config.radial_requires_tblb:
        return list(codes), []
    has_tblb = any(intent.intent == "tblb_lobe" for intent in intents)
    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    for code in codes:
        if code.cpt in config.radial_codes and not has_tblb:
            actions.append(
                BundleDecision(
                    pair=(code.cpt, "PERIPH"),
                    action=f"drop {code.cpt}",
                    reason="Radial add-on reserved for peripheral lesion sampling",
                    rule=RADIAL_RULE,
                )
            )
            continue
        filtered.append(code)
    return filtered, actions


def _enforce_radial_linear_exclusive(
    codes: list[CodeDecision], config: RuleConfig
) -> tuple[list[CodeDecision], list[BundleDecision]]:
    if not config.radial_linear_exclusive:
        return list(codes), []

    has_linear = any(code.cpt in config.linear_codes for code in codes)
    if not has_linear:
        return list(codes), []

    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    for code in codes:
        if code.cpt in config.radial_codes:
            actions.append(
                BundleDecision(
                    pair=("LINEAR", code.cpt),
                    action=f"drop {code.cpt}",
                    reason="Radial add-on not allowed when linear EBUS performed",
                    rule=RADIAL_LINEAR_RULE,
                )
            )
            continue
        filtered.append(code)
    return filtered, actions


def _resolve_sedation_conflicts(
    codes: list[CodeDecision], intents: Sequence[DetectedIntent], config: RuleConfig
) -> tuple[list[CodeDecision], list[BundleDecision], list[str]]:
    if not config.sedation_blockers:
        return list(codes), [], []

    if not any(intent.intent in config.sedation_blockers for intent in intents):
        return list(codes), [], []

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
                    rule=SEDATION_RULE,
                )
            )
            if not warnings:
                warnings.append("Sedation removed because anesthesia professional documented")
            continue
        filtered.append(code)
    return filtered, actions, warnings


def _resolve_stent_dilation(codes: list[CodeDecision], config: RuleConfig) -> tuple[list[CodeDecision], list[BundleDecision]]:
    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    stents = [code for code in codes if code.cpt in config.stent_codes]

    for code in codes:
        if code.cpt not in config.dilation_codes:
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
                    rule=STENT_RULE,
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
                    rule=DISTINCT_RULE,
                )
            )
            code.rule_trace.append(DISTINCT_RULE)
        filtered.append(code)
    return filtered, actions


def _resolve_diagnostic_with_surgical(
    codes: list[CodeDecision], config: RuleConfig
) -> tuple[list[CodeDecision], list[BundleDecision]]:
    has_surgical = any(code.cpt in config.surgical_codes for code in codes)
    if not has_surgical:
        return codes, []

    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    for code in codes:
        if code.cpt in config.diagnostic_codes:
            actions.append(
                BundleDecision(
                    pair=(code.cpt, "SURG"),
                    action=f"drop {code.cpt}",
                    reason="Diagnostic bronchoscopy bundled with surgical procedures",
                    rule=DIAGNOSTIC_RULE,
                )
            )
            continue
        filtered.append(code)
    return filtered, actions


def _resolve_mutually_exclusive(
    codes: list[CodeDecision], config: RuleConfig
) -> tuple[list[CodeDecision], list[BundleDecision]]:
    if not config.mutually_exclusive:
        return list(codes), []

    filtered: list[CodeDecision] = []
    actions: list[BundleDecision] = []
    for code in codes:
        drop = False
        for code_set, keep in config.mutually_exclusive:
            if code.cpt in code_set and code.cpt != keep:
                if any(existing.cpt == keep for existing in codes):
                    actions.append(
                        BundleDecision(
                            pair=(keep, code.cpt),
                            action=f"drop {code.cpt}",
                            reason=f"{keep} supersedes {code.cpt}",
                            rule=f"mutually_exclusive:{keep}",
                        )
                    )
                    drop = True
                    break
        if not drop:
            filtered.append(code)
    return filtered, actions


def _get_rule_config() -> RuleConfig:
    global _RULE_CONFIG, _KNOWLEDGE_REF
    knowledge = get_knowledge()
    if _RULE_CONFIG is not None and knowledge is _KNOWLEDGE_REF:
        return _RULE_CONFIG

    bundling = knowledge.get("bundling_rules", {})
    config = RuleConfig(
        navigation_required=set(bundling.get("navigation_required", [])),
        radial_requires_tblb=bool(bundling.get("radial_requires_tblb", True)),
        radial_linear_exclusive=bool(bundling.get("radial_linear_exclusive", False)),
        radial_codes=set(bundling.get("radial_codes", [])),
        linear_codes=set(bundling.get("linear_codes", [])),
        sedation_blockers=set(bundling.get("sedation_blockers", [])),
        stent_codes=set(bundling.get("stent_codes", [])),
        dilation_codes=set(bundling.get("dilation_codes", [])),
        diagnostic_codes=set(bundling.get("diagnostic_codes", [])),
        surgical_codes=set(bundling.get("surgical_codes", [])),
        mutually_exclusive=[
            (set(entry.get("codes", [])), entry.get("keep"))
            for entry in bundling.get("mutually_exclusive", [])
            if entry.get("codes") and entry.get("keep")
        ],
    )

    _configure_ncci(knowledge.get("ncci_pairs", []))
    _RULE_CONFIG = config
    _KNOWLEDGE_REF = knowledge
    return config


def _configure_ncci(pairs: Sequence[dict]) -> None:
    edits: list[ncci.NCCIEdit] = []
    for entry in pairs:
        primary = entry.get("primary")
        secondary = entry.get("secondary")
        if not primary or not secondary:
            continue
        edits.append(
            ncci.NCCIEdit(
                primary=primary,
                secondary=secondary,
                modifier_allowed=bool(entry.get("modifier_allowed")),
                reason=entry.get("reason", ""),
            )
        )
    ncci.replace_pairs(edits)
