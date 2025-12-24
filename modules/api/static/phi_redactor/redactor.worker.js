import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2";
import { applyVeto } from "./protectedVeto.js";

const MODEL_PATH = "./vendor/phi_distilbert_ner/";
const MODEL_ID = "phi_distilbert_ner";
const MODEL_BASE_URL = new URL("./vendor/", import.meta.url).toString();
const TASK = "token-classification";
const WINDOW = 2500;
const OVERLAP = 250;
const STEP = WINDOW - OVERLAP;

// =============================================================================
// HYBRID REGEX DETECTION (ported from phi_redactor_hybrid.py)
// =============================================================================

// Matches: "Patient: Smith, John" or "Pt Name: John Smith"
const PATIENT_HEADER_RE =
  /(?:Patient(?:\s+Name)?|Pt|Name|Subject)\s*[:\-]?\s*([A-Z][a-z]+,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?|[A-Z][a-z]+\s+[A-Z]'?[A-Za-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)/gim;

// Matches: "MRN: 12345" or "ID: 55-22-11"
const MRN_RE =
  /\b(?:MRN|MR|Medical\s*Record|Patient\s*ID|ID|EDIPI|DOD\s*ID)\s*[:\#]?\s*([A-Z0-9\-]{4,15})\b/gi;

env.allowLocalModels = true;
env.allowRemoteModels = false;
env.localModelPath = MODEL_BASE_URL;
// Temporarily disable browser cache to force reload of updated model (v2)
// Can re-enable once all users have the new model cached
env.useBrowserCache = false;
if (env.backends?.onnx?.wasm) {
  env.backends.onnx.wasm.proxy = false;
  // Avoid cross-origin worker requirements under COEP by staying single-threaded.
  env.backends.onnx.wasm.numThreads = 1;
}

let classifier = null;
let classifierQuantized = null;
let classifierUnquantized = null;
let protectedTerms = null;
let modelPromiseQuantized = null;
let modelPromiseUnquantized = null;
let termsPromise = null;
let cancelled = false;
let debug = false;
let workerConfig = {};
let didLogitsDebug = false;
let didTokenDebug = false;

function log(...args) {
  if (debug) console.log(...args);
}

function post(type, payload = {}) {
  self.postMessage({ type, ...payload });
}

function overlapsOrAdjacent(aStart, aEnd, bStart, bEnd) {
  // Use <= to include adjacent spans (where aEnd === bStart)
  // This ensures entities like dates "01/01/1970" get merged even when
  // tokenized into adjacent pieces: (24,26), (26,27), (27,29), etc.
  return aStart <= bEnd && bStart <= aEnd;
}

function mergeOverlaps(spans) {
  const sorted = [...spans].sort((a, b) => {
    if (a.start !== b.start) return a.start - b.start;
    return (b.score ?? 0) - (a.score ?? 0);
  });

  const out = [];
  for (const s of sorted) {
    const last = out[out.length - 1];
    if (!last || !overlapsOrAdjacent(last.start, last.end, s.start, s.end)) {
      out.push({ ...s });
      continue;
    }
    if (last.label === s.label) {
      last.end = Math.max(last.end, s.end);
      last.score = Math.max(last.score ?? 0, s.score ?? 0);
    } else {
      // If labels differ, be conservative: don't drop one unless overlap is substantial.
      const overlapLen = Math.max(0, Math.min(last.end, s.end) - Math.max(last.start, s.start));
      const lastLen = Math.max(1, last.end - last.start);
      const sLen = Math.max(1, s.end - s.start);
      const overlapRatio = overlapLen / Math.min(lastLen, sLen);

      // Only replace when the overlap is very large; otherwise keep both.
      if (overlapRatio >= 0.8) {
        if ((s.score ?? 0) > (last.score ?? 0)) out[out.length - 1] = { ...s };
      } else {
        out.push({ ...s });
      }
    }
  }
  return out;
}

function normalizeLabel(entity) {
  if (!entity) return "PHI";
  const raw = String(entity).toUpperCase();
  return raw.replace(/^B-/, "").replace(/^I-/, "");
}

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

  // Try quantized first (optional). If missing/unsupported, fall back to unquantized.
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

function normalizeRawOutput(raw) {
  if (Array.isArray(raw)) return raw;
  if (!raw || typeof raw !== "object") return [];
  if (Array.isArray(raw.data)) return raw.data;
  if (Array.isArray(raw.entities)) return raw.entities;
  return [];
}

function toFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function toFiniteInt(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  return Number.isInteger(value) ? value : Math.trunc(value);
}

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
  log("[PHI] aiThreshold", aiThreshold);
  const raw = await classifier(chunk, {
    aggregation_strategy: "simple",
    ignore_labels: ["O"],
  });
  const rawList = normalizeRawOutput(raw);
  log("[PHI] raw spans (simple) count:", rawList.length);
  log("[PHI] rawList[0] keys", rawList[0] ? Object.keys(rawList[0]) : null);
  log("[PHI] rawList sample", rawList.slice(0, 2));
  if (rawList.length === 0 && !didTokenDebug) {
    didTokenDebug = true;
    await debugTokenPredictions(chunk);
  }
  const spans = [];
  let offsets = null;
  let offsetsTried = false;
  let searchCursor = 0;
  for (const ent of rawList) {
    let start = toFiniteNumber(ent?.start) ?? toFiniteNumber(ent?.start_offset) ?? toFiniteNumber(ent?.begin);
    let end = toFiniteNumber(ent?.end) ?? toFiniteNumber(ent?.end_offset) ?? toFiniteNumber(ent?.finish);
    const score =
      toFiniteNumber(ent?.score) ??
      toFiniteNumber(ent?.confidence) ??
      toFiniteNumber(ent?.probability) ??
      null;

    // Some pipeline outputs omit char offsets (or return token indices); recover via tokenizer offsets.
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
        tokenIndex !== null || startTokenIndex !== null || endTokenIndex !== null || Boolean(getEntityText(ent));
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

      // Last-resort: find the token text in the chunk.
      // Use case-insensitive search because tokenizer may lowercase tokens
      // (e.g., "john" from tokenizer vs "John" in original text).
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
    // Minimum span length guard: filter single-character/punctuation detections.
    if (end - start < 1) continue;
    if (typeof score === "number" && score < aiThreshold) continue;
    searchCursor = Math.max(searchCursor, end);
    spans.push({
      start,
      end,
      label: normalizeLabel(ent.entity_group || ent.entity || ent.label),
      score: typeof score === "number" ? score : 0.0,
      source: "ner",
    });
  }
  return spans;
}

/**
 * Deterministic regex detectors for structured header PHI.
 * Returns spans with score 1.0 so they survive thresholding.
 * IMPORTANT: reset lastIndex because these are global regexes reused across chunks.
 */
function runRegexDetectors(text) {
  const spans = [];

  // Reset regex state (global regexes can carry lastIndex across calls)
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
        label: "PATIENT", // align with existing label schema
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

/**
 * Deduplicate spans to prevent double-highlights when ML + regex find the same span.
 */
function dedupeSpans(spans) {
  const seen = new Set();
  const out = [];
  for (const s of spans) {
    const k = `${s.start}:${s.end}:${s.label}`;
    if (!seen.has(k)) {
      seen.add(k);
      out.push(s);
    }
  }
  return out;
}

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
        ignore_labels: [], // critical: reveal O tokens
        return_offsets_mapping: true,
        topk: 1,
      });
    } catch (err) {
      log(
        "[PHI] token preds debug (with return_offsets_mapping) failed; retrying without offsets:",
        err
      );
      tokenRaw = await classifier(chunk, {
        aggregation_strategy: "none",
        ignore_labels: [], // critical: reveal O tokens
        topk: 1,
      });
    }

    const tokenList = normalizeRawOutput(tokenRaw);
    log("[PHI] token preds count:", tokenList.length);
    if (tokenList.length > 0) {
      let oCount = 0;
      for (const t of tokenList) {
        if (normalizeLabel(t?.entity || t?.entity_group || t?.label) === "O") oCount += 1;
      }
      const nonOCount = tokenList.length - oCount;
      log(`[PHI] token preds label counts: total=${tokenList.length} O=${oCount} nonO=${nonOCount}`);
      log(
        "[PHI] token has offsets? (word,start,end,label):",
        tokenList.slice(0, 5).map((t) => [
          t?.word ?? t?.token ?? t?.text ?? "(tok)",
          t?.start,
          t?.end,
          t?.entity ?? t?.label,
        ])
      );
      log(
        "[PHI] token preds preview (incl O):",
        tokenList.slice(0, 10).map(formatTokenPreview)
      );
      return;
    }
  } catch (err) {
    log("[PHI] token preds debug failed:", err);
  }

  if (didLogitsDebug) return;
  didLogitsDebug = true;

  // Definitive fallback: run the model directly and inspect logits.
  try {
    const inputs = await classifier.tokenizer(chunk, { return_tensors: "np" });
    log("[PHI] tokenizer inputs keys:", Object.keys(inputs || {}));
    const out = await classifier.model(inputs);
    const logits = out?.logits;
    log("[PHI] logits dims:", logits?.dims);
    const data = logits?.data;
    log("[PHI] logits sample:", data ? Array.from(data.slice(0, 20)) : null);
  } catch (err) {
    log("[PHI] logits debug failed:", err);
  }
}

