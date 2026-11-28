# Robotic bronchoscopy and linear EBUS launch candidate

Implementation date: 2026-09-14. Contract **0.2.0**, profile **robotic_ebus_v1**.

The focused source packages and application changes are implemented as a **review candidate** in Procedure_suite, ip-registry-clinical and ip-registry-national. The initial local NER candidate has been trained and measured. **Model acceptance, independent package review and production activation have not passed.** The first pilot achieved 52.0% recall. Parser corrections now recover all 98 reviewed facts in those eight exposed documents; this is a regression result, not independent qualification. Synthetic results are engineering evidence, not clinical validation.

## Field contract and scope

The authoritative input was `Robotic_EBUS_Registry_Data_Dictionary_2026_Updated.xlsx`, sheet `Data_Dictionary`, containing 1,164 fields across 48 proposed tables. The source workbook is unchanged.

- [Machine-readable dictionary](../data/knowledge/robotic_ebus_v1/launch_dictionary.json): 176 launch fields plus five existing application context bindings. It includes source row/field references, original definitions, launch adaptations, types, units, applicability, source, missingness and clinical/national destinations.
- [Review workbook](../outputs/robotic_ebus_v1/Robotic_EBUS_Launch_Dictionary_0_2_0.xlsx): 181 launch/binding rows and 999 remaining source fields retained as the roadmap. There are 165 distinct selected source fields; several fields have explicit adapted or shared mappings. Unselected source rows include alternative/duplicated linkage representations as well as deferred clinical content.
- [Contract models](../packages/ip_registry_contracts/src/ip_registry_contracts/launch.py): entities are stored within the existing encrypted immutable revisions. Indexed profile/version metadata and normalized table exports avoid creating all 48 physical tables.

New production-contract writes accept diagnostic robotic bronchoscopy, linear EBUS, or both. Started attempts, navigation failures and aborted cases remain eligible. Unknown eligibility can be drafted but cannot be approved. Generic peripheral navigation is never renamed robotic. Standalone nonrobotic navigation, radial EBUS, EUS-B, robotic ablation, BLVR, pleural and other procedures remain outside the launch profile. Their development code, training workflows and prior checkpoints remain available.

Contract validation separates station surveys from sampled targets and individual-node identity; requires explicitly documented short-axis measurements; preserves ordered imaging and actual tool confirmation; invalidates confirmation after intervening position/tool changes; preserves aggregate counts; validates all entity links; and retains preliminary/final/amended pathology history. Unattributed specimens cannot establish target-level index outcomes. Null fields receive a missingness reason. Incomplete follow-up cannot establish a negative interval outcome, while a documented positive event remains visible.

Clinical values, narrative, exact dates, original values and source evidence stay local. National projection explicitly allowlists coded fields and remaps every linked export ID, retaining the existing age bands, year-only dates, signed profiles and current-policy disclosure controls. Narrative and source-provenance fields are not national fields. New national batches must explicitly declare their contract/profile; old staged batches require revalidation.

## Application changes

`ip-registry-clinical` now has focused case/anesthesia, procedure, target, EBUS survey, navigation, localization, acquisition/specimen, pathology and safety review sections. Procedure/imaging/pathology/clinical-update jobs use the isolated worker. Findings are proposals; adoption, draft saving, approval and amendments remain separate actions. Pathology and imaging proposals require explicit local attribution. Clinical-update findings are reviewed against the safety interval fields. Approved revisions remain immutable.

The clinical analysis endpoint exports approved launch records as normalized tables and versioned descriptive counts. It applies the existing patient grants. The national report definition `robotic_ebus_launch` uses the same measure functions after national projection and current-policy filtering. Related national count vectors are suppressed together when small cells, denominators, quorum or institutional dominance make disclosure unsafe.

Migrations `b240914c01` and `b240914n01` label prior rows as legacy, preserve encrypted payloads, and invalidate old queued work/staged payloads/reports. Historical readers remain available. Rollback uses the independently retained prior installation; migrations do not rewrite old revisions to make them appear eligible.

The local source candidate is `outputs/robotic_ebus_v1/ip_registry_0_2_0_candidate.tar.gz`. Its SHA-256 is `5c2aa43b1e590fde235ebb058a248b5baf5794b1326961bc7e45c5d86ca576d8`. Both applications imported this archive using their own `tools/import_candidate.py`; the national application imported contracts without the engine. Their vendor manifests retain pending independent review. The [assembled candidate manifest](../outputs/robotic_ebus_v1/source_model_candidate_manifest.json) binds this source archive, unchanged trained model, frozen dictionaries/split, worker image and evaluation artifacts. No Procedure_suite application, database or training dataset was copied into either application.

## Corpus, labels and model

The inventory covers the entire supplied collection, including eight physical JSONL files containing 400 reports in 200 clean/messy pairs, additional standard/edge-case text notes, 146 physical PDFs (140 individual and six combined), manifests and 14 ZIP archives. The inventory contains 469 file/member entries and records no archive-read errors. Duplicate archive copies are inventoried without becoming independent cases.

