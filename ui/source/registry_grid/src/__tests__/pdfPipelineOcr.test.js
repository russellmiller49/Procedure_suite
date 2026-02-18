import { describe, expect, it } from "vitest";

import {
  applyOcrResultsToRawPages,
  selectPagesForOcr,
} from "../../../../static/phi_redactor/pdf_local/pdf/pipeline.js";

describe("pdf pipeline OCR helpers", () => {
  it("selects OCR targets from source decisions and classifier needs", () => {
    const doc = {
      pages: [
        { pageIndex: 0, sourceDecision: "native", classification: { needsOcr: false } },
        { pageIndex: 1, sourceDecision: "ocr", classification: { needsOcr: true } },
        { pageIndex: 2, sourceDecision: "native", classification: { needsOcr: true } },
      ],
    };

    expect(selectPagesForOcr(doc)).toEqual([1, 2]);
    expect(selectPagesForOcr(doc, { forceOcrAll: true })).toEqual([0, 1, 2]);
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
});
