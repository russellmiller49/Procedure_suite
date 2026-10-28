"""Synthetic, non-EMR robotic bronchoscopy + linear EBUS registry workbench.

Importing this package makes the bounded registry packages importable. They ship
to the secure repositories as source copies, so they load from ``packages/*/src``
the same way the ops tools and package tests load them. Doing it here (rather
than in a helper module) means it runs before any submodule's imports.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DICTIONARY_PATH = ROOT / "data/knowledge/robotic_ebus_v1/launch_dictionary.json"

for _package in ("ip_registry_contracts", "ip_registry_engine"):
    _path = str(ROOT / "packages" / _package / "src")
    if _path not in sys.path:
        sys.path.insert(0, _path)
