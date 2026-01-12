from __future__ import annotations

from modules.registry.schema.ip_v3 import IPRegistryV3


def run_v3_extraction(note_text: str) -> IPRegistryV3:
    from modules.registry.processing.focus import get_procedure_focus
    from modules.registry.extractors.v3_extractor import extract_v3_draft
    from modules.registry.evidence.verifier import verify_registry

    focused = get_procedure_focus(note_text)
    draft = extract_v3_draft(focused)
    final = verify_registry(draft, note_text)
    return final


__all__ = ["run_v3_extraction"]

