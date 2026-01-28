/* global monaco */

const statusTextEl = document.getElementById("statusText");
const progressTextEl = document.getElementById("progressText");
const detectionsListEl = document.getElementById("detectionsList");
const detectionsCountEl = document.getElementById("detectionsCount");
let serverResponseEl = document.getElementById("serverResponse");

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
if (statusTextEl) statusTextEl.textContent = "Booting UI…";

function setStatus(text) {
  if (!statusTextEl) return;
  statusTextEl.textContent = text;
}

function setProgress(text) {
  if (!progressTextEl) return;
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

function safeHtml(str) {
  return String(str || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function highlightSpanInEditor(start, end) {
  try {
    // Fallback: if Monaco is still loading/unavailable, highlight in the basic textarea.
    if (!window.editor) {
      const ta = document.getElementById("fallbackTextarea");
      if (!ta) return;
      const textLength = ta.value.length;
      const s = clamp(Number(start) || 0, 0, textLength);
      const e = clamp(Number(end) || 0, 0, textLength);
      ta.focus();
      ta.setSelectionRange(s, e);
      return;
    }

    const model = window.editor.getModel();
    if (!model) return;

    const s = model.getPositionAt(Math.max(0, start));
    const e = model.getPositionAt(Math.max(0, end));
    const range = new monaco.Range(s.lineNumber, s.column, e.lineNumber, e.column);

    window.editor.setSelection(range);
    window.editor.revealRangeInCenter(range);
    window.editor.focus();
  } catch (err) {
    console.warn("Failed to highlight evidence span", err);
  }
}

window.__highlightEvidence = (start, end) => highlightSpanInEditor(start, end);

function normalizeSpans(spans) {
  // Accept shapes:
  // {start,end,text} or {span:[start,end],text} or {start,end,snippet}
  if (!Array.isArray(spans)) return [];
  return spans
    .map((sp) => ({
      text: sp.text ?? sp.snippet ?? "",
      start: sp.start ?? sp.span?.[0] ?? sp.span?.start ?? 0,
      end: sp.end ?? sp.span?.[1] ?? sp.span?.end ?? 0,
    }))
    .filter(
      (sp) =>
        Number.isFinite(sp.start) && Number.isFinite(sp.end) && sp.end > sp.start
    );
}

function renderEvidenceChips(spans) {
  const normalized = normalizeSpans(spans);
  if (normalized.length === 0) return "—";

  return normalized
    .map(
      (sp) => `
    <button class="ev-chip" title="Click to highlight ${sp.start}-${sp.end}"
      onclick="window.__highlightEvidence(${sp.start}, ${sp.end})">
      ${safeHtml(sp.text || "(evidence)")}
      <span class="ev-range">(${sp.start}-${sp.end})</span>
    </button>
  `
    )
    .join(" ");
}

function getEvidenceMap(data) {
  // Prefer registry.evidence; fall back to top-level evidence
  return data?.registry?.evidence || data?.evidence || {};
}

function formatNumber(value, digits = 2) {
  if (!Number.isFinite(value)) return "—";
  return value.toFixed(digits);
}

function formatCurrency(value) {
  if (!Number.isFinite(value)) return "—";
  return `$${value.toFixed(2)}`;
}

function titleCaseKey(key) {
  const raw = String(key || "");
  if (!raw) return "—";

  const special = {
    bal: "BAL",
    linear_ebus: "Linear EBUS",
    radial_ebus: "Radial EBUS",
    navigational_bronchoscopy: "Navigational Bronchoscopy",
    diagnostic_bronchoscopy: "Diagnostic Bronchoscopy",
    therapeutic_aspiration: "Therapeutic Aspiration",
    tbna_conventional: "Conventional TBNA",
    peripheral_tbna: "Peripheral TBNA",
  };
  if (special[raw]) return special[raw];

  return raw
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function normalizeCptCode(code) {
  return String(code || "").trim().replace(/^\+/, "");
}

function clearEl(node) {
  if (!node) return;
  while (node.firstChild) node.removeChild(node.firstChild);
}

function fmtBool(val) {
  if (val === null || val === undefined) return "—";
  return val ? "Yes" : "No";
}

function fmtMaybe(val) {
  if (val === null || val === undefined) return "—";
  const s = String(val).trim();
  return s ? s : "—";
}

function fmtSpan(span) {
  const start = span?.[0];
  const end = span?.[1];
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return "—";
  return `${start}–${end}`;
}

function splitWarning(w) {
  const text = String(w || "").trim();
  if (!text) return null;
  const idx = text.indexOf(":");
  if (idx > 0 && idx < 48) {
    return { category: text.slice(0, idx).trim() || "Other", message: text.slice(idx + 1).trim() || "—" };
  }
  return { category: "Other", message: text };
}

function groupWarnings(warnings) {
  const grouped = new Map();
  (Array.isArray(warnings) ? warnings : []).forEach((w) => {
    const parsed = splitWarning(w);
    if (!parsed) return;
    if (!grouped.has(parsed.category)) grouped.set(parsed.category, []);
    grouped.get(parsed.category).push(parsed.message);
  });
  return grouped;
}

function getRegistry(data) {
  return data?.registry || {};
}

function getCodingSupport(data) {
  const cs = getRegistry(data)?.coding_support;
  return cs && typeof cs === "object" ? cs : null;
}

function getCodingLines(data) {
  const cs = getCodingSupport(data);
  const lines = cs?.coding_summary?.lines;
  if (Array.isArray(lines) && lines.length > 0) return lines;

  // Fallback: synthesize from suggestions/cpt_codes (selected-only)
  const suggestions = Array.isArray(data?.suggestions) ? data.suggestions : [];
  if (suggestions.length > 0) {
    return suggestions.map((s, idx) => ({
      sequence: idx + 1,
      code: normalizeCptCode(s.code),
      description: s.description || null,
      units: 1,
      role: "primary",
      selection_status: "selected",
      selection_reason: s.rationale || null,
      note_spans: null,
    }));
  }

  const codes = Array.isArray(data?.cpt_codes) ? data.cpt_codes : [];
  if (codes.length > 0) {
    return codes.map((c, idx) => ({
      sequence: idx + 1,
      code: normalizeCptCode(c),
      description: null,
      units: 1,
      role: "primary",
      selection_status: "selected",
      selection_reason: null,
      note_spans: null,
    }));
  }

  return [];
}

function getCodingRationale(data) {
  const cs = getCodingSupport(data);
  const cr = cs?.coding_rationale;
  return cr && typeof cr === "object" ? cr : {};
}

function getEvidence(data) {
  return data?.evidence || getRegistry(data)?.evidence || {};
}

function getPerCodeBilling(data) {
  const lines = Array.isArray(data?.per_code_billing) ? data.per_code_billing : [];
  return lines;
}

function getBillingByCode(data) {
  const map = new Map();
  getPerCodeBilling(data).forEach((b) => {
    const code = normalizeCptCode(b?.cpt_code);
    if (code) map.set(code, b);
  });
  return map;
}

function collectRegistryCodeEvidence(data, code) {
  const registry = getRegistry(data);
  const items = registry?.billing?.cpt_codes;
  if (!Array.isArray(items)) return [];
  const match = items.find((c) => normalizeCptCode(c?.code) === code);
  const ev = match?.evidence;
  return Array.isArray(ev) ? ev : [];
}

function makeEvidenceChip(span) {
  const start = span?.start ?? span?.span?.[0];
  const end = span?.end ?? span?.span?.[1];
  const text = span?.text ?? span?.snippet ?? span?.quote ?? "";
  const btn = document.createElement("button");
  btn.className = "ev-chip";
  btn.type = "button";
  btn.title = Number.isFinite(start) && Number.isFinite(end) ? `Click to highlight ${start}-${end}` : "Evidence";
  btn.appendChild(document.createTextNode(String(text || "(evidence)")));
  if (Number.isFinite(start) && Number.isFinite(end) && end > start) {
    const range = document.createElement("span");
    range.className = "ev-range";
    range.textContent = `(${start}-${end})`;
    btn.appendChild(range);
    btn.addEventListener("click", () => highlightSpanInEditor(start, end));
  } else {
    btn.disabled = true;
  }
  return btn;
}

function makeEvidenceDetails(spans, summaryText = "Evidence") {
  const normalized = normalizeSpans(spans);
  if (normalized.length === 0) return null;

  const details = document.createElement("details");
  details.className = "inline-details";
  const summary = document.createElement("summary");
  summary.textContent = summaryText;
  details.appendChild(summary);

  const wrap = document.createElement("div");
  wrap.style.marginTop = "8px";
  normalized.slice(0, 6).forEach((sp) => wrap.appendChild(makeEvidenceChip(sp)));
  details.appendChild(wrap);
  return details;
}

/**
 * Main Orchestrator: Renders the clean clinical dashboard
 */
function renderDashboard(data) {
  renderStatusBannerHost(data);
  renderStatCards(data);

  renderBillingSelected(data);
  renderBillingSuppressed(data);
  renderCodingRationaleTable(data);
  renderRulesAppliedTable(data);
  renderFinancialSummary(data);
  renderAuditFlags(data);
  renderPipelineMetadata(data);

  renderClinicalContextTable(data);
  renderProceduresSummaryTable(data);
  renderDiagnosticFindings(data);
  renderBalDetails(data);
  renderLinearEbusSummary(data);
  renderEbusNodeEvents(data);
  renderEvidenceTraceability(data);

  renderDebugLogs(data);
}

/**
 * 1. Renders the Executive Summary (Stat Cards)
 */
function renderStatCards(data) {
  const container = document.getElementById("statCards");
  if (!container) return;

  // Determine review status
  let statusText = "Ready";
  let statusClass = "";
  if (data.needs_manual_review || (data.audit_warnings && data.audit_warnings.length > 0)) {
    statusText = "⚠️ Review Required";
    statusClass = "warning";
  }

  // Format currency and RVU
  const payment = data.estimated_payment
    ? new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(data.estimated_payment)
    : "$0.00";
  const rvu = data.total_work_rvu ? data.total_work_rvu.toFixed(2) : "0.00";

  container.innerHTML = `
    <div class="stat-card">
      <span class="stat-label">Review Status</span>
      <div class="stat-value ${statusClass}">${statusText}</div>
    </div>
    <div class="stat-card">
      <span class="stat-label">Total wRVU</span>
      <div class="stat-value">${rvu}</div>
    </div>
    <div class="stat-card">
      <span class="stat-label">Est. Payment</span>
      <div class="stat-value currency">${payment}</div>
    </div>
    <div class="stat-card">
      <span class="stat-label">CPT Count</span>
      <div class="stat-value">${(data.per_code_billing || []).length}</div>
    </div>
  `;
}

function renderStatusBannerHost(data) {
  const host = document.getElementById("statusBannerHost");
  if (!host) return;

  clearEl(host);

  const banner = document.createElement("div");

  const warnings = Array.isArray(data?.audit_warnings) ? data.audit_warnings : [];
  const hasError = Boolean(data?.error);
  const needsReview = data?.review_status === "pending_phi_review" || data?.needs_manual_review;

  if (hasError) {
    banner.className = "status-banner error";
    banner.textContent = `Error: ${String(data.error)}`;
  } else if (needsReview) {
    banner.className = "status-banner error";
    banner.textContent = "⚠️ Manual review required";
  } else if (warnings.length > 0) {
    banner.className = "status-banner warning";
    banner.textContent = `⚠️ ${warnings.length} warning(s) – review recommended`;
  } else {
    banner.className = "status-banner success";
    banner.textContent = "✓ Extraction complete";
  }

  host.appendChild(banner);
}

function renderBillingSelected(data) {
  const tbody = document.getElementById("billingSelectedBody");
  if (!tbody) return;
  clearEl(tbody);

  const billingByCode = getBillingByCode(data);
  const codingLines = getCodingLines(data);
  const selected = codingLines.filter(
    (ln) => String(ln?.selection_status || "selected").toLowerCase() === "selected"
  );

  if (selected.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 4;
    td.className = "dash-empty";
    td.textContent = "No selected codes.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  selected.forEach((ln) => {
    const code = normalizeCptCode(ln?.code);
    const billing = billingByCode.get(code);
    const desc = ln?.description || billing?.description || "—";
    const units = Number.isFinite(ln?.units) ? ln.units : Number.isFinite(billing?.units) ? billing.units : 1;
    const roleRaw = String(ln?.role || (ln?.is_add_on ? "add_on" : "primary") || "primary");
    const role = roleRaw.toLowerCase() === "add_on" ? "add_on" : "primary";
    const reason = ln?.selection_reason || ln?.rationale || "";

    const tr = document.createElement("tr");

    const tdCode = document.createElement("td");
    const codeSpan = document.createElement("span");
    codeSpan.className = "code-cell";
    codeSpan.textContent = code || "—";
    tdCode.appendChild(codeSpan);

    const tdDesc = document.createElement("td");
    const descDiv = document.createElement("div");
    descDiv.style.fontWeight = "600";
    descDiv.textContent = String(desc || "—");
    tdDesc.appendChild(descDiv);

    if (reason) {
      const reasonDiv = document.createElement("div");
      reasonDiv.className = "qa-line";
      reasonDiv.textContent = `Rationale: ${String(reason)}`;
      tdDesc.appendChild(reasonDiv);
    }

    const combinedEvidence = [];
    if (Array.isArray(ln?.note_spans)) combinedEvidence.push(...ln.note_spans);
    combinedEvidence.push(...collectRegistryCodeEvidence(data, code));
    const evDetails = makeEvidenceDetails(combinedEvidence, "Evidence");
    if (evDetails) tdDesc.appendChild(evDetails);

    const tdUnits = document.createElement("td");
    tdUnits.textContent = String(units ?? "—");

    const tdRole = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = `status-badge ${role === "add_on" ? "role-addon" : "role-primary"}`;
    badge.textContent = role === "add_on" ? "Add On" : "Primary";
    tdRole.appendChild(badge);

    tr.appendChild(tdCode);
    tr.appendChild(tdDesc);
    tr.appendChild(tdUnits);
    tr.appendChild(tdRole);
    tbody.appendChild(tr);
  });
}

function renderBillingSuppressed(data) {
  const tbody = document.getElementById("billingSuppressedBody");
  if (!tbody) return;
  clearEl(tbody);

  const codingLines = getCodingLines(data);
  const rules = Array.isArray(getCodingRationale(data)?.rules_applied)
    ? getCodingRationale(data).rules_applied
    : [];
  const warnings = Array.isArray(data?.audit_warnings) ? data.audit_warnings : [];

  const entries = new Map(); // code -> {status, reason}

  // 1) Prefer explicit coding_support dropped lines (stable order)
  codingLines.forEach((ln) => {
    const status = String(ln?.selection_status || "").toLowerCase();
    if (status === "selected") return;
    const code = normalizeCptCode(ln?.code);
    if (!code) return;
    const reason = String(ln?.selection_reason || "").trim() || "Dropped by rule";
    const inferred = /^suppressed\b/i.test(reason) ? "Suppressed" : "Dropped";
    entries.set(code, { status: inferred, reason });
  });

  // 2) Add any rule-driven dropped codes not already present
  rules.forEach((r) => {
    const affected = Array.isArray(r?.codes_affected) ? r.codes_affected : [];
    const outcome = String(r?.outcome || "").toLowerCase();
    if (outcome !== "dropped" && outcome !== "suppressed") return;
    affected.forEach((c) => {
      const code = normalizeCptCode(c);
      if (!code || entries.has(code)) return;
      entries.set(code, { status: "Dropped", reason: String(r?.details || "Dropped by rule") });
    });
  });

  // 3) Add suppressed codes hinted by warnings (e.g., "Suppressed 31645: ...")
  warnings.forEach((w) => {
    const text = String(w || "");
    const match = text.match(/\bSuppressed\s+(\d{5})\b/i);
    if (!match) return;
    const code = match[1];
    if (entries.has(code)) return;
    entries.set(code, { status: "Suppressed", reason: text.replace(/\s+/g, " ").trim() });
  });

  if (entries.size === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 3;
    td.className = "dash-empty";
    td.textContent = "No codes dropped/suppressed.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  for (const [code, info] of entries.entries()) {
    const tr = document.createElement("tr");
    const tdCode = document.createElement("td");
    const codeSpan = document.createElement("span");
    codeSpan.className = "code-cell";
    codeSpan.textContent = code;
    tdCode.appendChild(codeSpan);

    const tdStatus = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = `status-badge ${info.status === "Suppressed" ? "status-suppressed" : "status-dropped"}`;
    badge.textContent = info.status;
    tdStatus.appendChild(badge);

    const tdReason = document.createElement("td");
    tdReason.textContent = String(info.reason || "—");

    tr.appendChild(tdCode);
    tr.appendChild(tdStatus);
    tr.appendChild(tdReason);
    tbody.appendChild(tr);
  }
}

function renderCodingRationaleTable(data) {
  const tbody = document.getElementById("codingRationaleBody");
  if (!tbody) return;
  clearEl(tbody);

  const codingLines = getCodingLines(data);
  const perCode = Array.isArray(getCodingRationale(data)?.per_code) ? getCodingRationale(data).per_code : [];
  const perCodeByCode = new Map();
  perCode.forEach((pc) => {
    const code = normalizeCptCode(pc?.code);
    if (code) perCodeByCode.set(code, pc);
  });

  const codesInOrder = [];
  codingLines.forEach((ln) => {
    const code = normalizeCptCode(ln?.code);
    if (code && !codesInOrder.includes(code)) codesInOrder.push(code);
  });
  // Include any per_code entries not present in coding_lines
  Array.from(perCodeByCode.keys())
    .sort((a, b) => a.localeCompare(b))
    .forEach((code) => {
      if (!codesInOrder.includes(code)) codesInOrder.push(code);
    });

  if (codesInOrder.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 3;
    td.className = "dash-empty";
    td.textContent = "No coding rationale returned.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  codesInOrder.forEach((code) => {
    const pc = perCodeByCode.get(code);
    const summary = pc?.summary || codingLines.find((ln) => normalizeCptCode(ln?.code) === code)?.selection_reason || "—";

    const tr = document.createElement("tr");

    const tdCode = document.createElement("td");
    const codeSpan = document.createElement("span");
    codeSpan.className = "code-cell";
    codeSpan.textContent = code;
    tdCode.appendChild(codeSpan);

    const tdLogic = document.createElement("td");
    tdLogic.textContent = String(summary || "—");

    const tdEvidence = document.createElement("td");

    const docEv = Array.isArray(pc?.documentation_evidence) ? pc.documentation_evidence : [];
    const spans = docEv
      .map((e) => ({
        text: e?.snippet || e?.text || "",
        start: e?.span?.start,
        end: e?.span?.end,
      }))
      .filter((e) => Number.isFinite(e.start) && Number.isFinite(e.end) && e.end > e.start);

    const evDetails = makeEvidenceDetails(spans, "Evidence");
    if (evDetails) tdEvidence.appendChild(evDetails);
    else tdEvidence.appendChild(document.createTextNode("—"));

    const qaFlags = Array.isArray(pc?.qa_flags) ? pc.qa_flags : [];
    if (qaFlags.length > 0) {
      const qaWrap = document.createElement("div");
      qaWrap.style.marginTop = "8px";
      qaFlags.forEach((q) => {
        const line = document.createElement("div");
        line.className = "qa-line";
        const sev = String(q?.severity || "info").toUpperCase();
        const msg = String(q?.message || "");
        line.textContent = `${sev}: ${msg}`;
        qaWrap.appendChild(line);
      });
      tdEvidence.appendChild(qaWrap);
    }

    tr.appendChild(tdCode);
    tr.appendChild(tdLogic);
    tr.appendChild(tdEvidence);
    tbody.appendChild(tr);
  });
}

function renderRulesAppliedTable(data) {
  const tbody = document.getElementById("rulesAppliedBody");
  if (!tbody) return;
  clearEl(tbody);

  const rules = Array.isArray(getCodingRationale(data)?.rules_applied)
    ? getCodingRationale(data).rules_applied
    : [];

  if (rules.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 4;
    td.className = "dash-empty";
    td.textContent = "No rules applied returned.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  rules.forEach((r) => {
    const tr = document.createElement("tr");
    const tdType = document.createElement("td");
    const type = String(r?.rule_type || "—");
    const id = r?.rule_id ? String(r.rule_id) : "";
    tdType.textContent = id ? `${type} (${id})` : type;

    const tdCodes = document.createElement("td");
    const codes = Array.isArray(r?.codes_affected) ? r.codes_affected.map(normalizeCptCode).filter(Boolean) : [];
    tdCodes.textContent = codes.length ? codes.join(", ") : "—";

    const tdOutcome = document.createElement("td");
    tdOutcome.textContent = fmtMaybe(r?.outcome);

    const tdDetails = document.createElement("td");
    tdDetails.textContent = fmtMaybe(r?.details);

    tr.appendChild(tdType);
    tr.appendChild(tdCodes);
    tr.appendChild(tdOutcome);
    tr.appendChild(tdDetails);
    tbody.appendChild(tr);
  });
}

function renderFinancialSummary(data) {
  const totalRvuEl = document.getElementById("financialTotalRVU");
  const totalPayEl = document.getElementById("financialTotalPayment");
  const tbody = document.getElementById("financialSummaryBody");
  if (!tbody) return;

  if (totalRvuEl) totalRvuEl.textContent = Number.isFinite(data?.total_work_rvu) ? data.total_work_rvu.toFixed(2) : "—";
  if (totalPayEl) totalPayEl.textContent = Number.isFinite(data?.estimated_payment) ? formatCurrency(data.estimated_payment) : "—";

  clearEl(tbody);

  const billing = getPerCodeBilling(data);
  const selectedUnits = new Map();
  getCodingLines(data)
    .filter((ln) => String(ln?.selection_status || "selected").toLowerCase() === "selected")
    .forEach((ln) => {
      const code = normalizeCptCode(ln?.code);
      if (!code) return;
      const units = Number.isFinite(ln?.units) ? ln.units : 1;
      selectedUnits.set(code, units);
    });

  if (!Array.isArray(billing) || billing.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 6;
    td.className = "dash-empty";
    td.textContent = "No financial breakdown available.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  billing.forEach((b) => {
    const code = normalizeCptCode(b?.cpt_code);
    const units = Number.isFinite(b?.units) ? b.units : 1;
    const selUnits = selectedUnits.get(code);
    const mismatch =
      Number.isFinite(selUnits) && Number.isFinite(units) && selUnits !== units;

    const tr = document.createElement("tr");

    const tdCode = document.createElement("td");
    const codeSpan = document.createElement("span");
    codeSpan.className = "code-cell";
    codeSpan.textContent = code || "—";
    tdCode.appendChild(codeSpan);

    const tdUnits = document.createElement("td");
    tdUnits.textContent = String(units);

    const tdWork = document.createElement("td");
    tdWork.textContent = formatNumber(b?.work_rvu);

    const tdFac = document.createElement("td");
    tdFac.textContent = formatNumber(b?.total_facility_rvu);

    const tdPay = document.createElement("td");
    tdPay.textContent = formatCurrency(b?.facility_payment);

    const tdNotes = document.createElement("td");
    if (mismatch) {
      tdNotes.textContent = `⚠ Units mismatch (selected ${selUnits}, billed ${units})`;
    } else {
      tdNotes.textContent = "—";
    }

    tr.appendChild(tdCode);
    tr.appendChild(tdUnits);
    tr.appendChild(tdWork);
    tr.appendChild(tdFac);
    tr.appendChild(tdPay);
    tr.appendChild(tdNotes);
    tbody.appendChild(tr);
  });
}

