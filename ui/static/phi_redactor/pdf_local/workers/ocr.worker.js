import "../../vendor/pdfjs/pdf.worker.mjs";
import * as pdfjs from "../../vendor/pdfjs/pdf.mjs";
import Tesseract from "../../vendor/tesseract/tesseract.esm.min.js";
import { clamp01, mergeRegions, normalizeRect, rectArea } from "../pdf/layoutAnalysis.js";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "../../vendor/pdfjs/pdf.worker.mjs",
  import.meta.url,
).toString();

const DEFAULT_OCR_OPTIONS = Object.freeze({
  lang: "eng",
  qualityMode: "fast",
  scale: 2,
  psm: "6",
  maskImages: "auto",
  maskMarginPx: 6,
  maxMaskRegions: 12,
});

let activeJobId = 0;
let tesseractWorker = null;
let tesseractConfigKey = "";

function resolveOcrOptions(options = {}) {
  const merged = {
    ...DEFAULT_OCR_OPTIONS,
    ...(options && typeof options === "object" ? options : {}),
  };

  const qualityMode = merged.qualityMode === "high_accuracy" ? "high_accuracy" : "fast";
  const qualityScale = qualityMode === "high_accuracy" ? 3.1 : 2.05;
  const configuredScale = Number.isFinite(merged.scale) ? Number(merged.scale) : qualityScale;
  const maskImages = merged.maskImages === "off" || merged.maskImages === "none" || merged.maskImages === false
    ? "off"
    : merged.maskImages === "on" || merged.maskImages === true
      ? "on"
      : "auto";
  const maskMarginPx = Number.isFinite(merged.maskMarginPx) ? Math.max(0, Number(merged.maskMarginPx)) : 6;
  const maxMaskRegions = Number.isFinite(merged.maxMaskRegions)
    ? Math.max(0, Math.min(40, Math.floor(Number(merged.maxMaskRegions))))
    : 12;

  return {
    lang: typeof merged.lang === "string" && merged.lang.trim() ? merged.lang.trim() : "eng",
    qualityMode,
    scale: Math.max(1.1, Math.min(4, configuredScale)),
    psm: String(merged.psm || "6"),
    maskImages,
    maskMarginPx,
    maxMaskRegions,
  };
}

function toAssetUrl(path) {
  return new URL(`../../vendor/tesseract/${path}`, import.meta.url).toString();
}

async function getTesseractWorker(options, pageIndex, totalPages) {
  const configKey = `${options.lang}:${options.psm}`;
  if (tesseractWorker && configKey === tesseractConfigKey) {
    return tesseractWorker;
  }

  if (tesseractWorker) {
    try {
      await tesseractWorker.terminate();
    } catch {
      // Best-effort cleanup.
    }
  }

  self.postMessage({
    type: "ocr_stage",
    stage: "ocr_loading_assets",
    pageIndex,
    totalPages,
  });

  const workerPath = toAssetUrl("worker.min.js");
  const corePath = toAssetUrl("tesseract-core-simd.wasm.js");
  const langPath = toAssetUrl("tessdata/");

  const worker = await Tesseract.createWorker(
    options.lang,
    Tesseract.OEM.LSTM_ONLY,
    {
      workerPath,
      corePath,
      langPath,
      // Keep worker loading same-origin only; avoids CSP failures from blob workers.
      workerBlobURL: false,
      gzip: false,
      logger: (message) => {
        if (!message || typeof message !== "object") return;
        const progress = Number(message.progress);
        if (!Number.isFinite(progress)) return;
        self.postMessage({
          type: "ocr_status",
          status: String(message.status || "ocr"),
          progress,
        });
      },
    },
  );

  await worker.setParameters({
    preserve_interword_spaces: "1",
    tessedit_pageseg_mode: options.psm,
  });

  tesseractWorker = worker;
  tesseractConfigKey = configKey;
  return worker;
}

function getViewportScale(page, baseScale) {
  const unscaled = page.getViewport({ scale: 1 });
  const maxDimension = Math.max(unscaled.width, unscaled.height);
  if (maxDimension <= 0) return baseScale;
  if (maxDimension * baseScale <= 2800) return baseScale;
  return Math.max(1.2, 2800 / maxDimension);
}

