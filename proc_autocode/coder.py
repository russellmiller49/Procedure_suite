from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict, Any
import os

from proc_autocode.ip_kb.ip_kb import IPCodingKnowledgeBase
from proc_autocode.rvu.rvu_calculator import ProcedureRVUCalculator

class CodeSuggestion:
    def __init__(self, cpt: str, modifiers: Optional[list[str]] = None):
        self.cpt = cpt
        self.modifiers = modifiers or []
        self.rvu_data = None
        self.groups = []

class EnhancedCPTCoder:
    def __init__(self, config: Optional[Dict] = None, use_llm_advisor: Optional[bool] = None):
        self.config = config or {}
        
        base_dir = Path(__file__).parent

        # RVU calculator
        rvu_dir = base_dir / "rvu" / "data"
        self.rvu_calc = ProcedureRVUCalculator(
            rvu_file=rvu_dir / "rvu_ip_2025.csv",
            gpci_file=rvu_dir / "gpci_2025.csv",
        )

        # IP coding knowledge base
        kb_path = base_dir / "ip_kb" / "ip_coding_billing.v2_2.json"
        self.ip_kb = IPCodingKnowledgeBase(kb_path)
        
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

    def _generate_codes(self, procedure_data: dict) -> list[CodeSuggestion]:
        """
        Generate candidate codes. 
        For this implementation, we use the Knowledge Base's synonym matcher
        to find codes from the note text.
        """
        note_text = procedure_data.get("note_text") or procedure_data.get("findings", "") or ""
        
        # Use IP KB to find codes from text
        candidates_from_text = self.ip_kb.codes_from_text(note_text)
        
        # Post-processing for EBUS-TBNA detection gap
        # If we found TBNA (31629) but not EBUS-TBNA (31652/53), and text implies EBUS-TBNA
        if "31629" in candidates_from_text and not any(c in candidates_from_text for c in ["31652", "31653"]):
            lower_text = note_text.lower()
            has_ebus = "ebus" in lower_text or "endobronchial ultrasound" in lower_text
            has_tbna = "tbna" in lower_text or "needle aspiration" in lower_text
            
            if has_ebus and has_tbna:
                candidates_from_text.remove("31629")
                candidates_from_text.add("31652")

        # Post-processing: Suppress standard TBNA if EBUS-TBNA is present
        # (Avoids double coding 31629 when 31652/53 is already capturing the aspiration)
        if any(c in candidates_from_text for c in ["31652", "31653"]):
            if "31629" in candidates_from_text:
                candidates_from_text.remove("31629")
            if "+31633" in candidates_from_text:
                candidates_from_text.remove("+31633")

        codes: list[CodeSuggestion] = []
        for cpt in sorted(candidates_from_text):
            codes.append(CodeSuggestion(cpt))
            
        return codes

    def code_procedure(self, procedure_data: dict) -> Dict[str, Any]:
        """
        Code a procedure, apply bundling, and calculate RVUs.
        """
        # 1) Generate candidate codes
        codes: list[CodeSuggestion] = self._generate_codes(procedure_data)

        # 2) Apply bundling rules from ip_coding_billing
        bundled_cpt_list = self.ip_kb.apply_bundling([c.cpt for c in codes])
        bundled_set = set(bundled_cpt_list)

        codes = [c for c in codes if c.cpt in bundled_set]

        # 3) Attach group/category metadata and fetch base RVU for sorting
        code_data_map = {}
        locality = procedure_data.get("locality", "00")
        setting = procedure_data.get("setting", "facility")

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
            
            payment_val = float(base_rvu.get("payment_amount", 0.0)) if base_rvu else 0.0
            
            code_data_map[c.cpt] = {
                "norm_cpt": norm_cpt,
                "is_addon": is_addon,
                "payment_val": payment_val
            }

        # 4) Sort and Assign Multipliers (MPPR Logic)
        # Standard Rule: Primary (Highest Value) @ 100%, Others @ 50%. Add-ons @ 100% (exempt).
        
        main_codes = [c for c in codes if not code_data_map[c.cpt]["is_addon"]]
        addon_codes = [c for c in codes if code_data_map[c.cpt]["is_addon"]]
        
        # Sort main codes by payment value descending
        main_codes.sort(key=lambda c: code_data_map[c.cpt]["payment_val"], reverse=True)
        
        procedures = []
        ordered_codes = [] # Track order for final result
        
        # Process Main Codes
        for i, code in enumerate(main_codes):
            multiplier = 1.0 if i == 0 else 0.5
            procedures.append({
                "cpt_code": code_data_map[code.cpt]["norm_cpt"],
                "modifiers": code.modifiers,
                "multiplier": multiplier
            })
            ordered_codes.append(code)
            
        # Process Add-on Codes (Exempt from reduction)
        for code in addon_codes:
            procedures.append({
                "cpt_code": code_data_map[code.cpt]["norm_cpt"],
                "modifiers": code.modifiers,
                "multiplier": 1.0 
            })
            ordered_codes.append(code)

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
            summary = {
                "cpt": c.cpt,
                "modifiers": c.modifiers,
                "groups": c.groups,
                "rvu_data": c.rvu_data
            }
            code_summaries.append(summary)

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
            "llm_suggestions": llm_suggestions,
            "llm_disagreements": llm_disagreements,
        }

        return case_summary
