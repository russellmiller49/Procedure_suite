# Unified Extraction Quality Improvement Plan

**Generated:** February 4, 2026  
**Branch:** `updates_2_3_26` @ `b4429e3`  
**Status:** Ready for implementation

---

## Executive Summary

This plan synthesizes five separate improvement proposals into a prioritized, coherent implementation roadmap. The core strategy follows the **"Model First, Rules Second"** hierarchy:

1. **NER (BiomedBERT)**: Primary extractor (speed + context)
2. **Deterministic/Regex**: Safety net / recovery mechanism (recall)  
3. **LLM (Judge)**: Tie-breaker / self-corrector (reasoning)

The plan is organized into:
- **Phase 1**: High-impact, low-effort guardrails (immediate wins)
- **Phase 2**: Architecture refinements (control flow fixes)
- **Phase 3**: Model maturity (NER schema expansion)
- **Phase 4**: Data quality loop (span-level annotation)

---

## Implementation Priorities

| Priority | Improvement | Impact | Effort | Files Affected |
|----------|------------|--------|--------|----------------|
| **1** | Template Checkbox Negation | 🔴 Critical | Low | `masking.py`, new module |
| **2** | Section-Aware Filtering | 🔴 Critical | Low | `section_filter.py` (new), `label_hydrator.py` |
| **3** | Airway Stent Assessment-Only | 🔴 Critical | Medium | `procedure_extractor.py`, `deterministic_extractors.py`, `verifier.py` |
| **4** | Evidence-Required Enforcement | 🟠 High | Medium | `verifier.py` |
| **5** | Unified Masking Pipeline | 🟠 High | Low | `registry_service.py` |
| **6** | EBUS "Site #" Block Parsing | 🟠 High | Medium | `postprocess.py` |
| **7** | Navigation Target Parsing | 🟠 High | Medium | `navigation_targets.py`, `registry_service.py` |
| **8** | Contextual Negation for Keywords | 🟡 Medium | Low | `label_hydrator.py` |
| **9** | Auto-populate Keyword Guard | 🟡 Medium | Medium | new generator script |
| **10** | Deterministic Evidence Spans | 🟡 Medium | Medium | `deterministic_extractors.py` |
| **11** | Header-CPT Recovery | 🟡 Medium | Low | `registry_service.py` |
| **12** | Granular NER Schema Expansion | 🟢 Long-term | High | `entity_types.py`, training pipeline |
| **13** | Span-Level Diamond Loop | 🟢 Long-term | High | Prodigy scripts |

---

## Phase 1: Immediate Guardrails (Week 1)

### 1.1 Template Checkbox Negation — PRIORITY 1

**Problem:** EMR templates with unchecked options (`0- Item`, `[ ] Item`) cause hallucinated `performed=True` flags.

**Solution:** Promote existing hotfix logic into production pipeline.

#### Codex Instructions

**Create new module:** `app/registry/postprocess/template_checkbox_negation.py`

