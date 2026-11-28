"""SMART on FHIR launch configuration (Epic / Oracle Health (Cerner) / SMART sandboxes).

The server-side footprint of the SMART integration is intentionally tiny: a public,
non-secret issuer allowlist that `GET /api/v1/smart/config` hands to the browser UI.
The browser performs the entire OAuth 2.0 authorization-code + PKCE dance and all
FHIR reads (DocumentReference/Binary/Patient/Encounter); access tokens and
unredacted note text never transit this server. That keeps the zero-knowledge
client-side pseudonymization model intact.

Configuration is env-driven and disabled by default:

- ``SMART_ENABLED=1`` turns the feature on.
- ``SMART_ISSUERS`` — inline JSON array of issuer objects (takes precedence), or
- ``SMART_ISSUERS_FILE`` — path to a JSON file with the same array
  (see ``configs/smart/issuers.example.json``).
- ``SMART_DEFAULT_SCOPES`` — optional override of the base scope set.

Issuer entries are validated fail-soft: bad entries are skipped and reported via
``config_errors`` in the API response instead of breaking startup, because SMART is
an optional add-on to the coding engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import AliasChoices, BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings

# Base scopes requested from the EHR authorization server. The browser client adds the
# launch-context scope at runtime (`launch` for EHR launch, `launch/patient` for
# standalone launch), so it is deliberately absent here.
DEFAULT_BASE_SCOPES = (
    "openid fhirUser user/Patient.read user/Encounter.read "
    "user/DocumentReference.read user/Binary.read"
)

SmartVendor = Literal["epic", "cerner", "smart_launcher", "other"]

_LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")


class SmartIssuer(BaseModel):
    """One allowed FHIR issuer (EHR FHIR base URL) and its registered public client."""

    name: str = Field(min_length=1)
    iss: str = Field(min_length=1)
    client_id: str = Field(min_length=1)
    vendor: SmartVendor = "other"
    # Optional per-issuer override of the base scope set (space-separated).
    scopes: str | None = None

    # Operator-authored config: reject unknown keys so typos surface as config_errors.
    model_config = {"extra": "forbid"}


def normalize_iss(iss: str) -> str:
    """Canonical issuer form used for allowlist matching (no trailing slash)."""
    return iss.strip().rstrip("/")


def _validate_iss_url(iss: str) -> str | None:
    """Return an error message when the issuer URL is unusable, else ``None``."""
    parsed = urlparse(iss)
    if parsed.scheme == "https" and parsed.netloc:
        return None
    if parsed.scheme == "http" and parsed.hostname in _LOCAL_HOSTS:
        # Plain http is tolerated only for local development FHIR servers.
        return None
    return f"iss must be an https URL (or http on localhost), got {iss!r}"


def resolve_scopes(issuer: SmartIssuer, default_scopes: str) -> str:
    """Final base scope string for one issuer (before the launch-context scope).

    Cerner (Oracle Health) access tokens are short-lived (~10 minutes), so
    ``online_access`` is appended for that vendor unless already present; it grants a
    refresh token that stays valid for the duration of the EHR user session.
    """
    scopes = (issuer.scopes or default_scopes).strip()
    if issuer.vendor == "cerner" and "online_access" not in scopes.split():
        scopes = f"{scopes} online_access"
    return scopes


class SmartSettings(BaseSettings):
    """Env-driven SMART on FHIR settings (feature-flagged, off by default)."""

    enabled: bool = Field(
        default=False,
        validation_alias=AliasChoices("SMART_ENABLED", "SMART_ON_FHIR_ENABLED"),
    )
    issuers_json: str | None = Field(default=None, validation_alias="SMART_ISSUERS")
    issuers_file: str | None = Field(default=None, validation_alias="SMART_ISSUERS_FILE")
    default_scopes: str = Field(
        default=DEFAULT_BASE_SCOPES, validation_alias="SMART_DEFAULT_SCOPES"
    )

    model_config = {"extra": "ignore"}

    def load_issuers(self) -> tuple[list[SmartIssuer], list[str]]:
        """Parse the issuer allowlist, skipping (and reporting) invalid entries."""
        errors: list[str] = []
        raw_text: str | None = None

        inline = (self.issuers_json or "").strip()
        file_path = (self.issuers_file or "").strip()
        if inline:
            raw_text = inline
            if file_path:
                errors.append(
                    "both SMART_ISSUERS and SMART_ISSUERS_FILE are set; using SMART_ISSUERS"
                )
        elif file_path:
            try:
                raw_text = Path(file_path).read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"SMART_ISSUERS_FILE unreadable ({file_path}): {exc}")
                return [], errors

        if raw_text is None:
            return [], errors

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            errors.append(f"SMART issuers config is not valid JSON: {exc}")
            return [], errors
        if not isinstance(parsed, list):
            errors.append("SMART issuers config must be a JSON array of issuer objects")
            return [], errors

        issuers: list[SmartIssuer] = []
        seen_iss: set[str] = set()
        for idx, entry in enumerate(parsed):
            try:
                issuer = SmartIssuer.model_validate(entry)
            except ValidationError as exc:
                first = exc.errors()[0]
                loc = ".".join(str(part) for part in first.get("loc", ()))
                errors.append(f"issuer[{idx}]: {loc or 'entry'}: {first.get('msg', 'invalid')}")
                continue

            issuer.iss = normalize_iss(issuer.iss)
            url_error = _validate_iss_url(issuer.iss)
            if url_error is not None:
                errors.append(f"issuer[{idx}] ({issuer.name}): {url_error}")
                continue
            if issuer.iss in seen_iss:
                errors.append(f"issuer[{idx}] ({issuer.name}): duplicate iss {issuer.iss}")
                continue

            seen_iss.add(issuer.iss)
            issuers.append(issuer)

        return issuers, errors


__all__ = [
    "DEFAULT_BASE_SCOPES",
    "SmartIssuer",
    "SmartSettings",
    "SmartVendor",
    "normalize_iss",
    "resolve_scopes",
]
