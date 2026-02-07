#!/usr/bin/env python3
from __future__ import annotations

from importlib import import_module

_impl = import_module("ml.scripts.generate_blank_granular_note_scripts")
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

    runpy.run_module("ml.scripts.generate_blank_granular_note_scripts", run_name="__main__")
