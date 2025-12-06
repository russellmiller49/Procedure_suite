"""Mapping from EBUS node evidence to CPT code candidates."""

from __future__ import annotations

from typing import Iterable, Sequence, Tuple

from modules.coder.types import CodeCandidate, EBUSNodeEvidence


def _normalize_station(station: str) -> str:
    return station.strip().upper()


def _normalize_method(method: str | None) -> str:
    return (method or "").strip().lower()


def _count_sampled_nodes(evidence: Iterable[EBUSNodeEvidence]) -> int:
    """Count unique sampled stations (optionally grouped by method)."""
    sampled_keys: set[Tuple[str, str]] = set()

    for entry in evidence:
        if entry.action != "Sampling":
            continue
        station = _normalize_station(entry.station)
        if not station:
            continue
        method = _normalize_method(entry.method)
        sampled_keys.add((station, method))

    return len(sampled_keys)


def ebus_nodes_to_candidates(evidence: Sequence[EBUSNodeEvidence]) -> list[CodeCandidate]:
    """Map EBUS node sampling counts to CPT code candidates."""
    sampled_count = _count_sampled_nodes(evidence)
    if sampled_count == 0:
        return []

    if 1 <= sampled_count <= 2:
        code = "31652"
    else:
        code = "31653"

    reason = f"ebus_nodes:sampled_count={sampled_count}"
    return [CodeCandidate(code=code, confidence=0.9, reason=reason)]


__all__ = ["ebus_nodes_to_candidates", "_count_sampled_nodes"]
