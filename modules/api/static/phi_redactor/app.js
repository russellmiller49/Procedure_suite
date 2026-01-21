/* global monaco */

const statusTextEl = document.getElementById("statusText");
const progressTextEl = document.getElementById("progressText");
const detectionsListEl = document.getElementById("detectionsList");
const detectionsCountEl = document.getElementById("detectionsCount");
const serverResponseEl = document.getElementById("serverResponse");

const runBtn = document.getElementById("runBtn");
const cancelBtn = document.getElementById("cancelBtn");
const applyBtn = document.getElementById("applyBtn");
const revertBtn = document.getElementById("revertBtn");
const submitBtn = document.getElementById("submitBtn");
const exportBtn = document.getElementById("exportBtn");
const addRedactionBtn = document.getElementById("addRedactionBtn");
const entityTypeSelect = document.getElementById("entityTypeSelect");

let lastServerResponse = null;

/**
 * Get merge mode from query param or localStorage.
 * - ?merge=union (default, safer - keeps all candidates until after veto)
 * - ?merge=best_of (legacy - may lose ML spans if regex span is vetoed)
 * - localStorage.phi_merge_mode (persistent dev override)
 */
function getConfiguredMergeMode() {
  const params = new URLSearchParams(location.search);
  const qp = params.get("merge");
  if (qp === "union" || qp === "best_of") return qp;

  const ls = localStorage.getItem("phi_merge_mode");
  if (ls === "union" || ls === "best_of") return ls;

  return "union"; // default: safer mode
}

const WORKER_CONFIG = {
  aiThreshold: 0.5,
  debug: true,
  // Quantized INT8 ONNX can silently collapse to all-"O" under WASM.
  // Keep this ON until quantized inference is validated end-to-end.
  forceUnquantized: true,
  // Merge mode: "union" (default, safer) or "best_of" (legacy)
  mergeMode: getConfiguredMergeMode(),
};

runBtn.disabled = true;
cancelBtn.disabled = true;
applyBtn.disabled = true;
revertBtn.disabled = true;
submitBtn.disabled = true;
if (exportBtn) exportBtn.disabled = true;

function setStatus(text) {
  statusTextEl.textContent = text;
}

function setProgress(text) {
  progressTextEl.textContent = text || "";
}

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

function buildLineStartOffsets(text) {
  const starts = [0];
  for (let i = 0; i < text.length; i++) {
    if (text.charCodeAt(i) === 10) starts.push(i + 1);
  }
  return starts;
}

function offsetToPosition(offset, lineStarts, textLength) {
  const safeOffset = clamp(offset, 0, textLength);

  let lo = 0;
  let hi = lineStarts.length - 1;
  let best = 0;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (lineStarts[mid] <= safeOffset) {
      best = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  const lineStart = lineStarts[best] ?? 0;
  return { lineNumber: best + 1, column: safeOffset - lineStart + 1 };
}

function formatScore(score) {
  if (typeof score !== "number") return "—";
  return score.toFixed(2);
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "className") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on") && typeof v === "function") {
      node.addEventListener(k.slice(2).toLowerCase(), v);
    } else if (v != null) {
      node.setAttribute(k, String(v));
    }
  }
  for (const child of children) node.appendChild(child);
  return node;
}

function safeSnippet(text, start, end) {
  const s = clamp(start, 0, text.length);
  const e = clamp(end, 0, text.length);
  const raw = text.slice(s, e);
  const oneLine = raw.replace(/\s+/g, " ").trim();
  if (oneLine.length <= 120) return oneLine || "(empty)";
  return `${oneLine.slice(0, 117)}…`;
}

/**
 * Render the formatted results from the server response.
 * Shows status banner, CPT codes table, and registry form.
 */
