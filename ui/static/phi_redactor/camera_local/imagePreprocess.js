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
      : "off";

  const dims = computeScaledDimensions(input.width, input.height, input.maxDim);
  return {
    mode,
    targetWidth: dims.width,
    targetHeight: dims.height,
    scale: dims.scale,
    applyGrayscale: mode === "grayscale" || mode === "bw_high_contrast",
    applyThreshold: mode === "bw_high_contrast",
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
  if (!data || !plan || (!plan.applyGrayscale && !plan.applyThreshold)) {
    return {
      changed: false,
      gray: data ? computeGrayFromImageData(data) : new Uint8ClampedArray(),
      threshold: null,
    };
  }

  const gray = computeGrayFromImageData(data);
  let threshold = null;
  let output = gray;

  if (plan.applyThreshold) {
    const histogram = buildHistogram(gray);
    threshold = computeOtsuThreshold(histogram, gray.length);
    const binary = new Uint8ClampedArray(gray.length);
    for (let i = 0; i < gray.length; i += 1) {
      binary[i] = gray[i] <= threshold ? 0 : 255;
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
    threshold,
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

  let whiteCount = 0;
  for (let i = 0; i < gray.length; i += 1) {
    if (gray[i] >= whiteThreshold) whiteCount += 1;
  }

  const pixelCount = Math.max(1, gray.length);
  const overexposureRatio = whiteCount / pixelCount;
  const blurVariance = computeLaplacianVariance(gray, safeWidth, safeHeight);

  return {
    overexposureRatio,
    blurVariance,
    pixelCount,
  };
}

export function buildCaptureWarnings(metrics, opts = {}) {
  const blurMinVariance = safeNumber(opts.blurMinVariance, 110);
  const maxOverexposureRatio = safeNumber(opts.maxOverexposureRatio, 0.55);
  const warnings = [];

  if (safeNumber(metrics.blurVariance, 0) < blurMinVariance) {
    warnings.push("Image may be blurry; consider retaking.");
  }
  if (safeNumber(metrics.overexposureRatio, 0) > maxOverexposureRatio) {
    warnings.push("Image may be overexposed; reduce glare and retake.");
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

  const gray = processed.gray.length
    ? processed.gray
    : computeGrayFromImageData(imageData.data);
  const metrics = computeCaptureQualityMetrics(gray, plan.targetWidth, plan.targetHeight, options);
  const warnings = buildCaptureWarnings(metrics, options);

  return {
    canvas: targetCanvas,
    plan,
    threshold: processed.threshold,
    metrics,
    warnings,
  };
}
