/**
 * Protection/Veto layer for PHI Redactor (Interventional Pulmonology)
 *
 * Refactored to include logic from phi_redactor_hybrid.py.
 * Combines allowlist patterns, contextual regex, and browser-side veto logic.
 */

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

// =============================================================================
// 1. CONSTANTS & LISTS (Ported from Python)
// =============================================================================

// Physician titles and role headers
const PHYSICIAN_TITLES_RE = /\b(?:Dr\.|Doctor|Attending|Fellow|Surgeon|Physician|Pulmonologist|Anesthesiologist|Oncologist|Radiologist|Pathologist|Cytopathologist|MD|DO|RN|RT|CRNA|PA|NP|Operator|Staff|Proctored\s+by|Supervising|Resident|Intern|Chief|Director)\b/i;

// Ambiguous device manufacturers that look like names (Needs context)
const AMBIGUOUS_MANUFACTURERS = new Set([
  "noah", "wang", "cook", "mark", "baker", "young", "king", "edwards",
  "olympus", "boston", "stryker", "intuitive", "auris", "fujifilm",
  "pentax", "medtronic", "merit", "conmed", "erbe", "karl storz"
]);

// Context words that prove an ambiguous name is actually a device
const DEVICE_CONTEXT_KEYWORDS = [
  "medical", "needle", "catheter", "echotip", "fiducial", "marker",
  "system", "platform", "robot", "forceps", "biopsy", "galaxy",
  "scientific", "surgical", "healthcare", "endoscopy", "bronchoscope", "scope"
];

// Specific Robotic Platforms (High false positive rate for "Ion" and "Galaxy")
const ROBOTIC_PLATFORMS = new Set(["ion", "monarch", "galaxy", "superdimension", "illumisite", "lungvision", "veran", "archimedes"]);
const ROBOTIC_CONTEXT_RE = /\b(?:robotic|bronchoscopy|system|platform|robot|catheter|controller|console)\b/i;

// Extended Anatomy (Segments, Airways, Stations)
const IP_SPECIFIC_ANATOMY = new Set([
  // Lobes
  "rul", "rml", "rll", "lul", "lll", "lingula", "lingular",
  // Segments (B1-B10) & Combined
  "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
  "b1+2", "b7+8", "rb1", "rb2", "rb3", "rb4", "rb5", "rb6",
  "lb1", "lb2", "lb3", "lb4", "lb5", "lb6",
  // Airways
  "trachea", "carina", "bronchus", "bronchi", "mainstem", "main stem",
  "rms", "lms", "intermedius",
  // Stations
  "4r", "4l", "7", "10r", "10l", "11r", "11l", "2r", "2l", "1r", "1l",
  "subcarinal", "paratracheal", "hilar", "mediastinal", "hilum",
  // Other
  "vocal cords", "glottis", "subglottis", "epiglottis", "larynx", "pleura"
]);

const CLINICAL_ALLOW_LIST = new Set([
  // ROSE / Path
  "rose", "rapid on-site evaluation", "lymphocytes", "atypical", "cells",
  "granuloma", "granulomatous", "suspicious", "malignancy", "malignant", "benign",
  "adenocarcinoma", "squamous", "nsclc", "scc", "sclc", "small cell", "carcinoid",
  // Procedures
  "ebus", "tbna", "bal", "tbbx", "bronchoscopy", "thoracoscopy", "nav",
  "radial", "linear", "endobronchial", "ultrasound",
  // Tools
  "forceps", "needle", "catheter", "scope", "probe", "basket", "snare",
  "cryoprobe", "apc", "microdebrider", "stent", "balloon", "pleurx", "aspira",
  // Meds/Abbr
  "lidocaine", "fentanyl", "midazolam", "versed", "propofol", "epinephrine",
  "ga", "ett", "asa", "npo", "nkda", "ebl", "ptx", "cxr", "cbct", "pacu", "icu"
]);

// =============================================================================
// 2. REGEX PATTERNS
// =============================================================================

const MEASUREMENT_PATTERN = /^[<>≤≥]?\s*\d+(\.\d+)?\s*(ml|cc|mm|cm|m|atm|psi|mg|g|kg|mcg|%|fr|gauge|ga|l|lpm|sec|min|hrs?|weeks?|days?|months?)$/i;
const MEASUREMENT_CONTEXT_PATTERN = /\b(ml|cc|mm|cm|atm|psi|mg|mcg|ebl|blood loss|inflation|diameter|length|size|volume|pressure|duration|cycles?)\b/i;
const SINGLE_CHAR_PATTERN = /^[^a-zA-Z0-9]$/; 
const ISOLATED_DIGIT_PATTERN = /^\d{1,2}$/;

