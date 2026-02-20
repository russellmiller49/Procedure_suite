import Tesseract from "../../vendor/tesseract/tesseract.esm.min.js";
import { computeOcrTextMetrics } from "../../pdf_local/pdf/ocrMetrics.js";
import {
  applyClinicalOcrHeuristics,
  composeOcrPageText,
  filterOcrLinesDetailed,
} from "../../pdf_local/pdf/ocrPostprocess.js";
import { preprocessCanvasForOcr } from "../imagePreprocess.js";

const DEFAULT_OPTIONS = Object.freeze({
  lang: "eng",
  mode: "fast",
  preprocess: {
    mode: "off",
  },
});

let tesseractWorker = null;
let tesseractConfigKey = "";
let activePsm = "";
let activeJobId = "";
const cancelledJobs = new Set();

function hasFunction(value) {
  return typeof value === "function";
}

function safeNumber(value, fallback = 0) {
  return Number.isFinite(value) ? Number(value) : fallback;
}

function resolveOptions(input = {}) {
  const preprocessMode = input?.preprocess?.mode === "bw_high_contrast"
    ? "bw_high_contrast"
    : input?.preprocess?.mode === "grayscale"
      ? "grayscale"
      : "off";

  const qualityMode = input?.mode === "high_accuracy" ? "high_accuracy" : "fast";

  return {
    ...DEFAULT_OPTIONS,
    ...input,
    lang: typeof input?.lang === "string" && input.lang.trim() ? input.lang.trim() : "eng",
    mode: qualityMode,
    psm: qualityMode === "high_accuracy" ? "6" : "6",
    maxDim: qualityMode === "high_accuracy" ? 2300 : 1800,
    preprocess: {
      mode: preprocessMode,
    },
  };
}

function toAssetUrl(path) {
  return new URL(`../../vendor/tesseract/${path}`, import.meta.url).toString();
}

async function getTesseractWorker(options) {
  const configKey = `${options.lang}`;
  if (tesseractWorker && configKey === tesseractConfigKey) {
    return tesseractWorker;
  }

  if (tesseractWorker) {
    try {
      await tesseractWorker.terminate();
    } catch {
      // ignore best-effort cleanup
    }
    tesseractWorker = null;
    tesseractConfigKey = "";
    activePsm = "";
  }

  const worker = await Tesseract.createWorker(
    options.lang,
    Tesseract.OEM.LSTM_ONLY,
    {
      workerPath: toAssetUrl("worker.min.js"),
      corePath: toAssetUrl("tesseract-core-simd.wasm.js"),
      langPath: toAssetUrl("tessdata/"),
      workerBlobURL: false,
      gzip: false,
      logger: (message) => {
        if (!message || typeof message !== "object") return;
        if (!activeJobId) return;
        const progress = Number(message.progress);
        if (!Number.isFinite(progress)) return;
        self.postMessage({
          type: "camera_ocr_progress",
          jobId: activeJobId,
          stage: "recognize",
          pct: progress,
          status: String(message.status || "recognize"),
        });
      },
    },
  );

  await worker.setParameters({
    preserve_interword_spaces: "1",
  });

  tesseractWorker = worker;
  tesseractConfigKey = configKey;
  activePsm = "";
  return worker;
}

async function setWorkerPsm(worker, psm) {
  const normalized = String(psm || "6");
  if (normalized === activePsm) return;
  await worker.setParameters({
    tessedit_pageseg_mode: normalized,
  });
  activePsm = normalized;
}

function coerceConfidence(value) {
  const conf = safeNumber(value, Number.NaN);
  if (!Number.isFinite(conf) || conf < 0) return null;
  return Math.max(0, Math.min(100, conf));
}

function normalizeBbox(rawBBox = {}) {
  if (!rawBBox || typeof rawBBox !== "object") {
    return { x: 0, y: 0, width: 0, height: 0 };
  }

  const x0 = Number.isFinite(rawBBox.x0) ? Number(rawBBox.x0) : safeNumber(rawBBox.x, 0);
  const y0 = Number.isFinite(rawBBox.y0) ? Number(rawBBox.y0) : safeNumber(rawBBox.y, 0);
  const x1 = Number.isFinite(rawBBox.x1)
    ? Number(rawBBox.x1)
    : Number.isFinite(rawBBox.w)
      ? x0 + Number(rawBBox.w)
      : x0;
  const y1 = Number.isFinite(rawBBox.y1)
    ? Number(rawBBox.y1)
    : Number.isFinite(rawBBox.h)
      ? y0 + Number(rawBBox.h)
      : y0;

  const left = Math.min(x0, x1);
  const top = Math.min(y0, y1);
  return {
    x: left,
    y: top,
    width: Math.max(0, Math.abs(x1 - x0)),
    height: Math.max(0, Math.abs(y1 - y0)),
  };
}

function extractLines(recognizedData, pageIndex) {
  const rawLines = Array.isArray(recognizedData?.lines) ? recognizedData.lines : [];
  const lines = [];

  for (const raw of rawLines) {
    const text = String(raw?.text || "").replace(/\s+/g, " ").trim();
    if (!text) continue;
    lines.push({
      text,
      confidence: coerceConfidence(raw?.confidence ?? raw?.conf),
      bbox: normalizeBbox(raw?.bbox || raw),
      pageIndex,
    });
  }

  return lines;
}

async function buildOcrInputFromCanvas(canvas) {
  if (hasFunction(canvas?.convertToBlob)) {
    try {
      const blob = await canvas.convertToBlob({ type: "image/png" });
      if (blob) return blob;
    } catch {
      // fallback to canvas
    }
  }
  return canvas;
}

