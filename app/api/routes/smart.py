"""SMART on FHIR launch support routes.

The only server-side surface of the SMART integration: a public configuration
endpoint that tells the browser UI which EHR issuers (Epic, Oracle Health/Cerner,
sandboxes) are allowlisted and which public client_id/scopes to use for each.

The browser performs the OAuth authorization-code + PKCE flow and all FHIR reads
directly against the EHR; tokens and unredacted note text never reach this server.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas.smart import SmartConfigResponse, SmartIssuerOut
from config.smart_settings import SmartSettings, resolve_scopes

router = APIRouter(tags=["smart"])


@router.get(
    "/v1/smart/config",
    response_model=SmartConfigResponse,
    summary="SMART on FHIR issuer allowlist for the browser launch client",
)
def get_smart_config() -> SmartConfigResponse:
    # Unlike action endpoints (which 503 when disabled), this is a probe the UI hits
    # on page load, so "disabled" is a normal 200 response rather than an error.
    settings = SmartSettings()
    if not settings.enabled:
        return SmartConfigResponse(enabled=False)

    issuers, errors = settings.load_issuers()
    if not issuers and not errors:
        errors = [
            "SMART_ENABLED is set but no issuers are configured "
            "(set SMART_ISSUERS or SMART_ISSUERS_FILE)"
        ]
    return SmartConfigResponse(
        enabled=True,
        issuers=[
            SmartIssuerOut(
                name=issuer.name,
                iss=issuer.iss,
                client_id=issuer.client_id,
                vendor=issuer.vendor,
                scopes=resolve_scopes(issuer, settings.default_scopes),
            )
            for issuer in issuers
        ],
        config_errors=errors,
    )


__all__ = ["router"]
