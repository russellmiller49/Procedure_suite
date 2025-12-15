from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Sequence
import os

from modules.autocode.ip_kb.ip_kb import IPCodingKnowledgeBase
from modules.autocode.ip_kb.terminology_utils import TerminologyNormalizer, QARuleChecker
from modules.autocode.rvu.rvu_calculator import ProcedureRVUCalculator
from modules.coder.rules_engine import CodingRulesEngine as PipelineRulesEngine
from modules.coder.types import CodeCandidate, EBUSNodeEvidence, PeripheralLesionEvidence
from modules.coder.ebus_rules import ebus_nodes_to_candidates
from modules.coder.ebus_extractor import EBUSEvidenceExtractor
from modules.coder.peripheral_rules import peripheral_lesions_to_candidates
from modules.coder.peripheral_extractor import PeripheralLesionExtractor
from modules.coder.ncci import NCCI_BUNDLED_REASON_PREFIX
from modules.domain.coding_rules import (
    CodingRulesEngine as DomainCodingRulesEngine,
    EvidenceContext,
)

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
    def __init__(
        self,
        config: Optional[Dict] = None,
        use_llm_advisor: Optional[bool] = None,
        rules_engine: PipelineRulesEngine | None = None,
        ebus_extractor: EBUSEvidenceExtractor | None = None,
        peripheral_extractor: PeripheralLesionExtractor | None = None,
    ):
        self.config = config or {}
        
        base_dir = Path(__file__).parent
        # repo_root is 2 levels up: modules/autocode -> modules -> repo_root
        repo_root = base_dir.parent.parent

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

        # Initialize CodingRulesEngines:
        # - _domain_rules_engine handles legacy evidence-to-code logic
        # - _rules_engine is the new pass-through layer for future deterministic rules
        self._domain_rules_engine = DomainCodingRulesEngine()
        self._rules_engine = rules_engine or PipelineRulesEngine()
        self._last_evidence_context: Optional[EvidenceContext] = None
        self._ebus_tuple_mode = os.getenv("CODING_EBUS_TUPLE_MODE", "").lower() in ("true", "1", "yes")
        self._ebus_extractor = ebus_extractor if self._ebus_tuple_mode else None
        self._peripheral_tuple_mode = os.getenv("CODING_PERIPHERAL_TUPLE_MODE", "").lower() in ("true", "1", "yes")
        self._peripheral_extractor = peripheral_extractor if self._peripheral_tuple_mode else None

    def _collect_initial_candidates(
        self,
        note_text: str,
        registry: Dict[str, Any],
        term_hits: Dict[str, List[str]],
    ) -> list[CodeCandidate]:
        """Collect initial candidates using the IP KB and legacy rule engine."""
        navigation_context = self._extract_navigation_registry(registry)
        radial_context = self._extract_radial_registry(registry)

        groups_from_text = self.ip_kb.groups_from_text(note_text)
        evidence = getattr(self.ip_kb, "last_group_evidence", {}) or {}
        candidates_from_text = self.ip_kb.codes_for_groups(groups_from_text)

        _initial_candidates = set(candidates_from_text)

        lobe_ev = evidence.get("bronchoscopy_biopsy_additional_lobe", {})
        normalized_lobes = self._extract_lobes_from_terms(term_hits)
        if normalized_lobes:
            lobe_ev.setdefault("normalized_terms", sorted(normalized_lobes))
            if lobe_ev.get("lobe_count", 0) < len(normalized_lobes):
                lobe_ev["lobe_count"] = len(normalized_lobes)
            evidence["bronchoscopy_biopsy_additional_lobe"] = lobe_ev

        context = EvidenceContext.from_procedure_data(
            groups_from_text=groups_from_text,
            evidence=evidence,
            registry=registry,
            candidates_from_text=_initial_candidates,
            term_hits=term_hits,
            navigation_context=navigation_context,
            radial_context=radial_context,
            note_text=note_text,
        )

        valid_cpts = self.ip_kb.all_relevant_cpt_codes()
        rules_result = self._domain_rules_engine.apply_rules(context, valid_cpts)
        self._last_evidence_context = context

        return [CodeCandidate(code=cpt) for cpt in sorted(rules_result.codes)]

    def _apply_rules(
        self,
        candidates: list[CodeCandidate],
        note_text: str,
    ) -> list[CodeCandidate]:
        """Apply deterministic rules (currently a no-op placeholder)."""
        return self._rules_engine.apply(candidates, note_text)

    def _collect_ebus_candidates(self, note_text: str) -> list[CodeCandidate]:
        """Use LLM-extracted EBUS evidence to produce additional candidates."""
        if not self._ebus_tuple_mode:
            return []
        if self._ebus_extractor is None:
            self._ebus_extractor = EBUSEvidenceExtractor()
        evidence: list[EBUSNodeEvidence] = self._ebus_extractor.extract(note_text) or []
        return ebus_nodes_to_candidates(evidence)

    def _collect_peripheral_candidates(self, note_text: str) -> list[CodeCandidate]:
        """Use LLM-extracted peripheral lesion evidence for add-on codes."""
        if not self._peripheral_tuple_mode:
            return []
        if self._peripheral_extractor is None:
            self._peripheral_extractor = PeripheralLesionExtractor()
        evidence: list[PeripheralLesionEvidence] = self._peripheral_extractor.extract(note_text) or []
        return peripheral_lesions_to_candidates(evidence)

    def _select_final_codes(self, candidates: list[CodeCandidate]) -> list[CodeSuggestion]:
        """Convert candidates to CodeSuggestion objects with stable ordering."""
        filtered_codes = {
            candidate.code
            for candidate in candidates
            if NCCI_BUNDLED_REASON_PREFIX not in (candidate.reason or "")
        }
        ordered_codes = sorted(filtered_codes)
        return [CodeSuggestion(code) for code in ordered_codes]

    def _apply_domain_rules_final(
        self,
        candidates: list[CodeCandidate],
        note_text: str,
        registry: Dict[str, Any],
        term_hits: Dict[str, List[str]],
    ) -> list[CodeCandidate]:
        """Apply domain rules (R015-R018) to the final candidate pool.

        This runs AFTER all candidates are collected (initial + EBUS + peripheral)
        to ensure rules like EBUS mutual exclusion work correctly.
        """
        navigation_context = self._extract_navigation_registry(registry)
        radial_context = self._extract_radial_registry(registry)

        groups_from_text = self.ip_kb.groups_from_text(note_text)
        evidence = getattr(self.ip_kb, "last_group_evidence", {}) or {}

        # Build context with ALL candidates
        all_candidate_codes = {c.code for c in candidates}

        context = EvidenceContext.from_procedure_data(
            groups_from_text=groups_from_text,
            evidence=evidence,
            registry=registry,
            candidates_from_text=all_candidate_codes,
            term_hits=term_hits,
            navigation_context=navigation_context,
            radial_context=radial_context,
            note_text=note_text,
        )

        valid_cpts = self.ip_kb.all_relevant_cpt_codes()
        rules_result = self._domain_rules_engine.apply_rules(context, valid_cpts)

        # Filter candidates based on domain rules result
        allowed_codes = rules_result.codes
        return [c for c in candidates if c.code in allowed_codes]

    def _generate_codes(
        self,
        procedure_data: dict,
        term_hits: Optional[Dict[str, List[str]]] = None,
        extra_candidates: Sequence[CodeCandidate] | None = None,
    ) -> list[CodeSuggestion]:
        """
        Generate candidate codes with CONSERVATIVE evidence-based filtering.

        CODING PRINCIPLES:
        1. High-value codes require STRONG positive evidence in the procedure note body
        2. Indications, history, and boilerplate text do NOT count as procedure evidence
        3. When ambiguous, prefer NOT billing (precision over recall for high-RVU codes)
        4. Only emit codes present in the IP golden knowledge base
        """
        note_text = procedure_data.get("note_text") or procedure_data.get("findings", "") or ""
        registry = procedure_data.get("registry") or procedure_data
        term_hits = term_hits or self._extract_term_hits(note_text)

        candidate_pool = self._collect_initial_candidates(
            note_text=note_text,
            registry=registry,
            term_hits=term_hits,
        )
        if extra_candidates:
            candidate_pool.extend(list(extra_candidates))
        ebus_candidates = self._collect_ebus_candidates(note_text)
        if ebus_candidates:
            candidate_pool.extend(ebus_candidates)
        peripheral_candidates = self._collect_peripheral_candidates(note_text)
        if peripheral_candidates:
            candidate_pool.extend(peripheral_candidates)

        # Apply domain rules (R015-R018) on the COMBINED candidate pool
        # This ensures EBUS mutual exclusion and other rules work correctly
        candidate_pool = self._apply_domain_rules_final(
            candidate_pool, note_text, registry, term_hits
        )

        ruled_candidates = self._apply_rules(candidate_pool, note_text)
        return self._select_final_codes(ruled_candidates)

    def code_procedure(self, procedure_data: dict) -> Dict[str, Any]:
        """
        Code a procedure, apply bundling, and calculate RVUs.
        """
        note_text = procedure_data.get("note_text") or procedure_data.get("findings", "") or ""
        term_hits = self._extract_term_hits(note_text)

        # 1) Generate candidate codes
        codes: list[CodeSuggestion] = self._generate_codes(procedure_data)
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
            repo_root / "data" / "knowledge" / "ip_coding_billing_v2_8.json",
            repo_root / "proc_autocode" / "ip_kb" / "ip_coding_billing_v2_8.json",
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
