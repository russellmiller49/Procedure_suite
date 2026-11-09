#!/usr/bin/env python3
# ruff: noqa: E402 -- Configure the environment before importing the workbench.
"""Serve the synthetic registry workbench on its own (API + review UI).

The full app also mounts the workbench when PROCSUITE_WORKBENCH_ENABLED=1, but it
needs the extraction model bundle to boot; this serves only the workbench.

    python ops/tools/seed_registry_workbench.py --splits validation
    python ops/tools/run_registry_workbench.py            # http://127.0.0.1:8010/workbench/

Claude runs need ANTHROPIC_API_KEY (from the environment, or the .env entry of that name).
"""

from __future__ import annotations

import argparse
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
    parser.add_argument("--port", type=int, default=8010)
    parser.add_argument(
        "--database-url", help="Default: REGISTRY_WORKBENCH_DATABASE_URL or ./registry_workbench.db"
    )
    args = parser.parse_args()

    # Take only the API key from .env: the app's .env may carry production flags
    # (e.g. CODER_REQUIRE_PHI_REVIEW) that correctly keep the workbench off.
    from app.common.anthropic_client import load_api_key_from_dotenv

    load_api_key_from_dotenv(ROOT / ".env")
    os.environ.setdefault("PROCSUITE_WORKBENCH_ENABLED", "1")
    if args.database_url:
        os.environ["REGISTRY_WORKBENCH_DATABASE_URL"] = args.database_url

    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import RedirectResponse
    from fastapi.staticfiles import StaticFiles

    from app.registry_workbench.db import database_url
    from app.registry_workbench.routes import router
    from app.registry_workbench.settings import workbench_enabled

    if not workbench_enabled():
        raise SystemExit(
            "The workbench is disabled in production (PROCSUITE_ENV / CODER_REQUIRE_PHI_REVIEW)."
        )
    static = ROOT / "ui/static/registry_workbench"
    if not (static / "index.html").exists():
        raise SystemExit("UI not built: run `make workbench-ui-build`.")

    app = FastAPI(title="Robotic/EBUS registry workbench (synthetic)")
    app.include_router(router, prefix="/api/v1/workbench")
    app.mount("/workbench", StaticFiles(directory=str(static), html=True), name="workbench")

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse("/workbench/")

    print(
        f"Registry workbench on http://{args.host}:{args.port}/workbench/  (database: {database_url()})"
    )
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
