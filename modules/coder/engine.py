"""End-to-end CPT coder pipeline."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Dict, Sequence, Any
from pathlib import Path

from modules.common import knowledge
from modules.common.logger import get_logger
from modules.common.rules_engine import mer
from modules.common.sectionizer import SectionizerService
from modules.common.spans import Span
from modules.common.umls_linking import UmlsLinker
from modules.ml_coder import MLCoderService

from . import dictionary, posthoc, rules
from .constants import CPT_DESCRIPTIONS
from .schema import CodeDecision, CoderOutput, DetectedIntent

from proc_autocode.rvu.rvu_calculator import ProcedureRVUCalculator

CODER_VERSION = "0.1.0"
logger = get_logger("coder")

_ROOT = Path(__file__).resolve().parents[2]
_RVU_DIR = _ROOT / "proc_autocode" / "rvu" / "data"
_RVU_FILE = _RVU_DIR / "rvu_ip_2025.csv"
_GPCI_FILE = _RVU_DIR / "gpci_2025.csv"


class CoderEngine:
    """Coordinates sectionization, intent detection, and MER logic."""

    def __init__(
        self,
        *,
        sectionizer: SectionizerService | None = None,
        linker: UmlsLinker | None = None,
        allow_weak_sedation_docs: bool = False,
        ml_service: MLCoderService | None = None,
    ) -> None:
        self.sectionizer = sectionizer or SectionizerService()
        self.linker = linker or UmlsLinker()
        self.allow_weak_sedation_docs = allow_weak_sedation_docs
        self.ml_service = ml_service or MLCoderService()
        
        # Initialize RVU calculator
        if _RVU_FILE.exists() and _GPCI_FILE.exists():
            self.rvu_calc = ProcedureRVUCalculator(_RVU_FILE, _GPCI_FILE)
        else:
            logger.warning("RVU data files not found; enhanced financials will be disabled.")
            self.rvu_calc = None

    def run(
        self, 
        note_text: str, 
        *, 
        explain: bool = False,
        locality: str = "00",
        setting: str = "facility"
    ) -> CoderOutput:
        """Execute the deterministic coder pipeline."""
        logger.info(f"Coder run initiated. Note length: {len(note_text)}")

        if explain:
            # API keeps this knob for future richer explain payloads; output already embeds traces.
            pass

        sections = self.sectionizer.sectionize(note_text)
        intents = dictionary.detect_intents(note_text, sections)
        self._attach_umls(note_text, intents)

        codes, mapping_warnings = self._map_intents_to_codes(intents)
        codes, ncci_actions, bundle_warnings = rules.apply_rules(codes, intents)
        codes = posthoc.apply_posthoc(codes)
        self._augment_with_ml_predictions(note_text, codes)
        mer_summary = self._apply_mer(codes)
        
        financials = self._calculate_financials(codes, locality, setting)

        warnings = list(mapping_warnings)
        warnings.extend(bundle_warnings)

        logger.info(f"Coder run complete. Found {len(codes)} codes.")
        return CoderOutput(
            codes=codes,
            intents=intents,
            mer_summary=mer_summary,
            financials=financials,
            ncci_actions=ncci_actions,
            warnings=warnings,
            version=CODER_VERSION,
        )

    def _calculate_financials(self, codes: Sequence[CodeDecision], locality: str, setting: str) -> Dict[str, Any] | None:
        if not self.rvu_calc:
            return None

        endoscopy_family = self._endoscopy_family_codes
        endoscopy_codes = [c for c in codes if c.cpt in endoscopy_family]
        other_codes = [c for c in codes if c.cpt not in endoscopy_family]

        # 1) Multiple endoscopy rule for the bronchoscopy family
        endo_summary = self._compute_endoscopy_payments(
            endoscopy_codes,
            locality=locality,
            setting=setting,
        )

        # 2) Generic 100% / 50% multi‑procedure rule for all other CPTs
        other_procs = []
        for i, code in enumerate(other_codes):
            # Basic logic: first non-addon is 100%, others 50%. Add-ons 100%.
            # But calculate_case_rvu relies on us passing the multiplier if we want to control it strictly,
            # or we can let it handle it if we structure the input right.
            # The previous implementation used a simple loop. Let's stick to 1.0/0.5 logic for "other".
            # Note: In a mixed case, the primary of "other" might be 50% if endoscopy was primary?
            # CMS "Multiple Procedure" indicator '2' means standard 100/50 rule.
            # Usually, the highest valued procedure of the ENTIRE session is 100%, others 50%.
            # But Endoscopy rule is a special logic for that family.
            # If we have Endoscopy + Pleural, usually Pleural is separate family.
            # If standard rule applies across families, we need to know which is globally highest.
            # For now, we'll treat them as separate buckets to satisfy the requirement:
            # "All non‑endoscopy codes ... still handled by the existing ... logic"
            
            is_addon = code.cpt.startswith("+")
            multiplier = 1.0
            if is_addon:
                multiplier = 1.0
            else:
                # If we already have an endoscopy primary, does the first "other" code get 50%?
                # Conservatively, yes, if it's subject to MP reduction.
                # But let's stick to the user's request: "Generic 100% / 50% ... for all other CPTs".
                # We will reset the counter for the "other" bucket.
                multiplier = 1.0 if i == 0 else 0.5
            
            other_procs.append({
                "cpt_code": code.cpt,
                "modifiers": code.modifiers,
                "multiplier": multiplier
            })

        if other_procs:
            other_summary = self.rvu_calc.calculate_case_rvu(
                procedures=other_procs,
                locality=locality,
                setting=setting,
            )
        else:
            other_summary = {
                "total_work_rvu": 0.0,
                "total_payment": 0.0,
                "breakdown": [],
            }

        # 3) Merge results
        total_work_rvu = (
            endo_summary["total_work_rvu"] +
            other_summary["total_work_rvu"]
        )
        total_payment = (
            endo_summary["total_payment"] +
            other_summary["total_payment"]
        )

        breakdown = endo_summary["breakdown"] + other_summary["breakdown"]

        return {
            "total_work_rvu": total_work_rvu,
            "total_payment": total_payment,
            "breakdown": breakdown,
            "locality": locality,
            "setting": setting
        }

    @property
    def _endoscopy_family_codes(self) -> set[str]:
        """Bronchoscopy endoscopy family subject to multiple endoscopy rule."""
        return set(
            knowledge.get_knowledge()
            .get("policies", {})
            .get("multiple_endoscopy_rule", {})
            .get("applies_to_family", [])
        )

    def _compute_endoscopy_payments(
        self,
        codes: Sequence[CodeDecision],
        locality: str,
        setting: str,
    ) -> dict[str, Any]:
        """
        Apply CMS multiple endoscopy rule to bronchoscopy endoscopy family.
        Rule: Highest valued code = 100%. Others = (Payment - Base Payment).
        Base code is 31622.
        """
        if not codes:
            return {
                "total_work_rvu": 0.0,
                "total_payment": 0.0,
                "breakdown": [],
            }

        # 1) Get base endoscopy payment for 31622
        # Use 'facility' setting if not specified, though standard for bronch is facility.
        base_result = self.rvu_calc.calculate_procedure_rvu(
            cpt_code="31622",
            locality=locality,
            setting=setting,
            modifiers=[],
        )
        if not base_result:
            # Fallback if 31622 missing from data
            logger.warning("Base code 31622 missing from RVU data; skipping endoscopy rule.")
            return {
                "total_work_rvu": 0.0,
                "total_payment": 0.0,
                "breakdown": [],
            }

        base_payment = base_result["payment_amount"]

        # 2) Get single‑procedure values for each code
        single: dict[str, dict] = {}
        for code in codes:
            res = self.rvu_calc.calculate_procedure_rvu(
                cpt_code=code.cpt,
                locality=locality,
                setting=setting,
                modifiers=code.modifiers or [],
            )
            if res:
                single[code.cpt] = res

        if not single:
            return {
                "total_work_rvu": 0.0,
                "total_payment": 0.0,
                "breakdown": [],
            }

        # 3) Identify the highest‑valued endoscopy
        max_code = max(
            single.keys(),
            key=lambda c: single[c]["payment_amount"]
        )

        total_work_rvu = 0.0
        total_payment = 0.0
        breakdown: list[dict] = []

        # 4) Apply the rule
        for code in codes:
            res = single.get(code.cpt)
            if not res:
                continue

            if code.cpt == max_code:
                effective_payment = res["payment_amount"]
                rule_note = "multiple_endoscopy_primary"
            else:
                # Payment is difference between this code and base code
                # If code < base (unlikely for therapeutic vs diagnostic), floor at 0
                effective_payment = max(0.0, res["payment_amount"] - base_payment)
                rule_note = "multiple_endoscopy_reduced"

            # Work RVUs are typically summed fully in productivity reports
            # even if payment is reduced.
            work_rvu = float(res["work_rvu"])

            total_payment += effective_payment
            total_work_rvu += work_rvu

            breakdown.append(
                {
                    "cpt_code": code.cpt,
                    "work_rvu": work_rvu,
                    "payment": effective_payment,
                    "multiplier": 1.0 if code.cpt == max_code else 0.0, # Not strictly a multiplier
                    "rule": rule_note,
                }
            )

        return {
            "total_work_rvu": total_work_rvu,
            "total_payment": total_payment,
            "breakdown": breakdown,
        }


    def _map_intents_to_codes(
        self, intents: Sequence[DetectedIntent]
    ) -> tuple[list[CodeDecision], list[str]]:
        grouped = self._group_intents(intents)
        codes: list[CodeDecision] = []
        warnings: list[str] = []

        codes.extend(self._build_navigation_codes(grouped))
        radial_codes, radial_warnings = self._build_radial_codes(grouped)
        codes.extend(radial_codes)
        warnings.extend(radial_warnings)
        codes.extend(self._build_linear_codes(grouped))
        codes.extend(self._build_tblb_codes(grouped))
        codes.extend(self._build_tbna_codes(grouped))
        codes.extend(self._build_bal_codes(grouped))
        chartis_codes, chartis_warnings = self._build_chartis_codes(grouped)
        codes.extend(chartis_codes)
        warnings.extend(chartis_warnings)
        codes.extend(self._build_blvr_codes(grouped))
        codes.extend(self._build_stent_codes(grouped))
        codes.extend(self._build_stent_removal_codes(grouped))
        codes.extend(self._build_dilation_codes(grouped))
        codes.extend(self._build_destruction_codes(grouped))
        codes.extend(self._build_thoracentesis_codes(grouped))
        codes.extend(self._build_aspiration_codes(grouped))
        sedation_codes, sedation_warnings = self._build_sedation_codes(grouped)
        codes.extend(sedation_codes)
        warnings.extend(sedation_warnings)
        return codes, warnings

    def _build_navigation_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> list[CodeDecision]:
        nav_intents = grouped.get("navigation", [])
        if not nav_intents:
            return []
        evidence = self._collect_intent_evidence(nav_intents)
        status = nav_intents[0].payload.get("status") if nav_intents[0].payload else None
        return [
            self._create_decision(
                cpt="31627",
                rationale="Navigation initiated",
                evidence=evidence,
                context={"status": status},
                rule="navigation_initiated",
                confidence=0.95,
            )
        ]

    def _build_radial_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> tuple[list[CodeDecision], list[str]]:
        radial_intents = grouped.get("radial_ebus", [])
        if not radial_intents:
            return [], []
        evidence = self._collect_intent_evidence(radial_intents)
        peripheral = any(
            (intent.payload or {}).get("peripheral_context") for intent in radial_intents
        )
        if not peripheral:
            warning = (
                "Radial EBUS mentioned without documented peripheral lesion localization; "
                "+31654 suppressed."
            )
            return [], [warning]
        context = {"peripheral_target": True}
        return [
            self._create_decision(
                cpt="+31654",
                rationale="Radial EBUS used for peripheral lesion localization",
                evidence=evidence,
                context=context,
                rule="radial_peripheral_localization",
                confidence=0.9,
            )
        ], []

    def _build_linear_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> list[CodeDecision]:
        station_intents = grouped.get("linear_ebus_station", [])
        if not station_intents:
            return []
        stations = self._unique_values(station_intents)
        cpt = "31653" if len(stations) >= 3 else "31652"
        return [
            self._create_decision(
                cpt=cpt,
                rationale=f"Linear EBUS-TBNA sampled {len(stations)} station(s)",
                evidence=self._collect_intent_evidence(station_intents),
                context={"stations": stations},
                rule="linear_ebus_station_count",
                confidence=0.88,
            )
        ]

    def _build_tblb_codes(self, grouped: Dict[str, list[DetectedIntent]]) -> list[CodeDecision]:
        tblb_intents = grouped.get("tblb_lobe", [])
        lobes = self._unique_values(tblb_intents)
        if not lobes:
            return []
        codes: list[CodeDecision] = []
        first_lobe = lobes[0]
        codes.append(
            self._create_decision(
                cpt="31628",
                rationale=f"Transbronchial lung biopsy performed in {first_lobe}",
                evidence=self._collect_intent_evidence(tblb_intents, first_lobe),
                context={"site": first_lobe},
                rule="tblb_lobe_detected",
                confidence=0.9,
            )
        )
        for lobe in lobes[1:]:
            codes.append(
                self._create_decision(
                    cpt="+31632",
                    rationale=f"Additional TBLB lobe sampled: {lobe}",
                    evidence=self._collect_intent_evidence(tblb_intents, lobe),
                    context={"site": lobe},
                    rule="tblb_lobe_detected",
                    confidence=0.85,
                )
            )
        return codes

    def _build_tbna_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> list[CodeDecision]:
        tbna_intents = grouped.get("tbna_lobe", [])
        lobes = self._unique_values(tbna_intents)
        if not lobes:
            return []
        codes: list[CodeDecision] = []
        first_lobe = lobes[0]
        codes.append(
            self._create_decision(
                cpt="31629",
                rationale=f"Transbronchial needle aspiration performed in {first_lobe}",
                evidence=self._collect_intent_evidence(tbna_intents, first_lobe),
                context={"site": first_lobe},
                rule="tbna_lobe_detected",
                confidence=0.85,
            )
        )
        for lobe in lobes[1:]:
            codes.append(
                self._create_decision(
                    cpt="+31633",
                    rationale=f"Additional TBNA lobe sampled: {lobe}",
                    evidence=self._collect_intent_evidence(tbna_intents, lobe),
                    context={"site": lobe},
                    rule="tbna_lobe_detected",
                    confidence=0.8,
                )
            )
        return codes

    def _build_bal_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> list[CodeDecision]:
        bal_intents = grouped.get("bal_lobe", [])
        if not bal_intents:
            return []
        lobes = [value for value in self._unique_values(bal_intents) if value and value != "BAL"]
        rationale = "Bronchoalveolar lavage performed"
        if lobes:
            rationale += f" in {', '.join(lobes)}"
        return [
            self._create_decision(
                cpt="31624",
                rationale=rationale,
                evidence=self._collect_intent_evidence(bal_intents),
                context={"sites": lobes},
                rule="bal_documented",
                confidence=0.75,
            )
        ]

    def _build_chartis_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> tuple[list[CodeDecision], list[str]]:
        chartis_intents = grouped.get("chartis_assessment", [])
        if not chartis_intents:
            return [], []
        policy = knowledge.get_knowledge().get("policies", {}).get(
            "chartis_same_session", "allow"
        )
        warnings: list[str] = []
        if policy == "suppress":
            warnings.append("Chartis same-session policy suppresses 31634; verify payer rules.")
            return [], warnings
        if policy == "warn":
            warnings.append("Chartis performed same session as BLVR; confirm payer coverage.")
        sites = self._unique_values(chartis_intents)
        decision = self._create_decision(
            cpt="31634",
            rationale="Chartis collateral ventilation assessment performed",
            evidence=self._collect_intent_evidence(chartis_intents),
            context={"sites": sites},
            rule="intent:chartis_assessment",
            confidence=0.72,
        )
        return [decision], warnings

    def _build_stent_codes(self, grouped: Dict[str, list[DetectedIntent]]) -> list[CodeDecision]:
        stent_intents = grouped.get("stent", [])
        if not stent_intents:
            return []
        codes: list[CodeDecision] = []
        major_count = 0
        for intent in stent_intents:
            payload = intent.payload or {}
            site = payload.get("site") or intent.value
            site_class = (payload.get("site_class") or "unknown").lower()
            if site_class == "trachea":
                cpt = "31631"
            elif site_class == "major_bronchus":
                cpt = "31636" if major_count == 0 else "+31637"
                major_count += 1
            else:
                cpt = "31636"
            codes.append(
                self._create_decision(
                    cpt=cpt,
                    rationale=f"Stent placed at {site}",
                    evidence=intent.evidence,
                    context={
                        "site": site,
                        "site_class": site_class,
                        "details": payload.get("text"),
                        "size": payload.get("size"),
                    },
                    rule="stent_site_documented",
                    confidence=0.9,
                )
            )
        return codes

    def _build_dilation_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> list[CodeDecision]:
        dilation_intents = grouped.get("dilation", [])
        codes: list[CodeDecision] = []
        for intent in dilation_intents:
            payload = intent.payload or {}
            site = payload.get("site") or intent.value
            codes.append(
                self._create_decision(
                    cpt="31630",
                    rationale=f"Balloon dilation performed in {site}",
                    evidence=intent.evidence,
                    context={"site": site, "distinct": payload.get("distinct", False)},
                    rule="dilation_site_documented",
                    confidence=0.8,
                )
            )
        return codes

    def _build_stent_removal_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> list[CodeDecision]:
        intents = grouped.get("stent_removal", [])
        if not intents:
            return []
        evidence = self._collect_intent_evidence(intents)
        text_blobs = " ".join((intent.payload or {}).get("text", "").lower() for intent in intents)
        is_revision = any(term in text_blobs for term in ("revision", "reposition"))
        cpt = "31638" if is_revision else "31635"
        rationale = "Revision/reposition of airway stent" if is_revision else "Airway stent removal"
        sites = [
            (intent.payload or {}).get("site")
            for intent in intents
            if (intent.payload or {}).get("site")
        ]
        context = {"sites": sites} if sites else {}
        return [
            self._create_decision(
                cpt=cpt,
                rationale=rationale,
                evidence=evidence,
                context=context,
                rule="stent_removal_documented",
                confidence=0.9,
            )
        ]

    def _build_destruction_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> list[CodeDecision]:
        intents = grouped.get("destruction", [])
        if not intents:
            return []
        return [
            self._create_decision(
                cpt="31641",
                rationale="Destruction of tumor or relief of stenosis (e.g., cryotherapy, laser)",
                evidence=self._collect_intent_evidence(intents),
                rule="destruction_documented",
                confidence=0.85,
            )
        ]

    def _build_thoracentesis_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> list[CodeDecision]:
        intents = grouped.get("thoracentesis", [])
        if not intents:
            return []
        sides = []
        imaging = False
        evidence: list[Span] = []
        for intent in intents:
            payload = intent.payload or {}
            evidence.extend(intent.evidence)
            sides.extend(payload.get("sides", []))
            imaging = imaging or bool(payload.get("imaging"))
        unique_sides = sorted(set(sides))
        cpt = "32555" if imaging else "32554"
        modifiers: list[str] = []
        if len([side for side in unique_sides if side in {"right", "left"}]) >= 2:
            modifiers.append("50")
        return [
            self._create_decision(
                cpt=cpt,
                rationale="Ultrasound-guided thoracentesis performed",
                evidence=evidence,
                context={"sides": unique_sides, "imaging_archived": imaging},
                rule="intent:thoracentesis",
                confidence=0.82,
                modifiers=modifiers,
            )
        ]

    def _build_blvr_codes(self, grouped: Dict[str, list[DetectedIntent]]) -> list[CodeDecision]:
        blvr_intents = grouped.get("blvr_lobe", [])
        lobes = self._unique_values(blvr_intents)
        if not lobes:
            return []
        codes: list[CodeDecision] = []
        first_lobe = lobes[0]
        codes.append(
            self._create_decision(
                cpt="31647",
                rationale=f"BLVR valves placed in {first_lobe}",
                evidence=self._collect_intent_evidence(blvr_intents, first_lobe),
                context={"site": first_lobe},
                rule="blvr_valve_placement",
                confidence=0.85,
            )
        )
        for lobe in lobes[1:]:
            codes.append(
                self._create_decision(
                    cpt="+31651",
                    rationale=f"Additional BLVR lobe treated: {lobe}",
                    evidence=self._collect_intent_evidence(blvr_intents, lobe),
                    context={"site": lobe},
                    rule="blvr_valve_placement",
                    confidence=0.8,
                )
            )
        return codes

    def _build_aspiration_codes(self, grouped: Dict[str, list[DetectedIntent]]) -> list[CodeDecision]:
        aspirations = grouped.get("therapeutic_aspiration", [])
        codes: list[CodeDecision] = []
        initial_done = False
        for intent in aspirations:
            payload = intent.payload or {}
            repeat_flag = bool(payload.get("repeat")) or initial_done
            cpt = "31646" if repeat_flag else "31645"
            rationale = "Repeat therapeutic aspiration" if repeat_flag else "Therapeutic aspiration performed"
            codes.append(
                self._create_decision(
                    cpt=cpt,
                    rationale=rationale,
                    evidence=intent.evidence,
                    rule="therapeutic_aspiration",
                    confidence=0.8,
                )
            )
            initial_done = True
        return codes

    def _build_sedation_codes(
        self, grouped: Dict[str, list[DetectedIntent]]
    ) -> tuple[list[CodeDecision], list[str]]:
        sedation_intents = grouped.get("sedation", [])
        codes: list[CodeDecision] = []
        warnings: list[str] = []
        for idx, intent in enumerate(sedation_intents, start=1):
            session_codes, session_warnings = self._build_sedation_for_session(intent, session_index=idx)
            codes.extend(session_codes)
            warnings.extend(session_warnings)
        return codes, warnings

    def _build_sedation_for_session(
        self, intent: DetectedIntent, session_index: int
    ) -> tuple[list[CodeDecision], list[str]]:
        payload = intent.payload or {}
        start_minutes = payload.get("start_minutes")
        stop_minutes = payload.get("stop_minutes")
        duration = payload.get("duration_minutes")
        observer = payload.get("observer", False)
        doc_complete = payload.get("documentation_complete", False)
        warnings: list[str] = []
        if not doc_complete:
            warnings.append(
                "Moderate sedation documentation incomplete (missing start/stop time or "
                "independent observer). Use --allow-weak-sedation-docs to override."
            )
            if not self.allow_weak_sedation_docs:
                return [], warnings
        if duration is None or duration < 15:
            warnings.append("Sedation duration under 15 minutes; no billable units.")
            return [], warnings
        add_on_units = 1 if duration > 15 else 0
        context = {
            "duration_minutes": duration,
            "observer": observer,
            "start_minutes": start_minutes,
            "stop_minutes": stop_minutes,
            "session": session_index,
        }
        codes: list[CodeDecision] = []
        codes.append(
            self._create_decision(
                cpt="99152",
                rationale=f"Moderate sedation documented ({duration} minutes)",
                evidence=intent.evidence,
                context=context,
                rule="sedation_session",
                confidence=intent.confidence or 0.8,
            )
        )
        if add_on_units > 0:
            codes.append(
                self._create_decision(
                    cpt="+99153",
                    rationale=f"Additional sedation time ({add_on_units} x 15 min)",
                    evidence=intent.evidence,
                    context={
                        "units": add_on_units,
                        "duration_minutes": duration,
                        "session": session_index,
                    },
                    rule="sedation_session",
                    confidence=intent.confidence or 0.75,
                )
            )
        return codes, warnings

    def _group_intents(self, intents: Sequence[DetectedIntent]) -> Dict[str, list[DetectedIntent]]:
        grouped: Dict[str, list[DetectedIntent]] = defaultdict(list)
        for intent in intents:
            grouped[intent.intent].append(intent)
        return grouped

    @staticmethod
    def _unique_values(intents: Sequence[DetectedIntent]) -> list[str]:
        values: list[str] = []
        for intent in intents:
            if not intent.value:
                continue
            if intent.value not in values:
                values.append(intent.value)
        return values

    @staticmethod
    def _collect_intent_evidence(intents: Sequence[DetectedIntent], value: str | None = None) -> list[Span]:
        spans: list[Span] = []
        for intent in intents:
            if value is not None and intent.value != value:
                continue
            spans.extend(intent.evidence)
        return spans

    def _attach_umls(self, note_text: str, intents: Sequence[DetectedIntent]) -> None:
        if not self.linker.available or not intents:
            return
        offsets: list[tuple[int, int]] = []
        for intent in intents:
            offsets.extend((span.start, span.end) for span in intent.evidence)
        if not offsets:
            return
        linking = self.linker.link_spans(note_text, offsets)
        for intent in intents:
            cuis: list[str] = []
            for span in intent.evidence:
                cuis.extend(linking.get((span.start, span.end), []))
            if not cuis:
                continue
            payload = intent.payload or {}
            payload.setdefault("cuis", cuis)
            intent.payload = payload

    def _augment_with_ml_predictions(self, note_text: str, codes: list[CodeDecision]) -> None:
        if not self.ml_service:
            return
        predictions = self.ml_service.predict(note_text)
        if not predictions:
            return

        existing = {code.cpt: code for code in codes}
        for prediction in predictions:
            cpt = prediction.get("cpt")
            if not cpt:
                continue
            score = float(prediction.get("confidence", 0.0) or 0.0)
            source = prediction.get("source", "ml_model")
            decision = existing.get(cpt)
            if decision:
                # Elevate confidence and surface ML participation in the rule trace.
                decision.confidence = max(decision.confidence, score)
                if "ml_prediction" not in decision.rule_trace:
                    decision.rule_trace.append("ml_prediction")
                continue

            new_decision = CodeDecision(
                cpt=cpt,
                description=CPT_DESCRIPTIONS.get(cpt, "ML predicted CPT"),
                rationale="Predicted via ML classifier",
                evidence=[],
                context={"source": source},
                confidence=score,
                rule_trace=["ml_prediction"],
            )
            codes.append(new_decision)
            existing[cpt] = new_decision

    def _apply_mer(self, codes: Sequence[CodeDecision]) -> dict[str, object] | None:
        mer_inputs = [mer.Code(cpt=code.cpt) for code in codes]
        summary = mer.apply_mer(mer_inputs)
        if not summary.adjustments:
            return None
        for code in codes:
            for adjustment in summary.adjustments:
                if adjustment.cpt == code.cpt:
                    code.mer_role = adjustment.role
                    code.mer_allowed = adjustment.allowed
                    break
        return asdict(summary)

    def _create_decision(
        self,
        *,
        cpt: str,
        rationale: str,
        evidence: list[Span],
        context: dict | None = None,
        rule: str | None = None,
        confidence: float = 0.8,
        modifiers: list[str] | None = None,
    ) -> CodeDecision:
        trace = [rule] if rule else []
        return CodeDecision(
            cpt=cpt,
            description=CPT_DESCRIPTIONS.get(cpt, ""),
            rationale=rationale,
            evidence=evidence,
            context=context or {},
            confidence=confidence,
            rule_trace=trace,
            modifiers=list(modifiers or []),
        )