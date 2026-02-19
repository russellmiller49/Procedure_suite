import { arbitratePageText } from "./fusion.js";
import { clamp01 } from "./layoutAnalysis.js";
import { classifyPage, isUnsafeNativePage, resolvePageSource } from "./pageClassifier.js";

const DEFAULT_GATE_OPTIONS = Object.freeze({
  minCompletenessConfidence: 0.72,
  maxContaminationScore: 0.24,
  hardBlockWhenUnsafeWithoutOcr: true,
});

const DEFAULT_OCR_OPTIONS = Object.freeze({
  available: true,
  enabled: true,
  lang: "eng",
  qualityMode: "fast",
  scale: 2.05,
  psm: "6",
  maskImages: "auto",
  cropMode: "auto",
  cropPaddingPx: 14,
});

function normalizeGateOptions(gate) {
  const merged = {
    ...DEFAULT_GATE_OPTIONS,
    ...(gate && typeof gate === "object" ? gate : {}),
  };

  return {
    minCompletenessConfidence: clamp01(Number(merged.minCompletenessConfidence)),
    maxContaminationScore: clamp01(Number(merged.maxContaminationScore)),
    hardBlockWhenUnsafeWithoutOcr: Boolean(merged.hardBlockWhenUnsafeWithoutOcr),
  };
}

function normalizeOcrOptions(opts = {}) {
  const ocr = opts.ocr && typeof opts.ocr === "object" ? opts.ocr : {};
  const qualityMode = ocr.qualityMode === "high_accuracy" ? "high_accuracy" : "fast";
  const defaultScale = qualityMode === "high_accuracy" ? 3.1 : 2.05;
  const scale = Number.isFinite(ocr.scale) ? Math.max(1.1, Math.min(4, Number(ocr.scale))) : defaultScale;
  const maskImages = ocr.maskImages === "off" || ocr.maskImages === "none"
    ? "off"
    : ocr.maskImages === "on"
      ? "on"
      : "auto";
  const cropMode = ocr.cropMode === "off" || ocr.cropMode === false
    ? "off"
    : ocr.cropMode === "on" || ocr.cropMode === true
      ? "on"
      : "auto";
  const cropPaddingPx = Number.isFinite(ocr.cropPaddingPx)
    ? Math.max(0, Math.min(120, Number(ocr.cropPaddingPx)))
    : DEFAULT_OCR_OPTIONS.cropPaddingPx;

  return {
    ...DEFAULT_OCR_OPTIONS,
    ...ocr,
    available: ocr.available !== false,
    enabled: ocr.enabled !== false,
    lang: typeof ocr.lang === "string" && ocr.lang.trim() ? ocr.lang.trim() : DEFAULT_OCR_OPTIONS.lang,
    qualityMode,
    scale,
    psm: String(ocr.psm || DEFAULT_OCR_OPTIONS.psm),
    maskImages,
    cropMode,
    cropPaddingPx,
    workerUrl: ocr.workerUrl,
  };
}

function isFileLike(value) {
  return typeof File !== "undefined" && value instanceof File;
}

function sourceHeaderLabel(page) {
  if (page.sourceDecision === "hybrid") return "HYBRID";
  if (page.sourceDecision === "ocr" && !page.ocrText) return "OCR_REQUIRED";
  return page.sourceDecision.toUpperCase();
}

function pageUnsafeReason(page, gateOptions) {
  if (!page) return "";

  const reasons = [];
  if (page.classification?.needsOcr) {
    reasons.push(page.classification.reason);
  } else {
    if ((page.stats?.contaminationScore || 0) >= gateOptions.maxContaminationScore) {
      reasons.push(`contamination score ${page.stats.contaminationScore.toFixed(2)}`);
    }
    if ((page.stats?.completenessConfidence || 0) < gateOptions.minCompletenessConfidence) {
      reasons.push(`completeness confidence ${page.stats.completenessConfidence.toFixed(2)}`);
    }
  }

  return reasons.join(", ");
}

