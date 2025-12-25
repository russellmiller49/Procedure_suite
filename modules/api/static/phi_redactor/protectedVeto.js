/**
 * protectedVeto.js - Best-of Veto/Protection Layer (Interventional Pulmonology)
 *
 * Purpose:
 * - Prevent false-positive redactions for clinical tokens (LN stations, segments, measurements, CPT context, etc.)
 * - Keep clinician/provider/staff names visible (Attending/Proceduralist/Fellow/RN/RT/etc.)
 * - Still allow true patient PHI to be redacted (patient names, MRN/IDs, dates, addresses, contact)
 *
 * Input:
 *   spans: [{ start, end, label, score? }, ...]
 *     label is expected to be one of: PATIENT, DATE, GEO, ID, CONTACT (BIO prefixes tolerated)
 *
 * Output:
 *   Returns the filtered spans that should STILL be redacted (i.e., after vetoing “safe” spans).
 */

// =============================================================================
// Helpers
// =============================================================================

function escapeRegExp(value) {
  return String(value || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
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

function normalizeLabel(label) {
  const v = String(label || "").toUpperCase();
  return v.replace(/^B-/, "").replace(/^I-/, "");
}

function makeNormalizedSet(items) {
  const s = new Set();
  for (const item of items || []) s.add(normalizeTerm(item));
  return s;
}

const PHI_LABELS = new Set(["PATIENT", "DATE", "GEO", "ID", "CONTACT"]);
const NAME_LIKE_LABELS = new Set(["PATIENT", "GEO"]); // where “hallucinated name” stopwords tend to appear

// =============================================================================
// Constants / Lists
// =============================================================================

// Titles/roles used to identify clinician/provider/staff context on the same line
const PHYSICIAN_TITLES_RE =
  /\b(?:Dr\.|Doctor|Attending|Assistant|Proceduralist(?:\(s\))?|Operator|Referring(?:\s+Physician)?|Consulting|Consultant|Fellow|Resident|Intern|Chief|Director|Surgeon|Physician|Pulmonologist|Anesthesiologist|Oncologist|Radiologist|Pathologist|Cytopathologist|MD|DO|RN|RT|CRNA|PA|NP|Staff|Support\s+Staff|Proctored\s+by|Supervising)\b/i;

// Ambiguous “name-like” manufacturers that should be protected only when device context is nearby
const AMBIGUOUS_MANUFACTURERS = new Set([
  "noah", "wang", "cook", "mark", "baker", "young", "king", "edwards",
  "olympus", "boston", "stryker", "intuitive", "auris", "fujifilm",
  "pentax", "medtronic", "merit", "conmed", "erbe", "karl storz"
]);

const DEVICE_CONTEXT_KEYWORDS = [
  "medical", "needle", "catheter", "echotip", "fiducial", "marker",
  "system", "platform", "robot", "forceps", "biopsy", "galaxy",
  "scientific", "surgical", "healthcare", "endoscopy", "bronchoscope", "scope",
  "stent", "balloon", "sheath", "guide", "wire", "dilator", "introducer", "kit"
];

const ROBOTIC_PLATFORMS = new Set([
  "ion", "monarch", "galaxy", "superdimension", "illumisite", "lungvision", "veran", "archimedes"
]);
const ROBOTIC_CONTEXT_RE = /\b(?:robotic|bronchoscopy|system|platform|robot|catheter|controller|console)\b/i;

// Stopwords to prevent "patient [REDACTED] stable" when the model hallucinates a name span
// - ALWAYS: function words and clinical verbs that are commonly mis-tagged as names
// - CONTEXTUAL: common header words; applied only for name-like labels (PATIENT/GEO)
const STOPWORDS_ALWAYS = new Set([
  // Function words (almost never names)
  "was", "is", "of", "in", "and", "with", "the", "a", "an", "to", "for", "or", "by", "at",
  "did", "does", "had", "has", "have", "been", "being", "are", "were",
  "will", "would", "could", "should", "may", "might", "must", "can", "shall",
  "if", "then", "so", "but", "not", "no", "yes", "as", "from", "on", "be",
  // Clinical verbs commonly mis-tagged (past participles that look like names)
  "intubated", "extubated", "identified", "placed", "transferred", "discharged", "tolerated",
  "performed", "removed", "obtained", "collected", "noted", "observed", "seen",
  "inserted", "advanced", "positioned", "withdrawn", "administered", "given",
  "sampled", "biopsied", "examined", "evaluated", "assessed", "confirmed",
  "visualized", "located", "accessed", "secured", "completed", "terminated",
  "transported", "admitted", "awakened", "recovered", "stable", "brought",
  "prepared", "draped", "sterilized", "cleaned", "irrigated", "suctioned",
  "prepped", "sedated", "anesthetized", "monitored", "extubated", "weaned",
  "well", "done", "sent", "taken", "made", "used", "needed",
  // Clinical context words that get mis-tagged
  "acceptable", "parameters", "precautions", "under", "general", "anesthesia",
  "sterilely", "aseptically", "routine", "standard", "usual", "uneventful"
]);
const STOPWORDS_CONTEXTUAL = new Set(["patient", "pt", "procedure", "diagnosis", "history", "indication", "findings"]);

// --- IP-specific anatomy / stations / segments (normalized set) ---
const IP_SPECIFIC_ANATOMY = makeNormalizedSet([
  // lobes/regions
  "rul", "rml", "rll", "lul", "lll", "lingula", "lingular",
  "right upper lobe", "right middle lobe", "right lower lobe",
  "left upper lobe", "left lower lobe",
  "upper lobe", "lower lobe", "middle lobe",
  "mediastinum", "mediastinal", "hilum", "hilar", "pleura", "pleural",
  "trachea", "carina", "mainstem", "main stem", "bronchus", "bronchi",
  "intermedius", "bronchus intermedius", "rms", "lms",

  // common segments (typed forms)
  "rb1", "rb2", "rb3", "rb4", "rb5", "rb6", "rb7", "rb8", "rb9", "rb10",
  "lb1", "lb2", "lb3", "lb4", "lb5", "lb6", "lb7", "lb8", "lb9", "lb10",
  "lb1+2", "lb7+8",
  "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10",
  "b1+2", "b7+8",

  // LN stations (IASLC)
  "station 1", "1r", "1l",
  "station 2", "2r", "2l",
  "station 3", "3a", "3p",
  "station 4", "4r", "4l",
  "station 5", "station 6",
  "station 7", "subcarinal", "7",
  "station 8", "station 9",
  "station 10", "10r", "10l",
  "station 11", "11r", "11l", "11rs", "11ri",
  "station 12", "12r", "12l",
  "station 13", "13r", "13l",
  "station 14", "14r", "14l"
]);

// Clinical allow list (normalized)
// IMPORTANT: This list is checked for ALL labels (not just PATIENT/GEO like STOPWORDS_ALWAYS).
// Clinical verbs MUST be here to prevent them slipping through when predicted as DATE/ID/CONTACT.
const CLINICAL_ALLOW_LIST = makeNormalizedSet([
  // ROSE / path
  "rose", "rapid on-site evaluation", "lymphocytes", "atypical", "cells",
  "granuloma", "granulomatous", "suspicious", "malignancy", "malignant", "benign",
  "adenocarcinoma", "squamous", "nsclc", "scc", "sclc", "small cell", "carcinoid",

  // procedures/tools
  "ebus", "tbna", "bal", "tbbx", "bronchoscopy", "thoracoscopy", "nav",
  "radial", "linear", "endobronchial", "ultrasound",
  "forceps", "needle", "catheter", "scope", "probe", "basket", "snare",
  "cryoprobe", "apc", "microdebrider", "stent", "balloon", "pleurx", "aspira",
  "medical thoracoscopy", "pleuroscopy", "rigid bronchoscopy", "flexible bronchoscopy",
  "electromagnetic navigation", "robotic bronchoscopy", "robotic",
  // Equipment - commonly mis-tagged
  "bronchoscope", "videobronchoscope", "fiberoptic", "fiber optic", "optic",
  "endoscope", "laryngoscope", "thoracoscope", "camera", "monitor", "processor",

  // meds/abbr
  "lidocaine", "fentanyl", "midazolam", "versed", "propofol", "epinephrine",
  "ga", "ett", "asa", "npo", "nkda", "ebl", "ptx", "cxr", "cbct", "pacu", "icu",

  // IP-specific abbreviations (commonly mis-tagged)
  "ip", "interventional pulmonology", "pulmonology",
  "d/c", "dc", "dispo", "disposition",
  "or", "operating room",
  "micu", "sicu", "cvicu",
  "f/u", "fu", "follow-up", "followup",

  // Anatomical modifiers
  "bilateral", "unilateral", "proximal", "distal", "central", "peripheral",
  "anterior", "posterior", "superior", "inferior", "lateral", "medial",
  "apical", "basal", "segmental", "subsegmental",

  // Technique/procedure context
  "sterile", "aseptic", "technique", "fashion", "manner",
  "inspection", "examination", "visualization", "registration",

  // frequent mis-tags / tokens
  "french", "fr", "suv", "uptake", "value", "uptake value",
  "standardized uptake value", "maximum standardized uptake value",
  "wks", "wk", "hrs", "mins", "mos", "yrs",
  // Segment terminology
  "segment", "segments", "segmental", "subsegmental",
  // Service/team terminology
  "ip consult", "consult team", "inpatient", "outpatient",
  "consult", "consultation", "follow", "team",

  // === CRITICAL FIX: Clinical Verbs (Fix for Veto Gap) ===
  // These are often misclassified as DATE/ID/CONTACT by the ML model.
  // STOPWORDS_ALWAYS only filters PATIENT/GEO labels, so these MUST be here.
  "placed", "identified", "performed", "obtained", "removed", "inserted",
  "advanced", "positioned", "withdrawn", "administered", "collected",
  "sampled", "biopsied", "examined", "visualized", "located", "accessed",
  "secured", "completed", "transported", "admitted", "discharged",
  "intubated", "extubated", "tolerated", "prepared", "draped",
  "noted", "observed", "seen", "confirmed", "stable", "well",
  "transferred", "sterilely", "aseptically", "routine", "uneventful",
  "cleaned", "irrigated", "suctioned", "awakened", "recovered",
  "given", "taken", "made", "used", "needed", "done", "sent",
  "terminated", "evaluated", "assessed", "sterilized",
  // Safety net for passive voice auxiliaries (in case they get tagged alone)
  "was", "were", "is", "are", "been", "being",
  // Common clinical context words that get mis-tagged
  "acceptable", "parameters", "precautions", "under", "general", "anesthesia",

  // === Additional terms from testing ===
  // Pathology/anatomy descriptors
  "luminal", "mucosal", "submucosal", "endobronchial", "peribronchial",
  "patent", "narrowed", "stenotic", "occluded", "obstructed",
  "middle", "severe", "mild", "moderate", "significant", "minimal",

  // Common phrase patterns that get tagged as entities
  "did well", "will be", "has remained", "has been", "had been",
  "with severe", "with mild", "with moderate",
  "remained stable", "remained intubated", "remained sedated",
  "optic was", "was introduced", "was brought", "was prepped",
  "acceptable parameters", "and follow-up", "and follow up",
  "tolerated the", "tolerated well", "patient tolerated",
  "was sterilely", "was aseptically", "was draped",

  // Additional verbs/auxiliaries
  "will", "would", "could", "should", "may", "might", "must",
  "remained", "continued", "underwent", "received", "required",

  // Outcome descriptors
  "successful", "unsuccessful", "uncomplicated", "complicated",
  "adequate", "inadequate", "satisfactory", "unsatisfactory",
  "good", "poor", "excellent", "fair",

  // === Fix for "scheduled for pathology review" false positives ===
  // Common words that appear after "scheduled for" or "procedure for"
  "pathology", "review", "results", "analysis", "evaluation",
  "core", "lesion", "biopsy", "specimen", "sample", "tissue",
  "follow-up", "followup", "appointment", "consultation",

  // === Fix for sedation terms being tagged as names ===
  "moderate sedation", "deep sedation", "conscious sedation", "mac",
  "monitored anesthesia care", "general anesthesia", "local anesthesia",
  "sedation", "anesthesia", "moderate", "deep", "conscious",

  // === Common procedure-related phrases ===
  "performed on", "performed by", "performed at", "performed with",
  "completed on", "completed by", "done on", "done by",
  "scheduled on", "scheduled for",

  // === Fix for clinical terms at sentence start being tagged as names ===
  // These are common medical terms that appear capitalized at sentence start
  "lymphadenopathy", "hemostasis", "biopsies", "biopsy", "navigation",
  "sarcoidosis", "malignancy", "metastasis", "metastases", "neoplasm",
  "carcinoma", "adenoma", "granuloma", "fibrosis", "inflammation",
  "hemorrhage", "obstruction", "stenosis", "stricture", "lesion",
  "nodule", "mass", "tumor", "tumour", "opacity", "consolidation",
  "effusion", "pneumothorax", "atelectasis", "bronchiectasis",

  // === Common sentence-start words that aren't names ===
  "everything", "nothing", "something", "anything", "everyone", "someone",
  "however", "therefore", "furthermore", "moreover", "meanwhile",
  "overall", "initially", "subsequently", "finally", "ultimately",

  // === Anatomical directional terms ===
  "right side", "left side", "right lung", "left lung",
  "right upper", "right lower", "right middle", "left upper", "left lower",
  "bilateral", "unilateral", "ipsilateral", "contralateral",

  // === Clinical action phrases (Confirm Sarcoidosis, Rule out X) ===
  "confirm", "rule out", "exclude", "evaluate", "assess", "monitor",
  "continue", "discontinue", "initiate", "recommend", "consider"
]);

// =============================================================================
// Regex patterns
// =============================================================================

const MEASUREMENT_PATTERN =
  /^[<>≤≥]?\s*\d+(\.\d+)?\s*(ml|cc|mm|cm|m|mmhg|atm|psi|mg|g|kg|mcg|%|fr|french|gauge|ga|l|lpm|bpm|sec|mins?|min|hrs?|hours?|weeks?|days?|months?)$/i;

const MEASUREMENT_CONTEXT_PATTERN =
  /\b(ml|cc|mm|cm|m|mmhg|atm|psi|mg|mcg|g|kg|%|fr|french|gauge|ga|lpm|bpm|ebl|blood loss|inflation|diameter|length|size|volume|pressure|duration|time|minutes?|hours?|days?|weeks?|months?|cycles?)\b/i;

const SINGLE_CHAR_PUNCT_RE = /^[^a-zA-Z0-9]$/;
const ISOLATED_DIGIT_RE = /^\d{1,2}$/;

// Bronchoscope/device model numbers: EB-1990i, EB-580S, BF-H190, Pentax EB19-J10, etc.
const DEVICE_MODEL_RE = /^(?:EB|BF|CV|EU|GIF|CF|TJF|CLV|OTV|VME|ENF|EPK|EPX|MAJ|OSF|PCF|EG|EUS)[-\s]?[A-Z0-9]{2,10}$/i;

// Duration patterns with unit attached: "1-2wks", "3-5days", "2hrs", "1-2 weeks"
const DURATION_COMPACT_RE = /^\d+(?:\s*-\s*\d+)?\s*(?:wks?|days?|hrs?|mins?|mos?|yrs?|weeks?|hours?|minutes?|months?|years?)$/i;

// Credentials anywhere at end of span (catches “Andrew Nakamura, MD” even if slice includes MD)
const CREDENTIAL_IN_SLICE_RE = /\b(?:MD|DO|PHD|RN|RT|CRNA|PA|NP|FCCP|DAABIP)\b\.?\s*$/i;
// Credentials in the text immediately after a name span
const CREDENTIAL_SUFFIX_RE = /^[,\s]+(?:MD|DO|RN|RT|CRNA|PA|NP|PhD|FCCP|DAABIP)\b/i;

// “11Rs”, “4L”, etc (run on compact)
const STATION_PATTERN_COMPACT_RE = /^(?:1[0-4]|[1-9])[rl](?:[is])?$/i;

// Segment codes in slice form (supports spaces and +): RB1, LB1+2, B7+8
const SEGMENT_PATTERN_SLICE_RE = /^[rl]?b\s*(?:10|[1-9])(?:\s*\+\s*(?:10|[1-9]))?$/i;

// Frequency tokens: x3
const FREQUENCY_COMPACT_RE = /^x\d+$/i;

// =============================================================================
// Context helpers
// =============================================================================

function getContext(fullText, start, end, window) {
  const lo = Math.max(0, start - window);
  const hi = Math.min(fullText.length, end + window);
  return fullText.slice(lo, hi);
}

function getLineBounds(fullText, pos) {
  const lineStart = fullText.lastIndexOf("\n", pos);
  const lineEnd = fullText.indexOf("\n", pos);
  const start = lineStart === -1 ? 0 : lineStart + 1;
  const end = lineEnd === -1 ? fullText.length : lineEnd;
  return { start, end, text: fullText.slice(start, end) };
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
// Logic functions
// =============================================================================

function isRoboticPlatform(slice, fullText, start, end) {
  const norm = normalizeTerm(slice);
  if (!ROBOTIC_PLATFORMS.has(norm)) return false;
  const ctx = getContext(fullText, start, end, 40);
  return ROBOTIC_CONTEXT_RE.test(ctx);
}

function isDeviceManufacturerContext(slice, fullText, start, end) {
  const norm = normalizeTerm(slice);
  if (!AMBIGUOUS_MANUFACTURERS.has(norm)) return false;

  const after = fullText.slice(end, Math.min(fullText.length, end + 60)).toLowerCase();
  const around = getContext(fullText, start, end, 50).toLowerCase();

  for (const keyword of DEVICE_CONTEXT_KEYWORDS) {
    if (after.includes(keyword) || around.includes(keyword)) return true;
  }
  return false;
}

/**
 * Detect “clinician/provider/staff name” context so we can KEEP these names visible.
 * This should return true for:
 * - “Attending: Dr. Laura Brennan”
 * - “Assistant: Miguel Santos (Fellow)”
 * - “Andrew Nakamura, MD”
 * - “RN: Maribel Dean”
 * - “Proceduralist(s): ROBERTO F. CASAL, …”
 */
function isProviderName(slice, fullText, start, end) {
  const sTrim = String(slice || "").trim();

  const before = fullText.slice(Math.max(0, start - 140), start);
  const after = fullText.slice(end, Math.min(fullText.length, end + 80));

  // A) Span itself includes credentials (e.g., “Andrew Nakamura, MD” or “Duane Johnson MD PhD”)
  if (CREDENTIAL_IN_SLICE_RE.test(sTrim)) return true;

  // B) “Dr. <Name>”
  if (/\bDr\.?\s*$/i.test(before)) return true;

  // C) “<Name>, MD/DO/…”
  if (CREDENTIAL_SUFFIX_RE.test(after)) return true;

  // D) Attribution/signature verbs before the name
  if (
    /(?:performed|supervised|supervision|signed|attested|dictated|reviewed|cosigned|authored|operator|assistant|anesthesia|referring|consult(?:ed|ing)?)\s*(?:by|of)?\s*[:\-]?\s*$/i.test(before)
  ) {
    return true;
  }

  // E) Same-line “HEADER: Name” where HEADER is a clinician/staff title
  const line = getLineBounds(fullText, start);
  const relStart = start - line.start;

  const colonIdx = line.text.indexOf(":");
  if (colonIdx !== -1 && relStart > colonIdx) {
    const header = line.text.slice(0, colonIdx);
    if (PHYSICIAN_TITLES_RE.test(header)) return true;
  }

  // F) Same-line title appearing before the name even without a colon (rare)
  const titleMatch = line.text.match(PHYSICIAN_TITLES_RE);
  if (titleMatch) {
    const idx = line.text.toLowerCase().indexOf(titleMatch[0].toLowerCase());
    if (idx !== -1 && relStart > idx + titleMatch[0].length) {
      const between = line.text.slice(idx + titleMatch[0].length, relStart);
      if (/[(:\-]\s*$/.test(between) || /[:\-]/.test(between)) return true;
    }
  }

  return false;
}

// =============================================================================
// Index builder (cached on protectedTerms)
// =============================================================================

function buildIndex(protectedTerms) {
  if (!protectedTerms) return null;
  if (protectedTerms._index) return protectedTerms._index;

  const anatomyTerms = Array.isArray(protectedTerms.anatomy_terms) ? protectedTerms.anatomy_terms : [];
  const deviceManufacturers = Array.isArray(protectedTerms.device_manufacturers) ? protectedTerms.device_manufacturers : [];
  const protectedDeviceNames = Array.isArray(protectedTerms.protected_device_names) ? protectedTerms.protected_device_names : [];

  const index = {
    anatomySet: new Set([
      ...anatomyTerms.map(normalizeTerm),
      ...IP_SPECIFIC_ANATOMY
    ]),
    deviceSet: new Set([
      ...deviceManufacturers.map(normalizeTerm),
      ...protectedDeviceNames.map(normalizeTerm)
    ]),
    codeMarkers: (protectedTerms.code_markers || []).map((v) => String(v).toLowerCase()),
    stationMarkers: (protectedTerms.station_markers || []).map((v) => String(v).toLowerCase())
  };

  protectedTerms._index = index;
  return index;
}

// =============================================================================
// Main export
// =============================================================================

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

  // If true (default), clinician/provider/staff names are kept visible (not redacted).
  const protectProviders = opts.protectProviders !== false;

  // Optional: only apply stopword veto if model confidence is <= threshold.
  // Default: apply regardless (stopwords are not PHI).
  const stopwordMaxScore = typeof opts.stopwordMaxScore === "number" ? opts.stopwordMaxScore : null;

  const kept = [];

  for (const span of spans) {
    const start = span?.start;
    const end = span?.end;

    if (typeof start !== "number" || typeof end !== "number" || end <= start) {
      kept.push(span);
      continue;
    }

    const slice = fullText.slice(start, end);
    const trimmed = slice.trim();

    if (!trimmed) {
      if (debug) console.log("[VETO]", "whitespace", `"${slice}"`);
      continue;
    }

    const norm = normalizeTerm(slice);
    const compact = normalizeCompact(slice);
    const label = normalizeLabel(span.label);

    const score = typeof span.score === "number" ? span.score : null;
    const isKnownPhiLabel = PHI_LABELS.has(label);

    // Lookaround windows (enough to catch “SUV 13.7”, “10 R”, “24 French”, “x 3”, etc.)
    const prev = fullText.slice(Math.max(0, start - 20), start);
    const next = fullText.slice(end, Math.min(fullText.length, end + 20));
    const prevLower = prev.toLowerCase();
    const nextLower = next.toLowerCase();

    let veto = false;
    let reason = null;

    // -------------------------------------------------------------------------
    // 0) STOPWORDS (label-aware)
    // Only for name-like labels (PATIENT/GEO) to avoid interfering with ID/CONTACT/DATE.
    // -------------------------------------------------------------------------
    if (!veto && NAME_LIKE_LABELS.has(label)) {
      const scoreOk =
        stopwordMaxScore === null ? true : (score === null ? true : score <= stopwordMaxScore);

      if (scoreOk && STOPWORDS_ALWAYS.has(norm)) {
        veto = true; reason = "stopword";
      } else if (scoreOk && STOPWORDS_CONTEXTUAL.has(norm)) {
        if (norm === "history") {
          const ctx = getContext(fullText, start, end, 24);
          if (/\bhistory\b\s+of\b/i.test(ctx) || /\b(?:past|medical|social|family)\s+history\b/i.test(ctx)) {
            veto = true; reason = "stopword_history_context";
          }
        } else {
          veto = true; reason = "stopword_contextual";
        }
      }
    }

    // -------------------------------------------------------------------------
    // 0b) Passive voice detection: "was placed", "was identified", etc.
    // When preceded by "was/were", the span is likely a past participle, not a name.
    // CRITICAL FIX: Apply to ALL labels (not just PATIENT/GEO) to catch clinical verbs
    // predicted as DATE/ID/CONTACT.
    // -------------------------------------------------------------------------
    if (!veto) {
      const beforeWindow = fullText.slice(Math.max(0, start - 12), start).toLowerCase();
      if (/\b(?:was|were|is|are|been|being)\s*$/.test(beforeWindow)) {
        // Check if the span looks like a past participle (ends in -ed/-en) or is a known clinical verb
        if (/^[a-z]+(?:ed|en)$/i.test(trimmed) || STOPWORDS_ALWAYS.has(norm)) {
          veto = true; reason = "passive_voice_verb";
        }
      }
    }

    // -------------------------------------------------------------------------
    // 0c) "Patient + verb" pattern: "Patient intubated", "Patient tolerated the"
    // When immediately preceded by "patient", the span is likely a clinical verb, not a name.
    // -------------------------------------------------------------------------
    if (!veto) {
      const beforeWindow = fullText.slice(Math.max(0, start - 12), start).toLowerCase();
      if (/\bpatient\s*$/.test(beforeWindow)) {
        // Check first word of span - if it's a verb or function word, veto the whole span
        const firstWord = trimmed.split(/\s+/)[0].toLowerCase();
        if (STOPWORDS_ALWAYS.has(firstWord) || /^[a-z]+(?:ed|en|ing|s)$/i.test(firstWord)) {
          veto = true; reason = "patient_followed_by_verb";
        }
      }
    }

    // -------------------------------------------------------------------------
    // 0d) Decimal number protection: ".6" in "9.6", ".00" in "12.00"
    // Decimals following digits are clinical values, not PHI.
    // -------------------------------------------------------------------------
    if (!veto && /^\.?\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?$/.test(trimmed)) {
      const beforeChar = start > 0 ? fullText[start - 1] : "";
      // If preceded by a digit or decimal, it's part of a number
      if (/[\d.]/.test(beforeChar)) {
        veto = true; reason = "decimal_continuation";
      }
      // If it's just digits with decimal, check for measurement context
      if (!veto) {
        const ctx = getContext(fullText, start, end, 30);
        if (/\b(?:suv|size|tube|gauge|french|fr|mm|cm|ml|mg|mcg|lpm|bpm)\b/i.test(ctx)) {
          veto = true; reason = "decimal_measurement_context";
        }
      }
    }

    // -------------------------------------------------------------------------
    // 0e) Safe field protection: "Procedure Name:", "Procedure:", "Service:"
    // Values after these headers are clinical terms, not PHI.
    // -------------------------------------------------------------------------
    if (!veto) {
      const beforeWindow = fullText.slice(Math.max(0, start - 30), start).toLowerCase();
      if (/\b(?:procedure(?:\s+name)?|service|technique|indication|diagnosis|impression|findings)\s*:\s*$/i.test(beforeWindow)) {
        // The span following a safe field header is likely a procedure name, not PHI
        if (/^[a-z]/i.test(trimmed) && trimmed.length < 50) {
          veto = true; reason = "safe_field_value";
        }
      }
    }

    // -------------------------------------------------------------------------
    // 0f) "Patient + verb" spans: "Patient is", "Patient was", "Patient has"
    // When the span STARTS with "patient" followed by a common verb, veto it.
    // This catches ML model errors like tagging "Patient is" as a PATIENT entity.
    // -------------------------------------------------------------------------
    if (!veto && NAME_LIKE_LABELS.has(label)) {
      const lowerTrimmed = trimmed.toLowerCase();
      // Check if span starts with "patient" or "the patient" followed by verb
      const patientVerbMatch = lowerTrimmed.match(/^(?:the\s+)?patient\s+(is|was|has|had|will|would|could|should|may|might|can|does|did|presents|presented|underwent|denies|denied|reports|reported|requires|required|needs|needed|appears|appeared|remains|remained|tolerated|developed)\b/);
      if (patientVerbMatch) {
        veto = true; reason = "patient_starts_with_verb";
      }
    }

    // -------------------------------------------------------------------------
    // 1) Explicit anatomy list
    // -------------------------------------------------------------------------
    if (!veto && activeIndex.anatomySet.has(norm)) {
      veto = true; reason = "anatomy_list";
    }

    // -------------------------------------------------------------------------
    // 2) Device allow-list from protectedTerms
    // -------------------------------------------------------------------------
    if (!veto && activeIndex.deviceSet && activeIndex.deviceSet.size) {
      if (activeIndex.deviceSet.has(norm)) {
        veto = true; reason = "device_set_allow";
      }
    }

    // -------------------------------------------------------------------------
    // 3) Stations / Segments / Frequency regex (single-span)
    // -------------------------------------------------------------------------
    if (!veto) {
      // “11Rs”, “4L”
      if (STATION_PATTERN_COMPACT_RE.test(compact)) {
        if (!slice.includes("/") && !slice.includes("-")) {
          veto = true; reason = "station_pattern";
        }
      }

      // “RB1”, “LB1+2”, “B7+8” (use trimmed slice, not compact)
      if (!veto && SEGMENT_PATTERN_SLICE_RE.test(trimmed)) {
        veto = true; reason = "segment_pattern";
      }

      // "x3"
      if (!veto && FREQUENCY_COMPACT_RE.test(compact)) {
        veto = true; reason = "frequency_pattern";
      }

      // Device model numbers: "EB-1990i", "EB-580S", "BF-H190"
      if (!veto && DEVICE_MODEL_RE.test(trimmed)) {
        veto = true; reason = "device_model_number";
      }

      // Duration patterns: "1-2wks", "3-5days", "2hrs"
      if (!veto && DURATION_COMPACT_RE.test(trimmed)) {
        veto = true; reason = "duration_compact_pattern";
      }
    }

    // -------------------------------------------------------------------------
    // 4) Split-token rescues (digit-only spans)
    // -------------------------------------------------------------------------
    if (!veto && ISOLATED_DIGIT_RE.test(compact)) {
      // 4a) “10R” where only “10” is tagged (allow optional whitespace)
      if (/^\s*[rl]\s*(?:[is])?\b/.test(nextLower)) {
        veto = true; reason = "station_suffix_lookahead";
      }

      // 4b) “x 3” where only “3” is tagged
      if (!veto && /x\s*$/.test(prevLower)) {
        veto = true; reason = "frequency_prefix_lookbehind";
      }

      // 4c) “B 3” / “RB 3” / “LB3” where only “3” is tagged
      if (!veto && /[rl]?b\s*$/.test(prevLower)) {
        veto = true; reason = "segment_prefix_lookbehind";
      }

      // 4d) Duration suffix: “3 wks”, “2 days”
      if (
        !veto &&
        /^\s*(w(?:ee)?ks?|days?|hrs?|hours?|mins?|minutes?|sec|seconds?|mo(?:nths?)?)\b/i.test(nextLower)
      ) {
        veto = true; reason = "duration_suffix_lookahead";
      }

      // 4e) Unit suffix: “24 French”, “7 Fr”, “5 ml”
      if (
        !veto &&
        /^\s*(ml|cc|mm|cm|fr(?:ench)?|g|kg|mg|mcg|%|mmhg|bpm|lpm)\b/i.test(nextLower)
      ) {
        veto = true; reason = "unit_suffix_lookahead";
      }

      // 4f) “station/level” digit-only context (generalizes “station 7”)
      if (!veto) {
        const ctx = getContext(fullText, start, end, 50);
        if (
          /\b(?:station|level|ln|lymph\s*node|nodal)\b/i.test(ctx) ||
          hasMarker(ctx, activeIndex.stationMarkers)
        ) {
          veto = true; reason = "station_level_context_digit";
        }
      }
    }

    // -------------------------------------------------------------------------
    // 5) SUV rescue: “SUV 13.7” where only “13.7” is tagged
    // -------------------------------------------------------------------------
    if (!veto && /^[\d.]+$/.test(compact)) {
      if (/\bsuv\s*[:=\-]?\s*$/i.test(prevLower)) {
        veto = true; reason = "suv_value_lookbehind";
      }
    }

    // -------------------------------------------------------------------------
    // 6) Robotic platforms (ION/Monarch) in robotic context
    // -------------------------------------------------------------------------
    if (!veto && isRoboticPlatform(slice, fullText, start, end)) {
      veto = true; reason = "robotic_platform";
    }

    // -------------------------------------------------------------------------
    // 7) Ambiguous manufacturers that look like names (protect only with device context)
    // -------------------------------------------------------------------------
    if (!veto && isDeviceManufacturerContext(slice, fullText, start, end)) {
      veto = true; reason = "device_manufacturer_context";
    }

    // -------------------------------------------------------------------------
    // 8) Clinical allow list (broad but safe)
    // -------------------------------------------------------------------------
    if (!veto && CLINICAL_ALLOW_LIST.has(norm)) {
      veto = true; reason = "clinical_allow_list";
    }

    // -------------------------------------------------------------------------
    // 9) CPT 5-digit protection (context-based)
    // -------------------------------------------------------------------------
    if (!veto && /^\d{5}$/.test(compact)) {
      const ctx = getContext(fullText, start, end, 90);
      if (/\b(?:cpt|code|billing|rvu)\b/i.test(ctx) || hasMarker(ctx, activeIndex.codeMarkers)) {
        veto = true; reason = "cpt_context";
      }
    }

    // -------------------------------------------------------------------------
    // 10) Measurements (full token) + measurement-context rescue
    // -------------------------------------------------------------------------
    if (!veto && MEASUREMENT_PATTERN.test(trimmed)) {
      veto = true; reason = "measurement_pattern";
    }

    if (!veto && ISOLATED_DIGIT_RE.test(compact)) {
      const ctx = getContext(fullText, start, end, 35);
      if (MEASUREMENT_CONTEXT_PATTERN.test(ctx)) {
        veto = true; reason = "measurement_context";
      }
    }

    // -------------------------------------------------------------------------
    // 11) Provider/staff name protection (prevents clinician names being redacted)
    // Only apply when the model calls it a name-like label.
    // -------------------------------------------------------------------------
    if (!veto && protectProviders && NAME_LIKE_LABELS.has(label)) {
      if (isProviderName(slice, fullText, start, end)) {
        veto = true; reason = "provider_role_or_credential";
      }
    }

    // -------------------------------------------------------------------------
    // 12) Noise filter (label-aware)
    // - Don’t veto short PATIENT spans (avoid breaking “Li/Ng” redactions if you need them)
    // - Do veto single punctuation always
    // - For non-PATIENT, veto tiny non-numeric junk
    // -------------------------------------------------------------------------
    if (!veto) {
      if (SINGLE_CHAR_PUNCT_RE.test(trimmed)) {
        veto = true; reason = "single_char_punct";
      }

      if (!veto && trimmed.length <= 2) {
        if (label === "PATIENT") {
          // Do NOT veto: could be a real short surname.
        } else if (!/^\d+$/.test(trimmed)) {
          veto = true; reason = "too_short_non_patient";
        }
      }
    }

    if (veto) {
      if (debug) console.log("[VETO]", reason, `"${slice}"`, `(${label}${score !== null ? ` score=${score}` : ""})`);
      continue; // veto => DO NOT redact this span
    }

    kept.push(span); // keep => SHOULD be redacted
  }

  return kept;
}
