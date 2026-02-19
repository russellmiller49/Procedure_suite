import { describe, expect, it } from "vitest";

import {
  arbitratePageText,
  mergeNativeAndOcrText,
  sanitizeOcrText,
} from "../../../../static/phi_redactor/pdf_local/pdf/fusion.js";

describe("pdf fusion arbitration", () => {
  it("blocks OCR-requested pages when OCR is unavailable", () => {
    const result = arbitratePageText({
      nativeText: "Partial native text",
      requestedSource: "ocr",
      ocrAvailable: false,
      classification: { needsOcr: true },
      stats: { contaminationScore: 0.2, completenessConfidence: 0.62 },
    });

    expect(result.sourceDecision).toBe("native");
    expect(result.blocked).toBe(true);
  });

  it("uses OCR text when native text is empty", () => {
    const result = arbitratePageText({
      nativeText: "",
      ocrText: "Recovered paragraph from OCR",
      requestedSource: "ocr",
      ocrAvailable: true,
      stats: { contaminationScore: 0.05, completenessConfidence: 0.9 },
    });

    expect(result.sourceDecision).toBe("ocr");
    expect(result.text).toContain("Recovered paragraph from OCR");
    expect(result.blocked).toBe(false);
  });

  it("uses hybrid merge when OCR recovers substantially more content on contaminated page", () => {
    const nativeText = "Procedure Report\nLeft upper lobe";
    const ocrText = [
      "Procedure Report",
      "Left upper lobe with severe stenosis",
      "Distal airway narrowing described in detail",
    ].join("\n");

    const result = arbitratePageText({
      nativeText,
      ocrText,
      requestedSource: "ocr",
      ocrAvailable: true,
      stats: { contaminationScore: 0.28, completenessConfidence: 0.58 },
    });

    expect(result.sourceDecision).toBe("hybrid");
    expect(result.text).toContain("Procedure Report");
    expect(result.text).toContain("Distal airway narrowing described in detail");
    expect(result.text.split("\n")).not.toContain("Left upper lobe");
  });

  it("deduplicates line content in native+ocr merges", () => {
    const merged = mergeNativeAndOcrText(
      "Line A\nLine B",
      "line a\nLine C",
    );

    expect(merged.split("\n")).toEqual(["Line A", "Line B", "Line C"]);
  });

  it("filters OCR photoreport noise while preserving narrative recovery", () => {
    const nativeText = "Procedure Report\nFindings:";
    const ocrText = [
      "OOOOMOO00 00000 COO = COO ooo",
      "CULT ILE                                                                                                    OWL LT",
      "consent was obtained from the patient after explaining the risks and alternatives to the procedure",
    ].join("\n");

    const merged = mergeNativeAndOcrText(nativeText, ocrText, { mode: "augment" });
    expect(merged).toContain("consent was obtained from the patient");
    expect(merged).not.toContain("OOOOMOO00");
    expect(merged).not.toContain("CULT ILE");
  });

  it("sanitizes OCR-only text by dropping repetitive noise lines", () => {
    const cleaned = sanitizeOcrText(
      [
        "OOOO 0000 OOO 000",
        "Large airway obstruction in the left main stem for one month.",
      ].join("\n"),
      { mode: "full" },
    );

    expect(cleaned).toContain("Large airway obstruction in the left main stem for one month.");
    expect(cleaned).not.toContain("OOOO 0000");
  });

  it("trims noisy OCR prefixes and keeps clinical sentence cores", () => {
    const cleaned = sanitizeOcrText(
      "MOO 00000 C00 C6 Large airway obstruction in the left main stem for one month.",
      { mode: "augment" },
    );

    expect(cleaned).toBe("Large airway obstruction in the left main stem for one month.");
  });

  it("drops OCR vendor/footer boilerplate in augment mode", () => {
    const cleaned = sanitizeOcrText(
      [
        "PHOTOREPORT",
        "EndoSoft Surgery Center OMI00C00 00007) OOO",
        "which the patient appeared to understand and so stated.",
      ].join("\n"),
      { mode: "augment" },
    );

    expect(cleaned).not.toContain("PHOTOREPORT");
    expect(cleaned).not.toContain("EndoSoft Surgery Center");
    expect(cleaned).toContain("which the patient appeared to understand and so stated.");
  });

  it("drops short O/0-heavy OCR garbage lines even with stray stopwords", () => {
    const cleaned = sanitizeOcrText("Oooo mo0 of '", { mode: "augment" });
    expect(cleaned).toBe("");
  });

  it("strips O/0-heavy OCR suffix clusters from narrative lines", () => {
    const cleaned = sanitizeOcrText(
      [
        "The patient was connected to the monitoring devices.",
        "Continuous oxygen was provided with a nasal cannula and IV medicine administered through an @ Como coo ooo Coo Oooo ooo",
      ].join("\n"),
      { mode: "augment" },
    );

    expect(cleaned).toContain("Continuous oxygen was provided with a nasal cannula");
    expect(cleaned).toContain("administered through an");
    expect(cleaned).not.toContain("@");
    expect(cleaned).not.toMatch(/\bComo\b/);
    expect(cleaned).not.toMatch(/\bcoo\b/i);
    expect(cleaned).not.toMatch(/\bOooo\b/);
  });

  it("strips all-caps O-heavy OCR prefixes from narrative lines", () => {
    const cleaned = sanitizeOcrText(
      "OMOMOD Extrinsic compression stricture begins left mainstem bronchus to the left lower lobe extending for the length of 3cm.",
      { mode: "augment" },
    );

    expect(cleaned).toContain("Extrinsic compression stricture begins left mainstem bronchus");
    expect(cleaned).not.toContain("OMOMOD");
  });
});