// Matches "Name, MD" or "Name, RN" pattern
const CREDENTIAL_SUFFIX_RE = /^[,\s]+(?:MD|DO|RN|CRNA|PA|NP|PhD|FCCP|DAABIP)\b/i;

// =============================================================================
// 3. CONTEXT HELPERS
// =============================================================================

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

// =============================================================================
// 4. LOGIC FUNCTIONS
// =============================================================================

function isPhysicianName(slice, fullText, start, end) {
  const lineContext = getLineContext(fullText, start, end);
  const beforeContext = fullText.slice(Math.max(0, start - 50), start);
  const afterContext = fullText.slice(end, Math.min(fullText.length, end + 20));

  // 1. Check for "Dr. Name"
  if (/\bDr\.\s*$/i.test(beforeContext)) return true;

  // 2. Check for "Name, MD" (Credentials)
  if (CREDENTIAL_SUFFIX_RE.test(afterContext)) return true;

  // 3. Check for Signature/Header Context ("Performed by: [Name]")
  // Matches Python's SIGNATURE_RE logic
  if (/(?:performed|supervision|signed|attested|dictated|reviewed|cosigned)\s*(?:by|of)?\s*[:\-]?\s*$/i.test(beforeContext)) {
    return true;
  }

  // 4. Check for Role Headers on same line
  const titleMatch = lineContext.match(PHYSICIAN_TITLES_RE);
  if (titleMatch) {
    const titleEnd = lineContext.indexOf(titleMatch[0]) + titleMatch[0].length;
    // Current span must be AFTER the title
    if ((start - getLineContext(fullText, start, end).indexOf(lineContext[0])) > titleEnd) {
      return true;
    }
  }

  return false;
}

function isDeviceManufacturerContext(slice, fullText, start, end) {
  const norm = normalizeTerm(slice);
  
  // If it's a known ambiguous manufacturer (Cook, Boston), check next words
  if (AMBIGUOUS_MANUFACTURERS.has(norm)) {
    const afterContext = fullText.slice(end, Math.min(fullText.length, end + 20)).toLowerCase();
    for (const keyword of DEVICE_CONTEXT_KEYWORDS) {
      if (afterContext.includes(keyword)) return true;
    }
  }
  return false;
}

function isRoboticPlatform(slice, fullText, start, end) {
  const norm = normalizeTerm(slice);
  if (ROBOTIC_PLATFORMS.has(norm)) {
    // Check surrounding ~30 chars for "robotic", "system", "catheter"
    const context = getContext(fullText, start, end, 30);
    if (ROBOTIC_CONTEXT_RE.test(context)) return true;
  }
  return false;
}

// =============================================================================
// 5. MAIN VETO EXPORT
// =============================================================================

function buildIndex(protectedTerms) {
  if (!protectedTerms) return null;
  if (protectedTerms._index) return protectedTerms._index;

  // Combine JSON protected terms with our hardcoded IP constants
  const index = {
    anatomySet: new Set([
        ...(protectedTerms.anatomy_terms || []).map(normalizeTerm),
        ...IP_SPECIFIC_ANATOMY
    ]),
    deviceSet: new Set([
        ...(protectedTerms.device_manufacturers || []).map(normalizeTerm),
        ...(protectedTerms.protected_device_names || []).map(normalizeTerm),
    ]),
    codeMarkers: (protectedTerms.code_markers || []).map((v) => String(v).toLowerCase()),
    stationMarkers: (protectedTerms.station_markers || []).map((v) => String(v).toLowerCase()),
    lnStationRegex: protectedTerms.ln_station_regex
      ? new RegExp(protectedTerms.ln_station_regex, "i")
      : /^\d{1,2}[lr](?:[is])?$/i,
  };

  protectedTerms._index = index;
  return index;
}