function toViewportRect(region, viewport) {
  const normalized = normalizeRect(region);
  const x1 = normalized.x;
  const y1 = normalized.y;
  const x2 = normalized.x + normalized.width;
  const y2 = normalized.y + normalized.height;
  if (![x1, y1, x2, y2].every((value) => Number.isFinite(value))) return null;

  const rect = viewport.convertToViewportRectangle([x1, y1, x2, y2]);
  if (!Array.isArray(rect) || rect.length < 4) return null;
  const left = Math.min(rect[0], rect[2]);
  const right = Math.max(rect[0], rect[2]);
  const top = Math.min(rect[1], rect[3]);
  const bottom = Math.max(rect[1], rect[3]);
  const width = right - left;
  const height = bottom - top;
  if (!Number.isFinite(width) || !Number.isFinite(height)) return null;
  if (width <= 1 || height <= 1) return null;
  return normalizeRect({ x: left, y: top, width, height });
}

function clampRectToCanvas(rect, canvasWidth, canvasHeight) {
  const normalized = normalizeRect(rect);
  const left = Math.max(0, normalized.x);
  const top = Math.max(0, normalized.y);
  const right = Math.min(canvasWidth, normalized.x + normalized.width);
  const bottom = Math.min(canvasHeight, normalized.y + normalized.height);
  const width = Math.max(0, right - left);
  const height = Math.max(0, bottom - top);
  if (width <= 1 || height <= 1) return null;
  return { x: left, y: top, width, height };
}

function expandRectPx(rect, marginPx) {
  const normalized = normalizeRect(rect);
  const m = Math.max(0, Number(marginPx) || 0);
  return {
    x: normalized.x - m,
    y: normalized.y - m,
    width: normalized.width + m * 2,
    height: normalized.height + m * 2,
  };
}

function computeCoverageRatio(rects, pageWidth, pageHeight) {
  const pageArea = Math.max(1, pageWidth * pageHeight);
  const merged = mergeRegions(rects, { mergeGap: 2 });
  let total = 0;
  for (const rect of merged) {
    total += rectArea(rect);
  }
  return clamp01(total / pageArea);
}

function computeRegionSampleMetrics(imageData) {
  const data = imageData?.data;
  if (!data || typeof data.length !== "number" || data.length < 4) {
    return {
      colorfulness: 0,
      whiteRatio: 0,
      darkRatio: 0,
    };
  }

  let colorDiffSum = 0;
  let white = 0;
  let dark = 0;
  const pixelCount = Math.floor(data.length / 4);

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const brightness = (r + g + b) / 3;
    if (brightness >= 240) white += 1;
    else if (brightness <= 50) dark += 1;
    colorDiffSum += Math.abs(r - g) + Math.abs(r - b) + Math.abs(g - b);
  }

  const denom = Math.max(1, pixelCount);
  const colorfulness = clamp01(colorDiffSum / (denom * 510));
  return {
    colorfulness,
    whiteRatio: clamp01(white / denom),
    darkRatio: clamp01(dark / denom),
  };
}

function shouldMaskRegion(metrics, areaRatio) {
  const whiteRatio = clamp01(metrics.whiteRatio);
  const darkRatio = clamp01(metrics.darkRatio);
  const midRatio = clamp01(1 - whiteRatio - darkRatio);
  const colorfulness = clamp01(metrics.colorfulness);

  const looksLikeTextScan = (colorfulness < 0.09 && whiteRatio > 0.72) || whiteRatio > 0.88;
  const looksLikePhoto = midRatio > 0.55 ||
    (colorfulness > 0.12 && whiteRatio < 0.78 && midRatio > 0.25) ||
    (colorfulness > 0.18 && whiteRatio < 0.88);

  if (areaRatio >= 0.92) return { mask: false, reason: "full_page_image" };
  if (looksLikePhoto && !looksLikeTextScan) return { mask: true, reason: "photo_like" };
  return { mask: false, reason: looksLikeTextScan ? "text_like" : "uncertain" };
}

