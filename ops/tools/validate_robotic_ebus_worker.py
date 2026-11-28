#!/usr/bin/env python3
"""Check the inference image against the frozen synthetic pilot, with networking disabled."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from uuid import uuid4

from eval_robotic_ebus import focused_facts, metrics

WORKER_CODE = """
import json,sys,importlib.metadata as metadata
from ip_registry_contracts.models import ExtractionRequest
from ip_registry_engine.engine import LocalDeterministicProvider
provider=LocalDeterministicProvider('/model')
if provider.ner is None:
    raise RuntimeError(provider.model_error)
responses=[provider.extract(ExtractionRequest.model_validate(row)).model_dump(mode='json') for row in json.load(sys.stdin)]
print(json.dumps({'responses':responses,'model_manifest_sha256':provider.ner.manifest_digest,
                  'runtime':{n:metadata.version(n) for n in ('torch','transformers','safetensors')}}))
"""


def validate(image, model, corpus, gold_path, output):
    gold = json.loads(gold_path.read_text())
    if (
        hashlib.sha256((corpus / "split_manifest.json").read_bytes()).hexdigest()
        != gold["corpus_manifest_sha256"]
    ):
        raise ValueError("Frozen corpus changed")
    documents = {
        row["document_id"]: row
        for line in (corpus / "test.jsonl").read_text().splitlines()
        if (row := json.loads(line))
    }
    requests = [
        {
            "job_id": str(uuid4()),
            "source_document_id": str(uuid4()),
            "text": documents[c["document_id"]]["text"],
            "source_digest": documents[c["document_id"]]["text_sha256"],
            "kind": "procedure",
        }
        for c in gold["cases"]
    ]
    command = [
        "docker",
        "run",
        "--rm",
        "-i",
        "--network=none",
        "--read-only",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=512m",
        "-e",
        "HF_HUB_DISABLE_PROGRESS_BARS=1",
        "-e",
        "TRANSFORMERS_VERBOSITY=error",
        "-v",
        str(model.resolve()) + ":/model:ro",
        "--entrypoint",
        "python",
        image,
        "-c",
        WORKER_CODE,
    ]
    result = subprocess.run(
        command, input=json.dumps(requests), text=True, capture_output=True, timeout=180, check=True
    )
    observed = json.loads(result.stdout)
    tp = fp = fn = 0
    cases = []
    for case, response in zip(gold["cases"], observed["responses"], strict=True):
        assert response["observations"]["inference"]["ner_available"] is True
        facts = focused_facts(response["observations"])
        failures = []
        for field in gold["critical_fields"]:
            expected, actual = set(case["expected"].get(field, [])), set(facts.get(field, []))
            tp += len(expected & actual)
            fp += len(actual - expected)
            fn += len(expected - actual)
            if actual != expected:
                failures.append(
                    {
                        "field": field,
                        "extra": sorted(actual - expected),
                        "missing": sorted(expected - actual),
                    }
                )
        cases.append(
            {"document_id": case["document_id"], "status": response["status"], "failures": failures}
        )
    digest = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    report = {
        "status": "inference_compatibility_passed",
        "image_id": digest,
        "network": "none",
        "read_only": True,
        "runtime": observed["runtime"],
        "model_manifest_sha256": observed["model_manifest_sha256"],
        "corpus_manifest_sha256": gold["corpus_manifest_sha256"],
        "gold_sha256": hashlib.sha256(gold_path.read_bytes()).hexdigest(),
        "pilot_metrics": metrics(tp, fp, fn),
        "cases": cases,
        "clinical_qualification": "pending",
        "promotion_allowed": False,
        "scope": "Same exposed eight-document engineering pilot; not independent qualification",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "cases"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    validate(args.image, args.model, args.corpus, args.gold, args.output)
