"""LLM-based detailed extractor for registry data.

Implements a ReAct/self-correction loop around a Pydantic schema to
extract structured registry data from procedure notes.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Optional, Type
import os

from pydantic import BaseModel, ValidationError

from modules.common.llm import DeterministicStubLLM, GeminiLLM
from modules.common.logger import get_logger
from modules.common.sectionizer import Section
from modules.registry.prompts import build_registry_prompt
from modules.registry.slots.base import SlotResult
from config.settings import LLMExtractionConfig
from observability.timing import timed
from observability.logging_config import get_logger as get_obs_logger

logger = get_logger("registry.extractors.llm")
obs_logger = get_obs_logger("llm_extractor")


@dataclass
class ExtractionAttempt:
    """Record of a single extraction attempt."""

    attempt_number: int
    response_text: str
    parsed_data: Optional[dict] = None
    validation_error: Optional[str] = None
    elapsed_ms: float = 0.0
    success: bool = False


@dataclass
class ExtractionResult:
    """Full result of the extraction process with all attempts."""

    value: Optional[dict] = None
    confidence: float = 0.0
    attempts: list[ExtractionAttempt] = field(default_factory=list)
    cache_hit: bool = False
    note_hash: str = ""
    schema_name: str = ""


class NoteHashCache:
    """Simple in-memory cache keyed by note hash + schema name."""

    def __init__(self, max_size: int = 1000):
        self._cache: dict[str, SlotResult] = {}
        self._max_size = max_size

    def _make_key(self, note_hash: str, schema_name: str) -> str:
        return f"{note_hash}:{schema_name}"

    def get(self, note_hash: str, schema_name: str) -> Optional[SlotResult]:
        key = self._make_key(note_hash, schema_name)
        return self._cache.get(key)

    def set(self, note_hash: str, schema_name: str, result: SlotResult) -> None:
        key = self._make_key(note_hash, schema_name)

        # Simple LRU: if at max size, remove oldest entry
        if len(self._cache) >= self._max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[key] = result

    def clear(self) -> None:
        self._cache.clear()


def hash_text(text: str) -> str:
    """Compute a hash of the text for caching."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


