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
    expect(classification.needsOcrBackfill).toBe(false);
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
    expect(classification.needsOcrBackfill).toBe(false);
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

  it("short-circuits OCR when native text density is high", () => {
    const stats = {
      charCount: 2400,
      pageArea: 480000,
      nativeTextDensity: 0.005,
      singleCharItemRatio: 0.04,
      nonPrintableRatio: 0,
      imageOpCount: 5,
      overlapRatio: 0.14,
      contaminationScore: 0.29,
      completenessConfidence: 0.91,
    };

    const classification = classifyPage(stats, "Detailed digitally generated bronchoscopy procedure narrative text.");
    expect(classification.needsOcr).toBe(false);
    expect(classification.qualityFlags).toContain("NATIVE_DENSE_TEXT");

    const unsafeEval = isUnsafeNativePage(stats, "Detailed digitally generated bronchoscopy procedure narrative text.");
    expect(unsafeEval.unsafe).toBe(false);
  });

  it("flags dense native pages for OCR when fragmented line signatures are present", () => {
    const denseNarrative = [
      ...Array.from(
        { length: 24 },
        (_, i) => `Instruction line ${i + 1} includes complete postoperative guidance and medication details.`,
      ),
      "surgeon every 4 hours.",
      ...Array.from(
        { length: 12 },
        (_, i) => `Follow-up line ${i + 1} confirms normal recovery expectations and return precautions.`,
      ),
      "nose.",
      "If bleeding worsens, contact ENT immediately.",
    ].join("\n");

    const stats = {
      charCount: denseNarrative.length,
      pageArea: 520000,
      nativeTextDensity: denseNarrative.length / 520000,
      singleCharItemRatio: 0.04,
      nonPrintableRatio: 0,
      imageOpCount: 0,
      overlapRatio: 0,
      contaminationScore: 0.04,
      completenessConfidence: 0.94,
    };

    const classification = classifyPage(stats, denseNarrative);
    expect(classification.needsOcr).toBe(true);
    expect(classification.needsOcrBackfill).toBe(true);
    expect(classification.qualityFlags).toContain("FRAGMENTED_NATIVE_LINES");
    expect(classification.qualityFlags).toContain("BACKFILL_ORPHAN_SIGNATURE");

    const unsafeEval = isUnsafeNativePage(stats, denseNarrative);
    expect(unsafeEval.unsafe).toBe(true);
    expect(unsafeEval.classification.qualityFlags).toContain("FRAGMENTED_NATIVE_LINES");
  });

  it("does not trigger OCR backfill on clean medium-density native pages", () => {
    const text = Array.from(
      { length: 20 },
      (_, i) => `Postoperative instruction ${i + 1} remains complete with punctuation and coherent narrative detail.`,
    ).join("\n");
    const stats = {
      charCount: text.length,
      pageArea: 520000,
      nativeTextDensity: text.length / 520000,
      singleCharItemRatio: 0.03,
      nonPrintableRatio: 0,
      imageOpCount: 1,
      overlapRatio: 0.03,
      contaminationScore: 0.05,
      completenessConfidence: 0.94,
    };

    const classification = classifyPage(stats, text);
    expect(classification.needsOcrBackfill).toBe(false);
    expect(classification.qualityFlags).not.toContain("BACKFILL_SHORT_LINE_RATIO");
    expect(classification.qualityFlags).not.toContain("BACKFILL_ROW_FRAGMENTATION");
  });

  it("requires strong or broad backfill signal consensus before triggering", () => {
    const text = Array.from(
      { length: 18 },
      (_, i) => `Line ${i + 1} short text block without punctuation`,
    ).join("\n");
    const stats = {
      charCount: text.length,
      pageArea: 520000,
      nativeTextDensity: 0.0014,
      singleCharItemRatio: 0.03,
      nonPrintableRatio: 0,
      imageOpCount: 1,
      overlapRatio: 0.02,
      contaminationScore: 0.06,
      completenessConfidence: 0.93,
    };

    const classification = classifyPage(stats, text);
    expect(classification.backfill.votes).toBeGreaterThanOrEqual(0);
    expect(classification.backfill.strongVotes).toBeLessThan(2);
    expect(classification.backfill.severityScore).toBeLessThan(3.15);
    expect(classification.needsOcrBackfill).toBe(false);
  });
});