The frozen split is [corpus_20260914_v2](../data/ml_training/robotic_ebus_v1/corpus_20260914_v2/split_manifest.json), SHA-256 `100a47971eab7cf315db0a2543489baf8028dbe016179cc18a89457c09e7728e`. The earlier `corpus_20260914` is superseded and must not be used. Family grouping uses supplied parent IDs, clean/messy counterparts, normalized text and PDF case/rendition identity. The overlap audit scanned 34 existing JSONL corpora. Previously used or potentially reused older cases are regression material.

| Split | Case families | Documents |
|---|---:|---:|
| Training | 168 | 374 |
| Validation | 36 | 79 |
| Test | 36 | 77 |
| Prior-use regression | 126 | 126 |
| Total | 366 | 656 |

The eligible 240-family partition is exactly 70/15/15 by family. A complete semantic review of reused clinical scenarios is still required before claiming test independence; exact-match checks and metadata grouping cannot prove that different wording describes a new scenario.

The first span set is **source-verified lexical weak supervision**, with every unique station/action/ROSE label surface reviewed by Codex. It uses the existing BIO ontology and masks synthetic downstream outcome labels. It is not a clinically adjudicated span/relationship gold set. The annotation manifest explicitly records `clinical_reviewed=false` and `independent_gold=false`. Hidden generator outcomes are not extraction labels.

BiomedBERT training ran locally for two epochs using 902 training chunks and 186 validation chunks. The training script now accepts a separate validation file and rejects overlapping families. Development checkpoints were retained at `artifacts/robotic_ebus_v1/biomedbert_candidate_20260914`. The inference-only candidate is `artifacts/robotic_ebus_v1/local_candidate_0_2_0`; its manifest binds the source, corpus, annotation and asset hashes. It contains safetensors/tokenizer/configuration assets, not optimizer or pickle checkpoints.

The worker uses local files only, validates the complete asset inventory and hashes, restricts architecture/labels, and disables remote code. Missing/incompatible models and failed inference produce explicit degraded results. They do not trigger a different inference engine or a cloud provider. The inference container has a separate hashed dependency lock; the original training environment is retained for reproducibility. Updated inference dependencies require their own compatibility and advisory evidence.

The inference image was built with PyTorch 2.14.0+cpu, Transformers 5.17.0 and safetensors 0.8.0. Its network-disabled, read-only run reproduced the revised parser's 98/0/0 TP/FP/FN counts on the exposed pilot; see [worker evaluation](../outputs/robotic_ebus_v1/worker_evaluation.json). Both the worker dependency advisory audit and the CPU wheel's upstream-version lookup passed with no known vulnerabilities reported. This does not qualify the model or replace image/binary release review. The [upstream Transformers v5 migration guide](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md) describes the safetensors and loading changes considered during this update.

## Measured evidence and limitations

The pilot gold selection contains eight source-reviewed clean/messy documents from four families covering Ion, Monarch, Galaxy and linear EBUS, with 98 documented critical facts across ten field groups. It reports TP/FP/FN and support by field, platform, format and their intersections.

| Observed local runtime | Precision | Recall | TP / FP / FN |
|---|---:|---:|---:|
| Focused initial candidate | 98.1% | 52.0% | 51 / 1 / 47 |
| Current development engine | 67.7% | 42.9% | 42 / 20 / 56 |
| Revised parser, exposed regression cases | 100% | 100% | 98 / 0 / 0 |

The original source/evaluation/model-run evidence is retained under [engineering_iterations/initial](../outputs/robotic_ebus_v1/engineering_iterations/initial/field_evaluation.json). Subsequent parser work corrected decimal splitting, cm-to-mm normalization, soft PDF wraps, whole-word lobe identity, survey-to-sampling enrichment, station counts, source-section precedence and active complication evidence. Training examples informed the corrections; the already exposed pilot was also used for regression debugging. The trained NER weights and family split were unchanged. The revised score must not be described as held-out accuracy or used to select a release model. Short-axis positive support remains zero in this pilot, and the full launch relationship/field coverage is absent.

The development baseline was measured through the actual extraction-first service, but its expected granular NER model was missing and its registry ML runtime was incompatible in this checkout. This comparison is against the **observed degraded local baseline**, not a qualified production baseline. The pilot does not establish full field/relationship accuracy, platform coverage or independent clinical performance. The exposed pilot cases must not subsequently be described as an untouched qualification test set.

[Field evaluation](../outputs/robotic_ebus_v1/field_evaluation.json) records the failed release acceptance gate despite its passing aggregate regression score. `--require-acceptance` exits nonzero. Token-level loss and exposed regression scores do not authorize model promotion. Full adjudication, independently measured critical-field precision ≥98% and recall ≥95%, baseline preservation/improvement, format/relationship coverage and all integrity checks are required before a later candidate can be considered for promotion.

