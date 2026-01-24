from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from modules.registry.schema import RegistryRecord


_NAV_FAILURE_PATTERN = re.compile(
    r"(mis-?regist|unable|aborted|fail|suboptimal).{0,50}(navigat|registration)",
    re.IGNORECASE | re.DOTALL,
)
_RADIAL_MARKER_PATTERN = re.compile(r"\b(concentric|eccentric)\b", re.IGNORECASE)
_LINEAR_MARKER_PATTERN = re.compile(
    r"\b(convex|mediastinal|station\s*\d{1,2}[A-Za-z]?)\b",
    re.IGNORECASE,
)
_DILATION_CONTEXT_PATTERN = re.compile(
    r"(skin|subcutaneous|chest wall|tract)(?:\W+\w+){0,10}\W+dilat"
    r"|dilat(?:\W+\w+){0,10}\W+(skin|subcutaneous|chest wall|tract)",
    re.IGNORECASE,
)

_STENT_NEGATION_PATTERNS = [
    re.compile(
        r"\bdecision\b[^.\n]{0,80}\bnot\b[^.\n]{0,40}\b(?:place|insert|perform|deploy)\w*\b"
        r"[^.\n]{0,80}\bstent\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bno\s+additional\s+stents?\b[^.\n]{0,40}\b(?:place|placed|placement|insert|inserted|deploy|deployed)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:no|not|without|declined|deferred)\b[^.\n]{0,40}\bstent(?:s)?\b"
        r"[^.\n]{0,40}\b(?:place|placed|placement|insert|inserted|deploy|deployed)\b",
        re.IGNORECASE,
    ),
]

_STENT_PLACEMENT_CONTEXT_RE = re.compile(
    r"\b(?:stent\b[^.\n]{0,30}\b(place|placed|deploy|deployed|insert|inserted|positioned|advance|advanced|seat|seated|expand|expanded|expanding)\b"
    r"|(place|placed|deploy|deployed|insert|inserted|positioned|advance|advanced|seat|seated|expand|expanded|expanding)\b[^.\n]{0,30}\bstent\b)\b",
    re.IGNORECASE,
)
_STENT_STRONG_PLACEMENT_RE = re.compile(
    r"\b(?:stent\b[^.\n]{0,30}\b(deploy|deployed|insert|inserted|advance|advanced|positioned|seat|seated|expand|expanded|expanding)\b"
    r"|(deploy|deployed|insert|inserted|advance|advanced|positioned|seat|seated|expand|expanded|expanding)\b[^.\n]{0,30}\bstent\b)\b",
    re.IGNORECASE,
)
_STENT_REMOVAL_CONTEXT_RE = re.compile(
    r"\bstent\b[^.\n]{0,60}\b(remov|retriev|extract|explant|grasp|pull|peel)\w*\b",
    re.IGNORECASE,
)
_STENT_INSPECTION_RE = re.compile(
    r"\bstent\b[^.\n]{0,60}\b(evaluat|inspect|inspection|patent|intact|visible|in\s+good\s+position|in\s+place|position\s+confirmed)\b",
    re.IGNORECASE,
)

_IPC_TERMS = ("pleurx", "aspira", "tunneled", "tunnelled", "indwelling pleural catheter", "ipc")
_CHEST_TUBE_TERMS = ("pigtail", "wayne", "pleur-evac", "pleur evac", "tube thoracostomy", "chest tube")
_INSERT_TERMS = ("insert", "inserted", "placed", "place", "deploy", "deployed", "introduced", "positioned")
_REMOVE_TERMS = (
    "remove",
    "removed",
    "removal",
    "exchanged",
    "exchange",
    "explant",
    "withdrawn",
    "discontinue",
    "discontinued",
    "discontinuation",
    "d/c",
    "dc",
)


@dataclass
class GuardrailOutcome:
    record: RegistryRecord | None
    warnings: list[str]
    needs_review: bool
    changed: bool