function selectMaskRects(canvas, viewport, hint, options) {
  const mode = options.maskImages;
  if (mode === "off") {
    return { rects: [], meta: { applied: false, mode, reason: "disabled" } };
  }

  const pdfRegions = Array.isArray(hint?.imageRegions) ? hint.imageRegions : [];
  if (!pdfRegions.length) {
    return { rects: [], meta: { applied: false, mode, reason: "no_image_regions" } };
  }

  const width = Math.max(1, canvas.width);
  const height = Math.max(1, canvas.height);
  const pageArea = width * height;

  const viewportRegions = [];
  for (const region of pdfRegions) {
    const vr = toViewportRect(region, viewport);
    if (!vr) continue;
    const expanded = expandRectPx(vr, options.maskMarginPx);
    const clamped = clampRectToCanvas(expanded, width, height);
    if (!clamped) continue;
    viewportRegions.push(clamped);
  }

  if (!viewportRegions.length) {
    return { rects: [], meta: { applied: false, mode, reason: "no_valid_regions" } };
  }

  const mergedRegions = mergeRegions(viewportRegions, { mergeGap: 4 });
  const coverageRatio = computeCoverageRatio(mergedRegions, width, height);
  const maxAreaRatio = Math.max(
    0,
    ...mergedRegions.map((rect) => rectArea(rect) / Math.max(1, pageArea)),
  );
  const nativeCharCount = Number(hint?.stats?.charCount) || 0;

  if (mode === "auto" && maxAreaRatio >= 0.92 && nativeCharCount < 200) {
    return {
      rects: [],
      meta: {
        applied: false,
        mode,
        reason: "likely_scanned_page",
        coverageRatio,
        nativeCharCount,
      },
    };
  }

  const minAreaRatio = 0.002;
  const candidates = mergedRegions
    .map((rect) => ({
      rect,
      areaRatio: rectArea(rect) / Math.max(1, pageArea),
    }))
    .filter((entry) => entry.areaRatio >= minAreaRatio)
    .sort((a, b) => b.areaRatio - a.areaRatio)
    .slice(0, options.maxMaskRegions);

  if (!candidates.length) {
    return {
      rects: [],
      meta: {
        applied: false,
        mode,
        reason: "regions_too_small",
        coverageRatio,
      },
    };
  }

  const sampleSize = 64;
  const sampleCanvas = new OffscreenCanvas(sampleSize, sampleSize);
  const sampleCtx = sampleCanvas.getContext("2d", { alpha: false, willReadFrequently: true });

  const rects = [];
  let maskedPhotoLike = 0;
  let keptTextLike = 0;
  let keptUncertain = 0;

  for (const entry of candidates) {
    const rect = entry.rect;
    if (!sampleCtx) {
      rects.push(rect);
      maskedPhotoLike += 1;
      continue;
    }

    try {
      sampleCtx.fillStyle = "#ffffff";
      sampleCtx.fillRect(0, 0, sampleSize, sampleSize);
      sampleCtx.drawImage(
        canvas,
        rect.x,
        rect.y,
        rect.width,
        rect.height,
        0,
        0,
        sampleSize,
        sampleSize,
      );
      const metrics = computeRegionSampleMetrics(sampleCtx.getImageData(0, 0, sampleSize, sampleSize));
      const decision = shouldMaskRegion(metrics, entry.areaRatio);
      if (decision.mask) {
        rects.push(rect);
        maskedPhotoLike += 1;
      } else if (decision.reason === "text_like" || decision.reason === "full_page_image") {
        keptTextLike += 1;
      } else {
        keptUncertain += 1;
        if (mode === "on") {
          rects.push(rect);
          maskedPhotoLike += 1;
        }
      }
    } catch {
      if (mode === "on") {
        rects.push(rect);
        maskedPhotoLike += 1;
      } else {
        keptUncertain += 1;
      }
    }
  }

  return {
    rects,
    meta: {
      applied: rects.length > 0,
      mode,
      reason: rects.length ? "masked_image_regions" : "no_photo_like_regions",
      coverageRatio,
      nativeCharCount,
      candidateCount: candidates.length,
      maskedCount: rects.length,
      maskedPhotoLike,
      keptTextLike,
      keptUncertain,
    },
  };
}

