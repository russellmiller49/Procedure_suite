"""End-to-end CPT coder pipeline."""

from __future__ import annotations

from dataclasses import asdict
from typing import Iterable, Sequence

from modules.common.rules_engine import mer
from modules.common.sectionizer import SectionizerService
from modules.common.spans import Span
from modules.common.umls_linking import UmlsLinker

from . import dictionary, posthoc, rules
from .schema import CoderOutput, CodeDecision, DetectedIntent

CODER_VERSION = "0.1.0"

CPT_DESCRIPTIONS = {
    "31627": "Navigational bronchoscopy (EMN)",
    "31628": "Transbronchial lung biopsy, single lobe",
    "+31632": "Additional transbronchial lung biopsy lobe",
    "31652": "Linear EBUS-TBNA 1-2 stations",
    "31653": "Linear EBUS-TBNA 3+ stations",
    "+31654": "Radial EBUS for peripheral lesion",
    "31636": "Bronchial stent placement",
    "31630": "Therapeutic dilation of airway",
    "99152": "Moderate sedation provided by same physician",
    "31645": "Therapeutic aspiration initial",
}


class CoderEngine:
    """Coordinates sectionization, intent detection, and MER logic."""

    def __init__(
        self,
        *,
        sectionizer: SectionizerService | None = None,
        linker: UmlsLinker | None = None,
    ) -> None:
        self.sectionizer = sectionizer or SectionizerService()
        self.linker = linker or UmlsLinker()

    def run(self, note_text: str) -> CoderOutput:
        """Execute the deterministic coder pipeline."""

        sections = self.sectionizer.sectionize(note_text)
        intents = dictionary.detect_intents(note_text, sections)
        self._attach_umls(note_text, intents)

        codes = self._map_intents_to_codes(intents)
        codes, ncci_actions, warnings = rules.apply_rules(codes, intents)
        codes = posthoc.apply_posthoc(codes)
        mer_summary = self._apply_mer(codes)

        return CoderOutput(
            codes=codes,
            intents=intents,
            mer_summary=mer_summary,
            ncci_actions=ncci_actions,
            warnings=warnings,
            version=CODER_VERSION,
        )

    def _map_intents_to_codes(self, intents: Sequence[DetectedIntent]) -> list[CodeDecision]:
        codes: list[CodeDecision] = []

        if any(intent.intent == "navigation" for intent in intents):
            codes.append(
                self._create_decision(
                    cpt="31627",
                    rationale="Navigation initiated",
                    evidence=self._collect_evidence(intents, "navigation"),
                    rule="intent:navigation",
                    confidence=0.92,
                )
            )

        if any(intent.intent == "radial_ebus" for intent in intents):
            codes.append(
                self._create_decision(
                    cpt="+31654",
                    rationale="Radial EBUS used for peripheral lesion",
                    evidence=self._collect_evidence(intents, "radial_ebus"),
                    rule="intent:radial_ebus",
                    confidence=0.9,
                )
            )

        stations = self._unique_values(intents, "linear_ebus_station")
        if stations:
            cpt = "31653" if len(stations) >= 3 else "31652"
            codes.append(
                self._create_decision(
                    cpt=cpt,
                    rationale=f"Linear EBUS-TBNA sampled {len(stations)} station(s)",
                    evidence=self._collect_evidence(intents, "linear_ebus_station"),
                    context={"stations": stations},
                    rule="intent:linear_ebus_station",
                    confidence=0.88,
                )
            )

        lobes = self._unique_values(intents, "tblb_lobe")
        if lobes:
            first_lobe = lobes[0]
            codes.append(
                self._create_decision(
                    cpt="31628",
                    rationale=f"Transbronchial biopsy performed in {first_lobe}",
                    evidence=self._collect_evidence(intents, "tblb_lobe", first_lobe),
                    context={"site": first_lobe},
                    rule="intent:tblb_lobe",
                    confidence=0.9,
                )
            )
            for lobe in lobes[1:]:
                codes.append(
                    self._create_decision(
                        cpt="+31632",
                        rationale=f"Additional lobe sampled: {lobe}",
                        evidence=self._collect_evidence(intents, "tblb_lobe", lobe),
                        context={"site": lobe},
                        rule="intent:tblb_lobe",
                        confidence=0.85,
                    )
                )

        for site in self._unique_values(intents, "stent"):
            codes.append(
                self._create_decision(
                    cpt="31636",
                    rationale=f"Stent placed at {site}",
                    evidence=self._collect_evidence(intents, "stent", site),
                    context={"site": site},
                    rule="intent:stent",
                    confidence=0.82,
                )
            )

        for site in self._unique_values(intents, "dilation"):
            codes.append(
                self._create_decision(
                    cpt="31630",
                    rationale=f"Airway dilation performed at {site}",
                    evidence=self._collect_evidence(intents, "dilation", site),
                    context={"site": site},
                    rule="intent:dilation",
                    confidence=0.8,
                )
            )

        if any(intent.intent == "sedation" for intent in intents):
            codes.append(
                self._create_decision(
                    cpt="99152",
                    rationale="Moderate sedation provided by proceduralist",
                    evidence=self._collect_evidence(intents, "sedation"),
                    context={"sedation": "moderate"},
                    rule="intent:sedation",
                    confidence=0.78,
                )
            )

        if any(intent.intent == "aspiration" for intent in intents):
            codes.append(
                self._create_decision(
                    cpt="31645",
                    rationale="Therapeutic aspiration performed",
                    evidence=self._collect_evidence(intents, "aspiration"),
                    rule="intent:aspiration",
                    confidence=0.7,
                )
            )

        return codes

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

    @staticmethod
    def _collect_evidence(
        intents: Sequence[DetectedIntent], intent_name: str, value: str | None = None
    ) -> list[Span]:
        spans: list[Span] = []
        for intent in intents:
            if intent.intent != intent_name:
                continue
            if value is not None and intent.value != value:
                continue
            spans.extend(intent.evidence)
        return spans

    @staticmethod
    def _unique_values(intents: Sequence[DetectedIntent], intent_name: str) -> list[str]:
        values: list[str] = []
        for intent in intents:
            if intent.intent != intent_name or not intent.value:
                continue
            if intent.value not in values:
                values.append(intent.value)
        return values

    @staticmethod
    def _create_decision(
        *,
        cpt: str,
        rationale: str,
        evidence: list[Span],
        context: dict | None = None,
        rule: str | None = None,
        confidence: float = 0.8,
    ) -> CodeDecision:
        trace = [rule] if rule else []
        return CodeDecision(
            cpt=cpt,
            description=CPT_DESCRIPTIONS[cpt],
            rationale=rationale,
            evidence=evidence,
            context=context or {},
            confidence=confidence,
            rule_trace=trace,
        )