function renderAuditFlags(data) {
  const tbody = document.getElementById("auditFlagsBody");
  if (!tbody) return;
  clearEl(tbody);

  const grouped = groupWarnings(data?.audit_warnings || []);
  const validationErrors = Array.isArray(data?.validation_errors) ? data.validation_errors : [];
  if (validationErrors.length > 0) grouped.set("Validation errors", validationErrors.map((e) => String(e || "—")));

  if (grouped.size === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 2;
    td.className = "dash-empty";
    td.textContent = "No audit or validation flags.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  for (const [category, messages] of grouped.entries()) {
    const tr = document.createElement("tr");
    const tdCat = document.createElement("td");
    tdCat.textContent = category;

    const tdMsg = document.createElement("td");
    const list = document.createElement("div");
    (Array.isArray(messages) ? messages : []).forEach((m) => {
      const line = document.createElement("div");
      line.className = "qa-line";
      line.textContent = `• ${String(m || "—")}`;
      list.appendChild(line);
    });
    tdMsg.appendChild(list);

    tr.appendChild(tdCat);
    tr.appendChild(tdMsg);
    tbody.appendChild(tr);
  }
}

function renderPipelineMetadata(data) {
  const tbody = document.getElementById("pipelineMetadataBody");
  if (!tbody) return;
  clearEl(tbody);

  const rows = [
    ["Needs manual review", data?.needs_manual_review ? "Yes" : "No"],
    ["Review status", fmtMaybe(data?.review_status)],
    ["Coder difficulty", fmtMaybe(data?.coder_difficulty)],
    ["Pipeline mode", fmtMaybe(data?.pipeline_mode)],
    ["KB version", fmtMaybe(data?.kb_version)],
    ["Policy version", fmtMaybe(data?.policy_version)],
    [
      "Processing time",
      Number.isFinite(data?.processing_time_ms)
        ? `${Math.round(data.processing_time_ms).toLocaleString()} ms`
        : "—",
    ],
  ];

  rows.forEach(([k, v]) => {
    const tr = document.createElement("tr");
    const tdK = document.createElement("td");
    tdK.textContent = k;
    const tdV = document.createElement("td");
    tdV.textContent = fmtMaybe(v);
    tr.appendChild(tdK);
    tr.appendChild(tdV);
    tbody.appendChild(tr);
  });
}

