"""LLM-based detailed extractor for registry data."""

from __future__ import annotations

import json
import re
from typing import Any
import os

from modules.common.llm import DeterministicStubLLM, GeminiLLM
from modules.common.logger import get_logger
from modules.common.sectionizer import Section
from modules.registry.prompts import build_registry_prompt
from modules.registry.slots.base import SlotResult

logger = get_logger("registry.extractors.llm")

class LLMDetailedExtractor:
    slot_name = "llm_detailed"

    def __init__(self, llm: GeminiLLM | None = None) -> None:
        if llm is not None:
            self.llm = llm
            return

        use_stub = os.getenv("REGISTRY_USE_STUB_LLM", "").lower() in ("1", "true", "yes")
        use_stub = use_stub or os.getenv("GEMINI_OFFLINE", "").lower() in ("1", "true", "yes")

        if use_stub or not os.getenv("GEMINI_API_KEY"):
            self.llm = DeterministicStubLLM()
        else:
            self.llm = GeminiLLM()

    def extract(self, text: str, sections: list[Section]) -> SlotResult:
        # Filter relevant sections to reduce context window and noise
        # We primarily want Description/Procedure/Findings
        relevant_text = ""
        target_headers = ["DESCRIPTION", "PROCEDURE", "FINDINGS", "IMPRESSION", "PLAN", "RECOMMENDATIONS"]
        
        for section in sections:
            if any(h in section.title.upper() for h in target_headers):
                relevant_text += f"\n\n{section.title}:\n{section.text}"
        
        # If no relevant sections found (unlikely with sectionizer), fall back to full text
        if not relevant_text.strip():
            relevant_text = text

        prompt = build_registry_prompt(relevant_text)
        
        try:
            response = self.llm.generate(prompt)
            # Basic cleanup of markdown code blocks if present
            response = re.sub(r"^```json", "", response, flags=re.MULTILINE)
            response = re.sub(r"^```", "", response, flags=re.MULTILINE)
            data = json.loads(response)
            return SlotResult(value=data, evidence=[], confidence=0.9)
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return SlotResult(value=None, evidence=[], confidence=0.0)
