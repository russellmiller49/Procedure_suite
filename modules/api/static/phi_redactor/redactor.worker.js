import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.0";

// Allow loading model artifacts from same-origin static files (vendored snapshot).
env.allowLocalModels = true;
env.useBrowserCache = true;

// Official WASM path setting (best-effort if shape differs across versions)
if (env.backends?.onnx?.wasm) {
  // Important for COOP/COEP pages: Transformers.js may try to spin up an ONNXRuntime "proxy worker".
  // If the Transformers.js bundle is imported cross-origin (e.g. from jsDelivr), that nested Worker
  // can fail with a SecurityError due to CORS. We disable the proxy worker and run WASM in-process.
  env.backends.onnx.wasm.proxy = false;
  // Avoid threaded WASM (which also spawns extra workers) unless we explicitly vendor runtime assets.
  env.backends.onnx.wasm.numThreads = 1;
  env.backends.onnx.wasm.wasmPaths =
    "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.0/dist/";
}

const REMOTE_MODEL_ID = "onnx-community/piiranha-v1-detect-personal-information-ONNX";
// Local vendor folder name (served from `/ui/phi_redactor/vendor/...` by FastAPI static files)
const LOCAL_MODEL_ID = "piiranha-v1-detect-personal-information-ONNX";
const LOCAL_VENDOR_ROOT = new URL("./vendor/", import.meta.url).toString(); // ends with /
let resolvedModelId = null;
let resolveModelPromise = null;

async function getModelId() {
  if (resolvedModelId) return resolvedModelId;
  if (resolveModelPromise) return resolveModelPromise;

  resolveModelPromise = (async () => {
    // If a vendored snapshot exists, prefer it. Otherwise, fall back to Hugging Face.
    try {
      const cfg = new URL(`./vendor/${LOCAL_MODEL_ID}/config.json`, import.meta.url).toString();
      const r = await fetch(cfg, { method: "HEAD" });
      if (r.ok) {
        // Point Transformers.js downloads at our same-origin vendor folder.
        // Default is:
        //   remoteHost: "https://huggingface.co/"
        //   remotePathTemplate: "{model}/resolve/{revision}/"
        // For local vendoring we keep it simple and fetch:
        //   `${LOCAL_VENDOR_ROOT}{model}/{file}`
        env.remoteHost = LOCAL_VENDOR_ROOT;
        env.remotePathTemplate = "{model}/";

        console.log(
          "[PHI Worker] Using vendored Piiranha model:",
          `${LOCAL_VENDOR_ROOT}${LOCAL_MODEL_ID}/`
        );
        resolvedModelId = LOCAL_MODEL_ID;
        return resolvedModelId;
      }
    } catch (e) {
      // ignore; we'll fall back to remote
    }
    // Restore default Hugging Face host/template for remote fetch.
    env.remoteHost = "https://huggingface.co/";
    env.remotePathTemplate = "{model}/resolve/{revision}/";
    console.log("[PHI Worker] Using remote Piiranha model:", REMOTE_MODEL_ID);
    resolvedModelId = REMOTE_MODEL_ID;
    return resolvedModelId;
  })();

  return resolveModelPromise;
}
const TASK = "token-classification";

const WINDOW = 2500;
const OVERLAP = 250;
const STEP = WINDOW - OVERLAP;

let nerPipeline = null;
let allowlistTrie = null;
let maxTermLen = 48;

let cancelled = false;
let running = false;
let allowlistPromise = null;
let nerPromise = null;
let nerLoadFailed = false;

function post(type, payload = {}) {
  self.postMessage({ type, ...payload });
}

function isAlphaNum(ch) {
  const code = ch.charCodeAt(0);
  return (
    (code >= 48 && code <= 57) ||
    (code >= 65 && code <= 90) ||
    (code >= 97 && code <= 122)
  );
}

function overlaps(aStart, aEnd, bStart, bEnd) {
  return aStart < bEnd && bStart < aEnd;
}

function binarySearchLastLE(arr, x) {
  let lo = 0;
  let hi = arr.length - 1;
  let best = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid].start <= x) {
      best = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  return best;
}