function summarizePageMetrics(metrics, preprocessResult) {
  return {
    charCount: Number(metrics.charCount) || 0,
    alphaRatio: Number(metrics.alphaRatio) || 0,
    meanConf: Number.isFinite(metrics.meanLineConf) ? Number(metrics.meanLineConf) : null,
    lowConfFrac: Number.isFinite(metrics.lowConfLineFrac) ? Number(metrics.lowConfLineFrac) : null,
    numLines: Number(metrics.numLines) || 0,
    medianTokenLen: Number(metrics.medianTokenLen) || 0,
    blurVariance: Number(preprocessResult?.metrics?.blurVariance) || 0,
    overexposureRatio: Number(preprocessResult?.metrics?.overexposureRatio) || 0,
  };
}

function isCancelled(jobId) {
  return cancelledJobs.has(String(jobId || ""));
}

function closeBitmap(bitmap) {
  if (!bitmap || !hasFunction(bitmap.close)) return;
  try {
    bitmap.close();
  } catch {
    // ignore
  }
}

async function runJob(data) {
  const jobId = String(data.jobId || "");
  if (!jobId) {
    self.postMessage({ type: "camera_ocr_error", jobId, error: "Missing jobId" });
    return;
  }

  const options = resolveOptions(data.options || {});
  const pages = (Array.isArray(data.pages) ? data.pages : [])
    .filter((page) => page && page.bitmap && Number.isFinite(page.pageIndex))
    .sort((a, b) => Number(a.pageIndex) - Number(b.pageIndex));

  if (!pages.length) {
    self.postMessage({ type: "camera_ocr_error", jobId, error: "No pages provided" });
    return;
  }

  activeJobId = jobId;

  try {
    const worker = await getTesseractWorker(options);
    const outPages = [];

    for (let idx = 0; idx < pages.length; idx += 1) {
      if (isCancelled(jobId)) {
        self.postMessage({ type: "camera_ocr_cancelled", jobId });
        return;
      }

      const page = pages[idx];
      const pageIndex = Number(page.pageIndex);
      self.postMessage({
        type: "camera_ocr_progress",
        jobId,
        pageIndex,
        stage: "preprocess",
        pct: idx / Math.max(1, pages.length),
      });

      const baseCanvas = new OffscreenCanvas(
        Math.max(1, Math.floor(safeNumber(page.width, page.bitmap.width || 1))),
        Math.max(1, Math.floor(safeNumber(page.height, page.bitmap.height || 1))),
      );
      const baseCtx = baseCanvas.getContext("2d", { alpha: false, willReadFrequently: true });
      if (!baseCtx) {
        throw new Error("Unable to acquire 2D context for camera OCR");
      }

      baseCtx.fillStyle = "#ffffff";
      baseCtx.fillRect(0, 0, baseCanvas.width, baseCanvas.height);
      baseCtx.drawImage(page.bitmap, 0, 0, baseCanvas.width, baseCanvas.height);

      const preprocessResult = preprocessCanvasForOcr(baseCanvas, {
        mode: options.preprocess.mode,
        maxDim: options.maxDim,
      });

      if (isCancelled(jobId)) {
        self.postMessage({ type: "camera_ocr_cancelled", jobId });
        return;
      }

      self.postMessage({
        type: "camera_ocr_progress",
        jobId,
        pageIndex,
        stage: "recognize",
        pct: idx / Math.max(1, pages.length),
      });

      await setWorkerPsm(worker, options.psm);
      const ocrInput = await buildOcrInputFromCanvas(preprocessResult.canvas);
      const recognized = await worker.recognize(ocrInput);

      if (isCancelled(jobId)) {
        self.postMessage({ type: "camera_ocr_cancelled", jobId });
        return;
      }

      self.postMessage({
        type: "camera_ocr_progress",
        jobId,
        pageIndex,
        stage: "postprocess",
        pct: idx / Math.max(1, pages.length),
      });

      const rawLines = extractLines(recognized?.data, pageIndex);
      const filtered = filterOcrLinesDetailed(rawLines, [], {
        disableFigureOverlap: true,
        dropCaptions: false,
        dropBoilerplate: true,
        shortLowConfThreshold: 30,
      });

      const lines = Array.isArray(filtered?.lines) ? filtered.lines : [];
      let text = composeOcrPageText(lines);
      if (!text.trim()) {
        text = applyClinicalOcrHeuristics(String(recognized?.data?.text || ""));
      }

      const metrics = computeOcrTextMetrics({ text, lines });
      const pageResult = {
        pageIndex,
        text,
        lines: lines.map((line) => ({
          text: String(line.text || ""),
          confidence: coerceConfidence(line.confidence),
          bbox: normalizeBbox(line.bbox),
        })),
        metrics: summarizePageMetrics(metrics, preprocessResult),
        warnings: Array.isArray(preprocessResult.warnings) ? preprocessResult.warnings : [],
      };

      outPages.push(pageResult);
      self.postMessage({ type: "camera_ocr_page", jobId, page: pageResult });
      closeBitmap(page.bitmap);
    }

    self.postMessage({
      type: "camera_ocr_progress",
      jobId,
      stage: "postprocess",
      pct: 1,
      completedPages: pages.length,
      totalPages: pages.length,
    });
    self.postMessage({ type: "camera_ocr_done", jobId, pages: outPages });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    self.postMessage({ type: "camera_ocr_error", jobId, error: message });
  } finally {
    cancelledJobs.delete(jobId);
    if (activeJobId === jobId) {
      activeJobId = "";
    }
  }
}

self.onmessage = async (event) => {
  const data = event?.data || {};
  if (data.type === "camera_ocr_cancel") {
    const jobId = String(data.jobId || "");
    if (jobId) cancelledJobs.add(jobId);
    return;
  }

  if (data.type === "camera_ocr_run") {
    await runJob(data);
  }
};
