import { describe, expect, it } from "vitest";

import { detectRegexPhi } from "../../../../static/phi_redactor/pdf_local/redaction/regexDetectors.js";

function spansOfType(spans, type) {
  return spans.filter((span) => span.type === type);
}

describe("detectRegexPhi", () => {
  it("detects email, phone, and SSN", () => {
    const text = [
      "Contact: jane.doe@example.org",
      "Phone: (415) 555-0199 ext 23",
      "SSN: 123-45-6789",
    ].join("\n");

    const spans = detectRegexPhi(text);

    expect(spansOfType(spans, "EMAIL").length).toBe(1);
    expect(spansOfType(spans, "PHONE").length).toBe(1);
    expect(spansOfType(spans, "SSN").length).toBeGreaterThanOrEqual(1);
  });

  it("detects MRN/account with anchor words and common date formats", () => {
    const text = [
      "MRN: A1234567",
      "Account Number: AC-998877",
      "DOB: 01/21/1978",
      "Procedure date 2026-02-17",
      "Follow-up on January 2, 2026",
    ].join("\n");

    const spans = detectRegexPhi(text);

    expect(spansOfType(spans, "MRN").length).toBe(1);
    expect(spansOfType(spans, "ACCOUNT").length).toBe(1);
    expect(spansOfType(spans, "DATE").length).toBeGreaterThanOrEqual(3);
  });

  it("detects URL and IPv4", () => {
    const text = "Portal https://hospital.example.org and device at 10.24.3.99";
    const spans = detectRegexPhi(text);

    expect(spansOfType(spans, "URL").length).toBe(1);
    expect(spansOfType(spans, "IP").length).toBe(1);
  });

  it("avoids common non-PHI numeric codes", () => {
    const text = "CPT 31652 and 99152; room 316-52; no patient identifiers present.";
    const spans = detectRegexPhi(text);

    expect(spansOfType(spans, "SSN").length).toBe(0);
    expect(spansOfType(spans, "PHONE").length).toBe(0);
    expect(spansOfType(spans, "MRN").length).toBe(0);
    expect(spansOfType(spans, "ACCOUNT").length).toBe(0);
  });

  it("handles adversarial punctuation-heavy input without crashing", () => {
    const text = "!!!@@@###$$$%%%^^^&&&***((()))---___+++=== ".repeat(2000);
    const spans = detectRegexPhi(text);

    expect(Array.isArray(spans)).toBe(true);
    expect(spans.length).toBe(0);
  });
});
