from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class Segment(BaseModel):
    """A segmented portion of the note with optional character spans."""
    type: str
    text: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    spans: Optional[List[Any]] = None

class Entity(BaseModel):
    """An entity extracted from the note, such as a station or stent."""
    name: str
    type: str
    attributes: Optional[Dict[str, Any]] = None

class Trace(BaseModel):
    """Trace metadata capturing what triggered an agent's output."""
    trigger_phrases: List[str] = []
    rule_paths: List[str] = []
    confounders_checked: List[str] = []
    confidence: float = 0.0

class ParserIn(BaseModel):
    note_id: str
    raw_text: str

class ParserOut(BaseModel):
    segments: List[Segment]
    entities: List[Entity]
    trace: Trace

class SummarizerIn(BaseModel):
    parser_out: ParserOut

class SummarizerOut(BaseModel):
    summaries: Dict[str, str]
    trace: Trace

class StructurerIn(BaseModel):
    summarizer_out: SummarizerOut

class StructurerOut(BaseModel):
    registry: Dict[str, Any]
    codes: List[Any]
    rationale: Dict[str, Any]
    trace: Trace
