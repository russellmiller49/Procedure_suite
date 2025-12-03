import json
from collections import defaultdict
from pathlib import Path


def main():
    error_path = Path("data/registry_errors.jsonl")
    summary_path = Path("reports/registry_error_summary.json")

    if not error_path.exists():
        print(f"No error log found at {error_path}. Run make validate-registry first.")
        return

    summary_path.parent.mkdir(parents=True, exist_ok=True)

    field_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    with error_path.open() as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            field = entry.get("field_name", "unknown")
            key = f"{entry.get('gold_value')} vs {entry.get('predicted_value')}"
            field_counts[field][key] += 1

    # Write machine-readable summary
    with summary_path.open("w") as out:
        json.dump(field_counts, out, indent=2)

    # Print human-friendly summary
    for field, pairs in field_counts.items():
        print(f"Field: {field}")
        for pair, count in sorted(pairs.items(), key=lambda kv: kv[1], reverse=True):
            print(f"  {pair}: {count} examples")
        print()

    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()
