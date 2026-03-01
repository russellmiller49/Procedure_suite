#!/usr/bin/env python3
"""Launch and monitor an OpenAI fine-tuning job for the reporter model.

Usage:
    python launch_finetune.py                          # upload files + start job
    python launch_finetune.py --status                 # check all running jobs
    python launch_finetune.py --status --job-id ftjob-abc123  # check specific job
    python launch_finetune.py --list-models             # list your fine-tuned models
    python launch_finetune.py --cancel --job-id ftjob-abc123   # cancel a job
    python launch_finetune.py --model gpt-4o-2024-08-06        # use gpt-4o instead

Requires: OPENAI_API_KEY environment variable.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed.")
    print("  pip install openai")
    sys.exit(1)

DEFAULT_TRAIN = Path("fine_tuning/reporter_ft_train.jsonl")
DEFAULT_VALID = Path("fine_tuning/reporter_ft_valid.jsonl")
DEFAULT_MODEL = "gpt-4o-mini-2024-07-18"
DEFAULT_SUFFIX = "reporter-v1"
DEFAULT_EPOCHS = 3
JOBS_LOG = Path("fine_tuning/finetune_jobs.jsonl")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    # Mode flags
    p.add_argument("--status", action="store_true", help="Check job status instead of launching.")
    p.add_argument("--list-models", action="store_true", help="List fine-tuned models.")
    p.add_argument("--cancel", action="store_true", help="Cancel a job (requires --job-id).")

    # Job config
    p.add_argument("--train", type=Path, default=DEFAULT_TRAIN)
    p.add_argument("--valid", type=Path, default=DEFAULT_VALID)
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"Base model to fine-tune (default: {DEFAULT_MODEL}).")
    p.add_argument("--suffix", default=DEFAULT_SUFFIX,
                   help=f"Model name suffix (default: {DEFAULT_SUFFIX}).")
    p.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS,
                   help=f"Number of training epochs (default: {DEFAULT_EPOCHS}).")
    p.add_argument("--job-id", default=None, help="Job ID for --status or --cancel.")
    p.add_argument("--wait", action="store_true",
                   help="Wait for the job to complete (polls every 60s).")
    return p.parse_args(argv)


def upload_file(client: OpenAI, path: Path, purpose: str = "fine-tune") -> str:
    """Upload a file to OpenAI and return the file ID."""
    print(f"  Uploading {path.name} ({path.stat().st_size / 1024:.0f} KB)...")
    with path.open("rb") as f:
        response = client.files.create(file=f, purpose=purpose)
    print(f"  Uploaded: {response.id}")
    return response.id


def wait_for_file(client: OpenAI, file_id: str, timeout: int = 300) -> bool:
    """Wait for a file to finish processing."""
    start = time.time()
    while time.time() - start < timeout:
        status = client.files.retrieve(file_id).status
        if status == "processed":
            return True
        if status == "error":
            print(f"  ERROR: File {file_id} processing failed.")
            return False
        time.sleep(5)
    print(f"  TIMEOUT: File {file_id} still processing after {timeout}s.")
    return False


def launch_job(args: argparse.Namespace) -> int:
    """Upload files and start fine-tuning."""
    client = OpenAI()

    if not args.train.exists():
        print(f"ERROR: Training file not found: {args.train}")
        print("Run prepare_finetune.py first.")
        return 1

    print(f"Base model: {args.model}")
    print(f"Suffix: {args.suffix}")
    print(f"Epochs: {args.epochs}")
    print()

    # Upload files
    print("Uploading files to OpenAI...")
    train_file_id = upload_file(client, args.train)

    valid_file_id = None
    if args.valid.exists():
        valid_file_id = upload_file(client, args.valid)

    # Wait for processing
    print("\nWaiting for files to process...")
    if not wait_for_file(client, train_file_id):
        return 1
    if valid_file_id and not wait_for_file(client, valid_file_id):
        return 1
    print("  Files ready.")

    # Create fine-tuning job
    print("\nStarting fine-tuning job...")
    create_kwargs: dict = {
        "training_file": train_file_id,
        "model": args.model,
        "suffix": args.suffix,
        "hyperparameters": {"n_epochs": args.epochs},
    }
    if valid_file_id:
        create_kwargs["validation_file"] = valid_file_id

    job = client.fine_tuning.jobs.create(**create_kwargs)

    print(f"\n{'=' * 60}")
    print(f"  Job ID:        {job.id}")
    print(f"  Status:        {job.status}")
    print(f"  Model:         {job.model}")
    print(f"  Created:       {job.created_at}")
    print(f"{'=' * 60}")

    # Log the job
    JOBS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with JOBS_LOG.open("a") as f:
        f.write(json.dumps({
            "job_id": job.id,
            "model": args.model,
            "suffix": args.suffix,
            "epochs": args.epochs,
            "train_file": train_file_id,
            "valid_file": valid_file_id,
            "status": job.status,
        }) + "\n")
    print(f"\nLogged to {JOBS_LOG}")

    # Optionally wait
    if args.wait:
        print("\nWaiting for job to complete (polling every 60s)...")
        return poll_job(client, job.id)

    print(f"\nTo check status:")
    print(f"  python launch_finetune.py --status --job-id {job.id}")
    print(f"\nTo wait for completion:")
    print(f"  python launch_finetune.py --status --job-id {job.id} --wait")

    return 0


def poll_job(client: OpenAI, job_id: str) -> int:
    """Poll a job until it completes."""
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        status = job.status
        print(f"  [{time.strftime('%H:%M:%S')}] Status: {status}", end="")

        if hasattr(job, "trained_tokens") and job.trained_tokens:
            print(f" | Trained tokens: {job.trained_tokens:,}", end="")
        print()

        if status == "succeeded":
            print(f"\n  DONE! Fine-tuned model: {job.fine_tuned_model}")
            print(f"\n  To evaluate:")
            print(f"    python eval_finetune.py --model {job.fine_tuned_model}")
            return 0
        elif status in ("failed", "cancelled"):
            print(f"\n  Job {status}.")
            if hasattr(job, "error") and job.error:
                print(f"  Error: {job.error}")
            return 1

        time.sleep(60)


def check_status(args: argparse.Namespace) -> int:
    """Check fine-tuning job status."""
    client = OpenAI()

    if args.job_id:
        job = client.fine_tuning.jobs.retrieve(args.job_id)
        print(f"Job: {job.id}")
        print(f"  Status:          {job.status}")
        print(f"  Model:           {job.model}")
        print(f"  Fine-tuned:      {job.fine_tuned_model or '(not yet)'}")
        print(f"  Created:         {job.created_at}")
        if hasattr(job, "trained_tokens") and job.trained_tokens:
            print(f"  Trained tokens:  {job.trained_tokens:,}")
        if hasattr(job, "error") and job.error:
            print(f"  Error:           {job.error}")

        # Show recent events
        try:
            events = client.fine_tuning.jobs.list_events(
                fine_tuning_job_id=args.job_id, limit=10
            )
            if events.data:
                print(f"\n  Recent events:")
                for evt in reversed(events.data):
                    print(f"    [{evt.created_at}] {evt.message}")
        except Exception:
            pass

        if args.wait and job.status in ("validating_files", "queued", "running"):
            return poll_job(client, args.job_id)
    else:
        # List all recent jobs
        jobs = client.fine_tuning.jobs.list(limit=10)
        if not jobs.data:
            print("No fine-tuning jobs found.")
            return 0
        print(f"{'Job ID':<30} {'Status':<15} {'Model':<30} {'Fine-tuned Model'}")
        print("-" * 100)
        for job in jobs.data:
            print(f"{job.id:<30} {job.status:<15} {job.model:<30} {job.fine_tuned_model or ''}")

    return 0


def list_models(args: argparse.Namespace) -> int:
    """List fine-tuned models."""
    client = OpenAI()
    jobs = client.fine_tuning.jobs.list(limit=50)
    ft_models = [j for j in jobs.data if j.status == "succeeded" and j.fine_tuned_model]
    if not ft_models:
        print("No completed fine-tuned models found.")
        return 0
    print("Fine-tuned models:")
    for j in ft_models:
        print(f"  {j.fine_tuned_model}")
        print(f"    Base: {j.model} | Created: {j.created_at}")
    return 0


def cancel_job(args: argparse.Namespace) -> int:
    """Cancel a fine-tuning job."""
    if not args.job_id:
        print("ERROR: --job-id required for --cancel")
        return 1
    client = OpenAI()
    client.fine_tuning.jobs.cancel(args.job_id)
    print(f"Cancelled job: {args.job_id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not (os.environ.get("OPENAI_API_KEY") or "").strip():
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print("  export OPENAI_API_KEY=sk-...")
        return 1

    if args.list_models:
        return list_models(args)
    if args.cancel:
        return cancel_job(args)
    if args.status:
        return check_status(args)
    return launch_job(args)


if __name__ == "__main__":
    raise SystemExit(main())
