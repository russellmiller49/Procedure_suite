"""LLM Advisor adapter using Gemini API.

Provides CPT code suggestions from the LLM based on procedure note text.
"""

from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from observability.logging_config import get_logger

logger = get_logger("llm_advisor")


@dataclass
class LLMCodeSuggestion:
    """A code suggestion from the LLM advisor."""

    code: str
    confidence: float
    rationale: str


class LLMAdvisorPort(ABC):
    """Abstract port for LLM-based code advisors."""

    @abstractmethod
    def suggest_codes(self, report_text: str) -> list[LLMCodeSuggestion]:
        """Get code suggestions from the LLM.

        Args:
            report_text: The procedure note text to analyze.

        Returns:
            List of code suggestions with confidences.
        """
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the model version identifier."""
        ...


class GeminiAdvisorAdapter(LLMAdvisorPort):
    """Advisor adapter using Google's Gemini API."""

    PROMPT_TEMPLATE = '''You are a medical coding expert specializing in Interventional Pulmonology procedures.
Analyze the following procedure note and suggest appropriate CPT codes.

For each code you suggest, provide:
1. The CPT code
2. Your confidence (0.0-1.0) that this code applies
3. A brief rationale

Only suggest codes from this allowed list: {allowed_codes}

Return your response as a JSON array of objects with keys: code, confidence, rationale

Example format:
[
  {{"code": "31628", "confidence": 0.95, "rationale": "Transbronchial biopsy clearly documented"}},
  {{"code": "31652", "confidence": 0.85, "rationale": "EBUS-TBNA of 2 stations mentioned"}}
]

Procedure Note:
{report_text}

Return ONLY the JSON array, no other text.
'''

    def __init__(
        self,
        model_name: str = "gemini-1.5-pro-002",
        allowed_codes: list[str] | None = None,
        api_key: str | None = None,
    ):
        self.model_name = model_name
        self.allowed_codes = set(allowed_codes) if allowed_codes else set()
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        self._client: Optional[object] = None

    @property
    def version(self) -> str:
        return self.model_name

    def _get_client(self) -> object:
        """Lazily initialize the Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
            except ImportError:
                logger.warning(
                    "google-generativeai not installed. LLM advisor will return empty suggestions."
                )
                return None  # type: ignore
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                return None  # type: ignore

        return self._client

    def suggest_codes(self, report_text: str) -> list[LLMCodeSuggestion]:
        """Get code suggestions from Gemini.

        Args:
            report_text: The procedure note text to analyze.

        Returns:
            List of code suggestions with confidences.
        """
        client = self._get_client()
        if client is None:
            return []

        # Build prompt
        allowed_codes_str = ", ".join(sorted(self.allowed_codes)[:50])  # Limit for prompt size
        prompt = self.PROMPT_TEMPLATE.format(
            allowed_codes=allowed_codes_str,
            report_text=report_text[:8000],  # Limit text size
        )

        try:
            response = client.generate_content(prompt)  # type: ignore
            response_text = response.text

            # Parse JSON response
            suggestions = self._parse_response(response_text)
            return suggestions

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return []

    def _parse_response(self, response_text: str) -> list[LLMCodeSuggestion]:
        """Parse the JSON response from the LLM.

        Args:
            response_text: Raw response text from the LLM.

        Returns:
            List of parsed code suggestions.
        """
        # Try to extract JSON from the response
        try:
            # Handle markdown code blocks
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_text.strip()

            data = json.loads(json_str)

            if not isinstance(data, list):
                logger.warning("LLM response is not a list")
                return []

            suggestions = []
            for item in data:
                if not isinstance(item, dict):
                    continue

                code = str(item.get("code", "")).strip()
                if not code:
                    continue

                # Validate against allowed codes
                if self.allowed_codes and code not in self.allowed_codes:
                    logger.debug(f"Skipping invalid code from LLM: {code}")
                    continue

                confidence = float(item.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]

                rationale = str(item.get("rationale", ""))

                suggestions.append(
                    LLMCodeSuggestion(
                        code=code,
                        confidence=confidence,
                        rationale=rationale,
                    )
                )

            return suggestions

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            return []
        except Exception as e:
            logger.warning(f"Error parsing LLM response: {e}")
            return []


class MockLLMAdvisor(LLMAdvisorPort):
    """Mock advisor for testing without making API calls."""

    def __init__(self, suggestions: list[LLMCodeSuggestion] | None = None):
        self._suggestions = suggestions or []

    @property
    def version(self) -> str:
        return "mock-advisor-v1"

    def suggest_codes(self, report_text: str) -> list[LLMCodeSuggestion]:
        return self._suggestions

    def set_suggestions(self, suggestions: list[LLMCodeSuggestion]) -> None:
        """Set the suggestions to return."""
        self._suggestions = suggestions