class LLMDetailedExtractor:
    """LLM-based extractor with self-correction loop.

    Features:
    - ReAct-style correction loop for validation errors
    - Caching by note hash to avoid redundant LLM calls
    - Fast path for high-confidence first attempts
    - Configurable timeouts and retry limits
    """

    slot_name = "llm_detailed"
    VERSION = "llm_extractor_v2"

    def __init__(
        self,
        llm: GeminiLLM | None = None,
        config: LLMExtractionConfig | None = None,
    ) -> None:
        if llm is not None:
            self.llm = llm
        else:
            use_stub = os.getenv("REGISTRY_USE_STUB_LLM", "").lower() in ("1", "true", "yes")
            use_stub = use_stub or os.getenv("GEMINI_OFFLINE", "").lower() in ("1", "true", "yes")

            if use_stub or not os.getenv("GEMINI_API_KEY"):
                self.llm = DeterministicStubLLM()
            else:
                self.llm = GeminiLLM()

        self.config = config or LLMExtractionConfig()
        self.cache = NoteHashCache()

    @property
    def version(self) -> str:
        return self.VERSION

    def extract(self, text: str, sections: list[Section]) -> SlotResult:
        """Extract registry data from text (legacy interface)."""
        # Filter relevant sections to reduce context window and noise
        relevant_text = self._filter_relevant_text(text, sections)

        prompt = build_registry_prompt(relevant_text)

        try:
            response = self.llm.generate(prompt)
            # Basic cleanup of markdown code blocks if present
            response = self._clean_response(response)
            data = json.loads(response)
            return SlotResult(value=data, evidence=[], confidence=0.9)
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return SlotResult(value=None, evidence=[], confidence=0.0)

    def extract_with_schema(
        self,
        text: str,
        schema: Type[BaseModel],
        sections: list[Section] | None = None,
    ) -> SlotResult:
        """Extract registry data with Pydantic schema validation and self-correction.

        Args:
            text: The procedure note text.
            schema: Pydantic model class for validation.
            sections: Optional pre-parsed sections (to filter text).

        Returns:
            SlotResult with extracted data and confidence.
        """
        # Check cache first
        note_hash = hash_text(text)
        schema_name = schema.__name__

        cached = self.cache.get(note_hash, schema_name)
        if cached is not None:
            obs_logger.debug("Cache hit", extra={"note_hash": note_hash, "schema": schema_name})
            return cached

        # Filter text if sections provided
        if sections:
            relevant_text = self._filter_relevant_text(text, sections)
        else:
            relevant_text = text

        # Run extraction with self-correction loop
        with timed("llm_extractor.extract_with_schema") as timing:
            result = self._extract_with_correction(relevant_text, schema)

        # Build SlotResult
        slot_result = SlotResult(
            value=result.value,
            evidence=[],
            confidence=result.confidence,
        )

        # Cache successful results
        if result.value is not None:
            self.cache.set(note_hash, schema_name, slot_result)

        obs_logger.info(
            "Extraction complete",
            extra={
                "note_hash": note_hash,
                "schema": schema_name,
                "attempts": len(result.attempts),
                "success": result.value is not None,
                "confidence": result.confidence,
                "elapsed_ms": timing.elapsed_ms,
            },
        )

        return slot_result

    def _extract_with_correction(
        self,
        text: str,
        schema: Type[BaseModel],
    ) -> ExtractionResult:
        """Run the extraction with self-correction loop.

        Args:
            text: The text to extract from.
            schema: Pydantic model for validation.

        Returns:
            ExtractionResult with attempts and final value.
        """
        result = ExtractionResult(
            note_hash=hash_text(text),
            schema_name=schema.__name__,
        )

        prompt = self._build_extraction_prompt(text, schema)

        for attempt_num in range(self.config.max_retries + 1):
            start_time = time.perf_counter()

            try:
                response = self.llm.generate(prompt)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                # Clean and parse response
                cleaned = self._clean_response(response)
                data = json.loads(cleaned)

                # Validate against schema
                validated = schema.model_validate(data)

                # Success!
                attempt = ExtractionAttempt(
                    attempt_number=attempt_num + 1,
                    response_text=response,
                    parsed_data=validated.model_dump(),
                    elapsed_ms=elapsed_ms,
                    success=True,
                )
                result.attempts.append(attempt)

                # Fast path: skip correction loop if first attempt is high confidence
                if attempt_num == 0:
                    result.confidence = self.config.fast_path_confidence_threshold
                else:
                    # Degrade confidence with each retry
                    result.confidence = max(0.5, 0.95 - (attempt_num * 0.1))

                result.value = validated.model_dump()
                return result

            except json.JSONDecodeError as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                attempt = ExtractionAttempt(
                    attempt_number=attempt_num + 1,
                    response_text=response if 'response' in locals() else "",
                    validation_error=f"JSON parse error: {e}",
                    elapsed_ms=elapsed_ms,
                )
                result.attempts.append(attempt)

                # Build correction prompt for next attempt
                if attempt_num < self.config.max_retries:
                    prompt = self._build_correction_prompt(prompt, response if 'response' in locals() else "", str(e))

            except ValidationError as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                attempt = ExtractionAttempt(
                    attempt_number=attempt_num + 1,
                    response_text=response if 'response' in locals() else "",
                    parsed_data=data if 'data' in locals() else None,
                    validation_error=str(e),
                    elapsed_ms=elapsed_ms,
                )
                result.attempts.append(attempt)

                # Build correction prompt for next attempt
                if attempt_num < self.config.max_retries:
                    prompt = self._build_correction_prompt(prompt, response if 'response' in locals() else "", str(e))

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                attempt = ExtractionAttempt(
                    attempt_number=attempt_num + 1,
                    response_text=response if 'response' in locals() else "",
                    validation_error=f"Unexpected error: {e}",
                    elapsed_ms=elapsed_ms,
                )
                result.attempts.append(attempt)
                logger.error(f"LLM extraction attempt {attempt_num + 1} failed: {e}")

        # All attempts failed
        result.confidence = 0.0
        return result

    def _filter_relevant_text(self, text: str, sections: list[Section]) -> str:
        """Filter text to relevant sections."""
        relevant_text = ""
        target_headers = ["DESCRIPTION", "PROCEDURE", "FINDINGS", "IMPRESSION", "PLAN", "RECOMMENDATIONS"]

        for section in sections:
            if any(h in section.title.upper() for h in target_headers):
                relevant_text += f"\n\n{section.title}:\n{section.text}"

        # If no relevant sections found, fall back to full text
        if not relevant_text.strip():
            relevant_text = text

        return relevant_text

    def _clean_response(self, response: str) -> str:
        """Clean LLM response by removing markdown code blocks."""
        # Remove markdown code block wrappers
        response = re.sub(r"^```json\s*", "", response, flags=re.MULTILINE)
        response = re.sub(r"^```\s*$", "", response, flags=re.MULTILINE)
        response = re.sub(r"```$", "", response)
        return response.strip()

    def _build_extraction_prompt(self, text: str, schema: Type[BaseModel]) -> str:
        """Build the extraction prompt with schema information."""
        schema_json = schema.model_json_schema()

        return f"""Extract structured data from this procedure note according to the schema below.

Return ONLY valid JSON that conforms to the schema. No other text.

Schema:
{json.dumps(schema_json, indent=2)}

Procedure Note:
{text[:8000]}

JSON Output:"""

    def _build_correction_prompt(
        self,
        original_prompt: str,
        previous_response: str,
        error_message: str,
    ) -> str:
        """Build a correction prompt after a failed attempt."""
        return f"""{original_prompt}

Your previous response had an error:
{error_message}

Previous response:
{previous_response[:1000]}

Please fix the error and return valid JSON:"""
