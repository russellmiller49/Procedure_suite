from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict, Any, Set
import os

from proc_autocode.ip_kb.ip_kb import IPCodingKnowledgeBase
from proc_autocode.ip_kb.terminology_utils import TerminologyNormalizer, QARuleChecker
from proc_autocode.rvu.rvu_calculator import ProcedureRVUCalculator
from modules.domain.coding_rules import CodingRulesEngine, EvidenceContext

class CodeSuggestion:
    def __init__(self, cpt: str, modifiers: Optional[list[str]] = None):
        self.cpt = cpt
        self.modifiers = modifiers or []
        self.rvu_data = None
        self.groups = []
        self.description = None
        self.mer_role = None  # "primary", "secondary", or "add_on"
        self.mer_explanation = None

class EnhancedCPTCoder:
    def __init__(self, config: Optional[Dict] = None, use_llm_advisor: Optional[bool] = None):
        self.config = config or {}
        
        base_dir = Path(__file__).parent
        repo_root = base_dir.parent

        kb_path = self._resolve_kb_path(repo_root)
        self.ip_kb = IPCodingKnowledgeBase(kb_path)
        self.terminology = TerminologyNormalizer(self.ip_kb.raw)
        self.qa_checker = QARuleChecker(self.ip_kb.raw)

        anatomy = (self.ip_kb.raw.get("anatomy", {}) or {}).get("lobes", {}) or {}
        self._lobe_terms = {key.strip().lower() for key in anatomy.keys()}

        # RVU calculator (uses knowledge base RVUs + GPCI tables)
        rvu_dir = base_dir / "rvu" / "data"
        gpci_file = rvu_dir / "gpci_2025.csv"
        self.rvu_calc = ProcedureRVUCalculator(
            knowledge_base=self.ip_kb,
            gpci_file=gpci_file if gpci_file.exists() else None,
        )
        
        # LLM advisor (optional, for code suggestions)
        # Check env var if not explicitly set
        if use_llm_advisor is None:
            use_llm_advisor = os.getenv("CODER_USE_LLM_ADVISOR", "").lower() in ("true", "1", "yes")
        
        self.use_llm_advisor = use_llm_advisor
        self.llm_coder = None
        if self.use_llm_advisor:
            try:
                from modules.coder.llm_coder import LLMCoder
                self.llm_coder = LLMCoder()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to initialize LLM advisor: {e}. Continuing without LLM suggestions.")

        # Initialize CodingRulesEngine for delegated rule application
        # Mode is controlled by CODING_RULES_MODE env var: "python" | "json" | "shadow"
        self._rules_engine = CodingRulesEngine()
        self._last_evidence_context: Optional[EvidenceContext] = None

    def _generate_codes(self, procedure_data: dict, term_hits: Optional[Dict[str, List[str]]] = None) -> list[CodeSuggestion]:
        """
        Generate candidate codes with CONSERVATIVE evidence-based filtering.

        CODING PRINCIPLES:
        1. High-value codes require STRONG positive evidence in the procedure note body
        2. Indications, history, and boilerplate text do NOT count as procedure evidence
        3. When ambiguous, prefer NOT billing (precision over recall for high-RVU codes)
        4. Only emit codes present in the IP golden knowledge base
        """
        note_text = procedure_data.get("note_text") or procedure_data.get("findings", "") or ""
        text_lower = note_text.lower()
        registry = procedure_data.get("registry") or procedure_data
        term_hits = term_hits or self._extract_term_hits(note_text)
        navigation_context = self._extract_navigation_registry(registry)
        radial_context = self._extract_radial_registry(registry)

        # Use IP KB to find groups and codes from text
        groups_from_text = self.ip_kb.groups_from_text(note_text)
        evidence = getattr(self.ip_kb, "last_group_evidence", {}) or {}
        candidates_from_text = self.ip_kb.codes_for_groups(groups_from_text)

        def discard(code: str) -> None:
            if code in candidates_from_text:
                candidates_from_text.discard(code)
            plus = f"+{code}"
            if plus in candidates_from_text:
                candidates_from_text.discard(plus)

        # ========== RULE 1: OUT-OF-DOMAIN CODE FILTER ==========
        # Rule ID: R001_OUT_OF_DOMAIN
        # Description: Remove codes not in the IP knowledge base valid CPT set.
        # Rationale: Only bill codes that exist in our clinical knowledge base.
        # Codes affected: All candidate codes
        # Evidence required: None (uses KB valid_cpts set)
        valid_cpts = self.ip_kb.all_relevant_cpt_codes()
        invalid_codes = set()
        for code in candidates_from_text:
            norm_code = code.lstrip("+")
            if norm_code not in valid_cpts:
                invalid_codes.add(code)
        for code in invalid_codes:
            candidates_from_text.discard(code)

        # ========== RULE 2: LINEAR vs RADIAL EBUS LOGIC ==========
        # Rule ID: R002_EBUS_LINEAR_UPGRADE
        # Description: Upgrade standard TBNA (31629) to EBUS-TBNA (31652) when linear EBUS is present.
        #              Also upgrade +31633 to 31653 for additional stations.
        # Rationale: Linear EBUS-TBNA is a more specific/higher-value code than conventional TBNA.
        # Codes affected: 31629 -> 31652, +31633 -> 31653
        # Evidence required: "bronchoscopy_ebus_linear" in groups_from_text
        if "bronchoscopy_ebus_linear" in groups_from_text:
            if "31629" in candidates_from_text:
                candidates_from_text.discard("31629")
            candidates_from_text.add("31652")
            if "+31633" in candidates_from_text:
                candidates_from_text.discard("+31633")
                candidates_from_text.add("31653")

        # Rule ID: R002b_RADIAL_ONLY_EXCLUSION
        # Description: In radial-only cases, exclude linear EBUS codes.
        # Rationale: Linear EBUS (31652/31653) should not be billed for radial-only procedures.
        # Codes affected: 31652, 31653 (removed)
        # Evidence required: "bronchoscopy_ebus_radial" in groups AND "bronchoscopy_ebus_linear" NOT in groups
        if "bronchoscopy_ebus_radial" in groups_from_text and "bronchoscopy_ebus_linear" not in groups_from_text:
            discard("31652")
            discard("31653")

        # ========== RULE 3: NAVIGATION (31627) - CONSERVATIVE ==========
        # Rule ID: R003_NAVIGATION_EVIDENCE
        # Description: Navigation code requires BOTH platform evidence AND concept/direct evidence.
        # Rationale: Navigation bronchoscopy (31627) is high-value and requires strong documentation:
        #   1. Navigation system used (platform: ION, EMN, SuperDimension, etc.)
        #   2. Target identification (concept) OR tool-in-lesion confirmation (direct)
        # Codes affected: 31627 (removed if evidence insufficient)
        # Evidence required: nav_performed AND (platform AND (concept OR direct))
        nav_ev = evidence.get("bronchoscopy_navigation", {})
        nav_tool_in_lesion = bool(navigation_context.get("tool_in_lesion"))
        nav_sampling_tools = navigation_context.get("sampling_tools") or []
        nav_performed = (
            navigation_context.get("performed")
            or nav_tool_in_lesion
            or bool(nav_sampling_tools)
            or "navigation" in term_hits.get("procedure_categories", [])
            or "bronchoscopy_navigation" in groups_from_text  # Text evidence of navigation
        )
        if not nav_performed:
            discard("31627")
        elif not (nav_ev.get("platform") and (nav_ev.get("concept") or nav_ev.get("direct"))):
            discard("31627")

        # ========== RULE 4: STENT CODES - VERY CONSERVATIVE (4-GATE) ==========
        # Rule ID: R004_STENT_4GATE
        # Description: Stent codes require ALL FOUR pieces of evidence (4-gate check):
        #   1. stent_word: Literal "stent" mentioned in note
        #   2. placement_action: Action verb (placed, deployed, inserted)
        #   3. tracheal_location OR bronchial_location: Anatomic site
        #   4. NOT stent_negated: No negation phrases ("no stent", "stent not placed")
        # Rationale: Stent procedures are high-RVU; require strong positive evidence.
        # Codes affected: 31631, 31636, 31637, 31638
        # Evidence required: bronchoscopy_therapeutic_stent.(stent_word, placement_action, location, !negated)
        stent_ev = evidence.get("bronchoscopy_therapeutic_stent", {})
        has_stent_evidence = (
            stent_ev.get("stent_word") and
            stent_ev.get("placement_action") and
            (stent_ev.get("tracheal_location") or stent_ev.get("bronchial_location")) and
            not stent_ev.get("stent_negated")  # Check for negation like "no stent was placed"
        )

        if not has_stent_evidence:
            # No strong stent evidence - remove ALL stent codes
            for code in ("31631", "31636", "31638"):
                discard(code)
            discard("31637")
        else:
            # Rule ID: R004b_STENT_LOCATION_SELECT
            # Description: Select tracheal (31631) vs bronchial (31636) based on anatomic location.
            # Per CPT coding rules (from ip_golden_knowledge_v2_2.json):
            #   31631 = Tracheal stent (including carina)
            #   31636 = Bronchial stent (initial bronchus - mainstem or lobar)
            #   +31637 = Each additional major bronchus stented
            has_tracheal = stent_ev.get("tracheal_location")
            has_bronchial = stent_ev.get("bronchial_location")

            if has_tracheal and not has_bronchial:
                # Tracheal stent only - use 31631
                discard("31636")
            elif has_bronchial and not has_tracheal:
                # Bronchial stent only - use 31636
                discard("31631")
            elif has_tracheal and has_bronchial:
                # Both tracheal and bronchial - can bill both 31631 and 31636
                pass
            else:
                # Should not reach here if has_stent_evidence is True
                discard("31631")
                discard("31636")

            # Rule ID: R004c_STENT_MULTIPLE
            # Description: +31637 requires multiple separate bronchial stents
            if not stent_ev.get("multiple_stents"):
                discard("31637")

            # Rule ID: R004d_STENT_REVISION
            # Description: 31638 (revision) requires pre-existing stent + revision action
            if not (stent_ev.get("revision_action") and stent_ev.get("has_preexisting")):
                discard("31638")

        # ========== RULE 5: BAL (31624) - CONSERVATIVE ==========
        # Rule ID: R005_BAL_EVIDENCE
        # Description: Bronchoalveolar lavage requires explicit BAL documentation.
        # Rationale: BAL (31624) should not be coded from incidental mentions or pleural procedures.
        # Codes affected: 31624 (removed if evidence insufficient)
        # Evidence required: bronchoscopy_bal.bal_explicit AND NOT bronchoscopy_bal.pleural_context
        bal_ev = evidence.get("bronchoscopy_bal", {})
        if not bal_ev.get("bal_explicit"):
            discard("31624")
        # If there's pleural context, don't code as BAL
        if bal_ev.get("pleural_context"):
            discard("31624")

        # ========== RULE 6: IPC (32550/32552) - CONSERVATIVE ==========
        # Rule ID: R006_IPC_INSERTION
        # Description: Tunneled pleural catheter insertion (32550) requires IPC mention + insertion action.
        # Codes affected: 32550 (removed if evidence insufficient)
        # Evidence required: tunneled_pleural_catheter.(ipc_mentioned AND insertion_action)
        ipc_ev = evidence.get("tunneled_pleural_catheter", {})
        if not (ipc_ev.get("ipc_mentioned") and ipc_ev.get("insertion_action")):
            discard("32550")
        # Rule ID: R006b_IPC_REMOVAL
        # Description: IPC removal (32552) requires explicit removal action.
        # Never bill removal if there's no explicit removal action.
        if not ipc_ev.get("removal_action"):
            discard("32552")
        # Rule ID: R006c_IPC_MUTUAL_EXCLUSION
        # Description: Cannot bill both insertion (32550) and removal (32552) together.
        # When ambiguous (both mentioned), default to insertion.
        if ipc_ev.get("removal_action") and ipc_ev.get("insertion_action"):
            discard("32552")

        # ========== RULE 7: PLEURAL DRAINAGE (32556/32557) - REGISTRY-GATED ==========
        # Rule ID: R007_PLEURAL_REGISTRY
        # Description: Pleural drainage codes require registry evidence of pleural procedure.
        # Rationale: Prevents coding chest tube from incidental text mentions without registry data.
        # Codes affected: 32556, 32557 (removed if registry evidence missing)
        # Evidence required: ANY of:
        #   - registry.pleural_procedure_type == "Chest Tube"
        #   - registry.pleural_catheter_type present
        #   - registry.pleural_procedures.chest_tube.performed
        #   - registry.pleural_procedures.ipc.performed
        pleural_type = registry.get("pleural_procedure_type")
        pleural_catheter_type = registry.get("pleural_catheter_type")
        pleural_ok = pleural_type == "Chest Tube" or bool(pleural_catheter_type)
        pleural_ok = pleural_ok or bool(self._registry_get(registry, "pleural_procedures", "chest_tube", "performed"))
        pleural_ok = pleural_ok or bool(self._registry_get(registry, "pleural_procedures", "ipc", "performed"))
        if not pleural_ok:
            discard("32556")
            discard("32557")

        # ========== RULE 8: ADDITIONAL LOBE TBLB (+31632) - CONSERVATIVE ==========
        # Rule ID: R008_ADDITIONAL_LOBE
        # Description: Additional lobe TBLB add-on code requires biopsy in 2+ distinct lobes.
        # Rationale: +31632 is only billable when multiple lobes are sampled.
        # Codes affected: 31632, +31632 (removed if lobe_count < 2)
        # Evidence required: lobe_count >= 2 OR explicit_multilobe flag
        lobe_ev = evidence.get("bronchoscopy_biopsy_additional_lobe", {})
        normalized_lobes = self._extract_lobes_from_terms(term_hits)
        if normalized_lobes:
            lobe_ev.setdefault("normalized_terms", sorted(normalized_lobes))
            if lobe_ev.get("lobe_count", 0) < len(normalized_lobes):
                lobe_ev["lobe_count"] = len(normalized_lobes)
        if lobe_ev.get("lobe_count", 0) < 2 and not lobe_ev.get("explicit_multilobe"):
            discard("31632")

        # ========== RULE 9: PARENCHYMAL TBBx (31628) - REGISTRY-REQUIRED ==========
        # Rule ID: R009_TBBX_REGISTRY
        # Description: Transbronchial biopsy (31628) requires registry evidence of parenchymal biopsy.
        # Rationale: TBNA alone does not qualify for 31628; need actual parenchymal sampling.
        # Codes affected: 31628, +31632 (removed if no registry evidence)
        # Evidence required: ANY of:
        #   - registry.bronch_num_tbbx > 0
        #   - registry.procedures_performed.transbronchial_biopsy.number_of_samples > 0
        #   - registry.bronch_tbbx_tool present (Forceps, etc.)
        #   - registry.procedures_performed.transbronchial_cryobiopsy.cryoprobe_size_mm present
        #   - registry.bronch_biopsy_sites present
        has_parenchymal_tbbx = False
        try:
            num_tbbx = registry.get("bronch_num_tbbx")
            if num_tbbx is None:
                num_tbbx = self._registry_get(
                    registry,
                    "procedures_performed",
                    "transbronchial_biopsy",
                    "number_of_samples",
                )
            if num_tbbx is not None:
                has_parenchymal_tbbx = int(num_tbbx) > 0
        except Exception:
            has_parenchymal_tbbx = False
        tbbx_tool = registry.get("bronch_tbbx_tool") or self._registry_get(
            registry,
            "procedures_performed",
            "transbronchial_biopsy",
            "forceps_type",
        )
        if not tbbx_tool:
            tbbx_tool = self._registry_get(
                registry,
                "procedures_performed",
                "transbronchial_cryobiopsy",
                "cryoprobe_size_mm",
            )
        if tbbx_tool:
            has_parenchymal_tbbx = True
        biopsy_sites = registry.get("bronch_biopsy_sites") or self._registry_get(
            registry,
            "procedures_performed",
            "transbronchial_biopsy",
            "locations",
        )
        if biopsy_sites:
            has_parenchymal_tbbx = True

        if not has_parenchymal_tbbx:
            discard("31628")
            discard("+31632")

        # ========== RULE 10: LINEAR EBUS STATION COUNTING (31652/31653) ==========
        # Rule ID: R010_EBUS_STATION_COUNT
        # Description: Select between 31652 (1-2 stations) and 31653 (3+ stations) based on station count.
        # Rationale: CPT coding rules specify 31653 for 3 or more lymph node stations sampled.
        # Codes affected: 31652 (1-2 stations), 31653 (3+ stations)
        # Evidence required: bronchoscopy_ebus_linear.(ebus AND station_context)
        #                    Then: station_count >= 3 -> 31653, else 31652
        linear_ev = evidence.get("bronchoscopy_ebus_linear", {})
        if not (linear_ev.get("ebus") and linear_ev.get("station_context")):
            discard("31652")
            discard("31653")
        else:
            # Use station count to determine code
            station_count = linear_ev.get("station_count", 0)
            if station_count >= 3:
                # Use 31653 for 3+ stations
                discard("31652")
            else:
                # Use 31652 for 1-2 stations
                discard("31653")

        # ========== RULE 11: RADIAL EBUS (+31654) - CONSERVATIVE ==========
        # Rule ID: R011_RADIAL_EBUS
        # Description: Radial EBUS add-on (+31654) requires text OR registry confirmation.
        # Rationale: Radial EBUS is an add-on for peripheral lesion visualization.
        # Codes affected: 31654, +31654 (removed if evidence insufficient)
        # Evidence required: (group evidence AND radial flag) OR (radial flag AND registry confirmation)
        radial_ev = evidence.get("bronchoscopy_ebus_radial", {})
        radial_registry = bool(
            radial_context.get("performed")
            or radial_context.get("visualization")
            or registry.get("nav_rebus_used")
            or registry.get("nav_rebus_view")
        )
        # Allow radial EBUS if text evidence shows radial EBUS group or if registry confirms
        radial_from_text = "bronchoscopy_ebus_radial" in groups_from_text and radial_ev.get("radial")
        if not (radial_from_text or (radial_ev.get("radial") and radial_registry)):
            discard("31654")

        # ========== RULE 12: TUMOR DEBULKING (31640/31641) ==========
        # Rule ID: R012_DEBULKING
        # Description: Select between mechanical excision (31640) and ablative destruction (31641).
        #              Debulking is BUNDLED when stent is placed.
        # Rationale:
        #   - 31640 = mechanical excision (snare, forceps)
        #   - 31641 = ablative destruction (APC, laser, cryo)
        #   - Per golden knowledge: when stent is placed, debulking to facilitate stent is bundled
        # Codes affected: 31640, 31641 (removed or selected based on technique)
        # Evidence required: text_lower contains ablation_terms OR excision_terms
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

        # Rule ID: R012b_DEBULKING_STENT_BUNDLE
        # If stent is being placed, debulking is bundled - remove 31640/31641
        if has_stent_evidence:
            discard("31640")
            discard("31641")
        else:
            # Rule ID: R012c_DEBULKING_TECHNIQUE_SELECT
            # Not stent placement - check for standalone debulking
            # Prefer 31641 for ablative, 31640 for mechanical
            if "31640" in candidates_from_text and "31641" in candidates_from_text:
                # Both present - choose based on predominant technique
                if has_ablation:
                    discard("31640")  # Keep 31641
                elif has_excision:
                    discard("31641")  # Keep 31640
                else:
                    # Default to 31641 if unclear
                    discard("31640")

        # ========== RULE 13: THERAPEUTIC ASPIRATION (31645/31646) ==========
        # Rule ID: R013_ASPIRATION
        # Description: Therapeutic aspiration requires explicit aspiration documentation.
        # Rationale:
        #   - 31645 = initial therapeutic aspiration
        #   - 31646 = subsequent therapeutic aspiration (same session)
        #   - Routine suctioning does NOT qualify; must be explicit therapeutic intervention
        # Codes affected: 31645, 31646 (removed if no explicit aspiration terms)
        # Evidence required: text_lower contains aspiration_terms
        aspiration_terms = [
            "therapeutic aspiration", "aspiration of secretions", "aspirate secretions",
            "suction removal", "suctioning of blood", "aspiration of mucus",
            "mucus plug aspiration", "aspirated clot", "clot aspiration",
            "clearance of secretions", "removal of secretions"
        ]
        has_aspiration = any(t in text_lower for t in aspiration_terms)
        if not has_aspiration:
            discard("31645")
            discard("31646")

        # ========== RULE 14: THORACOSCOPY SITE PRIORITY ==========
        # Rule ID: R014_THORACOSCOPY
        # Description: Select ONE thoracoscopy code per session based on anatomic site priority.
        # Rationale: Per CPT coding rules, only ONE thoracoscopy code per hemithorax.
        #   - 32601: Diagnostic only (NO biopsy)
        #   - 32604: Pericardial with biopsy
        #   - 32606: Mediastinal with biopsy
        #   - 32609: Pleural with biopsy
        #   - 32602/32607/32608: Lung parenchyma
        # Codes affected: 32601, 32602, 32604, 32606, 32607, 32608, 32609
        # Rules:
        #   1. Only ONE thoracoscopy code per session
        #   2. Biopsy codes trump diagnostic-only (32601)
        #   3. Priority: pleural (32609) > pericardial (32604) > mediastinal (32606) > lung (32607) > diagnostic (32601)
        #   4. Temporary drains are bundled into thoracoscopy

        thoracoscopy_ev = evidence.get("thoracoscopy", {})
        thoracoscopy_codes_present = candidates_from_text & {
            "32601", "32602", "32604", "32606", "32607", "32608", "32609"
        }

        if thoracoscopy_codes_present:
            has_biopsy_code = bool(thoracoscopy_codes_present & {"32604", "32606", "32609", "32602", "32607", "32608"})

            # Rule ID: R014b_BIOPSY_TRUMPS_DIAGNOSTIC
            # If any biopsy code present, remove diagnostic-only (32601)
            if has_biopsy_code and "32601" in candidates_from_text:
                discard("32601")

            # Rule ID: R014c_SITE_PRIORITY_SELECT
            # Select ONE thoracoscopy code based on anatomic site priority
            remaining_thoracoscopy = candidates_from_text & {
                "32601", "32604", "32606", "32609", "32607"
            }

            if len(remaining_thoracoscopy) > 1:
                # Multiple thoracoscopy codes - select based on documented site
                pleural_site = thoracoscopy_ev.get("pleural_site", False)
                pericardial_site = thoracoscopy_ev.get("pericardial_site", False)
                mediastinal_site = thoracoscopy_ev.get("mediastinal_site", False)
                lung_site = thoracoscopy_ev.get("lung_site", False)

                # Keep only the code matching the documented site
                codes_to_keep = set()
                if pleural_site and "32609" in remaining_thoracoscopy:
                    codes_to_keep.add("32609")
                if pericardial_site and "32604" in remaining_thoracoscopy:
                    codes_to_keep.add("32604")
                if mediastinal_site and "32606" in remaining_thoracoscopy:
                    codes_to_keep.add("32606")
                if lung_site and "32607" in remaining_thoracoscopy:
                    codes_to_keep.add("32607")

                # If no specific site matched but biopsy performed, keep one
                if not codes_to_keep and thoracoscopy_ev.get("has_biopsy", False):
                    # Default priority: 32609 > 32604 > 32606 > 32607
                    for preferred in ["32609", "32604", "32606", "32607"]:
                        if preferred in remaining_thoracoscopy:
                            codes_to_keep.add(preferred)
                            break

                # If still no code selected and diagnostic present
                if not codes_to_keep and "32601" in remaining_thoracoscopy:
                    codes_to_keep.add("32601")

                # Remove all thoracoscopy codes not in codes_to_keep
                for code in remaining_thoracoscopy - codes_to_keep:
                    discard(code)

            # Rule ID: R014d_TEMP_DRAIN_BUNDLE
            # Temporary drains during thoracoscopy are bundled
            if thoracoscopy_ev.get("temporary_drain_bundled", False):
                # Remove pleural drainage codes that are temporary
                for drain_code in ["32556", "32557"]:
                    discard(drain_code)

        codes: list[CodeSuggestion] = []
        for cpt in sorted(candidates_from_text):
            codes.append(CodeSuggestion(cpt))

        # Store the EvidenceContext for potential shadow mode / debugging
        # This allows the rules engine to be invoked externally if needed
        self._last_evidence_context = EvidenceContext.from_procedure_data(
            groups_from_text=groups_from_text,
            evidence=evidence,
            registry=registry,
            candidates_from_text={c.cpt for c in codes},
            term_hits=term_hits,
            navigation_context=navigation_context,
            radial_context=radial_context,
            note_text=note_text,
        )

        return codes

    def code_procedure(self, procedure_data: dict) -> Dict[str, Any]:
        """
        Code a procedure, apply bundling, and calculate RVUs.
        """
        note_text = procedure_data.get("note_text") or procedure_data.get("findings", "") or ""
        term_hits = self._extract_term_hits(note_text)

        # 1) Generate candidate codes
        codes: list[CodeSuggestion] = self._generate_codes(procedure_data, term_hits=term_hits)
        initial_cpts = [c.cpt for c in codes]

        # 2) Apply bundling rules from ip_coding_billing (with explanations)
        bundled_cpt_list, bundling_decisions = self.ip_kb.apply_bundling(initial_cpts, return_decisions=True)
        bundled_set = set(bundled_cpt_list)

        codes = [c for c in codes if c.cpt in bundled_set]

        # 3) Attach group/category metadata, description, and fetch base RVU for sorting
        code_data_map = {}
        locality = procedure_data.get("locality", "00")
        setting = procedure_data.get("setting", "facility")
        evidence = getattr(self.ip_kb, "last_group_evidence", {}) or {}

        for c in codes:
            c.groups = self.ip_kb.get_groups_for_code(c.cpt)

            # Normalize for lookup
            norm_cpt = c.cpt.lstrip("+")
            is_addon = self.ip_kb.is_add_on(c.cpt)

            # Get base RVU/Payment for sorting
            base_rvu = self.rvu_calc.calculate_procedure_rvu(
                cpt_code=norm_cpt,
                locality=locality,
                setting=setting
            )

            # Get CPT info including description - try KB first, then RVU data
            cpt_info = self.ip_kb.get_cpt_info(c.cpt)
            if cpt_info and cpt_info.description:
                c.description = cpt_info.description
            elif base_rvu and base_rvu.get("description") and base_rvu["description"] != "Generated Description":
                c.description = base_rvu["description"]
            else:
                c.description = f"CPT {norm_cpt}"

            payment_val = float(base_rvu.get("payment_amount", 0.0)) if base_rvu else 0.0

            code_data_map[c.cpt] = {
                "norm_cpt": norm_cpt,
                "is_addon": is_addon,
                "payment_val": payment_val
            }

        # 4) Sort and Assign Multipliers (Multiple Endoscopy Rule / MPPR Logic)
        # Standard Rule: Primary (Highest Value) @ 100%, Others @ 50%. Add-ons @ 100% (exempt).

        main_codes = [c for c in codes if not code_data_map[c.cpt]["is_addon"]]
        addon_codes = [c for c in codes if code_data_map[c.cpt]["is_addon"]]

        # Sort main codes by payment value descending
        main_codes.sort(key=lambda c: code_data_map[c.cpt]["payment_val"], reverse=True)

        procedures = []
        ordered_codes = [] # Track order for final result

        # Process Main Codes with MER explanations
        primary_code = main_codes[0] if main_codes else None
        for i, code in enumerate(main_codes):
            multiplier = 1.0 if i == 0 else 0.5

            # Assign MER role and explanation
            if i == 0:
                code.mer_role = "primary"
                code.mer_explanation = "Primary procedure - paid at 100% of the fee schedule"
            else:
                code.mer_role = "secondary"
                code.mer_explanation = (
                    f"Multiple Endoscopy Rule: Secondary procedure paid at 50% because "
                    f"{primary_code.cpt} ({primary_code.description}) is the higher-value primary procedure"
                )

            procedures.append({
                "cpt_code": code_data_map[code.cpt]["norm_cpt"],
                "modifiers": code.modifiers,
                "multiplier": multiplier
            })
            ordered_codes.append(code)

        # Process Add-on Codes (Exempt from reduction)
        for code in addon_codes:
            code.mer_role = "add_on"
            code.mer_explanation = "Add-on code - exempt from Multiple Endoscopy Rule reduction, paid at 100%"

            procedures.append({
                "cpt_code": code_data_map[code.cpt]["norm_cpt"],
                "modifiers": code.modifiers,
                "multiplier": 1.0
            })
            ordered_codes.append(code)

        nav_evidence = evidence.get("bronchoscopy_navigation", {})
        radial_evidence = evidence.get("bronchoscopy_ebus_radial", {})
        documentation_context = self._build_documentation_context(
            procedure_data,
            term_hits,
            nav_evidence,
            radial_evidence,
        )
        qa_flags_map = self._evaluate_qa_flags(ordered_codes, documentation_context)

        rvu_results = self.rvu_calc.calculate_case_rvu(
            procedures=procedures,
            locality=locality,
            setting=setting,
        )

        # 5) Attach RVU info per code (Mapping back results to ordered codes)
        # The rvu_results['breakdown'] list preserves the order of 'procedures' input
        for code, proc_rvu in zip(ordered_codes, rvu_results["breakdown"]):
            # Ensure display uses the original CPT (with + if applicable)
            proc_rvu['cpt_code'] = code.cpt
            code.rvu_data = proc_rvu
            
        # 6) Return a rich summary
        code_summaries = []
        # Return in the calculated order (Main -> Add-ons)
        for c in ordered_codes:
            rationale_parts = []
            if c.groups:
                rationale_parts.append(f"Detected via knowledge base groups: {', '.join(c.groups)}")
            else:
                rationale_parts.append("Detected via IP knowledge base patterns")
            if c.mer_explanation:
                rationale_parts.append(c.mer_explanation)
            if code_data_map.get(c.cpt, {}).get("is_addon"):
                rationale_parts.append("Add-on code exempt from Multiple Endoscopy Rule reductions")

            qa_entries = qa_flags_map.get(c.cpt, [])
            if qa_entries:
                missing_labels = []
                for entry in qa_entries:
                    missing = ", ".join(entry.get("missing", []))
                    label = entry.get("rule", "qa_rule")
                    if missing:
                        missing_labels.append(f"{label}: {missing}")
                    else:
                        missing_labels.append(f"{label}: {entry.get('description', 'documentation incomplete')}")
                rationale_parts.append(f"QA review pending - {', '.join(missing_labels)}")

            summary = {
                "cpt": c.cpt,
                "description": c.description,
                "modifiers": c.modifiers,
                "groups": c.groups,
                "rvu_data": c.rvu_data,
                "mer_role": c.mer_role,
                "mer_explanation": c.mer_explanation,
                "rationale": rationale_parts,
                "qa_flags": qa_entries,
            }
            code_summaries.append(summary)

        qa_warnings = []
        for summary in code_summaries:
            for qa_entry in summary.get("qa_flags") or []:
                missing = ", ".join(qa_entry.get("missing", [])) or qa_entry.get("description", "documentation incomplete")
                qa_warnings.append(f"{summary['cpt']}: {qa_entry.get('rule', 'qa_rule')} - {missing}")

        # 7) Optional: Get LLM suggestions if enabled
        llm_suggestions = []
        llm_disagreements = []
        if self.llm_coder:
            try:
                note_text = procedure_data.get("note_text") or procedure_data.get("findings", "") or ""
                llm_suggestions_raw = self.llm_coder.suggest_codes(note_text)
                # Convert LLMCodeSuggestion to dict format
                llm_suggestions = [
                    {
                        "cpt": s.cpt,
                        "description": s.description,
                        "rationale": s.rationale,
                    }
                    for s in llm_suggestions_raw
                ]
                
                # Compare LLM suggestions with detected codes
                if not llm_suggestions:
                    llm_disagreements.append("LLM produced no valid CPT suggestions; skipping comparison.")
                else:
                    detected_cpts = {c["cpt"] for c in code_summaries}
                    llm_cpts = {s["cpt"] for s in llm_suggestions}
                    
                    missing_in_det = llm_cpts - detected_cpts
                    extra_in_det = detected_cpts - llm_cpts
                    
                    if missing_in_det:
                        llm_disagreements.append(
                            f"LLM suggests additional CPT(s) not detected by knowledge base: {', '.join(sorted(missing_in_det))}"
                        )
                    if extra_in_det:
                        llm_disagreements.append(
                            f"Knowledge base detected CPT(s) not suggested by LLM: {', '.join(sorted(extra_in_det))}"
                        )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"LLM advisor failed: {e}. Continuing without LLM suggestions.")

        case_summary = {
            "codes": code_summaries,
            "total_work_rvu": rvu_results["total_work_rvu"],
            "estimated_payment": rvu_results["total_payment"],
            "locality": locality,
            "setting": setting,
            "bundled_codes": bundling_decisions,  # Codes not billed due to bundling rules
             "qa_warnings": qa_warnings,
             "qa_flags": qa_flags_map,
             "conversion_factor": rvu_results.get("conversion_factor"),
            "llm_suggestions": llm_suggestions,
            "llm_disagreements": llm_disagreements,
        }

        # Optional strict JSON output for LLM assistant mode
        output_mode = procedure_data.get("output_mode") or procedure_data.get("mode")
        if output_mode == "llm_assistant":
            bundled_norm = {c.lstrip("+") for c in bundled_cpt_list}
            excluded_or_bundled = []
            for cpt in initial_cpts:
                norm = cpt.lstrip("+")
                if norm not in bundled_norm:
                    info = self.ip_kb.get_cpt_info(cpt)
                    excluded_or_bundled.append(
                        {
                            "cpt": norm,
                            "description": info.description if info else f"CPT {norm}",
                            "reason": "Bundled via knowledge base rules",
                        }
                    )

            billed_codes_payload = []
            for c in ordered_codes:
                info = self.ip_kb.get_cpt_info(c.cpt)
                billed_codes_payload.append(
                    {
                        "cpt": c.cpt.lstrip("+"),
                        "description": info.description if info else f"CPT {c.cpt}",
                        "rationale": f"Detected via groups: {', '.join(c.groups)}" if c.groups else "Detected via knowledge base",
                    }
                )

            case_summary["llm_assistant_payload"] = {
                "billed_codes": billed_codes_payload,
                "excluded_or_bundled_codes": excluded_or_bundled,
                "comments": "Knowledge-base driven CPT selection; modifiers not inferred in this mode.",
            }

        return case_summary

    def _resolve_kb_path(self, repo_root: Path) -> Path:
        candidates = [
            os.getenv("PSUITE_KNOWLEDGE_FILE"),
            repo_root / "data" / "knowledge" / "ip_coding_billing.v2_7.json",
            repo_root / "proc_autocode" / "ip_kb" / "ip_coding_billing.v2_7.json",
            repo_root / "data" / "knowledge" / "ip_coding_billing.v2_2.json",
            repo_root / "proc_autocode" / "ip_kb" / "ip_coding_billing.v2_2.json",
        ]
        for candidate in candidates:
            if not candidate:
                continue
            path = Path(candidate)
            if not path.is_absolute():
                path = (repo_root / path).resolve()
            if path.exists():
                return path
        raise FileNotFoundError("Cannot locate IP knowledge base; set PSUITE_KNOWLEDGE_FILE")

    def _extract_term_hits(self, text: str) -> Dict[str, List[str]]:
        if not text or not text.strip():
            return {}
        return self.terminology.extract_terms(
            text,
            categories=["procedure_categories", "anatomic_terms", "modifiers"],
        )

    def _registry_get(self, payload: Any, *path: str) -> Any:
        current = payload
        for key in path:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
        return current

    def _extract_navigation_registry(self, registry: dict) -> Dict[str, Any]:
        nav_section = self._registry_get(registry, "procedures_performed", "navigational_bronchoscopy") or {}
        sampling = nav_section.get("sampling_tools_used") or registry.get("nav_sampling_tools") or []
        if isinstance(sampling, str):
            sampling = [item.strip() for item in sampling.split(",") if item.strip()]
        platform = registry.get("nav_platform") or self._registry_get(registry, "equipment", "navigation_platform")
        performed = bool(
            nav_section.get("performed")
            or nav_section.get("tool_in_lesion_confirmed")
            or registry.get("nav_tool_in_lesion")
            or sampling
        )
        return {
            "performed": performed,
            "tool_in_lesion": bool(
                nav_section.get("tool_in_lesion_confirmed")
                or registry.get("nav_tool_in_lesion")
            ),
            "target_reached": bool(
                nav_section.get("target_reached")
                or registry.get("nav_tool_in_lesion")
            ),
            "sampling_tools": sampling,
            "platform": platform,
        }

    def _extract_radial_registry(self, registry: dict) -> Dict[str, Any]:
        radial_section = self._registry_get(registry, "procedures_performed", "radial_ebus") or {}
        return {
            "performed": bool(radial_section.get("performed") or registry.get("nav_rebus_used")),
            "visualization": radial_section.get("probe_position") or registry.get("nav_rebus_view"),
            "sampling": bool(
                self._registry_get(registry, "procedures_performed", "transbronchial_biopsy", "number_of_samples")
                or registry.get("bronch_num_tbbx")
            ),
        }

    def _extract_lobes_from_terms(self, term_hits: Dict[str, List[str]]) -> Set[str]:
        terms = term_hits.get("anatomic_terms") or []
        return {term for term in terms if term.lower() in self._lobe_terms}

    def _build_documentation_context(
        self,
        procedure_data: dict,
        term_hits: Dict[str, List[str]],
        nav_evidence: Dict[str, Any],
        radial_evidence: Dict[str, Any],
    ) -> Dict[str, Any]:
        registry = procedure_data.get("registry") or procedure_data
        navigation_context = self._extract_navigation_registry(registry)
        radial_context = self._extract_radial_registry(registry)

        return {
            "navigation_system_used": bool(
                navigation_context.get("platform")
                or nav_evidence.get("platform")
                or "navigation" in term_hits.get("procedure_categories", [])
            ),
            "catheter_advanced_under_navigation_guidance": bool(navigation_context.get("tool_in_lesion")),
            "target_lesion_identified": bool(
                navigation_context.get("target_reached")
                or nav_evidence.get("concept")
                or nav_evidence.get("direct")
            ),
            "peripheral_lesion_targeted": bool(
                radial_context.get("performed")
                or navigation_context.get("target_reached")
            ),
            "radial_probe_visualization_documented": bool(
                radial_context.get("visualization") or radial_evidence.get("radial")
            ),
            "sampling_performed": bool(
                navigation_context.get("sampling_tools")
                or radial_context.get("sampling")
            ),
        }

    def _evaluate_qa_flags(
        self,
        codes: List[CodeSuggestion],
        documentation: Dict[str, Any],
    ) -> Dict[str, List[Dict[str, Any]]]:
        qa_results: Dict[str, List[Dict[str, Any]]] = {}
        for code in codes:
            checks = self.qa_checker.evaluate_code(code.cpt, documentation)
            if checks:
                qa_results[code.cpt] = checks
        return qa_results
