"""Coder package.

IMPORTANT:
- `app.coder.engine` is a **deprecated** legacy pipeline and imports heavy NLP deps
  (spaCy/medspaCy/UMLS tooling) at import-time.
- The primary supported entry point is `app.coder.application.coding_service.CodingService`.

Historically this package re-exported `CoderEngine` and `CoderOutput` from the legacy module.
To keep backward compatibility *without* slowing down unrelated imports (like the API app),
we lazily import these symbols on first access.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["CoderEngine", "CoderOutput"]


def __getattr__(name: str) -> Any:  # pragma: no cover
    if name == "CoderEngine":
        return getattr(import_module("app.coder.engine"), "CoderEngine")
    if name == "CoderOutput":
        return getattr(import_module("app.coder.schema"), "CoderOutput")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover
    return sorted(set(globals().keys()) | set(__all__))
