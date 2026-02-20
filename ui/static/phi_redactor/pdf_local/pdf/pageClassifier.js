import { clamp01, estimateCompletenessConfidence } from "./layoutAnalysis.js";

export const DEFAULT_CLASSIFIER_THRESHOLDS = Object.freeze({
  charCount: 80,
  singleCharItemRatio: 0.55,
  nonPrintableRatio: 0.08,
  alphaRatioMin: 0.38,
  medianTokenLenMin: 2.2,
  imageOpCount: 5,
  imageTextCharMax: 1800,
  overlapRatio: 0.08,
  contaminationScore: 0.24,
  completenessConfidence: 0.72,
  classifierDecisionScore: 0.5,
  nativeTextDensityBypass: 0.0022,
  nativeTextDensityCharFloor: 900,
  nativeTextDensityAlphaFloor: 0.55,
});

function computeTextQualityStats(text) {
  const trimmed = typeof text === "string" ? text.trim() : "";
  if (!trimmed) {
    return {
      alphaRatio: 0,
      medianTokenLen: 0,
    };
  }

  const tokens = trimmed.split(/\s+/).filter(Boolean);
  const chars = [...trimmed];
  const alphaCount = chars.filter((ch) => /[A-Za-z]/.test(ch)).length;

  const tokenLens = tokens
    .map((token) => token.replace(/^[^A-Za-z0-9]+|[^A-Za-z0-9]+$/g, ""))
    .filter(Boolean)
    .map((token) => token.length)
    .sort((a, b) => a - b);
  const mid = Math.floor(tokenLens.length / 2);
  const medianTokenLen = tokenLens.length
    ? (tokenLens.length % 2 ? tokenLens[mid] : (tokenLens[mid - 1] + tokenLens[mid]) / 2)
    : 0;

  return {
    alphaRatio: chars.length ? clamp01(alphaCount / chars.length) : 0,
    medianTokenLen,
  };
}

function addTextQualitySignals(scoreState, textStats, thresholds) {
  const { reasons, qualityFlags } = scoreState;
  let score = scoreState.score;

  if (textStats.alphaRatio < thresholds.alphaRatioMin) {
    score += 0.15;
    reasons.push(`low alpha ratio (${textStats.alphaRatio.toFixed(2)})`);
    qualityFlags.push("LOW_ALPHA_RATIO");
  }

  if (textStats.medianTokenLen > 0 && textStats.medianTokenLen < thresholds.medianTokenLenMin) {
    score += 0.1;
    reasons.push(`short median token length (${textStats.medianTokenLen.toFixed(1)})`);
    qualityFlags.push("SHORT_TOKENS");
  }

  return score;
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
 * @param {{charCount:number,itemCount:number,nonPrintableRatio:number,singleCharItemRatio:number,imageOpCount?:number,overlapRatio?:number,contaminationScore?:number,completenessConfidence?:number,excludedTokenRatio?:number,pageArea?:number,nativeTextDensity?:number}} stats
 * @param {string} text
 * @param {{thresholds?:Partial<typeof DEFAULT_CLASSIFIER_THRESHOLDS>}} [opts]
 * @returns {{needsOcr:boolean,reason:string,confidence:number,qualityFlags:string[],completenessConfidence:number,nativeTextDensity:number}}
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
  const pageArea = Math.max(0, Number(safeStats.pageArea) || 0);
  const nativeTextDensity = Number.isFinite(safeStats.nativeTextDensity)
    ? Math.max(0, Number(safeStats.nativeTextDensity))
    : (pageArea > 0 ? Math.max(0, charCount / pageArea) : 0);
  const textStats = computeTextQualityStats(text);
  const completenessConfidence = Number.isFinite(safeStats.completenessConfidence)
    ? clamp01(safeStats.completenessConfidence)
    : estimateCompletenessConfidence(safeStats, {
      excludedTokenRatio: Number(safeStats.excludedTokenRatio) || 0,
    });

  const nativeDensityBypass = pageArea > 0 &&
    charCount >= thresholds.nativeTextDensityCharFloor &&
    textStats.alphaRatio >= thresholds.nativeTextDensityAlphaFloor &&
    nativeTextDensity >= thresholds.nativeTextDensityBypass;
  if (nativeDensityBypass) {
    return {
      needsOcr: false,
      reason: `high native text density (${nativeTextDensity.toFixed(4)} chars/unit^2)`,
      confidence: clamp01(Math.max(0.85, completenessConfidence)),
      qualityFlags: ["NATIVE_DENSE_TEXT"],
      completenessConfidence,
      nativeTextDensity,
    };
  }

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

  score = addTextQualitySignals({ score, reasons, qualityFlags }, textStats, thresholds);

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
    nativeTextDensity,
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
  if (classification.qualityFlags?.includes("NATIVE_DENSE_TEXT")) {
    return {
      unsafe: false,
      classification,
      contaminationScore: clamp01(Number(stats?.contaminationScore) || 0),
      completenessConfidence: classification.completenessConfidence,
    };
  }
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
