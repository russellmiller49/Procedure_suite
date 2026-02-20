import { describe, expect, it } from "vitest";

import {
  computeHeaderZoneColumns,
  computeOcrCropRect,
  computeProvationDiagramSkipRegions,
  getLineBandRegions,
} from "../../../../static/phi_redactor/pdf_local/pdf/ocrRegions.js";

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
          { x: 700, y: 220, width: 140, height: 18 },
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

  it("keeps full-page OCR when right-margin text reaches page edge", () => {
    const result = computeOcrCropRect(
      {
        canvasWidth: 1000,
        canvasHeight: 1400,
        nativeCharCount: 1400,
        textRegions: [
          { x: 40, y: 120, width: 900, height: 20 },
          { x: 42, y: 180, width: 920, height: 20 },
          { x: 46, y: 240, width: 910, height: 20 },
          { x: 45, y: 300, width: 920, height: 20 },
        ],
        imageRegions: [{ x: 220, y: 760, width: 170, height: 220 }],
      },
      { mode: "auto", paddingPx: 12 },
    );

    expect(result.meta.applied).toBe(false);
    expect(result.meta.reason).toBe("right_margin_text");
  });

  it("splits top header zone into distinct left/right bounding boxes for two-column layouts", () => {
    const mockCanvas = { width: 1200, height: 1600 };
    const header = computeHeaderZoneColumns({
      canvas: mockCanvas,
      textRegions: [
        { x: 40, y: 40, width: 320, height: 22 },
        { x: 44, y: 94, width: 338, height: 22 },
        { x: 700, y: 44, width: 360, height: 22 },
        { x: 708, y: 92, width: 352, height: 22 },
      ],
    });

    expect(header.headerZoneRect.height).toBe(400);
    expect(header.columns).toHaveLength(2);
    expect(header.columns[0].rect.x).toBe(0);
    expect(header.columns[0].rect.x + header.columns[0].rect.width).toBeLessThanOrEqual(header.columns[1].rect.x);
    expect(header.columns[1].rect.x + header.columns[1].rect.width).toBe(1200);
  });

  it("detects provation right-side diagram region for OCR skip", () => {
    const skip = computeProvationDiagramSkipRegions({
      canvasWidth: 1000,
      canvasHeight: 1400,
      nativeCharCount: 520,
      pageIndex: 0,
      figureRegions: [
        { x: 640, y: 280, width: 300, height: 560 },
        { x: 660, y: 220, width: 240, height: 130 },
      ],
      textRegions: [
        { x: 40, y: 60, width: 420, height: 220 },
      ],
    });

    expect(skip.meta.applied).toBe(true);
    expect(skip.meta.reason).toBe("provation_tree_diagram");
    expect(skip.regions.length).toBeGreaterThan(0);
  });

  it("builds backfill OCR line bands for truncated native row fragments", () => {
    const bands = getLineBandRegions({
      canvasWidth: 1000,
      canvasHeight: 1400,
      layoutBlocks: [
        {
          id: "block-1",
          lines: [
            {
              text: "When the tonsil or adenoid scabs fall off, your child may have bleeding from the mouth or",
              bbox: { x: 40, y: 620, width: 720, height: 16 },
            },
            {
              text: "nose.",
              bbox: { x: 44, y: 598, width: 44, height: 16 },
            },
            {
              text: "Follow-up with ENT in 2 weeks.",
              bbox: { x: 40, y: 540, width: 220, height: 16 },
            },
          ],
        },
      ],
    });

    expect(bands.meta.applied).toBe(true);
    expect(bands.meta.regionCount).toBeGreaterThan(0);
    expect(bands.regions[0].x).toBeLessThanOrEqual(20);
    expect(Math.round(bands.regions[0].width)).toBeGreaterThanOrEqual(720);
    expect(Math.round(bands.regions[0].x + bands.regions[0].width)).toBeLessThanOrEqual(1000);
  });
});
