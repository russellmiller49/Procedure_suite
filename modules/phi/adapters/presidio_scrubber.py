"""Presidio-based scrubber adapter (synthetic PHI demo ready).

Implements PHIScrubberPort using Presidio AnalyzerEngine. Avoids logging raw
PHI and preserves IP anatomical terms via allowlist filtering.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Any
from functools import lru_cache
from typing import Iterable

from modules.phi.ports import PHIScrubberPort, ScrubResult

logger = logging.getLogger(__name__)


ANATOMICAL_ALLOW_LIST = {
    # Lung lobes and shorthand
    "upper lobe",
    "lower lobe",
    "middle lobe",
    "right upper lobe",
    "rul",
    "right middle lobe",
    "rml",
    "right lower lobe",
    "rll",
    "left upper lobe",
    "lul",
    "left lower lobe",
    "lll",
    "lingula",
    # Airway structures
    "carina",
    "trachea",
    "bronchus",
    "bronchi",
    "mainstem",
    "segmental",
    "subsegmental",
    # Stations
    "station 4r",
    "station 4l",
    "station 7",
    "station 2r",
    "station 2l",
    "station 10",
    "station 11",
    "station 12",
    # Mediastinal/lymphatic terms
    "mediastinum",
    "hilum",
    "hilar",
    "paratracheal",
    # Procedures/techniques
    "ebus",
    "eus",
    "tbna",
    "bal",
    "bronchoscopy",
    # Laterality descriptors
    "left",
    "right",
    "bilateral",
    "unilateral",
}

CLINICAL_ALLOW_LIST = {
    # Meds + common descriptors that frequently false-positive as PHI.
    "kenalog",
    "nonobstructive",
    # Common clinical/admin tokens that spaCy can misclassify as entities (often LOCATION).
    "anesthesia",
    "general anesthesia",
    # Common clinician credentials.
    "md",
    "do",
    "phd",
    # Existing anatomical allow-list (critical for procedure coding).
    *ANATOMICAL_ALLOW_LIST,
}

DEFAULT_ENTITY_SCORE_THRESHOLDS: dict[str, float] = {
    "PERSON": 0.50,
    "DATE_TIME": 0.60,
    "LOCATION": 0.70,
    "MRN": 0.50,
    "__DEFAULT__": 0.50,
}

DEFAULT_RELATIVE_DATE_TIME_PHRASES: tuple[str, ...] = (
    "about a week",
    "in a week",
    "next week",
    "today",
    "tomorrow",
)

_ALLOWLIST_BOUNDARY_RE = re.compile(
    r"(?i)\b(?:"
    + "|".join(sorted((re.escape(t) for t in CLINICAL_ALLOW_LIST), key=len, reverse=True))
    + r")\b"
)

_DEVICE_MODEL_CONTEXT_RE = re.compile(
    r"\b(?:[A-Z]{1,3}\d{2,4}|[A-Z]{1,3}-[A-Z0-9]{2,10})\b"
    r"(?=[^\n]{0,20}\b(?:video bronchoscope|bronchoscope|scope|cryoprobe|needle)\b)",
    re.IGNORECASE,
)

_MRN_ID_LINE_RE = re.compile(r"\b(mrn|id)\s*[:#]", re.IGNORECASE)


@dataclass(frozen=True)
class Detection:
    entity_type: str
    start: int
    end: int
    score: float


def _detection_key(d: Detection) -> tuple[str, int, int, float]:
    return (d.entity_type, d.start, d.end, d.score)


def _diff_removed(before: list[Detection], after: list[Detection]) -> list[Detection]:
    remaining: dict[tuple[str, int, int, float], int] = {}
    for d in after:
        key = _detection_key(d)
        remaining[key] = remaining.get(key, 0) + 1

    removed: list[Detection] = []
    for d in before:
        key = _detection_key(d)
        count = remaining.get(key, 0)
        if count > 0:
            remaining[key] = count - 1
            continue
        removed.append(d)
    return removed


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_score_thresholds(value: str | None) -> dict[str, float]:
    if not value:
        return dict(DEFAULT_ENTITY_SCORE_THRESHOLDS)

    thresholds: dict[str, float] = dict(DEFAULT_ENTITY_SCORE_THRESHOLDS)
    for part in value.split(","):
        if not part.strip():
            continue
        if ":" not in part:
            continue
        entity, raw_score = part.split(":", 1)
        entity = entity.strip().upper()
        try:
            thresholds[entity] = float(raw_score.strip())
        except ValueError:
            continue
    return thresholds


def _is_allowlisted(detected_text: str) -> bool:
    stripped = detected_text.strip().lower()
    if stripped in CLINICAL_ALLOW_LIST:
        return True
    return _ALLOWLIST_BOUNDARY_RE.search(detected_text) is not None


def filter_allowlisted_terms(text: str, results: list) -> list:
    """Drop detections whose detected text is allow-listed."""

    filtered: list = []
    for res in results:
        detected_text = text[int(getattr(res, "start")) : int(getattr(res, "end"))]
        if _is_allowlisted(detected_text):
            continue
        filtered.append(res)
    return filtered


def filter_device_model_context(text: str, results: list) -> list:
    """Drop detections which match known device/model identifiers in device context."""

    safe_spans: list[tuple[int, int]] = []
    for m in _DEVICE_MODEL_CONTEXT_RE.finditer(text):
        line_start, line_end = _line_bounds(text, m.start())
        line = text[line_start:line_end]
        if _MRN_ID_LINE_RE.search(line):
            continue
        safe_spans.append((m.start(), m.end()))

    if not safe_spans:
        return results

    filtered: list = []
    for res in results:
        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        if any(start >= s and end <= e for s, e in safe_spans):
            continue
        filtered.append(res)
    return filtered


def filter_datetime_exclusions(text: str, results: list, relative_phrases: Iterable[str]) -> list:
    """Drop DATE_TIME detections that are durations or vague/relative time."""

    duration_re = re.compile(
        r"^\s*\d+(?:\.\d+)?\s*(?:second|seconds|minute|minutes|hour|hours|day|days|week|weeks)\b",
        re.IGNORECASE,
    )
    relative_res = [re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE) for p in relative_phrases]

    filtered: list = []
    for res in results:
        if getattr(res, "entity_type", None) != "DATE_TIME":
            filtered.append(res)
            continue
        detected_text = text[int(getattr(res, "start")) : int(getattr(res, "end"))]
        if duration_re.search(detected_text):
            continue
        if any(r.search(detected_text) for r in relative_res):
            continue
        filtered.append(res)
    return filtered


def filter_low_score_results(results: list, thresholds: dict[str, float]) -> list:
    """Drop detections below per-entity minimum score thresholds."""

    filtered: list = []
    for res in results:
        entity_type = str(getattr(res, "entity_type", "")).upper()
        score = float(getattr(res, "score", 0.0) or 0.0)
        minimum = float(thresholds.get(entity_type, thresholds.get("__DEFAULT__", 0.0)))
        if score < minimum:
            continue
        filtered.append(res)
    return filtered


def select_non_overlapping_results(results: list) -> list:
    """Resolve overlaps by keeping the highest-confidence, longest detections."""

    def _key(r) -> tuple[float, int, int, str]:
        start = int(getattr(r, "start"))
        end = int(getattr(r, "end"))
        score = float(getattr(r, "score", 0.0) or 0.0)
        length = end - start
        entity_type = str(getattr(r, "entity_type", ""))
        return (score, length, -start, entity_type)

    selected: list = []
    for res in sorted(results, key=_key, reverse=True):
        start = int(getattr(res, "start"))
        end = int(getattr(res, "end"))
        if any(start < int(getattr(s, "end")) and end > int(getattr(s, "start")) for s in selected):
            continue
        selected.append(res)

    return sorted(selected, key=lambda r: int(getattr(r, "start")))


def filter_provider_signature_block(text: str, results: list) -> list:
    """Drop PERSON detections in likely provider signature blocks near the end."""

    header = re.search(r"(?im)^recommendations:\s*$", text)
    zone_start = header.start() if header else int(len(text) * 0.75)

    cred_re = re.compile(r"(?:,\s*)?(md|do)\b", re.IGNORECASE)
    service_re = re.compile(r"\binterventional\s+pulmonology\b", re.IGNORECASE)

    filtered: list = []
    for res in results:
        if getattr(res, "entity_type", None) != "PERSON":
            filtered.append(res)
            continue
        if int(getattr(res, "start")) < zone_start:
            filtered.append(res)
            continue

        line_start, line_end = _line_bounds(text, int(getattr(res, "start")))
        line = text[line_start:line_end]
        next_line = ""
        if line_end < len(text):
            nl_start = line_end + 1
            nl_end = text.find("\n", nl_start)
            if nl_end == -1:
                nl_end = len(text)
            next_line = text[nl_start:nl_end]

        has_cred = cred_re.search(line) is not None
        has_service = service_re.search(line) is not None or service_re.search(next_line) is not None
        if has_cred and has_service:
            continue

        filtered.append(res)

    return filtered


def _line_bounds(text: str, index: int) -> tuple[int, int]:
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    if end == -1:
        end = len(text)
    return start, end


def _context_window(text: str, start: int, end: int, window: int = 40) -> str:
    left = max(0, start - window)
    right = min(len(text), end + window)
    return text[left:right]


def filter_person_provider_context(text: str, results: list) -> list:
    """Prevent redaction of clinician/provider names based on local context."""

    patient_label_re = re.compile(r"^patient\s*:", re.IGNORECASE)
    dr_prefix_re = re.compile(r"\b(dr\.?|doctor)\s*$", re.IGNORECASE)
    provider_inline_label_re = re.compile(
        r"\b(surgeon|assistant|anesthesiologist|attending|fellow|resident)\b\s*:\s*$",
        re.IGNORECASE,
    )
    credential_suffix_re = re.compile(r"^\s*,?\s*(md|do)\b", re.IGNORECASE)

    filtered: list = []
    for res in results:
        if getattr(res, "entity_type", None) != "PERSON":
            filtered.append(res)
            continue

        res_start = int(getattr(res, "start"))
        res_end = int(getattr(res, "end"))
        start, _ = _line_bounds(text, res_start)
        _, end = _line_bounds(text, res_end)
        line = text[start:end]

        # Patient header line always redacts (even if patient is a clinician with credentials).
        if patient_label_re.search(line.lstrip()):
            filtered.append(res)
            continue

        prefix_window = text[max(0, res_start - 60) : res_start]
        if provider_inline_label_re.search(prefix_window):
            continue
        if dr_prefix_re.search(prefix_window):
            continue

        suffix_window = text[res_end : min(len(text), res_end + 12)]
        if credential_suffix_re.search(suffix_window):
            continue

        filtered.append(res)

    return filtered


def redact_with_audit(
    *,
    text: str,
    detections: list[Detection],
    enable_driver_license_recognizer: bool,
    score_thresholds: dict[str, float],
    relative_datetime_phrases: Iterable[str],
    nlp_backend: str | None = None,
    nlp_model: str | None = None,
    requested_nlp_model: str | None = None,
) -> tuple[ScrubResult, dict[str, Any]]:
    if not text:
        empty = ScrubResult(scrubbed_text="", entities=[])
        return empty, {"detections": [], "removed_detections": [], "redacted_text": ""}

    raw = detections
    removed: list[dict[str, Any]] = []

    def _record_removed(before: list[Detection], after: list[Detection], reason: str) -> None:
        for d in _diff_removed(before, after):
            removed.append(
                {
                    "reason": reason,
                    "entity_type": d.entity_type,
                    "start": d.start,
                    "end": d.end,
                    "score": d.score,
                    "detected_text": text[d.start : d.end],
                    "surrounding_context": _context_window(text, d.start, d.end, window=40),
                }
            )

    step = filter_person_provider_context(text, raw)
    _record_removed(raw, step, "provider_context")

    step2 = filter_provider_signature_block(text, step)
    _record_removed(step, step2, "provider_context")

    step3 = filter_device_model_context(text, step2)
    _record_removed(step2, step3, "device_model")

    step4 = filter_datetime_exclusions(text, step3, relative_phrases=relative_datetime_phrases)
    _record_removed(step3, step4, "duration_datetime")

    step5 = filter_allowlisted_terms(text, step4)
    _record_removed(step4, step5, "allowlist")

    step6 = filter_low_score_results(step5, thresholds=score_thresholds)
    _record_removed(step5, step6, "low_score")

    final = select_non_overlapping_results(step6)
    _record_removed(step6, final, "overlap")

    scrubbed_text = text
    entities = []
    for _, d in enumerate(sorted(final, key=lambda r: r.start, reverse=True)):
        placeholder = f"<{d.entity_type.upper()}>"
        scrubbed_text = scrubbed_text[: d.start] + placeholder + scrubbed_text[d.end :]
        entities.append(
            {
                "placeholder": placeholder,
                "entity_type": d.entity_type,
                "original_start": d.start,
                "original_end": d.end,
            }
        )

    entities = list(reversed(entities))
    scrub_result = ScrubResult(scrubbed_text=scrubbed_text, entities=entities)

    detections_report = []
    for d in raw:
        detections_report.append(
            {
                "entity_type": d.entity_type,
                "start": d.start,
                "end": d.end,
                "score": d.score,
                "detected_text": text[d.start : d.end],
                "surrounding_context": _context_window(text, d.start, d.end, window=40),
            }
        )

    report: dict[str, Any] = {
        "config": {
            "nlp_backend": nlp_backend,
            "nlp_model": nlp_model,
            "requested_nlp_model": requested_nlp_model,
            "enable_driver_license_recognizer": enable_driver_license_recognizer,
            "entity_score_thresholds": dict(score_thresholds),
            "relative_datetime_phrases": list(relative_datetime_phrases),
        },
        "detections": detections_report,
        "removed_detections": removed,
        "redacted_text": scrub_result.scrubbed_text,
    }

    return scrub_result, report


def _build_analyzer(model_name: str):
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": model_name}],
        }
    )
    nlp_engine = provider.create_engine()
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

    # High-confidence override: treat patient header patterns as PERSON.
    # This helps when Presidio misses the patient identity in demographic headers.
    from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult

    class _PatientLabelRecognizer(PatternRecognizer):
        def __init__(self):
            super().__init__(
                supported_entity="PERSON",
                patterns=[
                    Pattern(name="patient_label_line", regex=r"(?im)^Patient:\s*.+$", score=0.95),
                    Pattern(
                        name="name_then_mrn",
                        regex=r"(?im)^[A-Z][A-Za-z'-]+\s*,\s*[A-Z][A-Za-z'-]+.*\b(?:MRN|ID)\s*[:#]",
                        score=0.95,
                    ),
                ],
                name="PATIENT_LABEL_NAME",
            )
            self._patient_line = re.compile(
                r"(?im)^Patient:\s*(.+?)(?:\s+(?:MRN|ID)\s*[:#].*)?$"
            )
            self._name_then_mrn = re.compile(
                r"(?im)^([A-Z][A-Za-z'-]+\s*,\s*[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+)?)\s+(?=(?:MRN|ID)\s*[:#])"
            )

        def analyze(self, text: str, entities: list[str], nlp_artifacts=None):  # type: ignore[override]
            results: list[RecognizerResult] = []
            if "PERSON" not in entities:
                return results
            for m in self._patient_line.finditer(text):
                start, end = m.span(1)
                if end - start >= 2:
                    results.append(RecognizerResult(entity_type="PERSON", start=start, end=end, score=0.95))
            for m in self._name_then_mrn.finditer(text):
                start, end = m.span(1)
                if end - start >= 2:
                    results.append(RecognizerResult(entity_type="PERSON", start=start, end=end, score=0.95))
            return results

    analyzer.registry.add_recognizer(_PatientLabelRecognizer())

    class _MrnRecognizer(PatternRecognizer):
        def __init__(self):
            super().__init__(
                supported_entity="MRN",
                patterns=[
                    Pattern(name="mrn", regex=r"(?i)\b(?:MRN|ID)\s*[:#]?\s*[A-Z0-9][A-Z0-9-]{3,}\b", score=0.95)
                ],
                name="MRN",
            )
            self._mrn = re.compile(r"(?i)\b(?:MRN|ID)\s*[:#]?\s*([A-Z0-9][A-Z0-9-]{3,})\b")

        def analyze(self, text: str, entities: list[str], nlp_artifacts=None):  # type: ignore[override]
            results: list[RecognizerResult] = []
            if "MRN" not in entities:
                return results
            for m in self._mrn.finditer(text):
                start, end = m.span(1)
                results.append(RecognizerResult(entity_type="MRN", start=start, end=end, score=0.95))
            return results

    analyzer.registry.add_recognizer(_MrnRecognizer())
    return analyzer


@lru_cache()
def _get_analyzer(model_name: str):
    try:
        analyzer = _build_analyzer(model_name)
        logger.info("PresidioScrubber initialized", extra={"model": model_name})
        return analyzer
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "PresidioScrubber initialization failed; ensure presidio-analyzer and spaCy model are installed."
        ) from exc


class PresidioScrubber(PHIScrubberPort):
    """Presidio-powered scrubber with IP allowlist filtering."""

    def __init__(self, model_name: str | None = None):
        self.nlp_backend = os.getenv("NLP_BACKEND", "spacy").lower()
        default_model = "en_core_sci_sm" if self.nlp_backend == "scispacy" else "en_core_web_sm"
        self.requested_model_name = model_name or os.getenv("PRESIDIO_NLP_MODEL", default_model)

        fallbacks_env = os.getenv("PRESIDIO_NLP_MODEL_FALLBACKS")
        if fallbacks_env is not None:
            fallback_models = [m.strip() for m in fallbacks_env.split(",") if m.strip()]
        else:
            fallback_models = ["en_core_web_sm", "en_core_web_md", "en_core_web_lg"]

        model_candidates = [self.requested_model_name] + [
            m for m in fallback_models if m != self.requested_model_name
        ]

        last_exc: RuntimeError | None = None
        for candidate in model_candidates:
            try:
                self._analyzer = _get_analyzer(candidate)
                self.model_name = candidate
                break
            except RuntimeError as exc:
                last_exc = exc

        if last_exc is not None and not hasattr(self, "_analyzer"):
            raise last_exc

        if self.model_name != self.requested_model_name:
            logger.warning(
                "Requested spaCy model unavailable; falling back",
                extra={"requested_model": self.requested_model_name, "fallback_model": self.model_name},
            )
        # Clinical procedure notes rarely contain driver license IDs, but the recognizer
        # often false-positives on device model tokens like "T190" bronchoscope models.
        self.enable_driver_license_recognizer = _env_flag("ENABLE_DRIVER_LICENSE_RECOGNIZER", False)

        self.score_thresholds = _parse_score_thresholds(os.getenv("PHI_ENTITY_SCORE_THRESHOLDS"))
        self.relative_datetime_phrases = tuple(
            p.strip()
            for p in os.getenv("PHI_DATE_TIME_RELATIVE_PHRASES", ",".join(DEFAULT_RELATIVE_DATE_TIME_PHRASES)).split(
                ","
            )
            if p.strip()
        )

        # Entity types to request from Presidio (used by the scrubber and audit CLI).
        entities: list[str] = [
            "PERSON",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "US_SSN",
            "LOCATION",
            "DATE_TIME",
            "MEDICAL_LICENSE",
            "MRN",
        ]
        if self.enable_driver_license_recognizer:
            entities.append("US_DRIVER_LICENSE")
        self.entities = entities

    def _analyze_detections(self, text: str) -> list[Detection]:
        results = self._analyzer.analyze(
            text=text,
            language="en",
            entities=self.entities,
        )
        detections: list[Detection] = []
        for r in results:
            detections.append(
                Detection(
                    entity_type=str(getattr(r, "entity_type")),
                    start=int(getattr(r, "start")),
                    end=int(getattr(r, "end")),
                    score=float(getattr(r, "score", 0.0) or 0.0),
                )
            )
        return detections

    def scrub_with_audit(
        self, text: str, document_type: str | None = None, specialty: str | None = None
    ) -> tuple[ScrubResult, dict[str, Any]]:
        raw = self._analyze_detections(text)
        return redact_with_audit(
            text=text,
            detections=raw,
            enable_driver_license_recognizer=self.enable_driver_license_recognizer,
            score_thresholds=self.score_thresholds,
            relative_datetime_phrases=self.relative_datetime_phrases,
            nlp_backend=self.nlp_backend,
            nlp_model=self.model_name,
            requested_nlp_model=self.requested_model_name,
        )

    def scrub(self, text: str, document_type: str | None = None, specialty: str | None = None) -> ScrubResult:
        scrub_result, _ = self.scrub_with_audit(text, document_type=document_type, specialty=specialty)
        return scrub_result


__all__ = ["PresidioScrubber"]
