from __future__ import annotations

import re
from typing import Iterable


PATTERNS: list[str] = [
    r"(?ims)^IP CODE MOD DETAILS.*?(?=\n\n|\Z)",
    r"(?ims)^CPT\s+CODES?:.*?(?=\n\n|\Z)",
    r"(?ims)^BILLING:.*?(?=\n\n|\Z)",
    r"(?ims)^CODING\s+SUMMARY.*?(?=\n\n|\Z)",
    r"(?im)^\s*(?:CPT:?)?\s*\d{5}\b.*$",
]


def mask_offset_preserving(text: str, patterns: Iterable[str] = PATTERNS) -> str:
    """Mask matched spans with spaces while preserving length and newlines."""
    masked = text or ""
    for pat in patterns:
        for match in re.finditer(pat, masked):
            start, end = match.span()
            chunk = masked[start:end]
            chunk_mask = re.sub(r"[^\n]", " ", chunk)
            masked = masked[:start] + chunk_mask + masked[end:]
    return masked


__all__ = ["PATTERNS", "mask_offset_preserving"]
