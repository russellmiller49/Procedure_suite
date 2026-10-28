"""Make the bounded registry packages importable from app/ without installing them.

The packages ship to the secure repositories as source copies, so they are loaded
from ``packages/*/src`` the same way the ops tools and package tests load them.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

for _package in ("ip_registry_contracts", "ip_registry_engine"):
    _path = str(ROOT / "packages" / _package / "src")
    if _path not in sys.path:
        sys.path.insert(0, _path)

DICTIONARY_PATH = ROOT / "data/knowledge/robotic_ebus_v1/launch_dictionary.json"
