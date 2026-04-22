# Gate playbook for Procedure Suite

## Current fast gate shape

The current PR gate is centered on:
- a fixed focused pytest target list
- extraction eval on `tests/fixtures/unified_quality_corpus.json`
- diff output against the saved extraction baseline

That means a new test or fixture only protects the repo if the gate actually runs it.

## Preferred order

1. Add a focused pytest.
2. Extend the shared fixture when the evaluator can express the rule.
3. Update the gate target list if needed.
4. Re-run the gate and inspect `summary.md` and the captured stdout/stderr artifacts.

## High-value regression patterns to keep covered

- dimension text parsed as an EBUS station
- non-Chartis blockers coded as `31634`
- decimal medication dose loss
- prophylactic bleeding language causing a complication
- header/menu evidence leakage
- reporter loss of explicit complications or blank procedure bodies
