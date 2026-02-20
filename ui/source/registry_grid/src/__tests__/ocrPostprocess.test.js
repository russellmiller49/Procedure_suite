import { describe, expect, it } from "vitest";

import {
  composeOcrPageText,
  dedupeConsecutiveLines,
  filterOcrLinesDetailed,
} from "../../../../static/phi_redactor/pdf_local/pdf/ocrPostprocess.js";

describe("ocrPostprocess", () => {
  it("drops lines overlapping detected figure regions", () => {
    const lines = [
      {
        text: "Extrinsic compression extends for 3cm.",
        confidence: 88,
        bbox: { x: 40, y: 220, width: 360, height: 24 },
      },
      {
        text: "Right Lower Lobe Entrance",
        confidence: 61,
        bbox: { x: 760, y: 220, width: 180, height: 24 },
      },
    ];

    const filtered = filterOcrLinesDetailed(lines, [
      { x: 720, y: 180, width: 260, height: 400 },
    ]);

    expect(filtered.lines.map((line) => line.text)).toEqual([
      "Extrinsic compression extends for 3cm.",
    ]);
    expect(
      filtered.dropped.some((entry) => entry.reason === "figure_overlap" || entry.reason === "caption"),
    ).toBe(true);
  });

  it("drops short low-confidence OCR artifacts", () => {
    const filtered = filterOcrLinesDetailed([
      { text: "O0", confidence: 12, bbox: { x: 20, y: 20, width: 12, height: 12 } },
      { text: "Date of Birth: 09/15/1950", confidence: 82, bbox: { x: 20, y: 40, width: 200, height: 18 } },
    ], []);

    expect(filtered.lines).toHaveLength(1);
    expect(filtered.lines[0].text).toContain("Date of Birth");
    expect(filtered.dropped.some((entry) => entry.reason === "low_conf_short")).toBe(true);
  });

  it("strips Provation boilerplate and consecutive repeats", () => {
    const deduped = dedupeConsecutiveLines([
      { text: "Powered by Provation MD", confidence: 90, bbox: { x: 0, y: 0, width: 100, height: 10 } },
      { text: "Procedure:", confidence: 85, bbox: { x: 0, y: 20, width: 70, height: 10 } },
      { text: "Procedure:", confidence: 84, bbox: { x: 0, y: 35, width: 70, height: 10 } },
      { text: "Bronchoscopy", confidence: 84, bbox: { x: 0, y: 50, width: 90, height: 10 } },
    ]);

    const filtered = filterOcrLinesDetailed(deduped, []);
    expect(filtered.lines.map((line) => line.text)).toEqual([
      "Procedure:",
      "Bronchoscopy",
    ]);

    expect(composeOcrPageText(filtered.lines)).toBe("Procedure:\nBronchoscopy");
  });

  it("can disable figure-overlap suppression for scanned-like pages", () => {
    const lines = [
      {
        text: "Procedure Date: 01/02/2011",
        confidence: 81,
        bbox: { x: 28, y: 70, width: 220, height: 18 },
      },
    ];
    const hugeRegion = [{ x: 0, y: 0, width: 1400, height: 1900 }];

    const strict = filterOcrLinesDetailed(lines, hugeRegion, { overlapThreshold: 0.35 });
    expect(strict.lines).toHaveLength(0);

    const relaxed = filterOcrLinesDetailed(lines, hugeRegion, {
      overlapThreshold: 0.35,
      disableFigureOverlap: true,
    });
    expect(relaxed.lines).toHaveLength(1);
    expect(relaxed.lines[0].text).toContain("Procedure Date");
  });

  it("keeps short anatomy lines when they include clinical verbs", () => {
    const filtered = filterOcrLinesDetailed([
      { text: "Left Mainstem", confidence: 74, bbox: { x: 24, y: 24, width: 120, height: 14 } },
      { text: "Trachea was inspected", confidence: 78, bbox: { x: 24, y: 44, width: 180, height: 16 } },
    ], []);

    expect(filtered.lines.map((line) => line.text)).toEqual(["Trachea was inspected"]);
  });
});
