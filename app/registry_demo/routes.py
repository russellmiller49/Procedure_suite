"""Demo API. Registered only when PROCSUITE_ROBOTIC_EBUS_DEMO is set."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.common.logger import get_logger
from app.registry_demo import budget, service
from app.registry_demo.settings import MAX_TEXT_CHARS

logger = get_logger("registry_demo")
router = APIRouter(tags=["robotic-ebus-demo"])
RECODE_REQUESTS = budget.RateLimit(limit=30, window_s=60)


class ExtractInput(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS * 2)
    sample_id: str | None = Field(default=None, max_length=120)
    # Tester path only: the password, what the note is, and the tester's confirmation.
    access_code: str | None = Field(default=None, max_length=200)
    note_kind: str | None = Field(default=None, max_length=40)
    attested: bool = False


class UnlockInput(BaseModel):
    access_code: str = Field(min_length=1, max_length=200)


class RecodeInput(BaseModel):
    proposal: dict[str, Any]
    unresolved: list[dict[str, Any]] = Field(default_factory=list, max_length=500)


def _client(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")


def _call(fn, *args: Any, **kwargs: Any) -> Any:
    try:
        return fn(*args, **kwargs)
    except service.DemoError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": exc.message}) from exc


@router.get("/config")
def config() -> dict[str, Any]:
    return service.config()


@router.get("/samples/{sample_id}")
def sample(sample_id: str) -> dict[str, Any]:
    return _call(service.sample_detail, sample_id)


@router.post("/unlock")
def unlock(body: UnlockInput, request: Request) -> dict[str, Any]:
    return _call(service.unlock, body.access_code, _client(request))


@router.post("/extract")
def extract(body: ExtractInput, request: Request) -> dict[str, Any]:
    live = service.LiveRequest(
        access_code=body.access_code,
        note_kind=body.note_kind,
        attested=body.attested,
        client=_client(request),
    )
    result = _call(service.extract, body.text, body.sample_id, live=live)
    # Metrics only: never the note text or anything extracted from it.
    if result["source"] == "live":
        inference = (result.get("llm") or {}).get("inference") or {}
        logger.info(
            "demo extract source=live kind=%s model_used=%s reason=%s chars=%d cost=%s latency=%s",
            result["note_kind"],
            result["reader"]["model_used"],
            result["reader"]["reason"],
            len(body.text),
            inference.get("cost_usd"),
            inference.get("latency_s"),
        )
    else:
        logger.info(
            "demo extract source=%s sample=%s sha=%s chars=%d",
            result["source"],
            result["sample_id"],
            result["text_sha256"][:12],
            len(body.text),
        )
    return result


@router.post("/codes")
def codes(body: RecodeInput, request: Request) -> dict[str, Any]:
    if not RECODE_REQUESTS.allow(_client(request)):
        raise HTTPException(429, {"code": "too_many_requests", "message": "Try again shortly."})
    return _call(service.recode, body.proposal, body.unresolved)


__all__ = ["router"]
