import { clamp01, estimateCompletenessConfidence } from "./layoutAnalysis.js";

export const DEFAULT_CLASSIFIER_THRESHOLDS = Object.freeze({
  charCount: 80,
  singleCharItemRatio: 0.55,
  nonPrintableRatio: 0.08,
  garbageRatio: 0.35,
  imageOpCount: 5,
  imageTextCharMax: 1800,
  overlapRatio: 0.08,
  contaminationScore: 0.24,
  completenessConfidence: 0.72,
  classifierDecisionScore: 0.5,
});

function computeGarbageRatio(text) {
  const trimmed = typeof text === "string" ? text.trim() : "";
  if (!trimmed) return 1;

  const tokens = trimmed.split(/\s+/).filter(Boolean);
  if (!tokens.length) return 1;

  let bad = 0;
  for (const token of tokens) {
    const clean = token.replace(/[\u2010-\u2015]/g, "-");
    const isShortSymbol = clean.length <= 2 && /^[^A-Za-z0-9]+$/.test(clean);
    const isLongNoise = /^[^A-Za-z0-9]{3,}$/.test(clean);
    if (isShortSymbol || isLongNoise) bad += 1;
  }

  return bad / tokens.length;
}

function mergeThresholds(override) {
  if (!override || typeof override !== "object") return DEFAULT_CLASSIFIER_THRESHOLDS;
  return {
    ...DEFAULT_CLASSIFIER_THRESHOLDS,
    ...override,
  };
}

/**
 * Decide whether a page likely requires OCR.
 *
 * @param {{charCount:number,itemCount:number,nonPrintableRatio:number,singleCharItemRatio:number,imageOpCount?:number,overlapRatio?:number,contaminationScore?:number,completenessConfidence?:number,excludedTokenRatio?:number}} stats
 * @param {string} text
 * @param {{thresholds?:Partial<typeof DEFAULT_CLASSIFIER_THRESHOLDS>}} [opts]
 * @returns {{needsOcr:boolean,reason:string,confidence:number,qualityFlags:string[],completenessConfidence:number}}
 */
export function classifyPage(stats, text, opts = {}) {
  const thresholds = mergeThresholds(opts.thresholds);
  const safeStats = stats || {};

  const charCount = Number(safeStats.charCount) || 0;
  const singleCharItemRatio = clamp01(Number(safeStats.singleCharItemRatio) || 0);
  const nonPrintableRatio = clamp01(Number(safeStats.nonPrintableRatio) || 0);
  const imageOpCount = Math.max(0, Number(safeStats.imageOpCount) || 0);
  const overlapRatio = clamp01(Number(safeStats.overlapRatio) || 0);
  const contaminationScore = clamp01(Number(safeStats.contaminationScore) || 0);
  const garbageRatio = computeGarbageRatio(text);
  const completenessConfidence = Number.isFinite(safeStats.completenessConfidence)
    ? clamp01(safeStats.completenessConfidence)
    : estimateCompletenessConfidence(safeStats, {
      excludedTokenRatio: Number(safeStats.excludedTokenRatio) || 0,
    });

  let score = 0;
  const reasons = [];
  const qualityFlags = [];

  if (charCount < thresholds.charCount) {
    score += 0.35;
    reasons.push(`low char count (${charCount})`);
    qualityFlags.push("SPARSE_TEXT");
  }

  if (singleCharItemRatio >= thresholds.singleCharItemRatio) {
    score += 0.23;
    reasons.push(`high single-char item ratio (${singleCharItemRatio.toFixed(2)})`);
    qualityFlags.push("CHAR_FRAGMENTATION");
  }

  if (nonPrintableRatio >= thresholds.nonPrintableRatio) {
    score += 0.2;
    reasons.push(`high non-printable ratio (${nonPrintableRatio.toFixed(2)})`);
    qualityFlags.push("NON_PRINTABLE_TEXT");
  }

  if (garbageRatio >= thresholds.garbageRatio) {
    score += 0.15;
    reasons.push(`garbage-text ratio (${garbageRatio.toFixed(2)})`);
    qualityFlags.push("GARBAGE_TEXT");
  }

  if (imageOpCount >= thresholds.imageOpCount && charCount <= thresholds.imageTextCharMax) {
    score += 0.32;
    reasons.push(`image-heavy page (${imageOpCount} image ops) with limited text (${charCount} chars)`);
    qualityFlags.push("IMAGE_HEAVY");
  }

  if (overlapRatio >= thresholds.overlapRatio) {
    score += 0.31;
    reasons.push(`image/text overlap ratio (${overlapRatio.toFixed(2)})`);
    qualityFlags.push("IMAGE_TEXT_OVERLAP");
  }

  if (contaminationScore >= thresholds.contaminationScore) {
    score += 0.33;
    reasons.push(`contamination score (${contaminationScore.toFixed(2)})`);
    qualityFlags.push("CONTAMINATION_RISK");
  }

  if (completenessConfidence < thresholds.completenessConfidence) {
    score += 0.45;
    reasons.push(`low completeness confidence (${completenessConfidence.toFixed(2)})`);
    qualityFlags.push("LOW_COMPLETENESS");
  }

  const needsOcr = score >= thresholds.classifierDecisionScore;
  const confidence = clamp01(needsOcr ? score : 1 - score);

  return {
    needsOcr,
    reason: reasons.length ? reasons.join(", ") : "layout-safe native text",
    confidence,
    qualityFlags: [...new Set(qualityFlags)],
    completenessConfidence,
  };
}

/**
 * Evaluate whether native-only extraction should be considered unsafe.
 *
 * @param {object} stats
 * @param {string} text
 * @param {{minCompletenessConfidence?:number,maxContaminationScore?:number,thresholds?:Partial<typeof DEFAULT_CLASSIFIER_THRESHOLDS>}} [opts]
 */
export function isUnsafeNativePage(stats, text, opts = {}) {
  const thresholds = mergeThresholds(opts.thresholds);
  const classification = classifyPage(stats, text, { thresholds });
  const maxContaminationScore = Number.isFinite(opts.maxContaminationScore)
    ? clamp01(opts.maxContaminationScore)
    : thresholds.contaminationScore;
  const minCompletenessConfidence = Number.isFinite(opts.minCompletenessConfidence)
    ? clamp01(opts.minCompletenessConfidence)
    : thresholds.completenessConfidence;

  const contaminationScore = clamp01(Number(stats?.contaminationScore) || 0);
  const completenessConfidence = classification.completenessConfidence;

  const unsafe = Boolean(
    classification.needsOcr ||
    contaminationScore >= maxContaminationScore ||
    completenessConfidence < minCompletenessConfidence,
  );

  return {
    unsafe,
    classification,
    contaminationScore,
    completenessConfidence,
  };
}

/**
 * Resolve the requested source for a page after user/global overrides.
 *
 * @param {{classification:{needsOcr:boolean}, userOverride?:'force_native'|'force_ocr'}} page
 * @param {{forceOcrAll?:boolean}} [opts]
 * @returns {{source:'native'|'ocr', reason:string}}
 */
export function resolvePageSource(page, opts = {}) {
  if (opts.forceOcrAll) {
    return { source: "ocr", reason: "OCR all pages enabled" };
  }
  if (page.userOverride === "force_ocr") {
    return { source: "ocr", reason: "user override: force OCR" };
  }
  if (page.userOverride === "force_native") {
    return { source: "native", reason: "user override: force native" };
  }
  if (page.classification?.needsOcr) {
    return { source: "ocr", reason: page.classification.reason };
  }
  return { source: "native", reason: page.classification?.reason || "layout-safe native text" };
}
