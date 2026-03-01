#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops.tools.template_compiler.compiler import (
    CompilerError,
    compile_ip_adaptive_templates,
    default_paths,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile IP adaptive DOCX templates into reporter macros/schema/add-ons.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/template_sources/IP_Comprehensive_Adaptive_Templates.docx"),
        help="Source DOCX path",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write updates to repository files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for pending updates and exit non-zero if changes are needed",
    )
    parser.add_argument(
        "--emit-dir",
        type=Path,
        default=None,
        help="Optional directory for debug artifacts (AST/paragraph stream)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = REPO_ROOT
    paths = default_paths(repo_root)

    try:
        result = compile_ip_adaptive_templates(
            input_docx=args.input,
            repo_root=repo_root,
            schema_path=paths["schema_path"],
            addons_path=paths["addons_path"],
            overrides_path=paths["overrides_path"],
            write=args.write,
            check=args.check,
            emit_dir=args.emit_dir,
        )
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except CompilerError as exc:
        if args.check:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    mode = "write" if args.write else "check" if args.check else "plan"
    print(
        f"compile_ip_adaptive_templates: mode={mode} "
        f"macro_blocks={result.generated_macro_count} addon_blocks={result.generated_addon_count} "
        f"changed_files={len(result.changed_files)}"
    )
    for path in result.changed_files:
        print(f"- {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
