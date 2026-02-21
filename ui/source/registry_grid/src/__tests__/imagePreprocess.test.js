import { describe, expect, it } from "vitest";

import {
  applyPreprocessToImageData,
  buildCaptureWarnings,
  buildPreprocessPlan,
  computeGrayFromImageData,
  computeGrayStats,
  computeScaledDimensions,
  resolveCaptureWarningThresholds,
  resolveAutoPreprocessMode,
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
    const autoPlan = buildPreprocessPlan({ width: 1200, height: 800, mode: "auto" });
    const grayPlan = buildPreprocessPlan({ width: 1200, height: 800, mode: "grayscale" });
    const bwPlan = buildPreprocessPlan({ width: 1200, height: 800, mode: "bw_high_contrast" });
    const monitorPlan = buildPreprocessPlan({ width: 1200, height: 800, mode: "auto", sceneHint: "monitor" });

    expect(offPlan.applyGrayscale).toBe(false);
    expect(offPlan.applyThreshold).toBe(false);
    expect(offPlan.sceneHint).toBe("auto");
    expect(autoPlan.applyGrayscale).toBe(true);
    expect(autoPlan.applyThreshold).toBe(false);
    expect(autoPlan.autoTuning).toBe(true);
    expect(grayPlan.applyGrayscale).toBe(true);
    expect(grayPlan.applyThreshold).toBe(false);
    expect(bwPlan.applyGrayscale).toBe(true);
    expect(bwPlan.applyThreshold).toBe(true);
    expect(monitorPlan.sceneHint).toBe("monitor");
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

  it("auto mode picks high-contrast preprocess for low-contrast captures", () => {
    const lowContrastGray = new Uint8ClampedArray(1000).fill(120);
    const grayStats = computeGrayStats(lowContrastGray);
    const mode = resolveAutoPreprocessMode(grayStats, {
      overexposureRatio: 0.1,
      underexposureRatio: 0.1,
      blurVariance: 150,
    });
    expect(mode).toBe("bw_high_contrast");
  });

  it("uses relaxed warning thresholds for iOS Safari camera captures", () => {
    const thresholds = resolveCaptureWarningThresholds({
      dynamicRange: 58,
      overexposureRatio: 0.2,
      underexposureRatio: 0.12,
      pixelCount: 1_080_000,
    }, { warningProfile: "ios_safari" });

    expect(thresholds.profile).toBe("ios_safari");
    expect(thresholds.blurMinVariance).toBe(86);
    expect(thresholds.maxOverexposureRatio).toBeCloseTo(0.62, 2);
    expect(thresholds.maxUnderexposureRatio).toBeCloseTo(0.66, 2);
    expect(thresholds.minDynamicRange).toBe(44);
  });

  it("suppresses marginal blur warning when severe exposure clipping is present", () => {
    const warnings = buildCaptureWarnings({
      blurVariance: 60,
      overexposureRatio: 0.8,
      underexposureRatio: 0.02,
      dynamicRange: 36,
      pixelCount: 1_300_000,
    }, { warningProfile: "ios_safari" });

    expect(warnings.some((warning) => /overexposed|glare/i.test(warning))).toBe(true);
    expect(warnings.some((warning) => /blurry/i.test(warning))).toBe(false);
  });

  it("supports green-channel grayscale extraction for monitor captures", () => {
    const pixels = new Uint8ClampedArray([
      10, 200, 30, 255,
      220, 40, 20, 255,
    ]);
    const defaultGray = computeGrayFromImageData(pixels);
    const greenGray = computeGrayFromImageData(pixels, { channel: "green" });

    expect(Array.from(greenGray)).toEqual([200, 40]);
    expect(greenGray[0]).not.toBe(defaultGray[0]);
    expect(greenGray[1]).not.toBe(defaultGray[1]);
  });

  it("auto-detects monitor-like chroma patterns and enables anti-moire reduction", () => {
    const width = 192;
    const height = 192;
    const data = new Uint8ClampedArray(width * height * 4);

    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const i = (y * width + x) * 4;
        const tone = 152 + ((x + y) % 9) - 4;
        const stripe = x % 3;
        let r = tone;
        let g = tone;
        let b = tone;
        if (stripe === 0) {
          r = Math.min(255, tone + 50);
          g = Math.max(0, tone - 24);
          b = Math.max(0, tone - 28);
        } else if (stripe === 1) {
          r = Math.max(0, tone - 22);
          g = Math.min(255, tone + 54);
          b = Math.max(0, tone - 20);
        } else {
          r = Math.max(0, tone - 24);
          g = Math.max(0, tone - 18);
          b = Math.min(255, tone + 56);
        }
        data[i] = r;
        data[i + 1] = g;
        data[i + 2] = b;
        data[i + 3] = 255;
      }
    }

    const imageData = { data, width, height };
    const processed = applyPreprocessToImageData(imageData, { mode: "bw_high_contrast", sceneHint: "auto" });
    expect(processed.monitorMoireReduction).toBe(true);
  });
});