function renderResults(data) {
  const statusBanner = document.getElementById("statusBanner");
  const cptSection = document.getElementById("cptSection");
  const registrySection = document.getElementById("registrySection");
  const serverResponse = document.getElementById("serverResponse");

  lastServerResponse = data;
  if (exportBtn) exportBtn.disabled = !data;

  // Show raw JSON in collapsible section
  serverResponse.textContent = JSON.stringify(data, null, 2);

  // Render status banner
  if (data.needs_manual_review) {
    statusBanner.className = "status-banner error";
    statusBanner.textContent = "⚠️ Manual review required";
  } else if (data.audit_warnings?.length > 0) {
    statusBanner.className = "status-banner warning";
    statusBanner.textContent = `⚠️ ${data.audit_warnings.length} warning(s) - review recommended`;
  } else {
    statusBanner.className = "status-banner success";
    const difficulty = data.coder_difficulty || "HIGH_CONF";
    statusBanner.textContent = `✓ High confidence extraction (${difficulty})`;
  }
  statusBanner.classList.remove("hidden");

  // Render CPT table
  if (data.suggestions?.length > 0 || data.cpt_codes?.length > 0) {
    renderCPTTable(data);
    cptSection.classList.remove("hidden");
  } else {
    cptSection.classList.add("hidden");
  }

  // Render registry form
  if (data.registry) {
    renderRegistryForm(data.registry);
    registrySection.classList.remove("hidden");
  } else {
    registrySection.classList.add("hidden");
  }
}

/**
 * Render the CPT codes table with descriptions, confidence, RVU, and payment.
 */
function renderCPTTable(data) {
  const tbody = document.getElementById("cptTableBody");
  const suggestions = data.suggestions || [];
  const billing = data.per_code_billing || [];

  // Create billing lookup
  const billingMap = {};
  billing.forEach(b => billingMap[b.cpt_code] = b);

  let rows = "";

  // If we have suggestions, use those (more detailed)
  if (suggestions.length > 0) {
    suggestions.forEach((s) => {
      const b = billingMap[s.code] || {};
      const confidence = s.confidence ? `${(s.confidence * 100).toFixed(0)}%` : "—";
      const rvu = b.work_rvu?.toFixed(2) || "—";
      const payment = b.facility_payment ? `$${b.facility_payment.toFixed(2)}` : "—";

      rows += `
        <tr>
          <td><code>${s.code}</code></td>
          <td>${s.description || "—"}</td>
          <td>${confidence}</td>
          <td>${rvu}</td>
          <td>${payment}</td>
        </tr>
      `;
    });
  } else if (data.cpt_codes?.length > 0) {
    // Fallback to simple cpt_codes list
    data.cpt_codes.forEach((code) => {
      const b = billingMap[code] || {};
      const rvu = b.work_rvu?.toFixed(2) || "—";
      const payment = b.facility_payment ? `$${b.facility_payment.toFixed(2)}` : "—";

      rows += `
        <tr>
          <td><code>${code}</code></td>
          <td>${b.description || "—"}</td>
          <td>—</td>
          <td>${rvu}</td>
          <td>${payment}</td>
        </tr>
      `;
    });
  } else {
    rows = '<tr><td colspan="5" class="subtle" style="text-align: center;">No CPT codes returned</td></tr>';
  }

  // Totals row
  if (data.total_work_rvu || data.estimated_payment) {
    const totalRvu = data.total_work_rvu?.toFixed(2) || "—";
    const totalPayment = data.estimated_payment ? `$${data.estimated_payment.toFixed(2)}` : "—";
    rows += `
      <tr class="totals-row">
        <td colspan="3"><strong>TOTALS</strong></td>
        <td><strong>${totalRvu}</strong></td>
        <td><strong>${totalPayment}</strong></td>
      </tr>
    `;
  }

  tbody.innerHTML = rows;
}

/**
 * Format a value for display in the registry table.
 * Handles primitives, arrays, and objects.
 */
