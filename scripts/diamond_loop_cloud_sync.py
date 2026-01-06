#!/usr/bin/env python3
"""
Diamond Loop cloud sync helper.

Goal:
- Keep Diamond Loop state consistent across machines (WSL + macOS) using a cloud
  drive folder (Google Drive).
- Avoid syncing Prodigy's SQLite DB directly (unsafe). Instead sync via export/import.

What this syncs:
- Prodigy dataset snapshot (JSONL) for REGISTRY textcat workflow
- Registry Prodigy manifest (prevents re-sampling)
- Unlabeled notes pool (ensures consistent sampling universe)
- Optional: current batch + human export CSV

Two modes:
- push: export Prodigy dataset → copy to cloud; copy local files → cloud
- pull: copy cloud files → local; import Prodigy dataset (with --reset)

WSL + Google Drive on Windows G: example:
  python scripts/diamond_loop_cloud_sync.py push --dataset registry_v1 --gdrive-win-root "G:\\My Drive\\proc_suite_sync"
  python scripts/diamond_loop_cloud_sync.py pull --dataset registry_v1 --gdrive-win-root "G:\\My Drive\\proc_suite_sync"

macOS example (Drive path varies by install):
  python scripts/diamond_loop_cloud_sync.py push --dataset registry_v1 --sync-root "/Users/<you>/Library/CloudStorage/GoogleDrive-<acct>/My Drive/proc_suite_sync"
  python scripts/diamond_loop_cloud_sync.py pull --dataset registry_v1 --sync-root "/Users/<you>/Library/CloudStorage/GoogleDrive-<acct>/My Drive/proc_suite_sync"
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyncPaths:
    # Repo-local paths (relative to repo root)
    manifest_rel: Path = Path("data/ml_training/registry_prodigy_manifest.json")
    unlabeled_rel: Path = Path("data/ml_training/registry_unlabeled_notes.jsonl")
    batch_rel: Path = Path("data/ml_training/registry_prodigy_batch.jsonl")
    human_csv_rel: Path = Path("data/ml_training/registry_human.csv")

    # Cloud layout (relative to sync root)
    diamond_dir: Path = Path("diamond_loop")
    prodigy_dir: Path = Path("prodigy")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        capture_output=capture,
    )


def _is_wsl() -> bool:
    # Common signal in WSL envs.
    return "WSL_INTEROP" in os.environ or "WSL_DISTRO_NAME" in os.environ


def _wslpath_to_windows(path: Path) -> str:
    """
    Convert a Linux/WSL path to a Windows path usable by PowerShell.
    Requires wslpath.
    """
    cp = _run(["wslpath", "-w", str(path)], capture=True)
    out = (cp.stdout or "").strip()
    if not out:
        raise RuntimeError(f"wslpath returned empty output for {path}")
    return out


def _ps_copy_item(win_src: str, win_dst: str) -> None:
    # Use Copy-Item with -Force; ensure destination directory exists.
    # Use single quotes (PowerShell) for proper handling of spaces.
    dst_dir = win_dst.rsplit("\\", 1)[0]
    cmd = (
        f"New-Item -ItemType Directory -Force -Path '{dst_dir}' | Out-Null; "
        f"Copy-Item -Force '{win_src}' '{win_dst}'"
    )
    _run(["powershell.exe", "-NoProfile", "-Command", cmd], check=True)


def _copy_local_to_cloud(local_src: Path, cloud_dst: Path, *, sync_root: Path | None, gdrive_win_root: str | None) -> None:
    local_src = local_src.resolve()
    if not local_src.exists():
        return

    if gdrive_win_root:
        if not _is_wsl():
            raise RuntimeError("--gdrive-win-root is intended for WSL environments.")
        win_src = _wslpath_to_windows(local_src)
        win_dst = str(Path(gdrive_win_root) / cloud_dst).replace("/", "\\")
        _ps_copy_item(win_src, win_dst)
        return

    if sync_root is None:
        raise RuntimeError("Must provide either --sync-root (mac/linux) or --gdrive-win-root (WSL).")
    dst = (sync_root / cloud_dst).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(local_src, dst)


def _copy_cloud_to_local(cloud_src: Path, local_dst: Path, *, sync_root: Path | None, gdrive_win_root: str | None) -> bool:
    local_dst = local_dst.resolve()

    if gdrive_win_root:
        if not _is_wsl():
            raise RuntimeError("--gdrive-win-root is intended for WSL environments.")
        win_dst = _wslpath_to_windows(local_dst)
        win_src = str(Path(gdrive_win_root) / cloud_src).replace("/", "\\")
        try:
            _ps_copy_item(win_src, win_dst)
            return True
        except subprocess.CalledProcessError:
            return False

    if sync_root is None:
        raise RuntimeError("Must provide either --sync-root (mac/linux) or --gdrive-win-root (WSL).")
    src = (sync_root / cloud_src).resolve()
    if not src.exists():
        return False
    local_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, local_dst)
    return True


def _prodigy_export(dataset: str, out_file: Path) -> None:
    from scripts.prodigy_cloud_sync import export_dataset  # local helper

    export_dataset(dataset=dataset, out_file=out_file, answer=None)


def _prodigy_import(dataset: str, in_file: Path, *, reset: bool) -> None:
    from scripts.prodigy_cloud_sync import import_dataset  # local helper

    import_dataset(dataset=dataset, in_file=in_file, reset_first=reset, overwrite=False, rehash=False)


def push(
    *,
    dataset: str,
    sync_root: Path | None,
    gdrive_win_root: str | None,
    include_batch: bool,
    include_human: bool,
) -> None:
    repo = _repo_root()
    p = SyncPaths()

    # 1) Export Prodigy dataset snapshot to a temp file, then copy it to cloud.
    tmp = Path("/tmp") / f"{dataset}.prodigy.jsonl"
    _prodigy_export(dataset, tmp)
    _copy_local_to_cloud(tmp, p.prodigy_dir / f"{dataset}.prodigy.jsonl", sync_root=sync_root, gdrive_win_root=gdrive_win_root)

    # 2) Copy local Diamond Loop files to cloud if present.
    _copy_local_to_cloud(repo / p.manifest_rel, p.diamond_dir / p.manifest_rel.name, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    _copy_local_to_cloud(repo / p.unlabeled_rel, p.diamond_dir / p.unlabeled_rel.name, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if include_batch:
        _copy_local_to_cloud(repo / p.batch_rel, p.diamond_dir / p.batch_rel.name, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if include_human:
        _copy_local_to_cloud(repo / p.human_csv_rel, p.diamond_dir / p.human_csv_rel.name, sync_root=sync_root, gdrive_win_root=gdrive_win_root)

    print(f"OK: pushed dataset '{dataset}' and Diamond Loop files to sync root")


def pull(
    *,
    dataset: str,
    sync_root: Path | None,
    gdrive_win_root: str | None,
    reset_dataset: bool,
    include_batch: bool,
    include_human: bool,
) -> None:
    repo = _repo_root()
    p = SyncPaths()

    # 1) Pull dataset snapshot from cloud into temp, then import into local Prodigy DB.
    tmp = Path("/tmp") / f"{dataset}.prodigy.jsonl"
    ok = _copy_cloud_to_local(p.prodigy_dir / f"{dataset}.prodigy.jsonl", tmp, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if not ok:
        raise FileNotFoundError(f"Missing cloud dataset snapshot: {p.prodigy_dir / f'{dataset}.prodigy.jsonl'}")
    _prodigy_import(dataset, tmp, reset=reset_dataset)

    # 2) Pull Diamond Loop files from cloud into repo (best-effort).
    _copy_cloud_to_local(p.diamond_dir / p.manifest_rel.name, repo / p.manifest_rel, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    _copy_cloud_to_local(p.diamond_dir / p.unlabeled_rel.name, repo / p.unlabeled_rel, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if include_batch:
        _copy_cloud_to_local(p.diamond_dir / p.batch_rel.name, repo / p.batch_rel, sync_root=sync_root, gdrive_win_root=gdrive_win_root)
    if include_human:
        _copy_cloud_to_local(p.diamond_dir / p.human_csv_rel.name, repo / p.human_csv_rel, sync_root=sync_root, gdrive_win_root=gdrive_win_root)

    print(f"OK: pulled dataset '{dataset}' and Diamond Loop files from sync root")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--dataset", default="registry_v1", help="Prodigy dataset name (default: registry_v1)")
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--sync-root", type=Path, help="Local filesystem path to sync root (mac/linux)")
        g.add_argument("--gdrive-win-root", type=str, help="Windows path to sync root (WSL), e.g. G:\\My Drive\\proc_suite_sync")
        p.add_argument("--include-batch", action="store_true", help="Also sync the current batch JSONL")
        p.add_argument("--include-human", action="store_true", help="Also sync registry_human.csv")

    p_push = sub.add_parser("push", help="Export Prodigy dataset and push Diamond Loop files to cloud")
    add_common(p_push)

    p_pull = sub.add_parser("pull", help="Pull from cloud and import into local Prodigy DB")
    add_common(p_pull)
    p_pull.add_argument(
        "--reset",
        action="store_true",
        help="Drop local dataset before import (recommended when switching machines)",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    sync_root = args.sync_root.resolve() if getattr(args, "sync_root", None) is not None else None
    gdrive_win_root = getattr(args, "gdrive_win_root", None)

    if args.cmd == "push":
        push(
            dataset=args.dataset,
            sync_root=sync_root,
            gdrive_win_root=gdrive_win_root,
            include_batch=bool(args.include_batch),
            include_human=bool(args.include_human),
        )
        return 0

    if args.cmd == "pull":
        pull(
            dataset=args.dataset,
            sync_root=sync_root,
            gdrive_win_root=gdrive_win_root,
            reset_dataset=bool(args.reset),
            include_batch=bool(args.include_batch),
            include_human=bool(args.include_human),
        )
        return 0

    raise SystemExit(f"Unknown cmd: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())