export function applyVeto(spans, fullText, protectedTerms, opts = {}) {
  if (!Array.isArray(spans) || typeof fullText !== "string") return [];
  
  const index = buildIndex(protectedTerms);
  // If no index provided, create a temporary one with just our hardcoded constants
  const activeIndex = index || {
    anatomySet: IP_SPECIFIC_ANATOMY,
    deviceSet: new Set(),
    codeMarkers: [],
    stationMarkers: [],
    lnStationRegex: /^\d{1,2}[lr](?:[is])?$/i
  };

  const debug = Boolean(opts.debug);
  const vetoed = [];

  for (const span of spans) {
    const start = span.start;
    const end = span.end;
    
    // Sanity check
    if (typeof start !== "number" || typeof end !== "number" || end <= start) {
      vetoed.push(span);
      continue;
    }

    const slice = fullText.slice(start, end);
    const norm = normalizeTerm(slice);
    const compact = normalizeCompact(slice);
    const label = (span.label || "").toUpperCase();

    let veto = false;
    let reason = null;

    // --- 1. IP Specific Anatomy (B1, RUL, Station 7) ---
    if (!veto && activeIndex.anatomySet.has(norm)) {
      veto = true;
      reason = "anatomy_list";
    }

    // --- 2. Robotic Platforms (Ion, Monarch) ---
    if (!veto && isRoboticPlatform(slice, fullText, start, end)) {
      veto = true;
      reason = "robotic_platform";
    }

    // --- 3. Ambiguous Device Manufacturers (Cook Medical) ---
    if (!veto && isDeviceManufacturerContext(slice, fullText, start, end)) {
      veto = true;
      reason = "device_manufacturer_context";
    }

    // --- 4. General Device Set (from JSON) ---
    if (!veto && activeIndex.deviceSet.has(norm)) {
      veto = true;
      reason = "device_list";
    }

    // --- 5. Clinical Allow List (ROSE, EBUS) ---
    if (!veto && CLINICAL_ALLOW_LIST.has(norm)) {
      veto = true;
      reason = "clinical_allow_list";
    }

    // --- 6. Lymph node station "7" with context ---
    if (!veto && compact === "7") {
      const context = getContext(fullText, start, end, 40);
      if (hasMarker(context, activeIndex.stationMarkers) || /\bstation\b/i.test(context)) {
        veto = true;
        reason = "ln_station7";
      }
    }

    // --- 7. LN Station Patterns (4L, 10R) ---
    if (!veto && compact && activeIndex.lnStationRegex.test(compact)) {
      veto = true;
      reason = "ln_station_regex";
    }

    // --- 8. CPT Codes ---
    if (!veto && /^\d{5}$/.test(compact)) {
      const context = getContext(fullText, start, end, 60);
      if (hasMarker(context, activeIndex.codeMarkers) || /\bcpt\b/i.test(context)) {
        veto = true;
        reason = "cpt_context";
      }
    }

    // --- 9. Measurements (80%, <5ml) ---
    if (!veto && MEASUREMENT_PATTERN.test(slice.trim())) {
      veto = true;
      reason = "measurement_pattern";
    }

    // --- 10. Isolated Digits in Context ---
    if (!veto && ISOLATED_DIGIT_PATTERN.test(compact)) {
      const context = getContext(fullText, start, end, 30);
      if (MEASUREMENT_CONTEXT_PATTERN.test(context)) {
        veto = true;
        reason = "measurement_context";
      }
      // Range check "6-8"
      const surroundingText = getContext(fullText, start, end, 10);
      if (/\d\s*-\s*\d/.test(surroundingText) && !/\//.test(surroundingText)) {
        veto = true;
        reason = "range_number";
      }
    }

    // --- 11. Physician Name Protection (The "Patient" False Positive) ---
    if (!veto && (label.includes("PATIENT") || label.includes("PERSON"))) {
      if (isPhysicianName(slice, fullText, start, end)) {
        veto = true;
        reason = "physician_role_or_credential";
      }
    }

    // --- 12. Short/Noise Filter ---
    if (!veto && slice.length <= 2 && !/^\d+$/.test(slice)) {
      veto = true;
      reason = "too_short";
    }
    
    if (!veto && SINGLE_CHAR_PATTERN.test(slice)) {
      veto = true;
      reason = "single_char";
    }

    if (veto) {
      if (debug) {
        console.log("[VETO]", reason, `"${slice}"`, `(${label})`);
      }
      continue;
    }
    
    // If not vetoed, keep the span
    vetoed.push(span);
  }

  return vetoed;
}