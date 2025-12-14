#!/usr/bin/env python3
"""
Generate gitingest.md - A token-budget friendly snapshot of the repo structure
and curated important files for LLM/context ingestion.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Set


# Configuration
EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "data",
    "dist",
    "distilled",
    "proc_suite.egg-info",
    "reports",
    "validation_results",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
}

EXCLUDED_FILE_EXTENSIONS = {
    ".bin",
    ".db",
    ".onnx",
    ".pt",
    ".pth",
    ".tar.gz",
    ".zip",
    ".pyc",
    ".pyo",
}

IMPORTANT_DIRS = [
    "modules/",
    "proc_report/",
    "proc_autocode/",
    "proc_nlp/",
    "proc_registry/",
    "proc_schemas/",
    "schemas/",
    "configs/",
    "scripts/",
    "tests/",
]

IMPORTANT_FILES = [
    "README.md",
    "CLAUDE.md",
    "pyproject.toml",
    "requirements.txt",
    "Makefile",
    "runtime.txt",
    "modules/api/fastapi_app.py",
    "modules/coder/application/coding_service.py",
    "modules/registry/application/registry_service.py",
    "modules/agents/contracts.py",
    "modules/agents/run_pipeline.py",
    "docs/DEVELOPMENT.md",
    "docs/ARCHITECTURE.md",
    "docs/INSTALLATION.md",
    "docs/USER_GUIDE.md",
]


def get_git_info() -> tuple[str, str]:
    """Get current git branch and commit hash."""
    try:
        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        commit = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        return branch, commit
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown", "unknown"


def should_exclude_path(path: Path, repo_root: Path) -> bool:
    """Check if a path should be excluded."""
    try:
        rel_path = path.relative_to(repo_root)
    except ValueError:
        return True
    
    # Check if any part of the path matches excluded dirs
    parts = rel_path.parts
    if any(part in EXCLUDED_DIRS for part in parts):
        return True

    # Check file extension
    if path.is_file():
        for ext in EXCLUDED_FILE_EXTENSIONS:
            if str(path).endswith(ext):
                return True

    return False


def build_tree(root: Path, repo_root: Path, depth: int = 0) -> list[str]:
    """Build a directory tree structure matching the existing format."""
    lines = []
    indent = "  " * depth

    # Get all items in current directory
    try:
        items = sorted(
            [p for p in root.iterdir() if not should_exclude_path(p, repo_root)],
            key=lambda p: (p.is_file(), p.name.lower()),
        )
    except PermissionError:
        return lines

    for item in items:
        # Get relative path from repo root
        rel_path = item.relative_to(repo_root)
        path_str = str(rel_path).replace("\\", "/")
        
        lines.append(f"{indent}- {path_str}/" if item.is_dir() else f"{indent}- {path_str}")

        if item.is_dir():
            lines.extend(build_tree(item, repo_root, depth + 1))

    return lines


def get_repo_tree(repo_root: Path) -> str:
    """Generate the repository tree structure."""
    # Start with the root directory name
    root_name = repo_root.name if repo_root.name else "."
    tree_lines = [f"- {root_name}/"]
    
    # Build the rest of the tree
    tree_lines.extend(build_tree(repo_root, repo_root, depth=1))
    
    return "\n".join(tree_lines)


def read_file_content(file_path: Path) -> str:
    """Read file content, handling encoding issues."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"# Error reading file: {e}"


def generate_gitingest(repo_root: Path, output_path: Path) -> None:
    """Generate the gitingest.md file."""
    print(f"Generating gitingest.md from {repo_root}...")

    # Get git info
    branch, commit = get_git_info()
    # Format timestamp with timezone (matching original format)
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    # Generate repo tree
    print("Building repository tree...")
    repo_tree = get_repo_tree(repo_root)

    # Build the markdown content
    content_parts = [
        "# Procedure Suite — gitingest (curated)",
        "",
        f"Generated: `{timestamp}`",
        f"Git: `{branch}` @ `{commit}`",
        "",
        "## What this file is",
        "- A **token-budget friendly** snapshot of the repo **structure** + a curated set of **important files**.",
        "- Intended for LLM/context ingestion; excludes large artifacts (models, datasets, caches).",
        "",
        "## Exclusions (high level)",
        f"- Directories: `{', '.join(sorted(EXCLUDED_DIRS))}`",
        f"- File types: `{'`, `'.join(sorted(EXCLUDED_FILE_EXTENSIONS))}`",
        "",
        "## Repo tree (pruned)",
        "```",
        repo_tree,
        "```",
        "",
        "## Important directories (not inlined)",
    ]

    # Add important directories
    for dir_name in IMPORTANT_DIRS:
        content_parts.append(f"- `{dir_name}`")

    content_parts.extend([
        "",
        "## Important files (inlined)",
        "",
    ])

    # Add important files
    print("Inlining important files...")
    for file_path_str in IMPORTANT_FILES:
        file_path = repo_root / file_path_str
        if file_path.exists():
            print(f"  Reading {file_path_str}...")
            file_content = read_file_content(file_path)
            content_parts.extend([
                "---",
                f"### `{file_path_str}`",
                "```",
                file_content,
                "```",
                "",
            ])
        else:
            print(f"  Warning: {file_path_str} not found, skipping...")

    # Write the file
    print(f"Writing to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content_parts))

    print(f"✅ Successfully generated {output_path}")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / "gitingest.md"

    generate_gitingest(repo_root, output_path)


if __name__ == "__main__":
    main()
