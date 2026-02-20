import { describe, expect, it } from "vitest";

import {
  applyClinicalOcrHeuristics,
  composeOcrPageText,
  filterOcrLinesDetailed,
} from "../../../../static/phi_redactor/pdf_local/pdf/ocrPostprocess.js";

function countLowConfidenceLines(lines, threshold = 20) {
  return (Array.isArray(lines) ? lines : []).filter((line) => Number(line?.confidence) < threshold).length;
}

describe("provation OCR hardening fixtures", () => {
  it("suppresses figure garbage and preserves header clinical fields", () => {
    const inputLines = [
      { text: "Provation", confidence: 88, bbox: { x: 24, y: 18, width: 100, height: 20 } },
      { text: "Procedure:", confidence: 91, bbox: { x: 26, y: 46, width: 120, height: 18 } },
      { text: "Date of Birth: 09/15/1950", confidence: 86, bbox: { x: 28, y: 70, width: 220, height: 18 } },
      { text: "Age: 73", confidence: 82, bbox: { x: 270, y: 70, width: 80, height: 18 } },
      { text: "O77 O00", confidence: 12, bbox: { x: 760, y: 240, width: 96, height: 20 } },
      { text: "0D 0) Ge) C009) C0)", confidence: 8, bbox: { x: 750, y: 280, width: 180, height: 24 } },
      { text: "Extrinsic compression noted in the left mainstem.", confidence: 79, bbox: { x: 32, y: 180, width: 460, height: 20 } },
    ];

    const figureRegions = [
      { x: 700, y: 160, width: 260, height: 420 },
    ];

    const lowConfBefore = countLowConfidenceLines(inputLines);
    const filtered = filterOcrLinesDetailed(inputLines, figureRegions, {
      overlapThreshold: 0.35,
      shortLowConfThreshold: 30,
    });

    const lowConfAfter = countLowConfidenceLines(filtered.lines);
    const text = composeOcrPageText(filtered.lines);

    expect(text).toContain("Provation");
    expect(text).toContain("Procedure:");
    expect(text).toMatch(/\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/);
    expect(text).not.toContain("O77 O00");
    expect(text).toContain("Extrinsic compression noted in the left mainstem.");

    expect(lowConfAfter).toBeLessThanOrEqual(Math.floor(lowConfBefore * 0.5));
  });

  it("applies clinical OCR dosage and terminology corrections", () => {
    const corrected = applyClinicalOcrHeuristics(
      [
        "Lidocaine 49% sprayed to airway.",
        "Atropine 9.5 mg given once.",
        "Child may have bleeding from the mouth nose.",
        "Persistent lrynphadenopathy with hytnph node enlargement.",
        "tracheobronchlal narrowing noted.",
        "Proceduratist(s): Fellow listed for pleurescopy.",
        "Fodings mention the insion while discussing allematives wih patient.",
      ].join(" "),
    );

    expect(corrected).toContain("Lidocaine 4%");
    expect(corrected).toContain("Atropine 0.5 mg");
    expect(corrected).toContain("mouth or nose");
    expect(corrected).toContain("lymphadenopathy");
    expect(corrected).toContain("lymph node enlargement");
    expect(corrected).toContain("tracheobronchial narrowing");
    expect(corrected).toContain("Proceduralist(s): Fellow listed for pleuroscopy.");
    expect(corrected).toContain("Findings mention the incision while discussing alternatives with patient.");
  });

  it("does not over-correct non-target Atropine doses", () => {
    const corrected = applyClinicalOcrHeuristics("Atropine 19.5 mg was charted by anesthesia.");
    expect(corrected).toContain("Atropine 19.5 mg");
    expect(corrected).not.toContain("Atropine 0.5 mg");
  });

  it("drops garbled account and birch header lines while keeping valid DOB text", () => {
    const filtered = filterOcrLinesDetailed([
      {
        text: "Aeecrnimt #2: IIENOI IW",
        confidence: 45,
        bbox: { x: 28, y: 32, width: 320, height: 20 },
        zoneId: "header_left",
        zoneOrder: 0,
      },
      {
        text: "Date nf Birch: 19/9G/4GA1",
        confidence: 41,
        bbox: { x: 620, y: 32, width: 340, height: 20 },
        zoneId: "header_right",
        zoneOrder: 1,
      },
      {
        text: "Date of Birth: 09/15/1950",
        confidence: 86,
        bbox: { x: 26, y: 60, width: 250, height: 18 },
        zoneId: "header_left",
        zoneOrder: 0,
      },
    ], []);

    const text = composeOcrPageText(filtered.lines);
    expect(text).toContain("Date of Birth: 09/15/1950");
    expect(text).not.toContain("Aeecrnimt");
    expect(text).not.toContain("Date nf Birch");
  });
});
