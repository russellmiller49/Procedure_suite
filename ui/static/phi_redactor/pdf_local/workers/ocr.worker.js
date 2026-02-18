import "../../vendor/pdfjs/pdf.worker.mjs";
import * as pdfjs from "../../vendor/pdfjs/pdf.mjs";
import Tesseract from "../../vendor/tesseract/tesseract.esm.min.js";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "../../vendor/pdfjs/pdf.worker.mjs",
  import.meta.url,
).toString();

const DEFAULT_OCR_OPTIONS = Object.freeze({
  lang: "eng",
  qualityMode: "fast",
  scale: 2,
  psm: "6",
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

  return {
    lang: typeof merged.lang === "string" && merged.lang.trim() ? merged.lang.trim() : "eng",
    qualityMode,
    scale: Math.max(1.1, Math.min(4, configuredScale)),
    psm: String(merged.psm || "6"),
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

async function renderPageImageForOcr(page, requestedScale) {
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
  };
}

async function runOcrForPages(pdfBytes, pageIndexes, options, jobId) {
  const loadingTask = pdfjs.getDocument({
    data: pdfBytes,
    isEvalSupported: false,
    useWorkerFetch: false,
  });
  const doc = await loadingTask.promise;

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

    const render = await renderPageImageForOcr(page, options.scale);

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
