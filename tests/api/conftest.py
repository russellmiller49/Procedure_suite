import os
# Avoid network-bound LLM calls during tests.
os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
os.environ.setdefault("GEMINI_OFFLINE", "1")
os.environ.setdefault("DISABLE_STATIC_FILES", "1")
os.environ.setdefault("PHI_SCRUBBER_MODE", "stub")

import httpx
import pytest_asyncio

from modules.api.fastapi_app import app


@pytest_asyncio.fixture
async def api_client():
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=True)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
