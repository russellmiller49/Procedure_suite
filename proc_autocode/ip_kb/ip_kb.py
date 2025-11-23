from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Iterable
import json


@dataclass
class CPTInfo:
    code: str
    description: Optional[str]
    groups: List[str]
    is_add_on: bool
    rvus: Optional[dict]
    fee_schedule: Optional[dict]


class IPCodingKnowledgeBase:
    """
    Thin wrapper around ip_coding_billing.v2_2.json

    Responsibilities:
    - Expose "all relevant CPT/HCPCS codes"
    - Map codes <-> groups (bronchoscopy_tbna, thoracentesis, etc.)
    - Surface RVU approximations and vendor fee schedules where present
    - Provide helper to apply key bundling rules
    """

    def __init__(self, json_path: Path):
        self.json_path = json_path
        with open(json_path, "r") as f:
            self.raw = json.load(f)

        self.code_to_groups: Dict[str, Set[str]] = {}
        self.add_on_codes: Set[str] = set()
        self.cpt_rvus: Dict[str, dict] = self.raw.get("rvus", {})
        self._build_indexes()

    def _normalize_code(self, code: str) -> str:
        return code.lstrip("+").strip()

    def _build_indexes(self) -> None:
        # 1) Code lists
        for group, codes in self.raw.get("code_lists", {}).items():
            for code in codes:
                c = self._normalize_code(code)
                self.code_to_groups.setdefault(c, set()).add(group)

        # 2) Add-on codes
        for code in self.raw.get("add_on_codes", []):
            self.add_on_codes.add(self._normalize_code(code))

        # 3) Pleural / thoracoscopy maps
        pleural = self.raw.get("pleural", {})
        for submap_key in ("cpt_map", "thoracoscopy_cpt_map"):
            for code in pleural.get(submap_key, {}):
                c = self._normalize_code(code)
                self.code_to_groups.setdefault(c, set()).add(submap_key)

        # 4) Explicit lists in pleural section
        pleural_lists = [
            "thoracentesis_codes",
            "pleural_drainage_codes",
            "chest_tube_insertion_codes",
            "chest_tube_removal_codes",
            "ipc_codes",
            "thoracoscopy_diagnostic_codes",
            "thoracoscopy_surgical_codes",
            "ttna_codes",
        ]
        for list_name in pleural_lists:
            for code in pleural.get(list_name, []):
                c = self._normalize_code(code)
                self.code_to_groups.setdefault(c, set()).add(list_name)

        # 5) HCPCS devices that declare primary CPTs (e.g. C1601)
        for _hcpcs, info in self.raw.get("hcpcs", {}).items():
            for group_name, codes in info.get("primary_cpt_eligible", {}).items():
                for code in codes:
                    c = self._normalize_code(code)
                    self.code_to_groups.setdefault(c, set()).add(group_name)

    # ---------- Public API ----------

    def all_relevant_cpt_codes(self) -> Set[str]:
        """
        Union of everything referenced in the JSON:
        - code_lists
        - rvus
        - pleural sections
        - HCPCS primary_cpt_eligible lists
        """
        codes: Set[str] = set()

        # code_lists
        for codes_list in self.raw.get("code_lists", {}).values():
            for code in codes_list:
                codes.add(self._normalize_code(code))

        # rvus
        codes.update(self.raw.get("rvus", {}).keys())
        
        # rvus_additional (new section)
        codes.update(self.raw.get("rvus_additional", {}).keys())

        # pleural
        pleural = self.raw.get("pleural", {})
        for submap_key in ("cpt_map", "thoracoscopy_cpt_map"):
            codes.update(map(self._normalize_code, pleural.get(submap_key, {}).keys()))

        pleural_lists = [
            "thoracentesis_codes",
            "pleural_drainage_codes",
            "chest_tube_insertion_codes",
            "chest_tube_removal_codes",
            "ipc_codes",
            "thoracoscopy_diagnostic_codes",
            "thoracoscopy_surgical_codes",
            "ttna_codes",
        ]
        for list_name in pleural_lists:
            codes.update(map(self._normalize_code, pleural.get(list_name, [])))

        # HCPCS primary_cpt_eligible
        for _hcpcs, info in self.raw.get("hcpcs", {}).items():
            for _group, cpt_list in info.get("primary_cpt_eligible", {}).items():
                codes.update(self._normalize_code(c) for c in cpt_list)

        return codes

    def get_groups_for_code(self, code: str) -> List[str]:
        return sorted(self.code_to_groups.get(self._normalize_code(code), []))

    def is_add_on(self, code: str) -> bool:
        return self._normalize_code(code) in self.add_on_codes

    def get_cpt_info(self, code: str) -> CPTInfo:
        n = self._normalize_code(code)

        # Description from various places
        desc = None

        # 1) pleural->cpt_map / thoracoscopy_cpt_map
        pleural = self.raw.get("pleural", {})
        if n in pleural.get("cpt_map", {}):
            desc = pleural["cpt_map"][n]["description"]
        elif n in pleural.get("thoracoscopy_cpt_map", {}):
            desc = pleural["thoracoscopy_cpt_map"][n]["description"]

        # 2) fee_schedules (airway/Noah/etc.)
        fee_sched_info = None
        for sched in self.raw.get("fee_schedules", {}).values():
            codes = sched.get("codes", {})
            # codes keys include +31654, etc.
            for k, v in codes.items():
                if self._normalize_code(k) == n:
                    desc = desc or v.get("description")
                    fee_sched_info = v
                    break

        rvus = self.raw.get("rvus", {}).get(n) or self.raw.get("rvus_additional", {}).get(n)

        return CPTInfo(
            code=n,
            description=desc,
            groups=self.get_groups_for_code(n),
            is_add_on=self.is_add_on(n),
            rvus=rvus,
            fee_schedule=fee_sched_info,
        )

    # ---- bundling helpers (used by coder) ----

    def apply_bundling(self, codes: Iterable[str]) -> List[str]:
        """
        Apply core, low-risk bundling rules from the JSON to a list of CPTs.

        This is intentionally conservative: it only implements rules that are
        deterministic from the code set alone (no clinical nuance).
        """
        # Work with normalized codes, but preserve original strings
        original_codes = list(codes)
        norm_to_original: Dict[str, List[str]] = {}
        norm_codes: Set[str] = set()

        for c in original_codes:
            n = self._normalize_code(c)
            norm_codes.add(n)
            norm_to_original.setdefault(n, []).append(c)

        brules = self.raw.get("bundling_rules", {})

        # 1) Bronchoscopy diagnostic (31622) bundled when therapeutic in same family
        if "diagnostic_with_surgical" in brules:
            rule = brules["diagnostic_with_surgical"]
            drop = {self._normalize_code(c) for c in rule["drop_codes"]}
            dominant = {self._normalize_code(c) for c in rule["therapeutic_codes"]}
            if norm_codes & dominant:
                norm_codes -= drop

        # 2) Thoracoscopy diagnostic bundled when surgical thoracoscopy present
        if "thoracoscopy_diagnostic_with_surgical" in brules:
            rule = brules["thoracoscopy_diagnostic_with_surgical"]
            drop = {self._normalize_code(c) for c in rule["drop_codes"]}
            dominant = {self._normalize_code(c) for c in rule["therapeutic_codes"]}
            if norm_codes & dominant:
                norm_codes -= drop

        # 3) Pleural post-procedure chest x-ray bundling
        # (two overlapping rules; treat them as equivalent)
        pleural_codes = set()
        cxr_codes = set()
        for name in ("pleural_post_procedure_imaging", "pleural_chest_xray_bundled"):
            if name not in brules:
                continue
            rule = brules[name]
            pleural_codes |= {self._normalize_code(c) for c in rule.get("pleural_codes", [])}
            cxr_codes |= {self._normalize_code(c) for c in rule.get("bundled_imaging", [])}
            cxr_codes |= {self._normalize_code(c) for c in rule.get("radiology_codes", [])}

        if norm_codes & pleural_codes:
            norm_codes -= cxr_codes

        # Re-expand to original strings, preserving ordering where possible
        result: List[str] = []
        for c in original_codes:
            n = self._normalize_code(c)
            if n in norm_codes:
                result.append(c)
        return result

    def groups_from_text(self, note_text: str) -> Set[str]:
        """
        Very simple synonym matcher:
        - Scans the text for strings in synonyms.xxx_terms
        - Maps those synonym lists to relevant code_list keys
        """
        text = note_text.lower()
        syn = self.raw.get("synonyms", {})

        # You can expand this mapping as you refine things
        mapping = {
            "ttna_percutaneous_lung_biopsy": ["ttna_terms"],
            "thoracentesis": ["thoracentesis_terms"],
            "pleural_drainage_chest_tube_catheter": ["pleural_drainage_terms", "chest_tube_terms"],
            "tunneled_pleural_catheter": [
                "tunneled_pleural_catheter_terms",
                "indwelling_pleural_catheter_terms",
                "ipc_terms",
            ],
            "bronchoscopy_tbna": ["tbna_terms"],
            "bronchoscopy_biopsy_parenchymal": ["tblb_terms"],
            "bronchoscopy_diagnostic": ["bal_terms"],
            "bronchoscopy_navigation": ["navigation_terms", "navigation_initiated"],
            "bronchoscopy_ebus_radial": ["radial_terms"],
            "bronchoscopy_ebus_linear": ["linear_ebus_terms", "ebus_terms"],
            "thoracoscopy_diagnostic_biopsy": ["thoracoscopy_terms"],
        }

        matched_groups: Set[str] = set()

        for group, synonym_keys in mapping.items():
            for key in synonym_keys:
                for phrase in syn.get(key, []):
                    if phrase.lower() in text:
                        matched_groups.add(group)
                        break

        return matched_groups

    def codes_from_text(self, note_text: str) -> Set[str]:
        """
        Return candidate CPT codes based on synonym matches and code_lists.
        Preserves the '+' prefix for add-on codes.
        """
        groups = self.groups_from_text(note_text)
        codes: Set[str] = set()
        lists = self.raw.get("code_lists", {})
        for g in groups:
            for code in lists.get(g, []):
                # Preserve '+' prefix for add-on codes, but normalize otherwise
                if code.startswith("+"):
                    codes.add(code)  # Keep as "+31627", "+31654", etc.
                else:
                    codes.add(self._normalize_code(code))
        return codes
