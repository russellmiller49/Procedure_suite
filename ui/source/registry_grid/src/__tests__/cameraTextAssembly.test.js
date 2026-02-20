import { describe, expect, it } from "vitest";

import { buildCameraOcrDocumentText } from "../../../../static/phi_redactor/camera_local/imagePipeline.js";

describe("camera OCR text assembly", () => {
  it("builds page-separated camera OCR text in page order", () => {
    const text = buildCameraOcrDocumentText([
      { pageIndex: 1, text: "Second page text" },
      { pageIndex: 0, text: "First page text" },
    ]);

    expect(text).toContain("===== PAGE 1 (CAMERA_OCR) =====");
    expect(text).toContain("===== PAGE 2 (CAMERA_OCR) =====");
    expect(text.indexOf("First page text")).toBeLessThan(text.indexOf("Second page text"));
  });

  it("returns empty string when no pages exist", () => {
    expect(buildCameraOcrDocumentText([])).toBe("");
  });
});
