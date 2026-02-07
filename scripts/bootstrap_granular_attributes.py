#!/usr/bin/env python3
from __future__ import annotations

from importlib import import_module

_impl = import_module("ml.scripts.bootstrap_granular_attributes")
globals().update(
    {
        name: value
        for name, value in vars(_impl).items()
        if not (name.startswith("__") and name.endswith("__"))
    }
)

if __name__ == "__main__":
    if hasattr(_impl, "main"):
        raise SystemExit(_impl.main())

    import runpy

    runpy.run_module("ml.scripts.bootstrap_granular_attributes", run_name="__main__")
