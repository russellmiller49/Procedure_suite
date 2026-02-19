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

  it("anchors OCR lines under matching section headers instead of floating between sections", () => {
    const nativeText = [
      "INSTRUMENTS: Loaner",
      "MEDICATIONS: Demerol 25 mg, Versed 1 mg",
      "PROCEDURE TECHNIQUE:",
      "FINDINGS:",
    ].join("\n");

    const ocrText = [
      "PROCEDURE TECHNIQUE:",
      "consent was obtained from the patient and monitoring devices were connected.",
      "FINDINGS:",
      "Extrinsic compression stricture extends for the length of 3cm and lumen was 8mm.",
    ].join("\n");

    const merged = mergeNativeAndOcrText(nativeText, ocrText, { mode: "augment" });
    const mergedLines = merged.split("\n");
    const techniqueHeaderIdx = mergedLines.findIndex((line) => /^PROCEDURE TECHNIQUE:/i.test(line));
    const findingsHeaderIdx = mergedLines.findIndex((line) => /^FINDINGS:/i.test(line));

    expect(techniqueHeaderIdx).toBeGreaterThan(-1);
    expect(findingsHeaderIdx).toBeGreaterThan(techniqueHeaderIdx);
    expect(mergedLines[techniqueHeaderIdx + 1]).toMatch(/consent was obtained/i);
    expect(mergedLines[findingsHeaderIdx + 1]).toMatch(/Extrinsic compression stricture/i);
  });

  it("drops side-column anatomy caption lines from OCR merges", () => {
    const merged = mergeNativeAndOcrText(
      "PROCEDURE TECHNIQUE:\nThe bronchoscope was advanced.",
      [
        "Right Lower Lobe Entrance",
        "Left Mainstem",
        "The patient was connected to monitoring devices and oxygen was provided.",
      ].join("\n"),
      { mode: "augment" },
    );

    expect(merged).toContain("The patient was connected to monitoring devices");
    expect(merged).not.toContain("Right Lower Lobe Entrance");
    expect(merged).not.toContain("Left Mainstem");
  });

  it("routes narrative preamble lines to technique/findings instead of instruments", () => {
    const nativeText = [
      "INSTRUMENTS: Loaner",
      "MEDICATIONS: Demerol 25 mg, Versed 1 mg",
      "PROCEDURE TECHNIQUE:",
      "FINDINGS:",
    ].join("\n");
    const ocrText = [
      "anesthesia and conscious sedation. The bronchoscope was inserted and the airway examined.",
      "for the length of 3cm. Scope could be advanced beyond the stricture. The estimated diameter of the lumen was 4mm.",
    ].join("\n");

    const merged = mergeNativeAndOcrText(nativeText, ocrText, { mode: "augment" });
    const mergedLines = merged.split("\n");
    const instrumentsIdx = mergedLines.findIndex((line) => /^INSTRUMENTS:/i.test(line));
    const techniqueIdx = mergedLines.findIndex((line) => /^PROCEDURE TECHNIQUE:/i.test(line));
    const findingsIdx = mergedLines.findIndex((line) => /^FINDINGS:/i.test(line));

    expect(instrumentsIdx).toBeGreaterThan(-1);
    expect(techniqueIdx).toBeGreaterThan(-1);
    expect(findingsIdx).toBeGreaterThan(techniqueIdx);
    expect(mergedLines[instrumentsIdx + 1]).toMatch(/^MEDICATIONS:/i);
    expect(mergedLines[techniqueIdx + 1]).toMatch(/anesthesia and conscious sedation/i);
    expect(mergedLines[findingsIdx + 1]).toMatch(/estimated diameter of the lumen was 4mm/i);
  });

  it("drops PHOTOREPORT and O/0-heavy code junk lines during merge", () => {
    const merged = mergeNativeAndOcrText(
      [
        "ICD 10 Codes:",
        "CPT Code:",
        "31622 Bronchoscopy",
      ].join("\n"),
      [
        "ICD 10 Codes:",
        "O10 COM OC",
        "O77 O00",
        "5/18/2024, 08:56:49 AM By Debbie Doe, MD PHOTOREPORT",
      ].join("\n"),
      { mode: "augment" },
    );

    expect(merged).not.toContain("O10 COM OC");
    expect(merged).not.toContain("O77 O00");
    expect(merged).not.toContain("PHOTOREPORT");
    expect(merged).toContain("31622 Bronchoscopy");
  });
});
