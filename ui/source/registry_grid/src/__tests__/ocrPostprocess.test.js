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

  it("drops fuzzy page footer and symbol-only artifact lines", () => {
    const filtered = filterOcrLinesDetailed([
      { text: "te. ee ee ora | Page 10f3", confidence: 64, bbox: { x: 20, y: 20, width: 210, height: 14 } },
      { text: "| ~ _", confidence: 41, bbox: { x: 20, y: 38, width: 50, height: 12 } },
      { text: "Biopsies were performed in the upper pleura.", confidence: 83, bbox: { x: 20, y: 56, width: 330, height: 16 } },
    ], []);

    expect(filtered.lines.map((line) => line.text)).toEqual(["Biopsies were performed in the upper pleura."]);
    expect(filtered.dropped.some((entry) => entry.reason === "artifact")).toBe(true);
  });

  it("drops long repeated-character gibberish lines", () => {
    const filtered = filterOcrLinesDetailed([
      { text: "RGR UUEHHHHHAHIIIHL HHH EEE WHT HW WWIWt", confidence: 61, bbox: { x: 20, y: 22, width: 300, height: 14 } },
      { text: "Local Anesthesia: entry sites were infiltrated with 30 mL.", confidence: 82, bbox: { x: 20, y: 40, width: 360, height: 16 } },
    ], []);

    expect(filtered.lines).toHaveLength(1);
    expect(filtered.lines[0].text).toContain("Local Anesthesia");
    expect(filtered.dropped.some((entry) => entry.reason === "artifact")).toBe(true);
  });

  it("drops top-band uppercase garbage while keeping real header lines", () => {
    const filtered = filterOcrLinesDetailed([
      { text: "PIAPEPATIPTEPE ERE ELBE ESE FE REE RE", confidence: 78, bbox: { x: 24, y: 18, width: 380, height: 14 } },
      { text: "THE UNIVERSITY OF TEXAS", confidence: 92, bbox: { x: 24, y: 34, width: 260, height: 18 } },
      { text: "Patient Name: Power, Richard", confidence: 88, bbox: { x: 24, y: 58, width: 280, height: 18 } },
    ], []);

    expect(filtered.lines.map((line) => line.text)).toEqual([
      "THE UNIVERSITY OF TEXAS",
      "Patient Name: Power, Richard",
    ]);
    expect(filtered.dropped.some((entry) => entry.reason === "header_artifact" || entry.reason === "artifact")).toBe(true);
  });

  it("drops top-edge punctuation/short-token noise while keeping valid header text", () => {
    const filtered = filterOcrLinesDetailed([
      { text: ": : 14 ii i A \\", confidence: 68, bbox: { x: 24, y: 8, width: 160, height: 14 } },
      { text: "THE UNIVERSITY OF TEXAS", confidence: 92, bbox: { x: 24, y: 28, width: 260, height: 18 } },
      { text: "Patient Name: Power, Richard", confidence: 88, bbox: { x: 24, y: 52, width: 280, height: 18 } },
    ], []);

    expect(filtered.lines.map((line) => line.text)).toEqual([
      "THE UNIVERSITY OF TEXAS",
      "Patient Name: Power, Richard",
    ]);
    expect(filtered.dropped.some((entry) => entry.reason === "header_artifact")).toBe(true);
  });

  it("drops bottom-edge mush lines while keeping nearby clinical lines", () => {
    const filtered = filterOcrLinesDetailed([
      {
        text: "Biopsies of adhesions were performed in the upper pleura using forceps.",
        confidence: 81,
        bbox: { x: 24, y: 820, width: 520, height: 18 },
      },
      {
        text: "i eee a een nnnmennmnner ies a",
        confidence: 67,
        bbox: { x: 24, y: 900, width: 240, height: 14 },
      },
    ], []);

    expect(filtered.lines.map((line) => line.text)).toEqual([
      "Biopsies of adhesions were performed in the upper pleura using forceps.",
    ]);
    expect(filtered.dropped.some((entry) => entry.reason === "footer_artifact")).toBe(true);
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

  it("drops numeric-prefix anatomy caption lines", () => {
    const filtered = filterOcrLinesDetailed([
      { text: "1 Right Lower Lobe Entrance", confidence: 71, bbox: { x: 24, y: 24, width: 220, height: 16 } },
      { text: "2 Left Mainstem", confidence: 69, bbox: { x: 24, y: 44, width: 160, height: 16 } },
      { text: "Findings: No endobronchial lesion.", confidence: 84, bbox: { x: 24, y: 64, width: 320, height: 16 } },
    ], []);

    expect(filtered.lines.map((line) => line.text)).toEqual(["Findings: No endobronchial lesion."]);
    expect(filtered.dropped.filter((entry) => entry.reason === "caption")).toHaveLength(2);
  });
});