function renderClinicalContextTable(data) {
  const tbody = document.getElementById("clinicalContextBody");
  if (!tbody) return;
  clearEl(tbody);

  const registry = getRegistry(data);
  const ctx = registry?.clinical_context || {};
  const sed = registry?.sedation || {};
  const setting = registry?.procedure_setting || {};

  const rows = [
    ["Primary indication", ctx?.primary_indication],
    ["Indication category", ctx?.indication_category],
    ["Bronchus sign", ctx?.bronchus_sign === null || ctx?.bronchus_sign === undefined ? null : (ctx?.bronchus_sign ? "Yes" : "No")],
    ["Sedation type", sed?.type],
    ["Anesthesia provider", sed?.anesthesia_provider],
    ["Airway type", setting?.airway_type],
    ["Procedure location", setting?.location],
    ["Patient position", setting?.patient_position],
  ].filter(([, v]) => v !== null && v !== undefined && String(v).trim() !== "");

  if (rows.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 2;
    td.className = "dash-empty";
    td.textContent = "No clinical context available.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  rows.forEach(([k, v]) => {
    const tr = document.createElement("tr");
    const tdK = document.createElement("td");
    tdK.textContent = k;
    const tdV = document.createElement("td");
    tdV.textContent = fmtMaybe(v);
    tr.appendChild(tdK);
    tr.appendChild(tdV);
    tbody.appendChild(tr);
  });
}

function isPerformedProcedure(procObj) {
  if (procObj === true) return true;
  if (procObj === false || procObj === null || procObj === undefined) return false;
  if (typeof procObj === "object" && typeof procObj.performed === "boolean") return procObj.performed;
  return false;
}

