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

// State management for diff tracking
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
 * Shows status banner, CPT codes table, and registry summary.
 */
function renderResults(data) {
  const statusBanner = document.getElementById("statusBanner");
  const cptSection = document.getElementById("cptSection");
  const registrySection = document.getElementById("registrySection");
  const serverResponse = document.getElementById("serverResponse");

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

  let html = `
    <thead>
      <tr>
        <th>Code</th>
        <th>Description</th>
        <th>Confidence</th>
        <th>RVU</th>
        <th>Payment</th>
      </tr>
    </thead>
    <tbody>
  `;

  // If we have suggestions, use those (more detailed)
  if (suggestions.length > 0) {
    suggestions.forEach(s => {
      const b = billingMap[s.code] || {};
      const confidence = s.confidence ? `${(s.confidence * 100).toFixed(0)}%` : "—";
      const rvu = b.work_rvu?.toFixed(2) || "—";
      const payment = b.facility_payment ? `$${b.facility_payment.toFixed(2)}` : "—";

      html += `
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
    data.cpt_codes.forEach(code => {
      const b = billingMap[code] || {};
      const rvu = b.work_rvu?.toFixed(2) || "—";
      const payment = b.facility_payment ? `$${b.facility_payment.toFixed(2)}` : "—";

      html += `
        <tr>
          <td><code>${code}</code></td>
          <td>${b.description || "—"}</td>
          <td>—</td>
          <td>${rvu}</td>
          <td>${payment}</td>
        </tr>
      `;
    });
  }

  // Totals row
  if (data.total_work_rvu || data.estimated_payment) {
    const totalRvu = data.total_work_rvu?.toFixed(2) || "—";
    const totalPayment = data.estimated_payment ? `$${data.estimated_payment.toFixed(2)}` : "—";
    html += `
      <tr class="totals-row">
        <td colspan="3"><strong>TOTALS</strong></td>
        <td><strong>${totalRvu}</strong></td>
        <td><strong>${totalPayment}</strong></td>
      </tr>
    `;
  }

  html += "</tbody>";
  tbody.innerHTML = html;
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
          .map(part => part.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()))
          .join(" > ");

        rows.push({ path, label: displayKey, value: displayValue, rawValue: value });
      }
    }
  }

  extractFields(registry);

  // Build form HTML
  let html = "";
  if (rows.length === 0) {
    html = '<div class="subtle" style="text-align: center; padding: 20px;">No registry data extracted</div>';
  } else {
    // Group by top-level category
    const groups = {};
    rows.forEach(row => {
      const category = row.path.split(".")[0].replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
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
      "Cross-origin isolation is OFF (SharedArrayBuffer unavailable). Open /ui/phi_redactor/ and verify COOP/COEP headers."
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
    theme: "vs",
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
          : `**${d.label}** (${