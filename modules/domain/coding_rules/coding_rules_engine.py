"""Coding Rules Engine for CPT code filtering and validation.

This module provides the CodingRulesEngine class which encapsulates all
coding rules previously embedded in proc_autocode/coder.py::_generate_codes().

The engine supports three modes:
- "python": Uses the original Python rule implementations
- "json": Uses declarative JSON rules (future)
- "shadow": Runs both and compares results for validation

Rule ID Reference:
- R001: Out-of-domain filter
- R002: Linear vs Radial EBUS logic
- R003: Navigation evidence
- R004: Stent 4-gate evidence
- R005: BAL evidence
- R006: IPC insertion/removal
- R007: Pleural drainage registry-gated
- R008: Additional lobe TBLB
- R009: Parenchymal TBBx registry-required
- R010: Linear EBUS station counting
- R011: Radial EBUS
- R012: Tumor debulking
- R013: Therapeutic aspiration
- R014: Thoracoscopy site priority
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, Optional, Set

from observability.logging_config import get_logger

from .evidence_context import EvidenceContext, RulesResult

logger = get_logger("coding_rules_engine")


class CodingRulesEngine:
    """Engine for applying coding rules to CPT code candidates.

    This class encapsulates all coding rule logic, supporting both
    the original Python implementations and future JSON-based rules.

    Attributes:
        mode: Operating mode ("python", "json", or "shadow")
        valid_cpts: Set of valid CPT codes from knowledge base
    """

    VERSION = "coding_rules_engine_v1"

    def __init__(
        self,
        mode: Optional[str] = None,
        valid_cpts: Optional[Set[str]] = None,
    ):
        """Initialize the CodingRulesEngine.

        Args:
            mode: Operating mode. Defaults to CODING_RULES_MODE env var or "python"
            valid_cpts: Set of valid CPT codes from knowledge base
        """
        self.mode = mode or os.getenv("CODING_RULES_MODE", "python")
        self.valid_cpts = valid_cpts or set()

        logger.info(
            "CodingRulesEngine initialized",
            extra={"mode": self.mode, "version": self.VERSION},
        )

    @property
    def version(self) -> str:
        """Return the engine version."""
        return self.VERSION

    def apply_rules(
        self,
        context: EvidenceContext,
        valid_cpts: Optional[Set[str]] = None,
    ) -> RulesResult:
        """Apply all coding rules to the evidence context.

        This is the main entry point for rule evaluation.

        Args:
            context: EvidenceContext containing all procedure data
            valid_cpts: Override for valid CPT codes (uses self.valid_cpts if not provided)

        Returns:
            RulesResult containing final codes and rule application metadata
        """
        if valid_cpts:
            self.valid_cpts = valid_cpts

        if self.mode == "python":
            return self._apply_python_rules(context)
        elif self.mode == "json":
            return self._apply_json_rules(context)
        elif self.mode == "shadow":
            return self._apply_shadow_mode(context)
        else:
            logger.warning(f"Unknown mode '{self.mode}', defaulting to python")
            return self._apply_python_rules(context)

    def _apply_python_rules(self, context: EvidenceContext) -> RulesResult:
        """Apply rules using Python implementations.

        This method contains all the rule logic previously in _generate_codes().

        Args:
            context: EvidenceContext containing all procedure data

        Returns:
            RulesResult with filtered codes
        """
        # Start with a mutable copy of candidates
        result = RulesResult(codes=set(context.candidates))

        # Helper to discard code and its + variant
        def discard(code: str, rule_id: str, reason: str) -> None:
            result.remove_code(code, rule_id, reason)

        # Extract commonly used data
        groups = context.groups
        evidence = context.evidence
        registry = context.registry
        text_lower = context.text_lower

        # ========== RULE 1: OUT-OF-DOMAIN CODE FILTER ==========
        if self.valid_cpts:
            invalid_codes = set()
            for code in result.codes:
                norm_code = code.lstrip("+")
                if norm_code not in self.valid_cpts:
                    invalid_codes.add(code)
            for code in invalid_codes:
                discard(code, "R001_OUT_OF_DOMAIN", "Code not in IP knowledge base")

        # ========== RULE 2: LINEAR vs RADIAL EBUS LOGIC ==========
        if "bronchoscopy_ebus_linear" in groups:
            if "31629" in result.codes:
                result.upgrade_code("31629", "31652", "R002_EBUS_LINEAR_UPGRADE")
            else:
                result.add_code("31652", "R002_EBUS_LINEAR_UPGRADE")

            if "+31633" in result.codes:
                result.upgrade_code("+31633", "31653", "R002_EBUS_LINEAR_UPGRADE")

        # R002b: Radial-only exclusion
        if "bronchoscopy_ebus_radial" in groups and "bronchoscopy_ebus_linear" not in groups:
            discard("31652", "R002b_RADIAL_ONLY_EXCLUSION", "Radial-only case")
            discard("31653", "R002b_RADIAL_ONLY_EXCLUSION", "Radial-only case")

        # ========== RULE 3: NAVIGATION (31627) ==========
        nav_ev = evidence.get("bronchoscopy_navigation", {})
        nav_tool_in_lesion = bool(context.navigation_context.get("tool_in_lesion"))
        nav_sampling_tools = context.navigation_context.get("sampling_tools") or []
        nav_performed = (
            context.navigation_context.get("performed")
            or nav_tool_in_lesion
            or bool(nav_sampling_tools)
            or "navigation" in (context.term_hits.get("procedure_categories") or ())
            or "bronchoscopy_navigation" in groups
        )
        if not nav_performed:
            discard("31627", "R003_NAVIGATION_EVIDENCE", "Navigation not performed")
        elif not (nav_ev.get("platform") and (nav_ev.get("concept") or nav_ev.get("direct"))):
            discard("31627", "R003_NAVIGATION_EVIDENCE", "Missing platform or concept/direct evidence")

        # ========== RULE 4: STENT CODES (4-GATE) ==========
        stent_ev = evidence.get("bronchoscopy_therapeutic_stent", {})
        has_stent_evidence = (
            stent_ev.get("stent_word")
            and stent_ev.get("placement_action")
            and (stent_ev.get("tracheal_location") or stent_ev.get("bronchial_location"))
            and not stent_ev.get("stent_negated")
        )

        if not has_stent_evidence:
            for code in ("31631", "31636", "31638", "31637"):
                discard(code, "R004_STENT_4GATE", "Missing stent evidence")
        else:
            has_tracheal = stent_ev.get("tracheal_location")
            has_bronchial = stent_ev.get("bronchial_location")

            if has_tracheal and not has_bronchial:
                discard("31636", "R004b_STENT_LOCATION_SELECT", "Tracheal only")
            elif has_bronchial and not has_tracheal:
                discard("31631", "R004b_STENT_LOCATION_SELECT", "Bronchial only")
            elif not has_tracheal and not has_bronchial:
                discard("31631", "R004b_STENT_LOCATION_SELECT", "No location")
                discard("31636", "R004b_STENT_LOCATION_SELECT", "No location")

            if not stent_ev.get("multiple_stents"):
                discard("31637", "R004c_STENT_MULTIPLE", "No multiple stents evidence")

            if not (stent_ev.get("revision_action") and stent_ev.get("has_preexisting")):
                discard("31638", "R004d_STENT_REVISION", "No revision evidence")

        # ========== RULE 5: BAL (31624) ==========
        bal_ev = evidence.get("bronchoscopy_bal", {})
        if not bal_ev.get("bal_explicit"):
            discard("31624", "R005_BAL_EVIDENCE", "No explicit BAL evidence")
        if bal_ev.get("pleural_context"):
            discard("31624", "R005_BAL_EVIDENCE", "Pleural context present")

        # ========== RULE 6: IPC (32550/32552) ==========
        ipc_ev = evidence.get("tunneled_pleural_catheter", {})
        if not (ipc_ev.get("ipc_mentioned") and ipc_ev.get("insertion_action")):
            discard("32550", "R006_IPC_INSERTION", "No IPC insertion evidence")
        if not ipc_ev.get("removal_action"):
            discard("32552", "R006b_IPC_REMOVAL", "No IPC removal evidence")
        if ipc_ev.get("removal_action") and ipc_ev.get("insertion_action"):
            discard("32552", "R006c_IPC_MUTUAL_EXCLUSION", "Both insertion and removal - default to insertion")

        # ========== RULE 7: PLEURAL DRAINAGE (32556/32557) ==========
        pleural_type = registry.get("pleural_procedure_type")
        pleural_catheter_type = registry.get("pleural_catheter_type")
        pleural_ok = pleural_type == "Chest Tube" or bool(pleural_catheter_type)
        pleural_ok = pleural_ok or bool(context.registry_get("pleural_procedures", "chest_tube", "performed"))
        pleural_ok = pleural_ok or bool(context.registry_get("pleural_procedures", "ipc", "performed"))
        if not pleural_ok:
            discard("32556", "R007_PLEURAL_REGISTRY", "No registry pleural evidence")
            discard("32557", "R007_PLEURAL_REGISTRY", "No registry pleural evidence")

        # ========== RULE 8: ADDITIONAL LOBE TBLB (+31632) ==========
        lobe_ev = evidence.get("bronchoscopy_biopsy_additional_lobe", {})
        lobe_count = lobe_ev.get("lobe_count", 0)
        if lobe_count < 2 and not lobe_ev.get("explicit_multilobe"):
            discard("31632", "R008_ADDITIONAL_LOBE", "Less than 2 lobes")

        # ========== RULE 9: PARENCHYMAL TBBx (31628) ==========
        has_parenchymal_tbbx = False
        try:
            num_tbbx = registry.get("bronch_num_tbbx")
            if num_tbbx is None:
                num_tbbx = context.registry_get(
                    "procedures_performed", "transbronchial_biopsy", "number_of_samples"
                )
            if num_tbbx is not None:
                has_parenchymal_tbbx = int(num_tbbx) > 0
        except Exception:
            has_parenchymal_tbbx = False

        tbbx_tool = registry.get("bronch_tbbx_tool") or context.registry_get(
            "procedures_performed", "transbronchial_biopsy", "forceps_type"
        )
        if not tbbx_tool:
            tbbx_tool = context.registry_get(
                "procedures_performed", "transbronchial_cryobiopsy", "cryoprobe_size_mm"
            )
        if tbbx_tool:
            has_parenchymal_tbbx = True

        biopsy_sites = registry.get("bronch_biopsy_sites") or context.registry_get(
            "procedures_performed", "transbronchial_biopsy", "locations"
        )
        if biopsy_sites:
            has_parenchymal_tbbx = True

        if not has_parenchymal_tbbx:
            discard("31628", "R009_TBBX_REGISTRY", "No registry TBBx evidence")
            discard("+31632", "R009_TBBX_REGISTRY", "No registry TBBx evidence")

        # ========== RULE 10: LINEAR EBUS STATION COUNTING ==========
        linear_ev = evidence.get("bronchoscopy_ebus_linear", {})
        if not (linear_ev.get("ebus") and linear_ev.get("station_context")):
            discard("31652", "R010_EBUS_STATION_COUNT", "No EBUS station evidence")
            discard("31653", "R010_EBUS_STATION_COUNT", "No EBUS station evidence")
        else:
            station_count = linear_ev.get("station_count", 0)
            if station_count >= 3:
                discard("31652", "R010_EBUS_STATION_COUNT", "3+ stations - use 31653")
            else:
                discard("31653", "R010_EBUS_STATION_COUNT", "1-2 stations - use 31652")

        # ========== RULE 11: RADIAL EBUS (+31654) ==========
        radial_ev = evidence.get("bronchoscopy_ebus_radial", {})
        radial_registry = bool(
            context.radial_context.get("performed")
            or context.radial_context.get("visualization")
            or registry.get("nav_rebus_used")
            or registry.get("nav_rebus_view")
        )
        radial_from_text = "bronchoscopy_ebus_radial" in groups and radial_ev.get("radial")
        if not (radial_from_text or (radial_ev.get("radial") and radial_registry)):
            discard("31654", "R011_RADIAL_EBUS", "No radial EBUS evidence")

        # ========== RULE 12: TUMOR DEBULKING (31640/31641) ==========
        ablation_terms = [
            "apc", "argon", "electrocautery", "cautery", "laser", "ablation",
            "cryotherapy", "cryoablation", "rfa", "radiofrequency"
        ]
        excision_terms = [
            "snare", "forceps excision", "mechanical debulking", "excision of tumor",
            "tumor excision", "debridement"
        ]
        has_ablation = any(t in text_lower for t in ablation_terms)
        has_excision = any(t in text_lower for t in excision_terms)

        if has_stent_evidence:
            discard("31640", "R012b_DEBULKING_STENT_BUNDLE", "Bundled with stent")
            discard("31641", "R012b_DEBULKING_STENT_BUNDLE", "Bundled with stent")
        else:
            if "31640" in result.codes and "31641" in result.codes:
                if has_ablation:
                    discard("31640", "R012c_DEBULKING_TECHNIQUE_SELECT", "Ablative - keep 31641")
                elif has_excision:
                    discard("31641", "R012c_DEBULKING_TECHNIQUE_SELECT", "Mechanical - keep 31640")
                else:
                    discard("31640", "R012c_DEBULKING_TECHNIQUE_SELECT", "Default to 31641")

        # ========== RULE 13: THERAPEUTIC ASPIRATION (31645/31646) ==========
        aspiration_terms = [
            "therapeutic aspiration", "aspiration of secretions", "aspirate secretions",
            "suction removal", "suctioning of blood", "aspiration of mucus",
            "mucus plug aspiration", "aspirated clot", "clot aspiration",
            "clearance of secretions", "removal of secretions"
        ]
        has_aspiration = any(t in text_lower for t in aspiration_terms)
        if not has_aspiration:
            discard("31645", "R013_ASPIRATION", "No aspiration evidence")
            discard("31646", "R013_ASPIRATION", "No aspiration evidence")

        # ========== RULE 14: THORACOSCOPY SITE PRIORITY ==========
        thoracoscopy_ev = evidence.get("thoracoscopy", {})
        thoracoscopy_codes_present = result.codes & {
            "32601", "32602", "32604", "32606", "32607", "32608", "32609"
        }

        if thoracoscopy_codes_present:
            has_biopsy_code = bool(
                thoracoscopy_codes_present & {"32604", "32606", "32609", "32602", "32607", "32608"}
            )

            if has_biopsy_code and "32601" in result.codes:
                discard("32601", "R014b_BIOPSY_TRUMPS_DIAGNOSTIC", "Biopsy code present")

            remaining_thoracoscopy = result.codes & {
                "32601", "32604", "32606", "32609", "32607"
            }

            if len(remaining_thoracoscopy) > 1:
                pleural_site = thoracoscopy_ev.get("pleural_site", False)
                pericardial_site = thoracoscopy_ev.get("pericardial_site", False)
                mediastinal_site = thoracoscopy_ev.get("mediastinal_site", False)
                lung_site = thoracoscopy_ev.get("lung_site", False)

                codes_to_keep = set()
                if pleural_site and "32609" in remaining_thoracoscopy:
                    codes_to_keep.add("32609")
                if pericardial_site and "32604" in remaining_thoracoscopy:
                    codes_to_keep.add("32604")
                if mediastinal_site and "32606" in remaining_thoracoscopy:
                    codes_to_keep.add("32606")
                if lung_site and "32607" in remaining_thoracoscopy:
                    codes_to_keep.add("32607")

                if not codes_to_keep and thoracoscopy_ev.get("has_biopsy", False):
                    for preferred in ["32609", "32604", "32606", "32607"]:
                        if preferred in remaining_thoracoscopy:
                            codes_to_keep.add(preferred)
                            break

                if not codes_to_keep and "32601" in remaining_thoracoscopy:
                    codes_to_keep.add("32601")

                for code in remaining_thoracoscopy - codes_to_keep:
                    discard(code, "R014c_SITE_PRIORITY_SELECT", "Lower priority site")

            if thoracoscopy_ev.get("temporary_drain_bundled", False):
                for drain_code in ["32556", "32557"]:
                    discard(drain_code, "R014d_TEMP_DRAIN_BUNDLE", "Bundled with thoracoscopy")

        return result

    def _apply_json_rules(self, context: EvidenceContext) -> RulesResult:
        """Apply rules using JSON configuration.

        Args:
            context: EvidenceContext containing all procedure data

        Returns:
            RulesResult with filtered codes
        """
        from .json_rules_evaluator import JSONRulesEvaluator

        # Load evaluator (cached singleton would be better for production)
        evaluator = JSONRulesEvaluator.load_from_file()

        if not evaluator.rules:
            logger.warning("No JSON rules loaded, falling back to Python")
            return self._apply_python_rules(context)

        return evaluator.apply_rules(context, self.valid_cpts)

    def _apply_shadow_mode(self, context: EvidenceContext) -> RulesResult:
        """Run both Python and JSON rules, compare, and log differences.

        Args:
            context: EvidenceContext containing all procedure data

        Returns:
            RulesResult from Python rules (source of truth during migration)
        """
        python_result = self._apply_python_rules(context)
        json_result = self._apply_json_rules(context)

        # Compare results
        python_codes = python_result.codes
        json_codes = json_result.codes

        if python_codes != json_codes:
            added_by_json = json_codes - python_codes
            removed_by_json = python_codes - json_codes

            logger.warning(
                "coding_rules_mismatch",
                extra={
                    "python_codes": sorted(python_codes),
                    "json_codes": sorted(json_codes),
                    "added_by_json": sorted(added_by_json),
                    "removed_by_json": sorted(removed_by_json),
                },
            )

        # Return Python result as source of truth
        return python_result
