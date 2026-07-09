import { describe, expect, it } from "vitest";

import {
  buildAuthorizeUrl,
  buildScopes,
  buildTokenRequestBody,
  classifyAttachment,
  computeCodeChallenge,
  decodeJwtPayload,
  findIssuerConfig,
  formatPatientBanner,
  htmlToPlainText,
  isHttpsOrLocalhost,
  normalizeIss,
  noteMatchesEncounter,
  parseDocumentReferenceBundle,
  pickBestAttachment,
  rtfToPlainText,
} from "../../../../static/phi_redactor/smart/smartCore.js";

describe("PKCE", () => {
  it("computes the RFC 7636 S256 test vector", async () => {
    const challenge = await computeCodeChallenge("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk");
    expect(challenge).toBe("E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM");
  });
});

describe("issuer matching", () => {
  it("normalizes trailing slashes", () => {
    expect(normalizeIss("https://ehr.example.org/fhir/")).toBe("https://ehr.example.org/fhir");
  });

  it("matches allowlisted issuers regardless of trailing slash", () => {
    const issuers = [{ name: "A", iss: "https://ehr.example.org/fhir" }];
    expect(findIssuerConfig(issuers, "https://ehr.example.org/fhir/")).toBe(issuers[0]);
    expect(findIssuerConfig(issuers, "https://evil.example.org/fhir")).toBeNull();
  });

  it("accepts https and localhost http only", () => {
    expect(isHttpsOrLocalhost("https://ehr.example.org/fhir")).toBe(true);
    expect(isHttpsOrLocalhost("http://localhost:8080/fhir")).toBe(true);
    expect(isHttpsOrLocalhost("http://ehr.example.org/fhir")).toBe(false);
    expect(isHttpsOrLocalhost("not a url")).toBe(false);
  });
});

describe("scopes and OAuth request builders", () => {
  it("adds launch for EHR launch and strips stale launch scopes", () => {
    expect(buildScopes("openid fhirUser launch/patient user/Patient.read", "ehr")).toBe(
      "launch openid fhirUser user/Patient.read"
    );
  });

  it("adds launch/patient for standalone launch", () => {
    const scopes = buildScopes("openid launch user/DocumentReference.read", "standalone");
    expect(scopes.split(" ")[0]).toBe("launch/patient");
    expect(scopes.split(" ")).not.toContain("launch");
  });

  it("builds the authorize URL with aud and S256 PKCE", () => {
    const url = new URL(
      buildAuthorizeUrl({
        authorizationEndpoint: "https://ehr.example.org/oauth2/authorize?tenant=t1",
        clientId: "client-123",
        redirectUri: "https://app.example.org/ui/smart/callback.html",
        scopes: "launch openid",
        state: "state-1",
        aud: "https://ehr.example.org/fhir",
        codeChallenge: "challenge-1",
        launch: "launch-token",
      })
    );
    expect(url.searchParams.get("tenant")).toBe("t1");
    expect(url.searchParams.get("response_type")).toBe("code");
    expect(url.searchParams.get("aud")).toBe("https://ehr.example.org/fhir");
    expect(url.searchParams.get("code_challenge_method")).toBe("S256");
    expect(url.searchParams.get("code_challenge")).toBe("challenge-1");
    expect(url.searchParams.get("launch")).toBe("launch-token");
  });

  it("omits launch param for standalone authorize URLs", () => {
    const url = new URL(
      buildAuthorizeUrl({
        authorizationEndpoint: "https://ehr.example.org/oauth2/authorize",
        clientId: "c",
        redirectUri: "https://app.example.org/cb",
        scopes: "launch/patient openid",
        state: "s",
        aud: "https://ehr.example.org/fhir",
        codeChallenge: "ch",
      })
    );
    expect(url.searchParams.has("launch")).toBe(false);
  });

  it("builds token exchange and refresh bodies", () => {
    const exchange = new URLSearchParams(
      buildTokenRequestBody({
        grantType: "authorization_code",
        code: "code-1",
        redirectUri: "https://app.example.org/cb",
        clientId: "client-123",
        codeVerifier: "verifier-1",
      })
    );
    expect(exchange.get("grant_type")).toBe("authorization_code");
    expect(exchange.get("code_verifier")).toBe("verifier-1");
    expect(exchange.get("client_id")).toBe("client-123");

    const refresh = new URLSearchParams(
      buildTokenRequestBody({
        grantType: "refresh_token",
        refreshToken: "refresh-1",
        clientId: "client-123",
      })
    );
    expect(refresh.get("grant_type")).toBe("refresh_token");
    expect(refresh.get("refresh_token")).toBe("refresh-1");
  });
});