function makeProtectedChecker(protectedRanges) {
  const sorted = [...protectedRanges].sort((a, b) => a.start - b.start);
  return (start, end) => {
    if (!sorted.length) return false;
    const idx = binarySearchLastLE(sorted, start);
    const cand = [];
    if (idx >= 0) cand.push(sorted[idx]);
    if (idx + 1 < sorted.length) cand.push(sorted[idx + 1]);
    for (const r of cand) {
      if (overlaps(start, end, r.start, r.end)) return true;
    }
    return false;
  };
}

function trieScanProtectedRanges(text, trie) {
  if (!trie) return [];
  const lower = text.toLowerCase();
  const ranges = [];

  for (let i = 0; i < lower.length; i++) {
    let node = trie;
    for (let j = i; j < lower.length && j - i < maxTermLen; j++) {
      const ch = lower[j];
      node = node?.[ch];
      if (!node) break;
      if (node.$) {
        const start = i;
        const end = j + 1;
        const leftOk = start === 0 || !isAlphaNum(text[start - 1]);
        const rightOk = end === text.length || !isAlphaNum(text[end]);
        if (leftOk && rightOk) ranges.push({ start, end });
      }
    }
  }

  ranges.sort((a, b) => a.start - b.start);
  const merged = [];
  for (const r of ranges) {
    const last = merged[merged.length - 1];
    if (!last || r.start > last.end) merged.push({ ...r });
    else last.end = Math.max(last.end, r.end);
  }
  return merged;
}

function normalizeLabel(entity) {
  if (!entity) return "PHI";
  const raw = String(entity).toUpperCase();
  const stripped = raw.replace(/^B-/, "").replace(/^I-/, "");
  return stripped;
}

function makeId(span) {
  return `${span.source}:${span.label}:${span.start}:${span.end}`;
}

function maskSpans(text, spans) {
  if (!spans.length) return text;
  const chars = text.split("");
  for (const s of spans) {
    const start = Math.max(0, Math.min(text.length, s.start));
    const end = Math.max(0, Math.min(text.length, s.end));
    for (let i = start; i < end; i++) chars[i] = " ";
  }
  return chars.join("");
}

