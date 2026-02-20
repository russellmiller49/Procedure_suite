import { describe, expect, it } from "vitest";

import {
  buildCaptureWarnings,
  buildPreprocessPlan,
  computeScaledDimensions,
} from "../../../../static/phi_redactor/camera_local/imagePreprocess.js";

describe("camera image preprocess", () => {
  it("scales dimensions down to maxDim while preserving aspect ratio", () => {
    const dims = computeScaledDimensions(4000, 2000, 2000);
    expect(dims.width).toBe(2000);
    expect(dims.height).toBe(1000);
    expect(dims.scale).toBeCloseTo(0.5, 4);
  });

  it("builds mode-specific preprocess plans", () => {
    const offPlan = buildPreprocessPlan({ width: 1200, height: 800, mode: "off" });
    const grayPlan = buildPreprocessPlan({ width: 1200, height: 800, mode: "grayscale" });
    const bwPlan = buildPreprocessPlan({ width: 1200, height: 800, mode: "bw_high_contrast" });

    expect(offPlan.applyGrayscale).toBe(false);
    expect(offPlan.applyThreshold).toBe(false);
    expect(grayPlan.applyGrayscale).toBe(true);
    expect(grayPlan.applyThreshold).toBe(false);
    expect(bwPlan.applyGrayscale).toBe(true);
    expect(bwPlan.applyThreshold).toBe(true);
  });

  it("emits blur and glare warnings when quality metrics are weak", () => {
    const warnings = buildCaptureWarnings({
      blurVariance: 20,
      overexposureRatio: 0.8,
    }, {
      blurMinVariance: 90,
      maxOverexposureRatio: 0.55,
    });

    expect(warnings.length).toBe(2);
    expect(warnings[0]).toMatch(/blurry/i);
    expect(warnings[1]).toMatch(/overexposed|glare/i);
  });
});
