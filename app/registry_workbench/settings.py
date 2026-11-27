"""Workbench gates. It is synthetic-only and must never be reachable in production."""

from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes"}


def workbench_enabled() -> bool:
    if not _truthy("PROCSUITE_WORKBENCH_ENABLED"):
        return False
    if os.getenv("PROCSUITE_ENV", "").strip().lower() == "production":
        return False
    return not _truthy("CODER_REQUIRE_PHI_REVIEW")


def claude_configured() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def inline_jobs() -> bool:
    """Run extractions in the request thread (tests and scripted seeding)."""
    return _truthy("PROCSUITE_WORKBENCH_INLINE_JOBS")


__all__ = ["claude_configured", "inline_jobs", "workbench_enabled"]
