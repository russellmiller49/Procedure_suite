import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.0";
import { applyVeto } from "./protectedVeto.js";

const MODEL_PATH = "./vendor/phi_distilbert_ner/";
const MODEL_ID = "phi_distilbert_ner";
const MODEL_BASE_URL = new URL("./vendor/", import.meta.url).toString();
const TASK = "token-classification";
const WINDOW = 2500;
const OVERLAP = 250;
const STEP = WINDOW - OVERLAP;

env.allowLocalModels = true;
env.allowRemoteModels = false;
env.localModelPath = MODEL_BASE_URL;
env.useBrowserCache = true;
if (env.backends?.onnx?.wasm) {
  env.backends.onnx.wasm.proxy = false;
  // Avoid cross-origin worker requirements under COEP by staying single-threaded.
  env.backends.onnx.wasm.numThreads = 1;

}

let classifier = null;
let protectedTerms = null;
let modelPromise = null;
let termsPromise = null;
let cancelled = false;
let debug = false;

function log(...args) {
  if (debug) console.log(...args);
}

function post(type, payload = {}) {
  self.postMessage({ type, ...payload });
}

function overlaps(aStart, aEnd, bStart, bEnd) {
  return aStart < bEnd && bStart < aEnd;
}

function mergeOverlaps(spans) {
  const sorted = [...spans].sort((a, b) => {
    if (a.start !== b.start) return a.start - b.start;
    return (b.score ?? 0) - (a.score ?? 0);
  });

  const out = [];
  for (const s of sorted) {
    const last = out[out.length - 1];
    if (!last || !overlaps(last.start, last.end, s.start, s.end)) {
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

async function loadModel() {
  if (classifier) return classifier;
  if (modelPromise) return modelPromise;
  modelPromise = (async () => {
    // Always try quantized first. If the file is missing (404) or the runtime
    // can't load it, we'll fall back to the unquantized model.
    post("progress", { stage: "Loading local PHI model (quantized)…" });
    try {
      classifier = await pipeline(TASK, MODEL_ID, { device: "wasm", quantized: true });
      post("progress", { stage: "AI model ready" });
      return classifier;
    } catch (err) {
      classifier = null;
      log("[PHI Worker] Quantized load failed; falling back to unquantized", err);
    }

    post("progress", { stage: "Loading local PHI model (unquantized)…" });
    classifier = await pipeline(TASK, MODEL_ID, { device: "wasm", quantized: false });
    post("progress", { stage: "AI model ready" });
    return classifier;
  })().catch((err) => {
    // Allow retries on subsequent init attempts.
    modelPromise = null;
    throw err;
  });
  return modelPromise;
}

async function runNER(chunk, aiThreshold) {
  if (!classifier) return [];
  const raw = await classifier(chunk, {
    aggregation_strategy: "simple",
    ignore_labels: ["O"],
  });
  const spans = [];
  for (const ent of raw || []) {
    const start = ent.start ?? null;
    const end = ent.end ?? null;
    const score = ent.score ?? null;
    if (typeof start !== "number" || typeof end !== "number" || end <= start) continue;
    // Minimum span length guard: filter single-character/punctuation detections.
    if (end - start < 2) continue;
    if (typeof score === "number" && score < aiThreshold) continue;
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

self.onmessage = async (e) => {
  const msg = e.data;
  if (!msg || typeof msg.type !== "string") return;

  if (msg.type === "cancel") {
    cancelled = true;
    return;
  }

  if (msg.type === "init") {
    debug = Boolean(msg.debug);
    try {
      await loadProtectedTerms();
      await loadModel();
      post("ready");
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    }
    return;
  }

  if (msg.type === "start") {
    cancelled = false;
    try {
      await loadProtectedTerms();
      await loadModel();

      const text = String(msg.text || "");
      const config = msg.config || {};
      const aiThreshold = typeof config.aiThreshold === "number" ? config.aiThreshold : 0.3;

      const allSpans = [];
      const windowCount = Math.max(1, Math.ceil(Math.max(0, text.length - OVERLAP) / STEP));
      let windowIndex = 0;

      post("progress", { stage: "Running detection (local model)…", windowIndex, windowCount });

      for (let start = 0; start < text.length; start += STEP) {
        const end = Math.min(text.length, start + WINDOW);
        const chunk = text.slice(start, end);
        // Avoid an extra tiny tail window (often low signal / higher false positives).
        if (chunk.length < 50) break;
        windowIndex += 1;

        const nerSpans = await runNER(chunk, aiThreshold);
        const abs = nerSpans.map((s) => ({
          ...s,
          start: s.start + start,
          end: s.end + start,
        }));
        allSpans.push(...abs);

        post("progress", { windowIndex, windowCount });
        if (cancelled) break;
      }

      let merged = mergeOverlaps(allSpans);
      merged = applyVeto(merged, text, protectedTerms, { debug });

      post("done", { detections: merged });
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    }
  }
};
