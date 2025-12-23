function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizeTerm(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeCompact(text) {
  return String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, "");
}

function buildIndex(protectedTerms) {
  if (!protectedTerms) return null;
  if (protectedTerms._index) return protectedTerms._index;

  const anatomyTerms = (protectedTerms.anatomy_terms || []).map(normalizeTerm);
  const deviceManufacturers = (protectedTerms.device_manufacturers || []).map(normalizeTerm);
  const deviceNames = (protectedTerms.protected_device_names || []).map(normalizeTerm);

  const index = {
    anatomySet: new Set(anatomyTerms.filter(Boolean)),
    deviceSet: new Set([...deviceManufacturers, ...deviceNames].filter(Boolean)),
    codeMarkers: (protectedTerms.code_markers || []).map((v) => String(v).toLowerCase()),
    stationMarkers: (protectedTerms.station_markers || []).map((v) => String(v).toLowerCase()),
    lnStationRegex: protectedTerms.ln_station_regex
      ? new RegExp(protectedTerms.ln_station_regex, "i")
      : /^\d{1,2}[lr](?:[is])?$/i,
  };

  protectedTerms._index = index;
  return index;
}

function getContext(fullText, start, end, window) {
  const lo = Math.max(0, start - window);
  const hi = Math.min(fullText.length, end + window);
  return fullText.slice(lo, hi);
}

function getLineContext(fullText, start, end) {
  const lineStart = fullText.lastIndexOf("\n", start);
  const lineEnd = fullText.indexOf("\n", end);
  const lo = lineStart === -1 ? 0 : lineStart + 1;
  const hi = lineEnd === -1 ? fullText.length : lineEnd;
  return fullText.slice(lo, hi);
}

function hasMarker(context, markers) {
  if (!context || !markers?.length) return false;
  const lower = context.toLowerCase();
  for (const marker of markers) {
    if (!marker) continue;
    const re = new RegExp(`\\b${escapeRegExp(marker)}\\b`, "i");
    if (re.test(lower)) return true;
  }
  return false;
}

export function applyVeto(spans, fullText, protectedTerms, opts = {}) {
  if (!Array.isArray(spans) || typeof fullText !== "string") return [];
  const index = buildIndex(protectedTerms);
  if (!index) return spans;

  const debug = Boolean(opts.debug);
  const vetoed = [];

  for (const span of spans) {
    const start = span.start;
    const end = span.end;
    if (typeof start !== "number" || typeof end !== "number" || end <= start) {
      vetoed.push(span);
      continue;
    }
    const slice = fullText.slice(start, end);
    const norm = normalizeTerm(slice);
    const compact = normalizeCompact(slice);

    let veto = false;
    let reason = null;

    if (norm && index.anatomySet.has(norm)) {
      veto = true;
      reason = "anatomy";
    }
    if (!veto && norm && index.deviceSet.has(norm)) {
      veto = true;
      reason = "device";
    }

    if (!veto && compact === "7") {
      const context = getContext(fullText, start, end, 40);
      if (hasMarker(context, index.stationMarkers)) {
        veto = true;
        reason = "ln_station7";
      }
    }

    if (!veto && compact && index.lnStationRegex.test(compact)) {
      veto = true;
      reason = "ln_station";
    }

    if (!veto && /^\d{5}$/.test(compact)) {
      const context = getContext(fullText, start, end, 60);
      const line = getLineContext(fullText, start, end);
      if (hasMarker(context, index.codeMarkers) || hasMarker(line, index.codeMarkers)) {
        veto = true;
        reason = "cpt_context";
      }
    }

    if (veto) {
      if (debug) {
        console.log("[VETO]", reason, slice);
      }
      continue;
    }
    vetoed.push(span);
  }

  return vetoed;
}
