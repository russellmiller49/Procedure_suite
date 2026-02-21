import { describe, expect, it } from "vitest";

import { computeOcrTextMetrics } from "../../../../static/phi_redactor/pdf_local/pdf/ocrMetrics.js";

describe("ocrMetrics", () => {
  it("computes compact quality metrics from OCR lines", () => {
    const metrics = computeOcrTextMetrics({
      lines: [
        { text: "Procedure: Bronchoscopy", confidence: 82 },
        { text: "Date of Birth: 09/15/1950", confidence: 88 },
        { text: "O0", confidence: 9 },
      ],
    });

    expect(metrics.charCount).toBeGreaterThan(10);
    expect(metrics.alphaRatio).toBeGreaterThan(0.5);
    expect(metrics.meanLineConf).toBeGreaterThan(40);
    expect(metrics.lowConfLineFrac).toBeGreaterThan(0);
    expect(metrics.numLines).toBe(3);
    expect(metrics.medianTokenLen).toBeGreaterThan(2);
  });

  it("counts footer boilerplate hits", () => {
    const metrics = computeOcrTextMetrics({
      lines: [
        { text: "Powered by Provation MD", confidence: 92 },
        { text: "Page 1 of 2", confidence: 92 },
        { text: "Page 10f3", confidence: 67 },
        { text: "Clinical findings line.", confidence: 90 },
      ],
    });

    expect(metrics.footerBoilerplateHits).toBe(3);
  });
});
