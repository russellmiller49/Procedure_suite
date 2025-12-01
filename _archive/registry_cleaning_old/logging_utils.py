from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal

Severity = Literal["info", "warn", "error"]
Action = Literal["auto_fixed", "flagged_for_manual"]


@dataclass(slots=True)
class IssueLogEntry:
    entry_id: str
    issue_type: str
    severity: Severity
    action: Action
    details: dict[str, Any] | str


class IssueLogger:
    """Collects structured issues across cleaning passes."""

    def __init__(self) -> None:
        self._entries: list[IssueLogEntry] = []

    @property
    def entries(self) -> list[IssueLogEntry]:
        return list(self._entries)

    def log(
        self,
        *,
        entry_id: str,
        issue_type: str,
        severity: Severity,
        action: Action,
        details: dict[str, Any] | str,
    ) -> None:
        self._entries.append(
            IssueLogEntry(
                entry_id=entry_id,
                issue_type=issue_type,
                severity=severity,
                action=action,
                details=details,
            )
        )

    def extend(self, entries: Iterable[IssueLogEntry]) -> None:
        self._entries.extend(entries)

    def write_csv(self, destination: str | Path) -> None:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = ["entry_id", "issue_type", "severity", "action", "details"]
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self._entries:
                writer.writerow(
                    {
                        "entry_id": entry.entry_id,
                        "issue_type": entry.issue_type,
                        "severity": entry.severity,
                        "action": entry.action,
                        "details": _serialize_details(entry.details),
                    }
                )

    def write_json(self, destination: str | Path) -> None:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "entry_id": entry.entry_id,
                "issue_type": entry.issue_type,
                "severity": entry.severity,
                "action": entry.action,
                "details": entry.details,
            }
            for entry in self._entries
        ]
        path.write_text(json.dumps(payload, indent=2))


def derive_entry_id(entry: dict[str, Any], index: int) -> str:
    """Return a stable identifier composed of MRN, date, and record index."""

    mrn = _clean_identifier(str(entry.get("patient_mrn") or "unknown"))
    proc_date = _clean_identifier(str(entry.get("procedure_date") or "unknown"))
    return f"{mrn}_{proc_date}_{index:05d}"


def _serialize_details(details: dict[str, Any] | str) -> str:
    if isinstance(details, str):
        return details
    try:
        return json.dumps(details, sort_keys=True)
    except TypeError:
        return str(details)


def _clean_identifier(value: str) -> str:
    value = value.strip() or "unknown"
    value = re.sub(r"\s+", "-", value)
    return value.replace(",", "-")
