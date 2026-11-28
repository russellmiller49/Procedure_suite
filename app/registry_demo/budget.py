"""Spend cap and request limits for the tester path.

The ledger is one small JSON file per UTC day, updated under a file lock so every
server worker shares it. It holds amounts only. A dedicated API key with a
provider-side spending limit is still the hard stop; this keeps an ordinary day
inside the amount the owner chose.
"""

from __future__ import annotations

import fcntl
import json
import threading
import time
from collections import deque
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

from app.registry_demo import settings


def _ledger_path() -> Path:
    directory = settings.state_dir()
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"spend-{datetime.now(UTC):%Y-%m-%d}.json"


@contextmanager
def _locked() -> Iterator[dict[str, float]]:
    with open(_ledger_path(), "a+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            handle.seek(0)
            raw = handle.read()
            try:
                state = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError:
                state = {}
            ledger = {
                "spent": float(state.get("spent") or 0.0),
                "reserved": float(state.get("reserved") or 0.0),
            }
            yield ledger
            handle.seek(0)
            handle.truncate()
            handle.write(json.dumps({k: round(v, 6) for k, v in ledger.items()}))
            handle.flush()
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def reserve(amount: float) -> bool:
    """Hold ``amount`` against today's cap; False when the cap would be passed."""
    with _locked() as ledger:
        if ledger["spent"] + ledger["reserved"] + amount > settings.daily_usd_cap() + 1e-9:
            return False
        ledger["reserved"] += amount
        return True


def settle(reserved: float, actual: float | None) -> None:
    """Release a hold and record what the call cost (the whole hold when unknown)."""
    with _locked() as ledger:
        ledger["reserved"] = max(0.0, ledger["reserved"] - reserved)
        ledger["spent"] += reserved if actual is None else max(0.0, actual)


def spent_today() -> float:
    with _locked() as ledger:
        return ledger["spent"]


class RateLimit:
    """At most ``limit`` events per ``window_s`` seconds for one key, per worker."""

    def __init__(self, limit: int, window_s: float) -> None:
        self.limit, self.window_s = limit, window_s
        self._events: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def _recent(self, key: str, now: float) -> deque[float]:
        events = self._events.setdefault(key, deque())
        while events and now - events[0] > self.window_s:
            events.popleft()
        return events

    def blocked(self, key: str) -> bool:
        with self._lock:
            return len(self._recent(key, time.monotonic())) >= self.limit

    def record(self, key: str) -> None:
        with self._lock:
            now = time.monotonic()
            self._recent(key, now).append(now)
            if len(self._events) > 5000:  # forget idle keys
                for idle in [k for k, v in self._events.items() if not v]:
                    del self._events[idle]

    def allow(self, key: str) -> bool:
        """Record the event and say whether it is within the limit."""
        with self._lock:
            now = time.monotonic()
            events = self._recent(key, now)
            if len(events) >= self.limit:
                return False
            events.append(now)
            return True

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


__all__ = ["RateLimit", "reserve", "settle", "spent_today"]
