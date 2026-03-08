# Quality Gates

This repo now uses a two-tier quality gate model:

- `PR` gate: small, deterministic, and fast enough for routine pull requests.
- `Nightly / release` gate: broader evaluation with stored JSON artifacts and metric deltas.

The gate runner is:

```bash
python ops/tools/run_quality_gates.py --tier pr --output-dir reports/ci/pr
python ops/tools/run_quality_gates.py --tier nightly --output-dir reports/ci/nightly
```

Each run writes:

- `summary.json` and `summary.md`
- raw evaluation JSON reports
- `*.delta.json` files when a checked-in baseline exists

## Quality Signals

`quality_signals` are the stable machine-readable form of post-extraction quality outcomes.

Canonical storage:

- `registry.coding_support.quality_signals`

Legacy compatibility:

- existing warning strings are still emitted
- warning strings are derived from `quality_signals` by the legacy adapter

Current signal shape:

- `version`: currently `quality_signal.v1`
- `phase`: ordered quality-pass phase that emitted the signal
- `signal_type`: stable category such as `legacy_warning` or `source_type`
- `code`: stable machine code
- `severity`: `info`, `warning`, or `review`
- `message`: human-readable description
- `legacy_warning`: populated when the signal mirrors an existing warning string
- `emitted_by`: source function or module
- `metadata`: structured details for diffing and debugging

Interpretation rule:

- use `quality_signals` for machine logic, dashboards, and QA diffs
- use legacy warnings only for backward-compatible user-facing behavior

## Reporter Seed Promotion Rule

`REPORTER_SEED_STRATEGY=registry_extract_fields` remains the production default.

`llm_findings` is challenger-only and is not promoted automatically. Promotion requires all of the following:

1. PR fixed-subset compare stays clean:
   - same critical procedure presence/absence
   - zero forbidden artifact hits
   - no worse strict-render fallback cases
2. Nightly or release comparison remains non-regressing against the checked-in baselines.
3. A human explicitly changes `REPORTER_SEED_STRATEGY`; CI does not flip this automatically.

Offline CI note:

- the PR challenger gate uses the frozen fixture at `tests/fixtures/reporter_seed_eval_llm_fixture.json`
- nightly or release runs use the larger reporter dataset in `tests/fixtures/reporter_golden_dataset.json`
- if live LLM access is unavailable, nightly falls back to the frozen full challenger fixture at `tests/fixtures/reporter_seed_eval_llm_fixture_full.json`

That fallback keeps artifacts comparable, but it is not sufficient by itself to justify production promotion.

## What Runs Where

### PR Gate

The fast PR gate runs:

- focused regression pytest suites
- extraction fixture matrix tests
- reporter dual-path matrix tests
- `ml/scripts/eval_golden.py` on `tests/fixtures/unified_quality_corpus.json`
- reporter seed baseline eval on `tests/fixtures/reporter_seed_eval_samples.json`
- reporter seed `llm_findings` eval on the same fixed sample with a frozen fixture
- side-by-side reporter compare report

### Nightly / Release Gate

The broader nightly gate runs:

- the same focused pytest suites
- full extraction eval via `ml/scripts/eval_golden.py` on the unified quality corpus
- full reporter baseline eval on `tests/fixtures/reporter_golden_dataset.json`
- full reporter `llm_findings` eval on the same dataset
- side-by-side reporter compare report

## Baselines

Current checked-in baselines used for deltas:

- `reports/unified_quality_corpus_extraction_baseline.json`
- `reports/reporter_seed_registry_extract_fields_baseline.json`
- `reports/reporter_seed_llm_findings_baseline.json`
- `reports/reporter_seed_dual_path_compare.json`
- `reports/reporter_seed_registry_extract_fields_full_baseline.json`
- `reports/reporter_seed_llm_findings_full_baseline.json`
- `reports/reporter_seed_dual_path_full_compare_baseline.json`

When updating baselines intentionally, regenerate the reports, review the delta JSON, and call out the metric changes in the PR description.
