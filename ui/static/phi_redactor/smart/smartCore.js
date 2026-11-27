// SMART on FHIR core helpers — pure functions only (no DOM, no storage, no fetch).
// Used by smartClient.js / smartPanel.js in the browser and unit-tested with Vitest
// from ui/source/registry_grid/src/__tests__/smartCore.test.js.
//
// PHI stance: everything here runs in the browser. EHR tokens and unredacted note
// text never leave the client; the coding server only ever receives scrubbed text
// through the existing detect -> redact -> submit workflow.

const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]", "::1"]);

// ---------------------------------------------------------------------------
// URL / issuer helpers
// ---------------------------------------------------------------------------

export function normalizeIss(iss) {
  return String(iss || "").trim().replace(/\/+$/, "");
}

export function findIssuerConfig(issuers, iss) {
  const target = normalizeIss(iss);
  if (!target) return null;
  const list = Array.isArray(issuers) ? issuers : [];
  return list.find((issuer) => normalizeIss(issuer?.iss) === target) || null;
}

export function isHttpsOrLocalhost(url) {
  let parsed;
  try {
    parsed = new URL(String(url || ""));
  } catch {
    return false;
  }
  if (parsed.protocol === "https:") return true;
  return parsed.protocol === "http:" && LOCAL_HOSTS.has(parsed.hostname);
}

// ---------------------------------------------------------------------------
// PKCE / randomness (WebCrypto)
// ---------------------------------------------------------------------------

export function base64UrlEncode(bytes) {
  const arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let binary = "";
  for (let i = 0; i < arr.length; i += 1) binary += String.fromCharCode(arr[i]);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function randomToken(byteLength = 32) {
  const bytes = new Uint8Array(byteLength);
  crypto.getRandomValues(bytes);
  return base64UrlEncode(bytes);
}

export async function computeCodeChallenge(verifier) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier));
  return base64UrlEncode(new Uint8Array(digest));
}

export async function createPkcePair() {
  const verifier = randomToken(32);
  return { verifier, challenge: await computeCodeChallenge(verifier) };
}

// ---------------------------------------------------------------------------
// Scope / authorize / token request builders
// ---------------------------------------------------------------------------

const LAUNCH_SCOPES = new Set(["launch", "launch/patient", "launch/encounter"]);

// launchType: "ehr" (launched from within Epic/Cerner with a launch token) or
// "standalone" (user-initiated; the EHR prompts for patient selection).
export function buildScopes(baseScopes, launchType) {
  const parts = String(baseScopes || "")
    .split(/\s+/)
    .filter((part) => part && !LAUNCH_SCOPES.has(part));
  const launchScope = launchType === "ehr" ? "launch" : "launch/patient";
  return [...new Set([launchScope, ...parts])].join(" ");
}

export function buildAuthorizeUrl(params) {
  const {
    authorizationEndpoint,
    clientId,
    redirectUri,
    scopes,
    state,
    aud,
    codeChallenge,
    launch,
  } = params;
  const url = new URL(authorizationEndpoint);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("client_id", clientId);
  url.searchParams.set("redirect_uri", redirectUri);
  url.searchParams.set("scope", scopes);
  url.searchParams.set("state", state);
  // Epic and Cerner both require aud = the FHIR base URL (iss) being authorized.
  url.searchParams.set("aud", aud);
  url.searchParams.set("code_challenge", codeChallenge);
  url.searchParams.set("code_challenge_method", "S256");
  if (launch) url.searchParams.set("launch", launch);
  return url.toString();
}

export function buildTokenRequestBody(params) {
  const body = new URLSearchParams();
  if (params.grantType === "refresh_token") {
    body.set("grant_type", "refresh_token");
    body.set("refresh_token", params.refreshToken);
    body.set("client_id", params.clientId);
  } else {
    body.set("grant_type", "authorization_code");
    body.set("code", params.code);
    body.set("redirect_uri", params.redirectUri);
    body.set("client_id", params.clientId);
    body.set("code_verifier", params.codeVerifier);
  }
  return body.toString();
}

// ---------------------------------------------------------------------------
// Base64 / UTF-8 / JWT (display-only) helpers
// ---------------------------------------------------------------------------

