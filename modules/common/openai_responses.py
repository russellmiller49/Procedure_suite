"""OpenAI Responses API client wrapper.

This module provides a clean abstraction for the OpenAI Responses API
(POST /v1/responses), which is the primary path for first-party OpenAI calls.

Chat Completions (POST /v1/chat/completions) is kept for compat adapters only.
"""

from __future__ import annotations

import json
import os
import random
import time
from typing import Any, Literal

import httpx

from modules.common.logger import get_logger
from modules.common.exceptions import LLMError
from modules.common.model_capabilities import filter_payload_for_model, is_gpt5

logger = get_logger("common.openai_responses")


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def get_primary_api() -> Literal["responses", "chat"]:
    """Get the primary API to use for OpenAI calls."""
    val = os.getenv("OPENAI_PRIMARY_API", "responses").strip().lower()
    if val == "chat":
        return "chat"
    return "responses"


def is_fallback_enabled() -> bool:
    """Check if fallback from Responses to Chat Completions is enabled."""
    # Default: enabled (1)
    val = os.getenv("OPENAI_RESPONSES_FALLBACK_TO_CHAT", "1").strip().lower()
    return val in ("1", "true", "yes")


def _prepend_json_object_instruction(prompt: str) -> str:
    """Prepend JSON instruction for models that need it."""
    instruction = "Return exactly one JSON object. No markdown. No code fences."
    if instruction.lower() in (prompt or "").lower():
        return prompt
    return f"{instruction}\n\n{prompt}"


