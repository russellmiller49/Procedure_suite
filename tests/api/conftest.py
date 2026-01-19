import asyncio
import os
from types import SimpleNamespace

import httpx
import pytest
import pytest_asyncio

# Avoid network-bound LLM calls during tests.
os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
os.environ.setdefault("GEMINI_OFFLINE", "1")
# UI tests assert `/ui/` is available.
os.environ.setdefault("DISABLE_STATIC_FILES", "0")
os.environ.setdefault("PHI_SCRUBBER_MODE", "stub")

from modules.api.fastapi_app import app


@pytest.fixture(autouse=True)
def setup_app_state():
    """Set up app state for testing without running the full lifespan.

    This fixture ensures the readiness check passes by setting model_ready=True.
    Without this, the require_ready dependency would return 503 since the
    lifespan context manager doesn't run in unit tests.
    """
    # Ensure app.state exists and has required attributes
    if not hasattr(app, "state"):
        app.state = SimpleNamespace()

    app.state.model_ready = True
    app.state.model_error = None
    app.state.ready_event = asyncio.Event()
    app.state.ready_event.set()

    yield

    # Cleanup: reset state after test
    app.state.model_ready = False


@pytest_asyncio.fixture
async def api_client():
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=True)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
