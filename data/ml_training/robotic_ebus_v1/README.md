# Focused synthetic corpus

Use **corpus_20260914_v2**. `corpus_20260914` is a superseded preparation and is retained only for audit. Do not mix its assignments into the frozen v2 split.

The v2 manifest freezes 168/36/36 training/validation/test families and 126 prior-use regression families. Related clean/messy/archive/PDF renditions remain grouped. The manifest and inventory contain hashes and overlap decisions. Full semantic scenario-overlap adjudication is still pending.

`annotations_20260914_v1` contains source-verified lexical weak labels, not independent clinical gold. Its manifest explicitly records this distinction. Generator metadata and hidden final outcomes must not be promoted into extraction labels without support in the supplied note. Relation, missingness and conflict annotation remains a separate review task.

The eight documents selected for the initial field pilot have now been inspected and evaluated. They are engineering regression evidence and cannot be reused as an untouched qualification test after tuning. Keep any newly established independent evaluation set isolated.

This directory belongs exclusively to Procedure_suite development/training. It must never be imported into the clinical or national repositories or their production stores.

The blinded adjudication packet, strict CSV import, semantic scenario audit, and one-use independent synthetic qualification workflow are documented in [ROBOTIC_EBUS_ADJUDICATION.md](../../../docs/ROBOTIC_EBUS_ADJUDICATION.md). Reviewer submissions remain pending; synthetic review cannot establish clinical validation.

During 2026-10-10 packet QA, all 77 test texts were displayed to the implementation agent. `data/knowledge/robotic_ebus_v1/qualification_exposure.json` records this conservative exposure classification. This corpus version now has no untouched qualification candidates; reblinding it cannot restore independence.
