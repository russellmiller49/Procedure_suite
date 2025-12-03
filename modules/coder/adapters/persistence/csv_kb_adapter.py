"""Knowledge Base adapter for JSON/CSV files.

Loads the IP coding and billing knowledge base from JSON files
and implements the KnowledgeBaseRepository interface.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Set

from modules.domain.knowledge_base.models import ProcedureInfo, NCCIPair
from modules.domain.knowledge_base.repository import KnowledgeBaseRepository
from modules.common.exceptions import KnowledgeBaseError


class JsonKnowledgeBaseAdapter(KnowledgeBaseRepository):
    """Adapter that loads KB from the ip_coding_billing JSON format."""

    def __init__(self, data_path: str | Path):
        self._data_path = Path(data_path)
        self._raw_data: dict = {}
        self._procedures: dict[str, ProcedureInfo] = {}
        self._ncci_pairs: dict[str, list[NCCIPair]] = {}
        self._mer_groups: dict[str, str] = {}
        self._addon_codes: set[str] = set()
        self._all_codes: set[str] = set()
        self._version: str = ""

        self._load_data()

    @property
    def version(self) -> str:
        return self._version

    def _load_data(self) -> None:
        """Load and parse the knowledge base JSON file."""
        if not self._data_path.is_file():
            raise KnowledgeBaseError(f"KB file not found: {self._data_path}")

        try:
            with self._data_path.open() as f:
                self._raw_data = json.load(f)
        except json.JSONDecodeError as e:
            raise KnowledgeBaseError(f"Invalid JSON in KB file: {e}")

        self._version = self._raw_data.get("version", "unknown")

        # Load procedure codes from fee_schedules
        self._load_procedures()

        # Load NCCI pairs
        self._load_ncci_pairs()

        # Load MER groups from bundling_rules
        self._load_mer_groups()

        # Load addon codes from code_lists
        self._load_addon_codes()

    def _load_procedures(self) -> None:
        """Load procedure information from fee_schedules section."""
        fee_schedules = self._raw_data.get("fee_schedules", {})

        for schedule_name, schedule_data in fee_schedules.items():
            codes_section = schedule_data.get("codes", {})

            for code, code_data in codes_section.items():
                if code in self._procedures:
                    # Already loaded from another schedule
                    continue

                self._all_codes.add(code)

                # Determine category from schedule name
                category = self._extract_category(schedule_name)

                # Check if addon
                is_addon = code.startswith("+") or code in self._addon_codes

                # Get parent codes if addon
                parent_codes = self._get_parent_codes_for_addon(code)

                # Get bundled codes
                bundled_with = self._get_bundled_codes_for(code)

                proc_info = ProcedureInfo(
                    code=code,
                    description=code_data.get("description", ""),
                    category=category,
                    work_rvu=float(code_data.get("work_rvu", 0)),
                    facility_pe_rvu=float(code_data.get("facility_pe_rvu", 0)),
                    malpractice_rvu=float(code_data.get("malpractice_rvu", 0)),
                    total_facility_rvu=float(code_data.get("total_facility_rvu", 0)),
                    is_addon=is_addon,
                    parent_codes=parent_codes,
                    bundled_with=bundled_with,
                    mer_group=self._mer_groups.get(code),
                    modifiers=code_data.get("modifiers", []),
                    notes=code_data.get("notes"),
                    raw_data=code_data,
                )
                self._procedures[code] = proc_info

    def _load_ncci_pairs(self) -> None:
        """Load NCCI edit pairs from the ncci_pairs section."""
        ncci_list = self._raw_data.get("ncci_pairs", [])

        for pair_data in ncci_list:
            primary = pair_data.get("primary", "")
            secondary = pair_data.get("secondary", "")
            modifier_allowed = pair_data.get("modifier_allowed", False)
            reason = pair_data.get("reason", "")

            if not primary or not secondary:
                continue

            pair = NCCIPair(
                primary=primary,
                secondary=secondary,
                modifier_allowed=modifier_allowed,
                reason=reason,
            )

            # Index by primary code
            if primary not in self._ncci_pairs:
                self._ncci_pairs[primary] = []
            self._ncci_pairs[primary].append(pair)

            # Also index by secondary for reverse lookups
            if secondary not in self._ncci_pairs:
                self._ncci_pairs[secondary] = []
            self._ncci_pairs[secondary].append(pair)

    def _load_mer_groups(self) -> None:
        """Load MER groups from bundling_rules section."""
        bundling_rules = self._raw_data.get("bundling_rules", {})

        for rule_name, rule_data in bundling_rules.items():
            if not isinstance(rule_data, dict):
                continue

            # Look for MER-related rules
            if "mer_group" in rule_data or rule_data.get("rule_type") == "mer":
                mer_group_id = rule_data.get("mer_group", rule_name)
                codes = rule_data.get("codes", [])
                for code in codes:
                    self._mer_groups[code] = mer_group_id

    def _load_addon_codes(self) -> None:
        """Load addon code list from code_lists section."""
        code_lists = self._raw_data.get("code_lists", {})

        # Look for addon code lists
        for list_name, codes in code_lists.items():
            if "addon" in list_name.lower() and isinstance(codes, list):
                self._addon_codes.update(codes)

        # Also mark codes starting with + as addons
        for code in self._all_codes:
            if code.startswith("+"):
                self._addon_codes.add(code)

    def _extract_category(self, schedule_name: str) -> str:
        """Extract category from schedule name."""
        # e.g., "physician_2025_airway" -> "airway"
        parts = schedule_name.split("_")
        if len(parts) >= 3:
            return parts[-1]
        return "general"

    def _get_parent_codes_for_addon(self, addon_code: str) -> list[str]:
        """Get valid parent codes for an addon code."""
        bundling_rules = self._raw_data.get("bundling_rules", {})

        for rule_name, rule_data in bundling_rules.items():
            if not isinstance(rule_data, dict):
                continue

            addon_codes = rule_data.get("addon_codes", [])
            if addon_code in addon_codes or addon_code.lstrip("+") in addon_codes:
                return rule_data.get("parent_codes", [])

        return []

    def _get_bundled_codes_for(self, code: str) -> list[str]:
        """Get codes that are bundled with the given code."""
        bundled: list[str] = []
        bundling_rules = self._raw_data.get("bundling_rules", {})

        for rule_name, rule_data in bundling_rules.items():
            if not isinstance(rule_data, dict):
                continue

            codes_in_rule = rule_data.get("codes", [])
            if code in codes_in_rule:
                bundled.extend(c for c in codes_in_rule if c != code)

        return bundled

    def get_procedure_info(self, code: str) -> Optional[ProcedureInfo]:
        """Get procedure information for a CPT code."""
        return self._procedures.get(code)

    def get_mer_group(self, code: str) -> Optional[str]:
        """Get the MER group ID for a code, if any."""
        return self._mer_groups.get(code)

    def get_ncci_pairs(self, code: str) -> list[NCCIPair]:
        """Get all NCCI pairs where this code is involved."""
        return self._ncci_pairs.get(code, [])

    def is_addon_code(self, code: str) -> bool:
        """Check if a code is an add-on code."""
        return code in self._addon_codes or code.startswith("+")

    def get_all_codes(self) -> Set[str]:
        """Get all valid CPT codes in the knowledge base."""
        return self._all_codes.copy()

    def get_parent_codes(self, addon_code: str) -> list[str]:
        """Get valid parent codes for an add-on code."""
        proc = self._procedures.get(addon_code)
        if proc:
            return proc.parent_codes
        return []

    def get_bundled_codes(self, code: str) -> list[str]:
        """Get codes that are bundled with the given code."""
        proc = self._procedures.get(code)
        if proc:
            return proc.bundled_with
        return []


# Alias for backwards compatibility with starter scripts
CsvKnowledgeBaseAdapter = JsonKnowledgeBaseAdapter
