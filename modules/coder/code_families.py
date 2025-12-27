"""Loader for static code family hierarchy configuration."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


@lru_cache()
def load_code_families() -> Dict[str, Any]:
    """Load code family configuration from data/knowledge."""
    root = Path(__file__).resolve().parents[2]
    config_path = root / "data" / "knowledge" / "code_families.v1.json"
    with config_path.open() as f:
        data: Dict[str, Any] = json.load(f)
    return data


__all__ = ["load_code_families"]