```python
"""
Template checkbox negation - eliminates false positives from EMR checkbox templates.

EMR templates often include unchecked options as:
- "0- Chest tube"
- "[ ] Tunneled Pleural Catheter"  
- "☐ IPC placed"

These must NOT trigger performed=True.
"""

from __future__ import annotations
import re
from typing import List, Tuple
from app.registry.schema import RegistryRecord

# Patterns that indicate UNCHECKED/NOT PERFORMED
UNCHECKED_PATTERNS = [
    r"^\s*0\s*[-–—]\s*",           # "0- Item" or "0 - Item"
    r"^\s*\[\s*\]\s*",             # "[ ] Item"  
    r"^\s*\(\s*\)\s*",             # "( ) Item"
    r"^\s*[☐□]\s*",                # Unicode checkbox symbols
]

# Map of text patterns to registry paths that should be negated
# Add HIGH-IMPACT items that commonly appear in checkbox templates
CHECKBOX_NEGATION_MAP = {
    r"(?i)chest\s*tube": [
        "pleural_procedures.chest_tube.performed",
    ],
    r"(?i)tunneled\s*pleural\s*catheter|(?i)\bIPC\b|(?i)indwelling\s*pleural": [
        "pleural_procedures.ipc.performed",
    ],
    r"(?i)pneumothorax": [
        "complications.pneumothorax",
    ],
    r"(?i)airway\s*stent": [
        "procedures_performed.airway_stent.performed",
    ],
    r"(?i)airway\s*dilation|(?i)balloon\s*dilation": [
        "procedures_performed.airway_dilation.performed",
    ],
    r"(?i)rigid\s*bronch": [
        "procedures_performed.rigid_bronchoscopy.performed",
    ],
    r"(?i)cryotherapy|(?i)cryobiopsy": [
        "procedures_performed.transbronchial_cryobiopsy.performed",
    ],
    r"(?i)thermal\s*ablation|(?i)electrocautery|(?i)APC": [
        "procedures_performed.thermal_ablation.performed",
    ],
}

def _is_unchecked_line(line: str) -> bool:
    """Check if line starts with an unchecked checkbox pattern."""
    for pattern in UNCHECKED_PATTERNS:
        if re.match(pattern, line):
            return True
    return False

def _extract_unchecked_items(note_text: str) -> List[str]:
    """Extract all items from unchecked checkbox lines."""
    unchecked_items = []
    for line in note_text.split("\n"):
        if _is_unchecked_line(line):
            # Strip the checkbox prefix and get the item text
            cleaned = line
            for pattern in UNCHECKED_PATTERNS:
                cleaned = re.sub(pattern, "", cleaned, count=1)
            cleaned = cleaned.strip()
            if cleaned:
                unchecked_items.append(cleaned.lower())
    return unchecked_items

def _set_nested_path(record_dict: dict, path: str, value: any) -> bool:
    """Set a nested dictionary value by dot-notation path. Returns True if changed."""
    parts = path.split(".")
    current = record_dict
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    
    final_key = parts[-1]
    if current.get(final_key) != value:
        current[final_key] = value
        return True
    return False

def apply_template_checkbox_negation(
    note_text: str, 
    record: RegistryRecord
) -> Tuple[RegistryRecord, List[str]]:
    """
    Suppress performed flags that appear as unchecked items in EMR templates.
    
    Args:
        note_text: Raw clinical note text
        record: RegistryRecord after extraction
        
    Returns:
        Tuple of (modified_record, list_of_corrections_applied)
    """
    corrections = []
    unchecked_items = _extract_unchecked_items(note_text)
    
    if not unchecked_items:
        return record, corrections
    
    record_dict = record.model_dump()
    
    # Check each item pattern against unchecked items
    for item_pattern, registry_paths in CHECKBOX_NEGATION_MAP.items():
        for unchecked in unchecked_items:
            if re.search(item_pattern, unchecked, re.IGNORECASE):
                for path in registry_paths:
                    # Check if currently set to True
                    parts = path.split(".")
                    current = record_dict
                    try:
                        for part in parts[:-1]:
                            current = current.get(part, {})
                        if current.get(parts[-1]) is True:
                            _set_nested_path(record_dict, path, False)
                            corrections.append(
                                f"CHECKBOX_NEGATION: {path} → False (unchecked: '{unchecked}')"
                            )
                    except (KeyError, TypeError, AttributeError):
                        continue
    
    if corrections:
        return RegistryRecord(**record_dict), corrections
    return record, corrections
```

**Integrate into pipeline:** Modify `app/registry/application/registry_service.py`

In `_extract_fields_extraction_first()`, add after extraction but before CPT derivation:

```python
from app.registry.postprocess.template_checkbox_negation import (
    apply_template_checkbox_negation
)

# ... existing extraction code ...

# Apply template checkbox negation BEFORE CPT derivation
record, checkbox_corrections = apply_template_checkbox_negation(raw_note_text, record)
if checkbox_corrections:
    warnings.extend(checkbox_corrections)
```

**Extend masking to strip checkbox lines:** Modify `app/registry/processing/masking.py`

Add to `mask_extraction_noise()`:

```python
# Strip unchecked checkbox lines (they're noise, not procedures)
UNCHECKED_LINE_PATTERNS = [
    r"^\s*0\s*[-–—]\s*[A-Za-z].*$",      # "0- Item..."
    r"^\s*\[\s*\]\s*[A-Za-z].*$",        # "[ ] Item..."
    r"^\s*\(\s*\)\s*[A-Za-z].*$",        # "( ) Item..."
]
for pattern in UNCHECKED_LINE_PATTERNS:
    text = re.sub(pattern, "", text, flags=re.MULTILINE)
```

#### Tests to Add