export function decodeBase64ToBytes(b64) {
  const cleaned = String(b64 || "").replace(/\s+/g, "");
  const binary = atob(cleaned);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

export function bytesToUtf8(bytes) {
  const arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  return new TextDecoder("utf-8", { fatal: false }).decode(arr);
}

// Unverified decode of a JWT payload. Only ever used for display (e.g. the
// fhirUser/name claims from the id_token we just received over TLS from the
// token endpoint) — never for authorization decisions.
export function decodeJwtPayload(token) {
  try {
    const part = String(token || "").split(".")[1];
    if (!part) return null;
    const b64 = part.replace(/-/g, "+").replace(/_/g, "/");
    const padded = b64 + "=".repeat((4 - (b64.length % 4)) % 4);
    return JSON.parse(bytesToUtf8(decodeBase64ToBytes(padded)));
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// DocumentReference / attachment handling
// ---------------------------------------------------------------------------

export function classifyAttachment(contentType) {
  const mime = String(contentType || "").split(";")[0].trim().toLowerCase();
  if (mime === "text/plain") return "text";
  if (mime === "text/html" || mime === "application/xhtml+xml" || mime === "text/xhtml") {
    return "html";
  }
  if (mime === "application/rtf" || mime === "text/rtf" || mime === "application/x-rtf") {
    return "rtf";
  }
  if (mime === "application/pdf") return "pdf";
  return "unknown";
}

const ATTACHMENT_RANK = { text: 0, html: 1, rtf: 2, pdf: 3, unknown: 9 };

export function pickBestAttachment(attachments) {
  const list = Array.isArray(attachments) ? attachments.filter(Boolean) : [];
  let best = null;
  let bestRank = Infinity;
  for (const attachment of list) {
    if (!attachment.url && !attachment.data) continue;
    const rank = ATTACHMENT_RANK[classifyAttachment(attachment.contentType)];
    if (rank < bestRank) {
      best = attachment;
      bestRank = rank;
    }
  }
  return best;
}

// Flattens a FHIR searchset Bundle of DocumentReference resources into a
// display-ready list, newest first. Tolerates Epic/Cerner shape differences
// (missing date -> context.period.start, type.text -> coding display, ...).
export function parseDocumentReferenceBundle(bundle) {
  const entries = Array.isArray(bundle?.entry) ? bundle.entry : [];
  const notes = [];
  for (const entry of entries) {
    const resource = entry?.resource;
    if (!resource || resource.resourceType !== "DocumentReference") continue;
    const attachments = (Array.isArray(resource.content) ? resource.content : [])
      .map((content) => content?.attachment)
      .filter(Boolean)
      .map((attachment) => ({
        contentType: String(attachment.contentType || ""),
        url: String(attachment.url || ""),
        data: String(attachment.data || ""),
        title: String(attachment.title || ""),
      }));
    const typeText =
      resource.type?.text ||
      resource.type?.coding?.[0]?.display ||
      resource.type?.coding?.[0]?.code ||
      "";
    const categoryText =
      resource.category?.[0]?.text || resource.category?.[0]?.coding?.[0]?.display || "";
    notes.push({
      id: String(resource.id || ""),
      status: String(resource.status || ""),
      docStatus: String(resource.docStatus || ""),
      date: String(resource.date || resource.context?.period?.start || ""),
      typeText: String(typeText),
      categoryText: String(categoryText),
      title: String(resource.description || attachments[0]?.title || typeText || "Document"),
      encounterRef: String(resource.context?.encounter?.[0]?.reference || ""),
      attachments,
    });
  }
  notes.sort((a, b) => b.date.localeCompare(a.date));
  return notes;
}

export function noteMatchesEncounter(note, encounterId) {
  if (!encounterId || !note?.encounterRef) return false;
  const ref = String(note.encounterRef);
  return ref === `Encounter/${encounterId}` || ref.endsWith(`/Encounter/${encounterId}`);
}

// ---------------------------------------------------------------------------
// HTML -> plain text (regex-based so it also runs under Node for tests)
// ---------------------------------------------------------------------------

const NAMED_ENTITIES = {
  amp: "&",
  lt: "<",
  gt: ">",
  quot: '"',
  apos: "'",
  nbsp: " ",
  ndash: "-",
  mdash: "-",
  bull: "-",
  deg: "°",
  micro: "µ",
  plusmn: "±",
};

function decodeHtmlEntities(text) {
  return text
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(parseInt(dec, 10)))
    .replace(/&([a-z]+);/gi, (match, name) => {
      const replacement = NAMED_ENTITIES[name.toLowerCase()];
      return replacement === undefined ? match : replacement;
    });
}

export function htmlToPlainText(html) {
  let text = String(html || "");
  text = text.replace(/<(script|style)\b[\s\S]*?<\/\1\s*>/gi, " ");
  text = text.replace(/<!--[\s\S]*?-->/g, " ");
  text = text.replace(/<br\s*\/?>/gi, "\n");
  text = text.replace(/<li\b[^>]*>/gi, "- ");
  text = text.replace(/<\/t[dh]>/gi, "\t");
  text = text.replace(
    /<\/(p|div|li|tr|h[1-6]|section|header|table|ul|ol|blockquote|pre|title)\s*>/gi,
    "\n"
  );
  text = text.replace(/<[^>]+>/g, "");
  text = decodeHtmlEntities(text);
  text = text
    .replace(/\r\n?/g, "\n")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n");
  return text.trim();
}

// ---------------------------------------------------------------------------
// RTF -> plain text (best effort; Epic historically serves RTF note Binaries)
// ---------------------------------------------------------------------------

const RTF_SKIP_DESTINATIONS = new Set([
  "fonttbl",
  "colortbl",
  "stylesheet",
  "info",
  "pict",
  "object",
  "header",
  "footer",
  "headerl",
  "headerr",
  "footerl",
  "footerr",
  "themedata",
  "colorschememapping",
  "latentstyles",
  "datastore",
  "generator",
  "xmlnstbl",
  "listtable",
  "listoverridetable",
  "rsidtbl",
]);

export function rtfToPlainText(rtf) {
  const input = String(rtf || "");
  if (!/^\s*{\s*\\rtf/.test(input)) return input;

  let out = "";
  let i = 0;
  const n = input.length;
  let depth = 0;
  let skipUntilDepth = -1; // >=0 while inside an ignorable destination group
  let ucSkip = 1; // \ucN: fallback chars to skip after each \uN

  while (i < n) {
    const ch = input[i];
    if (ch === "{") {
      depth += 1;
      if (skipUntilDepth < 0) {
        const rest = input.slice(i + 1, i + 32);
        if (/^\\\*/.test(rest)) {
          skipUntilDepth = depth; // starred destination: skip unless understood
        } else {
          const dest = rest.match(/^\\([a-zA-Z]+)/);
          if (dest && RTF_SKIP_DESTINATIONS.has(dest[1].toLowerCase())) skipUntilDepth = depth;
        }
      }
      i += 1;
      continue;
    }
    if (ch === "}") {
      if (skipUntilDepth >= 0 && depth === skipUntilDepth) skipUntilDepth = -1;
      depth = Math.max(0, depth - 1);
      i += 1;
      continue;
    }
    if (skipUntilDepth >= 0) {
      i += 1;
      continue;
    }
    if (ch === "\\") {
      const next = input[i + 1];
      if (next === "\\" || next === "{" || next === "}") {
        out += next;
        i += 2;
        continue;
      }
      if (next === "~") {
        out += " ";
        i += 2;
        continue;
      }
      if (next === "'") {
        const code = Number.parseInt(input.slice(i + 2, i + 4), 16);
        if (Number.isFinite(code)) out += String.fromCharCode(code);
        i += 4;
        continue;
      }
      const ctrl = input.slice(i, i + 32).match(/^\\([a-zA-Z]+)(-?\d+)?[ ]?/);
      if (ctrl) {
        const word = ctrl[1];
        const numArg = ctrl[2] === undefined ? null : Number.parseInt(ctrl[2], 10);
        i += ctrl[0].length;
        if (word === "par" || word === "line" || word === "sect" || word === "page") out += "\n";
        else if (word === "tab" || word === "cell") out += "\t";
        else if (word === "row") out += "\n";
        else if (word === "emdash" || word === "endash") out += "-";
        else if (word === "lquote" || word === "rquote") out += "'";
        else if (word === "ldblquote" || word === "rdblquote") out += '"';
        else if (word === "uc") ucSkip = numArg === null ? 1 : Math.max(0, numArg);
        else if (word === "u" && numArg !== null) {
          let codePoint = numArg;
          if (codePoint < 0) codePoint += 65536;
          out += String.fromCharCode(codePoint);
          let skipped = 0;
          while (skipped < ucSkip && i < n) {
            if (input[i] === "\\" && input[i + 1] === "'") i += 4;
            else i += 1;
            skipped += 1;
          }
        }
        // all other control words (formatting) are dropped
        continue;
      }
      i += 1;
      continue;
    }
    if (ch === "\r" || ch === "\n") {
      // raw newlines in RTF source are not content
      i += 1;
      continue;
    }
    out += ch;
    i += 1;
  }

  return out.replace(/[ \t]+\n/g, "\n").replace(/\n{3,}/g, "\n\n").trim();
}

// ---------------------------------------------------------------------------
// Patient display helpers
// ---------------------------------------------------------------------------

export function formatPatientBanner(patient) {
  const name0 = patient?.name?.[0];
  const assembled = [
    Array.isArray(name0?.given) ? name0.given.join(" ") : "",
    name0?.family || "",
  ]
    .filter(Boolean)
    .join(" ");
  const identifiers = Array.isArray(patient?.identifier) ? patient.identifier : [];
  const mrnEntry = identifiers.find(
    (identifier) =>
      identifier?.type?.coding?.some((coding) => coding?.code === "MR") ||
      /\bmrn\b/i.test(String(identifier?.type?.text || ""))
  );
  return {
    name: String(name0?.text || assembled || "Unknown patient"),
    birthDate: String(patient?.birthDate || ""),
    gender: String(patient?.gender || ""),
    mrn: String(mrnEntry?.value || ""),
  };
}
