"LLM client infrastructure shared across modules."

from __future__ import annotations

import json
import os
from typing import Protocol

import httpx
from google.auth import default as google_auth_default
from google.auth.transport.requests import Request as GoogleAuthRequest

from modules.common.logger import get_logger

logger = get_logger("common.llm")


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
        model: str = "gemini-2.5-flash-preview-09-2025",
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
            # Attempt to find key in env if not passed explicitly and not using oauth
            if not api_key:
                self.api_key = os.getenv("GEMINI_API_KEY")
            
            if not self.api_key:
                 # As a fallback for local dev without keys, we might want to allow initialization 
                 # but fail on generate, or let the caller handle it.
                 # For now, we'll log a warning and expect the user to fix it.
                 logger.warning("No GEMINI_API_KEY found and OAuth not enabled.")

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
            if not self.api_key:
                 logger.error("Attempted to generate without API key or OAuth.")
                 return "{}"
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
