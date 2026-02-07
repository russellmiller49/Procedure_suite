# Knowledge Inventory (Single Source of Truth)

This repository is transitioning to **zero‑knowledge client‑side pseudonymization**:
the browser scrubs PHI and the server acts as a **stateless logic engine** (**Text In → Codes Out**).

This document defines which files/sections are **authoritative** for the extraction‑first pipeline and which are **legacy/reference** to prevent drift.

## Matrix (Authoritative → Consumer)

| Purpose | Authoritative Source | Notes / Consumers |
|---|---|---|
| CPT code metadata + RVUs + CMS financials | `data/knowledge/ip_coding_billing_v3_0.json` → `master_code_index` | Used by `app/coder/adapters/persistence/csv_kb_adapter.py` (CodingService KB) and `app/common/knowledge.py` RVU helpers. |
| CPT add‑on detection | `data/knowledge/ip_coding_billing_v3_0.json` → `add_on_codes` | Normalize `+`/non‑`+` variants at runtime. |
| Bundling / internal rule metadata | `data/knowledge/ip_coding_billing_v3_0.json` → `bundling_rules`, `ncci_pairs` | Used by rule validators and bundling logic; ensure only one canonical ruleset for enforcement. |
| Terminology / synonyms | `data/knowledge/ip_coding_billing_v3_0.json` → `synonyms`, `terminology_mappings` | All phrase lists used for detection should come from here (avoid duplicated lists in code or golden files). Consumers include `app/autocode/ip_kb/ip_kb.py` and `app/common/knowledge.py`. |
| Registry schema validation | `data/knowledge/IP_Registry.json` | Source of truth for `app/registry/schema.py` (dynamic RegistryRecord model). |
| Golden reference rules / notes | `ip_golden_knowledge_v2_2.json` | Legacy/reference. May inform rule design, but should not be the runtime source of synonyms/term lists. |

## Legacy/Reference Areas (Non‑Authoritative)

These sections may exist for historical reasons or display-only estimates; they must not drive runtime logic when `master_code_index` is present:

- `data/knowledge/ip_coding_billing_v3_0.json`: `fee_schedules`, `rvus`, `cms_rvus`, and other RVU/payment sub‑sections (reference/estimate only).

## Change Policy

- New synonym/term additions should require editing **one file**: `data/knowledge/ip_coding_billing_v3_0.json`.
- Runtime code should treat `master_code_index` as authoritative whenever present.
