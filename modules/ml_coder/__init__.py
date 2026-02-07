"""Compatibility wrapper for legacy ``modules.ml_coder`` imports."""

from __future__ import annotations

from importlib import import_module
import sys

_TARGET_PACKAGE = "ml.lib.ml_coder"
_LEGACY_SUBMODULES = (
    "data_prep",
    "distillation_io",
    "label_hydrator",
    "predictor",
    "preprocessing",
    "registry_data_prep",
    "registry_label_constraints",
    "registry_label_schema",
    "registry_predictor",
    "registry_training",
    "self_correction",
    "thresholds",
    "training",
    "training_losses",
    "utils",
    "valid_ip_codes",
)

_target_pkg = import_module(_TARGET_PACKAGE)

for _submodule in _LEGACY_SUBMODULES:
    _legacy_name = f"{__name__}.{_submodule}"
    _target_name = f"{_TARGET_PACKAGE}.{_submodule}"
    try:
        _module = import_module(_target_name)
    except ModuleNotFoundError:
        continue
    sys.modules[_legacy_name] = _module
    globals()[_submodule] = _module


def __getattr__(name: str):
    return getattr(_target_pkg, name)