```python
# tests/registry/test_template_checkbox_negation.py

def test_unchecked_chest_tube_negated():
    """0- Chest tube should NOT trigger chest_tube.performed=True."""
    note = """
    Procedure: Bronchoscopy
    0- Chest tube
    1- Thoracentesis performed
    """
    record = RegistryRecord(
        pleural_procedures={"chest_tube": {"performed": True}}
    )
    result, corrections = apply_template_checkbox_negation(note, record)
    assert result.pleural_procedures.chest_tube.performed is False
    assert len(corrections) == 1

def test_checked_item_preserved():
    """1- Item (checked) should NOT be negated."""
    note = "1- Chest tube placed"
    record = RegistryRecord(
        pleural_procedures={"chest_tube": {"performed": True}}
    )
    result, corrections = apply_template_checkbox_negation(note, record)
    assert result.pleural_procedures.chest_tube.performed is True
    assert len(corrections) == 0
```

---

### 1.2 Section-Aware Filtering — PRIORITY 2

**Problem:** "History of stent placement" triggers `airway_stent.performed=True` because extractors don't distinguish procedural sections from History/Plan sections.

**Solution:** Filter text to remove History/Plan/Assessment before extraction.

#### Codex Instructions

**Create new module:** `ml/lib/ml_coder/section_filter.py`

```python
"""
Section filtering utilities to prevent 'context bleeding' in extraction.

Filters out non-procedural sections (History, Plan, Indications) so extractors
only see what actually happened during the procedure.
"""

from __future__ import annotations
from typing import List, Set

# Sections that definitively describe the current procedure action
PROCEDURE_SECTIONS: Set[str] = {
    "PROCEDURE",
    "PROCEDURE IN DETAIL",
    "DESCRIPTION OF PROCEDURE",
    "OPERATIVE REPORT",
    "FINDINGS",
    "TECHNIQUE",
    "INTERVENTION",
    "BRONCHOSCOPY",
    "DETAILS",
    "PROCEDURE DETAILS",
    "PROCEDURE PERFORMED",
}

# Sections that describe past events or future plans (HIGH RISK for False Positives)
EXCLUDE_SECTIONS: Set[str] = {
    "HISTORY",
    "HISTORY OF PRESENT ILLNESS",
    "HPI",
    "PAST MEDICAL HISTORY",
    "PMH",
    "INDICATION",
    "INDICATIONS",
    "REASON FOR EXAM",
    "REASON FOR PROCEDURE",
    "ASSESSMENT",
    "PLAN",
    "RECOMMENDATIONS",
    "IMPRESSION",
    "CONCLUSION",
    "DISPOSITION",
    "FOLLOW UP",
    "FOLLOW-UP",
    "MEDICATIONS",
    "ALLERGIES",
    "SOCIAL HISTORY",
    "FAMILY HISTORY",
}

def extract_procedural_text(note_text: str) -> str:
    """
    Extract only procedure-relevant sections to prevent History/Plan contamination.
    
    Args:
        note_text: Raw clinical note text.
        
    Returns:
        String containing only the relevant sections (headers preserved).
        If no headers are found or parsing fails, returns the full text (fail-safe).
    """
    try:
        from app.common.sectionizer import SectionizerService
    except ImportError:
        return note_text

    if not note_text or not note_text.strip():
        return ""

    sectionizer = SectionizerService()
    sections = sectionizer.sectionize(note_text)
    
    # If no sections detected, return full text to be safe
    if not sections:
        return note_text

    procedural_parts: List[str] = []
    has_procedure_section = False

    for section in sections:
        header = (section.get("header") or "").upper().strip()
        text = section.get("text", "")
        
        # 1. Explicit Inclusion: If it's a known procedure header, keep it
        if any(p in header for p in PROCEDURE_SECTIONS):
            procedural_parts.append(f"{header}\n{text}")
            has_procedure_section = True
            continue
            
        # 2. Explicit Exclusion: If it's a known non-proc header, skip it
        if any(e in header for e in EXCLUDE_SECTIONS):
            continue
            
        # 3. Neutral/Unknown sections: Keep them
        # Many notes have unstructured paragraphs that contain vital info
        procedural_parts.append(f"{header}\n{text}")

    # Safety net: if we filtered EVERYTHING out (rare), return original
    if not procedural_parts:
        return note_text

    return "\n\n".join(procedural_parts)


def is_in_excluded_section(text: str, match_start: int, match_end: int) -> bool:
    """
    Check if a regex match falls within an excluded section.
    
    This is a lightweight alternative when you need to check individual matches
    without filtering the entire text.
    """
    try:
        from app.common.sectionizer import SectionizerService
    except ImportError:
        return False
    
    sectionizer = SectionizerService()
    sections = sectionizer.sectionize(text)
    
    for section in sections:
        header = (section.get("header") or "").upper().strip()
        section_start = section.get("start", 0)
        section_end = section.get("end", len(text))
        
        # Check if match is within this section
        if section_start <= match_start < section_end:
            # Check if it's an excluded section
            if any(e in header for e in EXCLUDE_SECTIONS):
                return True
            return False
    
    return False
```

