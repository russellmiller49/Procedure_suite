# Robotic EBUS blinded adjudication and qualification

The workflow uses the existing frozen `corpus_20260914_v2` synthetic corpus. It
creates review material and enforces evidence integrity; it does not manufacture
clinical review or establish clinical validation. The existing eight-document
pilot remains exposed engineering regression evidence.

## Review material

The prepared packet is at
`outputs/robotic_ebus_v1/adjudication_20261010_v1/reviewer/packet.html`.
Give **only the reviewer directory** to two clinical reviewers separately. Each
receives verbatim source notes under randomized case IDs, blank span and
relationship CSVs, a per-field completion checklist, and review instructions.
The HTML provides selectable text and Python-compatible Unicode code-point
span offsets. Reviewer files contain no model outputs, proposed labels,
generator metadata, source filenames, split assignments, or family keys.
Clinical details already written into a source note are preserved; this is
blinding to predictions and metadata, not removal of source clinical content.

Reviewers complete `reviews.csv`, `fields.csv`, `spans.csv`, and
`relationships.csv`. A third clinician adjudicates disagreements in a separate
copy, recording resolution notes while remaining blinded to model outputs.
The original submissions are retained and hashed. Review identities, expertise,
blinding, independence, and timestamps are attestations, not verified credentials;
the study coordinator is responsible for reviewer assignment and access control.
No reviewer identity or adjudication is supplied by this implementation.

Supported relationships link a source station to short-axis, sampling status,
observed-not-sampled status, or pass count; a lung target to localization; and the
procedure to immediate safety. Each endpoint must reference an exact source span
with the right label, normalization and assertion. Numeric short-axis annotations
must quote explicit short-axis wording. Unknown/conflicting fields stay unresolved;
blank annotation files do not count as reviewed negative evidence. Localization
qualification is currently lobe-level; multiple same-lobe targets must remain
unresolved, and full target-identity qualification remains separate.

## Split and exposure controls

`coordinator/scenarios.csv` inventories every corpus document. Proposed scenario
IDs initially follow families and every row is **pending**. A coordinator must
complete a semantic scenario review across the entire corpus, merging equivalent
scenarios into the same ID. Family assignments and source hashes are immutable.
Family or scenario overlap across train, validation, test or regression fails
validation; an overlap requires a new corpus/split/model version, not editing the
frozen assignments. Cosmetic/exact source fingerprints also enforce disjointness.
This automatic check does not replace semantic review.

Training, validation, prior-use regression, and every family containing an exposed
pilot document are ineligible for independent qualification. Their exposure cannot
be cleared. Record any additional tuning or engineering exposure as `true` before
qualification. All three clinical reviewers must attest independence from model
development and prior answers. A qualification run excludes exposed scenarios,
validates all original submissions again, checks complete positive coverage, and
reserves the test split with an exclusive corpus-local
`independent_qualification_use.json` ledger **before inference**. Preserve this
ledger, including failed runs, in all copies/versions of the corpus history.
A consumed set can subsequently support regression, never a second independent
qualification. Local files and attestations are audit controls, not a substitute
for organizational custody or an authenticated review service.

## Gates

Independent synthetic qualification requires positive support for all six critical
fields, including both present and absent safety examples, resolved fields, a
complete disjoint scenario audit, an available hash-verified candidate model,
per-field and relationship precision ≥98% and recall ≥95%, and no degradation
against the observed baseline on any critical field. Runtime failures block the
gate. Support is reported as facts, documents and families; zero support never
passes by vacuous precision/recall. These are engineering thresholds, not a clinical
sample-size or power justification.

`promotion_allowed` remains false for this synthetic-only workflow, even if its
independent synthetic gate passes. Clinical data validation, native/scanned/mixed
PDF equivalence, independent source/model review, and operational/release
qualification remain separate prerequisites. Running `--require-acceptance`
returns nonzero until clinical release evidence exists outside this workflow.

The packet was displayed to the implementation agent during HTML QA. The canonical
`data/knowledge/robotic_ebus_v1/qualification_exposure.json` therefore conservatively
marks all 77 test documents as engineering-exposed. They remain useful for blinded
clinical adjudication and engineering regression, but there are now **zero untouched
qualification documents** in this version. Independent qualification requires a
new, genuinely unexposed source set and model/split provenance; re-randomizing case
IDs or clearing the CSV exposure flag cannot restore independence.

The readiness report currently documents missing clinical reviews and semantic
scenario review, and zero positive short-axis and positive safety-event support
in the exposed pilot. It does not score unreviewed documents or imply the rest of
the corpus lacks these features.

## Commands

Run from the repository root. Use a new packet/import/output version rather than
overwriting completed reviews or a qualification result.

```sh
python ops/tools/robotic_ebus_adjudication.py packet \
  --corpus data/ml_training/robotic_ebus_v1/corpus_20260914_v2 \
  --output /new/adjudication-version

python ops/tools/robotic_ebus_adjudication.py import \
  --corpus data/ml_training/robotic_ebus_v1/corpus_20260914_v2 \
  --packet /new/adjudication-version \
  --review-a /reviews/clinician-a --review-b /reviews/clinician-b \
  --adjudication /reviews/adjudicator --output /new/adjudicated.json

python ops/tools/qualify_robotic_ebus.py \
  --corpus data/ml_training/robotic_ebus_v1/corpus_20260914_v2 \
  --packet /new/adjudication-version --gold /new/adjudicated.json \
  --review-a /reviews/clinician-a --review-b /reviews/clinician-b \
  --adjudication /reviews/adjudicator \
  --model-dir artifacts/robotic_ebus_v1/local_candidate_0_2_0 \
  --output /new/independent-qualification.json --require-acceptance

# Safe to regenerate: no held-out inference and no qualification-set consumption.
python ops/tools/robotic_ebus_adjudication.py readiness \
  --corpus data/ml_training/robotic_ebus_v1/corpus_20260914_v2 \
  --packet outputs/robotic_ebus_v1/adjudication_20261010_v1 \
  --output outputs/robotic_ebus_v1/qualification_readiness.json --require-acceptance

python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/robotic-ebus-pr
```

The readiness command's nonzero acceptance exit is expected. The PR tier includes
focused workflow regression tests; passing it never overrides the release gate.