function summarizeBlockedPages(pages) {
  const blockedPages = pages.filter((page) => page.blockedReason);
  if (!blockedPages.length) return undefined;

  const details = blockedPages
    .slice(0, 3)
    .map((page) => `p${page.pageIndex + 1}: ${page.blockedReason}`);

  if (blockedPages.length > 3) {
    details.push(`+${blockedPages.length - 3} more page(s)`);
  }

  return details.join(" | ");
}

function normalizeRawPages(rawPages) {
  return (Array.isArray(rawPages) ? rawPages : [])
    .filter((page) => page && Number.isFinite(page.pageIndex))
    .sort((a, b) => a.pageIndex - b.pageIndex);
}

/**
 * Build the client-side canonical document object from extracted pages.
 *
 * @param {{name:string}} file
 * @param {Array<{pageIndex:number,text:string,rawText?:string,stats:object,userOverride?:'force_native'|'force_ocr',layoutBlocks?:Array,imageRegions?:Array,textRegions?:Array,contaminatedSpans?:Array,qualityFlags?:Array,ocrText?:string,ocrMeta?:object}>} rawPages
 * @param {{forceOcrAll?:boolean,ocr?:object,gate?:object,classifier?:object}} [opts]
 */
export function buildPdfDocumentModel(file, rawPages, opts = {}) {
  const gateOptions = normalizeGateOptions(opts.gate);
  const ocrOptions = normalizeOcrOptions(opts);
  const forceOcrAll = Boolean(opts.forceOcrAll);

  const pages = [];
  const pageStartOffsets = [];
  let fullText = "";

  let lowConfidencePages = 0;
  let contaminatedPages = 0;

  for (const rawPage of normalizeRawPages(rawPages)) {
    const rawText = typeof rawPage.rawText === "string" ? rawPage.rawText : (rawPage.text || "");
    const nativeText = typeof rawPage.text === "string" ? rawPage.text : rawText;
    const pageStats = { ...(rawPage.stats || {}) };

    const classification = classifyPage(pageStats, nativeText, {
      thresholds: opts.classifier,
    });
    pageStats.completenessConfidence = classification.completenessConfidence;

    if (classification.completenessConfidence < gateOptions.minCompletenessConfidence) {
      lowConfidencePages += 1;
    }
    if ((pageStats.contaminationScore || 0) >= gateOptions.maxContaminationScore) {
      contaminatedPages += 1;
    }

    const provisionalPage = {
      classification,
      userOverride: rawPage.userOverride,
    };
    const resolvedSource = resolvePageSource(provisionalPage, { forceOcrAll });

    const fusion = arbitratePageText({
      nativeText,
      ocrText: rawPage.ocrText,
      requestedSource: resolvedSource.source,
      ocrAvailable: ocrOptions.available && ocrOptions.enabled,
      classification,
      stats: pageStats,
    });

    let sourceDecision = fusion.sourceDecision;
    if (resolvedSource.source === "ocr" && !rawPage.ocrText) {
      sourceDecision = "ocr";
    }

    const unsafeEval = isUnsafeNativePage(pageStats, nativeText, {
      minCompletenessConfidence: gateOptions.minCompletenessConfidence,
      maxContaminationScore: gateOptions.maxContaminationScore,
      thresholds: opts.classifier,
    });

    let blockedReason;
    if (!ocrOptions.available && gateOptions.hardBlockWhenUnsafeWithoutOcr && unsafeEval.unsafe) {
      blockedReason = `unsafe native extraction (${pageUnsafeReason({ stats: pageStats, classification }, gateOptions)})`;
    }

    const qualityFlags = new Set([
      ...(Array.isArray(rawPage.qualityFlags) ? rawPage.qualityFlags : []),
      ...(Array.isArray(classification.qualityFlags) ? classification.qualityFlags : []),
    ]);
    if (blockedReason) qualityFlags.add("BLOCKED_UNSAFE_NATIVE");

    const pageText = sourceDecision === "ocr" && typeof rawPage.ocrText === "string"
      ? rawPage.ocrText
      : fusion.text || nativeText;

    const page = {
      pageIndex: rawPage.pageIndex,
      text: pageText,
      rawText,
      stats: pageStats,
      classification,
      userOverride: rawPage.userOverride,
      source: sourceDecision === "native" ? "native" : "ocr",
      sourceDecision,
      sourceReason: resolvedSource.reason,
      layoutBlocks: Array.isArray(rawPage.layoutBlocks) ? rawPage.layoutBlocks : [],
      imageRegions: Array.isArray(rawPage.imageRegions) ? rawPage.imageRegions : [],
      textRegions: Array.isArray(rawPage.textRegions) ? rawPage.textRegions : [],
      contaminatedSpans: Array.isArray(rawPage.contaminatedSpans) ? rawPage.contaminatedSpans : [],
      qualityFlags: [...qualityFlags],
      blockedReason,
      ocrText: typeof rawPage.ocrText === "string" ? rawPage.ocrText : undefined,
      ocrMeta: rawPage.ocrMeta && typeof rawPage.ocrMeta === "object" ? rawPage.ocrMeta : undefined,
    };

    const header = `\n===== PAGE ${page.pageIndex + 1} (${sourceHeaderLabel(page)}) =====\n`;
    pageStartOffsets.push(fullText.length + header.length);
    fullText += header;
    fullText += page.text || "";
    fullText += "\n";

    pages.push(page);
  }

  const requiresOcr = pages.some((page) => page.classification?.needsOcr || page.sourceDecision !== "native");
  const blockReason = summarizeBlockedPages(pages);
  const blocked = Boolean(blockReason);
  const gate = {
    status: blocked ? "blocked" : "pass",
    blocked,
    reason: blockReason,
    ocrAvailable: ocrOptions.available && ocrOptions.enabled,
    requiresOcr,
    thresholds: gateOptions,
  };

  return {
    fileName: file.name,
    pages,
    fullText,
    pageStartOffsets,
    requiresOcr,
    blocked,
    blockReason,
    qualitySummary: {
      lowConfidencePages,
      contaminatedPages,
    },
    gate,
  };
}

