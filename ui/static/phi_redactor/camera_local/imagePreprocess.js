function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function safeNumber(value, fallback = 0) {
  return Number.isFinite(value) ? Number(value) : fallback;
}

function buildHistogram(grayValues) {
  const histogram = new Uint32Array(256);
  for (let i = 0; i < grayValues.length; i += 1) {
    histogram[grayValues[i]] += 1;
  }
  return histogram;
}

function computeOtsuThreshold(histogram, totalCount) {
  const total = Math.max(1, safeNumber(totalCount, 1));
  let sum = 0;
  for (let i = 0; i < 256; i += 1) {
    sum += i * histogram[i];
  }

  let sumBackground = 0;
  let weightBackground = 0;
  let bestThreshold = 127;
  let bestVariance = Number.NEGATIVE_INFINITY;

  for (let i = 0; i < 256; i += 1) {
    weightBackground += histogram[i];
    if (!weightBackground) continue;

    const weightForeground = total - weightBackground;
    if (!weightForeground) break;

    sumBackground += i * histogram[i];
    const meanBackground = sumBackground / weightBackground;
    const meanForeground = (sum - sumBackground) / weightForeground;
    const diff = meanBackground - meanForeground;
    const variance = weightBackground * weightForeground * diff * diff;
    if (variance > bestVariance) {
      bestVariance = variance;
      bestThreshold = i;
    }
  }

  return bestThreshold;
}

function percentileFromHistogram(histogram, totalCount, percentile) {
  const total = Math.max(1, Math.floor(safeNumber(totalCount, 1)));
  const pct = clamp(safeNumber(percentile, 0.5), 0, 1);
  const target = Math.max(0, Math.min(total - 1, Math.floor(total * pct)));
  let seen = 0;
  for (let i = 0; i < 256; i += 1) {
    seen += histogram[i];
    if (seen > target) return i;
  }
  return 255;
}

export function computeGrayStats(grayValues) {
  const gray = grayValues instanceof Uint8ClampedArray
    ? grayValues
    : new Uint8ClampedArray(Array.isArray(grayValues) ? grayValues : []);
  if (!gray.length) {
    return {
      p05: 0,
      p10: 0,
      p50: 0,
      p90: 0,
      p95: 0,
      dynamicRange: 0,
      histogram: new Uint32Array(256),
      pixelCount: 0,
    };
  }

  const histogram = buildHistogram(gray);
  const pixelCount = gray.length;
  const p05 = percentileFromHistogram(histogram, pixelCount, 0.05);
  const p10 = percentileFromHistogram(histogram, pixelCount, 0.1);
  const p50 = percentileFromHistogram(histogram, pixelCount, 0.5);
  const p90 = percentileFromHistogram(histogram, pixelCount, 0.9);
  const p95 = percentileFromHistogram(histogram, pixelCount, 0.95);

  return {
    p05,
    p10,
    p50,
    p90,
    p95,
    dynamicRange: Math.max(0, p90 - p10),
    histogram,
    pixelCount,
  };
}

function applyContrastStretch(grayValues, stats, opts = {}) {
  const gray = grayValues instanceof Uint8ClampedArray
    ? grayValues
    : new Uint8ClampedArray(Array.isArray(grayValues) ? grayValues : []);
  if (!gray.length) return gray;

  const lowerPct = clamp(safeNumber(opts.lowerPercentile, 0.06), 0, 0.45);
  const upperPct = clamp(safeNumber(opts.upperPercentile, 0.94), 0.55, 1);
  const lower = percentileFromHistogram(stats.histogram, stats.pixelCount, lowerPct);
  const upper = percentileFromHistogram(stats.histogram, stats.pixelCount, upperPct);
  const span = Math.max(12, upper - lower);

  const out = new Uint8ClampedArray(gray.length);
  for (let i = 0; i < gray.length; i += 1) {
    const normalized = ((gray[i] - lower) * 255) / span;
    out[i] = Math.max(0, Math.min(255, Math.round(normalized)));
  }
  return out;
}

export function resolveAutoPreprocessMode(grayStats, qualityMetrics) {
  const dynamicRange = safeNumber(grayStats?.dynamicRange, 0);
  const overexposureRatio = safeNumber(qualityMetrics?.overexposureRatio, 0);
  const underexposureRatio = safeNumber(qualityMetrics?.underexposureRatio, 0);

  if (overexposureRatio > 0.34) return "bw_high_contrast";
  if (underexposureRatio > 0.46) return "bw_high_contrast";
  if (dynamicRange < 54) return "bw_high_contrast";
  return "grayscale";
}