The launch measure follows the [ATS/ACCP research statement](https://pubmed.ncbi.nlm.nih.gov/38394646/): a prespecified peripheral target enters the diagnostic-attempt denominator when navigation, localization or sampling begins; navigation failures remain included. Strict index diagnostic results require an attributed index specimen and are separate from later follow-up diagnoses and diagnoses in another target. Measures are unadjusted descriptive engineering definitions. No staging sensitivity or long-term diagnostic-accuracy claim is implemented.

Targeted verification includes shared-contract integrity tests, both application suites on disposable PostgreSQL, migration replay with unchanged ciphertext/approval history, source evidence and stale-result checks, explicit national scope/allowlists, disclosure tests, and a complete clinical approval → stage → release → national intake → receipt → report round trip. See [round-trip evidence](../outputs/robotic_ebus_v1/roundtrip_validation.json) and [validation summary](../outputs/robotic_ebus_v1/validation_summary.json).

The final checks include 41 shared-contract regressions, 50 clinical and 44 national PostgreSQL tests, 73 development PDF tests, four clinical PDF tests, and both UI builds. All 374 training documents also produced contract-valid bounded proposals or explicit unsupported results with the NER deliberately unavailable; see [proposal integrity](../outputs/robotic_ebus_v1/training_proposal_integrity.json). This tests degraded behavior, not field accuracy. Documented positive complications remain visible with missing summaries; contradictory safety/specimen summaries cannot be approved or accepted nationally.

The clinical browser was exercised with a saved/approved aborted robotic attempt and one supplied two-page synthetic Ion PDF rendered as digital, scanned and mixed. Increasing OCR rendering to 216 dpi preserved the reviewed station labels, decimal measurements and pass counts and improved the displayed page confidences from 76%/73% to 94%/92%. Native headers were retained over scanned bodies. Spelling errors remained, including Ion/lon. This is a regression demonstration, not complete format parity or clinical OCR validation; source review remains mandatory. No PDF bytes were submitted to the server during this check.

## Reproduction and transition

Commands run from Procedure_suite unless noted. Corpus preparation and rendition tools refuse to overwrite existing outputs; use a new versioned directory for changes.

```sh
python ops/tools/build_robotic_ebus_dictionary.py --source /path/to/Robotic_EBUS_Registry_Data_Dictionary_2026_Updated.xlsx
node ops/tools/build_robotic_ebus_workbook.mjs --runtime /path/to/node-runtime-with-artifact-tool
python ops/tools/prepare_robotic_ebus_corpus.py --source /path/to/robotic_EBUS_9_14_26 --output /new/corpus-version --seed 20260914 --overlap data/ml_training
python ops/tools/prepare_robotic_ebus_spans.py --corpus /new/corpus-version --output /new/annotation-version
# Review the span/relationship evidence and annotation manifest before training.
python ml/scripts/train_registry_ner.py --train-data /reviewed/train.bio.jsonl --validation-data /reviewed/validation.bio.jsonl --output-dir /new/checkpoint --epochs 2 --train-batch 4 --eval-batch 8 --max-length 256 --eval-steps 225 --save-steps 225 --seed 20260914
python ops/tools/build_focused_model_candidate.py --checkpoint /new/checkpoint --annotations /reviewed --output /new/inference-bundle
python ops/tools/eval_robotic_ebus.py --corpus data/ml_training/robotic_ebus_v1/corpus_20260914_v2 --gold data/knowledge/robotic_ebus_v1/reviewed_eval_selection.json --model-dir artifacts/robotic_ebus_v1/local_candidate_0_2_0 --baseline --output /tmp/focused-eval.json --require-acceptance
python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/focused-pr-gates
python ops/tools/build_registry_candidate.py --output /tmp/focused-source-candidate.tar.gz
```

Use the secure application's Python test environment for the cross-application validator:

```sh
/path/to/ip-registry-clinical/.venv/bin/python ops/tools/validate_robotic_ebus_roundtrip.py --clinical-root /path/to/ip-registry-clinical --national-root /path/to/ip-registry-national --output /tmp/roundtrip.json
```

Two fresh local synthetic installations were created separately for browser checks. Previous installations remain independently intact. No clinical or national historical records were transferred. For rollout, create new focused installations using qualified keys/configuration and transfer only independently revalidated eligible records within the same clinical or national boundary. Approval, patient context, current permissions, source ownership, exact contract and ID mapping must be rechecked; never copy the development database or training corpus.

The remaining release work is concrete: finish clinical annotation and semantic family-overlap adjudication; restore a qualified baseline; improve missed fields/relationships using training/validation material; evaluate an untouched qualification set across formats; independently review the source/model/dependencies; and complete the existing clinical-activation, operational and national disclosure/release qualifications. Those gates remain closed.

## Blinded adjudication workflow (2026-10-10)

See [the adjudication guide](ROBOTIC_EBUS_ADJUDICATION.md) for the reviewer CSV/HTML packet, span and relationship import, family/scenario split enforcement, and one-use qualification runner. [Readiness evidence](../outputs/robotic_ebus_v1/qualification_readiness.json) reports the pending human reviews and missing positive pilot coverage. The existing synthetic corpus remains engineering evidence; no clinical qualification or promotion is claimed.