async function renderPageImageForOcr(page, requestedScale, hint, options) {
  if (typeof OffscreenCanvas === "undefined") {
    throw new Error("OffscreenCanvas is unavailable in this browser; OCR rendering cannot run in worker.");
  }

  const safeScale = getViewportScale(page, requestedScale);
  const viewport = page.getViewport({ scale: safeScale });
  const width = Math.max(1, Math.floor(viewport.width));
  const height = Math.max(1, Math.floor(viewport.height));

  const canvas = new OffscreenCanvas(width, height);
  const context = canvas.getContext("2d", { alpha: false, willReadFrequently: true });
  if (!context) {
    throw new Error("Unable to acquire 2D context for OCR rendering.");
  }

  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, width, height);

  await page.render({
    canvasContext: context,
    viewport,
  }).promise;

  const masking = selectMaskRects(canvas, viewport, hint, options);
  if (masking.rects.length) {
    context.fillStyle = "#ffffff";
    for (const rect of masking.rects) {
      context.fillRect(rect.x, rect.y, rect.width, rect.height);
    }
  }

  // tesseract.js in worker mode reliably accepts OffscreenCanvas/Blob inputs.
  // Avoid ImageData here; some runtimes fail with "Error attempting to read image."
  let ocrInput = canvas;
  if (typeof canvas.convertToBlob === "function") {
    try {
      ocrInput = await canvas.convertToBlob({ type: "image/png" });
    } catch {
      // Fall back to canvas when blob conversion is unavailable.
      ocrInput = canvas;
    }
  }

  return {
    ocrInput,
    width,
    height,
    scale: safeScale,
    masking: masking.meta,
  };
}

async function runOcrForPages(pdfBytes, pageIndexes, pageHints, options, jobId) {
  const loadingTask = pdfjs.getDocument({
    data: pdfBytes,
    isEvalSupported: false,
    useWorkerFetch: false,
  });
  const doc = await loadingTask.promise;

  const hintMap = new Map();
  for (const hint of Array.isArray(pageHints) ? pageHints : []) {
    const pageIndex = Number(hint?.pageIndex);
    if (!Number.isFinite(pageIndex)) continue;
    hintMap.set(pageIndex, hint);
  }

  const uniquePageIndexes = [...new Set(
    (Array.isArray(pageIndexes) ? pageIndexes : [])
      .map((value) => Number(value))
      .filter((value) => Number.isFinite(value) && value >= 0 && value < doc.numPages),
  )].sort((a, b) => a - b);

  const totalPages = uniquePageIndexes.length;
  const results = [];

  if (!totalPages) {
    await doc.destroy();
    return results;
  }

  const worker = await getTesseractWorker(options, 0, totalPages);

  for (let i = 0; i < uniquePageIndexes.length; i += 1) {
    if (jobId !== activeJobId) {
      break;
    }

    const pageIndex = uniquePageIndexes[i];
    const page = await doc.getPage(pageIndex + 1);

    self.postMessage({
      type: "ocr_stage",
      stage: "ocr_rendering",
      pageIndex: i,
      totalPages,
      sourcePageIndex: pageIndex,
    });

    const hint = hintMap.get(pageIndex) || null;
    const render = await renderPageImageForOcr(page, options.scale, hint, options);

    self.postMessage({
      type: "ocr_stage",
      stage: "ocr_recognizing",
      pageIndex: i,
      totalPages,
      sourcePageIndex: pageIndex,
    });

    const startedAt = Date.now();
    const recognized = await worker.recognize(render.ocrInput);
    const durationMs = Date.now() - startedAt;
    const text = typeof recognized?.data?.text === "string" ? recognized.data.text : "";
    const confidence = Number.isFinite(recognized?.data?.confidence)
      ? Number(recognized.data.confidence)
      : null;

    const pageResult = {
      pageIndex,
      text,
      meta: {
        confidence,
        source: "ocr",
        width: render.width,
        height: render.height,
        scale: render.scale,
        durationMs,
        masking: render.masking,
      },
    };

    results.push(pageResult);

    self.postMessage({
      type: "ocr_page",
      page: pageResult,
    });
    self.postMessage({
      type: "ocr_progress",
      completedPages: i + 1,
      totalPages,
    });
  }

  await doc.destroy();
  return results;
}

self.onmessage = async (event) => {
  const data = event.data || {};
  if (data.type !== "ocr_extract") return;

  const jobId = activeJobId + 1;
  activeJobId = jobId;

  try {
    const options = resolveOcrOptions(data.options || {});
    const pages = await runOcrForPages(
      data.pdfBytes,
      data.pageIndexes,
      data.pageHints,
      options,
      jobId,
    );

    if (jobId !== activeJobId) return;
    self.postMessage({ type: "ocr_done", pages });
  } catch (error) {
    if (jobId !== activeJobId) return;
    const message = error instanceof Error ? error.message : String(error);
    self.postMessage({ type: "error", error: message });
  }
};
