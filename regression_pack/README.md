# Procedure Suite Regression Pack (generated)

This pack was generated from the March 3, 2026 batch extraction reports and the accompanying quality review notes.

## Contents
- `fixtures/`: Note text fixtures (one file per note)
- `baseline_outputs/`: The pipeline JSON outputs captured in the batch report (for reference)
- `expectations/expectations.json`: Minimal assertion expectations (focused on the known failure modes)
- `evaluation_notes/`: The external QA summaries that motivated the expectations
- `run_regressions.py`: A lightweight runner you can adapt to your CLI

## How to use in your repo
1. Copy `fixtures/` into `tests/regression/fixtures/`
2. Copy `expectations/expectations.json` into `tests/regression/expectations/`
3. Copy `run_regressions.py` into `tests/regression/`
4. Run:
   ```bash
   python tests/regression/run_regressions.py \
     --runner "python -m <your_cli_module> --input {input}" \
     --fixtures tests/regression/fixtures \
     --expects tests/regression/expectations/expectations.json
   ```

Adjust the `--runner` command template so it emits your extraction JSON to stdout.

## Notes
Some expectations intentionally accept multiple valid answers (e.g. stent placement code could be 31631 vs 31636 depending on your coding rules).
