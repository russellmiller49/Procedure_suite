import { describe, expect, it } from "vitest";

import {
  assembleTextFromBlocks,
  buildLayoutBlocks,
  computeOverlapRatio,
  estimateCompletenessConfidence,
  markContaminatedItems,
  scoreContamination,
} from "../../../../static/phi_redactor/pdf_local/pdf/layoutAnalysis.js";

describe("layoutAnalysis", () => {
  it("builds separate layout blocks for column-like text", () => {
    const items = [
      { itemIndex: 0, str: "Procedure", x: 40, y: 700, width: 60, height: 10 },
      { itemIndex: 1, str: "Report", x: 106, y: 700, width: 40, height: 10 },
      { itemIndex: 2, str: "Findings", x: 40, y: 684, width: 55, height: 10 },
      { itemIndex: 3, str: "Left", x: 360, y: 700, width: 30, height: 10 },
      { itemIndex: 4, str: "Mainstem", x: 394, y: 700, width: 58, height: 10 },
      { itemIndex: 5, str: "Biopsy", x: 360, y: 684, width: 45, height: 10 },
    ];

    const blocks = buildLayoutBlocks(items);
    expect(blocks.length).toBeGreaterThanOrEqual(2);
  });

  it("computes overlap ratio between text and image regions", () => {
    const textRegions = [{ x: 10, y: 10, width: 100, height: 20 }];
    const imageRegions = [{ x: 40, y: 0, width: 40, height: 80 }];
    const ratio = computeOverlapRatio(textRegions, imageRegions, { margin: 0 });

    expect(ratio).toBeCloseTo(0.4, 2);
  });

  it("drops short contaminated label tokens during adaptive assembly", () => {
    const items = [
      { itemIndex: 0, str: "4", x: 300, y: 700, width: 8, height: 10 },
      { itemIndex: 1, str: "Left", x: 320, y: 700, width: 24, height: 10 },
      { itemIndex: 2, str: "Upper", x: 348, y: 700, width: 32, height: 10 },
      { itemIndex: 3, str: "Lobe", x: 384, y: 700, width: 28, height: 10 },
    ];

    const blocks = buildLayoutBlocks(items);
    const contamination = markContaminatedItems(items, [{ x: 294, y: 688, width: 18, height: 18 }], {
      margin: 0,
      minOverlapRatio: 0.05,
    });
    const assembled = assembleTextFromBlocks(blocks, contamination);

    expect(assembled.text).toContain("Left Upper Lobe");
    expect(assembled.text).not.toMatch(/\b4\b/);
  });

  it("scores contamination and lowers completeness confidence on unsafe pages", () => {
    const contaminationScore = scoreContamination({
      overlapRatio: 0.3,
      contaminatedRatio: 0.25,
      shortContaminatedRatio: 0.12,
      excludedTokenRatio: 0.2,
    });
    expect(contaminationScore).toBeGreaterThan(0.25);

    const confidence = estimateCompletenessConfidence({
      charCount: 35,
      singleCharItemRatio: 0.6,
      nonPrintableRatio: 0.12,
      imageOpCount: 9,
      layoutBlockCount: 1,
      overlapRatio: 0.25,
      contaminationScore,
      excludedTokenRatio: 0.2,
    });
    expect(confidence).toBeLessThan(0.72);
  });
});
