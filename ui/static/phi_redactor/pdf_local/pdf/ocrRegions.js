import { clamp01, mergeRegions, normalizeRect, rectArea } from "./layoutAnalysis.js";

const DEFAULT_CROP_OPTIONS = Object.freeze({
  mode: "auto",
  paddingPx: 14,
  minWidthRatio: 0.42,
  minHeightRatio: 0.5,
  minTextRegionCount: 6,
});

function clamp(value, min, max) {
  if (!Number.isFinite(value)) return min;
  if (value < min) return min;
  if (value > max) return max;
  return value;
}

function quantile(values, q) {
  const list = (Array.isArray(values) ? values : [])
    .filter((value) => Number.isFinite(value))
    .sort((a, b) => a - b);
  if (!list.length) return null;
  if (list.length === 1) return list[0];
  const qq = clamp(q, 0, 1);
  const position = (list.length - 1) * qq;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return list[lower];
  const weight = position - lower;
  return list[lower] * (1 - weight) + list[upper] * weight;
}

function normalizeRegions(regions, width, height) {
  return mergeRegions(
    (Array.isArray(regions) ? regions : [])
      .map(normalizeRect)
      .filter((rect) => rect.width > 1 && rect.height > 1)
      .map((rect) => {
        const x0 = clamp(rect.x, 0, width);
        const y0 = clamp(rect.y, 0, height);
        const x1 = clamp(rect.x + rect.width, 0, width);
        const y1 = clamp(rect.y + rect.height, 0, height);
        return normalizeRect({
          x: x0,
          y: y0,
          width: Math.max(0, x1 - x0),
          height: Math.max(0, y1 - y0),
        });
      })
      .filter((rect) => rect.width > 1 && rect.height > 1),
    { mergeGap: 2 },
  );
}

function buildBox(rect) {
  return [
    Math.floor(rect.x),
    Math.floor(rect.y),
    Math.floor(rect.x + rect.width),
    Math.floor(rect.y + rect.height),
  ];
}

/**
 * Compute a left-column OCR crop rectangle from text/image geometry.
 * Input regions are expected in viewport pixel space.
 */
export function computeOcrCropRect(input = {}, options = {}) {
  const width = Math.max(1, Math.floor(Number(input.canvasWidth) || 0));
  const height = Math.max(1, Math.floor(Number(input.canvasHeight) || 0));
  const pageArea = Math.max(1, width * height);

  const merged = {
    ...DEFAULT_CROP_OPTIONS,
    ...(options && typeof options === "object" ? options : {}),
  };
  const mode = merged.mode === "on" ? "on" : merged.mode === "off" ? "off" : "auto";
  const paddingPx = Math.max(0, Number(merged.paddingPx) || DEFAULT_CROP_OPTIONS.paddingPx);
  const minWidthRatio = clamp01(Number(merged.minWidthRatio) || DEFAULT_CROP_OPTIONS.minWidthRatio);
  const minHeightRatio = clamp01(Number(merged.minHeightRatio) || DEFAULT_CROP_OPTIONS.minHeightRatio);
  const minTextRegionCount = Math.max(2, Math.floor(Number(merged.minTextRegionCount) || DEFAULT_CROP_OPTIONS.minTextRegionCount));

  if (mode === "off") {
    return {
      rect: null,
      meta: {
        applied: false,
        mode,
        reason: "disabled",
      },
    };
  }

  const textRegions = normalizeRegions(input.textRegions, width, height);
  const imageRegions = normalizeRegions(input.imageRegions, width, height);
  const nativeCharCount = Math.max(0, Number(input.nativeCharCount) || 0);

  if (!textRegions.length && !imageRegions.length) {
    return {
      rect: null,
      meta: {
        applied: false,
        mode,
        reason: "no_regions",
      },
    };
  }

  if (mode === "auto" && textRegions.length < minTextRegionCount && nativeCharCount < 220) {
    return {
      rect: null,
      meta: {
        applied: false,
        mode,
        reason: "low_text_signal",
        nativeCharCount,
        textRegionCount: textRegions.length,
      },
    };
  }

  const rightEdges = textRegions.map((rect) => rect.x + rect.width);
  const x1FromText = quantile(rightEdges, 0.85);

  const rightStripRegions = imageRegions.filter((rect) => {
    const tallEnough = rect.height / Math.max(1, height) >= 0.18;
    const largeEnough = rectArea(rect) / pageArea >= 0.035;
    const rightSide = rect.x >= width * 0.45;
    return rightSide && (tallEnough || largeEnough);
  });
  const x1FromImageStrip = rightStripRegions.length
    ? Math.min(...rightStripRegions.map((rect) => rect.x))
    : null;

  let targetX1 = null;
  if (Number.isFinite(x1FromText) && Number.isFinite(x1FromImageStrip)) {
    targetX1 = Math.min(Number(x1FromText), Number(x1FromImageStrip)) + paddingPx;
  } else if (Number.isFinite(x1FromText)) {
    targetX1 = Number(x1FromText) + paddingPx;
  } else if (mode === "on" && Number.isFinite(x1FromImageStrip)) {
    targetX1 = Number(x1FromImageStrip) + paddingPx;
  }

  if (!Number.isFinite(targetX1)) {
    return {
      rect: null,
      meta: {
        applied: false,
        mode,
        reason: "no_column_signal",
        textRegionCount: textRegions.length,
        imageRegionCount: imageRegions.length,
      },
    };
  }

  const minWidthPx = Math.floor(width * Math.max(0.25, minWidthRatio));
  const croppedX1 = clamp(Math.floor(targetX1), minWidthPx, width);

  const yStarts = textRegions.map((rect) => rect.y);
  const yEnds = textRegions.map((rect) => rect.y + rect.height);
  let y0 = 0;
  let y1 = height;
  if (yStarts.length && yEnds.length) {
    y0 = clamp(Math.floor(Math.min(...yStarts) - paddingPx), 0, height);
    y1 = clamp(Math.ceil(Math.max(...yEnds) + paddingPx), 0, height);
    if (y1 - y0 < height * Math.max(0.25, minHeightRatio)) {
      y0 = 0;
      y1 = height;
    }
  }

  const rect = normalizeRect({
    x: 0,
    y: y0,
    width: croppedX1,
    height: Math.max(1, y1 - y0),
  });
  const applied = rect.width < width - 2 || rect.height < height - 2;

  return {
    rect: applied ? rect : null,
    meta: {
      applied,
      mode,
      reason: applied ? "left_column_crop" : "full_page",
      textRegionCount: textRegions.length,
      imageRegionCount: imageRegions.length,
      nativeCharCount,
      x1FromText: Number.isFinite(x1FromText) ? Number(x1FromText) : null,
      x1FromImageStrip: Number.isFinite(x1FromImageStrip) ? Number(x1FromImageStrip) : null,
      box: buildBox(rect),
    },
  };
}