**Update label_hydrator.py:** Modify `ml/lib/ml_coder/label_hydrator.py`

```python
# Add import at top
from ml.lib.ml_coder.section_filter import extract_procedural_text

# In hydrate_labels_from_text function, add section filtering:
def hydrate_labels_from_text(note_text: str) -> Dict[str, int]:
    """
    Hydrate registry labels from text using keyword patterns.
    
    NOW UPDATED: Applies section filtering first to remove History/Plan.
    """
    labels = {}
    
    # 1. Filter text to remove History/Plan noise
    focused_text = extract_procedural_text(note_text)
    
    # 2. Run regex patterns on the FOCUSED text
    for pattern, matches in KEYWORD_TO_PROCEDURE_MAP.items():
        if re.search(pattern, focused_text, re.IGNORECASE):
            for field, confidence in matches:
                labels[field] = 1
                
    return labels
```

#### Test to Add

```python
def test_history_stent_not_extracted():
    """'History of stent placement' should NOT trigger airway_stent."""
    note = """
    History: Patient had a stent placed in 2024.
    
    Procedure: Bronchoscopy with inspection.
    The airways were patent. No interventions performed.
    """
    labels = hydrate_labels_from_text(note)
    assert labels.get("airway_stent", 0) == 0
```

---

### 1.3 Airway Stent Assessment-Only — PRIORITY 3

**Problem:** Notes with "stent in good position" / "stent well-seated" incorrectly derive stent placement CPT (31636) when no intervention occurred.

**Solution:** Distinguish stent assessment/surveillance from actual placement/removal.

#### Codex Instructions

**Update `app/registry/ner_mapping/procedure_extractor.py`:**

Add stent decision logic:

```python
# Add these patterns near the top of the file
STENT_INTERVENTION_VERBS = re.compile(
    r"(?i)\b(place[ds]?|deploy[eds]?|insert[eds]?|position[eds]?|"
    r"remove[ds]?|retriev[eds]?|exchange[ds]?|revis[eding]?|"
    r"reposition[eds]?|adjust[eds]?|extract[eds]?)\b"
)

STENT_ASSESSMENT_PATTERNS = [
    r"(?i)stent.{0,30}(well[-\s]?seated|in\s+good\s+position|appropriate\s+position|patent|intact|stable)",
    r"(?i)(assessment|reassessment|inspection|surveillance|evaluation).{0,40}stent",
    r"(?i)stent.{0,20}(visualized|inspected|examined|seen)",
]

def _classify_stent_context(text: str, stent_span_start: int, stent_span_end: int) -> str:
    """
    Classify whether stent mention indicates intervention vs assessment.
    
    Returns: 'intervention', 'assessment', or 'unknown'
    """
    # Get context window around stent mention
    window_start = max(0, stent_span_start - 150)
    window_end = min(len(text), stent_span_end + 150)
    context = text[window_start:window_end]
    
    # Check for intervention verbs
    if STENT_INTERVENTION_VERBS.search(context):
        return "intervention"
    
    # Check for assessment patterns
    for pattern in STENT_ASSESSMENT_PATTERNS:
        if re.search(pattern, context):
            return "assessment"
    
    return "unknown"
```

**Update `app/registry/deterministic/deterministic_extractors.py`:**

Add `extract_airway_stent()` function:

