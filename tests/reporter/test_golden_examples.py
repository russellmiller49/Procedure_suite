#!/usr/bin/env python3
"""
Test harness for evaluating the reporter against the Golden Examples dataset.

Usage:
    pytest tests/reporter/test_golden_examples.py
    # OR directly for detailed output:
    python tests/reporter/test_golden_examples.py
"""

import json
import difflib
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure modules are importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from modules.registry.application.registry_service import RegistryService
from modules.reporting.engine import (
    apply_patch_result,
    build_procedure_bundle_from_extraction,
    ReporterEngine,
    default_template_registry,
    default_schema_registry,
    _load_procedure_order,
)
from modules.reporting.inference import InferenceEngine
from modules.reporting.validation import ValidationEngine

# Configuration
GOLDEN_DATASET_PATH = PROJECT_ROOT / "tests/fixtures/reporter_golden_dataset.json"

def run_pipeline(input_text: str) -> str:
    """
    Simulates the full extraction-to-report pipeline.
    1. Extract registry data from text (Extraction-First)
    2. Build ProcedureBundle
    3. Run Inference/Validation
    4. Render Report
    """
    # 1. Extraction
    registry_service = RegistryService()
    # Use 'parallel_ner' if available, otherwise default engine
    # In a test harness, we might want to mock the extraction to isolate reporter logic,
    # but here we want to test the full "Input -> Output" gap.
    extraction_result = registry_service.extract_fields_extraction_first(input_text)
    
    # 2. Build Bundle
    # Convert the RegistryExtractionResult (which contains a RegistryRecord) into the dict format expected by the bundle builder
    # Note: build_procedure_bundle_from_extraction usually expects a raw dict from the registry engine
    # We'll dump the pydantic model to a dict.
    extraction_payload = extraction_result.record.model_dump(exclude_none=True)
    bundle = build_procedure_bundle_from_extraction(extraction_payload, source_text=input_text)

    # 3. Inference & Validation
    inference = InferenceEngine()
    inference_result = inference.infer_bundle(bundle)
    bundle = apply_patch_result(bundle, inference_result)
    
    templates = default_template_registry()
    schemas = default_schema_registry()
    
    validator = ValidationEngine(templates, schemas)
    issues = validator.list_missing_critical_fields(bundle)
    
    # 4. Render
    reporter = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    
    # Render in non-strict mode to see what we get even if incomplete
    report_result = reporter.compose_report_with_metadata(
        bundle,
        strict=False, 
        validation_issues=issues,
        embed_metadata=False
    )
    
    return report_result.text

def normalize_text(text: str) -> str:
    """Normalize whitespace and newlines for fairer comparison."""
    if not text: return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity ratio."""
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def main():
    if not GOLDEN_DATASET_PATH.exists():
        print(f"Error: Dataset not found at {GOLDEN_DATASET_PATH}")
        print("Run `python scripts/parse_golden_reporter_examples.py` first.")
        return

    print(f"Loading dataset from {GOLDEN_DATASET_PATH}...")
    with open(GOLDEN_DATASET_PATH, 'r', encoding='utf-8') as f:
        examples = json.load(f)

    print(f"Loaded {len(examples)} examples. Running pipeline...\n")
    
    results = []
    
    for ex in examples:
        ex_id = ex['id']
        input_text = ex['input_text']
        ideal_output = ex['ideal_output']
        
        print(f"Processing {ex_id}...", end="", flush=True)
        
        try:
            generated_output = run_pipeline(input_text)
            
            norm_ideal = normalize_text(ideal_output)
            norm_gen = normalize_text(generated_output)
            
            similarity = calculate_similarity(norm_ideal, norm_gen)
            
            results.append({
                "id": ex_id,
                "similarity": similarity,
                "ideal": norm_ideal,
                "generated": norm_gen,
                "input": input_text
            })
            print(f" Done. Similarity: {similarity:.2f}")
            
        except Exception as e:
            print(f" Failed: {e}")
            results.append({
                "id": ex_id,
                "error": str(e),
                "similarity": 0.0
            })

    # Summary Analysis
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    scores = [r['similarity'] for r in results if 'similarity' in r]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    print(f"Average Similarity Score: {avg_score:.2f}")
    
    # Identify worst performers to prioritize logic fixes
    sorted_results = sorted(results, key=lambda x: x.get('similarity', 0))
    
    print("\nLOWEST SCORING EXAMPLES (Needs Improvement):")
    for r in sorted_results[:3]:
        print(f"\n--- Example {r['id']} (Score: {r.get('similarity', 0):.2f}) ---")
        print(f"INPUT SNAPSHOT: {r.get('input', '')[:100]}...")
        if 'error' in r:
            print(f"ERROR: {r['error']}")
        else:
            # Show a brief diff hint
            print("DIFF HINT (Missing lines in Generated):")
            # Simple check for missing key phrases from ideal
            ideal_lines = r['ideal'].split('\n')
            gen_text = r['generated']
            missing_count = 0
            for line in ideal_lines:
                if line not in gen_text and len(line) > 10:
                    print(f"  - {line[:60]}...")
                    missing_count += 1
                    if missing_count >= 5:
                        print("  ... (more missing)")
                        break

if __name__ == "__main__":
    main()
