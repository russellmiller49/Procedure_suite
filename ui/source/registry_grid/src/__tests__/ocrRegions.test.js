import { describe, expect, it } from "vitest";

import { computeOcrCropRect } from "../../../../static/phi_redactor/pdf_local/pdf/ocrRegions.js";

describe("ocr region cropping", () => {
  it("crops OCR to the left-column when image strip exists on the right", () => {
    const result = computeOcrCropRect(
      {
        canvasWidth: 1000,
        canvasHeight: 1400,
        nativeCharCount: 1200,
        textRegions: [
          { x: 40, y: 120, width: 420, height: 20 },
          { x: 42, y: 180, width: 430, height: 20 },
          { x: 45, y: 240, width: 410, height: 20 },
          { x: 46, y: 300, width: 425, height: 20 },
          // Right-column caption-like text should not expand the final crop.
          { x: 760, y: 220, width: 180, height: 18 },
        ],
        imageRegions: [
          { x: 710, y: 140, width: 250, height: 420 },
          { x: 705, y: 620, width: 260, height: 430 },
        ],
      },
      { mode: "auto", paddingPx: 12 },
    );

    expect(result.meta.applied).toBe(true);
    expect(result.rect).toBeTruthy();
    expect(result.rect.width).toBeLessThan(760);
    expect(result.rect.width).toBeGreaterThan(360);
    expect(result.meta.box?.[2]).toBe(result.rect.x + result.rect.width);
  });

  it("does not crop when explicitly disabled", () => {
    const result = computeOcrCropRect(
      {
        canvasWidth: 900,
        canvasHeight: 1200,
        textRegions: [{ x: 30, y: 120, width: 380, height: 20 }],
        imageRegions: [{ x: 620, y: 100, width: 220, height: 500 }],
      },
      { mode: "off" },
    );

    expect(result.meta.applied).toBe(false);
    expect(result.meta.reason).toBe("disabled");
    expect(result.rect).toBeNull();
  });

  it("keeps full-page OCR in auto mode when text-signal is low", () => {
    const result = computeOcrCropRect(
      {
        canvasWidth: 1000,
        canvasHeight: 1400,
        nativeCharCount: 120,
        textRegions: [{ x: 48, y: 110, width: 200, height: 16 }],
        imageRegions: [{ x: 680, y: 160, width: 250, height: 430 }],
      },
      { mode: "auto", minTextRegionCount: 4 },
    );

    expect(result.meta.applied).toBe(false);
    expect(result.meta.reason).toBe("low_text_signal");
  });
});
