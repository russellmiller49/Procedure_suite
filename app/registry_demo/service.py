"""Build demo responses.

Bundled samples are answered from stored, reviewed results: no provider call. A
tester's own note is read live (``app.registry_demo.live``) only with a tester
password; that path stores nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.registry_demo import store
from app.registry_demo.errors import DemoError
from app.registry_demo.settings import (
    MAX_TEXT_CHARS,
    PLACEHOLDER,
    live_extraction_enabled,
)
from app.registry_workbench import compare as comparison
from app.registry_workbench.contract_coding import suggest_codes
from app.registry_workbench.profile import profile

NOTICE = (
    "Prototype on synthetic notes only. Not clinically validated. "
    "Do not enter real patient information."
)
TESTER_NOTICE = (
    "Prototype. Not clinically validated. The bundled samples are synthetic. Approved "
    "testers can use their own notes: identifiers are removed in this browser before "
    "anything is sent, and nothing is stored."
)
MAX_PROPOSAL_CHARS = 600_000
INFERENCE_FIELDS = (
    "provider",
    "model",
    "requested_model",
    "effort",
    "prompt_version",
    "repair_used",
    "fallback_used",
    "cost_usd",
    "latency_s",
    "deterministic_version",
    "ner_available",
)


@dataclass(frozen=True)
class LiveRequest:
    """What a tester sends with their own note."""

    access_code: str | None
    note_kind: str | None
    attested: bool
    client: str


def _sample_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "title": item["title"],
        "teaching_point": item["teaching_point"],
        "platform": item.get("platform"),
        "components": item.get("components") or [],
        "style": item.get("style"),
        "traps": item.get("traps") or [],
        "chars": len(item["text"]),
        "has_result": store.has_result(item["id"]),
    }


def config() -> dict[str, Any]:
    return {
        "enabled": True,
        "notice": TESTER_NOTICE if live_extraction_enabled() else NOTICE,
        "placeholder": PLACEHOLDER,
        "max_text_chars": MAX_TEXT_CHARS,
        "live_extraction": {
            "enabled": live_extraction_enabled(),
            "reason": None if live_extraction_enabled() else "reviewed_samples_only",
        },
        "samples": [_sample_summary(s) for s in store.samples()],
        "profile": profile(),
    }


def sample_detail(sample_id: str) -> dict[str, Any]:
    item = store.sample(sample_id)
    if item is None:
        raise DemoError(404, "unknown_sample", "No sample has that id.")
    return {
        **_sample_summary(item),
        "text": item["text"],
        "reviewed_redactions": [
            {"worker": r.get("worker"), "text": r["text"]} for r in store.redactions(sample_id)
        ],
    }


def _side(response: dict[str, Any] | None) -> dict[str, Any] | None:
    if not response:
        return None
    observations = response.get("observations") or {}
    inference = observations.get("inference") or {}
    return {
        "status": response.get("status"),
        "warnings": response.get("warnings") or [],
        "proposal": observations.get("proposal"),
        "unresolved_mentions": observations.get("unresolved_mentions") or [],
        "quality_signals": observations.get("quality_signals") or [],
        "inference": {k: inference[k] for k in INFERENCE_FIELDS if k in inference},
    }


def _values(side: dict[str, Any] | None) -> dict[str, Any] | None:
    proposal = (side or {}).get("proposal")
    if not proposal:
        return None
    return {k: v for k, v in proposal.items() if k != "field_provenance"}


def _comparison(llm: dict[str, Any] | None, rules: dict[str, Any] | None) -> dict[str, Any]:
    sources = {"LLM": _values(llm), "Rules engine": _values(rules)}
    rows = comparison.compare(sources)
    summary = {"llm_only": 0, "rules_only": 0, "agree": 0, "differ": 0}
    for row in rows:
        a, b = row["values"]["LLM"], row["values"]["Rules engine"]
        if a is not None and b is None:
            summary["llm_only"] += 1
        elif a is None and b is not None:
            summary["rules_only"] += 1
        elif row["agree"]:
            summary["agree"] += 1
        else:
            summary["differ"] += 1
    summary["llm_total"] = summary["llm_only"] + summary["agree"] + summary["differ"]
    summary["rules_total"] = summary["rules_only"] + summary["agree"] + summary["differ"]
    return {"sources": list(sources), "rows": rows, "summary": summary}


def _result(
    llm_response: dict[str, Any] | None,
    rules_response: dict[str, Any] | None,
    source_text: str,
    **meta: Any,
) -> dict[str, Any]:
    llm, rules = _side(llm_response), _side(rules_response)
    # What the reader reviews: the model's reading, or the rules engine's when there is none.
    primary = "llm" if llm and llm.get("proposal") else "rules"
    reviewed = llm if primary == "llm" else rules
    codes = None
    if reviewed and reviewed.get("proposal"):
        codes = suggest_codes(
            reviewed["proposal"],
            source_text=source_text,
            unresolved=reviewed["unresolved_mentions"],
        )
    return {
        "status": "ok",
        **meta,
        "primary": primary,
        "llm": llm,
        "rules": rules,
        "comparison": _comparison(llm, rules),
        # Which model values the rules engine extracted too, keyed by proposal path.
        "rules_agreement": comparison.agreement(_values(llm), _values(rules)),
        "codes": codes,
    }


def _live(text: str, request: LiveRequest) -> dict[str, Any]:
    from app.registry_demo import live

    live.check_code(request.access_code, request.client)
    if request.note_kind not in live.NOTE_KINDS:
        raise DemoError(422, "note_kind_required", "Say whether the note is synthetic or real.")
    if not request.attested:
        raise DemoError(
            422,
            "attestation_required",
            "Confirm the statement about this note before extracting.",
        )
    if not live.LIVE_REQUESTS.allow(request.client):
        raise DemoError(429, "too_many_requests", "Too many notes in a minute. Try again shortly.")
    source_text = store.normalise(text)
    model, rules, reader = live.read_note(source_text, note_kind=request.note_kind)
    return _result(
        model,
        rules,
        source_text,
        source="live",
        source_label="Live extraction, not stored",
        sample_id=None,
        text_sha256=None,
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        notice=TESTER_NOTICE,
        note_kind=request.note_kind,
        reader=reader,
    )


def extract(
    text: str, sample_id: str | None = None, *, live: LiveRequest | None = None
) -> dict[str, Any]:
    """The stored result for an exact reviewed sample text; a live reading for a tester."""
    if not text or not text.strip():
        raise DemoError(422, "empty_text", "There is no note text to extract.")
    if len(text) > MAX_TEXT_CHARS:
        raise DemoError(413, "text_too_long", f"The note is over {MAX_TEXT_CHARS} characters.")
    entry = store.result_for(text)
    if entry is None and store.reviewed_sample_for(text) is not None:
        raise DemoError(
            409,
            "result_not_generated",
            "This is a reviewed sample, but its result has not been generated yet.",
        )
    if entry is None and live is not None and live.access_code is not None:
        return _live(text, live)
    if entry is None:
        raise DemoError(
            403,
            "reviewed_samples_only",
            "This demo serves stored results for the reviewed sample notes only. The text "
            "does not match a reviewed sample exactly. Use the reviewed redaction of a sample"
            + (", or unlock tester access to read your own note." if live_extraction_enabled() else "."),
        )
    return _result(
        entry.get("llm"),
        entry.get("rules"),
        store.normalise(text),
        source="precomputed_sample",
        source_label="Precomputed sample",
        sample_id=entry.get("sample_id") or sample_id,
        text_sha256=store.text_key(text),
        generated_at=entry.get("generated_at"),
        notice=NOTICE,
    )


def unlock(access_code: str | None, client: str) -> dict[str, Any]:
    """Check a tester password and say what this server will do with a tester's note."""
    from app.registry_demo import live

    live.check_code(access_code, client)
    return {"ok": True, **live.describe()}


def recode(proposal: dict[str, Any], unresolved: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Suggested codes for a proposal as corrected by a reviewer. Stateless; no note text."""
    import json

    if not isinstance(proposal, dict) or len(json.dumps(proposal)) > MAX_PROPOSAL_CHARS:
        raise DemoError(413, "proposal_too_large", "The reviewed record is too large.")
    try:
        return suggest_codes(proposal, source_text=None, unresolved=unresolved or [])
    except Exception as exc:  # a hand-edited record can be one the coding engine cannot read
        raise DemoError(
            422,
            "codes_not_derivable",
            "Codes could not be worked out from the corrected record.",
        ) from exc


__all__ = [
    "DemoError",
    "LiveRequest",
    "NOTICE",
    "TESTER_NOTICE",
    "config",
    "extract",
    "recode",
    "sample_detail",
    "unlock",
]
