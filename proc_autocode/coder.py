from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict, Any

from proc_autocode.ip_kb.ip_kb import IPCodingKnowledgeBase
from proc_autocode.rvu.rvu_calculator import ProcedureRVUCalculator

class CodeSuggestion:
    def __init__(self, cpt: str, modifiers: Optional[list[str]] = None):
        self.cpt = cpt
        self.modifiers = modifiers or []
        self.rvu_data = None
        self.groups = []

class EnhancedCPTCoder:
    def __init__(self, config: Optional[Dict] = None):
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

    def _generate_codes(self, procedure_data: dict) -> list[CodeSuggestion]:
        """
        Generate candidate codes. 
        For this implementation, we use the Knowledge Base's synonym matcher
        to find codes from the note text.
        """
        note_text = procedure_data.get("note_text") or procedure_data.get("findings", "") or ""
        
        # Use IP KB to find codes from text
        candidates_from_text = self.ip_kb.codes_from_text(note_text)
        
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

        # 3) Attach group/category metadata
        for c in codes:
            c.groups = self.ip_kb.get_groups_for_code(c.cpt)

        # 4) Calculate RVUs and payments for the case
        locality = procedure_data.get("locality", "00")
        setting = procedure_data.get("setting", "facility")

        procedures = []
        for i, code in enumerate(codes):
            procedures.append(
                {
                    "cpt_code": code.cpt,
                    "modifiers": code.modifiers,
                    "multiplier": 1.0 if i == 0 else 0.5,  # multiple procedure rule
                }
            )

        rvu_results = self.rvu_calc.calculate_case_rvu(
            procedures=procedures,
            locality=locality,
            setting=setting,
        )

        # 5) Attach RVU info per code
        for code, proc_rvu in zip(codes, rvu_results["breakdown"]):
            code.rvu_data = proc_rvu

        # 6) Return a rich summary
        # Convert CodeSuggestion objects to dicts for return
        code_summaries = []
        for c in codes:
            summary = {
                "cpt": c.cpt,
                "modifiers": c.modifiers,
                "groups": c.groups,
                "rvu_data": c.rvu_data
            }
            code_summaries.append(summary)

        case_summary = {
            "codes": code_summaries,
            "total_work_rvu": rvu_results["total_work_rvu"],
            "estimated_payment": rvu_results["total_payment"],
            "locality": locality,
            "setting": setting,
        }

        return case_summary
