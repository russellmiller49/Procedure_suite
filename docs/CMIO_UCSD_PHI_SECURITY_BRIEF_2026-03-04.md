# CMIO Meeting Brief: PHI, Security, and Hospital Approval Readiness

Date: March 4, 2026  
Audience: CMIO / Compliance / Security leadership  
Project context: Procedure Suite moving from Railway + Supabase toward AWS + BAA-backed vendor stack

## 1. Executive Summary

Procedure Suite is already designed around a zero-knowledge direction: client-side PHI redaction first, then server-side extraction/coding on scrubbed text. That is the right architecture for hospital adoption.

The key message for this meeting is:

- The architecture direction is strong and aligned with hospital requirements.
- Several production hardening controls are still needed before broad clinical deployment (especially auth on primary APIs, stricter PHI ingress enforcement, and infrastructure guardrails).
- Moving to AWS + BAAs can close most approval blockers quickly if paired with explicit technical policy changes.

## 2. Current State of PHI and Security (as implemented today)

## A. Data flow and PHI handling

- Primary API is `POST /api/v1/process` (stateless extraction-first path).
- UI workflow is client-side PHI detection -> apply redactions -> submit with `already_scrubbed=true`.
- Browser UI explicitly states server should only receive scrubbed text.
- Server can still accept raw text when `already_scrubbed=false` and then attempts server-side redaction.
- Multi-document bundle path enforces date-token guardrails and supports scrubbed bundle ingestion.

## B. Client-side protections already in place

- PHI redaction is performed in browser workers with local/vendor assets.
- PDF and camera OCR paths are browser-local; intended flow avoids raw OCR text uploads.
- Reporter Builder enforces `Run Detection` -> `Apply Redactions` before seed and sends `already_scrubbed=true`.

## C. Server-side safeguards already in place

- Startup invariants enforced:
  - `PROCSUITE_PIPELINE_MODE=extraction_first` required.
  - In production mode (`CODER_REQUIRE_PHI_REVIEW=true` or `PROCSUITE_ENV=production`), also enforces:
    - `REGISTRY_EXTRACTION_ENGINE=parallel_ner`
    - `REGISTRY_SCHEMA_VERSION=v3`
    - `REGISTRY_AUDITOR_SOURCE=raw_ml`
- PHI review gating exists: can force `review_status=pending_phi_review` and `needs_manual_review=true`.
- Legacy endpoints are feature-gated (`PROCSUITE_ALLOW_LEGACY_ENDPOINTS`, `PROCSUITE_ALLOW_REQUEST_MODE_OVERRIDE`).

## D. Storage and vault posture

- Stateless endpoint can run without persistent PHI storage.
- Optional persistence layers store scrubbed note text and response payloads for workflow/audit use.
- Client vault models are ciphertext-only by design.
- PHI domain includes vault + audit models and encryption adapters.

## E. External LLM exposure (OpenAI/Gemini)

- Extraction-first core can run without LLM as primary extractor.
- Optional features can call external LLMs:
  - OCR correction endpoint (`/api/v1/ocr/correct`) requires `already_scrubbed=true`.
  - Reporter findings mode can use LLM.
  - Self-correction can use LLM when enabled (`REGISTRY_SELF_CORRECT_ENABLED=1`; default is off).
- Offline controls exist (`OPENAI_OFFLINE`, `GEMINI_OFFLINE`).

## 3. Approval-Critical Gaps to Acknowledge in Meeting

These are the most important items likely to block hospital approval unless addressed:

1. Primary API auth gap
- `/api/v1/process` is not currently protected by user/service auth dependency.
- Auth exists for some user-scoped vault/case endpoints, but not the main processing path.

2. Raw PHI ingress is still possible
- `/api/v1/process` accepts `already_scrubbed=false` and then does server-side scrubbing.
- If server-side scrubber is unavailable/misconfigured, code path can proceed with raw text plus warning.

3. Dev/demo defaults still visible in runtime wiring
- PHI dependency wiring includes demo-oriented notes and fallback behavior (stub scrubber fallback unless strict mode).
- This will raise red flags in formal security review if unchanged.

4. CORS is currently open (`allow_origins=["*"]`)
- Appropriate for local/dev, not acceptable for hospital production.

