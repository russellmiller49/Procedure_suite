"""LLM Advisor adapter using an OpenAI-compatible Chat Completions API.

Implements the same interface as GeminiAdvisorAdapter but uses an OpenAI-protocol
backend selected via environment variables.
"""

from __future__ import annotations

import json
import os
import re

import httpx

from observability.logging_config import get_logger
from modules.common.model_capabilities import filter_payload_for_model
from modules.common.llm import _resolve_openai_timeout

from .gemini_advisor import LLMAdvisorPort, LLMCodeSuggestion

logger = get_logger("llm_advisor")


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def _normalize_openai_base_url(base_url: str) -> str:
    normalized = (base_url or "").strip().rstrip("/")
    if normalized.endswith("/v1"):
        normalized = normalized[:-3].rstrip("/")
    return normalized or "https://api.openai.com"


def _openai_request_id(response: httpx.Response) -> str | None:
    for header_name in ("x-request-id", "request-id", "x-openai-request-id", "openai-request-id"):
        value = response.headers.get(header_name)
        if value:
            return value
    return None


def _openai_error_details(response: httpx.Response) -> tuple[str, str | None, str | None]:
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

    message = " ".join(message.split())
    if len(message) > 500:
        message = message[:500] + "…"

    if not message:
        message = f"HTTP {response.status_code} from OpenAI"

    return message, error_type, error_param


