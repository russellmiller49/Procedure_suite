"""Metrics endpoint for Prometheus scraping.

This module provides a /metrics endpoint that exports application metrics
in Prometheus text format (when METRICS_BACKEND=registry or prometheus).

Configuration:
    METRICS_BACKEND: Set to "registry" or "prometheus" to enable metrics collection
    METRICS_ENABLED: Set to "true" to expose the /metrics endpoint (default: true if registry)

Usage:
    # Enable metrics collection
    export METRICS_BACKEND=prometheus

    # Scrape metrics
    curl http://localhost:8000/metrics
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from observability.metrics import get_metrics_client, RegistryMetricsClient
from observability.logging_config import get_logger

router = APIRouter()
logger = get_logger("metrics_api")

# Content type for Prometheus text format
PROMETHEUS_CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"


def _is_metrics_enabled() -> bool:
    """Check if metrics endpoint should be enabled."""
    # Enabled if METRICS_BACKEND is registry/prometheus, or if METRICS_ENABLED=true
    backend = os.getenv("METRICS_BACKEND", "null").lower()
    explicit = os.getenv("METRICS_ENABLED", "").lower()
    if explicit in ("true", "1", "yes"):
        return True
    if explicit in ("false", "0", "no"):
        return False
    # Default: enable if using registry backend
    return backend in ("registry", "prometheus")


@router.get(
    "/metrics",
    summary="Prometheus metrics endpoint",
    description="Export application metrics in Prometheus text format.",
    response_class=PlainTextResponse,
)
def get_metrics() -> Response:
    """Export metrics for Prometheus scraping.

    Returns:
        - 200 with Prometheus text format if metrics are enabled and using registry backend
        - 200 with JSON summary if metrics are enabled but not using registry backend
        - 404 if metrics endpoint is disabled

    The response format depends on the configured METRICS_BACKEND:
    - registry/prometheus: Prometheus text exposition format
    - stdout: JSON summary of last values
    - null: 404 with disabled message
    """
    if not _is_metrics_enabled():
        return PlainTextResponse(
            content="# Metrics endpoint disabled. Set METRICS_BACKEND=prometheus to enable.\n",
            status_code=404,
            media_type="text/plain",
        )

    client = get_metrics_client()

    if isinstance(client, RegistryMetricsClient):
        # Export in Prometheus text format
        content = client.export_prometheus()
        return Response(
            content=content,
            media_type=PROMETHEUS_CONTENT_TYPE,
        )
    else:
        # For other clients, return a helpful message
        return PlainTextResponse(
            content=(
                "# Metrics collection is not using registry backend.\n"
                "# Set METRICS_BACKEND=prometheus for Prometheus-compatible output.\n"
                f"# Current backend: {type(client).__name__}\n"
            ),
            media_type="text/plain",
        )


@router.get(
    "/metrics/json",
    summary="Metrics as JSON",
    description="Export application metrics as JSON (for debugging).",
)
def get_metrics_json() -> dict[str, Any]:
    """Export metrics as JSON for debugging.

    Returns:
        JSON object with counters, gauges, and histograms.
        Empty dicts if not using registry backend.
    """
    if not _is_metrics_enabled():
        return {"error": "Metrics disabled", "enabled": False}

    client = get_metrics_client()

    if isinstance(client, RegistryMetricsClient):
        return {
            "enabled": True,
            "backend": "registry",
            **client.export_json(),
        }
    else:
        return {
            "enabled": True,
            "backend": type(client).__name__,
            "counters": {},
            "gauges": {},
            "histograms": {},
            "note": "JSON export only available with registry backend",
        }


@router.get(
    "/metrics/status",
    summary="Metrics status",
    description="Check metrics collection status.",
)
def get_metrics_status() -> dict[str, Any]:
    """Get metrics collection status.

    Returns:
        Status information about metrics collection.
    """
    backend = os.getenv("METRICS_BACKEND", "null")
    client = get_metrics_client()

    status: dict[str, Any] = {
        "enabled": _is_metrics_enabled(),
        "backend": backend,
        "client_type": type(client).__name__,
    }

    if isinstance(client, RegistryMetricsClient):
        with client._lock:
            status["counters_count"] = len(client._counters)
            status["gauges_count"] = len(client._gauges)
            status["histograms_count"] = len(client._histograms)

    return status