/**
 * Select page indices that require OCR from the current document decision state.
 *
 * @param {{pages:Array<{pageIndex:number,sourceDecision?:string,classification?:{needsOcr?:boolean}}>}|null} documentModel
 * @param {{forceOcrAll?:boolean}} [opts]
 */
export function selectPagesForOcr(documentModel, opts = {}) {
  const pages = Array.isArray(documentModel?.pages) ? documentModel.pages : [];
  if (!pages.length) return [];
  if (opts.forceOcrAll) {
    return pages.map((page) => page.pageIndex).filter((index) => Number.isFinite(index));
  }

  return pages
    .filter((page) => page.sourceDecision === "ocr" || page.classification?.needsOcr)
    .map((page) => page.pageIndex)
    .filter((index) => Number.isFinite(index));
}

export function applyOcrResultsToRawPages(rawPages, ocrPages) {
  const map = new Map();
  for (const page of normalizeRawPages(rawPages)) {
    map.set(page.pageIndex, { ...page });
  }

  for (const ocrPage of Array.isArray(ocrPages) ? ocrPages : []) {
    if (!Number.isFinite(ocrPage?.pageIndex)) continue;
    const existing = map.get(ocrPage.pageIndex);
    if (!existing) continue;
    const ocrText = typeof ocrPage.text === "string" ? ocrPage.text : "";
    map.set(ocrPage.pageIndex, {
      ...existing,
      ocrText,
      ocrMeta: ocrPage.meta && typeof ocrPage.meta === "object" ? ocrPage.meta : undefined,
    });
  }

  return [...map.values()].sort((a, b) => a.pageIndex - b.pageIndex);
}

