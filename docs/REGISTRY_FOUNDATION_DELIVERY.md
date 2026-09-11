# Registry implementation delivery — 2026-09-10

**A working synthetic foundation has been implemented. The full hospital/national roadmap is not complete, and clinical activation is blocked in release 0.1.0.**

## Independent repositories

| Application | Private repository | Local checkout | Validated commit |
|---|---|---|---|
| Hospital clinical registry | [ip-registry-clinical](https://github.com/russellmiller49/ip-registry-clinical) | /Users/russellmiller/Projects/ip-registry-clinical | 410f56aad2d6f2049c540219de7d5f06817ce0f9 |
| AABIP national registry | [ip-registry-national](https://github.com/russellmiller49/ip-registry-national) | /Users/russellmiller/Projects/ip-registry-national | 26826678425249c252b6a47df7c0c0938188e247 |

These repositories have independent Git histories, private visibility, independent CI and fresh synthetic installations. Main requires the validate check, an approval of the latest push and administrator enforcement; force pushes and deletion are disabled. No institutional credentials, PHI, existing R&D databases, trained-model binaries or historical sessions were copied.

Procedure_suite remains the synthetic R&D workspace. Its new packages and candidate builder are on codex/registry-secure-foundation. Existing application behavior and the deployment mirror were not modified. The private repositories contain allowlisted source candidates awaiting independent review and qualification.

## Working implementation

- Hospital: patient/encounter context, patient-scoped access, encrypted immutable sources, extraction proposals, evidence validation, draft/approval concurrency, amendments, targets/specimens, pathology/follow-up and completeness worklists.
- Security: opaque backend sessions, OIDC/PKCE, CSRF, authorization, administrator separation, application encryption, transactional audit, safe errors, browser storage restrictions and local PDF/OCR assets.
- Extraction: durable leased jobs, retry limits and stale-result rejection. Only deterministic pathology/follow-up routines are currently isolated; the full NER/RAW-ML/CPT pipeline remains unported and unqualified.
- EHR: server-backed SMART and bounded FHIR patient/encounter/document reads. Actual vendor/hospital registration and qualification have not occurred.
- National: dedicated strict record contracts, random purpose-specific identities, signed profile validation, patient eligibility, reviewed outbox release, intake/receipts, revisions/withdrawals and authenticated institution binding.
- Participation: independent contribution/institutional/regional permissions, separate analytical populations, current-policy enforcement, report/job invalidation and stale-download rejection.
- Reporting: provisional annual measures with missingness, sample-size, peer-count, small-cell, complementary and dominance checks. No actual national dataset or live benchmarking is approved.
- Operations: container builds, PostgreSQL/Alembic, source promotion, signing preflight, audit-archive utility and Podman/systemd/backup reference files.

## Verified results

| Evidence | Result |
|---|---|
| Hospital suite | 45 passed on disposable PostgreSQL 17 |
| National suite | 39 passed on disposable PostgreSQL 17 |
| R&D package/source-equivalence suite | 7 passed |
| SQLite suites | Original 40 hospital / 34 national tests passed; five additional release-control cases are database-independent |
| Fresh Alembic migrations | Both applications upgraded; no schema drift |
| Frontends | TypeScript and Vite builds passed |
| Dependency checks | Python runtime and browser audits passed |
| Containers | Both runtime images built; non-root/read-only/offline smoke checks exercised |
| Browser | Synthetic OIDC, patient/encounter selection, source import, draft/approval, native PDF, scanned OCR, participation controls and sign-out checked |

Independent GitHub evidence: [hospital CI](https://github.com/russellmiller49/ip-registry-clinical/actions/runs/34561079170) and [national CI](https://github.com/russellmiller49/ip-registry-national/actions/runs/34561079939).

No full Procedure_suite extraction-quality, hospital/vendor, penetration, recovery-time, statistical disclosure or clinical sample qualification is claimed.

## Remaining engineering and approvals

The authoritative engineering/gate inventory is [clinical implementation status](https://github.com/russellmiller49/ip-registry-clinical/blob/main/docs/IMPLEMENTATION_STATUS.md), also included in the national repository. It covers full engine isolation/equivalence; vendor imports/conformance; richer clinical reconciliation and retention; PDF fusion parity; signed participation synchronization and dispatch reconciliation; expert-approved cross-report disclosure; Linux/backup/monitoring/capacity qualification; and complete release evidence.

UCSD/MD Anderson institutional owners, AABIP governance/agreements, the national dictionary/measures, qualified Expert Determination and approved clinical/statistical validation protocols remain external prerequisites. No institution or third party was contacted. The first clinical pilot is whichever institution completes its prerequisites first.

GitHub accepted branch protection but rejected required environment reviewers with HTTP 422 under the current billing plan. The signing workflow now has a separate preflight that refuses absent or incomplete independent review protections. No signed image was published or installed. See [release controls](https://github.com/russellmiller49/ip-registry-clinical/blob/main/docs/RELEASE_CONTROLS.md). Enabling clinical mode requires a separately reviewed release after the engineering and institutional gates are met.
