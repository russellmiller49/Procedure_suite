"""Deprecated shim forwarding to app.reporting.engine."""

from __future__ import annotations

import warnings
from typing import Any

from app.reporting.engine import *  # noqa: F401,F403
from app.reporting.engine import ReporterEngine

# Backward-compat alias for legacy imports.
ReportEngine: Any = ReporterEngine

warnings.warn(
    "app.reporter.engine is deprecated; please import from app.reporting.engine instead.",
    DeprecationWarning,
    stacklevel=2,
)
