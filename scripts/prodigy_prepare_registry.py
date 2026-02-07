#!/usr/bin/env python3
from __future__ import annotations

from importlib import import_module
import runpy

_impl = import_module("ml.scripts.prodigy_prepare_registry")
globals().update(
    {
        name: value
        for name, value in vars(_impl).items()
        if not (name.startswith("__") and name.endswith("__"))
    }
)

# Keep monkeypatch-friendly indirection for tests/importers that patch
# `scripts.prodigy_prepare_registry.load_predictor`.
load_predictor = _impl.load_predictor


def main(argv=None):
    _impl.load_predictor = load_predictor
    return _impl.main(argv)


if __name__ == "__main__":
    if hasattr(_impl, "main"):
        raise SystemExit(main())
    runpy.run_module("ml.scripts.prodigy_prepare_registry", run_name="__main__")