function summarizeProcedure(procKey, procObj) {
  if (!isPerformedProcedure(procObj)) return "—";
  const p = procObj && typeof procObj === "object" ? procObj : {};

  if (procKey === "diagnostic_bronchoscopy") {
    const abn = Array.isArray(p.airway_abnormalities) ? p.airway_abnormalities.filter(Boolean) : [];
    const findings = String(p.inspection_findings || "").trim();
    const parts = [];
    if (abn.length > 0) parts.push(`Abnormalities: ${abn.join(", ")}`);
    if (findings) parts.push(`Findings: ${findings}`);
    return parts.join(" · ") || "—";
  }

  if (procKey === "bal") {
    const parts = [];
    if (p.location) parts.push(`Location: ${p.location}`);
    if (Number.isFinite(p.volume_instilled_ml)) parts.push(`Instilled: ${p.volume_instilled_ml} mL`);
    if (Number.isFinite(p.volume_recovered_ml)) parts.push(`Recovered: ${p.volume_recovered_ml} mL`);
    return parts.join(" · ") || "—";
  }

  if (procKey === "linear_ebus") {
    const stations = Array.isArray(p.stations_sampled) ? p.stations_sampled.filter(Boolean) : [];
    const parts = [];
    if (stations.length > 0) parts.push(`Stations: ${stations.join(", ")}`);
    if (p.needle_gauge) parts.push(`Needle: ${p.needle_gauge}`);
    if (p.elastography_used !== null && p.elastography_used !== undefined) parts.push(`Elastography: ${p.elastography_used ? "Yes" : "No"}`);
    return parts.join(" · ") || "—";
  }

  if (procKey === "therapeutic_aspiration") {
    const parts = [];
    if (p.material) parts.push(`Material: ${p.material}`);
    if (p.location) parts.push(`Location: ${p.location}`);
    return parts.join(" · ") || "—";
  }

  if (procKey === "radial_ebus") {
    const parts = [];
    if (p.probe_position) parts.push(`Probe: ${p.probe_position}`);
    if (p.guide_sheath_used !== null && p.guide_sheath_used !== undefined) parts.push(`Guide sheath: ${p.guide_sheath_used ? "Yes" : "No"}`);
    return parts.join(" · ") || "—";
  }

  if (procKey === "navigational_bronchoscopy") {
    const parts = [];
    if (p.target_reached !== null && p.target_reached !== undefined) parts.push(`Target reached: ${p.target_reached ? "Yes" : "No"}`);
    if (Number.isFinite(p.divergence_mm)) parts.push(`Divergence: ${p.divergence_mm} mm`);
    if (p.confirmation_method) parts.push(`Confirmed by: ${p.confirmation_method}`);
    return parts.join(" · ") || "—";
  }

  // Fallback: surface a few common fields without being noisy
  const parts = [];
  if (p.location) parts.push(`Location: ${p.location}`);
  if (Array.isArray(p.locations) && p.locations.length > 0) parts.push(`Locations: ${p.locations.join(", ")}`);
  if (Number.isFinite(p.number_of_samples)) parts.push(`${p.number_of_samples} samples`);
  return parts.join(" · ") || "—";
}

function renderProceduresSummaryTable(data) {
  const tbody = document.getElementById("proceduresSummaryBody");
  if (!tbody) return;
  clearEl(tbody);

  const registry = getRegistry(data);
  const procs = registry?.procedures_performed;
  if (!procs || typeof procs !== "object") {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 3;
    td.className = "dash-empty";
    td.textContent = "No procedures_performed available.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  const keys = Object.keys(procs);
  keys.sort((a, b) => titleCaseKey(a).localeCompare(titleCaseKey(b)));

  const items = keys.map((k) => ({ key: k, obj: procs[k], performed: isPerformedProcedure(procs[k]) }));
  items.sort((a, b) => {
    if (a.performed !== b.performed) return a.performed ? -1 : 1;
    return titleCaseKey(a.key).localeCompare(titleCaseKey(b.key));
  });

  if (items.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 3;
    td.className = "dash-empty";
    td.textContent = "No procedures found.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  items.forEach(({ key, obj, performed }) => {
    const tr = document.createElement("tr");
    if (!performed) tr.classList.add("opacity-50");

    const tdName = document.createElement("td");
    tdName.style.fontWeight = "600";
    tdName.textContent = titleCaseKey(key);

    const tdPerf = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = `status-badge ${performed ? "status-selected" : "status-suppressed"}`;
    badge.textContent = performed ? "Yes" : "No";
    tdPerf.appendChild(badge);

    const tdDetails = document.createElement("td");
    tdDetails.textContent = summarizeProcedure(key, obj);

    tr.appendChild(tdName);
    tr.appendChild(tdPerf);
    tr.appendChild(tdDetails);
    tbody.appendChild(tr);
  });
}

function toggleCard(cardId, visible) {
  const card = document.getElementById(cardId);
  if (!card) return;
  card.classList.toggle("hidden", !visible);
}

function renderDiagnosticFindings(data) {
  const tbody = document.getElementById("diagnosticFindingsBody");
  if (!tbody) return;
  clearEl(tbody);

  const proc = getRegistry(data)?.procedures_performed?.diagnostic_bronchoscopy;
  const performed = isPerformedProcedure(proc);
  toggleCard("diagnosticFindingsCard", performed);
  if (!performed) return;

  const abn = Array.isArray(proc?.airway_abnormalities) ? proc.airway_abnormalities.filter(Boolean) : [];
  const rows = [
    ["Airway abnormalities", abn.length ? abn.join(", ") : "—"],
    ["Findings (free text)", proc?.inspection_findings || "—"],
  ];
  rows.forEach(([k, v]) => {
    const tr = document.createElement("tr");
    const tdK = document.createElement("td");
    tdK.textContent = k;
    const tdV = document.createElement("td");
    tdV.textContent = fmtMaybe(v);
    tr.appendChild(tdK);
    tr.appendChild(tdV);
    tbody.appendChild(tr);
  });
}

function renderBalDetails(data) {
  const tbody = document.getElementById("balDetailsBody");
  if (!tbody) return;
  clearEl(tbody);

  const proc = getRegistry(data)?.procedures_performed?.bal;
  const performed = isPerformedProcedure(proc);
  toggleCard("balDetailsCard", performed);
  if (!performed) return;

  const rows = [
    ["Location", proc?.location || "—"],
    ["Instilled (mL)", Number.isFinite(proc?.volume_instilled_ml) ? String(proc.volume_instilled_ml) : "—"],
    ["Recovered (mL)", Number.isFinite(proc?.volume_recovered_ml) ? String(proc.volume_recovered_ml) : "—"],
    ["Appearance", proc?.appearance || "—"],
  ];
  rows.forEach(([k, v]) => {
    const tr = document.createElement("tr");
    const tdK = document.createElement("td");
    tdK.textContent = k;
    const tdV = document.createElement("td");
    tdV.textContent = fmtMaybe(v);
    tr.appendChild(tdK);
    tr.appendChild(tdV);
    tbody.appendChild(tr);
  });
}

function renderLinearEbusSummary(data) {
  const tbody = document.getElementById("linearEbusSummaryBody");
  if (!tbody) return;
  clearEl(tbody);

  const proc = getRegistry(data)?.procedures_performed?.linear_ebus;
  const performed = isPerformedProcedure(proc);
  toggleCard("linearEbusSummaryCard", performed);
  if (!performed) return;

  const stations =
    Array.isArray(proc?.stations_sampled) && proc.stations_sampled.length > 0
      ? proc.stations_sampled.filter(Boolean)
      : Array.isArray(proc?.node_events)
        ? proc.node_events
            .filter((e) => e?.action && e.action !== "inspected_only" && e.station)
            .map((e) => e.station)
        : [];
  const uniqueStations = Array.from(new Set(stations));

  const rows = [
    ["Stations sampled", uniqueStations.length ? uniqueStations.join(", ") : "—"],
    ["Needle gauge", proc?.needle_gauge || "—"],
    ["Elastography used", proc?.elastography_used === null || proc?.elastography_used === undefined ? "—" : (proc.elastography_used ? "Yes" : "No")],
    ["Elastography pattern", proc?.elastography_pattern || "—"],
  ];

  rows.forEach(([k, v]) => {
    const tr = document.createElement("tr");
    const tdK = document.createElement("td");
    tdK.textContent = k;
    const tdV = document.createElement("td");
    tdV.textContent = fmtMaybe(v);
    tr.appendChild(tdK);
    tr.appendChild(tdV);
    tbody.appendChild(tr);
  });
}

