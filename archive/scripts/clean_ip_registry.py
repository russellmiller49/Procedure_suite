from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.registry_cleaning import (  # noqa: E402
    CPTProcessor,
    ClinicalQCChecker,
    ConsistencyChecker,
    IssueLogger,
    SchemaNormalizer,
    derive_entry_id,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean and audit registry data entries")
    parser.add_argument("--registry-data", required=True, help="Path to registry JSON/JSONL input")
    parser.add_argument(
        "--schema",
        "--registry-schema",
        dest="schema",
        default=_default_schema_path(),
        help="Path to the registry JSON schema",
    )
    parser.add_argument(
        "--coding-kb",
        "--kb",
        dest="coding_kb",
        default=_default_kb_path(),
        help="Path to the IP coding/billing knowledge base",
    )
    parser.add_argument(
        "--output-json",
        default="cleaned_registry_data.json",
        help="Destination for cleaned registry data",
    )
    parser.add_argument(
        "--issues-log",
        default="issues_log.csv",
        help="Destination CSV for the issue log",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registry_entries = _load_registry_entries(Path(args.registry_data))
    logger = IssueLogger()
    schema = SchemaNormalizer(args.schema)
    cpt = CPTProcessor(args.coding_kb)
    consistency = ConsistencyChecker()
    clinical = ClinicalQCChecker()

    cleaned_entries: list[dict[str, Any]] = []
    for idx, entry in enumerate(registry_entries):
        entry_id = derive_entry_id(entry, idx)
        if not isinstance(entry, dict):
            logger.log(
                entry_id=entry_id,
                issue_type="invalid_entry",
                severity="error",
                action="flagged_for_manual",
                details="Entry is not a JSON object",
            )
            continue
        cleaned = schema.normalize_entry(entry, entry_id, logger)
        cpt_context = cpt.process_entry(cleaned, entry_id, logger)
        consistency.apply(cleaned, entry_id, logger)
        clinical.check(cleaned, cpt_context, entry_id, logger)
        schema.validate_entry(cleaned, entry_id, logger)
        cleaned_entries.append(cleaned)

    _write_json(Path(args.output_json), cleaned_entries)
    logger.write_csv(Path(args.issues_log))
    _print_summary(cleaned_entries, logger, args.output_json, args.issues_log)


def _load_registry_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Registry data not found: {path}")
    format_name, raw_items = _read_json_payload(path)
    entries: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        if isinstance(item.get("registry_entry"), dict):
            entries.append(item["registry_entry"])
        else:
            entries.append(item)
    print(f"[RegistryCleaner] Loaded {len(entries)} entries from {path} (format={format_name})")
    return entries


def _read_json_payload(path: Path) -> Tuple[str, list[Any]]:
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        payload: list[Any] = []
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            payload.append(json.loads(line))
        return "ndjson", payload
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return "json_array", data
    if isinstance(data, dict):
        entries = data.get("entries")
        if isinstance(entries, list):
            return "json_object_entries", entries
    raise ValueError("Registry data must be an array, NDJSON file, or object with an 'entries' array")


def _write_json(path: Path, payload: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def _print_summary(entries: list[dict[str, Any]], logger: IssueLogger, output_path: str, log_path: str) -> None:
    summary = logger.summarize_by_action()
    print(f"Processed {len(entries)} entries -> {output_path}")
    print(f"Captured {len(logger.entries)} issues -> {log_path}")
    for action in ("auto_fixed", "flagged_for_manual"):
        counts = summary.get(action, {})
        if not counts:
            continue
        print(f"{action.replace('_', ' ').title()} issues:")
        for issue_type, count in sorted(counts.items()):
            print(f"  - {issue_type}: {count}")
    error_entries = logger.error_entry_ids()
    print(f"Entries with severity=error: {len(error_entries)}")


def _default_schema_path() -> str:
    candidates = [
        "schemas/IP_Registry.json",
        "data/knowledge/IP_Registry.json",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return candidates[-1]


def _default_kb_path() -> str:
    candidates = [
        "data/knowledge/ip_coding_billing_v2_8.json",
        "data/ip_coding_billing.v2_3.json",
        "data/ip_coding_billing.v2_2.json",
        "data/knowledge/ip_coding_billing.v2_2.json",
        "proc_autocode/ip_kb/ip_coding_billing.v2_2.json",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return candidates[-1]


if __name__ == "__main__":
    main()
