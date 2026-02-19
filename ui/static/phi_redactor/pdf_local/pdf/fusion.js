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
  if (!text || text.length > 56) return false;
  if (/[.:;%]/.test(text)) return false;
  if (/\d/.test(text)) return false;

  const tokens = text.split(/\s+/).filter(Boolean);
  if (tokens.length < 2 || tokens.length > 7) return false;

  const anatomyTokenPattern = /^(left|right|upper|lower|middle|lobe|lobar|mainstem|entrance|segment|bronchus|airway|carina|trachea|lingula|LUL|LLL|RUL|RML|RLL)$/i;
  const anatomyCount = tokens.filter((token) => anatomyTokenPattern.test(token)).length;
  if (anatomyCount < 2) return false;
  if (tokens.length <= 4) return true;
  return anatomyCount / Math.max(1, tokens.length) >= 0.72;
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

const OCR_BOILERPLATE_PATTERNS = Object.freeze([
  /\bPowered\s+by\s+Provation\b/i,
  /^\s*Page\s+\d+\s+of\s+\d+\s*$/i,
  /\bAMA\b.*\bcopyright\b/i,
  /\bAmerican Medical Association\b/i,
  /\bProvation\b.*\b(?:Suite|Road|Street|Drive|Avenue|Blvd|Lane|Court|Way)\b/i,
]);

function isLikelyBoilerplateLine(line) {
  const text = String(line || "").trim();
  if (!text) return false;
  return OCR_BOILERPLATE_PATTERNS.some((pattern) => pattern.test(text));
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
  if (/^(?:mm|cm|mg|ml|mcg|ug|kg|g|l|dl|cc|%)$/i.test(t)) return true;
  if (/^[A-Z](?!0{2,3}$)\d{2,3}(?:\.\d+)?$/.test(t)) return true;
  if (/^\d{1,2}\/\d{1,2}\/\d{2,4}$/.test(t)) return true;
  if (/^(ICD|CPT|MRN|DOB|MD|IV|LUL|LLL|RUL|RLL)$/i.test(t)) return true;
  return false;
}

function tokenLooksNarrative(token) {
  const t = normalizeToken(token);
  if (!t) return false;
  if (tokenLooksNoisy(t)) return false;
  return /[a-z]{2,}/.test(t) || tokenHasClinicalSignal(t);
}

function countMatches(text, re) {
  if (!text) return 0;
  const matches = String(text).match(re);
  return matches ? matches.length : 0;
}

function tokenLooksNoisy(token) {
  const t = normalizeToken(token);
  if (!t) return true;
  if (tokenHasClinicalSignal(t)) return false;

  const lowerToken = t.toLowerCase();
  if (/^[a-z]$/.test(lowerToken)) {
    return lowerToken !== "a";
  }

  const shortWordAllowlist = new Set(["an", "in", "on", "to", "of", "or", "by", "as", "at", "if", "is", "it", "we", "he", "be"]);
  if (/^[a-z]{2}$/.test(lowerToken) && !shortWordAllowlist.has(lowerToken)) {
    return true;
  }

  const len = t.length;
  const hasLowerWord = /[a-z]{2,}/.test(t);
  const hasLetters = /[A-Za-z]/.test(t);
  const hasDigits = /\d/.test(t);
  const hasZero = /0/.test(t);

  const o0Count = countMatches(t, /[O0o]/g);
  const ocCount = countMatches(t, /[O0oCc]/g);
  const o0Ratio = o0Count / Math.max(1, len);
  const ocRatio = ocCount / Math.max(1, len);

  const isAllCaps = hasLetters && !/[a-z]/.test(t) && /^[A-Z0-9]+$/.test(t);

  // Common OCR garbage: tokens dominated by O/0 (optionally with C/c).
  if (/^[O0CcoIl1]+$/.test(t) && len >= 3 && o0Ratio >= 0.6) return true;
  if (len >= 4 && o0Count >= 2 && ocRatio >= 0.75) return true;

  // Mixed letter+digit tokens with 0 are often OCR confusion (e.g., "mo0").
  if (len >= 3 && hasZero && hasDigits && hasLetters && o0Count >= 1) return true;

  // All-caps tokens with heavy O/0 presence are frequently watermark artifacts (e.g., "OMOMOD").
  if (isAllCaps && len >= 4 && o0Ratio >= 0.45) return true;

  if (hasLowerWord) return false;
  if (/^[A-Z0-9]{3,}$/.test(t) && /[0-9]/.test(t) && /[O0C]/.test(t)) return true;
  if (/^[A-Z]{1,2}$/.test(t) && !/^(AM|PM|MD|IV)$/i.test(t)) return true;
  if (/^\d{1,3}$/.test(t)) return true;
  return false;
}

