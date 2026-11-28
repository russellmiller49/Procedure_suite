# SMART on FHIR Integration (Epic / Oracle Health–Cerner)

The Procedure Suite can be launched from inside Epic and Oracle Health (Cerner) as a
**SMART on FHIR** app: a clinician opens it from the patient's chart, the app pulls the
procedure note from the EHR's FHIR API **in the browser**, and the note then flows through
the existing client-side PHI workflow (Run Detection → Apply Redactions → Submit) so the
coding server still only ever receives **scrubbed text**.

The feature is **optional and disabled by default** (`SMART_ENABLED`).

## Architecture (zero-knowledge preserved)

```
Epic / Cerner EHR ──(launch: iss + launch token)──> /ui/smart/launch.html
        ▲                                                   │ discovery (.well-known/smart-configuration)
        │                                                   │ OAuth2 authorization-code + PKCE (S256)
        └──(authorize + token, browser-only)◄───────────────┘
                                                            ▼
                                              /ui/smart/callback.html
                                                            │ session -> sessionStorage (per tab)
                                                            ▼
/ui/ dashboard "EHR Connection" panel ──(FHIR reads: Patient, DocumentReference, Binary)──> EHR
                                                            │ note text into editor
                                                            ▼
                              normal PHI flow: Run Detection → Apply Redactions → Submit
                                                            │ scrubbed text only
                                                            ▼
                                              POST /api/v1/process (unchanged)
```

Division of responsibilities:

- **Browser**: the entire OAuth dance (PKCE, state, token exchange, refresh) and all FHIR
  reads. Tokens and unredacted note text live only in the tab (`sessionStorage`) and are
  never sent to the Procedure Suite server.
- **Server**: one public endpoint, `GET /api/v1/smart/config`, which returns the issuer
  allowlist (FHIR base URLs + public `client_id`s + scopes). Nothing secret is served and
  nothing about the EHR session is stored.

This matches the repo's zero-knowledge client-side pseudonymization direction: the server
remains a stateless "scrubbed text in → registry + CPT out" engine.

## Files

| Piece | Path |
| --- | --- |
| Settings (env-driven, fail-soft) | `config/smart_settings.py` |
| Config endpoint | `app/api/routes/smart.py` (`GET /api/v1/smart/config`) |
| Response schemas | `app/api/schemas/smart.py` |
| Launch page (register in the EHR) | `ui/static/phi_redactor/smart/launch.html` + `launch.js` |
| OAuth redirect page | `ui/static/phi_redactor/smart/callback.html` + `callback.js` |
| Session + FHIR client | `ui/static/phi_redactor/smart/smartClient.js` |
| Pure helpers (PKCE, parsing, HTML/RTF→text) | `ui/static/phi_redactor/smart/smartCore.js` |
| Dashboard panel | `ui/static/phi_redactor/smart/smartPanel.js` (+ `#smartEhrCard` in `index.html`) |
| Example issuer allowlist | `configs/smart/issuers.example.json` |
| API tests | `tests/api/test_smart_config.py` |
| JS unit tests (Vitest) | `ui/source/registry_grid/src/__tests__/smartCore.test.js` |

## Server configuration

| Env var | Meaning |
| --- | --- |
| `SMART_ENABLED=1` | Turn the feature on (alias: `SMART_ON_FHIR_ENABLED`). Default: off. |
| `SMART_ISSUERS` | Inline JSON array of issuer objects (takes precedence). |
| `SMART_ISSUERS_FILE` | Path to a JSON file with the same array. |
| `SMART_DEFAULT_SCOPES` | Optional override of the base scope set. |

Issuer object fields: `name`, `iss` (exact FHIR base URL), `client_id` (public),
optional `vendor` (`epic` \| `cerner` \| `smart_launcher` \| `other`) and optional
`scopes` (verbatim override of the base scopes).

Example (`configs/smart/issuers.example.json`):

```json
[
  {
    "name": "Epic on FHIR Sandbox (R4)",
    "iss": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    "client_id": "REPLACE-WITH-EPIC-NON-PRODUCTION-CLIENT-ID",
    "vendor": "epic"
  },
  {
    "name": "Oracle Health (Cerner) Sandbox (R4)",
    "iss": "https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d",
    "client_id": "REPLACE-WITH-CERNER-CLIENT-ID",
    "vendor": "cerner"
  }
]
```

Validation is **fail-soft**: bad entries are skipped and reported in the endpoint's
`config_errors` (visible in the launch page console) instead of breaking startup. Rules:

- `iss` must be `https` (plain `http` tolerated only for `localhost` dev servers).
- `iss` is normalized (trailing slash stripped) and must be **unique**.
- Unknown keys in an issuer entry are rejected (catches typos like `clientid`).

Scopes: the default base set is
`openid fhirUser user/Patient.read user/Encounter.read user/DocumentReference.read user/Binary.read`.
The browser adds the launch-context scope at authorize time (`launch` for EHR launch,
`launch/patient` for standalone). For `vendor: "cerner"`, `online_access` is appended
automatically (Cerner access tokens last ~10 minutes; `online_access` grants a refresh
token valid for the EHR session). SMART v1-style scopes are the default for maximum
Epic/Cerner compatibility; set per-issuer `scopes` if a tenant requires v2 granular
scopes (e.g. `user/DocumentReference.rs`).

## URLs to register with the EHR

| Purpose | URL |
| --- | --- |
| SMART launch URL | `https://<your-host>/ui/smart/launch.html` |
| OAuth redirect URI | `https://<your-host>/ui/smart/callback.html` |

For local development, `http://localhost:8000/ui/smart/…` works with both vendor
sandboxes and the SMART Health IT launcher. Production registrations must be HTTPS.

## Epic registration (sandbox first)

1. Sign in at [fhir.epic.com](https://fhir.epic.com) (Epic on FHIR) → **Build Apps** →
   create an app for **Clinicians or Administrative Users**, FHIR version **R4**.
2. Select the APIs the app requests (they must cover the scopes):
   `Patient.Read (R4)`, `Encounter.Read (R4)`, `DocumentReference.Read (Clinical Notes) (R4)`,
   `DocumentReference.Search (Clinical Notes) (R4)`, `Binary.Read (Clinical Notes) (R4)`.
3. Set the **redirect URI** to your callback URL, and answer **No** to
   "can your app keep a secret" (public client — this app uses PKCE, which Epic requires
   for public clients). Epic derives allowed CORS origins from the registered redirect URIs.
4. Copy the **Non-Production Client ID** into `SMART_ISSUERS` with
   `iss = https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4`.
   New client IDs can take a while (up to ~12h) to propagate to the sandbox.
5. Test: either an EHR-launch simulation from Epic's tooling, or open
   `https://<host>/ui/smart/launch.html` with no parameters and pick the Epic issuer
   (standalone launch → Epic login → patient selection). Epic's public sandbox test
   credentials and test patients (e.g. Camila Lopez) are listed on fhir.epic.com.
6. Production: create the production client from the same app listing; the customer's
   Epic Client Systems Administrator authorizes/downloads it for their environment. Update
   `SMART_ISSUERS` with the production `iss` (each Epic customer has its own FHIR base URL)
   and production client ID — multiple issuer entries are supported side by side.

## Oracle Health (Cerner) registration

1. Sign in to the [Oracle Health developer console](https://code-console.cerner.com)
   (accounts via code.cerner.com) → create a **Provider** app.
2. App type **Public** (browser app, PKCE), launch type **EHR launch** (standalone also
   supported). Set the SMART Launch URI and Redirect URI from the table above.
3. Select scopes matching the config: `openid`, `fhirUser`, `launch`, `online_access`,
   `user/Patient.read`, `user/Encounter.read`, `user/DocumentReference.read`,
   `user/Binary.read`.
4. Copy the client ID into `SMART_ISSUERS` with the sandbox tenant
   `iss = https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d`.
5. Test with the console's launch tooling or a standalone launch; sandbox test users are
   documented in Oracle Health's developer docs.
6. Production: promote the app in the console and add the customer tenant's `iss`
   (`https://fhir-ehr.cerner.com/r4/<tenant-id>`) + client ID as another issuer entry.

## Local testing without a vendor sandbox (SMART Health IT launcher)

1. Start the dev server with SMART enabled:

   ```bash
   SMART_ENABLED=1 SMART_ISSUERS_FILE=configs/smart/issuers.example.json ./ops/devserver.sh
   ```

2. Open <https://launch.smarthealthit.org>, choose **Provider EHR Launch**, and set the
   App's Launch URL to `http://localhost:8000/ui/smart/launch.html`.
3. **Important:** the launcher passes a simulated `iss` that embeds launch options, e.g.
   `https://launch.smarthealthit.org/v/r4/sim/<encoded-options>/fhir`. Copy the exact
   FHIR base URL the launcher displays into your `SMART_ISSUERS` entry (any `client_id`
   works there, e.g. `procedure-suite-local`) — the allowlist matches the `iss` exactly.
4. Click Launch: EHR-simulated login → callback → the dashboard opens with the
   "EHR Connection (SMART on FHIR)" panel showing the patient and their documents.

## What the dashboard panel does

- Renders only when a SMART session exists in the tab (arrival via the launch flow).
- Shows the launch patient (name/DOB/sex/MRN — **browser-only**, never sent to the server)
  and lists the patient's `DocumentReference`s (US Core `category=clinical-note` search,
  falling back to an unfiltered patient search for tenants that reject `category`),
  newest first, with an "encounter" marker when a document belongs to the launch encounter.
- **Load** resolves the best attachment (`text/plain` → `text/html`/XHTML → RTF → PDF):
  - text/HTML/RTF are converted to plain text in the browser (RTF is best-effort) and
    inserted into the editor with `note_source_type=ehr_fhir`;
  - PDFs are handed to the existing **local** `pdf_local` extraction pipeline (same
    worker path as manual PDF upload).
- Loading a note performs the same reset as **New Note**, then the standard workflow
  applies: Run Detection → Apply Redactions → Submit Scrubbed Note.
- **Disconnect** clears the tab's session (tokens are gone when the tab closes anyway).

## Security model

- **Exact issuer allowlist**: the `iss` from the launch must exactly match a configured
  issuer (trailing-slash normalized) or the launch stops — prevents a malicious `iss`
  from harvesting tokens.
- **PKCE S256 + `state`** on every authorization; `aud` (required by Epic and Cerner) is
  always sent; discovered OAuth endpoints must be HTTPS (or localhost).
- **Tokens never leave the issuer origin**: FHIR/attachment URLs that resolve off the
  issuer's origin are refused before any `Authorization` header is attached.
- **Tokens never reach the Procedure Suite server**; sessions are per-tab
  `sessionStorage`, and token refresh (Cerner `online_access`) happens in the browser.
- `id_token` claims are decoded **without verification** and used for display only
  (clinician name in the banner) — never for authorization decisions.
- The SMART pages load only same-origin assets (consistent with the PHI redactor's
  vendored-assets constraint). The `/ui` COOP/COEP headers are compatible with this flow
  (full-page redirects + CORS-mode FHIR fetches); the EHR's FHIR + OAuth endpoints must
  serve CORS for registered browser apps, which Epic and Cerner do.
- Debug logging in the SMART modules is metrics/status-only — no raw clinical text.

## Limitations / roadmap

- **Read-only v1**: no FHIR write-back of CPT results (Epic/Cerner write support varies
  by tenant; export continues via the existing JSON/tables downloads). A future
  `DocumentReference`/charge write-back would be a separate, gated addition.
- One note loads at a time (mirrors the New Note workflow).
- RTF conversion is best-effort (the panel flags it for review).
- The `classic` UI variant (`ui/static/phi_redactor_classic/`) is not wired for SMART.
- Public-client PKCE only; a confidential-client/backend token flow is not implemented
  (not needed for browser-only reads, and it would route tokens through the server).

## Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| Launch page: "issuer is not on the server allowlist" | The EHR's `iss` doesn't exactly match a configured entry — copy the exact FHIR base URL (watch tenant IDs and the SMART launcher's `/sim/…/` segment). |
| Launch page: "SMART on FHIR is disabled" | Set `SMART_ENABLED=1` and restart; check `GET /api/v1/smart/config`. |
| `config_errors` in `/api/v1/smart/config` | Malformed `SMART_ISSUERS` JSON or rejected entries (http non-localhost, duplicate `iss`, unknown keys). |
| Token exchange fails (400/401) | Redirect URI mismatch (must byte-match the registered URI), unregistered scopes, or Epic client ID not yet propagated to the sandbox. |
| Panel: "EHR session expired or unauthorized" | Access token expired (Epic ~1h; Cerner ~10min without `online_access`) — relaunch from the EHR. |
| Notes list empty but patient has notes | Tenant rejects/ignores `category=clinical-note`; the client already falls back to a plain patient search — check the browser console for the FHIR response. |
| CORS errors in the browser console | The EHR must allow your app's origin (Epic: derived from redirect URIs; Cerner: registered app). Verify the registration and that you're on the registered host. |

## Tests

```bash
.venv/bin/python -m pytest -q tests/api/test_smart_config.py
cd ui/source/registry_grid && npx vitest run smartCore
```