async function runOcrPass(file, pageIndexes, opts, push) {
  if (!pageIndexes.length) return [];

  const ocrOptions = normalizeOcrOptions(opts);
  const workerUrl = ocrOptions.workerUrl || new URL("../workers/ocr.worker.js", import.meta.url);
  const worker = new Worker(workerUrl, { type: "module" });
  const pdfBytes = await file.arrayBuffer();
  const rawPages = normalizeRawPages(opts.rawPages);
  const rawPageByIndex = new Map(rawPages.map((page) => [page.pageIndex, page]));
  const pageHints = pageIndexes.map((pageIndex) => {
    const rawPage = rawPageByIndex.get(pageIndex);
    if (!rawPage) return { pageIndex };
    return {
      pageIndex,
      stats: rawPage.stats && typeof rawPage.stats === "object" ? rawPage.stats : undefined,
      imageRegions: Array.isArray(rawPage.imageRegions) ? rawPage.imageRegions : [],
      textRegions: Array.isArray(rawPage.textRegions) ? rawPage.textRegions : [],
    };
  });

  return new Promise((resolve, reject) => {
    let done = false;
    const results = [];

    const finish = (error) => {
      if (done) return;
      done = true;
      worker.terminate();
      if (error) reject(error);
      else resolve(results);
    };

    worker.onmessage = (event) => {
      const data = event.data || {};

      if (data.type === "ocr_stage") {
        push({
          kind: "stage",
          stage: data.stage,
          pageIndex: Number.isFinite(data.sourcePageIndex)
            ? Number(data.sourcePageIndex)
            : Number(data.pageIndex) || 0,
          totalPages: Number(data.totalPages) || pageIndexes.length,
        });
        return;
      }
      if (data.type === "ocr_progress") {
        push({
          kind: "ocr_progress",
          completedPages: Number(data.completedPages) || 0,
          totalPages: Number(data.totalPages) || pageIndexes.length,
        });
        return;
      }
      if (data.type === "ocr_status") {
        push({
          kind: "ocr_status",
          status: data.status,
          progress: Number.isFinite(data.progress) ? data.progress : 0,
        });
        return;
      }
      if (data.type === "ocr_page") {
        const page = data.page || {};
        results.push(page);
        push({
          kind: "ocr_page",
          page,
        });
        return;
      }
      if (data.type === "ocr_done") {
        const pages = Array.isArray(data.pages) ? data.pages : [];
        if (pages.length > results.length) {
          results.length = 0;
          results.push(...pages);
        }
        finish();
        return;
      }
      if (data.type === "error") {
        finish(new Error(data.error || "OCR worker failed"));
      }
    };

    worker.onerror = (event) => {
      const error = event instanceof ErrorEvent && event.error
        ? event.error
        : new Error(event.message || "OCR worker error");
      finish(error);
    };

    worker.postMessage({
      type: "ocr_extract",
      pdfBytes,
      pageIndexes,
      pageHints,
      options: {
        lang: ocrOptions.lang,
        qualityMode: ocrOptions.qualityMode,
        scale: ocrOptions.scale,
        psm: ocrOptions.psm,
        maskImages: ocrOptions.maskImages,
        cropMode: ocrOptions.cropMode,
        cropPaddingPx: ocrOptions.cropPaddingPx,
      },
    }, [pdfBytes]);
  });
}

