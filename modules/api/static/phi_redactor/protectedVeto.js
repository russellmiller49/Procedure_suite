/**
 * Protection/Veto layer for PHI Redactor (Interventional Pulmonology)
 * UPDATED: Added Lookahead/Lookbehind for split tokens (10R, x3, SUV 13.7)
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
// 1. CONSTANTS & LISTS
// =============================================================================

const PHYSICIAN_TITLES_RE = /\b(?:Dr\.|Doctor|Attending|Fellow|Surgeon|Physician|Pulmonologist|Anesthesiologist|Oncologist|Radiologist|Pathologist|Cytopathologist|MD|DO|RN|RT|CRNA|PA|NP|Operator|Staff|Proctored\s+by|Supervising|Resident|Intern|Chief|Director)\b/i;

const AMBIGUOUS_MANUFACTURERS = new Set([
  "noah", "wang", "cook", "mark", "baker", "young", "king", "edwards",
  "olympus", "boston", "stryker", "intuitive", "auris", "fujifilm",
  "pentax", "medtronic", "merit", "conmed", "erbe", "karl storz"
]);

const DEVICE_CONTEXT_KEYWORDS = [
  "medical", "needle", "catheter", "echotip", "fiducial", "marker",
  "system", "platform", "robot", "forceps", "biopsy", "galaxy",
  "scientific", "surgical", "healthcare", "endoscopy", "bronchoscope", "scope"
];

const ROBOTIC_PLATFORMS = new Set(["ion", "monarch", "galaxy", "superdimension", "illumisite", "lungvision", "veran", "archimedes"]);
const ROBOTIC_CONTEXT_RE = /\b(?:robotic|bronchoscopy|system|platform|robot|catheter|controller|console)\b/i;

// --- EXPANDED ANATOMY LIST ---
const IP_SPECIFIC_ANATOMY = new Set([
  "rul", "rml", "rll", "lul", "lll", "lingula", "lingular",
  "right upper lobe", "right middle lobe", "right lower lobe",
  "left upper lobe", "left lower lobe",
  "upper lobe", "lower lobe", "middle lobe",
  "mediastinum", "mediastinal", "hilum", "hilar", "pleura", "pleural",
  "trachea", "carina", "mainstem", "main stem", "bronchus", "bronchi",
  "intermedius", "bronchus intermedius", "rms", "lms",
  "rb1", "rb2", "rb3", "rb4", "rb5", "rb6", "rb7", "rb8", "rb9", "rb10",
  "lb1", "lb2", "lb3", "lb4", "lb5", "lb6", "lb7", "lb8", "lb9", "lb10",
  "lb1+2", "lb7+8", 
  "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
  "station 1", "1r", "1l", "station 2", "2r", "2l", "station 3", "3a", "3p", 
  "station 4", "4r", "4l", "station 5", "station 6", "station 7", "subcarinal", "7",
  "station 8", "station 9", "station 10", "10r", "10l", "station 11", "11r", "11l", "11rs", "11ri",
  "station 12", "12r", "12l", "station 13", "13r", "13l", "station 14", "14r", "14l"
]);

const CLINICAL_ALLOW_LIST = new Set([
  "rose", "rapid on-site evaluation", "lymphocytes", "atypical", "cells",
  "granuloma", "granulomatous", "suspicious", "malignancy", "malignant", "benign",
  "adenocarcinoma", "squamous", "nsclc", "scc", "sclc", "small cell", "carcinoid",
  "ebus", "tbna", "bal", "tbbx", "bronchoscopy", "thoracoscopy", "nav",
  "radial", "linear", "endobronchial", "ultrasound",
  "forceps", "needle", "catheter", "scope", "probe", "basket", "snare",
  "cryoprobe", "apc", "microdebrider", "stent", "balloon", "pleurx", "aspira",
  "lidocaine", "fentanyl", "midazolam", "versed", "propofol", "epinephrine",
  "ga", "ett", "asa", "npo", "nkda", "ebl", "ptx", "cxr", "cbct", "pacu", "icu",
  "french", "fr", "suv"
]);

// =============================================================================
// 2. REGEX PATTERNS
// =============================================================================

const MEASUREMENT_PATTERN = /^[<>≤≥]?\s*\d+(\.\d+)?\s*(ml|cc|mm|cm|m|atm|psi|mg|g|kg|mcg|%|fr|gauge|ga|l|lpm|sec|min|hrs?|weeks?|days?|months?)$/i;
const MEASUREMENT_CONTEXT_PATTERN = /\b(ml|cc|mm|cm|atm|psi|mg|mcg|ebl|blood loss|inflation|diameter|length|size|volume|pressure|duration|cycles?)\b/i;
const SINGLE_CHAR_PATTERN = /^[^a-zA-Z0-9]$/; 
const ISOLATED_DIGIT_PATTERN = /^\d{1,2}$/;
const CREDENTIAL_SUFFIX_RE = /^[,\s]+(?:MD|DO|RN|CRNA|PA|NP|PhD|FCCP|DAABIP)\b/i;
const STATION_PATTERN_RE = /^(?:1[0-4]|[1-9])[rl](?:[is])?$/i;
const SEGMENT_PATTERN_RE = /^[rl]?b\d+(?:\+\d+)?$/i;

// New: Frequency pattern "x3", "x4"
const FREQUENCY_RE = /^x\d+$/i;

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

// =============================================================================
// 4. LOGIC FUNCTIONS
// =============================================================================

function isPhysicianName(slice, fullText, start, end) {
  const lineContext = getLineContext(fullText, start, end);
  const beforeContext = fullText.slice(Math.max(0, start - 50), start);
  const afterContext = fullText.slice(end, Math.min(fullText.length, end + 20));

  if (/\bDr\.\s*$/i.test(beforeContext)) return true;
  if (CREDENTIAL_SUFFIX_RE.test(afterContext)) return true;
  if (/(?:performed|supervision|signed|attested|dictated|reviewed|cosigned)\s*(?:by|of)?\s*[:\-]?\s*$/i.test(beforeContext)) return true;
  
  const titleMatch = lineContext.match(PHYSICIAN_TITLES_RE);
  if (titleMatch) {
    const titleEnd = lineContext.indexOf(titleMatch[0]) + titleMatch[0].length;
    if ((start - getLineContext(fullText, start, end).indexOf(lineContext[0])) > titleEnd) {
      return true;
    }
  }
  return false;
}

function isDeviceManufacturerContext(slice, fullText, start, end) {
  const norm = normalizeTerm(slice);
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
  };

  protectedTerms._index = index;
  return index;
}

export function applyVeto(spans, fullText, protectedTerms, opts = {}) {
  if (!Array.isArray(spans) || typeof fullText !== "string") return [];
  
  const index = buildIndex(protectedTerms);
  const activeIndex = index || {
    anatomySet: IP_SPECIFIC_ANATOMY,
    deviceSet: new Set(),
    codeMarkers: [],
    stationMarkers: []
  };

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
    const label = (span.label || "").toUpperCase();

    // Lookahead/Lookbehind slices (Check next/prev 5 chars)
    const nextChars = fullText.slice(end, end + 5).toLowerCase();
    const prevChars = fullText.slice(Math.max(0, start - 5), start).toLowerCase();

    let veto = false;
    let reason = null;

    // --- 1. IP Specific Anatomy ---
    if (!veto && activeIndex.anatomySet.has(norm)) {
      veto = true;
      reason = "anatomy_list";
    }

    // --- 2. Regex for Stations/Segments (11Rs, RB1, x3) ---
    if (!veto) {
      if (STATION_PATTERN_RE.test(compact) || SEGMENT_PATTERN_RE.test(compact) || FREQUENCY_RE.test(compact)) {
         if (!slice.includes("/") && !slice.includes("-")) {
            veto = true;
            reason = "clinical_pattern_regex";
         }
      }
    }

    // --- 3. Split Token Rescue (10 detected, next char is R) ---
    // This fixes "10R" where only "10" is detected
    if (!veto && /^\d{1,2}$/.test(compact)) {
        // Check if immediately followed by R, L, r, l (Station)
        if (/^[rl]/.test(nextChars)) {
            veto = true;
            reason = "station_suffix_lookahead";
        }
        // Check if immediately followed by 'x' (Frequency reverse case) usually x3 but maybe 3x? 
        // More common: "x 3" -> if "3" detected, check prev
        if (/x\s*$/.test(prevChars)) {
            veto = true;
            reason = "frequency_prefix_lookbehind";
        }
        // Check if followed by "wks" or "weeks" (Duration)
        if (/^\s*w(?:ee)?ks/.test(nextChars)) {
            veto = true;
            reason = "duration_suffix_lookahead";
        }
    }

    // --- 4. SUV Rescue (13.7 detected, prev is SUV) ---
    if (!veto && /^[\d\.]+$/.test(compact)) {
        if (/suv\s*[:\-]?\s*$/i.test(prevChars)) {
            veto = true;
            reason = "suv_value_lookbehind";
        }
    }

    // --- 5. Robotic Platforms ---
    if (!veto && isRoboticPlatform(slice, fullText, start, end)) {
      veto = true;
      reason = "robotic_platform";
    }

    // --- 6. Clinical Allow List ---
    if (!veto && CLINICAL_ALLOW_LIST.has(norm)) {
      veto = true;
      reason = "clinical_allow_list";
    }

    // --- 7. Measurements (<5ml) ---
    if (!veto && MEASUREMENT_PATTERN.test(slice.trim())) {
      veto = true;
      reason = "measurement_pattern";
    }

    // --- 8. Physician Name Protection ---
    if (!veto && (label.includes("PATIENT") || label.includes("PERSON"))) {
      if (isPhysicianName(slice, fullText, start, end)) {
        veto = true;
        reason = "physician_role_or_credential";
      }
    }

    // --- 9. Noise Filter ---
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
    
    vetoed.push(span);
  }

  return vetoed;
}