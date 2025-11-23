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
from modules.common.rvu_calc import RVUCalc
from modules.ml_coder import MLCoderService

from . import dictionary, posthoc, rules
from .constants import CPT_DESCRIPTIONS
from .schema import CodeDecision, CoderOutput, DetectedIntent, FinancialSummary, PerCodeBilling

CODER_VERSION = "0.1.0"
logger = get_logger("coder")

_ROOT = Path(__file__).resolve().parents[2]
_RVU_DIR = _ROOT / "proc_autocode" / "rvu" / "data"
RVU_FILE = _RVU_DIR / "rvu_ip_2025.csv"
GPCI_FILE = _RVU_DIR / "gpci_2025.csv"


from .llm_coder import LLMCoder, LLMCodeSuggestion

class CoderEngine:
    """Coordinates sectionization, intent detection, and MER logic."""

    def __init__(
        self,
        *,
        sectionizer: SectionizerService | None = None,
        linker: UmlsLinker | None = None,
        allow_weak_sedation_docs: bool = False,
        ml_service: MLCoderService | None = None,
        use_llm_advisor: bool = False,
    ) -> None:
        self.sectionizer = sectionizer or SectionizerService()
        self.linker = linker or UmlsLinker()
        self.allow_weak_sedation_docs = allow_weak_sedation_docs
        self.ml_service = ml_service or MLCoderService()
        self.rvu_calc = RVUCalc()
        self.use_llm_advisor = use_llm_advisor
        self.llm_coder = LLMCoder() if use_llm_advisor else None

    def run(
        self, 
        note_text: str, 
        *, 
        explain: bool = False,
        locality: str = "00", # Kept for API compat but not used in simple RVUCalc yet
        setting: str = "facility" # Kept for API compat
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
        
        financials = self._compute_financials(codes, mer_summary)

        llm_suggestions: list[LLMCodeSuggestion] = []
        disagreements: list[str] = []
        if self.llm_coder:
            llm_suggestions = self.llm_coder.suggest_codes(note_text)
            self._compare_llm_and_deterministic(codes, llm_suggestions, disagreements)

        warnings = list(mapping_warnings)
        warnings.extend(bundle_warnings)
        warnings.extend(disagreements)

        logger.info(f"Coder run complete. Found {len(codes)} codes.")
        return CoderOutput(
            codes=codes,
            intents=intents,
            mer_summary=mer_summary,
            financials=financials,
            ncci_actions=ncci_actions,
            warnings=warnings,
            version=CODER_VERSION,
            llm_suggestions=llm_suggestions,
            llm_disagreements=disagreements,
        )

    @staticmethod
    def _compare_llm_and_deterministic(
        codes: Sequence[CodeDecision],
        llm_suggestions: Sequence[LLMCodeSuggestion],
        disagreements: list[str],
    ) -> None:
        if not llm_suggestions:
            disagreements.append("LLM produced no valid CPT suggestions; skipping comparison.")
            return

        det_codes = {c.cpt for c in codes}
        llm_codes = {s.cpt for s in llm_suggestions}

        missing_in_det = llm_codes - det_codes
        extra_in_det = det_codes - llm_codes

        if missing_in_det:
            disagreements.append(
                f"LLM suggests additional CPT(s) not coded deterministically: {', '.join(sorted(missing_in_det))}"
            )
        if extra_in_det:
            disagreements.append(
                f"Deterministic coder produced CPT(s) not suggested by LLM: {', '.join(sorted(extra_in_det))}"
            )

    def _compute_financials(self, codes: Sequence[CodeDecision], mer_summary: dict | None) -> FinancialSummary:
        """Build full per-code billing rows using MER math + RVU data."""
        mer_adjustments = {row["cpt"]: row for row in (mer_summary or {}).get("adjustments", [])}
        per_code_rows: list[PerCodeBilling] = []

        for code in codes:
            base = self.rvu_calc.lookup(code.cpt)
            if not base:
                # Log or warn, but still emit a row with zeros
                row = PerCodeBilling(cpt_code=code.cpt, description=code.description or "", modifiers=code.modifiers)
            else:
                row = PerCodeBilling(
                    cpt_code=code.cpt,
                    description=code.description or "",
                    modifiers=code.modifiers,
                    work_rvu=base.work_rvu,
                    total_facility_rvu=base.total_facility_rvu,
                    total_nonfacility_rvu=base.total_nonfacility_rvu,
                    facility_payment=base.facility_payment,
                    nonfacility_payment=base.nonfacility_payment,
                )

            adj = mer_adjustments.get(code.cpt)
            if adj:
                row.mer_role = adj.get("role")
                row.mer_allowed = float(adj.get("allowed", 0.0))
                row.mer_reduction = float(adj.get("reduction", 0.0))
                # For endoscopy, MER allowed is the *facility* total RVU after multiple-endoscopy rules
                row.allowed_facility_rvu = row.mer_allowed or 0.0
            else:
                # If MER didn't touch this code, allow full total RVU
                # But MER usually touches everything if it runs.
                # If MER engine only returns adjustments for modified codes, this handles untouched.
                row.allowed_facility_rvu = row.total_facility_rvu

            # Payment: allowed RVU * CF; for now, mirror facility logic into nonfacility
            row.allowed_facility_payment = row.allowed_facility_rvu * self.rvu_calc.cf
            # If you want full nonfacility logic later, adjust here
            # For now, assume similar reduction ratio or just full allowed if MER didn't specify
            # Note: MER logic in mer.py might be calculating RVUs, not dollars.
            # allowed_nonfacility_rvu calculation requires knowing if MER applies to non-fac similarly.
            # Usually yes for multiple procedure.
            
            if row.total_facility_rvu > 0:
                ratio = row.allowed_facility_rvu / row.total_facility_rvu
                row.allowed_nonfacility_rvu = row.total_nonfacility_rvu * ratio
            else:
                row.allowed_nonfacility_rvu = 0.0
                
            row.allowed_nonfacility_payment = row.allowed_nonfacility_rvu * self.rvu_calc.cf

            per_code_rows.append(row)

        total_work = sum(row.work_rvu for row in per_code_rows)
        total_fac_pay = sum(row.allowed_facility_payment for row in per_code_rows)
        total_nonfac_pay = sum(row.allowed_nonfacility_payment for row in per_code_rows)

        return FinancialSummary(
            conversion_factor=self.rvu_calc.cf,
            locality="00",
            per_code=per_code_rows,
            total_work_rvu=total_work,
            total_facility_payment=total_fac_pay,
            total_nonfacility_payment=total_nonfac_pay,
        )

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