function renderEbusNodeEvents(data) {
  const tbody = document.getElementById("ebusNodeEventsBody");
  if (!tbody) return;
  clearEl(tbody);

  const proc = getRegistry(data)?.procedures_performed?.linear_ebus;
  const performed = isPerformedProcedure(proc);
  const events = Array.isArray(proc?.node_events) ? proc.node_events : [];
  const show = performed && events.length > 0;
  toggleCard("ebusNodeEventsCard", show);
  if (!show) return;

  const actionLabel = (action) => {
    const a = String(action || "");
    if (a === "inspected_only") return "Inspected only";
    if (a === "needle_aspiration") return "Needle aspiration";
    if (a === "core_biopsy") return "Core biopsy";
    if (a === "forceps_biopsy") return "Forceps biopsy";
    return a || "—";
  };

  events.forEach((ev) => {
    const tr = document.createElement("tr");

    const tdStation = document.createElement("td");
    tdStation.textContent = fmtMaybe(ev?.station);

    const tdAction = document.createElement("td");
    tdAction.textContent = actionLabel(ev?.action);

    const tdPasses = document.createElement("td");
    tdPasses.textContent = Number.isFinite(ev?.passes) ? String(ev.passes) : "—";

    const tdElast = document.createElement("td");
    tdElast.textContent = fmtMaybe(ev?.elastography_pattern);

    const tdEvidence = document.createElement("td");
    const quote = String(ev?.evidence_quote || "").trim();
    if (!quote) {
      tdEvidence.textContent = "—";
    } else {
      const details = document.createElement("details");
      details.className = "inline-details";
      const summary = document.createElement("summary");
      summary.textContent = safeSnippet(quote, 0, quote.length);
      details.appendChild(summary);
      const body = document.createElement("div");
      body.style.marginTop = "8px";
      const pre = document.createElement("pre");
      pre.style.whiteSpace = "pre-wrap";
      pre.style.margin = "0";
      pre.textContent = quote;
      body.appendChild(pre);
      details.appendChild(body);
      tdEvidence.appendChild(details);
    }

    tr.appendChild(tdStation);
    tr.appendChild(tdAction);
    tr.appendChild(tdPasses);
    tr.appendChild(tdElast);
    tr.appendChild(tdEvidence);
    tbody.appendChild(tr);
  });
}

