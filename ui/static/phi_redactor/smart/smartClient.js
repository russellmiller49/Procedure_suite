// SMART on FHIR browser client: session storage, OAuth (PKCE) flow, FHIR reads.
//
// All OAuth and FHIR traffic is browser <-> EHR. The Procedure Suite server only
// supplies the public issuer allowlist via GET /api/v1/smart/config; it never sees
// tokens or unredacted note text. Sessions live in sessionStorage (per-tab, cleared
// when the tab closes), mirroring the standard SMART browser-app pattern.

import {
  buildAuthorizeUrl,
  buildScopes,
  buildTokenRequestBody,
  bytesToUtf8,
  classifyAttachment,
  createPkcePair,
  decodeBase64ToBytes,
  decodeJwtPayload,
  formatPatientBanner,
  htmlToPlainText,
  isHttpsOrLocalhost,
  normalizeIss,
  parseDocumentReferenceBundle,
  randomToken,
  rtfToPlainText,
} from "./smartCore.js";

const PENDING_KEY = "procsuite.smart.pending";
const SESSION_KEY = "procsuite.smart.session";
const PENDING_MAX_AGE_MS = 10 * 60 * 1000;

// ---------------------------------------------------------------------------
// Server-side allowlist config
// ---------------------------------------------------------------------------

export async function fetchSmartUiConfig() {
  const resp = await fetch("/api/v1/smart/config", { headers: { Accept: "application/json" } });
  if (!resp.ok) throw new Error(`SMART config endpoint failed (${resp.status})`);
  return resp.json();
}

// ---------------------------------------------------------------------------
// Session storage
// ---------------------------------------------------------------------------

export function getSmartSession() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const session = JSON.parse(raw);
    return session && session.accessToken ? session : null;
  } catch {
    return null;
  }
}

export function saveSmartSession(session) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSmartSession() {
  sessionStorage.removeItem(SESSION_KEY);
  sessionStorage.removeItem(PENDING_KEY);
}

function requireSession() {
  const session = getSmartSession();
  if (!session) throw new Error("No active SMART/EHR session in this tab");
  return session;
}

// ---------------------------------------------------------------------------
// Discovery + authorization
// ---------------------------------------------------------------------------

export async function discoverSmartConfiguration(iss) {
  const wellKnown = `${normalizeIss(iss)}/.well-known/smart-configuration`;
  const resp = await fetch(wellKnown, { headers: { Accept: "application/json" } });
  if (!resp.ok) {
    throw new Error(`SMART discovery failed (HTTP ${resp.status}) at ${wellKnown}`);
  }
  const config = await resp.json();
  const authorizationEndpoint = String(config?.authorization_endpoint || "");
  const tokenEndpoint = String(config?.token_endpoint || "");
  if (!isHttpsOrLocalhost(authorizationEndpoint) || !isHttpsOrLocalhost(tokenEndpoint)) {
    throw new Error("SMART discovery returned missing or non-HTTPS OAuth endpoints");
  }
  return { authorizationEndpoint, tokenEndpoint, capabilities: config?.capabilities || [] };
}

// issuerConfig comes from /api/v1/smart/config: {name, iss, client_id, vendor, scopes}.
// `launch` is the opaque launch token from an EHR launch; omit for standalone.
export async function beginAuthorization({ issuerConfig, launch }) {
  const launchType = launch ? "ehr" : "standalone";
  const iss = normalizeIss(issuerConfig.iss);
  const { authorizationEndpoint, tokenEndpoint } = await discoverSmartConfiguration(iss);
  const { verifier, challenge } = await createPkcePair();
  const state = randomToken(16);
  const redirectUri = new URL("callback.html", window.location.href).toString();
  const scopes = buildScopes(issuerConfig.scopes, launchType);

  sessionStorage.setItem(
    PENDING_KEY,
    JSON.stringify({
      state,
      verifier,
      redirectUri,
      tokenEndpoint,
      scopes,
      launchType,
      createdAt: Date.now(),
      issuer: {
        name: issuerConfig.name,
        iss,
        vendor: issuerConfig.vendor,
        clientId: issuerConfig.client_id,
      },
    })
  );

  window.location.assign(
    buildAuthorizeUrl({
      authorizationEndpoint,
      clientId: issuerConfig.client_id,
      redirectUri,
      scopes,
      state,
      aud: iss,
      codeChallenge: challenge,
      launch,
    })
  );
}

