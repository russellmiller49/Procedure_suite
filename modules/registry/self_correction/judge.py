"""Phase 6 judge: propose a JSON Patch for high-confidence omissions.

This module must never mutate a RegistryRecord. It generates patch proposals
only, with short verbatim evidence quotes anchored in text.

Design note:
Phase 7 introduces an OpenAI-protocol judge. For Phase 6 we keep a deterministic
offline judge to ensure tests have no network dependency.
"""

from __future__ import annotations

from dataclasses import asdict

from modules.registry.schema import RegistryRecord
from modules.registry.self_correction.types import JudgeProposal, SelfCorrectionTrigger


_CPT_TO_PATCH_PATH: dict[str, str] = {
    "32550": "/pleural_procedures/ipc/performed",
    "32554": "/pleural_procedures/thoracentesis/performed",
    "32555": "/pleural_procedures/thoracentesis/performed",
    "32551": "/pleural_procedures/chest_tube/performed",
}


_CPT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "32550": (
        "indwelling pleural catheter",
        "tunneled pleural catheter",
        "pleurx",
        "pneumocatheter",
        "ipc",
    ),
    "32554": ("thoracentesis", "pleural tap", "pleurocentesis", "pleuracentesis"),
    "32555": (
        "ultrasound-guided thoracentesis",
        "us-guided thoracentesis",
        "thoracentesis",
        "pleural tap",
    ),
    "32551": ("chest tube", "tube thoracostomy", "pigtail catheter", "thoracostomy"),
}


def propose_patch(
    *,
    raw_note_text: str,
    extraction_text: str | None,
    record: RegistryRecord,
    trigger: SelfCorrectionTrigger,
) -> JudgeProposal:
    target_cpt = (trigger.target_cpt or "").strip()
    if not target_cpt:
        return JudgeProposal(
            target_cpt="",
            patch=[],
            evidence_quotes=[],
            rationale="Missing target CPT in trigger",
            model_info={"judge": "offline.keyword_v1", "trigger": asdict(trigger)},
        )

    path = _CPT_TO_PATCH_PATH.get(target_cpt)
    if not path:
        return JudgeProposal(
            target_cpt=target_cpt,
            patch=[],
            evidence_quotes=[],
            rationale=f"Unsupported target CPT {target_cpt} for Phase 6 allowlist",
            model_info={"judge": "offline.keyword_v1", "trigger": asdict(trigger)},
        )

    text = extraction_text if (extraction_text and extraction_text.strip()) else raw_note_text
    quote = _find_evidence_quote(text, _CPT_KEYWORDS.get(target_cpt, ()))
    if not quote:
        return JudgeProposal(
            target_cpt=target_cpt,
            patch=[],
            evidence_quotes=[],
            rationale="No reliable verbatim evidence found for target CPT",
            model_info={
                "judge": "offline.keyword_v1",
                "trigger": asdict(trigger),
                "used_extraction_text": bool(extraction_text and extraction_text.strip()),
            },
        )

    if target_cpt == "32555":
        thora = getattr(getattr(record, "pleural_procedures", None), "thoracentesis", None)
        guidance = getattr(thora, "guidance", None) if thora is not None else None
        if guidance != "Ultrasound":
            return JudgeProposal(
                target_cpt=target_cpt,
                patch=[],
                evidence_quotes=[quote],
                rationale=(
                    "Thoracentesis guidance is not 'Ultrasound' in RegistryRecord; "
                    "cannot safely derive 32555 with a performed-only patch"
                ),
                model_info={"judge": "offline.keyword_v1", "trigger": asdict(trigger)},
            )

    if target_cpt == "32554":
        thora = getattr(getattr(record, "pleural_procedures", None), "thoracentesis", None)
        guidance = getattr(thora, "guidance", None) if thora is not None else None
        if guidance == "Ultrasound":
            return JudgeProposal(
                target_cpt=target_cpt,
                patch=[],
                evidence_quotes=[quote],
                rationale=(
                    "Thoracentesis guidance is 'Ultrasound' in RegistryRecord; "
                    "performed-only patch would derive 32555, not 32554"
                ),
                model_info={"judge": "offline.keyword_v1", "trigger": asdict(trigger)},
            )

    patch = [{"op": "add", "path": path, "value": True}]
    return JudgeProposal(
        target_cpt=target_cpt,
        patch=patch,
        evidence_quotes=[quote],
        rationale=f"Keyword evidence found for {target_cpt}; setting performed flag at {path}",
        model_info={
            "judge": "offline.keyword_v1",
            "trigger": asdict(trigger),
            "used_extraction_text": bool(extraction_text and extraction_text.strip()),
        },
    )


def _find_evidence_quote(text: str, keywords: tuple[str, ...]) -> str | None:
    if not text or not text.strip() or not keywords:
        return None

    lowered = text.lower()
    for keyword in keywords:
        needle = (keyword or "").strip().lower()
        if not needle:
            continue
        idx = lowered.find(needle)
        if idx < 0:
            continue
        if _looks_negated(lowered, idx, len(needle)):
            continue

        start = max(0, idx - 80)
        end = min(len(text), idx + len(needle) + 80)
        quote = text[start:end].strip()

        if len(quote) < 10:
            quote = text[max(0, idx - 120) : min(len(text), idx + len(needle) + 120)].strip()

        if len(quote) > 200:
            quote = quote[:200].rstrip()

        if 10 <= len(quote) <= 200:
            return quote
    return None


def _looks_negated(lowered_text: str, idx: int, needle_len: int) -> bool:
    window_start = max(0, idx - 20)
    window = lowered_text[window_start : idx + needle_len + 10]
    patterns = ("no ", "without ", "not ", "denies ", "declines ")
    return any(p in window for p in patterns)


__all__ = ["propose_patch"]