def _looks_like_unsupported_parameter_error(
    *,
    message: str,
    error_type: str | None,
    error_param: str | None,
) -> bool:
    if error_param and error_param in {
        "response_format",
        "temperature",
        "top_p",
        "seed",
        "logprobs",
        "tools",
        "tool_choice",
        "parallel_tool_calls",
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


def _error_suggests_tools_unsupported(*, message: str, error_param: str | None) -> bool:
    if error_param and error_param in {"tools", "tool_choice", "parallel_tool_calls"}:
        return True
    haystack = message.lower()
    return any(token in haystack for token in (" tools", "tool_choice", "parallel_tool_calls", "function calling"))


def _build_unsupported_param_retry_payload(
    payload: dict,
    *,
    message: str,
    error_param: str | None,
) -> tuple[dict, list[str]]:
    retry_payload: dict = dict(payload)
    removed: list[str] = []

    def _pop(key: str) -> None:
        if key in retry_payload:
            retry_payload.pop(key, None)
            removed.append(key)

    _pop("response_format")
    for key in ("temperature", "top_p", "seed", "logprobs", "top_logprobs"):
        _pop(key)

    if _error_suggests_tools_unsupported(message=message, error_param=error_param):
        for key in ("tools", "tool_choice", "parallel_tool_calls"):
            _pop(key)

    return retry_payload, removed


class OpenAICompatAdvisorAdapter(LLMAdvisorPort):
    """Advisor adapter using an OpenAI-compatible Chat Completions API."""

    PROMPT_TEMPLATE = '''You are a medical coding expert specializing in Interventional Pulmonology procedures.
Analyze the following procedure note and suggest appropriate CPT codes.

IMPORTANT CONSTRAINTS:
- Suggest 31640 (tumor excision) ONLY when explicit resection/debulking language is present. Pure ablation terminology should map to 31641 instead.
- Photodynamic therapy without independent stent/cryotherapy/debulking work → 31641 only; suppress 31635/31649/31651/31654 unless separate interventions are clearly described.
- 31634 (hemorrhage control) should be added when massive/brisk hemoptysis is treated with iced saline, epinephrine/TXA instillation, balloon tamponade, etc.; drop navigation/foreign-body codes unless those tasks are explicitly performed.
- 31654 (Radial EBUS) should only be suggested when targeting a peripheral lung lesion with radial probe localization.
- 31645 vs 31646: routine stent cleaning/surveillance without reposition/exchange supports 31645. Only suggest 31646 when the stent is repositioned, exchanged, upsized/downsized, or removed/replaced.
- Do NOT suggest 31622 (Diagnostic bronchoscopy) if any therapeutic/surgical bronchoscopy code (31625-31661) is applicable.
- 32550 (tunneled pleural catheter) requires documentation of tunnel creation, cuff placement, or brand names (PleurX/Aspira). Planning phrases such as "consider PleurX" do NOT qualify.
- When talc/doxycycline pleurodesis is performed through an existing tube without new tunneled catheter placement, prefer 32560 and suppress 32550.

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

    CONTEXT_PROMPT_TEMPLATE = '''You are the final judge for CPT code assignment in an ML-assisted coding pipeline.

The ML model predicted the following CPT codes with these confidence scores:
{ml_predictions}

ML Classification: {difficulty}
Reason for LLM Review: {reason_for_fallback}

Given the full procedure note below, evaluate whether you agree with the ML suggestions.
If not, explain briefly and provide the corrected list of CPT codes.

IMPORTANT CONSTRAINTS:
- Suggest 31640 (tumor excision) ONLY when explicit resection/debulking language is present.
- 31654 (Radial EBUS) should only be suggested when targeting a peripheral lung lesion.
- Do NOT suggest 31622 (Diagnostic bronchoscopy) if any therapeutic code applies.
- 32550 (tunneled pleural catheter) requires documentation of tunnel creation or brand names.

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

    MAX_TEXT_SIZE = 32000

    def __init__(
        self,
        model_name: str = "",
        allowed_codes: list[str] | None = None,
        api_key: str | None = None,
    ):
        self.model_name = model_name
        self.allowed_codes = set(allowed_codes) if allowed_codes else set()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = _normalize_openai_base_url(os.getenv("OPENAI_BASE_URL", "https://api.openai.com"))
        self._offline = _truthy_env("OPENAI_OFFLINE") or not bool(self.api_key)

    @property
    def version(self) -> str:
        env_model = os.getenv("OPENAI_MODEL", "").strip()
        if env_model:
            return env_model
        if self.model_name and self.model_name.strip():
            return self.model_name.strip()
        if self._offline:
            return "openai_compat_offline_stub"
        return "openai_compat_unconfigured"

    def suggest_codes(self, report_text: str, *, task: str | None = None) -> list[LLMCodeSuggestion]:
        if self._offline:
            return self._offline_suggestions()

        allowed_codes_str = ", ".join(sorted(self.allowed_codes)[:50])
        processed_text = self._prepare_text_for_llm(report_text)
        prompt = self.PROMPT_TEMPLATE.format(
            allowed_codes=allowed_codes_str,
            report_text=processed_text,
        )

        try:
            response_text = self._call_chat(prompt, task=task or "coder")
            return self._parse_response(response_text)
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenAI-compat advisor call failed: %s", type(exc).__name__)
            return []

    def suggest_with_context(
        self,
        report_text: str,
        context: dict,
        *,
        task: str | None = None,
    ) -> list[LLMCodeSuggestion]:
        if self._offline:
            return self._offline_suggestions()

        ml_preds = context.get("ml_predictions", [])
        ml_pred_str = "\n".join(f"  - {p['cpt']}: {p['prob']:.2f}" for p in ml_preds[:10]) or "  (none)"

        difficulty = context.get("difficulty", "unknown")
        reason = context.get("reason_for_fallback", "unknown")

        allowed_codes_str = ", ".join(sorted(self.allowed_codes)[:50])
        processed_text = self._prepare_text_for_llm(report_text)

        prompt = self.CONTEXT_PROMPT_TEMPLATE.format(
            ml_predictions=ml_pred_str,
            difficulty=difficulty,
            reason_for_fallback=reason,
            allowed_codes=allowed_codes_str,
            report_text=processed_text,
        )

        try:
            response_text = self._call_chat(prompt, task=task or "coder")
            return self._parse_response(response_text)
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenAI-compat advisor call with context failed: %s", type(exc).__name__)
            return []

    def _resolve_model(self) -> str:
        env_model = os.getenv("OPENAI_MODEL", "").strip()
        if env_model:
            return env_model
        if self.model_name and self.model_name.strip():
            return self.model_name.strip()
        if self._offline:
            return "openai_compat_offline_stub"
        raise ValueError("OPENAI_MODEL is required unless OPENAI_OFFLINE=1")

    def _call_chat(self, prompt: str, *, task: str | None = None) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict = {
            "model": self._resolve_model(),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        }

        payload = filter_payload_for_model(payload, str(payload.get("model", "")), api_style="chat")

        # Use task-aware timeout (registry extraction gets longer read timeout)
        timeout = _resolve_openai_timeout(task)
        with httpx.Client(timeout=timeout) as client:
            removed_on_retry: list[str] = []
            attempt_payload: dict = payload
            for attempt in range(2):
                response = client.post(url, headers=headers, json=attempt_payload)
                if response.status_code < 400:
                    data = response.json()
                    break

                message, error_type, error_param = _openai_error_details(response)
                request_id = _openai_request_id(response)
                logger.warning(
                    "OpenAI-compat API error",
                    extra={
                        "status": response.status_code,
                        "endpoint": url,
                        "model": attempt_payload.get("model", ""),
                        "request_id": request_id,
                        "openai_error_message": message,
                    },
                )

                should_retry = (
                    attempt == 0
                    and response.status_code == 400
                    and _looks_like_unsupported_parameter_error(
                        message=message, error_type=error_type, error_param=error_param
                    )
                )
                if should_retry:
                    retry_payload, removed_on_retry = _build_unsupported_param_retry_payload(
                        attempt_payload,
                        message=message,
                        error_param=error_param,
                    )
                    if removed_on_retry:
                        attempt_payload = retry_payload
                        continue

                response.raise_for_status()
            else:
                # Defensive: should never reach; loop either breaks or raises.
                raise RuntimeError("OpenAI-compat request failed after retry")

        choices = data.get("choices", []) if isinstance(data, dict) else []
        if not choices:
            return ""
        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content", "") if isinstance(message, dict) else ""
        return content or ""

    def _offline_suggestions(self) -> list[LLMCodeSuggestion]:
        if not self.allowed_codes:
            return []
        code = sorted(self.allowed_codes)[0]
        return [
            LLMCodeSuggestion(
                code=code,
                confidence=0.5,
                rationale="offline_stub",
            )
        ]

    def _prepare_text_for_llm(self, text: str) -> str:
        if len(text) <= self.MAX_TEXT_SIZE:
            return text

        begin_size = int(self.MAX_TEXT_SIZE * 0.4)
        end_size = int(self.MAX_TEXT_SIZE * 0.4)

        begin_text = text[:begin_size]
        end_text = text[-end_size:]

        begin_break = begin_text.rfind(". ")
        if begin_break > begin_size * 0.8:
            begin_text = begin_text[: begin_break + 1]

        end_break = end_text.find(". ")
        if 0 < end_break < end_size * 0.2:
            end_text = end_text[end_break + 2 :]

        truncated_chars = len(text) - len(begin_text) - len(end_text)
        truncation_marker = (
            f"\n\n[... {truncated_chars} characters of detailed procedure content omitted "
            f"due to length. Key procedures may be in this section. ...]\n\n"
        )

        logger.warning(
            "Text truncated for LLM: %d chars -> %d chars (%d chars removed from middle)",
            len(text),
            len(begin_text) + len(end_text),
            truncated_chars,
        )

        return begin_text + truncation_marker + end_text

    def _parse_response(self, response_text: str) -> list[LLMCodeSuggestion]:
        try:
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_text.strip()

            data = json.loads(json_str)

            if not isinstance(data, list):
                logger.warning("LLM response is not a list")
                return []

            suggestions: list[LLMCodeSuggestion] = []
            for item in data:
                if not isinstance(item, dict):
                    continue

                code = str(item.get("code", "")).strip()
                if not code:
                    continue

                if self.allowed_codes and code not in self.allowed_codes:
                    logger.debug("Skipping invalid code from LLM: %s", code)
                    continue

                confidence = float(item.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))

                rationale = str(item.get("rationale", ""))

                suggestions.append(
                    LLMCodeSuggestion(
                        code=code,
                        confidence=confidence,
                        rationale=rationale,
                    )
                )

            return suggestions

        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON")
            return []
        except Exception:
            logger.warning("Error parsing LLM response")
            return []


__all__ = ["OpenAICompatAdvisorAdapter"]
