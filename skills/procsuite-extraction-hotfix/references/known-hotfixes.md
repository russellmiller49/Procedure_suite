# Known hotfix targets for Procedure Suite extraction hotfixes

This reference captures the highest-priority extraction bugs already identified in the current review cycle.

## Billing-grade bugs to prioritize

1. EBUS dimension text like `9 mm` must not be parsed as station 9.
   - Main file: `app/registry/postprocess/__init__.py`
   - Acceptance shape:
     - sampled stations stay `{"7", "11L"}`
     - `31652` remains
     - `31653` is not emitted

2. Non-Chartis bronchial blockers must not emit `31634`.
   - Main file: `app/coder/domain_rules/registry_to_cpt/coding_rules.py`
   - Examples: Uniblocker, Arndt blocker, Fogarty, hemoptysis isolation
   - Acceptance shape:
     - `31634` suppressed
     - underlying therapeutic bronchoscopy codes remain when supported

3. Decimal medication doses must survive extraction.
   - Main file: `app/registry/deterministic_extractors.py`
   - Acceptance shape:
     - `0.4mg` stays `0.4mg`
     - no `4mg` inflation
     - parsed dose text should verify against source text

4. Prophylactic bleeding language must not create a true bleeding complication.
   - Main file: `app/registry/postprocess/complications_reconcile.py`
   - Acceptance shape:
     - no Nashville grade inflation when the note says `COMPLICATIONS: None`
     - low EBL and prophylactic wording should cap or suppress bleeding

## Working style

- Add the failing test first.
- Keep changes minimal and evidence-aware.
- Prefer fixture coverage when the bug pattern is likely to recur.