def build_responses_payload(
    model: str,
    prompt: str,
    *,
    wants_json: bool = True,
    task: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a payload for the Responses API.

    Args:
        model: The model identifier
        prompt: The user prompt text
        wants_json: Whether JSON output is desired
        task: Task identifier for capability/timeout selection
        extra: Additional parameters to include (capability-filtered)

    Returns:
        A dict suitable for POST /v1/responses
    """
    # For JSON-required paths, use instruction-first approach (PHI-safe)
    outgoing_prompt = prompt
    if wants_json and is_gpt5(model):
        outgoing_prompt = _prepend_json_object_instruction(prompt)

    # Responses API uses "input" field
    # Structure: simple string input or can be wrapped
    payload: dict[str, Any] = {
        "model": model,
        "input": outgoing_prompt,
    }

    # Merge extra params if provided
    if extra:
        for key, value in extra.items():
            if value is not None:
                payload[key] = value

    return payload


def parse_responses_text(resp_json: dict[str, Any]) -> str:
    """Parse the text content from a Responses API response.

    The Responses API may return output in various shapes:
    - {"output": [{"type": "message", "content": [{"type": "text", "text": "..."}]}]}
    - {"output": "..."} (direct text)
    - {"output_text": "..."}

    Args:
        resp_json: The JSON response from the API

    Returns:
        The extracted text content

    Raises:
        ValueError: If no output can be extracted (with safe message, no PHI)
    """
    if not isinstance(resp_json, dict):
        raise ValueError("Responses API returned non-dict response")

    # Try output_text first (simplest form)
    if "output_text" in resp_json:
        return str(resp_json["output_text"])

    output = resp_json.get("output")

    # Direct string output
    if isinstance(output, str):
        return output

    # List of output segments
    if isinstance(output, list):
        texts = []
        for segment in output:
            if isinstance(segment, str):
                texts.append(segment)
            elif isinstance(segment, dict):
                # Handle message-style output
                if segment.get("type") == "message":
                    content = segment.get("content", [])
                    if isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                texts.append(str(part.get("text", "")))
                            elif isinstance(part, str):
                                texts.append(part)
                    elif isinstance(content, str):
                        texts.append(content)
                # Handle text-type directly
                elif segment.get("type") == "text":
                    texts.append(str(segment.get("text", "")))
                # Handle content array directly
                elif "content" in segment:
                    content = segment["content"]
                    if isinstance(content, str):
                        texts.append(content)
                # Fallback: try text field
                elif "text" in segment:
                    texts.append(str(segment["text"]))
        if texts:
            return "".join(texts)

    # Dict output with text field
    if isinstance(output, dict):
        if "text" in output:
            return str(output["text"])
        if "content" in output:
            content = output["content"]
            if isinstance(content, str):
                return content

    raise ValueError("Responses API returned no extractable output")


def parse_responses_json_object(resp_json: dict[str, Any]) -> dict[str, Any] | None:
    """Best-effort parse of JSON object from Responses API response.

    Args:
        resp_json: The JSON response from the API

    Returns:
        Parsed JSON object or None if parsing fails
    """
    try:
        text = parse_responses_text(resp_json)
        if not text or not text.strip():
            return None
        # Strip markdown code fences if present
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.lstrip("`").strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
        return json.loads(cleaned)
    except (ValueError, json.JSONDecodeError):
        return None


def _openai_request_id(response: httpx.Response) -> str | None:
    """Extract request ID from response headers."""
    for header_name in ("x-request-id", "request-id", "x-openai-request-id", "openai-request-id"):
        value = response.headers.get(header_name)
        if value:
            return value
    return None


def _openai_error_details(response: httpx.Response) -> tuple[str, str | None, str | None]:
    """Extract error details from an OpenAI error response (PHI-safe)."""
    message = ""
    error_type: str | None = None
    error_param: str | None = None

    try:
        data = response.json()
    except Exception:  # noqa: BLE001
        data = None

    if isinstance(data, dict):
        err = data.get("error")
        if isinstance(err, dict):
            message = str(err.get("message") or "")
            error_type = str(err.get("type") or "") or None
            error_param = str(err.get("param") or "") or None

    if not message:
        message = str((response.text or "")).strip()

    # Truncate and sanitize
    message = " ".join(message.split())
    if len(message) > 500:
        message = message[:500] + "..."

    if not message:
        message = f"HTTP {response.status_code} from OpenAI"

    return message, error_type, error_param


def _looks_like_unsupported_parameter_error(
    *,
    message: str,
    error_type: str | None,
    error_param: str | None,
) -> bool:
    """Check if error suggests unsupported parameter."""
    if error_param and error_param in {
        "response_format",
        "temperature",
        "top_p",
        "seed",
        "logprobs",
        "tools",
        "tool_choice",
        "parallel_tool_calls",
        "input",
        "instructions",
    }:
        return True

    haystack = f"{error_type or ''} {message}".lower()
    return any(
        token in haystack
        for token in (
            "unsupported",
            "unknown parameter",
            "unrecognized request argument",
            "unrecognized",
            "unexpected",
            "additional properties",
            "extra fields",
            "invalid_request_error",
        )
    )


def _looks_like_endpoint_not_found(
    status_code: int,
    message: str,
) -> bool:
    """Check if error suggests endpoint doesn't exist (for fallback)."""
    if status_code == 404:
        return True
    haystack = message.lower()
    return any(
        token in haystack
        for token in ("not found", "unknown endpoint", "no such", "does not exist")
    )


def _build_responses_retry_payload(
    payload: dict[str, Any],
    *,
    message: str,
    error_param: str | None,
) -> tuple[dict[str, Any], list[str]]:
    """Build retry payload by removing unsupported parameters."""
    retry_payload: dict[str, Any] = dict(payload)
    removed: list[str] = []

    def _pop(key: str) -> None:
        if key in retry_payload:
            retry_payload.pop(key, None)
            removed.append(key)

    # Remove potentially unsupported sampling params
    for key in ("temperature", "top_p", "seed", "max_tokens", "max_completion_tokens"):
        _pop(key)

    # Remove chat-completions-specific params that may have leaked
    for key in ("response_format", "messages"):
        _pop(key)

    return retry_payload, removed


def post_responses(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    *,
    timeout: httpx.Timeout,
    model: str,
) -> dict[str, Any]:
    """POST to Responses API with retry logic.

    Implements:
    - Exactly-one retry on transient timeout/transport errors
    - Exactly-one retry on HTTP 400 unsupported params

    Args:
        url: The full URL for /v1/responses
        headers: Request headers (with auth)
        payload: The request payload
        timeout: httpx.Timeout configuration
        model: Model name (for logging, not payload - payload already has it)

    Returns:
        Parsed JSON response

    Raises:
        LLMError: On failure after retries
        ResponsesEndpointNotFound: If endpoint returns 404 (for fallback)
    """
    removed_on_retry: list[str] = []
    did_retry_timeout = False
    did_retry_unsupported = False

    attempt_payload = payload

    with httpx.Client(timeout=timeout) as client:
        for _ in range(3):  # Max attempts
            try:
                response = client.post(url, headers=headers, json=attempt_payload)
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError, httpx.TransportError) as exc:
                if not did_retry_timeout:
                    did_retry_timeout = True
                    backoff = random.uniform(0.8, 1.5)
                    logger.warning(
                        "Responses API transient transport error; retrying once endpoint=%s model=%s",
                        url,
                        model,
                    )
                    time.sleep(backoff)
                    continue
                raise LLMError(
                    f"Responses API transport error after retry (model={model}): {type(exc).__name__}"
                ) from exc

            if response.status_code < 400:
                return response.json()

            message, error_type, error_param = _openai_error_details(response)
            request_id = _openai_request_id(response)
            request_id_suffix = f" request_id={request_id}" if request_id else ""

            logger.warning(
                "Responses API error status=%s endpoint=%s model=%s%s",
                response.status_code,
                url,
                model,
                request_id_suffix,
            )

            # Check for endpoint not found (for fallback)
            if _looks_like_endpoint_not_found(response.status_code, message):
                raise ResponsesEndpointNotFound(
                    f"Responses endpoint not available (status={response.status_code}, model={model})"
                )

            # Try retry on unsupported param
            should_retry = (
                not did_retry_unsupported
                and response.status_code == 400
                and _looks_like_unsupported_parameter_error(
                    message=message, error_type=error_type, error_param=error_param
                )
            )
            if should_retry:
                retry_payload, removed_on_retry = _build_responses_retry_payload(
                    attempt_payload,
                    message=message,
                    error_param=error_param,
                )
                if removed_on_retry:
                    attempt_payload = retry_payload
                    did_retry_unsupported = True
                    continue

            removed_summary = ", ".join(removed_on_retry) if removed_on_retry else "none"
            raise LLMError(
                f"Responses API request failed (status={response.status_code}, model={model}, "
                f"removed_on_retry={removed_summary}): {message}"
            )

    # Should not reach here, but safety
    raise LLMError(f"Responses API request failed after all attempts (model={model})")


class ResponsesEndpointNotFound(LLMError):
    """Raised when Responses API endpoint is not available (triggers fallback)."""

    pass


__all__ = [
    "get_primary_api",
    "is_fallback_enabled",
    "build_responses_payload",
    "parse_responses_text",
    "parse_responses_json_object",
    "post_responses",
    "ResponsesEndpointNotFound",
]