function isLikelyCodeNoiseLine(line) {
  const text = String(line || "").trim();
  if (!text) return true;
  if (/^(?:ICD\b|CPT\b)/i.test(text)) return false;

  const tokens = text.split(/\s+/).map(normalizeToken).filter(Boolean);
  if (!tokens.length) return true;

  const lowerWordCount = tokens.filter((token) => /[a-z]{2,}/.test(token)).length;
  if (lowerWordCount > 0) return false;

  const shortRatio = tokens.filter((token) => token.length <= 4).length / Math.max(1, tokens.length);
  const noisyRatio = tokens.filter((token) => tokenLooksNoisy(token)).length / Math.max(1, tokens.length);
  const compact = tokens.join("");
  const oZeroRatio = countMatches(compact, /[O0o]/g) / Math.max(1, compact.length);
  const codeLikeCount = tokens.filter((token) => /^[A-Z]\d{2}(?:\.[A-Z0-9]{1,4})?$/.test(token) || /^\d{5}$/.test(token)).length;

  if (tokens.length >= 2 && shortRatio >= 0.8 && oZeroRatio >= 0.28 && codeLikeCount <= 1) return true;
  if (tokens.length >= 2 && shortRatio >= 0.9 && oZeroRatio >= 0.35 && tokens.every((token) => /^[A-Z0-9.]{1,5}$/.test(token))) {
    return true;
  }
  if (tokens.length >= 2 && noisyRatio >= 0.55 && shortRatio >= 0.7) return true;
  return false;
}

function pruneNoisyEdgeTokens(tokens) {
  const list = Array.isArray(tokens) ? tokens.slice() : [];
  if (list.length < 2) return list;

  let start = 0;
  let end = list.length - 1;

  while (end - start + 1 >= 4 && tokenLooksNoisy(list[start])) start += 1;
  while (end - start + 1 >= 4 && tokenLooksNoisy(list[end])) end -= 1;

  return list.slice(start, end + 1);
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
  const pruned = pruneNoisyEdgeTokens(selected);
  const cleaned = pruned.join(" ").replace(/\s+/g, " ").trim();
  return cleaned;
}

