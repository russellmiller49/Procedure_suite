"""Read one named API key from a .env file for CLI tools."""

from __future__ import annotations

import os


def load_api_key_from_dotenv(path: str | os.PathLike[str], name: str = "ANTHROPIC_API_KEY") -> bool:
    """Set ``name`` from a .env file if the environment lacks it.

    Only that one entry is read: the app's .env may carry production flags that
    must not leak into CLI tools. Returns whether the key is now available.
    """
    if not os.getenv(name) and os.path.exists(path):
        from dotenv import dotenv_values

        key = dotenv_values(path).get(name)
        if key:
            os.environ[name] = key
    return bool(os.getenv(name))


__all__ = ["load_api_key_from_dotenv"]
