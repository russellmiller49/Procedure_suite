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

  it("prefers native text when native density indicates a digital text layer", () => {
    const nativeText = Array.from({ length: 35 }, (_, i) => `Narrative line ${i + 1} with detailed bronchoscopy findings.`).join("\n");
    const result = arbitratePageText({
      nativeText,
      ocrText: "Noisy OCR variant",
      requestedSource: "ocr",
      ocrAvailable: true,
      classification: { needsOcr: true, nativeTextDensity: 0.0048 },
      stats: { nativeTextDensity: 0.0048, completenessConfidence: 0.92, contaminationScore: 0.18 },
    });

    expect(result.sourceDecision).toBe("native");
    expect(result.text).toContain("Narrative line 1");
    expect(result.reason).toMatch(/native text density/i);
  });

  it("does not bypass to native when dense text is flagged as fragmented", () => {
    const nativeText = [
      ...Array.from(
        { length: 18 },
        (_, i) => `Postoperative instruction line ${i + 1} is complete and clinically coherent for patient guidance.`,
      ),
      "surgeon every 4 hours.",
      ...Array.from(
        { length: 8 },
        (_, i) => `Follow-up narrative line ${i + 1} remains complete and clinically coherent for discharge education.`,
      ),
      "nose.",
    ].join("\n");
    const ocrText = [
      "Call surgeon every 4 hours for bleeding from the nose.",
      "Continue hydration and follow up with ENT as directed.",
    ].join("\n");

    const result = arbitratePageText({
      nativeText,
      ocrText,
      requestedSource: "ocr",
      ocrAvailable: true,
      classification: {
        needsOcr: true,
        nativeTextDensity: 0.0045,
        qualityFlags: ["FRAGMENTED_NATIVE_LINES"],
        reason: "fragmented native lines (2/30, orphan=1)",
      },
      stats: { nativeTextDensity: 0.0045, completenessConfidence: 0.92, contaminationScore: 0.2 },
    });

    expect(result.sourceDecision).not.toBe("native");
    expect(result.text).toContain("Call surgeon every 4 hours");
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

  it("repairs joined OCR continuation artifacts for mouth-or-nose phrases", () => {
    const cleaned = sanitizeOcrText(
      [
        "When the tonsil or adenoid scabs fall off, your child may have bleeding from the mouth",
        "nose.",
      ].join("\n"),
      { mode: "augment" },
    );

    expect(cleaned).toContain("bleeding from the mouth or nose.");
    expect(cleaned).not.toContain("mouth nose");
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

  it("prunes standalone anatomy caption lines from native text on image-heavy pages", () => {
    const nativeText = [
      "Procedure performed with moderate sedation.",
      "Left Mainstem",
      "Right Lower Lobe Entrance",
      "Follow up with pulmonology.",
    ].join("\n");

    const result = arbitratePageText({
      nativeText,
      requestedSource: "native",
      ocrAvailable: true,
      stats: { imageOpCount: 3, overlapRatio: 0.09, nativeTextDensity: 0.0031, completenessConfidence: 0.91 },
      classification: { needsOcr: false, nativeTextDensity: 0.0031 },
    });

    expect(result.sourceDecision).toBe("native");
    expect(result.text).toContain("Procedure performed with moderate sedation.");
    expect(result.text).toContain("Follow up with pulmonology.");
    expect(result.text).not.toContain("Left Mainstem");
    expect(result.text).not.toContain("Right Lower Lobe Entrance");
  });

  it("removes inline anatomy caption chunks split by wide spacing", () => {
    const cleaned = sanitizeOcrText(
      "Procedure note completed      Left Mainstem      Right Lower Lobe Entrance",
      { mode: "augment" },
    );

    expect(cleaned).toContain("Procedure note completed");
    expect(cleaned).not.toContain("Left Mainstem");
    expect(cleaned).not.toContain("Right Lower Lobe Entrance");
  });

  it("removes trailing caption suffixes attached with @ separators", () => {
    const cleaned = sanitizeOcrText(
      "EndoSoft Surgery Center @ Right Lower Lobe Entrance",
      { mode: "augment" },
    );

    expect(cleaned).toContain("EndoSoft Surgery Center");
    expect(cleaned).not.toContain("Right Lower Lobe Entrance");
  });

  it("drops numeric-prefix anatomy captions during native pruning", () => {
    const result = arbitratePageText({
      nativeText: [
        "Procedure Report  Bronchoscopy",
        "1 Right Lower Lobe Entrance",
        "2 Left Mainstem",
        "3 Left Lower Lobe",
        "Findings: No endobronchial lesion.",
      ].join("\n"),
      requestedSource: "native",
      ocrAvailable: true,
      stats: { imageOpCount: 6, overlapRatio: 0.24, nativeTextDensity: 0.003, completenessConfidence: 0.9 },
      classification: { needsOcr: false, nativeTextDensity: 0.003 },
    });

    expect(result.text).toContain("Procedure Report  Bronchoscopy");
    expect(result.text).toContain("Findings: No endobronchial lesion.");
    expect(result.text).not.toContain("1 Right Lower Lobe Entrance");
    expect(result.text).not.toContain("2 Left Mainstem");
    expect(result.text).not.toContain("3 Left Lower Lobe");
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

  it("replaces truncated native fragments with longer OCR narrative lines", () => {
    const merged = mergeNativeAndOcrText(
      [
        "PROCEDURE TECHNIQUE:",
        "surgeon every 4 hours.",
        "Bleeding:",
        "nose.",
      ].join("\n"),
      [
        "PROCEDURE TECHNIQUE:",
        "Give the prescribed pain medication Oxycodone and acetaminophen as ordered by your",
        "surgeon every 4 hours.",
        "Bleeding:",
        "When the tonsil or adenoid scabs fall off, your child may have bleeding from the mouth or",
        "nose.",
        "If you see blood, call ENT immediately.",
      ].join("\n"),
      { mode: "augment" },
    );

    const mergedLines = merged.split("\n").map((line) => line.trim());
    expect(merged).toContain("ordered by your surgeon every 4 hours.");
    expect(merged).toContain("bleeding from the mouth or nose.");
    expect(mergedLines).not.toContain("surgeon every 4 hours.");
    expect(mergedLines).not.toContain("nose.");
  });

  it("keeps repair-only merge bounded when OCR has no fragment match", () => {
    const nativeText = [
      "PROCEDURE TECHNIQUE:",
      "The bronchoscope was advanced to the distal airway.",
      "Findings remained stable with no bleeding.",
    ].join("\n");
    const ocrText = [
      "PROCEDURE TECHNIQUE:",
      "The bronchoscope was advanced to the distal airway.",
      "AEECRNIMT ## 0000 OO0O",
      "Random footer 12345 0000",
      "Additional noisy line not tied to native fragment recovery.",
      "Another extra OCR-only line that should not be imported in repair mode.",
    ].join("\n");

    const merged = mergeNativeAndOcrText(nativeText, ocrText, { mode: "repair_only" });
    const growthRatio = merged.length / Math.max(1, nativeText.length);

    expect(merged).toContain("The bronchoscope was advanced to the distal airway.");
    expect(merged).not.toContain("AEECRNIMT");
    expect(merged).not.toContain("Additional noisy line");
    expect(growthRatio).toBeLessThanOrEqual(1.2);
  });

  it("uses repair-only arbitration for OCR backfill pages", () => {
    const nativeText = [
      "PROCEDURE TECHNIQUE:",
      "surgeon every 4 hours.",
      "Bleeding:",
      "nose.",
    ].join("\n");
    const ocrText = [
      "Give the prescribed pain medication Oxycodone and acetaminophen as ordered by your",
      "surgeon every 4 hours.",
      "When the tonsil or adenoid scabs fall off, your child may have bleeding from the mouth or",
      "nose.",
      "Injected OCR-only noise that should not be appended.",
    ].join("\n");

    const result = arbitratePageText({
      nativeText,
      ocrText,
      requestedSource: "native",
      mergeMode: "repair_only",
      ocrAvailable: true,
      classification: { needsOcrBackfill: true, needsOcr: true },
      stats: { contaminationScore: 0.1, completenessConfidence: 0.9 },
    });

    expect(result.sourceDecision).toBe("hybrid");
    expect(result.text).toContain("ordered by your surgeon every 4 hours.");
    expect(result.text).toContain("mouth or nose.");
    expect(result.text).not.toContain("Injected OCR-only noise");
  });

  it("rejects low-similarity noisy OCR candidates during fragment repair", () => {
    const nativeText = [
      "PROCEDURE TECHNIQUE:",
      "surgeon every 4 hours.",
      "Bleeding:",
      "nose.",
    ].join("\n");
    const ocrText = [
      "AEECRNIMT ## OO0O 111",
      "Additional unrelated noisy sentence that does not end with the native fragment context.",
      "ete EIS Val ser a i",
      "Random footer 0000 OOOO",
    ].join("\n");

    const merged = mergeNativeAndOcrText(nativeText, ocrText, { mode: "repair_only" });
    expect(merged).toContain("surgeon every 4 hours.");
    expect(merged).toContain("nose.");
    expect(merged).not.toContain("Additional unrelated noisy sentence");
  });

  it("does not replace valid short uppercase narrative lines during fragment repair", () => {
    const merged = mergeNativeAndOcrText(
      [
        "FINDINGS:",
        "No bleeding.",
      ].join("\n"),
      [
        "FINDINGS:",
        "No bleeding.",
        "Noisy footer 0000 OOOO",
      ].join("\n"),
      { mode: "augment" },
    );

    const mergedLines = merged.split("\n");
    expect(mergedLines).toContain("No bleeding.");
    expect(merged).not.toContain("Noisy footer");
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

  it("drops Provation footer boilerplate and consecutive duplicate lines", () => {
    const cleaned = sanitizeOcrText(
      [
        "Bronchoscopy performed with moderate sedation.",
        "Bronchoscopy performed with moderate sedation.",
        "Powered by Provation MD",
        "Page 1 of 2",
        "Follow up with Pulmonology in 2 weeks.",
      ].join("\n"),
      { mode: "augment" },
    );

    expect(cleaned).toContain("Bronchoscopy performed with moderate sedation.");
    expect(cleaned).toContain("Follow up with Pulmonology in 2 weeks.");
    expect(cleaned).not.toContain("Powered by Provation");
    expect(cleaned).not.toContain("Page 1 of 2");
    expect(cleaned.split("\n").filter((line) => /moderate sedation/i.test(line))).toHaveLength(1);
  });
});
