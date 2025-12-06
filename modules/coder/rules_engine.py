"""No-op rules engine skeleton for future deterministic logic."""

# Future responsibilities (next phases):
# - Hierarchy normalization: stent families, thoracoscopy precedence.
# - Bundling: NCCI / payer-specific hard walls.
# - Count-based mappings: EBUS nodes, number of lesions, etc.
# This keeps LLMs focused on extraction; RulesEngine handles billable logic.

from __future__ import annotations

from typing import Any, Dict, Sequence, Set

from modules.coder.code_families import load_code_families
from modules.coder.ncci import NCCIEngine, NCCI_BUNDLED_REASON_PREFIX
from modules.coder.types import CodeCandidate


class CodingRulesEngine:
    """Deterministic rules layer placeholder.

    Phase 2: add hierarchy normalization using code family definitions.
    Phase 3: add NCCI bundling gatekeeper.
    """

    def __init__(
        self,
        families_cfg: Dict[str, Any] | None = None,
        ncci_engine: NCCIEngine | None = None,
    ):
        self._families_cfg = families_cfg or load_code_families()
        self._ncci = ncci_engine or NCCIEngine()

    def _compute_replacements(self, codes: Set[str]) -> Dict[str, str]:
        """Build mapping of target_code -> replacement_code."""
        replacements: Dict[str, str] = {}
        families = (self._families_cfg.get("families") if self._families_cfg else None) or {}

        for family in families.values():
            dominant_map = (family.get("dominant_codes") or {}) if isinstance(family, dict) else {}
            for dominant_code, rule in dominant_map.items():
                if dominant_code not in codes:
                    continue
                overrides = (rule.get("overrides") or {}) if isinstance(rule, dict) else {}
                for target_code, replacement_code in overrides.items():
                    if target_code in codes:
                        replacements[target_code] = replacement_code

        return replacements

    def _apply_hierarchy_normalization(
        self,
        candidates: Sequence[CodeCandidate],
    ) -> list[CodeCandidate]:
        if not candidates:
            return []

        present_codes = {candidate.code for candidate in candidates}
        replacements = self._compute_replacements(present_codes)

        normalized: list[CodeCandidate] = []
        seen: Set[str] = set()

        for candidate in candidates:
            original_code = candidate.code
            replacement_code = replacements.get(original_code)

            if replacement_code:
                if replacement_code in seen:
                    continue
                reason = candidate.reason or ""
                hierarchy_note = f"hierarchy:{original_code}->{replacement_code}"
                reason = f"{reason}|{hierarchy_note}" if reason else hierarchy_note
                normalized.append(
                    CodeCandidate(
                        code=replacement_code,
                        confidence=candidate.confidence,
                        reason=reason,
                        evidence=candidate.evidence,
                    )
                )
                seen.add(replacement_code)
                continue

            if original_code in seen:
                continue
            normalized.append(candidate)
            seen.add(original_code)

        return normalized

    def _apply_ncci_bundling(
        self,
        candidates: Sequence[CodeCandidate],
    ) -> list[CodeCandidate]:
        if not candidates:
            return []

        codes = {candidate.code for candidate in candidates}
        result = self._ncci.apply(codes)
        allowed = result.allowed
        bundled_map = result.bundled

        bundled_candidates: list[CodeCandidate] = []
        for candidate in candidates:
            code = candidate.code
            if code in allowed:
                bundled_candidates.append(candidate)
                continue
            if code in bundled_map:
                primary = bundled_map[code]
                marker = f"{NCCI_BUNDLED_REASON_PREFIX}{primary}"
                reason = candidate.reason or ""
                reason = f"{reason}|{marker}" if reason else marker
                bundled_candidates.append(
                    CodeCandidate(
                        code=code,
                        confidence=candidate.confidence,
                        reason=reason,
                        evidence=candidate.evidence,
                    )
                )
            else:
                bundled_candidates.append(candidate)

        return bundled_candidates

    def apply(self, candidates: Sequence[CodeCandidate], note_text: str) -> list[CodeCandidate]:
        """Apply deterministic rules to candidate codes."""
        normalized = self._apply_hierarchy_normalization(candidates)
        bundled = self._apply_ncci_bundling(normalized)
        return bundled
