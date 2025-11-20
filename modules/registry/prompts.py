"""Prompts for LLM-based registry extraction."""

from __future__ import annotations

from pathlib import Path

_PROMPT_CACHE: str | None = None


def _load_registry_prompt() -> str:
    """Load and cache the registry system prompt text."""

    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        prompt_path = Path(__file__).with_name("registry_system_prompt.txt")
        _PROMPT_CACHE = prompt_path.read_text().strip()
    return _PROMPT_CACHE


def build_registry_prompt(note_text: str) -> str:
    prompt_text = _load_registry_prompt()
    return f"{prompt_text}\n\nProcedure Note:\n{note_text}"
