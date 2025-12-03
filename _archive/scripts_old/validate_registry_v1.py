import json
from pathlib import Path
from collections import defaultdict

# Ensure local imports work when run as a script
import sys
sys.path.append(str(Path.cwd()))

from modules.registry.engine import RegistryEngine  # noqa: E402


def normalize(val):
    return str(val).strip().lower() if val is not None else ""


def main():
    input_file = Path("data/synthetic_notes_with_registry.jsonl")
    error_log = Path("data/registry_errors.jsonl")

    engine = RegistryEngine()
    metrics = defaultdict(lambda: {"correct": 0, "total": 0})

    fields_to_validate = [
        "patient_mrn",
        "procedure_date",
        "asa_class",
        "sedation_type",
        "airway_type",
        "pleural_procedure_type",
        "pleural_guidance",
        "final_diagnosis_prelim",
        "disposition",
        "stent_type",
        "stent_location",
        "stent_deployment_method",
        "ebus_rose_result",
        "ebus_needle_gauge",
        "ebus_needle_type",
    ]

    if not input_file.exists():
        print(f"Missing synthetic registry file: {input_file}")
        return

    error_log.parent.mkdir(parents=True, exist_ok=True)
    error_log.write_text("")  # reset

    print("Starting Registry Validation Loop...")

    with input_file.open("r") as f, error_log.open("a") as elog:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            data = json.loads(line)
            note_text = data.get("note_text")
            ground_truth = data.get("registry_entry") or {}
            patient_trigger = data.get("patient_identifier_trigger")

            if not note_text or not ground_truth:
                continue

            try:
                result_record = engine.run(note_text, include_evidence=False)
                prediction = result_record.dict()
            except Exception as e:
                print(f"Error processing record {i}: {e}")
                continue

            for field in fields_to_validate:
                truth_val = normalize(ground_truth.get(field))
                pred_val = normalize(prediction.get(field))

                metrics[field]["total"] += 1
                if truth_val == pred_val or (
                    field == "patient_mrn" and truth_val and pred_val in truth_val
                ):
                    metrics[field]["correct"] += 1
                else:
                    error_entry = {
                        "example_index": i,
                        "patient_identifier_trigger": patient_trigger,
                        "field_name": field,
                        "gold_value": truth_val,
                        "predicted_value": pred_val,
                        "note_text": note_text[:2000],
                        "ground_truth_entry": ground_truth,
                    }
                    elog.write(json.dumps(error_entry) + "\n")

    print("\n=== Validation Results ===")
    for field, stats in metrics.items():
        acc = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"{field.ljust(24)}: {acc:.1f}% ({stats['correct']}/{stats['total']})")
    print(f"\nError log written to {error_log}")


if __name__ == "__main__":
    main()