function runRegexDetections(maskedText) {
  const detections = [];

  const patterns = [
    // Patient name from header (e.g., "Patient: Thompson, Margaret A.")
    { label: "PATIENT_NAME", score: 0.95, re: /(?:^|\n)\s*(?:Patient(?:\s+Name)?|Pt|Name|Subject)\s*[:\-]\s*([A-Z][a-z]+(?:,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?)?)/gm },
    { label: "EMAIL", score: 0.98, re: /\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b/g },
    { label: "SSN", score: 0.98, re: /\b\d{3}-\d{2}-\d{4}\b/g },
    { label: "PHONE", score: 0.9, re: /\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g },
    { label: "DOB", score: 0.95, re: /\b(?:DOB|Date\s*of\s*Birth|Birth\s*Date|Born)\s*[:\-]?\s*\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b/gi },
    { label: "MRN", score: 0.95, re: /\b(?:MRN|Medical\s*Record(?:\s*Number)?|Patient\s*ID|ID|Accession|CSN)\s*[:#\-]?\s*[A-Z0-9\-]{4,15}\b/gi },
    { label: "ADDRESS", score: 0.6, re: /\b\d{1,5}\s+[A-Za-z0-9][A-Za-z0-9.\-]*(?:\s+[A-Za-z0-9][A-Za-z0-9.\-]*){0,4}\s+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Ln|Lane|Dr|Drive|Ct|Court|Way|Pkwy|Parkway)\b\.?/g },
    { label: "DATE", score: 0.55, re: /\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b/g },
    // Facility with City, State pattern
    { label: "FACILITY", score: 0.85, re: /\b(?:Facility|Location|Hospital|Clinic)\s*[:\-]\s*([A-Z][a-zA-Z\s]+(?:Medical\s+Center|Hospital|Clinic|Healthcare)[,\s]+[A-Z][a-z]+[,\s]+[A-Z]{2})\b/g },
  ];

  for (const p of patterns) {
    p.re.lastIndex = 0;
    let m;
    while ((m = p.re.exec(maskedText)) !== null) {
      const start = m.index;
      const end = m.index + m[0].length;
      detections.push({
        start,
        end,
        label: p.label,
        score: p.score,
        source: "regex",
      });
      if (m.index === p.re.lastIndex) p.re.lastIndex++;
    }
  }

  return detections;
}

function mergeOverlaps(spans) {
  const sorted = [...spans].sort((a, b) => {
    if (a.start !== b.start) return a.start - b.start;
    return (b.score ?? 0) - (a.score ?? 0);
  });

  const out = [];
  for (const s of sorted) {
    const last = out[out.length - 1];
    if (!last) {
      out.push({ ...s });
      continue;
    }
    if (!overlaps(last.start, last.end, s.start, s.end)) {
      out.push({ ...s });
      continue;
    }
    const lastScore = last.score ?? 0;
    const thisScore = s.score ?? 0;

    if (last.label === s.label) {
      last.end = Math.max(last.end, s.end);
      last.score = Math.max(lastScore, thisScore);
    } else if (thisScore > lastScore) {
      out[out.length - 1] = { ...s };
    }
  }
  return out;
}

async function loadNER() {
  // Transformers.js v3 executes CPU inference via `device: "wasm"` (or "webgpu" when available),
  // not `device: "cpu"`. Also, some combinations of `dtype` + `model_file_name` can cause
  // Transformers.js to synthesize a filename that doesn't exist on Hugging Face (e.g.
  // `model_int8.onnx_quantized.onnx`). To keep things robust, we try only known-good filenames.
  //
  // See: onnx-community/piiranha-v1-detect-personal-information-ONNX artifacts (e.g.
  // `onnx/model_quantized.onnx`, `onnx/model_int8.onnx`, `onnx/model_uint8.onnx`, `onnx/model.onnx`).
  const tries = [
    // Prefer quantized variants (smaller download, faster local inference).
    // NOTE: In Transformers.js v3, the ONNX filename is built as:
    //   `${subfolder}/${model_file_name}${dtype_suffix}.onnx`
    // So `model_file_name` must NOT include ".onnx" or you can end up with
    // "model.onnx_quantized.onnx". We therefore pass base names here.
    //
    // We also set dtype:"fp32" to prevent Transformers.js from auto-appending a dtype suffix
    // (e.g. "_quantized") based on the device default.
    { device: "wasm", dtype: "fp32", subfolder: "onnx", model_file_name: "model_quantized" },
    { device: "wasm", dtype: "fp32", subfolder: "onnx", model_file_name: "model_int8" },
    { device: "wasm", dtype: "fp32", subfolder: "onnx", model_file_name: "model_uint8" },
    // Last resort: unquantized model (can be much larger).
    { device: "wasm", dtype: "fp32", subfolder: "onnx", model_file_name: "model" },
  ];

  let lastErr = null;
  const modelId = await getModelId();
  for (const opts of tries) {
    try {
      console.log("[PHI Worker] Trying to load NER model with options:", opts);
      const p = await pipeline(TASK, modelId, opts);
      console.log("[PHI Worker] NER model loaded successfully");
      return p;
    } catch (e) {
      const msg = String(e?.message || e);
      console.warn("[PHI Worker] NER load attempt failed:", msg);
      lastErr = e;
    }
  }
  console.error("[PHI Worker] All NER load attempts failed");
  throw lastErr;
}

async function runNER(chunk, aiThreshold) {
  if (!nerPipeline) {
    console.log("[PHI Worker] NER pipeline not available, skipping AI detection");
    return [];
  }

  const raw = await nerPipeline(chunk, { aggregation_strategy: "simple" });
  const spans = [];
  for (const ent of raw || []) {
    const start = ent.start ?? null;
    const end = ent.end ?? null;
    const score = ent.score ?? null;
    if (typeof start !== "number" || typeof end !== "number" || end <= start) continue;
    if (typeof score === "number" && score < aiThreshold) continue;
    spans.push({
      start,
      end,
      label: normalizeLabel(ent.entity_group || ent.entity),
      score: typeof score === "number" ? score : 0.0,
      source: "ner",
    });
  }
  return spans;
}

async function ensureAllowlistReady() {
  if (allowlistTrie !== null) return;
  if (allowlistPromise) return allowlistPromise;

  allowlistPromise = (async () => {
    console.log("[PHI Worker] Loading allowlist...");
    post("progress", { windowIndex: 0, windowCount: 0, stage: "Loading allowlist…" });
    try {
      const trieUrl = new URL("./allowlist_trie.json", import.meta.url);
      const trieJson = await fetch(trieUrl).then((r) => {
        if (!r.ok) throw new Error(`Failed to load allowlist_trie.json (${r.status})`);
        return r.json();
      });
      allowlistTrie = trieJson.trie || trieJson;
      maxTermLen = trieJson.max_term_len || 48;
    } catch (e) {
      console.warn("[PHI Worker] Failed to load allowlist trie, using empty:", e?.message);
      allowlistTrie = {};
      maxTermLen = 48;
    }
  })();

  try {
    await allowlistPromise;
  } finally {
    // keep promise for reuse; no-op
  }
}

function ensureNERLoadingStarted() {
  if (nerPipeline || nerLoadFailed) return;
  if (nerPromise) return;

  nerPromise = (async () => {
    post("progress", {
      windowIndex: 0,
      windowCount: 0,
      stage: "Downloading AI model… (runs locally; may take minutes)",
    });
    try {
      nerPipeline = await loadNER();
      post("progress", {
        windowIndex: 0,
        windowCount: 0,
        stage: "AI model ready (rerun detection to include AI spans)",
      });
    } catch (e) {
      nerLoadFailed = true;
      nerPipeline = null;
      const msg = String(e?.message || e);
      console.warn("[PHI Worker] NER model unavailable; regex-only mode:", msg);
      post("progress", {
        windowIndex: 0,
        windowCount: 0,
        stage: `AI model failed to load: ${msg}`,
      });
    }
  })();
}

self.onmessage = async (e) => {
  const msg = e.data;
  if (!msg || typeof msg.type !== "string") return;

  if (msg.type === "cancel") {
    cancelled = true;
    return;
  }

  if (msg.type === "init") {
    try {
      await ensureAllowlistReady();
      ensureNERLoadingStarted(); // load in background; don't block readiness
      post("ready");
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    }
    return;
  }

  if (msg.type === "start") {
    if (running) return;
    running = true;
    cancelled = false;
    try {
      await ensureAllowlistReady();
      ensureNERLoadingStarted();

      const text = String(msg.text || "");
      const config = msg.config || {};
      const aiThreshold =
        typeof config.aiThreshold === "number" ? config.aiThreshold : 0.85;

      const protectedRanges = trieScanProtectedRanges(text, allowlistTrie);
      const isProtected = makeProtectedChecker(protectedRanges);

      const allSpans = [];

      const windowCount = Math.max(
        1,
        Math.ceil(Math.max(0, text.length - OVERLAP) / STEP)
      );
      let windowIndex = 0;

      post("progress", {
        windowIndex: 0,
        windowCount,
        stage: nerPipeline
          ? "Running detection (AI + regex)…"
          : "Running detection (regex-only; AI model downloading)…",
      });

      for (let start = 0; start < text.length; start += STEP) {
        const end = Math.min(text.length, start + WINDOW);
        const chunk = text.slice(start, end);
        windowIndex += 1;

        const nerSpansLocal = await runNER(chunk, aiThreshold);
        const masked = maskSpans(chunk, nerSpansLocal);
        const regexSpansLocal = runRegexDetections(masked);

        const mergedLocal = mergeOverlaps([...nerSpansLocal, ...regexSpansLocal]);
        const abs = mergedLocal
          .map((s) => ({
            ...s,
            start: s.start + start,
            end: s.end + start,
          }))
          .filter((s) => !isProtected(s.start, s.end))
          .map((s) => ({ ...s, id: makeId(s) }));

        allSpans.push(...abs);

        post("progress", { windowIndex, windowCount });
        post("detections_delta", { windowIndex, detections: abs });

        if (cancelled) break;
      }

      const mergedAll = mergeOverlaps(allSpans)
        .filter((s) => !isProtected(s.start, s.end))
        .map((s) => ({ ...s, id: makeId(s) }));

      post("done", { detections: mergedAll });
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    } finally {
      running = false;
    }
  }
};
