#!/usr/bin/env python3
from __future__ import annotations

from importlib import import_module

_impl = import_module("ml.scripts.build_model_agnostic_phi_spans")
globals().update(
    {
        name: value
        for name, value in vars(_impl).items()
        if not (name.startswith("__") and name.endswith("__"))
    }
)

if __name__ == "__main__":
    raise SystemExit(_impl.main())