function tokenExpiryMs(expiresIn) {
  const seconds = Math.max(60, Number(expiresIn) || 3600);
  return Date.now() + seconds * 1000 - 30_000;
}

export async function completeAuthorization(searchParams) {
  const error = searchParams.get("error");
  if (error) {
    const description = searchParams.get("error_description") || "authorization was not granted";
    throw new Error(`${error}: ${description}`);
  }
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  if (!code || !state) throw new Error("Callback URL is missing the code/state parameters");

  const pendingRaw = sessionStorage.getItem(PENDING_KEY);
  if (!pendingRaw) {
    throw new Error("No pending SMART authorization in this tab — start again from the EHR.");
  }
  const pending = JSON.parse(pendingRaw);
  if (pending.state !== state) {
    throw new Error("State mismatch — stale or forged callback. Start the launch again.");
  }
  if (Date.now() - Number(pending.createdAt || 0) > PENDING_MAX_AGE_MS) {
    sessionStorage.removeItem(PENDING_KEY);
    throw new Error("The sign-in took too long and expired. Start the launch again.");
  }

  const resp = await fetch(pending.tokenEndpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: buildTokenRequestBody({
      grantType: "authorization_code",
      code,
      redirectUri: pending.redirectUri,
      clientId: pending.issuer.clientId,
      codeVerifier: pending.verifier,
    }),
  });
  sessionStorage.removeItem(PENDING_KEY);
  if (!resp.ok) {
    const body = (await resp.text()).slice(0, 300);
    throw new Error(`Token exchange failed (HTTP ${resp.status}): ${body}`);
  }
  const token = await resp.json();
  if (!token.access_token) throw new Error("Token response is missing access_token");

  const idClaims = token.id_token ? decodeJwtPayload(token.id_token) : null;
  const session = {
    iss: pending.issuer.iss,
    issuerName: pending.issuer.name,
    vendor: pending.issuer.vendor,
    clientId: pending.issuer.clientId,
    tokenEndpoint: pending.tokenEndpoint,
    accessToken: token.access_token,
    refreshToken: token.refresh_token || "",
    scope: token.scope || pending.scopes,
    patientId: String(token.patient || ""),
    encounterId: String(token.encounter || ""),
    fhirUser: String(idClaims?.fhirUser || ""),
    userDisplay: String(idClaims?.name || ""),
    expiresAt: tokenExpiryMs(token.expires_in),
  };
  saveSmartSession(session);
  return session;
}

async function refreshSession(session) {
  if (!session.refreshToken) return null;
  let resp;
  try {
    resp = await fetch(session.tokenEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: buildTokenRequestBody({
        grantType: "refresh_token",
        refreshToken: session.refreshToken,
        clientId: session.clientId,
      }),
    });
  } catch {
    return null;
  }
  if (!resp.ok) return null;
  const token = await resp.json().catch(() => null);
  if (!token?.access_token) return null;
  const next = {
    ...session,
    accessToken: token.access_token,
    refreshToken: token.refresh_token || session.refreshToken,
    expiresAt: tokenExpiryMs(token.expires_in),
  };
  saveSmartSession(next);
  return next;
}

// ---------------------------------------------------------------------------
// FHIR reads
// ---------------------------------------------------------------------------

function resolveFhirUrl(session, pathOrUrl) {
  const base = `${session.iss}/`;
  const url = new URL(String(pathOrUrl), base);
  // Never send the Bearer token off the issuer's origin (guards against a
  // DocumentReference pointing its attachment.url at a third-party host).
  if (url.origin !== new URL(base).origin) {
    throw new Error(`Refusing to send EHR credentials to a non-issuer origin: ${url.origin}`);
  }
  return url.toString();
}

