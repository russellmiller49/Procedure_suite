"""Schemas for the SMART on FHIR launch configuration endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SmartIssuerOut(BaseModel):
    """One allowlisted EHR FHIR issuer, as handed to the browser SMART client.

    Everything here is public by design (OAuth public-client identifiers); the
    endpoint must never carry secrets.
    """

    name: str
    iss: str
    client_id: str
    vendor: str
    # Resolved base scopes; the browser prepends `launch` (EHR launch) or
    # `launch/patient` (standalone launch) at authorization time.
    scopes: str


class SmartConfigResponse(BaseModel):
    """Response for GET /api/v1/smart/config."""

    enabled: bool
    issuers: list[SmartIssuerOut] = Field(default_factory=list)
    # Fail-soft configuration problems (bad JSON, rejected issuer entries, ...).
    config_errors: list[str] = Field(default_factory=list)


__all__ = ["SmartConfigResponse", "SmartIssuerOut"]
