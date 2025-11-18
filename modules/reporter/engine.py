"""Structured report engine that wraps LLM inference and templating."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Protocol, Any

import httpx
from google.auth import default as google_auth_default
from google.auth.transport.requests import Request as GoogleAuthRequest
from jinja2 import Environment, FileSystemLoader, select_autoescape

from modules.common.logger import get_logger
from . import prompts
from .schema import StructuredReport

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
logger = get_logger("reporter")


class LLMInterface(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class GeminiLLM:
    """Implementation of LLMInterface using Google's Gemini API via HTTP.
    
    Supports both API key and OAuth2/service account authentication.
    - API key: Pass api_key parameter
    - OAuth2: Set GEMINI_USE_OAUTH=true and configure Google Cloud credentials
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-1.5-flash",
        use_oauth: bool | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        # Determine authentication method
        if use_oauth is None:
            use_oauth = os.getenv("GEMINI_USE_OAUTH", "").lower() in ("true", "1", "yes")
        
        self.use_oauth = use_oauth
        
        if self.use_oauth:
            if api_key:
                logger.warning("Both API key and OAuth enabled. Using OAuth authentication.")
            logger.info("Using OAuth2/service account authentication for Gemini API")
            self._credentials = None
            self._refresh_credentials()
        elif not api_key:
            raise ValueError("Either api_key must be provided or use_oauth must be True")

    def _refresh_credentials(self) -> None:
        """Refresh OAuth2 credentials using Application Default Credentials."""
        try:
            credentials, _ = google_auth_default()
            # Ensure we have a valid token
            if not credentials.valid:
                credentials.refresh(GoogleAuthRequest())
            self._credentials = credentials
            logger.debug("OAuth2 credentials refreshed successfully")
        except Exception as e:
            logger.error(f"Failed to obtain OAuth2 credentials: {e}")
            raise RuntimeError(
                "OAuth2 authentication failed. Ensure you have:\n"
                "1. Set up Application Default Credentials (gcloud auth application-default login), or\n"
                "2. Set GOOGLE_APPLICATION_CREDENTIALS to a service account JSON file, or\n"
                "3. Running on GCP with appropriate IAM roles"
            ) from e

    def _get_access_token(self) -> str:
        """Get a valid OAuth2 access token."""
        if not self._credentials or not self._credentials.valid:
            self._refresh_credentials()
        return self._credentials.token  # type: ignore[return-value]

    def generate(self, prompt: str) -> str:
        if self.use_oauth:
            url = f"{self.base_url}/{self.model}:generateContent"
            access_token = self._get_access_token()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
        else:
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        
        try:
            logger.info(f"Sending request to Gemini model: {self.model} (auth: {'OAuth2' if self.use_oauth else 'API key'})")
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Extract text from response structure
                # { "candidates": [ { "content": { "parts": [ { "text": "..." } ] } } ] }
                candidates = data.get("candidates", [])
                if not candidates:
                    logger.error("No candidates returned from Gemini API")
                    return "{}"
                
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return text
        except httpx.RequestError as e:
            logger.error(f"Network error contacting Gemini API: {e}")
            return "{}"
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Gemini API: {e.response.text}")
            return "{}"
        except Exception as e:
            logger.error(f"Unexpected error in GeminiLLM: {e}")
            return "{}"


class DeterministicStubLLM:
    """Simple deterministic LLM stub used for tests and local runs."""

    def __init__(self, payload: dict | None = None) -> None:
        self.payload = payload or {
            "indication": "Peripheral nodule",
            "anesthesia": "Moderate Sedation",
            "survey": ["Airways inspected"],
            "localization": "Navigated to RUL",
            "sampling": ["EBUS 4R"],
            "therapeutics": ["Stent RMB"],
            "complications": [],
            "disposition": "Home",
        }

    def generate(self, prompt: str) -> str:
        logger.warning("Using DeterministicStubLLM. Set GEMINI_API_KEY for real inference.")
        return json.dumps(self.payload)


class ReportEngine:
    """Handles NL→structured conversion, validation, and rendering."""

    def __init__(self, llm: LLMInterface | None = None) -> None:
        if llm:
            self.llm = llm
        else:
            use_oauth = os.getenv("GEMINI_USE_OAUTH", "").lower() in ("true", "1", "yes")
            api_key = os.getenv("GEMINI_API_KEY")
            
            if use_oauth:
                logger.info("Initializing GeminiLLM with OAuth2/service account authentication.")
                try:
                    self.llm = GeminiLLM(use_oauth=True)
                except Exception as e:
                    logger.error(f"Failed to initialize OAuth2 authentication: {e}")
                    logger.warning("Falling back to DeterministicStubLLM.")
                    self.llm = DeterministicStubLLM()
            elif api_key:
                logger.info("Initializing GeminiLLM with API key from environment.")
                self.llm = GeminiLLM(api_key=api_key)
            else:
                logger.warning("GEMINI_API_KEY not found and GEMINI_USE_OAUTH not set. Falling back to DeterministicStubLLM.")
                self.llm = DeterministicStubLLM()

        self._jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(enabled_extensions=("jinja", "md")),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def from_free_text(self, note: str) -> StructuredReport:
        logger.info(f"Generating report from note (length: {len(note)})")
        prompt_text = prompts.build_prompt(note)
        raw = self.llm.generate(prompt_text)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON. Falling back to default.")
            payload = self._fallback_payload()
        
        payload = self._normalize_payload(payload)
        report = StructuredReport(**payload)
        return self.validate_and_autofix(report)

    def validate_and_autofix(self, report: StructuredReport) -> StructuredReport:
        data = report.model_dump()
        for key in ("survey", "sampling", "therapeutics", "complications"):
            value = data.get(key)
            if not isinstance(value, list):
                data[key] = []
        for field in ("indication", "anesthesia", "localization", "disposition"):
            if not data.get(field):
                data[field] = "Unknown"

        if "stent" in " ".join(data["therapeutics"]).lower() and not data["sampling"]:
            data["sampling"].append("Stent site documented")

        return StructuredReport(**data)

    def render(self, report: StructuredReport, template: str = "bronchoscopy") -> str:
        template_name = {
            "bronchoscopy": "bronchoscopy_synoptic.md.jinja",
            "pleural": "pleural_synoptic.md.jinja",
            "blvr": "blvr_synoptic.md.jinja",
        }.get(template, template)
        tpl = self._jinja_env.get_template(template_name)
        return tpl.render(report=report)

    @staticmethod
    def _fallback_payload() -> dict:
        return {
            "indication": "Unknown",
            "anesthesia": "Unknown",
            "survey": [],
            "localization": "Unknown",
            "sampling": [],
            "therapeutics": [],
            "complications": [],
            "disposition": "Unknown",
        }

    @staticmethod
    def _normalize_payload(payload: dict | object) -> dict:
        if not isinstance(payload, dict):
            return ReportEngine._fallback_payload()
        data = ReportEngine._fallback_payload() | payload
        for key in ("survey", "sampling", "therapeutics", "complications"):
            value = data.get(key)
            if isinstance(value, list):
                continue
            if value in (None, ""):
                data[key] = []
            else:
                data[key] = [str(value)]
        return data


class ReporterEngine(ReportEngine):
    """Compatibility shim exposing a ReporterEngine-friendly signature."""

    def __init__(self, model: LLMInterface | None = None) -> None:
        super().__init__(llm=model)


__all__ = ["ReportEngine", "ReporterEngine", "DeterministicStubLLM", "LLMInterface", "GeminiLLM"]