export async function smartFhirFetch(pathOrUrl, { accept, raw } = {}) {
  let session = requireSession();
  if (Date.now() >= Number(session.expiresAt || 0)) {
    session = (await refreshSession(session)) || session;
  }
  const url = resolveFhirUrl(session, pathOrUrl);
  const doFetch = (sess) =>
    fetch(url, {
      headers: {
        Authorization: `Bearer ${sess.accessToken}`,
        Accept: accept || "application/fhir+json",
      },
    });

  let resp = await doFetch(session);
  if (resp.status === 401) {
    const refreshed = await refreshSession(session);
    if (refreshed) resp = await doFetch(refreshed);
  }
  if (raw) return resp;
  if (!resp.ok) {
    const err = new Error(`FHIR request failed (HTTP ${resp.status}) for ${url}`);
    err.status = resp.status;
    throw err;
  }
  return resp.json();
}

export async function fetchPatientContext() {
  const session = requireSession();
  if (!session.patientId) return null;
  const patient = await smartFhirFetch(`Patient/${encodeURIComponent(session.patientId)}`);
  return formatPatientBanner(patient);
}

// Lists recent clinical notes for the launch patient. Tries the US Core
// clinical-note category first; falls back to an unfiltered patient search for
// servers that reject the category parameter (some Cerner tenants).
export async function listClinicalNotes() {
  const session = requireSession();
  if (!session.patientId) {
    throw new Error("No patient context from this launch (missing launch/patient scope?)");
  }
  const pid = encodeURIComponent(session.patientId);
  const queries = [
    `DocumentReference?patient=${pid}&category=clinical-note&_count=50`,
    `DocumentReference?patient=${pid}&_count=50`,
  ];
  let lastError = null;
  for (let i = 0; i < queries.length; i += 1) {
    try {
      const bundle = await smartFhirFetch(queries[i]);
      const notes = parseDocumentReferenceBundle(bundle);
      if (notes.length || i === queries.length - 1) return notes;
    } catch (err) {
      lastError = err;
    }
  }
  if (lastError) throw lastError;
  return [];
}

// Resolves one attachment to either plain text (ready for the editor) or PDF
// bytes (handed to the existing local PDF extraction pipeline).
export async function fetchNoteAttachmentContent(attachment) {
  let bytes = null;
  let contentType = String(attachment?.contentType || "");

  if (attachment?.data) {
    bytes = decodeBase64ToBytes(attachment.data);
  } else if (attachment?.url) {
    const resp = await smartFhirFetch(attachment.url, {
      raw: true,
      accept: contentType || "application/fhir+json",
    });
    if (!resp.ok) {
      const err = new Error(`Attachment fetch failed (HTTP ${resp.status})`);
      err.status = resp.status;
      throw err;
    }
    const respType = String(resp.headers.get("content-type") || "").toLowerCase();
    if (respType.includes("json")) {
      // Binary requested as FHIR JSON: {resourceType: "Binary", contentType, data}
      const payload = await resp.json();
      if (payload?.resourceType === "Binary" && payload.data) {
        bytes = decodeBase64ToBytes(payload.data);
        contentType = String(payload.contentType || contentType);
      } else {
        throw new Error("Attachment endpoint returned JSON that is not a Binary resource");
      }
    } else {
      bytes = new Uint8Array(await resp.arrayBuffer());
      if (respType) contentType = respType;
    }
  } else {
    throw new Error("Attachment has neither inline data nor a url");
  }

  const kind = classifyAttachment(contentType);
  if (kind === "pdf") return { kind: "pdf", bytes, contentType };
  if (kind === "text") return { kind: "text", text: bytesToUtf8(bytes), contentType };
  if (kind === "html") {
    return { kind: "text", text: htmlToPlainText(bytesToUtf8(bytes)), contentType };
  }
  if (kind === "rtf") {
    return {
      kind: "text",
      text: rtfToPlainText(bytesToUtf8(bytes)),
      contentType,
      bestEffort: true,
    };
  }
  throw new Error(`Unsupported attachment content type: ${contentType || "unknown"}`);
}