export function computeScaledDimensions(width, height, maxDim = 2000) {
  const srcWidth = Math.max(1, Math.floor(safeNumber(width, 1)));
  const srcHeight = Math.max(1, Math.floor(safeNumber(height, 1)));
  const safeMaxDim = clamp(Math.floor(safeNumber(maxDim, 2000)), 320, 4096);
  const scale = Math.min(1, safeMaxDim / Math.max(srcWidth, srcHeight));
  return {
    width: Math.max(1, Math.round(srcWidth * scale)),
    height: Math.max(1, Math.round(srcHeight * scale)),
    scale,
  };
}

export function buildPreprocessPlan(input = {}) {
  const mode = input.mode === "bw_high_contrast"
    ? "bw_high_contrast"
    : input.mode === "grayscale"
      ? "grayscale"
      : input.mode === "auto"
        ? "auto"
        : "off";

  const dims = computeScaledDimensions(input.width, input.height, input.maxDim);
  return {
    mode,
    resolvedMode: mode,
    targetWidth: dims.width,
    targetHeight: dims.height,
    scale: dims.scale,
    applyGrayscale: mode === "grayscale" || mode === "bw_high_contrast" || mode === "auto",
    applyThreshold: mode === "bw_high_contrast",
    autoTuning: mode === "auto",
  };
}

function computeGrayFromImageData(data) {
  const pixelCount = Math.floor(data.length / 4);
  const gray = new Uint8ClampedArray(pixelCount);
  let p = 0;
  for (let i = 0; i < data.length; i += 4) {
    gray[p] = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
    p += 1;
  }
  return gray;
}

export function applyPreprocessToImageData(imageData, plan) {
  const data = imageData?.data;
  if (!data) {
    return {
      changed: false,
      gray: new Uint8ClampedArray(),
      sourceGray: new Uint8ClampedArray(),
      threshold: null,
      resolvedMode: "off",
      grayStats: computeGrayStats([]),
    };
  }

  const sourceGray = computeGrayFromImageData(data);
  const sourceStats = computeGrayStats(sourceGray);
  const srcWidth = Math.max(1, Math.floor(safeNumber(imageData?.width, 1)));
  const srcHeight = Math.max(1, Math.floor(safeNumber(imageData?.height, 1)));

  let resolvedMode = String(plan?.mode || "off");
  if (resolvedMode === "auto") {
    const qualityMetrics = computeCaptureQualityMetrics(sourceGray, srcWidth, srcHeight);
    resolvedMode = resolveAutoPreprocessMode(sourceStats, qualityMetrics);
  }

  if (resolvedMode !== "grayscale" && resolvedMode !== "bw_high_contrast") {
    return {
      changed: false,
      gray: sourceGray,
      sourceGray,
      threshold: null,
      resolvedMode: "off",
      grayStats: sourceStats,
    };
  }

  let threshold = null;
  let output = applyContrastStretch(sourceGray, sourceStats);

  if (resolvedMode === "bw_high_contrast") {
    const histogram = buildHistogram(output);
    threshold = computeOtsuThreshold(histogram, output.length);
    const binary = new Uint8ClampedArray(output.length);
    for (let i = 0; i < output.length; i += 1) {
      binary[i] = output[i] <= threshold ? 0 : 255;
    }
    output = binary;
  }

  let p = 0;
  for (let i = 0; i < data.length; i += 4) {
    const v = output[p];
    data[i] = v;
    data[i + 1] = v;
    data[i + 2] = v;
    data[i + 3] = 255;
    p += 1;
  }

  return {
    changed: true,
    gray: output,
    sourceGray,
    threshold,
    resolvedMode,
    grayStats: computeGrayStats(output),
  };
}

function computeLaplacianVariance(gray, width, height) {
  if (!gray.length || width < 3 || height < 3) return 0;

  let sum = 0;
  let sumSquares = 0;
  let count = 0;
  const stride = Math.max(1, Math.floor(Math.max(width, height) / 600));

  for (let y = 1; y < height - 1; y += stride) {
    for (let x = 1; x < width - 1; x += stride) {
      const idx = y * width + x;
      const lap =
        gray[idx - width] +
        gray[idx - 1] +
        gray[idx + 1] +
        gray[idx + width] -
        4 * gray[idx];

      sum += lap;
      sumSquares += lap * lap;
      count += 1;
    }
  }

  if (!count) return 0;
  const mean = sum / count;
  return Math.max(0, sumSquares / count - mean * mean);
}