async function* runWorkerExtraction(file, opts = {}, messageType = "extract_adaptive") {
  if (!isFileLike(file)) {
    throw new Error("PDF extraction expects a File");
  }

  const workerUrl = opts.workerUrl || new URL("../workers/pdf.worker.js", import.meta.url);
  const worker = new Worker(workerUrl, { type: "module" });
  const pdfBytes = await file.arrayBuffer();

  const queue = [];
  let wake = null;
  let finished = false;
  let fatalError = null;

  const push = (event) => {
    queue.push(event);
    if (wake) {
      const next = wake;
      wake = null;
      next();
    }
  };

  worker.onmessage = (event) => {
    const data = event.data || {};
    if (data.type === "stage") {
      push({
        kind: "stage",
        stage: data.stage,
        pageIndex: Number(data.pageIndex) || 0,
        totalPages: Number(data.totalPages) || 0,
      });
      return;
    }
    if (data.type === "progress") {
      push({
        kind: "progress",
        completedPages: data.completedPages,
        totalPages: data.totalPages,
      });
      return;
    }
    if (data.type === "page") {
      push({ kind: "page", page: data.page });
      return;
    }
    if (data.type === "done") {
      (async () => {
        try {
          let pages = normalizeRawPages(data.pages);
          let document = buildPdfDocumentModel(file, pages, opts);

          const ocrOptions = normalizeOcrOptions(opts);
          const shouldRunOcr = messageType === "extract_adaptive" && ocrOptions.available && ocrOptions.enabled;
          const ocrTargets = shouldRunOcr ? selectPagesForOcr(document, { forceOcrAll: opts.forceOcrAll }) : [];

          if (ocrTargets.length) {
            push({
              kind: "stage",
              stage: "ocr_prepare",
              pageIndex: 0,
              totalPages: ocrTargets.length,
            });
            try {
              const ocrPages = await runOcrPass(file, ocrTargets, { ...opts, rawPages: pages }, push);
              pages = applyOcrResultsToRawPages(pages, ocrPages);
              document = buildPdfDocumentModel(file, pages, {
                ...opts,
                ocr: {
                  ...ocrOptions,
                  available: true,
                  enabled: true,
                },
              });
            } catch (ocrError) {
              push({
                kind: "stage",
                stage: "ocr_failed",
                pageIndex: 0,
                totalPages: ocrTargets.length,
              });
              const message = ocrError instanceof Error ? ocrError.message : String(ocrError);
              push({
                kind: "ocr_error",
                error: message,
              });
              document = buildPdfDocumentModel(file, pages, {
                ...opts,
                ocr: {
                  ...ocrOptions,
                  available: false,
                  enabled: false,
                },
              });
            }
          }

          push({
            kind: "done",
            pages,
            document,
            gate: document.gate,
          });
        } catch (error) {
          fatalError = error instanceof Error ? error : new Error(String(error));
        } finally {
          finished = true;
          push({ kind: "__closed__" });
        }
      })();
      return;
    }
    if (data.type === "error") {
      fatalError = new Error(data.error || "PDF extraction worker failed");
      finished = true;
      push({ kind: "__closed__" });
    }
  };

  worker.onerror = (event) => {
    fatalError = event instanceof ErrorEvent && event.error
      ? event.error
      : new Error(event.message || "Worker error");
    finished = true;
    push({ kind: "__closed__" });
  };

  worker.postMessage({
    type: messageType,
    pdfBytes,
    options: {
      lineYTolerance: Number.isFinite(opts.lineYTolerance) ? opts.lineYTolerance : undefined,
      imageRegionMargin: Number.isFinite(opts.imageRegionMargin) ? opts.imageRegionMargin : undefined,
      dropContaminatedNumericTokens: opts.dropContaminatedNumericTokens !== false,
    },
  }, [pdfBytes]);

  try {
    while (!finished || queue.length) {
      if (!queue.length) {
        await new Promise((resolve) => {
          wake = resolve;
        });
      }

      while (queue.length) {
        const next = queue.shift();
        if (!next || next.kind === "__closed__") continue;
        yield next;
      }
    }

    if (fatalError) throw fatalError;
  } finally {
    worker.terminate();
  }
}

/**
 * Adaptive extraction pipeline with layout-aware analysis + OCR and safety gate output.
 *
 * @param {File} file
 * @param {{workerUrl?:URL,forceOcrAll?:boolean,ocr?:object,gate?:object}} [opts]
 */
export async function* extractPdfAdaptive(file, opts = {}) {
  yield* runWorkerExtraction(file, opts, "extract_adaptive");
}

/**
 * Legacy native extraction generator. Kept for compatibility.
 *
 * @param {File} file
 * @param {object} [opts]
 */
export async function* extractPdfNative(file, opts = {}) {
  const nativeOpts = {
    ...opts,
    ocr: {
      ...normalizeOcrOptions(opts),
      ...(opts.ocr || {}),
      available: false,
      enabled: false,
    },
    gate: {
      ...normalizeGateOptions(opts.gate),
      hardBlockWhenUnsafeWithoutOcr: false,
    },
  };

  for await (const event of runWorkerExtraction(file, nativeOpts, "extract")) {
    if (event.kind === "stage") continue;
    if (event.kind === "done") {
      yield { kind: "done", pages: event.pages };
      continue;
    }
    yield event;
  }
}
