"LLM client infrastructure shared across modules."

from __future__ import annotations

import json
import os
from typing import Any, Protocol, TypeVar

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel
try:
    from google.auth import default as google_auth_default
    from google.auth.transport.requests import Request as GoogleAuthRequest
except ImportError:  # google-auth is optional unless OAuth is used
    google_auth_default = None  # type: ignore[assignment]
    GoogleAuthRequest = None  # type: ignore[assignment]

from modules.common.logger import get_logger

logger = get_logger("common.llm")

# Load environment variables from a .env file if present so GEMINI_* keys are available locally.
# Override=True ensures .env values take precedence over stale shell exports.
load_dotenv(override=True)


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def _normalize_openai_base_url(base_url: str | None) -> str:
    normalized = (base_url or "").strip().rstrip("/")
    if normalized.endswith("/v1"):
        normalized = normalized[:-3].rstrip("/")
    return normalized or "https://api.openai.com"


def _resolve_openai_model(task: str | None) -> str:
    task_key = (task or "").strip().lower()
    if task_key == "summarizer":
        return (os.getenv("OPENAI_MODEL_SUMMARIZER") or os.getenv("OPENAI_MODEL") or "").strip()
    if task_key == "structurer":
        return (os.getenv("OPENAI_MODEL_STRUCTURER") or os.getenv("OPENAI_MODEL") or "").strip()
    if task_key == "judge":
        return (os.getenv("OPENAI_MODEL_JUDGE") or os.getenv("OPENAI_MODEL") or "").strip()
    return (os.getenv("OPENAI_MODEL") or "").strip()


class LLMInterface(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class OpenAILLM:
    """Minimal OpenAI chat client for use in self-correction flows."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.1")
        self.base_url = _normalize_openai_base_url(os.getenv("OPENAI_BASE_URL"))

        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set; OpenAILLM calls will fail.")

    def generate(self, prompt: str) -> str:
        if _truthy_env("OPENAI_OFFLINE") or not self.api_key:
            return "{}"

        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            # Encourage JSON output; the prompt should still enforce structure.
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    logger.error("No choices returned from OpenAI API")
                    return "{}"
                return choices[0].get("message", {}).get("content", "")
        except httpx.RequestError as e:
            logger.error(f"Network error contacting OpenAI API: {e}")
            return "{}"
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from OpenAI API: {e.response.text}")
            return "{}"
        except Exception as e:
            logger.error(f"Unexpected error in OpenAILLM: {e}")
            return "{}"


class GeminiLLM:
    """Implementation of LLMInterface using Google's Gemini API via HTTP.
    
    Supports both API key and OAuth2/service account authentication.
    - API key: Pass api_key parameter
    - OAuth2: Set GEMINI_USE_OAUTH=true and configure Google Cloud credentials
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        use_oauth: bool | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
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
        if not google_auth_default or not GoogleAuthRequest:
            raise RuntimeError(
                "google-auth is required for OAuth2 Gemini access. Install google-auth and retry."
            )
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

    def generate(
        self,
        prompt: str,
        response_schema: dict | None = None,
        max_retries: int = 3,
        *,
        temperature: float | None = None,
    ) -> str:
        import time

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

        generation_config: dict[str, Any] = {"response_mime_type": "application/json"}
        if response_schema:
            generation_config["response_schema"] = response_schema
        if temperature is not None:
            generation_config["temperature"] = float(temperature)

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": generation_config
        }

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending request to Gemini model: {self.model} (auth: {'OAuth2' if self.use_oauth else 'API key'}, attempt {attempt + 1}/{max_retries})")
                # Increase timeout to 120s for complex extractions; use separate connect/read timeouts
                timeout = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)
                with httpx.Client(timeout=timeout) as client:
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
                last_error = e
                logger.warning(f"Network error contacting Gemini API (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            except httpx.HTTPStatusError as e:
                # Don't retry on 4xx errors (client errors) - only on 5xx (server errors)
                if e.response.status_code >= 500:
                    last_error = e
                    logger.warning(f"HTTP 5xx error from Gemini API (attempt {attempt + 1}): {e.response.text}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.info(f"Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                else:
                    logger.error(f"HTTP error from Gemini API: {e.response.text}")
                    return "{}"
            except Exception as e:
                logger.error(f"Unexpected error in GeminiLLM: {e}")
                return "{}"

        # All retries exhausted
        logger.error(f"All {max_retries} retries exhausted. Last error: {last_error}")
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

TModel = TypeVar("TModel", bound=BaseModel)


class LLMService:
    """Small helper for structured (JSON) generations.

    This wraps the repo's LLM clients and provides a convenience method that:
    - requests JSON output
    - parses the JSON payload
    - validates it against a Pydantic model
    """

    def __init__(self, llm: LLMInterface | None = None, *, task: str | None = None) -> None:
        if llm is not None:
            self._llm = llm
            return

        use_stub = os.getenv("REGISTRY_USE_STUB_LLM", "").lower() in ("1", "true", "yes")
        use_stub = use_stub or os.getenv("GEMINI_OFFLINE", "").lower() in ("1", "true", "yes")

        if use_stub:
            self._llm = DeterministicStubLLM()
            return

        provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        if provider == "openai_compat":
            openai_offline = _truthy_env("OPENAI_OFFLINE") or not bool(os.getenv("OPENAI_API_KEY"))
            if openai_offline:
                self._llm = DeterministicStubLLM()
                return

            model = _resolve_openai_model(task)
            if not model:
                logger.warning("OPENAI_MODEL not set; falling back to DeterministicStubLLM")
                self._llm = DeterministicStubLLM()
                return

            self._llm = OpenAILLM(api_key=os.getenv("OPENAI_API_KEY"), model=model)
            return

        if provider != "gemini":
            logger.warning("Unknown LLM_PROVIDER='%s'; defaulting to gemini", provider)

        if not os.getenv("GEMINI_API_KEY"):
            self._llm = DeterministicStubLLM()
            return

        self._llm = GeminiLLM()

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[TModel],
        temperature: float = 0.0,
    ) -> TModel:
        prompt = f"{system_prompt.strip()}\n\n{user_prompt.strip()}\n"

        # Prefer prompt-only enforcement for now; Gemini response_schema requires a
        # provider-specific schema shape (see LLMDetailedExtractor for conversion).
        raw = self._generate(prompt, temperature=temperature)
        cleaned = _strip_markdown_code_fences(raw)

        if cleaned.strip() in {"null", "None", ""}:
            raise ValueError("LLM returned null/empty response")

        data = json.loads(cleaned)
        return response_model.model_validate(data)

    def _generate(self, prompt: str, *, temperature: float) -> str:
        llm = self._llm
        if isinstance(llm, GeminiLLM):
            return llm.generate(prompt, temperature=temperature)
        return llm.generate(prompt)


def _strip_markdown_code_fences(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.lstrip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[: -3].strip()
    return cleaned.strip()


__all__ = ["LLMInterface", "GeminiLLM", "OpenAILLM", "DeterministicStubLLM", "LLMService"]
