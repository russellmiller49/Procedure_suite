"""Presidio-based scrubber adapter (Unified Clinical Context).

Implements PHIScrubberPort using Presidio AnalyzerEngine with enhanced
dynamic safeguards for clinical terms, providers, and HIPAA age rules.
Unified version combining scispacy integration and targeted false positive fixes.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from modules.phi.ports import PHIScrubberPort, ScrubResult, ScrubbedEntity

logger = logging.getLogger(__name__)

ZERO_WIDTH_CHARACTERS: frozenset[str] = frozenset(
    {
        "\u200b", "\u200c", "\u200d", "\u200e", "\u200f", "\u2060", "\ufeff"
    }
)
ZERO_WIDTH_TRANSLATION_TABLE: dict[int, int] = {ord(ch): ord(" ") for ch in ZERO_WIDTH_CHARACTERS}

# --- 1. Allow Lists (Terms to Protect) ---

# Pulmonary/Interventional terms often mistaken for Names/Orgs by NLP
PULMONARY_ALLOW_LIST = {
    # Robots & Navigation
    "ion", "monarch", "superdimension", "veran", "spin", "lungvision", "galaxy", "archimedes",
    # Valves & Stents
    "zephyr", "spiration", "aero", "ultraflex", "bonastent", "silicone", "dumon", "hood",
    # Catheters & Tools
    "alair", "pleurx", "pleura-x", "chartis", "prosense", "neuwave", "vizishot", 
    "olympus", "cre", "elation", "erbe", "erbokryo", "truefreeze", "cryoprobe",
    "fogarty", "freitag", "pneumostat", "monsoon",
    # Anatomy often mistaken for names
    "lingula", "carina", "hilum", "naris", "nares", "glottis", "epiglottis",
    # Clinical Acronyms/Terms
    "rose", "ebus", "rebus", "tbna", "bal", "gpa", "copd", "pap", "ip", "or",
    "severe", "moderate", "mild", "acute", "chronic", "for", "with" # Clinical stopwords
}

# --- 2. Dynamic Regex Configurations ---

# HIPAA Age Rule: Match ages >= 90.
AGE_OVER_90_RE = re.compile(
    r"(?i)(?:\b(?:age|aged)\s*[:]?\s*(?:9\d|[1-9]\d{2,})\b)|"
    r"(?:\b(?:9\d|[1-9]\d{2,})\s*-?\s*(?:y/o|y\.?o\.?|yo|yrs?|years?|year-old|year\s+old)\b)"
)

# Date of Birth (DOB) - Catches "DOB: 11/22/1971"
DOB_RE = re.compile(
    r"(?i)\b(?:DOB|Date\s*of\s*Birth)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"
)

# Structured Header Names (High Sensitivity)
# Handles CSV artifacts (newlines/quotes/pipes) and expanded roles (Operator, Staff, Fellow).
# Captures: "Patient: Jasmine Young", "Pt: Williams, Robert J.", "Operator: Dr. Smith"
STRUCTURED_PERSON_RE = re.compile(
    r"(?im)(?:^|[\r\n\"\|;])\s*(?:Patient(?:\s+Name)?|Pt|Name|Subject|Attending|Fellow|Surgeon|Physician|Assistants?|"
    r"RN|RT|CRNA|Cytology|Cytopathologist|Proceduralist|Operator|Resident|Anesthesia|Staff|Provider)\s*[:\-\|]+\s+"
    r"((?:Dr\.|Mr\.|Ms\.|Mrs\.|LCDR\.|CDR\.|Prof\.)?\s*[A-Z][a-z]+(?:[\s,]+(?:[A-Z]\.?|[A-Z][a-z]+)){1,4})"
)

# Narrative Provider/Dictation (Contextual)
# Catches "Dr. Smith performed..." or dictation starts like "Lisa Morgan here..."
NARRATIVE_PERSON_RE = re.compile(
    r"(?im)(?:\b(?:Dr\.|Doctor|LCDR|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?))|"  # Dr. Smith
    r"(?:^|[\r\n])\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s+(?:here|presents|presented|with|has|is|was|underwent)\b" # Dictation start
)

# Structured Location/Facility
# Catches "Facility: Lakeshore University Hospital", "Location: Bronchoscopy Suite"
STRUCTURED_LOCATION_RE = re.compile(
    r"(?im)(?:^|[\r\n\"\|;])\s*(?:Facility|Location|Hospital|Institution|Service|Center|Site)\s*[:\-\|]+\s+"
    r"([A-Z0-9][a-zA-Z0-9\s\.\,\-\&]+?)(?=\s{2,}|\n|$|Dr\.|Attending)"
)

# MRN / ID Values
MRN_RE = re.compile(
    r"(?i)\b(?:MRN|MR|Medical\s*Record|Medical\s*Rec(?:ord)?|Patient\s*ID|ID|EDIPI|DOD\s*ID)\s*[:\#]?\s*(\d{5,12})\b"
)

# Improved ROSE Context (To Identify Clinical Context vs Person)
_ROSE_CONTEXT_RE = re.compile(
    r"\bROSE(?:\s*(?:[-:]|from|said|result|report|findings?)\s*|\s+)"
    r"(?:suspicious|consistent|positive|negative|pos|neg|performed|"
    r"collected|sample|specimen|analysis|evaluation|procedure|review|findings?|"
    r"malignant|benign|adequate|inadequate|atypical|granuloma|granulomatous|"
    r"lymphocytes|cells|carcinoma|adeno|squamous|nsclc|scc|inflammation|inflammatory|maybe)\b",
    re.IGNORECASE,
)

# Device Context (To Protect names like "Noah" or "King" when part of a device)
_DEVICE_CONTEXT_RE = re.compile(
    r"\b(?:Noah|Wang|Cook|Mark|Baker|Young|King|Edwards|Ion|Monarch|Zephyr|Chartis|"
    r"Alair|PleurX|Fogarty|Freitag|Olympus|SuperDimension|Pneumostat|Monsoon|ViziShot|"
    r"TrueFreeze|ProSense|Neuwave|Erbokryo)\s+"
    r"(?:Medical|Needle|Catheter|EchoTip|Fiducial|Marker|System|Platform|Robot|Forceps|"
    r"Biopsy|Galaxy|Valve|Drain|Stent|Scope|Bronchoscope|Nav|Navigation|Probe|Generator|Ablation)\b",
    re.IGNORECASE,
)

@dataclass
class PresidioScrubber(PHIScrubberPort):
    """
    Adapter that uses Microsoft Presidio + Custom Regex for scrubbing.
    """
    analyzer: Any = None
    anonymizer: Any = None
    model_name: str = "presidio"

    def scrub(self, text: str, document_type: str | None = None, specialty: str | None = None) -> ScrubResult:
        if not text:
            return ScrubResult(scrubbed_text="", entities=[])

        # 1. Pre-process: Clean invisible chars
        clean_text = text.translate(ZERO_WIDTH_TRANSLATION_TABLE)
        
        # 2. Identify Protected Ranges (Allow List)
        # These are ranges that MUST NOT be redacted.
        protected_ranges = set()
        
        # A. Pulmonary Allow List (Exact words like "Ion", "Lingula")
        for term in PULMONARY_ALLOW_LIST:
            for match in re.finditer(r"\b" + re.escape(term) + r"\b", clean_text, re.IGNORECASE):
                protected_ranges.add((match.start(), match.end()))

        # B. ROSE Context protection (Protect "ROSE" when followed by clinical keywords)
        for match in _ROSE_CONTEXT_RE.finditer(clean_text):
            rose_match = re.search(r"\bROSE\b", match.group(0), re.IGNORECASE)
            if rose_match:
                # Add only the "ROSE" part to protected ranges
                start_offset = match.start() + rose_match.start()
                end_offset = match.start() + rose_match.end()
                protected_ranges.add((start_offset, end_offset))

        # C. Device Context protection (Protect "Noah" in "Noah Medical")
        for match in _DEVICE_CONTEXT_RE.finditer(clean_text):
            protected_ranges.add((match.start(), match.end()))

        # 3. Identify Redaction Candidates
        redaction_candidates = []

        # A. Strict Regexes (High Confidence)
        regex_map = [
            (MRN_RE, "ID"),
            (AGE_OVER_90_RE, "AGE_90+"),
            (DOB_RE, "DATE_TIME"),
            (STRUCTURED_PERSON_RE, "PERSON"),
            (NARRATIVE_PERSON_RE, "PERSON"),
            (STRUCTURED_LOCATION_RE, "LOCATION")
        ]
        
        for regex, label in regex_map:
            for match in regex.finditer(clean_text):
                # If the regex has capturing groups, use the first group
                if regex.groups > 0:
                    for i in range(1, regex.groups + 1):
                        span = match.span(i)
                        if span[0] != -1:
                            redaction_candidates.append((span[0], span[1], label))
                else:
                    redaction_candidates.append((match.start(), match.end(), label))

        # B. Presidio Analyzer (Fallback)
        # Analyze for standard entities if analyzer is configured
        if self.analyzer:
            presidio_results = self.analyzer.analyze(
                text=clean_text,
                entities=["PERSON", "LOCATION", "ORGANIZATION", "DATE_TIME"],
                language="en"
            )
            for res in presidio_results:
                redaction_candidates.append((res.start, res.end, res.entity_type))

        # 4. Filter Redactions vs Protected Ranges
        final_redactions = []
        
        for start, end, label in redaction_candidates:
            is_protected = False
            
            # Check for overlap with protected ranges
            for p_start, p_end in protected_ranges:
                if start < p_end and end > p_start:
                    is_protected = True
                    break
            
            # Check if the text itself is in the allow list (e.g. "Severe")
            if not is_protected:
                text_segment = clean_text[start:end].lower()
                if text_segment in PULMONARY_ALLOW_LIST:
                    is_protected = True

            if not is_protected:
                final_redactions.append((start, end, label))

        # 5. Apply Redactions (Reverse order)
        # Deduplicate and sort
        final_redactions = sorted(list(set(final_redactions)), key=lambda x: x[0], reverse=True)
        
        scrubbed_text_list = list(clean_text)
        scrubbed_entities: list[ScrubbedEntity] = []
        
        last_start = len(clean_text) + 1
        
        for start, end, label in final_redactions:
            # Avoid applying overlapping redactions
            if end > last_start:
                continue

            replacement = f"<{label}>"
            scrubbed_text_list[start:end] = replacement
            
            # Store entity information
            scrubbed_entities.append(ScrubbedEntity(
                placeholder=replacement,
                entity_type=label,
                original_start=start,
                original_end=end
            ))
            last_start = start

        # Reverse entities list to match forward order in text
        scrubbed_entities.reverse()

        return ScrubResult(
            scrubbed_text="".join(scrubbed_text_list),
            entities=scrubbed_entities
        )