5. Unauthenticated PHI-specific routes exist
- `/v1/phi/*` routes (including re-identification route) are not currently behind the same auth model expected for production.

6. Persistence PHI-risk scanner is limited
- Current pre-persist PHI risk scan checks obvious patterns but is not a full safe-harbor validator.

## 4. Target State for AWS + BAA Deployment

Recommended target posture for hospital approval:

1. Enforce scrubbed-only ingress
- Reject `already_scrubbed=false` on production processing routes.
- Keep server-side scrubbing as an emergency fallback path only, not default clinical path.

2. Require strong auth on all clinical APIs
- Protect `/api/v1/process`, `/api/v1/process_bundle`, `/report/*`, `/v1/phi/*`.
- Use hospital SSO/OIDC for interactive users and signed service tokens for backend calls.

3. Lock down network and platform
- Private subnets, least-privilege IAM, WAF, strict egress controls.
- No public DB access; TLS in transit everywhere.

4. Strengthen key/secrets management
- AWS KMS-backed keys for any server-side encryption needs.
- Secrets in AWS Secrets Manager; no long-lived secrets in `.env` for production.

5. Restrict browser/API origins
- Environment-based allowlist CORS and UI origin controls.

6. Disable non-essential endpoints in production
- Remove or hard-disable demo/QA/legacy routes from prod exposure.

7. LLM vendor controls with BAAs
- Limit LLM calls to scrubbed-only payloads.
- Explicitly disable optional LLM paths unless BAA + legal sign-off is complete.
- Document provider-specific retention/training settings and contractual controls.

## 5. Questions to Ask the CMIO and Security Team

Use these directly in the meeting.

## A. Clinical/compliance policy

1. Is a scrubbed-text-only architecture acceptable if the server never receives direct identifiers in normal operation?
2. Which PHI classes are considered highest risk for this use case (names, dates, MRNs, free-text identifiers)?
3. Do you require Safe Harbor-level de-identification, expert determination, or a hybrid policy?
4. Are provider names acceptable to retain in scrubbed text, or should we redact all person names by default?

## B. Security architecture requirements

1. Is hospital approval contingent on SSO enforcement for every API, including machine-to-machine endpoints?
2. Do you require all production endpoints to be private/VPN-only, or is public + zero-trust gateway acceptable?
3. What are your minimum requirements for audit logs, retention, and immutability?
4. What incident response SLA (detection, notification, containment) is required by policy?

## C. Data retention and governance

1. What retention period is acceptable for scrubbed notes and derived outputs?
2. Should we support configurable org-level data residency and deletion windows?
3. Is persistent storage of scrubbed note text acceptable, or must we run stateless-only for pilot?
4. What patient/encounter re-identification controls must be in place before go-live?

## D. Vendor/BAA decisions (OpenAI + Gemini)

1. Under what conditions will UCSD approve using external LLM vendors for de-identified text?
2. Do you require BAA coverage even for scrubbed/de-identified payloads?
3. Which vendor attestations are mandatory (SOC 2, HITRUST, pen test summaries, subprocessor lists)?
4. Are there approved defaults for no-training/no-retention modes that legal expects in contracts?
5. Should we disable all optional LLM-assisted features until both BAAs are fully executed?

## E. Pilot scope and sign-off gates

1. What is the minimum control set required for a pilot versus production expansion?
2. Who must sign off (CMIO, CISO, Privacy, Legal, Compliance, IT security architecture)?
3. What objective acceptance criteria should we use (auth complete, scrubbed-only enforcement, audit coverage, penetration test)?

## 6. Recommended Commitments to Bring Into the Meeting

Offer these as near-term commitments:

1. Lock production to scrubbed-only ingress and enforce auth on `/api/v1/process`.
2. Disable demo/legacy/QA routes and tighten CORS before pilot.
3. Use AWS-native secrets and key management from day one.
4. Keep optional LLM features off until BAA/legal controls are complete.
5. Provide a written data-flow + threat model + control matrix for final security review.

## 7. Suggested Meeting Outcome

Aim to leave with:

- A yes/no list of required controls for pilot approval.
- A clear stance on external LLM usage with BAAs.
- Named approvers and required evidence artifacts.
- A short remediation timeline tied to go-live criteria.

