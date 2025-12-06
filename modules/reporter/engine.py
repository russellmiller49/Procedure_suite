"""Deprecated shim forwarding to modules.reporting.engine."""

from __future__ import annotations

import warnings

from modules.reporting.engine import *  # noqa: F401,F403

warnings.warn(
    "modules.reporter.engine is deprecated; please import from modules.reporting.engine instead.",
    DeprecationWarning,
    stacklevel=2,
)
