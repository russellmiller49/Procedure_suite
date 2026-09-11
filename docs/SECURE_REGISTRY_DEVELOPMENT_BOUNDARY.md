# Synthetic R&D to independent clinical releases

Procedure_suite remains the synthetic development/training workspace. It does not gain clinical deployment rights, secure repository write tokens, signing keys, hospital credentials or patient records.

The new bounded packages are ip_registry_contracts and ip_registry_engine under packages/. Version 0.1.0 includes explicit clinical/national contracts and original deterministic pathology/follow-up extraction copied with import-only namespace changes. The complete procedure/NER/CPT engine is not yet isolated or qualified; existing runtime behavior and quality gates are unchanged.

Build an import-only candidate using:

~~~sh
python ops/tools/build_registry_candidate.py --output /tmp/candidate.tar.gz
~~~

This writes an allowlisted archive with per-file digests and original source provenance. It cannot push to or install into a secure repository. Each private repository owns candidate retrieval, integrity checks, review, tests, build, signing and installation approval. Its promotion tool rejects path traversal, links, unknown archive paths and digest mismatches.

Do not point the existing deployment mirror at either private registry. No changes were made to that workflow. Sharing candidate source is distinct from deployment authorization.

Feedback from hospitals is limited to approved aggregate findings or newly authored synthetic reproductions. National contribution is never permission to use hospital/national records for model development or training.

Run the bounded package tests independently:

~~~sh
python -m pytest packages/tests --confcutdir=packages/tests
~~~

These tests establish source-copy equivalence and contract/proposal behavior. They do not replace existing extraction-first quality gates or institutional clinical validation.