```python
def extract_airway_stent(text: str) -> dict:
    """
    Extract airway stent information with assessment-only detection.
    
    Returns dict with:
    - performed: bool
    - action: 'Placement' | 'Removal' | 'Revision' | 'Assessment only' | None
    - airway_stent_removal: bool
    """
    result = {
        "airway_stent": {
            "performed": False,
            "action": None,
        },
        "airway_stent_removal": False,
    }
    
    # Look for any stent mention
    stent_pattern = r"(?i)\b(stent|y-?stent|silicone\s*stent|metallic\s*stent)\b"
    stent_matches = list(re.finditer(stent_pattern, text))
    
    if not stent_matches:
        return result
    
    # Check for explicit placement/deployment
    placement_patterns = [
        r"(?i)stent.{0,40}(placed|deployed|inserted|positioned)",
        r"(?i)(place[ds]?|deploy[eds]?|insert[eds]?).{0,40}stent",
    ]
    
    # Check for explicit removal
    removal_patterns = [
        r"(?i)stent.{0,40}(removed|retrieved|extracted|explanted)",
        r"(?i)(remove[ds]?|retriev[eds]?|extract[eds]?).{0,40}stent",
    ]
    
    # Check for revision/repositioning
    revision_patterns = [
        r"(?i)stent.{0,40}(repositioned|adjusted|revised)",
        r"(?i)(reposition|adjust|revis[eding]).{0,40}stent",
    ]
    
    # Check for assessment-only
    assessment_patterns = [
        r"(?i)stent.{0,30}(well[-\s]?seated|in\s+good\s+position|appropriate|patent|intact|stable)",
        r"(?i)(assessment|surveillance|inspection|examination).{0,40}stent",
        r"(?i)stent.{0,30}(visualized|inspected|examined)",
    ]
    
    has_placement = any(re.search(p, text) for p in placement_patterns)
    has_removal = any(re.search(p, text) for p in removal_patterns)
    has_revision = any(re.search(p, text) for p in revision_patterns)
    has_assessment = any(re.search(p, text) for p in assessment_patterns)
    
    if has_placement:
        result["airway_stent"]["performed"] = True
        result["airway_stent"]["action"] = "Placement"
    elif has_removal:
        result["airway_stent"]["performed"] = True
        result["airway_stent"]["action"] = "Removal"
        result["airway_stent_removal"] = True
    elif has_revision:
        result["airway_stent"]["performed"] = True
        result["airway_stent"]["action"] = "Revision"
    elif has_assessment and stent_matches:
        # Stent present/assessed but no intervention
        result["airway_stent"]["performed"] = True
        result["airway_stent"]["action"] = "Assessment only"
    
    return result
```

**Update verifier.py safety net:** In `app/registry/evidence/verifier.py`:

```python
def _verify_stent_action(record_dict: dict, text: str) -> list[str]:
    """
    Verify stent action is appropriate - downgrade to Assessment if needed.
    """
    corrections = []
    stent_data = record_dict.get("procedures_performed", {}).get("airway_stent", {})
    
    if not stent_data.get("performed"):
        return corrections
    
    action = stent_data.get("action")
    
    # If action is Placement but no placement evidence, check for assessment
    if action == "Placement":
        from app.registry.deterministic.deterministic_extractors import extract_airway_stent
        det_result = extract_airway_stent(text)
        det_action = det_result.get("airway_stent", {}).get("action")
        
        if det_action == "Assessment only":
            stent_data["action"] = "Assessment only"
            corrections.append("STENT_DOWNGRADED_TO_ASSESSMENT_ONLY: No placement evidence found")
    
    return corrections
```

#### Tests to Add

```python
def test_stent_assessment_only():
    """'Stent well-seated' should set action='Assessment only'."""
    note = "The previously placed stent was well-seated and patent."
    result = extract_airway_stent(note)
    assert result["airway_stent"]["performed"] is True
    assert result["airway_stent"]["action"] == "Assessment only"
    assert result["airway_stent_removal"] is False

def test_stent_placement():
    """'Stent deployed' should set action='Placement'."""
    note = "A 14x10x10mm silicone Y-stent was deployed in the trachea."
    result = extract_airway_stent(note)
    assert result["airway_stent"]["performed"] is True
    assert result["airway_stent"]["action"] == "Placement"
```

---

## Phase 2: Architecture Refinements (Weeks 2-3)

### 2.1 Unified Masking Pipeline — PRIORITY 5

**Problem:** Multiple entry points use different masking strategies, causing inconsistent extraction.

**Solution:** Make `mask_extraction_noise()` the single source of truth with fallback.

#### Codex Instructions

**Update `app/registry/application/registry_service.py`:**

In `run_with_warnings()` and `_extract_fields_extraction_first()`:

```python
from app.registry.processing.masking import mask_extraction_noise, mask_offset_preserving

def _get_masked_text(raw_text: str) -> str:
    """
    Get masked text using aggressive noise removal with fallback.
    """
    masked = mask_extraction_noise(raw_text)
    
    # Fallback: if masking removed too much, use lighter masking
    # Check for procedural content indicators
    procedural_verbs = r"(?i)\b(performed|placed|inserted|removed|biopsied|aspirated)\b"
    if not re.search(procedural_verbs, masked) and re.search(procedural_verbs, raw_text):
        # Aggressive masking removed procedural content - fall back
        masked = mask_offset_preserving(raw_text)
    
    return masked
```