function isLikelyOcrNoiseLine(line, mode = "augment", rawLine = "") {
  const trimmed = String(line || "").trim();
  if (!trimmed) return true;
  if (trimmed.length < 2) return true;

  const rawTrimmed = String(rawLine || "").trim();
  const vendorScanText = rawTrimmed || trimmed;
  if (mode === "augment" && /\bPHOTOREPORT\b/i.test(vendorScanText)) return true;

  if (mode === "augment" && !hasClinicalPattern(trimmed)) {
    if (/^PHOTOREPORT$/i.test(trimmed)) return true;
    if (/\belectronically signed off\b/i.test(vendorScanText)) return true;
    if (/\bEndoSoft\b/i.test(vendorScanText) && (/[0-9]/.test(vendorScanText) || /[O0]{3,}/.test(vendorScanText))) {
      return true;
    }
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
  if (chars >= 8 && oZeroRatio > 0.5 && lower <= 1 && tokens.length >= 2 && !/[.]/.test(trimmed)) return true;
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
  let prevKey = "";

  for (const rawLine of lines) {
    const line = cleanupOcrLine(rawLine, mode);
    if (!line) continue;
    if (isLikelyBoilerplateLine(line)) continue;
    if (isLikelyImageCaptionLine(line)) continue;
    if (shouldDropLineForMerge(line)) continue;
    if (isLikelyOcrNoiseLine(line, mode, rawLine)) continue;
    const key = normalizeLineKey(line);
    if (!key || seen.has(key)) continue;
    if (key === prevKey) continue;
    seen.add(key);
    prevKey = key;
    out.push(line.trim());
  }

  return out.join("\n");
}

const SECTION_DEFS = Object.freeze([
  {
    id: "procedure_performed",
    header: "PROCEDURE PERFORMED:",
    headerRe: /^PROCEDURE PERFORMED:/i,
    keywordRe: /\b(bronchoscopy|ebus|biopsy|lavage|tbna|procedure performed)\b/i,
  },
  {
    id: "indications",
    header: "INDICATIONS FOR EXAMINATION:",
    headerRe: /^INDICATIONS FOR EXAMINATION:/i,
    keywordRe: /\b(obstruction|indication|dyspnea|shortness of breath|cough)\b/i,
  },
  {
    id: "instruments",
    header: "INSTRUMENTS:",
    headerRe: /^INSTRUMENTS?:/i,
    keywordRe: /\b(instrument|loaner|bronchoscope|catheter|needle|forceps|snare|basket)\b/i,
  },
  {
    id: "medications",
    header: "MEDICATIONS:",
    headerRe: /^MEDICATIONS?:/i,
    keywordRe: /\b(versed|demerol|midazolam|fentanyl|lidocaine|propofol|\d+\s*(?:mg|ml|mcg|ug|%)\b)\b/i,
  },
  {
    id: "procedure_technique",
    header: "PROCEDURE TECHNIQUE:",
    headerRe: /^PROCEDURE TECHNIQUE:/i,
    keywordRe: /\b(consent was obtained|monitoring|nasal cannula|conscious sedation|anesthesia|bronchoscope was inserted|airway examined|indwelling iv catheter|benefits and alternatives|patient appeared to understand)\b/i,
  },
  {
    id: "findings",
    header: "FINDINGS:",
    headerRe: /^FINDINGS?:/i,
    keywordRe: /\b(stricture|stenosis|erythema|friable|lumen|compression|submucosal|fibrosis|carcinoma|scope could be advanced|estimated diameter)\b/i,
  },
  {
    id: "diagnosis",
    header: "PULMONOLOGIST DIAGNOSIS:",
    headerRe: /^(?:PULMONOLOGIST\s+)?DIAGNOSIS:/i,
    keywordRe: /\b(malignancy|carcinoma|neoplasm|small cell|benign|diagnosis)\b/i,
  },
  {
    id: "recommendations",
    header: "RECOMMENDATIONS:",
    headerRe: /^RECOMMENDATIONS?:/i,
    keywordRe: /\b(follow-up|follow up|primary care|return|recommend)\b/i,
  },
  {
    id: "icd_codes",
    header: "ICD 10 Codes:",
    headerRe: /^(?:ICD\b|ICD[-\s]*10\b).*:/i,
    keywordRe: /\b[A-Z](?!0{2,3}\b)\d{2}(?:\.\d+)?\b|\bICD\b/i,
  },
  {
    id: "cpt_codes",
    header: "CPT Code:",
    headerRe: /^CPT(?:\s+Code)?\s*:/i,
    keywordRe: /\b(?:\d{5}|CPT)\b/i,
  },
]);

const NARRATIVE_SECTION_IDS = new Set([
  "indications",
  "procedure_technique",
  "findings",
  "diagnosis",
  "recommendations",
]);

const CODE_SECTION_IDS = new Set(["icd_codes", "cpt_codes"]);

function shouldDropLineForMerge(line, sectionId = "__preamble") {
  const text = String(line || "").trim();
  if (!text) return true;
  if (isLikelyBoilerplateLine(text)) return true;
  if (isLikelyImageCaptionLine(text)) return true;
  if (/\bPHOTOREPORT\b/i.test(text)) return true;

  if (CODE_SECTION_IDS.has(sectionId) && isLikelyCodeNoiseLine(text)) {
    return true;
  }

  const tokens = text.split(/\s+/).map(normalizeToken).filter(Boolean);
  if (!tokens.length) return true;

  const lowerWordCount = tokens.filter((token) => /[a-z]{2,}/.test(token)).length;
  if (lowerWordCount > 0) return false;

  const noisyRatio = tokens.filter((token) => tokenLooksNoisy(token)).length / Math.max(1, tokens.length);
  const shortRatio = tokens.filter((token) => token.length <= 4).length / Math.max(1, tokens.length);
  const compact = tokens.join("");
  const symbolRatio = countMatches(text, /[^A-Za-z0-9\s]/g) / Math.max(1, text.length);
  const oZeroRatio = countMatches(compact, /[O0o]/g) / Math.max(1, compact.length);

  if (tokens.length >= 2 && noisyRatio >= 0.6 && (oZeroRatio >= 0.26 || symbolRatio >= 0.25)) return true;
  return false;
}

function dedupeLines(lines) {
  const out = [];
  const seen = new Set();
  for (const line of Array.isArray(lines) ? lines : []) {
    const key = normalizeLineKey(line);
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(line);
  }
  return out;
}

function matchSectionHeader(line) {
  for (const section of SECTION_DEFS) {
    if (section.headerRe.test(line)) return section;
  }
  return null;
}

function buildSectionBuckets(lines) {
  const sections = new Map([["__preamble", []]]);
  const headers = new Map();
  const order = ["__preamble"];
  let currentId = "__preamble";

  for (const line of dedupeLines(lines)) {
    const section = matchSectionHeader(line);
    if (section) {
      currentId = section.id;
      if (!sections.has(currentId)) {
        sections.set(currentId, []);
        order.push(currentId);
      }
      headers.set(currentId, String(line).trim());
      continue;
    }

    if (shouldDropLineForMerge(line, currentId)) continue;
    sections.get(currentId)?.push(String(line).trim());
  }

  return { sections, headers, order };
}

function pushUniqueLine(out, line, seen) {
  const key = normalizeLineKey(line);
  if (!key || seen.has(key)) return false;
  seen.add(key);
  out.push(line);
  return true;
}

function buildTokenSets(lines) {
  return (Array.isArray(lines) ? lines : [])
    .map((line) => new Set(tokenizeForOverlap(line)))
    .filter((tokens) => tokens.size > 0);
}

function lineHasNarrativeSignal(line) {
  const text = String(line || "").trim();
  if (!text) return false;
  const tokens = text.split(/\s+/).filter(Boolean);
  const lowerWordCount = tokens.filter((token) => /[a-z]{2,}/.test(normalizeToken(token))).length;
  if (lowerWordCount >= 3 && tokens.length >= 5) return true;
  if (/\b(consent|monitoring|sedation|anesthesia|airway examined|stricture|stenosis|lumen|compression|follow-up|recommend)\b/i.test(text)) {
    return true;
  }
  if (/\b\d+(?:mm|cm|mg|ml|%)\b/i.test(text) && lowerWordCount >= 2) return true;
  return false;
}

function sectionLooksTruncated(lines, sectionId) {
  const list = Array.isArray(lines) ? lines : [];
  if (!list.length) return true;
  const text = list.join(" ").replace(/\s+/g, " ").trim();
  if (!text) return true;

  if (sectionId === "__preamble" && text.length < 80) {
    return true;
  }

  if (NARRATIVE_SECTION_IDS.has(sectionId)) {
    if (text.length < 90) return true;
    if (/\b(?:an|and|the|of|to|for|with|through|in|on)\.?$/i.test(text)) return true;
    if (!/[.!?]$/.test(text) && text.length < 160) return true;
  }

  if ((sectionId === "instruments" || sectionId === "medications") && text.length < 24) {
    return true;
  }

  return false;
}

function shouldKeepOcrLineForSection(line, sectionId) {
  const text = String(line || "").trim();
  if (!text) return false;
  if (shouldDropLineForMerge(text, sectionId)) return false;
  if (isLikelyOcrNoiseLine(text, "augment", text)) return false;
  if (NARRATIVE_SECTION_IDS.has(sectionId)) {
    return lineHasNarrativeSignal(text) || (hasClinicalPattern(text) && /[a-z]{2,}/.test(text));
  }
  if (sectionId === "cpt_codes") {
    return /\b(?:\d{5}|CPT)\b/i.test(text);
  }
  if (sectionId === "icd_codes") {
    return /\b(?:ICD|[A-Z]\d{2}(?:\.[A-Z0-9]{1,4})?)\b/i.test(text) && !isLikelyCodeNoiseLine(text);
  }
  return true;
}

function scoreSectionGuess(line, section) {
  const text = String(line || "").trim();
  if (!text || !section?.keywordRe?.test(text)) return Number.NEGATIVE_INFINITY;
  if (shouldDropLineForMerge(text, section.id)) return Number.NEGATIVE_INFINITY;

  const narrative = lineHasNarrativeSignal(text);
  let score = 1;

  if (NARRATIVE_SECTION_IDS.has(section.id) && narrative) {
    score += 2;
  }

  if (section.id === "procedure_technique") {
    if (/\b(consent|monitoring|sedation|anesthesia|nasal cannula|indwelling iv|benefits and alternatives|patient appeared to understand)\b/i.test(text)) {
      score += 2;
    }
  }

  if (section.id === "findings") {
    if (/\b(stricture|stenosis|lumen|compression|fibrosis|erythema|friable|scope could be advanced|estimated diameter|carcinoma)\b/i.test(text)) {
      score += 2;
    }
  }

  if (section.id === "diagnosis") {
    if (/\b(malignancy|diagnosis|neoplasm|carcinoma|benign|small cell)\b/i.test(text)) {
      score += 1.5;
    }
  }

  if (section.id === "instruments" || section.id === "medications") {
    if (narrative) score -= 2.5;
    const tokenCount = text.split(/\s+/).filter(Boolean).length;
    if (tokenCount <= 6) score += 0.8;
    if (/[,:;]/.test(text)) score += 0.4;
  }

  if (section.id === "cpt_codes") {
    if (!/\b\d{5}\b|\bCPT\b/i.test(text)) return Number.NEGATIVE_INFINITY;
    score += 1.2;
  }
  if (section.id === "icd_codes") {
    if (!/\b[A-Z]\d{2}(?:\.[A-Z0-9]{1,4})?\b|\bICD\b/i.test(text) || isLikelyCodeNoiseLine(text)) {
      return Number.NEGATIVE_INFINITY;
    }
    score += 1.2;
  }

  return score;
}

function guessSectionForLine(line, preferredIds = []) {
  const preferredSet = new Set(Array.isArray(preferredIds) ? preferredIds : []);
  const sections = [];
  for (const id of preferredSet) {
    const section = SECTION_DEFS.find((entry) => entry.id === id);
    if (section) sections.push(section);
  }
  for (const section of SECTION_DEFS) {
    if (!preferredSet.has(section.id)) sections.push(section);
  }

  let bestId = null;
  let bestScore = Number.NEGATIVE_INFINITY;
  for (const section of sections) {
    const score = scoreSectionGuess(line, section);
    if (score > bestScore) {
      bestScore = score;
      bestId = section.id;
    }
  }

  return bestScore > 0 ? bestId : null;
}

function mergeSectionLines(sectionId, nativeLines, ocrLines) {
  const native = dedupeLines(nativeLines);
  const nativeTokenSets = buildTokenSets(native);
  const filteredOcr = [];
  const seenOcr = new Set();

  for (const line of dedupeLines(ocrLines)) {
    if (!pushUniqueLine(filteredOcr, line, seenOcr)) continue;
  }

  const selectedOcr = filteredOcr
    .filter((line) => shouldKeepOcrLineForSection(line, sectionId))
    .filter((line) => !hasHighTokenOverlap(line, nativeTokenSets));

  if (!selectedOcr.length) return native;

  const nativeChars = native.join(" ").length;
  const ocrChars = selectedOcr.join(" ").length;
  const replaceThreshold = sectionId === "__preamble"
    ? Math.max(36, nativeChars * 1.15)
    : Math.max(80, nativeChars * 1.25);
  const replaceWithOcr = sectionLooksTruncated(native, sectionId) &&
    ocrChars > replaceThreshold;

  if (replaceWithOcr) {
    return selectedOcr;
  }

  const merged = [...native];
  const mergedTokenSets = buildTokenSets(merged);
  for (const line of selectedOcr) {
    if (hasHighTokenOverlap(line, mergedTokenSets)) continue;
    merged.push(line);
    mergedTokenSets.push(new Set(tokenizeForOverlap(line)));
  }
  return merged;
}

export function mergeNativeAndOcrText(nativeText, ocrText, opts = {}) {
  const mode = opts.mode === "augment" ? "augment" : "full";
  const nativeLines = dedupeLines(normalizeLines(nativeText).filter((line) => !shouldDropLineForMerge(line)));
  const ocrLines = dedupeLines(normalizeLines(sanitizeOcrText(ocrText, { mode })));

  if (mode !== "augment") {
    const out = [];
    const seen = new Set();
    for (const line of nativeLines) pushUniqueLine(out, line, seen);
    for (const line of ocrLines) pushUniqueLine(out, line, seen);
    return out.join("\n");
  }

  const nativeBuckets = buildSectionBuckets(nativeLines);
  const ocrBuckets = buildSectionBuckets(ocrLines);

  const nativeSectionIds = nativeBuckets.order.filter((id) => id !== "__preamble");
  const ocrAssigned = new Map();
  const ocrOrphan = [];

  for (const [sectionId, lines] of ocrBuckets.sections.entries()) {
    if (sectionId === "__preamble") continue;
    ocrAssigned.set(sectionId, dedupeLines(lines));
  }

  const preferredSectionIds = nativeSectionIds.length
    ? nativeSectionIds
    : SECTION_DEFS.map((section) => section.id);
  const fallbackNarrativeSection = preferredSectionIds.includes("procedure_technique")
    ? "procedure_technique"
    : preferredSectionIds.find((id) => NARRATIVE_SECTION_IDS.has(id)) || null;
  for (const line of ocrBuckets.sections.get("__preamble") || []) {
    const guessed = guessSectionForLine(line, preferredSectionIds);
    if (!guessed) {
      if (fallbackNarrativeSection && lineHasNarrativeSignal(line)) {
        const current = ocrAssigned.get(fallbackNarrativeSection) || [];
        current.push(line);
        ocrAssigned.set(fallbackNarrativeSection, dedupeLines(current));
        continue;
      }
      ocrOrphan.push(line);
      continue;
    }
    const current = ocrAssigned.get(guessed) || [];
    current.push(line);
    ocrAssigned.set(guessed, dedupeLines(current));
  }

  const out = [];
  const seenOut = new Set();

  const pushSection = (sectionId, nativeSectionLines, ocrSectionLines, headerText) => {
    if (sectionId !== "__preamble" && headerText) {
      pushUniqueLine(out, headerText, seenOut);
    }

    const merged = mergeSectionLines(sectionId, nativeSectionLines, ocrSectionLines);
    for (const line of merged) {
      pushUniqueLine(out, line, seenOut);
    }
  };

  for (const sectionId of nativeBuckets.order) {
    const nativeSectionLines = nativeBuckets.sections.get(sectionId) || [];
    const ocrSectionLines = ocrAssigned.get(sectionId) || [];
    const headerText = sectionId === "__preamble"
      ? null
      : (nativeBuckets.headers.get(sectionId) || SECTION_DEFS.find((section) => section.id === sectionId)?.header || null);
    pushSection(sectionId, nativeSectionLines, ocrSectionLines, headerText);
  }

  const nativeSectionSet = new Set(nativeSectionIds);
  for (const section of SECTION_DEFS) {
    if (nativeSectionSet.has(section.id)) continue;
    const ocrSectionLines = ocrAssigned.get(section.id) || [];
    if (!ocrSectionLines.length) continue;
    const headerText = ocrBuckets.headers.get(section.id) || section.header;
    pushSection(section.id, [], ocrSectionLines, headerText);
  }

  for (const line of ocrOrphan) {
    if (shouldDropLineForMerge(line)) continue;
    if (!lineHasNarrativeSignal(line)) continue;
    pushUniqueLine(out, line, seenOut);
  }

  return out.join("\n");
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
  const shouldPruneCaptions = contaminationScore >= 0.28 && ocrMuchLonger;
  const nativeForMerge = shouldPruneCaptions ? pruneCaptionNoiseFromNativeText(nativeText) : nativeText;

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
