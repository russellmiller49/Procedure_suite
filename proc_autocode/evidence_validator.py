from typing import List, Dict
from proc_schemas.envelope_models import CodeSuggestion, EvidenceSpan, ValidationIssue


def validate_evidence(suggestions: List[CodeSuggestion], source_docs: Dict[str, str]):
    """Validate evidence spans for each suggestion against source documents.
    Returns a list of ValidationIssue objects and sets validation_status on suggestions.
    """
    issues: List[ValidationIssue] = []
    for suggestion in suggestions:
        valid = True
        for span in suggestion.evidence:
            # Check if source_id exists
            if hasattr(span, 'source_id') and span.source_id not in source_docs:
                issues.append(ValidationIssue(issue=f"source_id {span.source_id} missing"))
                valid = False
                continue
            # Check if text appears in source doc
            doc = source_docs.get(getattr(span, 'source_id', ''), "")
            if getattr(span, 'text', "") and getattr(span, 'text') not in doc:
                issues.append(ValidationIssue(issue=f"text '{span.text}' not found in source {span.source_id}"))
                valid = False
        suggestion.validation_status = "validated" if valid else "failed"
    return issues
