"""The one error type the demo API turns into an HTTP response."""

from __future__ import annotations


class DemoError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(code)
        self.status, self.code, self.message = status, code, message


__all__ = ["DemoError"]
