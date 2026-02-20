import { describe, expect, it } from "vitest";

import {
  applyOcrResultsToRawPages,
  buildPdfDocumentModel,
  selectPagesForOcr,
} from "../../../../static/phi_redactor/pdf_local/pdf/pipeline.js";

describe("pdf pipeline OCR helpers", () => {
  it("selects OCR targets from source decisions and classifier needs", () => {
    const doc = {
      pages: [
        { pageIndex: 0, sourceDecision: "native", classification: { needsOcr: false, needsOcrBackfill: false } },
        { pageIndex: 1, sourceDecision: "ocr", classification: { needsOcr: true, needsOcrBackfill: false } },
        { pageIndex: 2, sourceDecision: "native", classification: { needsOcr: true, needsOcrBackfill: true } },
        { pageIndex: 3, sourceDecision: "native", classification: { needsOcr: true, needsOcrBackfill: false } },
      ],
    };

    expect(selectPagesForOcr(doc)).toEqual([1, 2]);
    expect(selectPagesForOcr(doc, { forceOcrAll: true })).toEqual([0, 1, 2, 3]);
  });

  it("applies OCR text to matching raw pages only", () => {
    const rawPages = [
      { pageIndex: 0, text: "native a", stats: {} },
      { pageIndex: 1, text: "native b", stats: {} },
    ];

    const merged = applyOcrResultsToRawPages(rawPages, [
      { pageIndex: 1, text: "ocr b", meta: { confidence: 91.5 } },
      { pageIndex: 3, text: "orphan", meta: { confidence: 20 } },
    ]);

    expect(merged).toHaveLength(2);
    expect(merged[0].ocrText).toBeUndefined();
    expect(merged[1].ocrText).toBe("ocr b");
    expect(merged[1].ocrMeta?.confidence).toBe(91.5);
  });

  it("computes post-filter quality summary metrics after OCR merge", () => {
    const file = /** @type {File} */ ({ name: "provation_examples.pdf" });
    const rawPages = [
      {
        pageIndex: 0,
        text: "Procedure:",
        rawText: "Procedure:",
        stats: {
          charCount: 12,
          itemCount: 24,
          nonPrintableRatio: 0,
          singleCharItemRatio: 0.2,
          imageOpCount: 10,
          overlapRatio: 0.3,
          contaminationScore: 0.31,
          completenessConfidence: 0.22,
        },
        ocrText: [
          "Procedure:",
          "Date of Birth: 9/15/1950",
          "Flexible bronchoscopy with findings documented in detail including extrinsic compression and airway narrowing with clear narrative continuity for quality checks.",
        ].join("\n"),
        ocrMeta: {
          metrics: {
            postFilter: {
              charCount: 128,
              alphaRatio: 0.82,
              meanLineConf: 86,
              lowConfLineFrac: 0.05,
              numLines: 3,
              medianTokenLen: 5,
              footerBoilerplateHits: 0,
            },
          },
          lines: [
            { text: "Procedure:", confidence: 84, bbox: { x: 20, y: 20, width: 80, height: 18 } },
            { text: "Date of Birth: 9/15/1950", confidence: 87, bbox: { x: 20, y: 44, width: 200, height: 18 } },
            { text: "Flexible bronchoscopy with findings documented.", confidence: 88, bbox: { x: 20, y: 68, width: 330, height: 18 } },
          ],
        },
      },
    ];

    const model = buildPdfDocumentModel(file, rawPages, {
      ocr: { available: true, enabled: true },
      gate: {
        minCompletenessConfidence: 0.72,
        maxContaminationScore: 0.24,
        hardBlockWhenUnsafeWithoutOcr: true,
      },
    });

    expect(model.qualitySummary.lowConfidencePages).toBe(0);
    expect(model.qualitySummary.pageMetrics?.length).toBe(1);
    expect(model.qualitySummary.pageMetrics?.[0]).toContain("chars=");
    expect(model.pages[0].qualityMetrics?.meanLineConf).toBe(86);
  });

  it("does not blank page text when OCR result is an empty string", () => {
    const file = /** @type {File} */ ({ name: "provation_examples.pdf" });
    const rawPages = [
      {
        pageIndex: 0,
        text: "Native fallback note text",
        rawText: "Native fallback note text",
        stats: {
          charCount: 180,
          itemCount: 60,
          nonPrintableRatio: 0,
          singleCharItemRatio: 0.1,
          imageOpCount: 6,
          overlapRatio: 0.2,
          contaminationScore: 0.3,
          completenessConfidence: 0.58,
        },
        ocrText: "",
      },
    ];

    const model = buildPdfDocumentModel(file, rawPages, {
      ocr: { available: true, enabled: true },
    });

    expect(model.pages[0].text).toContain("Native fallback note text");
    expect(model.pages[0].text.length).toBeGreaterThan(0);
  });

  it("marks dense but fragmented native pages for OCR backfill", () => {
    const file = /** @type {File} */ ({ name: "endosoft_notes.pdf" });
    const nativeText = [
      ...Array.from(
        { length: 22 },
        (_, i) => `Instruction line ${i + 1} is complete and clinically coherent for discharge planning.`,
      ),
      "surgeon every 4 hours.",
      ...Array.from(
        { length: 9 },
        (_, i) => `Recovery line ${i + 1} remains complete and clinically coherent for patient education.`,
      ),
      "nose.",
      "If bleeding worsens, contact ENT immediately.",
    ].join("\n");
    const rawPages = [
      {
        pageIndex: 0,
        text: nativeText,
        rawText: nativeText,
        stats: {
          charCount: nativeText.length,
          itemCount: 420,
          nonPrintableRatio: 0,
          singleCharItemRatio: 0.03,
          imageOpCount: 1,
          overlapRatio: 0.05,
          contaminationScore: 0.05,
          completenessConfidence: 0.93,
          pageArea: 540000,
          nativeTextDensity: nativeText.length / 540000,
        },
      },
    ];

    const model = buildPdfDocumentModel(file, rawPages, {
      ocr: { available: true, enabled: true },
    });

    expect(model.pages[0].classification.needsOcr).toBe(true);
    expect(model.pages[0].classification.needsOcrBackfill).toBe(true);
    expect(model.pages[0].classification.qualityFlags).toContain("FRAGMENTED_NATIVE_LINES");
    expect(selectPagesForOcr(model)).toEqual([0]);
  });

  it("does not target clean EndoSoft-like native pages for OCR", () => {
    const file = /** @type {File} */ ({ name: "endosoft_notes.pdf" });
    const nativeText = Array.from(
      { length: 20 },
      (_, i) => `Instruction line ${i + 1} remains complete and coherent for discharge guidance with full punctuation.`,
    ).join("\n");
    const rawPages = [
      {
        pageIndex: 0,
        text: nativeText,
        rawText: nativeText,
        stats: {
          charCount: nativeText.length,
          itemCount: 380,
          nonPrintableRatio: 0,
          singleCharItemRatio: 0.03,
          imageOpCount: 1,
          overlapRatio: 0.02,
          contaminationScore: 0.04,
          completenessConfidence: 0.95,
          pageArea: 540000,
          nativeTextDensity: nativeText.length / 540000,
        },
      },
    ];

    const model = buildPdfDocumentModel(file, rawPages, {
      ocr: { available: true, enabled: true },
    });

    expect(model.pages[0].classification.needsOcrBackfill).toBe(false);
    expect(selectPagesForOcr(model)).toEqual([]);
  });
});