### 2.2 Evidence-Required Enforcement — PRIORITY 4

**Problem:** `performed=True` flags can be set without supporting evidence, leading to hallucinations.

**Solution:** Require evidence spans for high-risk performed flags.

#### Codex Instructions

**Update `app/registry/evidence/verifier.py`:**

```python
# Add evidence-required policy
EVIDENCE_REQUIRED_PATHS = {
    "procedures_performed.airway_stent.performed": "HARD",
    "procedures_performed.airway_dilation.performed": "HARD", 
    "procedures_performed.rigid_bronchoscopy.performed": "HARD",
    "pleural_procedures.chest_tube.performed": "HARD",
    "pleural_procedures.ipc.performed": "HARD",
    # Add more as needed
}

def enforce_evidence_requirements(
    record_dict: dict, 
    evidence_dict: dict,
    policy: str = "HARD"  # or "REVIEW"
) -> tuple[dict, list[str]]:
    """
    Enforce evidence requirements for high-risk performed flags.
    
    Args:
        record_dict: The registry record as dict
        evidence_dict: Evidence spans keyed by path
        policy: "HARD" = set to False, "REVIEW" = add warning only
        
    Returns:
        Tuple of (modified_record, list_of_changes)
    """
    changes = []
    
    for path, required_policy in EVIDENCE_REQUIRED_PATHS.items():
        if required_policy != policy:
            continue
            
        # Check if flag is True
        parts = path.split(".")
        current = record_dict
        try:
            for part in parts[:-1]:
                current = current.get(part, {})
            if current.get(parts[-1]) is not True:
                continue
        except (KeyError, TypeError):
            continue
        
        # Check for evidence
        has_evidence = path in evidence_dict and evidence_dict[path]
        
        if not has_evidence:
            if policy == "HARD":
                # Set to False
                current[parts[-1]] = False
                changes.append(f"EVIDENCE_REQUIRED: {path} → False (no evidence)")
            else:
                changes.append(f"EVIDENCE_REVIEW_NEEDED: {path} has no evidence")
    
    return record_dict, changes
```

### 2.3 EBUS "Site #" Block Parsing — PRIORITY 6

**Problem:** EBUS notes with "Site 1: station 11Rs" where sampling appears on subsequent lines incorrectly mark stations as `inspected_only`.

**Solution:** Parse "Site #" blocks as units and apply sampling evidence within the block.

#### Codex Instructions

**Update `app/registry/processing/linear_ebus_stations_detail.py` or create new postprocessor:**

```python
import re
from typing import Dict, List, Tuple

SITE_BLOCK_PATTERN = re.compile(r"(?im)^\s*Site\s*\d+\s*:", re.MULTILINE)
STATION_TOKEN_PATTERN = re.compile(r"\b(2[LR]?|4[LR]|7|8|9|10[LR]|11[LR]s?|12[LR]?)\b", re.IGNORECASE)
SAMPLING_INDICATORS = re.compile(
    r"(?i)\b(needle|tbna|fna|sampled|passes|biopsies?|aspirat[eding]|core|forceps)\b"
)
NEGATION_PATTERN = re.compile(
    r"(?i)\b(not\s+biopsied|not\s+sampled|no\s+sampling|deferred)\b"
)

def parse_ebus_site_blocks(text: str) -> List[Dict]:
    """
    Parse EBUS narrative into site blocks.
    
    Returns list of dicts with:
    - block_text: str
    - station: str or None
    - has_sampling: bool
    - has_negation: bool
    """
    blocks = []
    
    # Split by Site # headers
    matches = list(SITE_BLOCK_PATTERN.finditer(text))
    
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block_text = text[start:end]
        
        # Extract station from first line
        station_match = STATION_TOKEN_PATTERN.search(block_text[:200])
        station = station_match.group(1).upper() if station_match else None
        
        # Check for sampling indicators anywhere in block
        has_sampling = bool(SAMPLING_INDICATORS.search(block_text))
        has_negation = bool(NEGATION_PATTERN.search(block_text))
        
        blocks.append({
            "block_text": block_text,
            "station": station,
            "has_sampling": has_sampling,
            "has_negation": has_negation,
        })
    
    return blocks


def reconcile_ebus_from_site_blocks(
    node_events: List[dict],
    text: str
) -> Tuple[List[dict], List[str]]:
    """
    Upgrade node_events based on site block analysis.
    """
    corrections = []
    blocks = parse_ebus_site_blocks(text)
    
    # Build station -> sampling lookup
    station_sampling = {}
    for block in blocks:
        if block["station"] and block["has_sampling"] and not block["has_negation"]:
            station_sampling[block["station"]] = block["block_text"][:280]
    
    # Upgrade inspected_only stations that have sampling evidence
    for event in node_events:
        station = event.get("station")
        action = event.get("action")
        
        if station in station_sampling and action == "inspected_only":
            event["action"] = "needle_aspiration"
            event["evidence_quote"] = station_sampling[station]
            corrections.append(
                f"EBUS_SITE_BLOCK_UPGRADE: {station} inspected_only → needle_aspiration"
            )
    
    return node_events, corrections
```