function formatValueForDisplay(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return String(value);
  if (typeof value === "string") return value;

  if (Array.isArray(value)) {
    if (value.length === 0) return "—";
    // Check if array contains objects
    if (typeof value[0] === "object" && value[0] !== null) {
      // For arrays of objects, extract meaningful info
      return value.map(item => {
        if (item.code) return item.code; // CPT code object
        if (item.text) return `"${item.text.slice(0, 50)}${item.text.length > 50 ? '...' : ''}"`; // Evidence span
        if (item.name) return item.name;
        // Fallback: show first few properties
        const keys = Object.keys(item).slice(0, 2);
        return keys.map(k => `${k}: ${item[k]}`).join(", ");
      }).join("; ");
    }
    return value.join(", ");
  }

  if (typeof value === "object") {
    // For single objects, extract meaningful info
    if (value.code) return value.code;
    if (value.text) return `"${value.text.slice(0, 50)}${value.text.length > 50 ? '...' : ''}"`;
    // Fallback: JSON but truncated
    const json = JSON.stringify(value);
    return json.length > 100 ? json.slice(0, 97) + "..." : json;
  }

  return String(value);
}

/**
 * Recursively render all non-null registry fields as a form.
 * Flattens nested objects with arrow notation paths.
 */
function renderRegistryForm(registry) {
  const container = document.getElementById("registryForm");
  const rows = [];

  // Keys to skip (complex nested structures shown separately or not useful)
  const skipKeys = new Set(["evidence", "billing", "ner_spans"]);

  // Recursively extract non-null fields
  function extractFields(obj, prefix = "") {
    if (obj === null || obj === undefined) return;

    for (const [key, value] of Object.entries(obj)) {
      const path = prefix ? `${prefix}.${key}` : key;
      const lowKey = key.toLowerCase();

      if (value === null || value === undefined) continue;
      if (value === false) continue; // Skip false booleans (procedures not performed)
      if (Array.isArray(value) && value.length === 0) continue; // Skip empty arrays

      // Skip complex evidence/billing structures at top level
      if (!prefix && skipKeys.has(lowKey)) continue;

      if (typeof value === "object" && !Array.isArray(value)) {
        // Recurse into nested objects
        extractFields(value, path);
      } else {
        // Format the value for display
        const displayValue = formatValueForDisplay(value);
        if (displayValue === "—") continue; // Skip empty values

        // Format the key for display (snake_case → Title Case with arrow separators)
        const displayKey = path
          .split(".")
          .map((part) => part.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()))
          .join(" > ");

        rows.push({ path, label: displayKey, value: displayValue, rawValue: value });
      }
    }
  }

  extractFields(registry);

  // Build form HTML
  let html = "";
  if (rows.length === 0) {
    html =
      '<div class="subtle" style="text-align: center; padding: 20px;">No registry data extracted</div>';
  } else {
    // Group by top-level category
    const groups = {};
    rows.forEach((row) => {
      const category = row.path
        .split(".")[0]
        .replace(/_/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());
      if (!groups[category]) groups[category] = [];
      groups[category].push(row);
    });

    for (const [category, items] of Object.entries(groups)) {
      html += `<div class="collapsible-section open">`;
      html += `<button type="button" class="collapsible-header" onclick="this.parentElement.classList.toggle('open')">`;
      html += `<span>${category}</span>`;
      html += `<span class="collapsible-icon">▼</span>`;
      html += `</button>`;
      html += `<div class="collapsible-content">`;

      items.forEach(({ path, label, value }) => {
        // Escape HTML in values to prevent XSS
        const safeValue = String(value).replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const shortLabel = label.includes(" > ") ? label.split(" > ").slice(1).join(" > ") : label;

        html += `<div class="form-group" data-path="${path}">`;
        html += `<label class="form-label">${shortLabel}</label>`;
        html += `<input type="text" class="form-control" value="${safeValue}" readonly>`;
        html += `</div>`;
      });

      html += `</div></div>`;
    }
  }

  container.innerHTML = html;
}