export function computeCaptureQualityMetrics(gray, width, height, opts = {}) {
  const safeWidth = Math.max(1, Math.floor(safeNumber(width, 1)));
  const safeHeight = Math.max(1, Math.floor(safeNumber(height, 1)));
  const whiteThreshold = clamp(Math.floor(safeNumber(opts.whiteThreshold, 245)), 180, 254);
  const darkThreshold = clamp(Math.floor(safeNumber(opts.darkThreshold, 32)), 1, 120);

  let whiteCount = 0;
  let darkCount = 0;
  for (let i = 0; i < gray.length; i += 1) {
    if (gray[i] >= whiteThreshold) whiteCount += 1;
    if (gray[i] <= darkThreshold) darkCount += 1;
  }

  const pixelCount = Math.max(1, gray.length);
  const histogram = buildHistogram(gray);
  const p10 = percentileFromHistogram(histogram, pixelCount, 0.1);
  const p90 = percentileFromHistogram(histogram, pixelCount, 0.9);
  const overexposureRatio = whiteCount / pixelCount;
  const underexposureRatio = darkCount / pixelCount;
  const blurVariance = computeLaplacianVariance(gray, safeWidth, safeHeight);

  return {
    overexposureRatio,
    underexposureRatio,
    dynamicRange: Math.max(0, p90 - p10),
    blurVariance,
    pixelCount,
  };
}

export function buildCaptureWarnings(metrics, opts = {}) {
  const blurMinVariance = safeNumber(opts.blurMinVariance, 110);
  const maxOverexposureRatio = safeNumber(opts.maxOverexposureRatio, 0.55);
  const maxUnderexposureRatio = safeNumber(opts.maxUnderexposureRatio, 0.58);
  const minDynamicRange = safeNumber(opts.minDynamicRange, 50);
  const warnings = [];

  if (safeNumber(metrics.blurVariance, 0) < blurMinVariance) {
    warnings.push("Image may be blurry; consider retaking.");
  }
  if (safeNumber(metrics.overexposureRatio, 0) > maxOverexposureRatio) {
    warnings.push("Image may be overexposed; reduce glare and retake.");
  }
  if (safeNumber(metrics.underexposureRatio, 0) > maxUnderexposureRatio) {
    warnings.push("Image may be underexposed; increase lighting and retake.");
  }
  if (safeNumber(metrics.dynamicRange, 999) < minDynamicRange) {
    warnings.push("Image has low contrast; use flatter lighting or high-contrast enhance mode.");
  }

  return warnings;
}

function createOffscreenCanvas(width, height) {
  return new OffscreenCanvas(width, height);
}

export function preprocessCanvasForOcr(canvas, options = {}) {
  const sourceWidth = Math.max(1, Math.floor(safeNumber(canvas?.width, 1)));
  const sourceHeight = Math.max(1, Math.floor(safeNumber(canvas?.height, 1)));
  const plan = buildPreprocessPlan({
    width: sourceWidth,
    height: sourceHeight,
    maxDim: options.maxDim,
    mode: options.mode,
  });

  const targetCanvas = createOffscreenCanvas(plan.targetWidth, plan.targetHeight);
  const ctx = targetCanvas.getContext("2d", { alpha: false, willReadFrequently: true });
  if (!ctx) {
    throw new Error("Unable to acquire 2D context for preprocess");
  }

  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, plan.targetWidth, plan.targetHeight);
  ctx.drawImage(canvas, 0, 0, sourceWidth, sourceHeight, 0, 0, plan.targetWidth, plan.targetHeight);

  const imageData = ctx.getImageData(0, 0, plan.targetWidth, plan.targetHeight);
  const processed = applyPreprocessToImageData(imageData, plan);
  if (processed.changed) {
    ctx.putImageData(imageData, 0, 0);
  }

  const qualityGray = processed.sourceGray.length
    ? processed.sourceGray
    : computeGrayFromImageData(imageData.data);
  const metrics = computeCaptureQualityMetrics(qualityGray, plan.targetWidth, plan.targetHeight, options);
  const warnings = buildCaptureWarnings(metrics, options);

  return {
    canvas: targetCanvas,
    plan: {
      ...plan,
      resolvedMode: processed.resolvedMode || plan.mode,
    },
    threshold: processed.threshold,
    grayStats: processed.grayStats,
    metrics,
    warnings,
  };
}