function renderEvidenceTraceability(data) {
  const host = document.getElementById("evidenceTraceabilityHost");
  if (!host) return;
  clearEl(host);

  const evidence = getEvidence(data);
  if (!evidence || typeof evidence !== "object") {
    const empty = document.createElement("div");
    empty.className = "dash-empty";
    empty.textContent = "No evidence available.";
    host.appendChild(empty);
    return;
  }

  const fields = Object.keys(evidence).sort((a, b) => a.localeCompare(b));
  const rows = [];
  fields.forEach((field) => {
    const items = evidence[field];
    if (!Array.isArray(items)) return;
    items.forEach((item) => rows.push({ field, item }));
  });

  if (rows.length === 0) {
    const empty = document.createElement("div");
    empty.className = "dash-empty";
    empty.textContent = "No evidence spans.";
    host.appendChild(empty);
    return;
  }

  const wrap = document.createElement("div");
  wrap.className = "dash-table-wrap";

  const table = document.createElement("table");
  table.className = "dash-table";

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  ["Field", "Evidence", "Span", "Confidence", "Source"].forEach((h) => {
    const th = document.createElement("th");
    th.textContent = h;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");

  rows.slice(0, 250).forEach(({ field, item }) => {
    const tr = document.createElement("tr");

    const tdField = document.createElement("td");
    tdField.textContent = field;

    const tdEv = document.createElement("td");
    const text = String(item?.text || item?.quote || "").trim();
    const span = Array.isArray(item?.span) ? item.span : null;
    const chip = makeEvidenceChip({ text: safeSnippet(text || "(evidence)", 0, Math.min(text.length || 0, 240)), span });
    tdEv.appendChild(chip);

    const tdSpan = document.createElement("td");
    tdSpan.textContent = fmtSpan(span);

    const tdConf = document.createElement("td");
    tdConf.textContent = typeof item?.confidence === "number" ? item.confidence.toFixed(2) : "—";

    const tdSource = document.createElement("td");
    tdSource.textContent = fmtMaybe(item?.source);

    tr.appendChild(tdField);
    tr.appendChild(tdEv);
    tr.appendChild(tdSpan);
    tr.appendChild(tdConf);
    tr.appendChild(tdSource);
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  wrap.appendChild(table);
  host.appendChild(wrap);

  if (rows.length > 250) {
    const note = document.createElement("div");
    note.className = "qa-line";
    note.style.marginTop = "8px";
    note.textContent = `Showing first 250 evidence items (${rows.length} total).`;
    host.appendChild(note);
  }
}

/**
 * Transforms API data into a unified "Golden Record"
 * FIX: Now prioritizes backend rationale over generic placeholders
 */
function transformToUnifiedTable(rawData) {
  const unifiedMap = new Map();

  // Helper: Get explanation from specific coding_support backend map
  const getBackendRationale = (code) => {
    if (rawData.registry?.coding_support?.code_rationales?.[code]) {
      return rawData.registry.coding_support.code_rationales[code];
    }
    // Fallback to "evidence" array if available
    const billingEntry = rawData.registry?.billing?.cpt_codes?.find((c) => c.code === code);
    if (billingEntry?.evidence?.length > 0) {
      return billingEntry.evidence.map((e) => e.text).join("; ");
    }
    return null;
  };

  // 1. Process Header Codes (Raw)
  (rawData.header_codes || []).forEach((item) => {
    unifiedMap.set(item.code, {
      code: item.code,
      desc: item.description || "Unknown Procedure",
      inHeader: true,
      inBody: false,
      status: "pending",
      rationale: "Found in header scan",
      rvu: 0.0,
      payment: 0.0,
    });
  });

  // 2. Process Derived Codes (Body)
  (rawData.derived_codes || []).forEach((item) => {
    const existing = unifiedMap.get(item.code) || {
      code: item.code,
      inHeader: false,
      rvu: 0.0,
      payment: 0.0,
    };

    existing.desc = item.description || existing.desc;
    existing.inBody = true;

    // FIX: Grab specific backend rationale if available
    const backendReason = getBackendRationale(item.code);
    if (backendReason) {
      existing.rationale = backendReason;
    } else {
      existing.rationale = "Derived from procedure actions";
    }

    unifiedMap.set(item.code, existing);
  });

  // 3. Process Final Selection (The "Truth")
  (rawData.per_code_billing || []).forEach((item) => {
    const existing = unifiedMap.get(item.cpt_code) || {
      code: item.cpt_code,
      inHeader: false,
      inBody: true,
      rationale: "Selected",
    };

    existing.code = item.cpt_code; // Ensure code is set
    existing.desc = item.description || existing.desc;
    existing.status = item.status || "selected";
    existing.rvu = item.work_rvu;
    existing.payment = item.facility_payment;

    // FIX: Ensure suppression/bundling logic is visible
    if (item.work_rvu === 0) {
      existing.status = "Bundled/Suppressed";
      // If we have a specific bundling warning, append it
      const warning = (rawData.audit_warnings || []).find((w) => w.includes(item.cpt_code));
      if (warning) existing.rationale = warning;
    } else {
      // Refresh rationale from backend to ensure it's not "Derived..."
      const backendReason = getBackendRationale(item.cpt_code);
      if (backendReason) existing.rationale = backendReason;
    }

    unifiedMap.set(item.cpt_code, existing);
  });

  // Sort: High Value -> Suppressed -> Header Only
  return Array.from(unifiedMap.values()).sort((a, b) => {
    if (a.rvu > 0 && b.rvu === 0) return -1;
    if (b.rvu > 0 && a.rvu === 0) return 1;
    return a.code.localeCompare(b.code);
  });
}

/**
 * 2. Renders the Unified Billing Reconciliation Table
 * Merges Header, Derived, and Final codes into one view.
 */
function renderUnifiedTable(data) {
  const tbody = document.getElementById("unifiedTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const sortedRows = transformToUnifiedTable(data);

  // Render Rows
  sortedRows.forEach((row) => {
    const tr = document.createElement("tr");

    // Logic Badges
    let sourceBadge = "";
    if (row.inHeader && row.inBody) sourceBadge = `<span class="badge badge-both">Match</span>`;
    else if (row.inHeader) sourceBadge = `<span class="badge badge-header">Header Only</span>`;
    else sourceBadge = `<span class="badge badge-body">Derived</span>`;

    // Status Badge
    let statusBadge = `<span class="badge badge-primary">Primary</span>`;
    if (row.rvu === 0 || row.status === "Bundled/Suppressed") {
      statusBadge = `<span class="badge badge-bundled">Bundled</span>`;
      tr.classList.add("row-suppressed");
    }

    // Rationale cleaning
    const rationale = row.rationale || (row.inBody ? "Derived from procedure actions" : "Found in header scan");
    const rvuDisplay = Number.isFinite(row.rvu) ? row.rvu.toFixed(2) : "0.00";
    const paymentDisplay = Number.isFinite(row.payment) ? row.payment.toFixed(2) : "0.00";

    tr.innerHTML = `
      <td><span class="code-cell">${row.code}</span></td>
      <td>
        <span class="desc-text">${row.desc || "Unknown Procedure"}</span>
        ${sourceBadge}
      </td>
      <td>${statusBadge}</td>
      <td><span class="rationale-text">${rationale}</span></td>
      <td><strong>${rvuDisplay}</strong></td>
      <td>$${paymentDisplay}</td>
    `;
    tbody.appendChild(tr);
  });
}

/**
 * Renders the Clinical/Registry Data Table (Restored)
 * Flattens nested registry objects into a clean key-value view.
 */
function renderRegistrySummary(data) {
  const tbody = document.getElementById("registryTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const registry = data.registry || {};

  // 1. Clinical Context (Top Priority)
  if (registry.clinical_context) {
    addRegistryRow(tbody, "Indication", registry.clinical_context.primary_indication);
    if (registry.clinical_context.indication_category) {
      addRegistryRow(tbody, "Category", registry.clinical_context.indication_category);
    }
  }

  // 2. Anesthesia/Sedation
  if (registry.sedation) {
    const sedationStr = `${registry.sedation.type || "Not specified"} (${registry.sedation.anesthesia_provider || "Provider unknown"})`;
    addRegistryRow(tbody, "Sedation", sedationStr);
  }

  // 3. EBUS Details (Granular)
  if (registry.procedures_performed?.linear_ebus?.performed) {
    const ebus = registry.procedures_performed.linear_ebus;
    const stations = Array.isArray(ebus.stations_sampled) ? ebus.stations_sampled.join(", ") : "None";
    const needle = ebus.needle_gauge || "Not specified";
    addRegistryRow(
      tbody,
      "Linear EBUS",
      `<strong>Stations:</strong> ${stations} <br> <span style="font-size:11px; color:#64748b;">Gauge: ${needle} | Elastography: ${ebus.elastography_used ? "Yes" : "No"}</span>`
    );
  }

  // 4. Other Procedures (Iterate generic performed flags)
  const procs = registry.procedures_performed || {};
  Object.keys(procs).forEach((key) => {
    if (key === "linear_ebus") return; // Handled above
    const p = procs[key];
    if (p === true || (p && p.performed)) {
      // Convert snake_case to Title Case (e.g., radial_ebus -> Radial Ebus)
      const label = key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());

      // Extract useful details if they exist (e.g., "lobes", "sites")
      let details = "Performed";
      if (p?.sites) details = `Sites: ${Array.isArray(p.sites) ? p.sites.join(", ") : p.sites}`;
      else if (p?.target_lobes) details = `Lobes: ${p.target_lobes.join(", ")}`;
      else if (p?.action) details = p.action;

      addRegistryRow(tbody, label, details);
    }
  });
}

// Helper to append rows
function addRegistryRow(tbody, label, content) {
  if (!content) return;
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td style="font-weight:600; color:#475569;">${label}</td>
    <td>${content}</td>
  `;
  tbody.appendChild(tr);
}

/**
 * 3. Renders Technical Logs (Collapsed by default)
 */
function renderDebugLogs(data) {
  const logBox = document.getElementById("systemLogs");
  if (!logBox) return;

  let logs = [];

  // Collect all warnings and logs
  if (data.audit_warnings) logs.push(...data.audit_warnings.map((w) => `[AUDIT] ${w}`));
  if (data.warnings) logs.push(...data.warnings.map((w) => `[WARN] ${w}`));
  if (data.self_correction) {
    data.self_correction.forEach((sc) => {
      logs.push(`[SELF-CORRECT] Applied patch for ${sc.trigger.target_cpt}: ${sc.trigger.reason}`);
    });
  }

  if (logs.length === 0) {
    logBox.textContent = "No system warnings or overrides.";
  } else {
    logBox.textContent = logs.join("\n");
  }
}

/**
 * Render the formatted results from the server response.
 * Shows status banner, CPT codes table, and registry form.
 */
function renderResults(data) {
  const container = document.getElementById("resultsContainer");
  if (!container) return;

  lastServerResponse = data;
  if (exportBtn) exportBtn.disabled = !data;

  container.classList.remove("hidden");
  renderDashboard(data);

  if (serverResponseEl) {
    serverResponseEl.textContent = JSON.stringify(data, null, 2);
  }
}

function renderStatusBanner(data, container) {
  const statusBanner = document.createElement("div");

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

  container.appendChild(statusBanner);
}

// --- Helper: Create Section Wrapper ---
function createSection(title, icon) {
  const div = document.createElement('div');
  div.className = 'report-section';
  div.innerHTML = `<div class="report-header">${icon} ${title}</div><div class="report-body"></div>`;
  return div;
}

function buildQaByCode(codingSupport) {
  const qaByCode = {};
  const perCode = codingSupport?.coding_rationale?.per_code || [];
  perCode.forEach((pc) => {
    if (!pc?.code) return;
    qaByCode[pc.code] = pc.qa_flags || [];
  });
  return qaByCode;
}

function renderCPTRawHeader(registry, codingSupport, data) {
  const section = createSection("CPT Codes – Raw (Header)", "🧾");

  const ev = getEvidenceMap(data);
  const header = ev.code_evidence || []; // [{text,start,end}] in schema
  if (!Array.isArray(header) || header.length === 0) {
    section.querySelector(
      ".report-body"
    ).innerHTML = `<div class="subtle" style="text-align:center;">No header CPT codes found</div>`;
    return section;
  }

  const derivedSet = new Set((registry?.billing?.cpt_codes || []).map((c) => c.code));
  const decisionByCode = new Map(
    (codingSupport?.coding_summary?.lines || []).map((ln) => [
      ln.code,
      (ln.selection_status || "selected").toLowerCase(),
    ])
  );

  const rows = header
    .map((ce) => {
      const code = typeof ce === "string" ? ce : ce?.text;
      if (!code) return "";

      const status = (
        decisionByCode.get(code) || (derivedSet.has(code) ? "derived_only" : "header_only")
      ).toLowerCase();
      const bodyEv = derivedSet.has(code) ? "Yes" : "No";
      const evidenceHtml = typeof ce === "string" ? "—" : renderEvidenceChips([ce]);

      return `
      <tr>
        <td><strong>${safeHtml(code)}</strong></td>
        <td><span class="status-badge status-${safeHtml(status)}">${safeHtml(status)}</span></td>
        <td>${bodyEv}</td>
        <td>${evidenceHtml}</td>
      </tr>
    `;
    })
    .filter(Boolean)
    .join("");

  section.querySelector(".report-body").innerHTML = `
    <table class="data-table">
      <thead><tr><th>Code</th><th>Status</th><th>Body evidence?</th><th>Evidence</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
  return section;
}

function renderCPTDerivedEvidence(registry, data) {
  const section = createSection("CPT Codes – Derived (Body Evidence)", "🔎");
  const derived = registry?.billing?.cpt_codes || [];

  if (!Array.isArray(derived) || derived.length === 0) {
    section.querySelector(
      ".report-body"
    ).innerHTML = `<div class="subtle" style="text-align:center;">No derived CPT codes</div>`;
    return section;
  }

  const rows = derived
    .map((c) => {
      const derivedFrom = Array.isArray(c.derived_from) ? c.derived_from.join(", ") : "";
      return `
    <tr>
      <td><strong>${safeHtml(c.code)}</strong></td>
      <td>${safeHtml(c.description || "-")}</td>
      <td>${safeHtml(derivedFrom || "-")}</td>
      <td>${renderEvidenceChips(c.evidence || [])}</td>
    </tr>
  `;
    })
    .join("");

  section.querySelector(".report-body").innerHTML = `
    <table class="data-table">
      <thead><tr><th>Code</th><th>Description</th><th>Derived From</th><th>Evidence</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
  return section;
}

// --- 2. CPT Coding Summary ---
function renderCPTSummary(lines, qaByCode = {}) {
  const section = createSection('CPT Coding Summary (Final Selection)', '💳');
  if (!Array.isArray(lines) || lines.length === 0) {
    section.querySelector('.report-body').innerHTML = `
      <div class="subtle" style="text-align:center;">No CPT summary lines returned</div>
    `;
    return section;
  }
  const tbody = lines
    .map((line) => {
      const code = line.code || "-";
      const qa =
        (qaByCode[code] || [])
          .map(
            (q) =>
              `<div class="qa-line">${safeHtml(
                (q.severity || "info").toUpperCase()
              )}: ${safeHtml(q.message || "")}</div>`
          )
          .join("") || "—";

      const evidence = renderEvidenceChips(line.note_spans || []);

      return `
        <tr class="${line.selection_status === 'dropped' ? 'opacity-50' : ''}">
            <td>${safeHtml(line.sequence ?? '-')}</td>
            <td><strong>${safeHtml(code)}</strong></td>
            <td>${safeHtml(line.description || '-')}</td>
            <td>${safeHtml(line.units ?? '-')}</td>
            <td><span class="status-badge ${
              line.role === "primary" ? "role-primary" : "role-addon"
            }">${safeHtml(line.role || "-")}</span></td>
            <td><span class="status-badge status-${safeHtml(
              (line.selection_status || "selected").toLowerCase()
            )}">${safeHtml(line.selection_status || "selected")}</span></td>
            <td>${safeHtml(line.selection_reason || '-')}</td>
            <td>${evidence}</td>
            <td>${qa}</td>
        </tr>
    `;
    })
    .join('');

  section.querySelector('.report-body').innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Seq</th><th>CPT Code</th><th>Description</th><th>Units</th><th>Role</th><th>Status</th><th>Selection Rationale</th><th>Evidence</th><th>QA</th>
                </tr>
            </thead>
            <tbody>${tbody}</tbody>
        </table>
    `;
  return section;
}

// --- 3. Bundling & Suppression Decisions ---
function renderBundlingDecisions(rules) {
  const section = createSection('Bundling & Suppression Decisions', '🧾');

  // Filter for rules that actually affected codes (dropped/informational)
  const validRules = rules.filter(r => Array.isArray(r.codes_affected) && r.codes_affected.length > 0);

  if (validRules.length === 0) return document.createDocumentFragment();

  const tbody = validRules.map(rule => `
        <tr>
            <td>${rule.codes_affected.join(', ')}</td>
            <td><span class="status-badge status-${rule.outcome === 'dropped' ? 'dropped' : 'suppressed'}">${rule.outcome === 'dropped' ? 'Dropped' : 'Suppressed'}</span></td>
            <td>${rule.details || '-'}</td>
        </tr>
    `).join('');

  section.querySelector('.report-body').innerHTML = `
        <table class="data-table">
            <thead><tr><th>CPT Code</th><th>Action</th><th>Reason</th></tr></thead>
            <tbody>${tbody}</tbody>
        </table>
    `;
  return section;
}

// --- 4. RVU & Payment Summary ---
function renderRVUSummary(billingLines, totalRVU, totalPay) {
  const section = createSection('RVU & Payment Summary', '💰');

  const rows = (Array.isArray(billingLines) ? billingLines : []).map(line => `
        <tr>
            <td><strong>${line.cpt_code || '-'}</strong></td>
            <td>${line.units ?? '-'}</td>
            <td>${formatNumber(line.work_rvu)}</td>
            <td>${formatNumber(line.total_facility_rvu)}</td>
            <td>${formatCurrency(line.facility_payment)}</td>
        </tr>
    `).join('');

  const totals = `
        <tr class="totals-row">
            <td colspan="2" style="text-align:right">Totals:</td>
            <td>${formatNumber(totalRVU)}</td>
            <td>-</td>
            <td>${formatCurrency(totalPay)}</td>
        </tr>
    `;

  section.querySelector('.report-body').innerHTML = `
        <table class="data-table">
            <thead>
                <tr><th>CPT Code</th><th>Units</th><th>Work RVU</th><th>Facility RVU</th><th>Est. Payment ($)</th></tr>
            </thead>
            <tbody>${rows}${totals}</tbody>
        </table>
    `;
  return section;
}

// --- 5. Clinical Context ---
function renderClinicalContext(registry, data) {
  const section = createSection('Clinical Context', '🩺');
  const ev = getEvidenceMap(data);

  const rows = [];

  if (registry.clinical_context?.primary_indication) {
    rows.push([
      "Primary Indication",
      registry.clinical_context.primary_indication,
      renderEvidenceChips(ev["clinical_context.primary_indication"] || []),
    ]);
  }
  if (registry.clinical_context?.bronchus_sign) {
    rows.push(["Bronchus Sign", registry.clinical_context.bronchus_sign, "—"]);
  }
  if (registry.sedation?.type) {
    rows.push([
      "Sedation Type",
      registry.sedation.type,
      renderEvidenceChips(ev["sedation.type"] || []),
    ]);
  }
  if (registry.procedure_setting?.airway_type) {
    rows.push([
      "Airway Type",
      registry.procedure_setting.airway_type,
      renderEvidenceChips(ev["procedure_setting.airway_type"] || []),
    ]);
  }

  if (rows.length === 0) {
    section.querySelector(
      ".report-body"
    ).innerHTML = `<div class="subtle" style="text-align:center;">No clinical context found</div>`;
    return section;
  }

  section.querySelector(".report-body").innerHTML = `
    <table class="data-table">
      <thead><tr><th style="width:25%">Field</th><th>Value</th><th>Evidence</th></tr></thead>
      <tbody>
        ${rows
          .map(
            ([k, v, e]) =>
              `<tr><td><strong>${safeHtml(k)}</strong></td><td>${safeHtml(
                v
              )}</td><td>${e}</td></tr>`
          )
          .join("")}
      </tbody>
    </table>
  `;
  return section;
}

// --- 6. Procedures Performed ---
function renderProceduresSection(procedures, data) {
  const container = document.createElement('div');
  const ev = getEvidenceMap(data);

  // A. Main Procedures List
  const summarySection = createSection('Procedures Performed', '🔍');
  const summaryRows = Object.entries(procedures).map(([key, proc]) => {
    if (!proc || proc.performed !== true) return '';
    const name = key.replace(/_/g, ' ').toUpperCase();
    const evKey = `procedures_performed.${key}.performed`;
    const evidenceHtml = renderEvidenceChips(ev[evKey] || []);

    // Extract key details based on procedure type
    let details = [];
    if (typeof proc.inspection_findings === "string") {
      const snippet = proc.inspection_findings.length > 50
        ? `${proc.inspection_findings.substring(0, 50)}...`
        : proc.inspection_findings;
      details.push(`Findings: ${snippet}`);
    }
    if (proc.material) details.push(`Material: ${proc.material}`);
    if (Array.isArray(proc.stations_sampled))
      details.push(`Stations: ${proc.stations_sampled.join(', ')}`);

    return `
            <tr>
                <td><strong>${safeHtml(name)}</strong></td>
                <td><span class="status-badge status-selected">Yes</span></td>
                <td>${safeHtml(details.join('; ') || '-')}</td>
                <td>${evidenceHtml}</td>
            </tr>
        `;
  }).filter(Boolean).join('');

  summarySection.querySelector('.report-body').innerHTML = `
        <table class="data-table">
            <thead><tr><th>Procedure</th><th>Performed</th><th>Key Details</th><th>Evidence</th></tr></thead>
            <tbody>${summaryRows}</tbody>
        </table>
    `;
  container.appendChild(summarySection);

  // B. Special Linear EBUS Detail Table
  if (procedures.linear_ebus && procedures.linear_ebus.performed) {
    const ebus = procedures.linear_ebus;
    const ebusSection = createSection('Linear EBUS Details', '📊');

    // General Attributes
    const stationsSampled = Array.isArray(ebus.stations_sampled) ? ebus.stations_sampled.join(", ") : "-";
    let attrRows = `
            <tr><td><strong>Stations Sampled</strong></td><td>${stationsSampled}</td></tr>
            <tr><td><strong>Needle Gauge</strong></td><td>${ebus.needle_gauge || '-'}</td></tr>
            <tr><td><strong>Elastography Used</strong></td><td>${ebus.elastography_used ? 'Yes' : 'No'}</td></tr>
        `;

    let nodeTable = '';
    if (Array.isArray(ebus.node_events) && ebus.node_events.length > 0) {
      const nodeRows = ebus.node_events.map(ev => `
                <tr>
                    <td>${ev.station || '-'}</td>
                    <td>${ev.action || '-'}</td>
                    <td style="font-style:italic; color:#64748b">"${ev.evidence_quote || ''}"</td>
                </tr>
            `).join('');

      nodeTable = `
                <h4 style="margin:1rem 0 0.5rem; font-size:0.9rem; color:#475569">Node Events</h4>
                <table class="data-table">
                    <thead><tr><th>Station</th><th>Action</th><th>Documentation Evidence</th></tr></thead>
                    <tbody>${nodeRows}</tbody>
                </table>
            `;
    }

    ebusSection.querySelector('.report-body').innerHTML = `
            <table class="data-table" style="margin-bottom:1rem">
                <thead><tr><th style="width:30%">Attribute</th><th>Value</th></tr></thead>
                <tbody>${attrRows}</tbody>
            </table>
            ${nodeTable}
        `;
    container.appendChild(ebusSection);
  }

  return container;
}

// --- 7. Audit & QA Notes ---
function renderAuditNotes(warnings) {
  const section = createSection('Audit & QA Notes (Condensed)', '⚠️');

  // Simple heuristic to categorize strings like "CATEGORY: Message"
  const parsed = warnings.map(w => {
    const match = w.match(/^([A-Z_]+):\s*(.+)$/);
    return match
      ? { cat: match[1], msg: match[2] }
      : { cat: 'General', msg: w };
  });

  const rows = parsed.map(item => `
        <tr>
            <td style="width:25%"><strong>${item.cat}</strong></td>
            <td>${item.msg}</td>
        </tr>
    `).join('');

  section.querySelector('.report-body').innerHTML = `
        <table class="data-table">
            <thead><tr><th>Category</th><th>Message</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>
    `;
  return section;
}

/**
 * Render the CPT codes table with descriptions, confidence, RVU, and payment.
 */
function renderLegacyCPTTable(data) {
  const section = createSection("CPT Codes", "💳");
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

  section.querySelector(".report-body").innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Code</th>
          <th>Description</th>
          <th>Confidence</th>
          <th>RVU</th>
          <th>Payment</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;

  return section;
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
  const editorHost = document.getElementById("editor");
  const fallbackTextarea = document.getElementById("fallbackTextarea");

  // Let users paste/typing immediately; Monaco boot can lag on first load.
  if (fallbackTextarea) {
    fallbackTextarea.classList.remove("hidden");
    fallbackTextarea.disabled = false;
  }

  setStatus("Ready to type (model loading in background)...");

  let usingPlainEditor = true;
  let editor = null;
  let model = null;

  // Try to boot Monaco quickly, but never hang the app if it stalls.
  if (window.__monacoReady) {
    try {
      await Promise.race([
        window.__monacoReady,
        new Promise((_, reject) => setTimeout(() => reject(new Error("Monaco load timeout")), 2500)),
      ]);
      usingPlainEditor = false;
    } catch {
      usingPlainEditor = true;
    }
  }

  const crossOriginIsolated = globalThis.crossOriginIsolated === true;
  if (!crossOriginIsolated) {
    setStatus(
      "Cross-origin isolation is OFF (SharedArrayBuffer unavailable). Running in single-threaded mode."
    );
  } else if (usingPlainEditor) {
    setStatus("Loading… (basic editor mode; Monaco still initializing)");
  }

  if (!usingPlainEditor && editorHost) {
    const initialValue = fallbackTextarea ? fallbackTextarea.value : "";
    if (fallbackTextarea) fallbackTextarea.remove();

    editor = monaco.editor.create(editorHost, {
      value: initialValue,
      language: "plaintext",
      theme: "vs-dark",
      minimap: { enabled: false },
      wordWrap: "on",
      fontSize: 13,
      automaticLayout: true,
    });
    // Expose for evidence click-to-highlight
    window.editor = editor;
    model = editor.getModel();
  } else {
    // Monaco unavailable/slow: use the built-in textarea as the editor surface.
    window.editor = null;
    model = {
      getValue: () => (fallbackTextarea ? fallbackTextarea.value : ""),
      setValue: (value) => {
        if (!fallbackTextarea) return;
        fallbackTextarea.value = String(value ?? "");
      },
    };
  }

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
  if (!usingPlainEditor && editor) {
    editor.onDidChangeCursorSelection((e) => {
      const selection = e.selection;
      const hasSelection = !selection.isEmpty();

      currentSelection = hasSelection ? selection : null;

      // Only enable Add button if we have a selection and aren't running detection
      if (addRedactionBtn) {
        addRedactionBtn.disabled = !hasSelection || running;
      }
    });
  } else if (fallbackTextarea) {
    const updateSelection = () => {
      const start = fallbackTextarea.selectionStart;
      const end = fallbackTextarea.selectionEnd;
      const hasSelection = Number.isFinite(start) && Number.isFinite(end) && end > start;

      currentSelection = hasSelection ? { start, end } : null;

      if (addRedactionBtn) {
        addRedactionBtn.disabled = !hasSelection || running;
      }
    };

    fallbackTextarea.addEventListener("select", updateSelection);
    fallbackTextarea.addEventListener("mouseup", updateSelection);
    fallbackTextarea.addEventListener("keyup", updateSelection);
    updateSelection();
  }

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
    if (!usingPlainEditor && editor) {
      decorations = editor.deltaDecorations(decorations, []);
    } else {
      decorations = [];
    }
    detectionsListEl.innerHTML = "";
    detectionsCountEl.textContent = "0";
    applyBtn.disabled = true;
    revertBtn.disabled = true;
    lastServerResponse = null;
    if (exportBtn) exportBtn.disabled = true;
  }

  function updateDecorations() {
    if (usingPlainEditor || !editor) return;

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

  if (!usingPlainEditor && typeof model?.onDidChangeContent === "function") {
    model.onDidChangeContent(() => {
      if (suppressDirtyFlag) return;
      setScrubbedConfirmed(false);
      revertBtn.disabled = running || originalText === model.getValue();
    });
  } else if (fallbackTextarea) {
    fallbackTextarea.addEventListener("input", () => {
      if (suppressDirtyFlag) return;
      setScrubbedConfirmed(false);
      revertBtn.disabled = running || originalText === model.getValue();
    });
  }

  let worker = null;
  let workerReady = false;
  let lastWorkerMessageAt = Date.now();
  let aiModelReady = false;
  let aiModelFailed = false;
  let aiModelError = null;
  let legacyFallbackAttempted = false;
  let usingLegacyWorker = false;
  let workerInitTimer = null;

  function clearWorkerInitTimer() {
    if (!workerInitTimer) return;
    clearTimeout(workerInitTimer);
    workerInitTimer = null;
  }

  function shouldForceLegacyWorker() {
    const params = new URLSearchParams(location.search);
    if (params.get("legacy") === "1") return true;

    const ua = navigator.userAgent || "";
    const isIOSDevice =
      /iPad|iPhone|iPod/i.test(ua) || (ua.includes("Mac") && "ontouchend" in document);
    const isSafari =
      /Safari/i.test(ua) && !/Chrome|CriOS|FxiOS|EdgiOS|OPR/i.test(ua);
    return isIOSDevice && isSafari;
  }

  function buildWorkerUrl(name) {
    return `/ui/${name}?v=${Date.now()}`;
  }

  function startWorker({ forceLegacy = false } = {}) {
    if (worker) {
      try {
        worker.terminate();
      } catch (err) {
        // ignore
      }
    }

    workerReady = false;
    aiModelReady = false;
    aiModelFailed = false;
    aiModelError = null;

    let nextWorker = null;
    let nextIsLegacy = forceLegacy;

    if (!forceLegacy) {
      try {
        nextWorker = new Worker(buildWorkerUrl("redactor.worker.js"), { type: "module" });
        nextIsLegacy = false;
      } catch (err) {
        legacyFallbackAttempted = true;
        nextIsLegacy = true;
        setStatus("Module worker unsupported; falling back to legacy worker…");
      }
    }

    if (!nextWorker) {
      nextWorker = new Worker(buildWorkerUrl("redactor.worker.legacy.js"));
      nextIsLegacy = true;
    }

    worker = nextWorker;
    usingLegacyWorker = nextIsLegacy;
    attachWorkerHandlers(worker);
    worker.postMessage({ type: "init", debug: WORKER_CONFIG.debug, config: WORKER_CONFIG });
    clearWorkerInitTimer();
    workerInitTimer = setTimeout(() => {
      if (!workerReady) {
        setStatus(
          "Worker initializing… (first load can take a few minutes). If this stalls, check DevTools."
        );
      }
    }, 8000);
  }

  function attachWorkerHandlers(activeWorker) {
    activeWorker.addEventListener("error", (ev) => {
      clearWorkerInitTimer();
      if (!usingLegacyWorker && !legacyFallbackAttempted) {
        legacyFallbackAttempted = true;
        setStatus("Module worker failed to load; falling back to legacy worker…");
        setProgress("");
        running = false;
        cancelBtn.disabled = true;
        runBtn.disabled = true;
        applyBtn.disabled = true;
        startWorker({ forceLegacy: true });
        return;
      }
      setStatus(`Worker error: ${ev.message || "failed to load"}`);
      setProgress("");
      running = false;
      cancelBtn.disabled = true;
      runBtn.disabled = true;
      applyBtn.disabled = true;
    });

    activeWorker.addEventListener("messageerror", () => {
      clearWorkerInitTimer();
      setStatus("Worker message error (serialization failed)");
      setProgress("");
      running = false;
      cancelBtn.disabled = true;
      runBtn.disabled = true;
      applyBtn.disabled = true;
    });

    activeWorker.onmessage = (e) => {
      const msg = e.data;
      if (!msg || typeof msg.type !== "string") return;
      lastWorkerMessageAt = Date.now();

      if (msg.type === "ready") {
        clearWorkerInitTimer();
        workerReady = true;
        setStatus("Ready (local model loaded)");
        setProgress("");
        runBtn.disabled = !workerReady;
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
        runBtn.disabled = !workerReady;
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
        clearWorkerInitTimer();
        running = false;
        cancelBtn.disabled = true;
        runBtn.disabled = !workerReady;
        applyBtn.disabled = !hasRunDetection;
        setStatus(`Error: ${msg.message || "unknown"}`);
        setProgress("");
        return;
      }
    };
  }

  const forceLegacy = shouldForceLegacyWorker();
  if (forceLegacy) {
    legacyFallbackAttempted = true;
    setStatus("Using legacy worker for Safari compatibility…");
  }
  startWorker({ forceLegacy });

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

    suppressDirtyFlag = true;
    try {
      if (!usingPlainEditor && editor) {
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

        editor.executeEdits("phi-redactor", edits);
      } else {
        let text = model.getValue();
        // Apply replacements from the end to preserve offsets.
        for (const d of spans) {
          const start = clamp(d.start, 0, text.length);
          const end = clamp(d.end, 0, text.length);
          if (end <= start) continue;
          text = `${text.slice(0, start)}[REDACTED]${text.slice(end)}`;
        }
        model.setValue(text);
      }
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
      if (!usingPlainEditor && editor) editor.setValue(originalText);
      else model.setValue(originalText);
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
      if (!currentSelection) return;

      let startOffset = 0;
      let endOffset = 0;
      if (!usingPlainEditor) {
        if (typeof currentSelection.isEmpty === "function" && currentSelection.isEmpty()) return;
        startOffset = model.getOffsetAt(currentSelection.getStartPosition());
        endOffset = model.getOffsetAt(currentSelection.getEndPosition());
      } else {
        startOffset = Number(currentSelection.start) || 0;
        endOffset = Number(currentSelection.end) || 0;
        if (endOffset <= startOffset) return;
      }

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
      if (!usingPlainEditor && editor) {
        editor.setSelection(new monaco.Selection(0, 0, 0, 0));
      } else if (fallbackTextarea) {
        fallbackTextarea.focus();
        fallbackTextarea.setSelectionRange(0, 0);
      }
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
