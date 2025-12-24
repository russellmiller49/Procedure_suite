/**
 * redactor.worker.js — “Best-of” Hybrid PHI Detector (ML + Regex)
 *
 * Combines:
 *  - Version B robustness: quantized→unquantized fallback, offset recovery, cancel, debug hooks
 *  - Version A fix: expand spans to word boundaries to prevent partial-word redactions
 *  - Hybrid regex injection BEFORE veto (cold-start header guarantees)
 *  - Smarter merge rules: prefer regex spans over overlapping ML spans to avoid double-highlights
 */

import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2";
import { applyVeto } from "./protectedVeto.js";

const MODEL_PATH = "./vendor/phi_distilbert_ner/";
const MODEL_ID = "phi_distilbert_ner";
const MODEL_BASE_URL = new URL("./vendor/", import.meta.url).toString();
const TASK = "token-classification";

// Character windowing (simple + robust)
const WINDOW = 2500;
const OVERLAP = 250;
const STEP = WINDOW - OVERLAP;

// =============================================================================
// HYBRID REGEX DETECTION (guarantees headers/IDs)
// =============================================================================

// Matches: "Patient: Smith, John" or "Pt Name: John Smith"
const PATIENT_HEADER_RE =
  /(?:Patient(?:\s+Name)?|Pt|Name|Subject)\s*[:\-]?\s*([A-Z][a-z]+,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?|[A-Z][a-z]+\s+[A-Z]'?[A-Za-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)/gim;

// Matches: "MRN: 12345" or "ID: 55-22-11"
const MRN_RE =
  /\b(?:MRN|MR|Medical\s*Record|Patient\s*ID|ID|EDIPI|DOD\s*ID)\s*[:\#]?\s*([A-Z0-9\-]{4,15})\b/gi;

// =============================================================================
// Transformers.js env
// =============================================================================

env.allowLocalModels = true;
env.allowRemoteModels = false;
env.localModelPath = MODEL_BASE_URL;

// Disable browser cache temporarily while iterating (you can re-enable later)
env.useBrowserCache = false;

if (env.backends?.onnx?.wasm) {
  env.backends.onnx.wasm.proxy = false;
  env.backends.onnx.wasm.numThreads = 1;
}

// =============================================================================
// Worker state
// =============================================================================

let classifier = null;
let classifierQuantized = null;
let classifierUnquantized = null;

let modelPromiseQuantized = null;
let modelPromiseUnquantized = null;

let protectedTerms = null;
let termsPromise = null;

let cancelled = false;
let debug = false;
let didTokenDebug = false;
let didLogitsDebug = false;

function log(...args) {
  if (debug) console.log(...args);
}

function post(type, payload = {}) {
  self.postMessage({ type, ...payload });
}

function toFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function toFiniteInt(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  return Number.isInteger(value) ? value : Math.trunc(value);
}

function normalizeLabel(entity) {
  if (!entity) return "PHI";
  const raw = String(entity).toUpperCase();
  return raw.replace(/^B-/, "").replace(/^I-/, "");
}

function normalizeRawOutput(raw) {
  if (Array.isArray(raw)) return raw;
  if (!raw || typeof raw !== "object") return [];
  if (Array.isArray(raw.data)) return raw.data;
  if (Array.isArray(raw.entities)) return raw.entities;
  return [];
}

// =============================================================================
// Protected terms (veto list) loader
// =============================================================================

async function loadProtectedTerms() {
  if (protectedTerms) return protectedTerms;
  if (termsPromise) return termsPromise;

  termsPromise = (async () => {
    const termsUrl = new URL(`${MODEL_PATH}protected_terms.json`, import.meta.url);
    const res = await fetch(termsUrl);
    if (!res.ok) throw new Error(`Failed to load protected_terms.json (${res.status})`);
    protectedTerms = await res.json();
    return protectedTerms;
  })();

  return termsPromise;
}

// =============================================================================
// Model loading (quantized -> fallback unquantized)
// =============================================================================

async function loadQuantizedModel() {
  if (classifierQuantized) return classifierQuantized;
  if (modelPromiseQuantized) return modelPromiseQuantized;

  modelPromiseQuantized = pipeline(TASK, MODEL_ID, { device: "wasm", quantized: true })
    .then((c) => {
      classifierQuantized = c;
      return c;
    })
    .catch((err) => {
      modelPromiseQuantized = null;
      classifierQuantized = null;
      throw err;
    });

  return modelPromiseQuantized;
}

async function loadUnquantizedModel() {
  if (classifierUnquantized) return classifierUnquantized;
  if (modelPromiseUnquantized) return modelPromiseUnquantized;

  modelPromiseUnquantized = pipeline(TASK, MODEL_ID, { device: "wasm", quantized: false })
    .then((c) => {
      classifierUnquantized = c;
      return c;
    })
    .catch((err) => {
      modelPromiseUnquantized = null;
      classifierUnquantized = null;
      throw err;
    });

  return modelPromiseUnquantized;
}

async function loadModel(config = {}) {
  const forceUnquantized = Boolean(config.forceUnquantized);

  if (forceUnquantized) {
    post("progress", { stage: "Loading local PHI model (unquantized; forced)…" });
    classifier = await loadUnquantizedModel();
    post("progress", { stage: "AI model ready" });
    return classifier;
  }

  post("progress", { stage: "Loading local PHI model (quantized)…" });
  try {
    classifier = await loadQuantizedModel();
    post("progress", { stage: "AI model ready" });
    return classifier;
  } catch (err) {
    classifier = null;
    log("[PHI Worker] Quantized load failed; falling back to unquantized", err);
  }

  post("progress", { stage: "Loading local PHI model (unquantized)…" });
  classifier = await loadUnquantizedModel();
  post("progress", { stage: "AI model ready" });
  return classifier;
}

// =============================================================================
// Regex injection (deterministic)
// =============================================================================

function runRegexDetectors(text) {
  const spans = [];

  // Reset global regex state
  PATIENT_HEADER_RE.lastIndex = 0;
  MRN_RE.lastIndex = 0;

  // 1) Patient header names
  for (const match of text.matchAll(PATIENT_HEADER_RE)) {
    const fullMatch = match[0];
    const nameGroup = match[1];
    const groupOffset = fullMatch.indexOf(nameGroup);
    if (groupOffset !== -1 && match.index != null) {
      spans.push({
        start: match.index + groupOffset,
        end: match.index + groupOffset + nameGroup.length,
        label: "PATIENT",
        score: 1.0,
        source: "regex_header",
      });
    }
  }

  // 2) MRN / IDs
  for (const match of text.matchAll(MRN_RE)) {
    const fullMatch = match[0];
    const idGroup = match[1];
    const groupOffset = fullMatch.indexOf(idGroup);
    if (groupOffset !== -1 && match.index != null) {
      spans.push({
        start: match.index + groupOffset,
        end: match.index + groupOffset + idGroup.length,
        label: "ID",
        score: 1.0,
        source: "regex_mrn",
      });
    }
  }

  return spans;
}

// =============================================================================
// NER: robust offsets
// =============================================================================

function getOffsetsMappingFromTokenizerEncoding(encoding) {
  const mapping = encoding?.offset_mapping ?? encoding?.offsets ?? encoding?.offsetMapping;
  if (!Array.isArray(mapping)) return null;

  // Some tokenizers return a batch: [ [ [s,e], ... ] ]
  const candidate = Array.isArray(mapping[0]) && Array.isArray(mapping[0][0]) ? mapping[0] : mapping;
  if (!Array.isArray(candidate) || candidate.length === 0) return null;
  if (!Array.isArray(candidate[0]) || candidate[0].length < 2) return null;
  if (typeof candidate[0][0] !== "number" || typeof candidate[0][1] !== "number") return null;
  return candidate;
}

function getOffsetPair(offsets, index) {
  if (!Array.isArray(offsets) || typeof index !== "number" || !Number.isFinite(index)) return null;
  const idx = toFiniteInt(index);
  if (idx === null) return null;
  const pair = offsets[idx] ?? (idx > 0 ? offsets[idx - 1] : null);
  if (!Array.isArray(pair) || pair.length < 2) return null;
  const start = pair[0];
  const end = pair[1];
  if (typeof start !== "number" || typeof end !== "number") return null;
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return null;
  return [start, end];
}

function getEntityText(ent) {
  const text =
    typeof ent?.word === "string"
      ? ent.word
      : typeof ent?.token === "string"
      ? ent.token
      : typeof ent?.text === "string"
      ? ent.text
      : typeof ent?.value === "string"
      ? ent.value
      : null;
  if (!text) return null;
  return String(text).replace(/^##/, "");
}

async function runNER(chunk, aiThreshold) {
  if (!classifier) return [];
  const raw = await classifier(chunk, {
    aggregation_strategy: "simple",
    ignore_labels: ["O"],
  });

  const rawList = normalizeRawOutput(raw);
  log("[PHI] raw spans (simple) count:", rawList.length);

  const spans = [];
  let offsets = null;
  let offsetsTried = false;
  let searchCursor = 0;

  for (const ent of rawList) {
    let start =
      toFiniteNumber(ent?.start) ??
      toFiniteNumber(ent?.start_offset) ??
      toFiniteNumber(ent?.begin);

    let end =
      toFiniteNumber(ent?.end) ??
      toFiniteNumber(ent?.end_offset) ??
      toFiniteNumber(ent?.finish);

    const score =
      toFiniteNumber(ent?.score) ??
      toFiniteNumber(ent?.confidence) ??
      toFiniteNumber(ent?.probability) ??
      0.0;

    // If offsets are missing/bad, try to recover.
    if (typeof start !== "number" || typeof end !== "number" || end <= start) {
      const tokenIndex =
        toFiniteInt(ent?.index) ??
        toFiniteInt(ent?.token) ??
        toFiniteInt(ent?.position) ??
        toFiniteInt(ent?.token_index) ??
        toFiniteInt(ent?.tokenIndex) ??
        null;

      const startTokenIndex =
        toFiniteInt(ent?.start_token) ??
        toFiniteInt(ent?.startToken) ??
        toFiniteInt(ent?.start_index) ??
        toFiniteInt(ent?.startIndex) ??
        null;

      const endTokenIndex =
        toFiniteInt(ent?.end_token) ??
        toFiniteInt(ent?.endToken) ??
        toFiniteInt(ent?.end_index) ??
        toFiniteInt(ent?.endIndex) ??
        null;

      const needsOffsets =
        tokenIndex !== null ||
        startTokenIndex !== null ||
        endTokenIndex !== null ||
        Boolean(getEntityText(ent));

      if (needsOffsets && !offsetsTried) {
        offsetsTried = true;
        try {
          const enc = await classifier.tokenizer(chunk, { return_offsets_mapping: true });
          offsets = getOffsetsMappingFromTokenizerEncoding(enc);
          log("[PHI] tokenizer offsets mapping count:", offsets ? offsets.length : null);
        } catch (err) {
          log("[PHI] tokenizer return_offsets_mapping failed:", err);
        }
      }

      if (offsets) {
        if (startTokenIndex !== null || endTokenIndex !== null) {
          const sPair =
            getOffsetPair(offsets, startTokenIndex) ??
            (startTokenIndex !== null ? getOffsetPair(offsets, startTokenIndex + 1) : null);
          const ePair =
            getOffsetPair(offsets, endTokenIndex) ??
            (endTokenIndex !== null ? getOffsetPair(offsets, endTokenIndex + 1) : null);
          if (sPair && ePair) {
            start = sPair[0];
            end = ePair[1];
          }
        } else if (tokenIndex !== null) {
          const pair = getOffsetPair(offsets, tokenIndex) ?? getOffsetPair(offsets, tokenIndex + 1);
          if (pair) {
            start = pair[0];
            end = pair[1];
          }
        }
      }

      // Last-resort: find token text in the chunk (case-insensitive) with cursor.
      if (typeof start !== "number" || typeof end !== "number" || end <= start) {
        const tokenText = getEntityText(ent);
        if (tokenText) {
          const candidates = tokenText.trim() !== tokenText ? [tokenText, tokenText.trim()] : [tokenText];
          const chunkLower = chunk.toLowerCase();

          let found = -1;
          let foundLen = 0;

          for (const t of candidates) {
            const tLower = t.toLowerCase();
            const idx = chunkLower.indexOf(tLower, searchCursor);
            if (idx !== -1) {
              found = idx;
              foundLen = t.length;
              break;
            }
          }

          if (found === -1 && searchCursor > 0) {
            for (const t of candidates) {
              const tLower = t.toLowerCase();
              const idx = chunkLower.indexOf(tLower);
              if (idx !== -1) {
                found = idx;
                foundLen = t.length;
                break;
              }
            }
          }

          if (found !== -1 && foundLen > 0) {
            start = found;
            end = found + foundLen;
          }
        }
      }
    }

    if (typeof start !== "number" || typeof end !== "number" || end <= start) continue;
    if (end - start < 1) continue;
    if (typeof score === "number" && score < aiThreshold) continue;

    searchCursor = Math.max(searchCursor, end);

    spans.push({
      start,
      end,
      label: normalizeLabel(ent?.entity_group || ent?.entity || ent?.label),
      score: typeof score === "number" ? score : 0.0,
      source: "ner",
    });
  }

  // If model returns nothing, optionally dump token debug once per run.
  if (spans.length === 0 && debug && !didTokenDebug) {
    didTokenDebug = true;
    await debugTokenPredictions(chunk);
  }

  return spans;
}

// =============================================================================
// Span utilities: dedupe, merge, word-boundary expansion
// =============================================================================

function dedupeSpans(spans) {
  const seen = new Set();
  const out = [];
  for (const s of spans) {
    const k = `${s.start}:${s.end}:${s.label}:${s.source || ""}`;
    if (!seen.has(k)) {
      seen.add(k);
      out.push(s);
    }
  }
  return out;
}

function isRegexSpan(s) {
  return typeof s?.source === "string" && s.source.startsWith("regex_");
}

function overlapsOrAdjacent(aStart, aEnd, bStart, bEnd) {
  // include adjacency (aEnd === bStart)
  return aStart <= bEnd && bStart <= aEnd;
}

function mergeOverlapsBestOf(spans) {
  const sorted = [...spans].sort((a, b) => {
    if (a.start !== b.start) return a.start - b.start;
    // Prefer regex then higher score
    const aR = isRegexSpan(a) ? 1 : 0;
    const bR = isRegexSpan(b) ? 1 : 0;
    if (aR !== bR) return bR - aR;
    return (b.score ?? 0) - (a.score ?? 0);
  });

  const out = [];
  for (const s of sorted) {
    const last = out[out.length - 1];
    if (!last || !overlapsOrAdjacent(last.start, last.end, s.start, s.end)) {
      out.push({ ...s });
      continue;
    }

    // Overlapping or adjacent
    const overlapLen = Math.max(0, Math.min(last.end, s.end) - Math.max(last.start, s.start));
    const lastIsRegex = isRegexSpan(last);
    const sIsRegex = isRegexSpan(s);

    // If either is regex and they overlap, prefer regex to avoid double-highlights and prefix-capture.
    if (overlapLen > 0 && (lastIsRegex || sIsRegex)) {
      const keep = lastIsRegex ? last : s;
      out[out.length - 1] = { ...keep };
      continue;
    }

    // If same label, union them (also merges adjacent token pieces nicely)
    if (last.label === s.label) {
      out[out.length - 1] = {
        ...last,
        start: Math.min(last.start, s.start),
        end: Math.max(last.end, s.end),
        score: Math.max(last.score ?? 0, s.score ?? 0),
        source: last.source || s.source,
      };
      continue;
    }

    // Different labels: only replace if overlap is huge; otherwise keep both.
    const lastLen = Math.max(1, last.end - last.start);
    const sLen = Math.max(1, s.end - s.start);
    const overlapRatio = overlapLen / Math.min(lastLen, sLen);

    if (overlapRatio >= 0.8) {
      if ((s.score ?? 0) > (last.score ?? 0)) out[out.length - 1] = { ...s };
    } else {
      out.push({ ...s });
    }
  }

  return out;
}

/**
 * Expand spans to full word boundaries to prevent partial-word redactions.
 * - Fixes cases like "id[REDACTED]" when the model only tagged part of a token.
 */
function expandToWordBoundaries(spans, fullText) {
  function isWordCharAt(i) {
    if (i < 0 || i >= fullText.length) return false;
    const ch = fullText[i];
    if (/[A-Za-z0-9]/.test(ch)) return true;

    // Treat apostrophe/hyphen as word-char only when adjacent to alnum
    if (ch === "'" || ch === "’" || ch === "-") {
      const left = i > 0 ? fullText[i - 1] : "";
      const right = i + 1 < fullText.length ? fullText[i + 1] : "";
      return /[A-Za-z0-9]/.test(left) || /[A-Za-z0-9]/.test(right);
    }
    return false;
  }

  return spans.map((span) => {
    let { start, end } = span;

    while (start > 0 && isWordCharAt(start - 1)) start--;
    while (end < fullText.length && isWordCharAt(end)) end++;

    if (start !== span.start || end !== span.end) {
      return { ...span, start, end, text: fullText.slice(start, end) };
    }
    return span;
  });
}

// =============================================================================
// Debug helpers (optional)
// =============================================================================

function formatTokenPreview(token) {
  const word =
    typeof token?.word === "string"
      ? token.word
      : typeof token?.token === "string"
      ? token.token
      : typeof token?.text === "string"
      ? token.text
      : typeof token?.index === "number"
      ? String(token.index)
      : "(tok)";
  const label = normalizeLabel(token?.entity || token?.entity_group || token?.label);
  const score = typeof token?.score === "number" ? token.score : 0;
  return `${word} -> ${label} (${score.toFixed(3)})`;
}

async function debugTokenPredictions(chunk) {
  if (!debug || !classifier) return;
  try {
    let tokenRaw;
    try {
      tokenRaw = await classifier(chunk, {
        aggregation_strategy: "none",
        ignore_labels: [],
        return_offsets_mapping: true,
        topk: 1,
      });
    } catch (err) {
      log("[PHI] token preds debug (with offsets) failed; retrying without offsets:", err);
      tokenRaw = await classifier(chunk, {
        aggregation_strategy: "none",
        ignore_labels: [],
        topk: 1,
      });
    }

    const tokenList = normalizeRawOutput(tokenRaw);
    log("[PHI] token preds count:", tokenList.length);
    if (tokenList.length > 0) {
      log("[PHI] token preds preview:", tokenList.slice(0, 10).map(formatTokenPreview));
      return;
    }
  } catch (err) {
    log("[PHI] token preds debug failed:", err);
  }

  if (didLogitsDebug) return;
  didLogitsDebug = true;

  try {
    const inputs = await classifier.tokenizer(chunk, { return_tensors: "np" });
    const out = await classifier.model(inputs);
    const logits = out?.logits;
    log("[PHI] logits dims:", logits?.dims);
    const data = logits?.data;
    log("[PHI] logits sample:", data ? Array.from(data.slice(0, 20)) : null);
  } catch (err) {
    log("[PHI] logits debug failed:", err);
  }
}

// =============================================================================
// Worker message loop
// =============================================================================

self.onmessage = async (e) => {
  const msg = e.data;
  if (!msg || typeof msg.type !== "string") return;

  if (msg.type === "cancel") {
    cancelled = true;
    return;
  }

  if (msg.type === "init") {
    cancelled = false;
    didTokenDebug = false;
    didLogitsDebug = false;

    const config = msg.config && typeof msg.config === "object" ? msg.config : {};
    debug = Boolean(msg.debug ?? config.debug);

    try {
      await loadProtectedTerms();
      await loadModel(config);
      post("ready");
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    }
    return;
  }

  if (msg.type === "start") {
    cancelled = false;
    didTokenDebug = false;
    didLogitsDebug = false;

    try {
      await loadProtectedTerms();

      const text = String(msg.text || "");
      const config = msg.config && typeof msg.config === "object" ? msg.config : {};
      debug = Boolean(config.debug);

      await loadModel(config);

      const aiThreshold = typeof config.aiThreshold === "number" ? config.aiThreshold : 0.45;

      const allSpans = [];
      const windowCount = Math.max(1, Math.ceil(Math.max(0, text.length - OVERLAP) / STEP));
      let windowIndex = 0;

      post("progress", { stage: "Running detection (local model)…", windowIndex, windowCount });

      for (let start = 0; start < text.length; start += STEP) {
        const end = Math.min(text.length, start + WINDOW);
        const chunk = text.slice(start, end);

        // Avoid an extra tiny tail window (often low signal / higher false positives)
        if (start > 0 && chunk.length < 50) break;

        windowIndex += 1;

        // 1) ML spans (robust offsets)
        const nerSpans = await runNER(chunk, aiThreshold);

        // 2) Regex injection spans (header guarantees)
        const regexSpans = runRegexDetectors(chunk);

        // 3) Combine (still chunk-relative)
        const combined = dedupeSpans([...nerSpans, ...regexSpans]);

        // 4) Convert to absolute offsets
        for (const s of combined) {
          allSpans.push({
            ...s,
            start: s.start + start,
            end: s.end + start,
          });
        }

        post("progress", { windowIndex, windowCount });
        if (cancelled) break;
      }

      // 5) Merge/dedupe across windows
      let merged = mergeOverlapsBestOf(allSpans);

      // 6) Expand to word boundaries (fixes partial-word redactions)
      merged = expandToWordBoundaries(merged, text);

      // 7) Re-merge after expansion
      merged = mergeOverlapsBestOf(merged);

      // 8) Apply veto (protected allow-list)
      merged = applyVeto(merged, text, protectedTerms, { debug });

      post("done", { detections: merged });
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    }
  }
};
