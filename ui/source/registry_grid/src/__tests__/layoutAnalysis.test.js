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

  it("reconstructs simple label/value tables by zipping adjacent rows", () => {
    const items = [
      // Labels row (y=700)
      { itemIndex: 0, str: "Patient", x: 40, y: 700, width: 48, height: 10 },
      { itemIndex: 1, str: "Name:", x: 102, y: 700, width: 44, height: 10 },
      { itemIndex: 2, str: "Date", x: 220, y: 700, width: 30, height: 10 },
      { itemIndex: 3, str: "of", x: 254, y: 700, width: 14, height: 10 },
      { itemIndex: 4, str: "Birth:", x: 272, y: 700, width: 44, height: 10 },
      { itemIndex: 5, str: "Record", x: 400, y: 700, width: 44, height: 10 },
      { itemIndex: 6, str: "Number:", x: 456, y: 700, width: 66, height: 10 },
      // Values row (y=680)
      { itemIndex: 7, str: "Robert", x: 40, y: 680, width: 42, height: 10 },
      { itemIndex: 8, str: "Smith", x: 86, y: 680, width: 38, height: 10 },
      { itemIndex: 9, str: "09/15/1950", x: 220, y: 680, width: 82, height: 10 },
      { itemIndex: 10, str: "0159834", x: 400, y: 680, width: 56, height: 10 },
    ];

    const blocks = buildLayoutBlocks(items);
    const assembled = assembleTextFromBlocks(blocks, { contaminatedByItemIndex: new Set() });

    expect(assembled.text).toContain("Patient Name: Robert Smith");
    expect(assembled.text).toContain("Date of Birth: 09/15/1950");
    expect(assembled.text).toContain("Record Number: 0159834");
  });

  it("preserves overflow value segments when zipping label/value rows", () => {
    const items = [
      // Labels row
      { itemIndex: 0, str: "Discharge", x: 40, y: 700, width: 62, height: 10 },
      { itemIndex: 1, str: "Instructions:", x: 108, y: 700, width: 92, height: 10 },
      { itemIndex: 2, str: "Nose", x: 320, y: 700, width: 30, height: 10 },
      { itemIndex: 3, str: "Care:", x: 354, y: 700, width: 38, height: 10 },
      // Values row
      { itemIndex: 4, str: "Follow", x: 40, y: 684, width: 36, height: 10 },
      { itemIndex: 5, str: "up", x: 80, y: 684, width: 14, height: 10 },
      { itemIndex: 6, str: "with", x: 98, y: 684, width: 26, height: 10 },
      { itemIndex: 7, str: "surgeon", x: 128, y: 684, width: 48, height: 10 },
      { itemIndex: 8, str: "every", x: 180, y: 684, width: 34, height: 10 },
      { itemIndex: 9, str: "4", x: 218, y: 684, width: 8, height: 10 },
      { itemIndex: 10, str: "hours.", x: 230, y: 684, width: 40, height: 10 },
      { itemIndex: 11, str: "Use", x: 320, y: 684, width: 24, height: 10 },
      { itemIndex: 12, str: "saline", x: 348, y: 684, width: 34, height: 10 },
      { itemIndex: 13, str: "spray", x: 386, y: 684, width: 30, height: 10 },
      { itemIndex: 14, str: "for", x: 420, y: 684, width: 18, height: 10 },
      { itemIndex: 15, str: "nose.", x: 442, y: 684, width: 30, height: 10 },
      // Extra unpaired value segment that previously could be dropped.
      { itemIndex: 16, str: "Call", x: 540, y: 684, width: 24, height: 10 },
      { itemIndex: 17, str: "if", x: 568, y: 684, width: 10, height: 10 },
      { itemIndex: 18, str: "bleeding", x: 582, y: 684, width: 46, height: 10 },
      { itemIndex: 19, str: "worsens.", x: 632, y: 684, width: 50, height: 10 },
    ];

    const blocks = buildLayoutBlocks(items);
    const assembled = assembleTextFromBlocks(blocks, { contaminatedByItemIndex: new Set() });

    expect(assembled.text).toMatch(/Discharge Instructions: Follow up with surgeon every\s?4 hours\./);
    expect(assembled.text).toContain("Nose Care: Use saline spray for nose.");
    expect(assembled.text).toContain("Call if bleeding worsens.");
  });

  it("keeps same-line tokens together despite moderate Y jitter", () => {
    const items = [
      { itemIndex: 0, str: "Use", x: 40, y: 700, width: 24, height: 10 },
      { itemIndex: 1, str: "saline", x: 68, y: 705, width: 34, height: 10 },
      { itemIndex: 2, str: "spray", x: 106, y: 701, width: 30, height: 10 },
      { itemIndex: 3, str: "every", x: 140, y: 704, width: 34, height: 10 },
      { itemIndex: 4, str: "4", x: 178, y: 702, width: 8, height: 10 },
      { itemIndex: 5, str: "hours.", x: 190, y: 706, width: 40, height: 10 },
      { itemIndex: 6, str: "for", x: 40, y: 684, width: 18, height: 10 },
      { itemIndex: 7, str: "nose.", x: 62, y: 684, width: 30, height: 10 },
    ];

    const blocks = buildLayoutBlocks(items);
    const assembled = assembleTextFromBlocks(blocks, { contaminatedByItemIndex: new Set() });

    expect(assembled.text).toMatch(/Use saline spray every\s?4 hours\./);
    expect(assembled.text).toContain("for nose.");
  });
});
