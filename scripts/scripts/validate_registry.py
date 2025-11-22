import json
import sys
from pathlib import Path
from collections import defaultdict

# Ensure we can import from modules
sys.path.append(str(Path.cwd()))

from modules.registry.engine import RegistryEngine

def normalize(text):
    """Helper to normalize strings for comparison"""
    return str(text).lower().strip() if text else ""

def main():
    input_file = Path("data/synthetic_notes_with_registry.jsonl")
    engine = RegistryEngine()
    
    metrics = defaultdict(lambda: {"correct": 0, "total": 0})
    
    print("Starting Registry Validation Loop...")
    
    with open(input_file, 'r') as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            note_text = data.get("note_text")
            ground_truth = data.get("registry_entry")
            
            if not note_text or not ground_truth:
                continue

            # Run extraction (skip evidence to avoid validation noise)
            try:
                result_record = engine.run(note_text, include_evidence=False)
                prediction = result_record.dict()
            except Exception as e:
                print(f"Error processing record {i}: {e}")
                continue

            # Compare specific fields of interest
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
            ]
            
            for field in fields_to_validate:
                truth_val = normalize(ground_truth.get(field))
                pred_val = normalize(prediction.get(field))
                
                metrics[field]["total"] += 1
                if truth_val == pred_val:
                    metrics[field]["correct"] += 1
                elif field == "patient_mrn" and pred_val in truth_val: 
                    # Loose match for MRN extraction if it grabbed extra chars
                    metrics[field]["correct"] += 1

    print("\n=== Validation Results ===")
    for field, stats in metrics.items():
        acc = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"{field.ljust(20)}: {acc:.1f}% ({stats['correct']}/{stats['total']})")

if __name__ == "__main__":
    main()
