"""Demo API. Registered only when PROCSUITE_ROBOTIC_EBUS_DEMO is set."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.common.logger import get_logger
from app.registry_demo import service
from app.registry_demo.settings import MAX_TEXT_CHARS

logger = get_logger("registry_demo")
router = APIRouter(tags=["robotic-ebus-demo"])


class ExtractInput(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS * 2)
    sample_id: str | None = Field(default=None, max_length=120)


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


@router.post("/extract")
def extract(body: ExtractInput) -> dict[str, Any]:
    result = _call(service.extract, body.text, body.sample_id)
    # Metrics only: never the note text or anything extracted from it.
    logger.info(
        "demo extract source=%s sample=%s sha=%s chars=%d",
        result["source"],
        result["sample_id"],
        result["text_sha256"][:12],
        len(body.text),
    )
    return result


__all__ = ["router"]