class ClinicalGuardrails:
    """Postprocess guardrails for common extraction failure modes."""

    def apply_record_guardrails(self, note_text: str, record: RegistryRecord) -> GuardrailOutcome:
        warnings: list[str] = []
        needs_review = False
        changed = False

        record_data = record.model_dump()
        text_lower = (note_text or "").lower()

        # Airway dilation false positives (skin/subcutaneous/chest wall/tract context).
        if _DILATION_CONTEXT_PATTERN.search(text_lower):
            if self._set_procedure_performed(record_data, "airway_dilation", False):
                warnings.append("Airway dilation excluded due to chest wall/skin context.")
                changed = True

        # Rigid bronchoscopy header/body conflict.
        if self._rigid_header_conflict(note_text):
            if self._set_procedure_performed(record_data, "rigid_bronchoscopy", False):
                warnings.append("Rigid bronchoscopy header/body conflict; treating as not performed.")
                changed = True

        # Radial vs linear EBUS disambiguation.
        radial_marker = bool(_RADIAL_MARKER_PATTERN.search(text_lower))
        explicit_radial = bool(
            re.search(
                r"\b(?:radial\s+ebus|radial\s+probe|r-?ebus|rp-?ebus|miniprobe)\b",
                text_lower,
                re.IGNORECASE,
            )
        )
        radial_present = radial_marker or explicit_radial
        linear_marker = bool(_LINEAR_MARKER_PATTERN.search(text_lower))
        station_data_present = self._linear_station_data_present(record_data)
        peripheral_context_present = bool(
            re.search(
                r"\b(?:"
                r"peripheral\s+bronchoscopy|"
                r"fluoro(?:scop\w*)?|"
                r"guide\s+sheath|sheath\s+catheter|large\s+sheath|"
                r"nodule|target\s+lesion|pulmonary\s+nodule|lung\s+nodule|"
                r"transbronchial\s+(?:lung\s+)?biops|tbbx|tblb|"
                r"brush(?:ings?)?\b"
                r")\b",
                text_lower,
            )
        )

        if radial_present:
            changed |= self._set_procedure_performed(record_data, "radial_ebus", True)
            if radial_marker:
                warnings.append("Radial EBUS inferred from concentric/eccentric view.")
            else:
                warnings.append("Radial EBUS inferred from radial probe keywords.")

        if linear_marker:
            changed |= self._set_procedure_performed(record_data, "linear_ebus", True)
            warnings.append("Linear EBUS inferred from convex/mediastinal/station sampling.")

        if station_data_present:
            if self._set_procedure_performed(record_data, "linear_ebus", True):
                warnings.append("Linear EBUS inferred from sampled station data.")

        if radial_present and not linear_marker and not station_data_present:
            changed |= self._set_procedure_performed(record_data, "linear_ebus", False)

        # Combined linear (staging) + radial (peripheral localization) EBUS is common.
        # Only force manual review when there is no peripheral-context evidence that
        # explains why both marker families appear.
        if radial_present and (linear_marker or station_data_present) and not peripheral_context_present:
            needs_review = True
            warnings.append("Radial vs linear EBUS markers both present; review required.")

        # Stent negation and inspection-only guardrails.
        procedures = record_data.get("procedures_performed")
        stent = procedures.get("airway_stent") if isinstance(procedures, dict) else None
        if isinstance(stent, dict) and stent.get("performed") is True:
            negated = any(p.search(text_lower) for p in _STENT_NEGATION_PATTERNS)
            removal_text_present = bool(_STENT_REMOVAL_CONTEXT_RE.search(text_lower))
            removal_flag = stent.get("airway_stent_removal") is True
            removal_present = removal_text_present or removal_flag
            placement_present = bool(_STENT_PLACEMENT_CONTEXT_RE.search(text_lower))
            strong_placement = bool(_STENT_STRONG_PLACEMENT_RE.search(text_lower))
            inspection_only = bool(_STENT_INSPECTION_RE.search(text_lower))

            if negated and not strong_placement:
                if removal_present:
                    if self._set_stent_action(record_data, "Removal"):
                        warnings.append("Stent placement negated; treating as stent removal.")
                        changed = True
                else:
                    if self._clear_stent(record_data):
                        warnings.append("Stent placement negated; treating as not performed.")
                        changed = True
            elif removal_text_present and not placement_present and not strong_placement:
                if self._set_stent_action(record_data, "Removal"):
                    warnings.append("Stent removal language; treating as removal only.")
                    changed = True
            elif removal_flag and not removal_text_present and inspection_only and not placement_present:
                if self._clear_stent(record_data):
                    warnings.append("Stent removal flag not supported by text; treating as not performed.")
                    changed = True
            elif inspection_only and not placement_present and not removal_text_present:
                if self._clear_stent(record_data):
                    warnings.append("Stent inspection-only language; treating as not performed.")
                    changed = True

        # IPC vs chest tube disambiguation.
        ipc_present = self._contains_any(text_lower, _IPC_TERMS)
        tube_present = self._contains_any(text_lower, _CHEST_TUBE_TERMS)
        pleural_flagged = self._pleural_procedure_flagged(record_data)
        if pleural_flagged and (ipc_present or tube_present):
            ipc_insert = any(self._has_action_near(text_lower, term, _INSERT_TERMS) for term in _IPC_TERMS)
            tube_insert = any(self._has_action_near(text_lower, term, _INSERT_TERMS) for term in _CHEST_TUBE_TERMS)
            ipc_remove = any(self._has_action_near(text_lower, term, _REMOVE_TERMS) for term in _IPC_TERMS)
            tube_remove = any(self._has_action_near(text_lower, term, _REMOVE_TERMS) for term in _CHEST_TUBE_TERMS)

            removal_only = False
            if tube_present and tube_remove and not tube_insert and not ipc_insert:
                changed |= self._set_pleural_performed(record_data, "chest_tube", False)
                warnings.append("Chest tube discontinue/removal language; treating as not performed.")
                removal_only = True
            if ipc_present and ipc_remove and not ipc_insert and not tube_insert:
                changed |= self._set_pleural_performed(record_data, "ipc", False)
                warnings.append("IPC discontinue/removal language; treating as not performed.")
                removal_only = True
            if removal_only:
                pass
            else:
                preferred = self._resolve_pleural_device(text_lower, ipc_present, tube_present)
                if preferred == "ipc":
                    changed |= self._set_pleural_performed(record_data, "ipc", True)
                    changed |= self._set_pleural_performed(record_data, "chest_tube", False)
                    warnings.append("IPC inferred from tunneled/IPC device language.")
                elif preferred == "chest_tube":
                    changed |= self._set_pleural_performed(record_data, "chest_tube", True)
                    changed |= self._set_pleural_performed(record_data, "ipc", False)
                    warnings.append("Chest tube inferred from pigtail/Wayne/tube thoracostomy language.")
                elif ipc_present and tube_present:
                    needs_review = True
                    warnings.append("IPC vs chest tube conflict; review required.")

        updated = RegistryRecord(**record_data) if changed else record
        return GuardrailOutcome(
            record=updated,
            warnings=warnings,
            needs_review=needs_review,
            changed=changed,
        )

    def apply_code_guardrails(
        self, note_text: str, codes: list[str]
    ) -> GuardrailOutcome:
        warnings: list[str] = []
        needs_review = False

        if "31627" in codes and _NAV_FAILURE_PATTERN.search(note_text or ""):
            warnings.append("Navigation failure detected. Verify Modifier -53.")
            needs_review = True

        return GuardrailOutcome(
            record=None,
            warnings=warnings,
            needs_review=needs_review,
            changed=False,
        )

    def _contains_any(self, text: str, terms: tuple[str, ...]) -> bool:
        return any(term in text for term in terms)

    def _has_action_near(self, text: str, term: str, actions: tuple[str, ...], window: int = 80) -> bool:
        start = 0
        while True:
            idx = text.find(term, start)
            if idx == -1:
                return False
            window_start = max(0, idx - window)
            window_end = min(len(text), idx + len(term) + window)
            window_text = text[window_start:window_end]
            if any(action in window_text for action in actions):
                return True
            start = idx + len(term)

    def _resolve_pleural_device(
        self,
        text: str,
        ipc_present: bool,
        tube_present: bool,
    ) -> str | None:
        if ipc_present and not tube_present:
            return "ipc"
        if tube_present and not ipc_present:
            return "chest_tube"

        ipc_insert = any(self._has_action_near(text, term, _INSERT_TERMS) for term in _IPC_TERMS)
        tube_insert = any(self._has_action_near(text, term, _INSERT_TERMS) for term in _CHEST_TUBE_TERMS)
        ipc_remove = any(self._has_action_near(text, term, _REMOVE_TERMS) for term in _IPC_TERMS)
        tube_remove = any(self._has_action_near(text, term, _REMOVE_TERMS) for term in _CHEST_TUBE_TERMS)

        if ipc_insert and not tube_insert:
            return "ipc"
        if tube_insert and not ipc_insert:
            return "chest_tube"
        if tube_insert and ipc_remove and not ipc_insert:
            return "chest_tube"
        if ipc_insert and tube_remove and not tube_insert:
            return "ipc"

        return None

    def _rigid_header_conflict(self, note_text: str) -> bool:
        if not note_text:
            return False
        lines = note_text.splitlines()
        header = "\n".join(lines[:8]).lower()
        body = "\n".join(lines[8:]).lower()
        if "rigid" not in header:
            return False
        if "rigid" in body:
            return False
        return "flexible" in body

    def _set_procedure_performed(self, record_data: dict[str, Any], proc_name: str, value: bool) -> bool:
        procedures = record_data.get("procedures_performed")
        if not isinstance(procedures, dict):
            procedures = {}
        proc = procedures.get(proc_name)
        if not isinstance(proc, dict):
            proc = {}
        current = proc.get("performed")
        proc["performed"] = value
        procedures[proc_name] = proc
        record_data["procedures_performed"] = procedures
        return current != value

    def _set_stent_action(self, record_data: dict[str, Any], action: str) -> bool:
        procedures = record_data.get("procedures_performed")
        if not isinstance(procedures, dict):
            procedures = {}
        stent = procedures.get("airway_stent")
        if not isinstance(stent, dict):
            stent = {}
        current = stent.get("action")
        stent["performed"] = True
        stent["action"] = action
        if action.lower().startswith("remov"):
            stent["airway_stent_removal"] = True
        procedures["airway_stent"] = stent
        record_data["procedures_performed"] = procedures
        return current != action

    def _clear_stent(self, record_data: dict[str, Any]) -> bool:
        procedures = record_data.get("procedures_performed")
        if not isinstance(procedures, dict):
            procedures = {}
        stent = procedures.get("airway_stent")
        if not isinstance(stent, dict):
            stent = {}
        current = stent.get("performed")
        procedures["airway_stent"] = {"performed": False}
        record_data["procedures_performed"] = procedures
        return current is not False or len(stent) > 1

    def _set_pleural_performed(self, record_data: dict[str, Any], proc_name: str, value: bool) -> bool:
        pleural = record_data.get("pleural_procedures")
        if not isinstance(pleural, dict):
            pleural = {}
        proc = pleural.get(proc_name)
        if not isinstance(proc, dict):
            proc = {}
        current = proc.get("performed")
        proc["performed"] = value
        pleural[proc_name] = proc
        record_data["pleural_procedures"] = pleural
        return current != value

    def _pleural_procedure_flagged(self, record_data: dict[str, Any]) -> bool:
        pleural = record_data.get("pleural_procedures")
        if not isinstance(pleural, dict):
            return False
        for proc in pleural.values():
            if isinstance(proc, dict) and proc.get("performed") is True:
                return True
        return False

    def _linear_station_data_present(self, record_data: dict[str, Any]) -> bool:
        procedures = record_data.get("procedures_performed")
        if not isinstance(procedures, dict):
            return False
        linear = procedures.get("linear_ebus")
        if not isinstance(linear, dict):
            return False
        stations_sampled = linear.get("stations_sampled")
        stations_detail = linear.get("stations_detail")
        station_bucket = linear.get("station_count_bucket")
        if stations_sampled:
            return True
        if stations_detail:
            return True
        if isinstance(station_bucket, str) and station_bucket.strip():
            return True
        return False


__all__ = ["ClinicalGuardrails", "GuardrailOutcome"]