async function main() {
  if (!window.__monacoReady) {
    setStatus("Monaco loader missing");
    return;
  }
  await window.__monacoReady;

  if (!globalThis.crossOriginIsolated) {
    setStatus(
      "Cross-origin isolation is OFF (SharedArrayBuffer unavailable). Open /ui/ and verify COOP/COEP headers."
    );
    runBtn.disabled = true;
    cancelBtn.disabled = true;
    applyBtn.disabled = true;
    revertBtn.disabled = true;
    submitBtn.disabled = true;
  }

  const editor = monaco.editor.create(document.getElementById("editor"), {
    value: "",
    language: "plaintext",
    theme: "vs-dark",
    minimap: { enabled: false },
    wordWrap: "on",
    fontSize: 13,
    automaticLayout: true,
  });

  const model = editor.getModel();
  let originalText = model.getValue();
  let hasRunDetection = false;
  let scrubbedConfirmed = false;
  let suppressDirtyFlag = false;

  let detections = [];
  let detectionsById = new Map();
  let excluded = new Set();
  let decorations = [];

  let running = false;
  let currentSelection = null;

  // Track selection changes for manual redaction
  editor.onDidChangeCursorSelection((e) => {
    const selection = e.selection;
    const hasSelection = !selection.isEmpty();

    currentSelection = hasSelection ? selection : null;

    // Only enable Add button if we have a selection and aren't running detection
    if (addRedactionBtn) {
      addRedactionBtn.disabled = !hasSelection || running;
    }
  });

  function setScrubbedConfirmed(value) {
    scrubbedConfirmed = value;
    submitBtn.disabled = !scrubbedConfirmed || running;
    // Update button title for better UX
    if (submitBtn.disabled) {
      if (running) {
        submitBtn.title = "Wait for detection to complete";
      } else if (!scrubbedConfirmed) {
        submitBtn.title = "Click 'Apply redactions' first";
      }
    } else {
      submitBtn.title = "Submit the scrubbed note to the server";
    }
  }

  function clearDetections() {
    detections = [];
    detectionsById = new Map();
    excluded = new Set();
    decorations = editor.deltaDecorations(decorations, []);
    detectionsListEl.innerHTML = "";
    detectionsCountEl.textContent = "0";
    applyBtn.disabled = true;
    revertBtn.disabled = true;
    lastServerResponse = null;
    if (exportBtn) exportBtn.disabled = true;
  }

  function updateDecorations() {
    const text = model.getValue();
    const lineStarts = buildLineStartOffsets(text);
    const textLength = text.length;

    const included = detections.filter((d) => !excluded.has(d.id));
    const newDecorations = included
      .filter((d) => Number.isFinite(d.start) && Number.isFinite(d.end) && d.end > d.start)
      .map((d) => {
        const startPos = offsetToPosition(d.start, lineStarts, textLength);
        const endPos = offsetToPosition(d.end, lineStarts, textLength);

        // Determine class and hover based on source (manual vs auto)
        const className = d.source === "manual"
          ? "phi-detection-manual"
          : "phi-detection";

        const hoverMessage = d.source === "manual"
          ? `**${d.label}** (Manual)`
          : `**${d.label}** (${d.source}, score ${formatScore(d.score)})`;

        return {
          range: new monaco.Range(
            startPos.lineNumber,
            startPos.column,
            endPos.lineNumber,
            endPos.column
          ),
          options: {
            inlineClassName: className,
            hoverMessage: { value: hoverMessage },
          },
        };
      });

    decorations = editor.deltaDecorations(decorations, newDecorations);
  }

  function renderDetections() {
    const text = model.getValue();
    detectionsCountEl.textContent = String(detections.length);
    detectionsListEl.innerHTML = "";

    const sorted = [...detections].sort((a, b) => {
      if (a.start !== b.start) return a.start - b.start;
      return (b.score ?? 0) - (a.score ?? 0);
    });

    for (const d of sorted) {
      const checked = !excluded.has(d.id);
      const checkbox = el("input", {
        type: "checkbox",
        checked: checked ? "checked" : null,
        onChange: (ev) => {
          const on = ev.target.checked;
          if (!on) excluded.add(d.id);
          else excluded.delete(d.id);
          updateDecorations();
        },
      });
      checkbox.checked = checked;

      // Add conditional classes for manual detections
      const sourceClass = d.source === "manual" ? "pill source source-manual" : "pill source";
      const scoreText = d.source === "manual" ? "Manual" : `score ${formatScore(d.score)}`;

      const meta = el("div", { className: "detMeta" }, [
        el("span", { className: "pill label", text: d.label }),
        el("span", { className: sourceClass, text: d.source }),
        el("span", { className: "pill score", text: scoreText }),
        el("span", { className: "pill", text: `${d.start}–${d.end}` }),
      ]);

      const snippet = el("div", {
        className: "snippet",
        text: safeSnippet(text, d.start, d.end),
      });

      detectionsListEl.appendChild(
        el("div", { className: "detRow" }, [
          checkbox,
          el("div", {}, [meta, snippet]),
        ])
      );
    }

    if (detections.length === 0 && hasRunDetection && !running) {
      detectionsListEl.innerHTML = '<div class="subtle" style="padding: 1rem; text-align: center;">No PHI detected. Click "Apply redactions" to enable submit.</div>';
    }

    updateDecorations();
    // Enable apply button if detection has completed (even with 0 detections)
    applyBtn.disabled = running || !hasRunDetection;
    if (applyBtn.disabled) {
      if (running) {
        applyBtn.title = "Wait for detection to complete";
      } else if (!hasRunDetection) {
        applyBtn.title = "Click 'Run detection' first";
      }
    } else {
      applyBtn.title = "Apply redactions to enable submit button";
    }
    revertBtn.disabled = running || originalText === model.getValue();
  }

  model.onDidChangeContent(() => {
    if (suppressDirtyFlag) return;
    setScrubbedConfirmed(false);
    revertBtn.disabled = running || originalText === model.getValue();
  });

  const worker = new Worker(`/ui/redactor.worker.js?v=${Date.now()}`, {
    type: "module",
  });
  let workerReady = false;
  let lastWorkerMessageAt = Date.now();
  let aiModelReady = false;
  let aiModelFailed = false;
  let aiModelError = null;

  worker.addEventListener("error", (ev) => {
    setStatus(`Worker error: ${ev.message || "failed to load"}`);
    setProgress("");
    running = false;
    cancelBtn.disabled = true;
    runBtn.disabled = true;
    applyBtn.disabled = true;
  });

  worker.addEventListener("messageerror", () => {
    setStatus("Worker message error (serialization failed)");
    setProgress("");
    running = false;
    cancelBtn.disabled = true;
    runBtn.disabled = true;
    applyBtn.disabled = true;
  });

  worker.postMessage({ type: "init", debug: WORKER_CONFIG.debug, config: WORKER_CONFIG });

  worker.onmessage = (e) => {
    const msg = e.data;
    if (!msg || typeof msg.type !== "string") return;
    lastWorkerMessageAt = Date.now();

    if (msg.type === "ready") {
      workerReady = true;
      setStatus("Ready (local model loaded)");
      setProgress("");
      runBtn.disabled = !globalThis.crossOriginIsolated;
      return;
    }

    if (msg.type === "progress") {
      const stage = msg.stage ? String(msg.stage) : null;
      if (stage) {
        if (stage.startsWith("AI model ready")) {
          aiModelReady = true;
          aiModelFailed = false;
          aiModelError = null;
          if (!running) setStatus("Ready (AI model loaded)");
        } else if (stage.startsWith("AI model failed")) {
          aiModelReady = false;
          aiModelFailed = true;
          aiModelError = stage.includes(":") ? stage.split(":").slice(1).join(":").trim() : null;
          const shortErr =
            aiModelError && aiModelError.length > 120
              ? `${aiModelError.slice(0, 117)}…`
              : aiModelError;
          if (!running) {
            setStatus(
              shortErr
                ? `Ready (regex-only; AI failed: ${shortErr})`
                : "Ready (regex-only; AI model failed)"
            );
          }
        }
        if (msg.windowCount && msg.windowIndex) {
          setProgress(`${stage} (${msg.windowIndex}/${msg.windowCount})`);
        } else {
          setProgress(stage);
        }
      } else {
        const percent = msg.windowCount
          ? Math.round((msg.windowIndex / msg.windowCount) * 100)
          : 0;
        setProgress(`Processing window ${msg.windowIndex}/${msg.windowCount} (${percent}%)`);
      }
      return;
    }

    if (msg.type === "detections_delta") {
      for (const det of msg.detections || []) detectionsById.set(det.id, det);
      detections = Array.from(detectionsById.values());
      renderDetections();
      return;
    }

    if (msg.type === "done") {
      running = false;
      cancelBtn.disabled = true;
      runBtn.disabled = !workerReady || !globalThis.crossOriginIsolated;
      applyBtn.disabled = false; // Enable even with 0 detections
      revertBtn.disabled = originalText === model.getValue();

      detections = Array.isArray(msg.detections) ? msg.detections : [];
      detectionsById = new Map(detections.map((d) => [d.id, d]));

      const detectionCount = detections.length;
      if (detectionCount === 0) {
        const modeNote = aiModelReady
          ? "AI+regex"
          : aiModelFailed
          ? "regex-only (AI failed)"
          : "regex-only (AI loading)";
        setStatus(`Done (0 detections) — ${modeNote}`);
      } else {
        const modeNote = aiModelReady
          ? "AI+regex"
          : aiModelFailed
          ? "regex-only (AI failed)"
          : "regex-only (AI loading)";
        setStatus(
          `Done (${detectionCount} detection${detectionCount === 1 ? "" : "s"}) — ${modeNote}`
        );
      }
      setProgress("");
      renderDetections();
      return;
    }

    if (msg.type === "error") {
      running = false;
      cancelBtn.disabled = true;
      runBtn.disabled = !workerReady || !globalThis.crossOriginIsolated;
      applyBtn.disabled = !hasRunDetection;
      setStatus(`Error: ${msg.message || "unknown"}`);
      setProgress("");
      return;
    }
  };

  cancelBtn.addEventListener("click", () => {
    if (!running) return;
    worker.postMessage({ type: "cancel" });
    setStatus("Cancelling…");
  });

  runBtn.addEventListener("click", () => {
    if (running) return;
    if (!workerReady) {
      setStatus("Worker still loading… (first run may take minutes)");
      return;
    }
    hasRunDetection = true;
    setScrubbedConfirmed(false);

    originalText = model.getValue();
    clearDetections();

    running = true;
    runBtn.disabled = true;
    cancelBtn.disabled = false;
    applyBtn.disabled = true;
    revertBtn.disabled = false;
    submitBtn.disabled = true;

    setStatus("Detecting… (client-side)");
    setProgress("");

    worker.postMessage({
      type: "start",
      text: originalText,
      config: WORKER_CONFIG,
    });
  });

  applyBtn.addEventListener("click", () => {
    if (!hasRunDetection) return;

    const included = detections.filter((d) => !excluded.has(d.id));
    const spans = included
      .filter((d) => Number.isFinite(d.start) && Number.isFinite(d.end) && d.end > d.start)
      .sort((a, b) => b.start - a.start);

    const text = model.getValue();
    const lineStarts = buildLineStartOffsets(text);
    const textLength = text.length;

    const edits = spans.map((d) => {
      const startPos = offsetToPosition(d.start, lineStarts, textLength);
      const endPos = offsetToPosition(d.end, lineStarts, textLength);
      return {
        range: new monaco.Range(
          startPos.lineNumber,
          startPos.column,
          endPos.lineNumber,
          endPos.column
        ),
        text: "[REDACTED]",
      };
    });

    suppressDirtyFlag = true;
    try {
      editor.executeEdits("phi-redactor", edits);
    } finally {
      suppressDirtyFlag = false;
    }

    setScrubbedConfirmed(true);
    setStatus("Redactions applied (scrubbed text ready to submit)");
    revertBtn.disabled = false;
  });

  revertBtn.addEventListener("click", () => {
    suppressDirtyFlag = true;
    try {
      editor.setValue(originalText);
    } finally {
      suppressDirtyFlag = false;
    }
    clearDetections();
    hasRunDetection = false;
    setScrubbedConfirmed(false);
    setStatus("Reverted to baseline");
    setProgress("");
  });

  // Manual redaction: Add button click handler
  if (addRedactionBtn) {
    addRedactionBtn.addEventListener("click", () => {
      if (!currentSelection || currentSelection.isEmpty()) return;

      const startOffset = model.getOffsetAt(currentSelection.getStartPosition());
      const endOffset = model.getOffsetAt(currentSelection.getEndPosition());
      const selectedText = model.getValue().slice(startOffset, endOffset);
      const entityType = entityTypeSelect ? entityTypeSelect.value : "OTHER";

      // Create new detection object
      const newDetection = {
        id: `manual_${Date.now()}_${Math.random().toString(36).slice(2)}`,
        label: entityType,
        text: selectedText,
        start: startOffset,
        end: endOffset,
        score: 1.0,
        source: "manual"  // Critical for styling distinction
      };

      // Add to global state (manual additions "win" by being at end)
      detections.push(newDetection);
      detectionsById.set(newDetection.id, newDetection);

      // Re-render sidebar and editor highlights
      renderDetections();

      // Reset UI: Clear selection and disable button
      editor.setSelection(new monaco.Selection(0, 0, 0, 0));
      currentSelection = null;
      addRedactionBtn.disabled = true;

      setStatus(`Added manual redaction: ${entityType}`);
    });
  }

  submitBtn.addEventListener("click", async () => {
    if (!scrubbedConfirmed) {
      console.warn("Submit blocked: redactions not confirmed. Click 'Apply redactions' first.");
      setStatus("Error: Apply redactions before submitting");
      return;
    }
    submitBtn.disabled = true;
    setStatus("Submitting scrubbed note…");
    serverResponseEl.textContent = "(submitting...)";

    try {
      const requestBody = {
        note: model.getValue(),
        already_scrubbed: true,
      };
      console.log("Submitting to /api/v1/process", { noteLength: requestBody.note.length });
      
      const res = await fetch("/api/v1/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      
      console.log("Response status:", res.status, res.statusText);

      const bodyText = await res.text();
      let data;
      try {
        data = bodyText ? JSON.parse(bodyText) : null;
      } catch (parseErr) {
        console.error("Failed to parse JSON response:", parseErr);
        data = { error: "Invalid JSON response", raw: bodyText };
      }
      
      if (!res.ok) {
        console.error("Request failed:", res.status, data);
        serverResponseEl.textContent = JSON.stringify(
          { error: data, status: res.status, statusText: res.statusText },
          null,
          2
        );
        setStatus(`Submit failed (${res.status})`);
        return;
      }
      
      console.log("Success:", data);
      renderResults(data);
      setStatus("Submitted (scrubbed text only)");
    } catch (err) {
      console.error("Submit error:", err);
      serverResponseEl.textContent = JSON.stringify(
        { error: String(err?.message || err), type: err?.name || "UnknownError" },
        null,
        2
      );
      setStatus("Submit error - check console for details");
    } finally {
      submitBtn.disabled = false;
    }
  });

  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      if (!lastServerResponse) {
        setStatus("No results to export yet");
        return;
      }

      const payload = JSON.stringify(lastServerResponse, null, 2);
      const blob = new Blob([payload], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `procedure_suite_response_${Date.now()}.json`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      setStatus("Exported results");
    });
  }

  // Optional: service worker (local assets only)
  if ("serviceWorker" in navigator && new URL(location.href).searchParams.get("sw") === "1") {
    try {
      await navigator.serviceWorker.register("./sw.js");
    } catch {
      // ignore
    }
  }

  setStatus("Initializing local PHI model (first load downloads ONNX)…");

  setInterval(() => {
    if (!running) return;
    const quietMs = Date.now() - lastWorkerMessageAt;
    if (quietMs > 15_000) {
      setProgress("Still working… (model download/inference can take a while)");
    }
  }, 2_000);
}

main().catch((e) => {
  console.error(e);
  statusTextEl.textContent = `Init failed: ${e?.message || e}`;
});
