import { clamp01 } from "./layoutAnalysis.js";

function normalizeLines(text) {
  if (typeof text !== "string") return [];
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function safeText(value) {
  return typeof value === "string" ? value : "";
}

function hasText(value) {
  return safeText(value).trim().length > 0;
}

function normalizeLineKey(line) {
  return String(line || "")
    .toLowerCase()
    .replace(/[^a-z0-9%:/.,\- ]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function tokenizeForOverlap(line) {
  return normalizeLineKey(line)
    .split(/\s+/)
    .filter((token) => token.length >= 3 && /[a-z]/.test(token));
}

function hasHighTokenOverlap(line, nativeTokenSets) {
  const tokens = tokenizeForOverlap(line);
  if (tokens.length < 4) return false;

  const tokenSet = new Set(tokens);
  for (const nativeSet of nativeTokenSets) {
    if (!nativeSet || nativeSet.size < 4) continue;
    let overlap = 0;
    for (const token of tokenSet) {
      if (nativeSet.has(token)) overlap += 1;
    }
    const minSize = Math.min(tokenSet.size, nativeSet.size);
    if (minSize > 0 && overlap / minSize >= 0.75) return true;
  }
  return false;
}

function hasClinicalPattern(line) {
  return (
    /\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/.test(line) ||
    /\b\d{1,2}:\d{2}(?::\d{2})?\b/.test(line) ||
    /\b[A-Z]\d{1,2}(?:\.\d+)?\b/.test(line) ||
    /\b(CPT|ICD|MRN|DOB|MD|AM|PM)\b/i.test(line)
  );
}

function isLikelyOcrNoiseLine(line, mode = "augment") {
  const trimmed = String(line || "").trim();
  if (!trimmed) return true;
  if (trimmed.length < 2) return true;

  const chars = trimmed.length;
  const letters = (trimmed.match(/[A-Za-z]/g) || []).length;
  const lower = (trimmed.match(/[a-z]/g) || []).length;
  const digits = (trimmed.match(/\d/g) || []).length;
  const punctuation = (trimmed.match(/[^A-Za-z0-9\s]/g) || []).length;
  const oZero = (trimmed.match(/[O0o]/g) || []).length;
  const tokens = trimmed.split(/\s+/).filter(Boolean);
  const singleCharTokenRatio = tokens.length
    ? tokens.filter((token) => token.length <= 1).length / tokens.length
    : 1;
  const symbolicTokenRatio = tokens.length
    ? tokens.filter((token) => /^[^A-Za-z0-9]+$/.test(token) || /^[O0o]+$/.test(token)).length / tokens.length
    : 1;
  const longWordCount = tokens.filter((token) => /[A-Za-z]{4,}/.test(token)).length;
  const alphaNumRatio = (letters + digits) / Math.max(1, chars);
  const punctuationRatio = punctuation / Math.max(1, chars);
  const oZeroRatio = oZero / Math.max(1, chars);
  const clinicalPattern = hasClinicalPattern(trimmed);

  if (/(.)\1{6,}/.test(trimmed)) return true;
  if (chars >= 10 && alphaNumRatio < 0.34) return true;
  if (chars >= 12 && punctuationRatio > 0.3 && !clinicalPattern) return true;
  if (chars >= 10 && oZeroRatio > 0.42 && lower <= 1 && !clinicalPattern) return true;
  if (tokens.length >= 8 && singleCharTokenRatio > 0.5) return true;
  if (tokens.length >= 6 && symbolicTokenRatio > 0.45) return true;
  if (lower === 0 && longWordCount < 2 && !clinicalPattern) return true;

  if (mode === "augment") {
    if (lower === 0 && !clinicalPattern) return true;
    if (tokens.length < 3 && !clinicalPattern) return true;
  }

  return false;
}

export function sanitizeOcrText(ocrText, opts = {}) {
  const mode = opts.mode === "augment" ? "augment" : "full";
  const lines = normalizeLines(ocrText);
  const out = [];
  const seen = new Set();

  for (const line of lines) {
    if (isLikelyOcrNoiseLine(line, mode)) continue;
    const key = normalizeLineKey(line);
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(line.trim());
  }

  return out.join("\n");
}

export function mergeNativeAndOcrText(nativeText, ocrText, opts = {}) {
  const mode = opts.mode === "augment" ? "augment" : "full";
  const nativeLines = normalizeLines(nativeText);
  const ocrLines = normalizeLines(sanitizeOcrText(ocrText, { mode }));
  const seen = new Set();
  const nativeTokenSets = [];
  const merged = [];

  for (const line of nativeLines) {
    const key = normalizeLineKey(line);
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(line);
    nativeTokenSets.push(new Set(tokenizeForOverlap(line)));
  }

  for (const line of ocrLines) {
    const key = normalizeLineKey(line);
    if (seen.has(key)) continue;
    if (hasHighTokenOverlap(line, nativeTokenSets)) continue;
    seen.add(key);
    merged.push(line);
  }

  return merged.join("\n");
}

/**
 * Arbitrates page text/source between native extraction and OCR output.
 *
 * @param {{
 * nativeText?:string,
 * ocrText?:string,
 * requestedSource?:'native'|'ocr',
 * ocrAvailable?:boolean,
 * classification?:{needsOcr?:boolean},
 * stats?:{contaminationScore?:number,completenessConfidence?:number}
 * }} input
 * @returns {{sourceDecision:'native'|'ocr'|'hybrid',text:string,reason:string,confidence:number,blocked:boolean}}
 */
export function arbitratePageText(input = {}) {
  const nativeText = safeText(input.nativeText);
  const rawOcrText = safeText(input.ocrText);
  const requestedSource = input.requestedSource === "ocr" ? "ocr" : "native";
  const ocrAvailable = Boolean(input.ocrAvailable);

  const contaminationScore = clamp01(Number(input.stats?.contaminationScore) || 0);
  const completenessConfidence = clamp01(Number(input.stats?.completenessConfidence) || 0);

  const nativeLen = nativeText.trim().length;
  const sanitizedOcrText = sanitizeOcrText(rawOcrText, {
    mode: nativeLen > 0 ? "augment" : "full",
  });
  const ocrText = hasText(sanitizedOcrText) ? sanitizedOcrText : rawOcrText;
  const ocrLen = ocrText.trim().length;
  const nativePresent = nativeLen > 0;
  const ocrPresent = ocrLen > 0;

  if (!ocrAvailable) {
    const blocked = requestedSource === "ocr" || Boolean(input.classification?.needsOcr);
    return {
      sourceDecision: "native",
      text: nativeText,
      reason: blocked
        ? "OCR requested/required but unavailable"
        : "using native extraction",
      confidence: clamp01(completenessConfidence * (1 - contaminationScore * 0.35)),
      blocked,
    };
  }

  if (requestedSource === "native" && nativePresent) {
    return {
      sourceDecision: "native",
      text: nativeText,
      reason: "native extraction requested",
      confidence: clamp01(Math.max(0.45, completenessConfidence)),
      blocked: false,
    };
  }

  if (!nativePresent && ocrPresent) {
    return {
      sourceDecision: "ocr",
      text: ocrText,
      reason: "native text missing; using OCR",
      confidence: 0.8,
      blocked: false,
    };
  }

  if (nativePresent && !ocrPresent) {
    return {
      sourceDecision: "native",
      text: nativeText,
      reason: "OCR output unavailable; using native fallback",
      confidence: clamp01(completenessConfidence * 0.85),
      blocked: Boolean(input.classification?.needsOcr),
    };
  }

  if (!nativePresent && !ocrPresent) {
    return {
      sourceDecision: "native",
      text: "",
      reason: "no extractable text available",
      confidence: 0,
      blocked: true,
    };
  }

  const ocrMuchLonger = ocrLen > nativeLen * 1.25;
  const contaminationHigh = contaminationScore >= 0.12;

  if (ocrMuchLonger && contaminationHigh) {
    return {
      sourceDecision: "hybrid",
      text: mergeNativeAndOcrText(nativeText, ocrText, { mode: "augment" }),
      reason: "hybrid merge: OCR recovered likely missing content on contaminated native text",
      confidence: 0.84,
      blocked: false,
    };
  }

  if (ocrMuchLonger) {
    return {
      sourceDecision: "ocr",
      text: ocrText,
      reason: "OCR recovered significantly more content",
      confidence: 0.82,
      blocked: false,
    };
  }

  return {
    sourceDecision: "hybrid",
    text: mergeNativeAndOcrText(nativeText, ocrText, { mode: "augment" }),
    reason: "hybrid merge for traceable native+OCR coverage",
    confidence: 0.78,
    blocked: false,
  };
}
