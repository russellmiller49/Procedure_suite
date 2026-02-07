#!/usr/bin/env python3
from __future__ import annotations

from importlib import import_module
import runpy
import sys

_TARGET_MODULE = "ops.tools.generate_cpt_keywords"
_impl = import_module(_TARGET_MODULE)

if __name__ != "__main__":
    sys.modules[__name__] = _impl
else:
    if hasattr(_impl, "main"):
        raise SystemExit(_impl.main())
    runpy.run_module(_TARGET_MODULE, run_name="__main__")