describe("DocumentReference bundle parsing", () => {
  const bundle = {
    resourceType: "Bundle",
    entry: [
      { resource: { resourceType: "OperationOutcome" } },
      {
        resource: {
          resourceType: "DocumentReference",
          id: "older",
          status: "current",
          type: { coding: [{ display: "Procedure Note" }] },
          context: {
            period: { start: "2026-06-01T09:00:00Z" },
            encounter: [{ reference: "Encounter/enc-1" }],
          },
          content: [
            {
              attachment: {
                contentType: "application/pdf",
                url: "Binary/pdf-1",
                title: "Bronchoscopy report",
              },
            },
          ],
        },
      },
      {
        resource: {
          resourceType: "DocumentReference",
          id: "newer",
          status: "current",
          docStatus: "final",
          date: "2026-07-02T10:30:00Z",
          description: "IP procedure note",
          type: { text: "Procedure Note" },
          content: [
            { attachment: { contentType: "text/html; charset=utf-8", url: "Binary/html-1" } },
            { attachment: { contentType: "application/pdf", url: "Binary/pdf-2" } },
          ],
        },
      },
    ],
  };

  it("maps, sorts newest-first, and skips non-DocumentReference entries", () => {
    const notes = parseDocumentReferenceBundle(bundle);
    expect(notes.map((note) => note.id)).toEqual(["newer", "older"]);
    expect(notes[0].title).toBe("IP procedure note");
    expect(notes[1].date).toBe("2026-06-01T09:00:00Z"); // context.period.start fallback
    expect(notes[1].typeText).toBe("Procedure Note"); // coding display fallback
    expect(notes[1].title).toBe("Bronchoscopy report"); // attachment title fallback
  });

  it("marks encounter-context notes", () => {
    const notes = parseDocumentReferenceBundle(bundle);
    expect(noteMatchesEncounter(notes[1], "enc-1")).toBe(true);
    expect(noteMatchesEncounter(notes[0], "enc-1")).toBe(false);
  });

  it("prefers text over html over rtf over pdf attachments", () => {
    const best = pickBestAttachment([
      { contentType: "application/pdf", url: "Binary/1" },
      { contentType: "application/rtf", url: "Binary/2" },
      { contentType: "text/html", url: "Binary/3" },
      { contentType: "text/plain" }, // no url/data -> not retrievable, skipped
    ]);
    expect(best.contentType).toBe("text/html");
  });

  it("classifies content types with parameters", () => {
    expect(classifyAttachment("text/html; charset=utf-8")).toBe("html");
    expect(classifyAttachment("application/xhtml+xml")).toBe("html");
    expect(classifyAttachment("application/pdf")).toBe("pdf");
    expect(classifyAttachment("application/rtf")).toBe("rtf");
    expect(classifyAttachment("image/tiff")).toBe("unknown");
  });
});

describe("note content conversion", () => {
  it("converts HTML to readable plain text", () => {
    const text = htmlToPlainText(
      "<html><head><style>p{color:red}</style></head><body>" +
        "<h1>Procedure Note</h1><p>EBUS-TBNA of station 4R.</p>" +
        "<ul><li>ROSE: adequate</li><li>No complications</li></ul>" +
        "<p>Sat &gt; 94% &amp; stable&nbsp;throughout.</p></body></html>"
    );
    expect(text).toContain("Procedure Note");
    expect(text).toContain("EBUS-TBNA of station 4R.");
    expect(text).toContain("- ROSE: adequate");
    expect(text).toContain("Sat > 94% & stable throughout.");
    expect(text).not.toContain("color:red");
  });

  it("converts RTF to plain text (paragraphs, hex, unicode, escapes)", () => {
    const rtf =
      "{\\rtf1\\ansi{\\fonttbl{\\f0 Arial;}}\\f0 Bronchoscopy findings\\par " +
      "Lidocaine 1% applied\\tab tolerated\\par caf\\'e9 au lait \\{stent\\} " +
      "patient\\u8217?s airway}";
    const text = rtfToPlainText(rtf);
    expect(text).toContain("Bronchoscopy findings\nLidocaine 1% applied\ttolerated");
    expect(text).toContain("café au lait {stent}");
    expect(text).toContain("patient’s airway");
    expect(text).not.toContain("Arial");
  });

  it("passes non-RTF input through unchanged", () => {
    expect(rtfToPlainText("plain narrative text")).toBe("plain narrative text");
  });
});

describe("display helpers", () => {
  it("decodes a JWT payload for display only", () => {
    const payload = { fhirUser: "Practitioner/123", name: "Dr. Example" };
    const b64 = btoa(JSON.stringify(payload)).replace(/\+/g, "-").replace(/\//g, "_");
    expect(decodeJwtPayload(`header.${b64}.sig`)).toEqual(payload);
    expect(decodeJwtPayload("garbage")).toBeNull();
  });

  it("formats a patient banner with MRN detection", () => {
    const banner = formatPatientBanner({
      name: [{ given: ["Camila", "Maria"], family: "Lopez" }],
      birthDate: "1987-09-12",
      gender: "female",
      identifier: [
        { type: { text: "SSN" }, value: "000-00-0000" },
        { type: { coding: [{ code: "MR" }] }, value: "E3826" },
      ],
    });
    expect(banner.name).toBe("Camila Maria Lopez");
    expect(banner.mrn).toBe("E3826");
    expect(banner.birthDate).toBe("1987-09-12");
  });
});
