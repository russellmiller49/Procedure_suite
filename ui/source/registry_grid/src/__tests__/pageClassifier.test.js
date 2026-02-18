import { describe, expect, it } from "vitest";

import {
  classifyPage,
  isUnsafeNativePage,
  resolvePageSource,
} from "../../../../static/phi_redactor/pdf_local/pdf/pageClassifier.js";

describe("pageClassifier", () => {
  it("keeps high-quality native pages as native", () => {
    const stats = {
      charCount: 2200,
      itemCount: 460,
      nonPrintableRatio: 0,
      singleCharItemRatio: 0.02,
      imageOpCount: 0,
      overlapRatio: 0,
      contaminationScore: 0,
      completenessConfidence: 0.97,
    };

    const classification = classifyPage(stats, "Detailed narrative text with clear findings.");
    expect(classification.needsOcr).toBe(false);
    expect(classification.confidence).toBeGreaterThan(0.6);
  });

  it("flags contaminated low-confidence pages as OCR-needed", () => {
    const stats = {
      charCount: 210,
      itemCount: 190,
      nonPrintableRatio: 0.03,
      singleCharItemRatio: 0.21,
      imageOpCount: 8,
      overlapRatio: 0.26,
      contaminationScore: 0.31,
      completenessConfidence: 0.48,
    };

    const classification = classifyPage(stats, "1 2 3 Left Lobe ...");
    expect(classification.needsOcr).toBe(true);
    expect(classification.qualityFlags).toContain("LOW_COMPLETENESS");
    expect(classification.qualityFlags).toContain("CONTAMINATION_RISK");
  });

  it("supports source override controls", () => {
    const base = {
      classification: { needsOcr: true, reason: "unsafe native page" },
    };

    expect(resolvePageSource(base).source).toBe("ocr");
    expect(resolvePageSource({ ...base, userOverride: "force_native" }).source).toBe("native");
    expect(resolvePageSource({ ...base, userOverride: "force_ocr" }).source).toBe("ocr");
    expect(resolvePageSource(base, { forceOcrAll: true }).source).toBe("ocr");
  });

  it("marks low-completeness pages as unsafe for native-only mode", () => {
    const stats = {
      charCount: 55,
      itemCount: 75,
      nonPrintableRatio: 0.01,
      singleCharItemRatio: 0.2,
      imageOpCount: 6,
      overlapRatio: 0.18,
      contaminationScore: 0.22,
      completenessConfidence: 0.61,
    };

    const evalResult = isUnsafeNativePage(stats, "Partial text");
    expect(evalResult.unsafe).toBe(true);
    expect(evalResult.completenessConfidence).toBeLessThan(0.72);
  });
});
