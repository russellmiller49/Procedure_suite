#!/usr/bin/env python3
# ruff: noqa: E402 -- Configure the environment before importing the app.
"""Serve the full app locally with the robotic/EBUS demo page as the home page.

    python ops/tools/run_robotic_ebus_demo.py                # http://127.0.0.1:8020/ui/
    python ops/tools/run_robotic_ebus_demo.py --data-dir DIR  # alternate samples/results

The full app needs the extraction model bundle to boot, so this runs it without
the startup lifespan and marks it ready, the way the API tests do. The demo API
serves stored results only; nothing here calls a model provider.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8020)
    parser.add_argument("--data-dir", help="Demo data directory (samples, redactions, results)")
    parser.add_argument(
        "--home",
        default="robotic_ebus_demo",
        choices=["robotic_ebus_demo", "dashboard"],
        help="Which page answers at /ui/",
    )
    args = parser.parse_args()

    # The app's .env may carry production flags and keys; none are needed here.
    os.environ["PROCSUITE_SKIP_DOTENV"] = "1"
    os.environ.setdefault("PROCSUITE_PIPELINE_MODE", "extraction_first")
    os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")
    os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
    os.environ.setdefault("GEMINI_OFFLINE", "1")
    os.environ.setdefault("PHI_SCRUBBER_MODE", "stub")
    os.environ["PROCSUITE_ROBOTIC_EBUS_DEMO"] = "1"
    os.environ["PROCSUITE_UI_HOME"] = args.home
    if args.data_dir:
        os.environ["PROCSUITE_DEMO_DATA_DIR"] = str(Path(args.data_dir).resolve())

    import uvicorn

    from app.api.fastapi_app import app

    if not (ROOT / "ui/static/phi_redactor/registry_demo/index.html").exists():
        raise SystemExit(
            "Demo page not built: run `npm run build:demo` in ui/source/registry_workbench."
        )
    app.state.model_ready = True
    app.state.model_error = None
    app.state.ready_event = asyncio.Event()
    app.state.ready_event.set()
    print(f"Robotic/EBUS demo: http://{args.host}:{args.port}/ui/", flush=True)
    uvicorn.run(app, host=args.host, port=args.port, lifespan="off", log_level="warning")


if __name__ == "__main__":
    main()
