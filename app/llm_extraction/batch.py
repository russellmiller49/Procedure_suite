"""Message Batches helpers: submit, wait, collect (half price, no latency guarantee).

Results arrive in any order and are keyed by ``custom_id``. Batch requests cannot
use server-side refusal fallbacks, so a refusal is simply a failed item.
"""

from __future__ import annotations

import re
import time
from typing import Any, Callable, Iterable

from app.common.anthropic_client import PROVIDER
from app.common.llm_egress import assert_egress_allowed

_CUSTOM_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def submit(sdk: Any, items: Iterable[tuple[str, dict[str, Any]]]) -> str:
    assert_egress_allowed(PROVIDER)
    requests = []
    for custom_id, params in items:
        if not _CUSTOM_ID.match(custom_id):
            raise ValueError(f"invalid batch custom_id: {custom_id!r}")
        requests.append({"custom_id": custom_id, "params": params})
    if not requests:
        raise ValueError("empty batch")
    return sdk.messages.batches.create(requests=requests).id


def wait(
    sdk: Any,
    batch_id: str,
    *,
    poll_seconds: float = 60.0,
    timeout_seconds: float = 24 * 3600.0,
    sleep: Callable[[float], None] = time.sleep,
    on_poll: Callable[[Any], None] | None = None,
) -> Any:
    deadline = time.monotonic() + timeout_seconds
    while True:
        batch = sdk.messages.batches.retrieve(batch_id)
        if on_poll is not None:
            on_poll(batch)
        if batch.processing_status == "ended":
            return batch
        if time.monotonic() > deadline:
            raise TimeoutError(f"batch {batch_id} still {batch.processing_status}")
        sleep(poll_seconds)


def collect(sdk: Any, batch_id: str) -> tuple[dict[str, Any], dict[str, str]]:
    """Return (messages by custom_id, error type by custom_id)."""
    messages, errors = {}, {}
    for entry in sdk.messages.batches.results(batch_id):
        result = entry.result
        if result.type == "succeeded":
            messages[entry.custom_id] = result.message
        else:
            errors[entry.custom_id] = result.type
    return messages, errors


__all__ = ["collect", "submit", "wait"]
