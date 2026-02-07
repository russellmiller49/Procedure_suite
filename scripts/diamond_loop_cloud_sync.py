#!/usr/bin/env python3
from __future__ import annotations

from importlib import import_module

_impl = import_module("ml.scripts.diamond_loop_cloud_sync")
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

    runpy.run_module("ml.scripts.diamond_loop_cloud_sync", run_name="__main__")
