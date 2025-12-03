from pydantic import BaseModel
from typing import List
from .envelope_models import EvidenceSpan

class ReasoningFields(BaseModel):
    trigger_phrases: List[str] = []
    evidence_spans: List[EvidenceSpan] = []
    coding_rationale: str = ""
    bundling_rationale: str = ""
    rule_paths: List[str] = []
    confidence: float = 0.0
    mer_notes: str = ""
    ncci_notes: str = ""
    confounders_checked: List[str] = []
