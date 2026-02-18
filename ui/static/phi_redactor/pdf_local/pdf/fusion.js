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

function isLikelyImageCaptionLine(line) {
  const text = String(line || "").trim();
  if (!text || text.length > 48) return false;
  if (/[.:;%]/.test(text)) return false;

  const tokens = text.split(/\s+/).filter(Boolean);
  if (tokens.length < 2 || tokens.length > 6) return false;

  const anatomyTokenPattern = /^(left|right|upper|lower|lobe|mainstem|entrance|segment|bronchus|airway|LUL|LLL|RUL|RLL)$/i;
  const anatomyCount = tokens.filter((token) => anatomyTokenPattern.test(token)).length;
  if (anatomyCount < 2) return false;

  const allAnatomyTokens = tokens.every((token) => anatomyTokenPattern.test(token));
  return allAnatomyTokens;
}

function pruneCaptionNoiseFromNativeText(nativeText) {
  return normalizeLines(nativeText)
    .filter((line) => !isLikelyImageCaptionLine(line))
    .join("\n");
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
    /\b[A-Z](?!0{2,3}\b)\d{2,3}(?:\.\d+)?\b/.test(line) ||
    /\b\d+(?:mm|cm|mg|ml|%)\b/i.test(line) ||
    /\b(CPT|ICD|MRN|DOB|MD|AM|PM)\b/i.test(line)
  );
}

function normalizeToken(token) {
  return String(token || "")
    .replace(/^[^A-Za-z0-9]+/, "")
    .replace(/[^A-Za-z0-9]+$/, "");
}

function tokenHasClinicalSignal(token) {
  const t = normalizeToken(token);
  if (!t) return false;
  if (/\d+(?:mm|cm|mg|ml|%)$/i.test(t)) return true;
  if (/^[A-Z](?!0{2,3}$)\d{2,3}(?:\.\d+)?$/.test(t)) return true;
  if (/^\d{1,2}\/\d{1,2}\/\d{2,4}$/.test(t)) return true;
  if (/^(ICD|CPT|MRN|DOB|MD|IV|LUL|LLL|RUL|RLL)$/i.test(t)) return true;
  return false;
}

function tokenLooksNarrative(token) {
  const t = normalizeToken(token);
  if (!t) return false;
  return /[a-z]{2,}/.test(t) || tokenHasClinicalSignal(t);
}

function tokenLooksNoisy(token) {
  const t = normalizeToken(token);
  if (!t) return true;
  if (tokenHasClinicalSignal(t)) return false;
  if (/[a-z]{2,}/.test(t)) return false;
  if (/^[O0CcoIl1]+$/.test(t) && t.length >= 2) return true;
  if (/^[A-Z0-9]{3,}$/.test(t) && /[0-9]/.test(t) && /[O0C]/.test(t)) return true;
  if (/^[A-Z]{1,2}$/.test(t) && !/^(AM|PM|MD|IV)$/i.test(t)) return true;
  if (/^\d{1,3}$/.test(t)) return true;
  return false;
}

function findNarrativeBoundary(tokens, direction = "start") {
  if (!tokens.length) return 0;

  if (direction === "start") {
    for (let i = 0; i < tokens.length; i += 1) {
      const window = tokens.slice(i, i + 6);
      const informative = window.filter((token) => tokenLooksNarrative(token)).length;
      const noisy = window.filter((token) => tokenLooksNoisy(token)).length;
      if (informative >= 3 && informative > noisy) return i;
    }
    return 0;
  }

  for (let i = tokens.length - 1; i >= 0; i -= 1) {
    const window = tokens.slice(Math.max(0, i - 5), i + 1);
    const informative = window.filter((token) => tokenLooksNarrative(token)).length;
    const noisy = window.filter((token) => tokenLooksNoisy(token)).length;
    if (informative >= 3 && informative > noisy) return i;
  }
  return tokens.length - 1;
}

function cleanupOcrLine(line, mode = "augment") {
  const trimmed = String(line || "").trim();
  if (!trimmed) return "";

  const tokens = trimmed.split(/\s+/).filter(Boolean);
  if (!tokens.length) return "";

  let start = 0;
  let end = tokens.length - 1;
  if (mode === "augment") {
    let prefixStart = 0;
    const firstLowerWordIndex = tokens.findIndex((token) => /[a-z]{2,}/.test(normalizeToken(token)));
    if (firstLowerWordIndex >= 2) {
      const prefix = tokens.slice(0, firstLowerWordIndex);
      const prefixNoisyRatio = prefix.length
        ? prefix.filter((token) => tokenLooksNoisy(token)).length / prefix.length
        : 0;
      if (prefixNoisyRatio >= 0.5) {
        prefixStart = firstLowerWordIndex;
      }
    }

    start = Math.max(prefixStart, findNarrativeBoundary(tokens, "start"));
    end = findNarrativeBoundary(tokens, "end");
    if (start > end) return "";
  }

  const selected = tokens.slice(start, end + 1);
  const cleaned = selected.join(" ").replace(/\s+/g, " ").trim();
  return cleaned;
}

function isLikelyOcrNoiseLine(line, mode = "augment") {
  const trimmed = String(line || "").trim();
  if (!trimmed) return true;
  if (trimmed.length < 2) return true;

  if (
    mode === "augment" &&
    /\b(PHOTOREPORT|ENDOSOFT|Surgery Center|electronically signed off)\b/i.test(trimmed) &&
    !hasClinicalPattern(trimmed)
  ) {
    return true;
  }

  const chars = trimmed.length;
  const letters = (trimmed.match(/[A-Za-z]/g) || []).length;
  const lower = (trimmed.match(/[a-z]/g) || []).length;
  const digits = (trimmed.match(/\d/g) || []).length;
  const punctuation = (trimmed.match(/[^A-Za-z0-9\s]/g) || []).length;
  const oZero = (trimmed.match(/[O0o]/g) || []).length;
  const tokens = trimmed.split(/\s+/).filter(Boolean);
  const lowerWordCount = tokens.filter((token) => /[a-z]{2,}/.test(token)).length;
  const noisyTokenRatio = tokens.length
    ? tokens.filter((token) => tokenLooksNoisy(token)).length / tokens.length
    : 1;
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
  if (tokens.length >= 5 && noisyTokenRatio >= 0.42 && !clinicalPattern) return true;
  if (lower === 0 && longWordCount < 2 && !clinicalPattern) return true;

  if (mode === "augment") {
    if (lower === 0 && !clinicalPattern) return true;
    if (lowerWordCount < 3 && !clinicalPattern) return true;
    if (noisyTokenRatio >= 0.3 && !clinicalPattern) return true;
    if (tokens.length < 3 && !clinicalPattern) return true;
  }

  return false;
}

export function sanitizeOcrText(ocrText, opts = {}) {
  const mode = opts.mode === "augment" ? "augment" : "full";
  const lines = normalizeLines(ocrText);
  const out = [];
  const seen = new Set();

  for (const rawLine of lines) {
    const line = cleanupOcrLine(rawLine, mode);
    if (!line) continue;
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
  const nativeForMerge = contaminationHigh
    ? pruneCaptionNoiseFromNativeText(nativeText)
    : nativeText;

  if (ocrMuchLonger && contaminationHigh) {
    return {
      sourceDecision: "hybrid",
      text: mergeNativeAndOcrText(nativeForMerge, ocrText, { mode: "augment" }),
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
    text: mergeNativeAndOcrText(nativeForMerge, ocrText, { mode: "augment" }),
    reason: "hybrid merge for traceable native+OCR coverage",
    confidence: 0.78,
    blocked: false,
  };
}
