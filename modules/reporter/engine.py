"""Deprecated shim forwarding to proc_report.engine."""

from __future__ import annotations

import warnings

from proc_report.engine import *  # noqa: F401,F403

warnings.warn(
    "modules.reporter.engine is deprecated; please import from proc_report.engine instead.",
    DeprecationWarning,
    stacklevel=2,
)
