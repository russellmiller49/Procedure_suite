"""Build demo responses from stored results. No provider call happens here."""

from __future__ import annotations

from typing import Any

from app.registry_demo import store
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


class DemoError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(code)
        self.status, self.code, self.message = status, code, message


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
        "notice": NOTICE,
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


def extract(text: str, sample_id: str | None = None) -> dict[str, Any]:
    """Return the stored result for an exact reviewed text; nothing else is served."""
    if not text or not text.strip():
        raise DemoError(422, "empty_text", "There is no note text to extract.")
    if len(text) > MAX_TEXT_CHARS:
        raise DemoError(413, "text_too_long", f"The note is over {MAX_TEXT_CHARS} characters.")
    entry = store.result_for(text)
    if entry is None:
        raise DemoError(
            403,
            "reviewed_samples_only",
            "This demo serves stored results for the reviewed sample notes only. The text "
            "does not match a reviewed sample exactly. Use the reviewed redaction of a sample.",
        )
    llm, rules = _side(entry.get("llm")), _side(entry.get("rules"))
    source_text = store.normalise(text)
    codes = None
    if llm and llm.get("proposal"):
        codes = suggest_codes(
            llm["proposal"], source_text=source_text, unresolved=llm["unresolved_mentions"]
        )
    return {
        "status": "ok",
        "source": "precomputed_sample",
        "source_label": "Precomputed sample",
        "sample_id": entry.get("sample_id") or sample_id,
        "text_sha256": store.text_key(text),
        "generated_at": entry.get("generated_at"),
        "notice": NOTICE,
        "llm": llm,
        "rules": rules,
        "comparison": _comparison(llm, rules),
        "codes": codes,
    }


__all__ = ["DemoError", "NOTICE", "config", "extract", "sample_detail"]
