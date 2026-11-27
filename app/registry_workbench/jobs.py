"""Run extraction jobs off the request thread with a single writer (SQLite).

Workbench documents are synthetic by construction (corpus imports or attested
manual entries), so Claude runs inside a declared synthetic egress context.
"""

from __future__ import annotations

import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Callable

from app.common.anthropic_client import ClaudeClient, ClaudeSettings
from app.common.llm_egress import egress_context
from app.common.logger import get_logger
from app.registry_workbench.db import Case, Document, ExtractionRun, session_factory
from app.registry_workbench.extraction.claude_provider import ClaudeRegistryProvider
from app.registry_workbench.settings import inline_jobs
from ip_registry_contracts.models import ExtractionRequest
from ip_registry_engine.engine import LocalDeterministicProvider

logger = get_logger("registry_workbench.jobs")

_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="workbench-extract")
# Tests swap in a fake Anthropic SDK; None uses the real client.
SDK_FACTORY: Callable[[], Any] | None = None


def _provider(run: ExtractionRun) -> Any:
    if run.provider == "deterministic":
        return LocalDeterministicProvider()
    settings = ClaudeSettings.from_env(model=run.model, effort=run.effort)
    sdk = SDK_FACTORY() if SDK_FACTORY is not None else None
    return ClaudeRegistryProvider(ClaudeClient(settings, sdk=sdk))


def execute_run(run_id: str) -> None:
    with session_factory()() as db:
        run = db.get(ExtractionRun, run_id)
        if run is None or run.status not in {"queued", "running"}:
            return
        document = db.get(Document, run.document_id)
        case = db.get(Case, document.case_id)
        run.status = "running"
        db.commit()
        request = ExtractionRequest(
            job_id=uuid.uuid4(),
            source_document_id=document.id,
            source_digest=document.sha256,
            text=document.text,
            kind=document.kind,
        )
        try:
            provider = _provider(run)
            with egress_context("synthetic", source=f"workbench:{case.source}"):
                response = provider.extract(request)
            data = response.model_dump(mode="json")
            inference = (data.get("observations") or {}).get("inference") or {}
            run.response = data
            run.status = "succeeded"
            run.model = inference.get("model") or run.model
            run.cost_usd = inference.get("cost_usd")
            run.latency_s = inference.get("latency_s")
            run.prompt_digest = inference.get("prompt_digest")
            run.schema_digest = inference.get("schema_digest")
        except Exception as exc:  # recorded on the run; the worker keeps serving
            logger.warning("workbench extraction %s failed: %s", run.id, type(exc).__name__)
            run.status = "failed"
            run.error = f"{type(exc).__name__}: {exc}"[:2000]
        run.finished_at = datetime.now(timezone.utc)
        db.commit()


def submit(run_id: str) -> Future | None:
    if inline_jobs():
        execute_run(run_id)
        return None
    return _EXECUTOR.submit(execute_run, run_id)


__all__ = ["SDK_FACTORY", "execute_run", "submit"]