---

## Phase 3: Model Maturity (Weeks 3-4)

### 3.1 Contextual Negation for Keywords — PRIORITY 8

**Problem:** Keyword hydration is binary - "stent in good position" triggers stent even though it's not an intervention.

#### Codex Instructions

**Update `ml/lib/ml_coder/label_hydrator.py`:**

```python
# Add negation contexts near top of file
NEGATION_CONTEXTS = {
    "airway_stent": [
        r"(?i)stent\s+(in\s+)?(good|stable|appropriate)\s+position",
        r"(?i)stent\s+(patent|intact|well[-\s]?seated)",
        r"(?i)(possible|consider|may\s+need)\s+stent",
        r"(?i)history\s+of\s+stent",
        r"(?i)previous\s+stent",
    ],
    "chest_tube": [
        r"(?i)d/?c\s+chest\s+tube",
        r"(?i)remove\s+chest\s+tube",
        r"(?i)chest\s+tube\s+(to\s+be\s+)?removed",
    ],
    "airway_dilation": [
        r"(?i)no\s+(need\s+for\s+)?dilation",
        r"(?i)dilation\s+not\s+(required|needed|indicated)",
    ],
}

def _is_negated(field: str, text: str, match_start: int, match_end: int) -> bool:
    """Check if a keyword match is negated by context."""
    if field not in NEGATION_CONTEXTS:
        return False
    
    # Check context window
    window_start = max(0, match_start - 100)
    window_end = min(len(text), match_end + 100)
    context = text[window_start:window_end]
    
    for neg_pattern in NEGATION_CONTEXTS[field]:
        if re.search(neg_pattern, context):
            return True
    
    return False
```

### 3.2 Auto-populate Keyword Guard — PRIORITY 9

**Problem:** Self-correction skipped due to "no keywords configured" for some CPT codes.

#### Codex Instructions

**Create script:** `ops/tools/generate_cpt_keywords.py`

```python
#!/usr/bin/env python3
"""
Generate CPT_KEYWORDS from KB synonyms and deterministic mappings.

This ensures every code that can be emitted has keywords for the self-correction guard.
"""

import json
from pathlib import Path

def load_kb_synonyms(kb_path: Path) -> dict:
    """Load synonym lists from knowledge base."""
    # Implementation depends on your KB structure
    pass

def load_deterministic_mappings() -> dict:
    """Load codes from deterministic mapping rules."""
    # Scan app/domain/coding_rules/ for code mappings
    pass

def generate_keywords():
    """Generate CPT_KEYWORDS dict."""
    keywords = {}
    
    # From KB synonyms
    synonyms = load_kb_synonyms(Path("data/knowledge/"))
    for cpt, terms in synonyms.items():
        keywords[cpt] = list(set(terms))
    
    # From deterministic mappings
    mappings = load_deterministic_mappings()
    for cpt, terms in mappings.items():
        if cpt in keywords:
            keywords[cpt].extend(terms)
            keywords[cpt] = list(set(keywords[cpt]))
        else:
            keywords[cpt] = terms
    
    return keywords

if __name__ == "__main__":
    keywords = generate_keywords()
    output_path = Path("data/ml_training/cpt_keywords_generated.json")
    with open(output_path, "w") as f:
        json.dump(keywords, f, indent=2)
    print(f"Generated {len(keywords)} CPT keyword entries")
```

---

## Phase 4: Data Quality Loop (Ongoing)

