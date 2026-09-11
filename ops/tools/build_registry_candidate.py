#!/usr/bin/env python3
"""Publish a bounded source candidate. This command cannot deploy or push to secure repos."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import io

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    "app/registry/aggregation/sanitize.py",
    "app/registry/aggregation/pathology/normalize.py",
    "app/registry/aggregation/pathology/extract_pathology.py",
    "app/registry/aggregation/clinical/extract_clinical_update.py",
]
PACKAGE_ROOT = ROOT / "packages"


def synchronize():
    entries = []
    for source in SOURCES:
        raw = (ROOT / source).read_bytes()
        relative = source.removeprefix("app/registry/")
        dest = PACKAGE_ROOT / "ip_registry_engine/src/ip_registry_engine" / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(raw.decode().replace("app.registry.aggregation", "ip_registry_engine.aggregation"))
        parent = dest.parent
        while parent.name != "src":
            init = parent / "__init__.py"
            if not init.exists():
                init.write_text("")
            parent = parent.parent
        entries.append({"source": source, "source_sha256": hashlib.sha256(raw).hexdigest(),
                        "package_path": str(dest.relative_to(PACKAGE_ROOT)),
                        "package_sha256": hashlib.sha256(dest.read_bytes()).hexdigest()})
    return entries


def build(output: Path):
    sources = synchronize()
    files = []
    for name in ("ip_registry_contracts", "ip_registry_engine"):
        files.extend((PACKAGE_ROOT / name).rglob("*.py"))
        files.append(PACKAGE_ROOT / name / "pyproject.toml")
    files = sorted(p for p in files if "__pycache__" not in p.parts and "build" not in p.parts)
    manifest = {
        "format": 1, "candidate_only": True,
        "source_repository": "russellmiller49/Procedure_suite",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "working_tree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
        "clinical_qualification": "pending", "license_review": "pending", "sources": sources,
        "files": {str(p.relative_to(PACKAGE_ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as archive:
        for p in files:
            info = tarfile.TarInfo(str(p.relative_to(PACKAGE_ROOT)))
            data = p.read_bytes()
            info.size, info.mode, info.mtime = len(data), 0o644, 0
            archive.addfile(info, io.BytesIO(data))
        data = json.dumps(manifest, indent=2, sort_keys=True).encode()
        info = tarfile.TarInfo("candidate-manifest.json")
        info.size, info.mode = len(data), 0o644
        archive.addfile(info, io.BytesIO(data))
    print(json.dumps({"candidate": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                      "files": len(files), "qualified_for_clinical_use": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    build(parser.parse_args().output)