self.onmessage = async (e) => {
  const msg = e.data;
  if (!msg || typeof msg.type !== "string") return;

  if (msg.type === "cancel") {
    cancelled = true;
    return;
  }

  if (msg.type === "init") {
    workerConfig = msg.config && typeof msg.config === "object" ? msg.config : {};
    debug = Boolean(msg.debug ?? workerConfig.debug);
    try {
      await loadProtectedTerms();
      await loadModel(workerConfig);
      post("ready");
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    }
    return;
  }

  if (msg.type === "start") {
    cancelled = false;
    didLogitsDebug = false;
    didTokenDebug = false;
    try {
      await loadProtectedTerms();

      const text = String(msg.text || "");
      const config = msg.config && typeof msg.config === "object" ? msg.config : {};
      workerConfig = config;
      debug = Boolean(config.debug);
      await loadModel(config);
      // Lower default threshold slightly (0.45) to catch borderline entity detections
      // while still filtering low-confidence noise.
      const aiThreshold = typeof config.aiThreshold === "number" ? config.aiThreshold : 0.45;

      const allSpans = [];
      const windowCount = Math.max(1, Math.ceil(Math.max(0, text.length - OVERLAP) / STEP));
      let windowIndex = 0;

      post("progress", { stage: "Running detection (local model)…", windowIndex, windowCount });

      for (let start = 0; start < text.length; start += STEP) {
        const end = Math.min(text.length, start + WINDOW);
        const chunk = text.slice(start, end);
        // Avoid an extra tiny tail window (often low signal / higher false positives).
        if (start > 0 && chunk.length < 50) break;
        windowIndex += 1;

        // 1) Run ML model
        const nerSpans = await runNER(chunk, aiThreshold);

        // 2) Run regex injection (hybrid detection)
        const regexSpans = runRegexDetectors(chunk);
        log("[PHI] regex spans in chunk:", regexSpans.length);

        // 3) Merge and dedupe results
        const combinedSpans = dedupeSpans([...nerSpans, ...regexSpans]);

        // 4) Convert to absolute offsets (chunk -> full text)
        const abs = combinedSpans.map((s) => ({
          ...s,
          start: s.start + start,
          end: s.end + start,
        }));

        allSpans.push(...abs);

        post("progress", { windowIndex, windowCount });
        if (cancelled) break;
      }

      let merged = mergeOverlaps(allSpans);
      log("[PHI] spans before veto", merged.length);
      merged = applyVeto(merged, text, protectedTerms, { debug });
      log("[PHI] spans after veto", merged.length);

      post("done", { detections: merged });
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    }
  }
};