### 4.1 Span-Level Diamond Loop — PRIORITY 13

**Problem:** Current Prodigy loop uses textcat (document classification), which doesn't teach the model *where* evidence is.

**Solution:** Create span-level annotation workflow using `ner_manual`.

#### Russell's Manual Tasks

1. **Create bootstrap script:** `ml/scripts/bootstrap_granular_attributes.py`
   - Use regex to pre-highlight entities like:
     - `DEV_STENT_TYPE`: silicone, hybrid, metallic, covered, uncovered
     - `DEV_STENT_DIM`: 14x10x10mm, 14x40mm
     - `NODULE_SIZE`: 14mm, 2.5cm
     - `OBS_VAL_PRE`: 90% occlusion, near complete obstruction
     - `OBS_VAL_POST`: patent, widely open

2. **Run Prodigy ner_manual:**
   ```bash
   prodigy ner.manual granular_ner_v1 blank:en \
     data/ml_training/granular_ner/silver_attributes.jsonl \
     --label DEV_STENT_TYPE,DEV_STENT_DIM,NODULE_SIZE,OBS_VAL_PRE,OBS_VAL_POST
   ```

3. **Review ~100-200 notes** - fix boundaries, reject false positives

4. **Export and merge with existing NER data:**
   ```bash
   prodigy db-out granular_ner_v1 > data/ml_training/granular_ner/gold_attributes.jsonl
   ```

5. **Retrain NER:**
   ```bash
   python ml/scripts/convert_spans_to_bio.py --input merged_ner_data.jsonl
   python ml/scripts/train_registry_ner.py
   ```

---

## Validation Checklist

### Smoke Tests

```bash
# Test section filtering
python ops/tools/registry_pipeline_smoke.py --text "History: Patient had stent placed in 2024. Procedure: Bronchoscopy with inspection."
# Expected: airway_stent.performed=False OR action="Assessment only"

# Test checkbox negation  
python ops/tools/registry_pipeline_smoke.py --text "0- Chest tube
1- Thoracentesis performed"
# Expected: chest_tube.performed=False, thoracentesis.performed=True

# Test stent assessment
python ops/tools/registry_pipeline_smoke.py --note tests/fixtures/notes/note_068.txt
# Expected: airway_stent.action="Assessment only", NO 31636 derived
```

### Regression Tests

```bash
make test
# Ensure all existing tests pass

# Run batch evaluation
python ops/tools/registry_pipeline_smoke_batch.py --fixtures tests/fixtures/notes/
```

---

## Summary: Implementation Order

| Week | Tasks | Owner |
|------|-------|-------|
| **Week 1** | Priorities 1-3: Checkbox negation, Section filtering, Stent assessment | Codex |
| **Week 1** | Create tests, run smoke validation | Russell |
| **Week 2** | Priorities 4-6: Evidence enforcement, Unified masking, EBUS blocks | Codex |
| **Week 2** | Review and merge PRs | Russell |
| **Week 3** | Priorities 7-9: Navigation parsing, Contextual negation, Keyword guard | Codex |
| **Week 3** | Run batch evaluation, identify remaining issues | Russell |
| **Week 4+** | Priorities 10-13: Evidence spans, Header-CPT, NER expansion, Diamond loop | Both |

---

## Files Modified Summary

### New Files to Create
- `app/registry/postprocess/template_checkbox_negation.py`
- `ml/lib/ml_coder/section_filter.py`
- `ops/tools/generate_cpt_keywords.py`
- `ml/scripts/bootstrap_granular_attributes.py`
- `tests/registry/test_template_checkbox_negation.py`
- `tests/registry/test_section_filter.py`

### Files to Modify
- `app/registry/application/registry_service.py`
- `app/registry/processing/masking.py`
- `app/registry/deterministic/deterministic_extractors.py`
- `app/registry/ner_mapping/procedure_extractor.py`
- `app/registry/evidence/verifier.py`
- `ml/lib/ml_coder/label_hydrator.py`
- `app/registry/processing/navigation_targets.py`
- `app/registry/processing/linear_ebus_stations_detail.py`

---

## Appendix: Quick Reference for Codex

When implementing, follow these principles:

1. **Fail-safe**: Always return original data if processing fails
2. **Evidence-first**: Attach evidence spans to any performed=True
3. **Section-aware**: Don't trust History/Plan/Assessment sections
4. **Negation-aware**: Check for negation context before setting True
5. **Test-driven**: Add unit tests for each new function
