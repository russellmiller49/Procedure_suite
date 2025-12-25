/**
 * redactor.worker.js — “Best-of” Hybrid PHI Detector (ML + Regex)
 *
 * Combines:
 *  - Version B robustness: quantized→unquantized fallback, offset recovery, cancel, debug hooks
 *  - Version A fix: expand spans to word boundaries to prevent partial-word redactions
 *  - Hybrid regex injection BEFORE veto (cold-start header guarantees)
 *  - Smarter merge rules: prefer regex spans over overlapping ML spans to avoid double-highlights
 */

import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2";
import { applyVeto } from "./protectedVeto.js";

const MODEL_PATH = "./vendor/phi_distilbert_ner/";
const MODEL_ID = "phi_distilbert_ner";
const MODEL_BASE_URL = new URL("./vendor/", import.meta.url).toString();
const TASK = "token-classification";

// Character windowing (simple + robust)
const WINDOW = 2500;
const OVERLAP = 250;
const STEP = WINDOW - OVERLAP;

// =============================================================================
// HYBRID REGEX DETECTION (guarantees headers/IDs)
// =============================================================================

// Matches: "Patient: Smith, John" or "Pt Name: John Smith" or "Patient Name: Carey , Cloyd D" (footer format)
// Also matches "Pt: C. Rodriguez" (Initial. Lastname format) and "Pt: White, E." (Last, Initial format)
// IMPORTANT: Requires colon/dash delimiter to avoid matching "patient went into" as a name
const PATIENT_HEADER_RE =
  /(?:Patient(?:\s+Name)?|Pt\.?(?:\s+Name)?|Pat\.?|Name|Subject)\s*[:\-]\s*([A-Z][a-z]+\s*,\s*[A-Z]\.?|[A-Z]\.?\s+[A-Z][a-z]+|[A-Z][a-z]+\s*,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?|[A-Z][a-z]+\s+[A-Z]'?[A-Za-z]+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)/gim;

// Matches: "MRN: 12345" or "ID: 55-22-11"
// IMPORTANT: Must contain at least one digit to avoid matching medical acronyms like "rEBUS"
const MRN_RE =
  /\b(?:MRN|MR|Medical\s*Record|Patient\s*ID|ID|EDIPI|DOD\s*ID)\s*[:\#]?\s*([A-Z0-9\-]*\d[A-Z0-9\-]*)\b/gi;

// Matches: MRN with spaces like "A92 555" or "AB 123 456" (2-3 groups of alphanumerics)
const MRN_SPACED_RE =
  /\b(?:MRN|MR|Medical\s*Record|Patient\s*ID|ID)\s*[:\#]?\s*([A-Z0-9]{2,5}\s+[A-Z0-9]{2,5}(?:\s+[A-Z0-9]{2,5})?)\b/gi;

// Matches inline narrative patient names followed by age: "Emma Jones, a 64-year-old male..."
// Also supports "Last, First" format: "Belardes, Lisa is a 64-year-old..."
// Captures: "Emma Jones" or "Belardes, Lisa" when followed by age descriptor
// IMPORTANT: Excludes "The patient", "A patient", etc. via negative lookahead
const INLINE_PATIENT_NAME_RE =
  /\b(?!(?:The|A|An)\s+(?:patient|subject|candidate|individual|person)\b)([A-Z][a-z]+(?:(?:\s+|,\s*)[A-Z]\.?)?(?:\s+|,\s*)[A-Z][a-z]+),?\s+(?:(?:is|was)\s+)?(?:a\s+)?(?:\d{1,3}\s*-?\s*(?:year|yr|y\/?o|yo)[\s-]*old|aged?\s+\d{1,3})\b/gi;

// Matches names after procedural verbs: "performed on Robert Chen", "procedure for Jane Doe"
// Captures patient name when following "performed on/for", "procedure on/for", etc.
// IMPORTANT: Case-sensitive (no 'i' flag) to avoid matching lowercase words like "the core"
const PROCEDURAL_NAME_RE =
  /\b(?:performed|completed|done|scheduled|procedure)\s+(?:on|for)\s+([A-Z][a-z]+(?:'[A-Z][a-z]+)?\s+[A-Z][a-z]+(?:'[A-Z][a-z]+)?)\b/g;

// Matches: "pt Name mrn 1234" pattern common in IP notes
// Captures the name between "pt" and "mrn"
const PT_NAME_MRN_RE =
  /\bpt\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+mrn\s+\d+/gi;

// Matches: "PT Name" standalone (without MRN) in unstructured text
// E.g., "PT James Wilson ID MRN..."
const PT_STANDALONE_RE =
  /\bPT\s+([A-Z][a-z]+(?:'[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+(?:'[A-Z][a-z]+)?)?)\b/g;

// Matches: "Mr./Mrs./Ms./Miss Smith" or "Mr. John Smith" or "Mr. O'Brien"
// IMPORTANT: Case-sensitive for name capture to avoid consuming lowercase verbs like "underwent"
// Only matches names starting with capital letters, supports apostrophe surnames (O'Brien, D'Angelo)
const TITLE_NAME_RE =
  /\b(?:Mr|Mrs|Ms|Miss|Mister|Missus)\.?\s+([A-Z][a-z]*(?:'[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+(?:'[A-Z][a-z]+)?)?)\b/g;

// Matches narrative names: "for [Name]" in context like "bronch for Logan Roy massive bleeding"
// Requires name to be followed by common clinical words to reduce false positives
const NARRATIVE_FOR_NAME_RE =
  /\bfor\s+([A-Z][a-z]+(?:'[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+(?:'[A-Z][a-z]+)?)?)\s+(?:who|with|has|had|massive|severe|acute|chronic|presenting|underwent|scheduled|referred)\b/g;

// Matches de-identification placeholders/artifacts: "<PERSON>", "[Name]", "[REDACTED]", "***NAME***"
// These appear in pre-processed or dirty data and should be redacted to prevent leakage
const PLACEHOLDER_NAME_RE =
  /(?:Patient(?:\s+Name)?|Pt(?:\s+Name)?|Name|Subject)\s*[:\-]?\s*(<[A-Z]+>|\[[A-Za-z_]+\]|\*{2,}[A-Za-z_]+\*{2,})/gi;

// Matches "Patient 69F" shorthand pattern (no colon, alphanumeric identifier)
// Fallback for non-standard patient identifiers like age/gender clusters
const PATIENT_SHORTHAND_RE =
  /\bPatient\s+(\d{1,3}\s*[MF](?:emale)?)\b/gi;

// Matches names at sentence start followed by clinical verbs: "Robert has a LLL nodule..."
// Must be at sentence start (after period/newline) and followed by clinical context
// Requires both first and last name to reduce false positives
const SENTENCE_START_NAME_RE =
  /(?:^|[.!?]\s+|\n\s*)([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:has|had|is|was|presents|presented|underwent|undergoing|needs|needed|required|denies|denied|reports|reported|complained|complains|notes|noted|states|stated|describes|described|exhibits|exhibited|demonstrates|demonstrated|developed|shows|showed|appears|appeared)\b/gm;

// Matches names at very start of line/document followed by period: "Kimberly Garcia. Ion Bronchoscopy."
// For notes that begin directly with patient name without a header label
const LINE_START_NAME_RE =
  /^([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[.,]/gm;

// Matches informal/lowercase names followed by "here for": "jason phillips here for right lung lavage"
// Case-insensitive to catch dictation notes where names aren't capitalized
// The "here for" phrase is a strong indicator of patient context in informal notes
const INFORMAL_NAME_HERE_RE =
  /^([a-z]+\s+[a-z]+)\s+here\s+for\b/gim;

// Matches underscore-wrapped template placeholders: "___Lisa Anderson___", "___BB-8472-K___", "___03/19/1961___"
// These appear in de-identification templates where PHI is wrapped in triple underscores
const UNDERSCORE_NAME_RE =
  /___([A-Za-z][A-Za-z\s]+[A-Za-z])___/g;
const UNDERSCORE_ID_RE =
  /___([A-Z0-9][A-Z0-9\-]+)___/gi;
const UNDERSCORE_DATE_RE =
  /___(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})___/g;

// Matches lowercase honorific + name patterns: "mrs lopez", "mr harris", "ms johnson"
// Case-insensitive to catch dictation/informal notes where names aren't capitalized
const TITLE_NAME_LOWERCASE_RE =
  /\b((?:mr|mrs|ms|miss|mister|missus)\.?\s+[a-z]+(?:\s+[a-z]+)?)\b/gi;

// Matches standalone first names followed by clinical verbs: "liam came in choking", "Frank underwent a procedure"
// Requires first name to be followed by a verb to reduce false positives
const FIRST_NAME_CLINICAL_RE =
  /\b([A-Z][a-z]+)\s+(?:came|went|underwent|presents|presented|needs|needed|required|complains|complained|reports|reported|developed|has|had|is|was)\b/g;

// Matches names after "Procedure note" header: "Procedure note Justin Fowler 71M."
// Common format in procedure documentation headers
const PROCEDURE_NOTE_NAME_RE =
  /\bProcedure\s+note\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b/gi;

// Matches alphanumeric MRN patterns without prefix: "LM-9283", "AB-1234-K"
// For identifiers that look like MRNs but lack the "MRN:" prefix
const STANDALONE_ALPHANUMERIC_ID_RE =
  /\b([A-Z]{2,3}-\d{3,6}(?:-[A-Z0-9])?)\b/g;

// Matches "pt [Name]" prefix patterns in informal notes: "pt Juan C R long term trach"
// Supports mixed case and middle initials
const PT_LOWERCASE_NAME_RE =
  /\bpt\s+([A-Za-z][a-z]*(?:\s+[A-Z])?(?:\s+[A-Z])?(?:\s+[A-Za-z][a-z]+)?)\b/gi;

// Matches lowercase full names at start of line followed by date: "oscar godsey 5/15/19"
// Common in dictation notes where names aren't capitalized
const LOWERCASE_NAME_DATE_RE =
  /^([a-z]+\s+[a-z]+)\s+\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}/gim;

// Matches lowercase names followed by age/gender: "barbara kim 69 female"
// Common format in informal/dictated notes
const LOWERCASE_NAME_AGE_GENDER_RE =
  /^([a-z]+\s+[a-z]+)\s+\d{1,3}\s*(?:year|yr|y\/?o|yo|male|female|m|f)\b/gim;

// Matches lowercase names followed by "here to" (variant of "here for"): "gilbert barkley here to get his stents out"
const INFORMAL_NAME_HERE_TO_RE =
  /^([a-z]+\s+[a-z]+)\s+here\s+to\b/gim;

// Matches lowercase names followed by "note": "michael foster note hard to read"
// Common in resident notes where patient name precedes "note"
const LOWERCASE_NAME_NOTE_RE =
  /^([a-z]+\s+[a-z]+)\s+note\b/gim;

// Matches names at absolute start followed by clinical context (no punctuation required)
// E.g., "Brenda Lewis transplant patient with stenosis" or "John Smith status post lobectomy"
// Requires clinical follow-word to reduce false positives
const NAME_START_CLINICAL_CONTEXT_RE =
  /^([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:transplant|patient|pt|status|post|s\/p|here|presented|presenting|hx|history|scheduled|referred|admitted|seen|evaluated|is|was|with|who|underwent)\b/gim;

// Matches lowercase names after "for" in narrative text (not just at line start)
// E.g., "diag bronch for charlene king she has hilar adenopathy"
// Requires pronoun or clinical word after name to confirm patient context
const LOWERCASE_FOR_NAME_RE =
  /\bfor\s+([a-z]+\s+[a-z]+)\s+(?:she|he|they|who|to|we|and|patient|pt|with|has|had|is|was|the|a|for|due|because|secondary)\b/gi;

// Date patterns - various formats commonly found in medical notes
// Matches: "18Apr2022", "18-Apr-2022", "18 Apr 2022" (DDMMMYYYY variants)
const DATE_DDMMMYYYY_RE =
  /\b(\d{1,2}[-\s]?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-\s]?\d{2,4})\b/gi;

// Matches: "6/3/2016", "06/03/2016", "6-3-2016" (M/D/YYYY or MM/DD/YYYY)
const DATE_SLASH_RE =
  /\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b/g;

// Matches: "2024-01-15" (YYYY-MM-DD ISO format)
const DATE_ISO_RE =
  /\b(\d{4}[-\/]\d{1,2}[-\/]\d{1,2})\b/g;

// Matches: "DOB: 01/15/1960" or "Date of Birth: January 15, 1960"
const DOB_HEADER_RE =
  /\b(?:DOB|Date\s+of\s+Birth|Birth\s*Date|Birthdate)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{1,2}[-\s]?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-\s,]?\s*\d{1,2}[-,\s]+\d{2,4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}[-,\s]+\d{2,4})\b/gi;

// =============================================================================
// Transformers.js env
// =============================================================================

env.allowLocalModels = true;
env.allowRemoteModels = false;
env.localModelPath = MODEL_BASE_URL;

// Disable browser cache temporarily while iterating (you can re-enable later)
env.useBrowserCache = false;

if (env.backends?.onnx?.wasm) {
  env.backends.onnx.wasm.proxy = false;
  env.backends.onnx.wasm.numThreads = 1;
}

// =============================================================================
// Worker state
// =============================================================================

let classifier = null;
let classifierQuantized = null;
let classifierUnquantized = null;

let modelPromiseQuantized = null;
let modelPromiseUnquantized = null;

let protectedTerms = null;
let termsPromise = null;

let cancelled = false;
let debug = false;
let didTokenDebug = false;
let didLogitsDebug = false;

function log(...args) {
  if (debug) console.log(...args);
}

function post(type, payload = {}) {
  self.postMessage({ type, ...payload });
}

function toFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function toFiniteInt(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  return Number.isInteger(value) ? value : Math.trunc(value);
}

function normalizeLabel(entity) {
  if (!entity) return "PHI";
  const raw = String(entity).toUpperCase();
  return raw.replace(/^B-/, "").replace(/^I-/, "");
}

function normalizeRawOutput(raw) {
  if (Array.isArray(raw)) return raw;
  if (!raw || typeof raw !== "object") return [];
  if (Array.isArray(raw.data)) return raw.data;
  if (Array.isArray(raw.entities)) return raw.entities;
  return [];
}

// =============================================================================
// Protected terms (veto list) loader
// =============================================================================

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

// =============================================================================
// Model loading (quantized -> fallback unquantized)
// =============================================================================

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

// =============================================================================
// Regex injection (deterministic)
// =============================================================================

function runRegexDetectors(text) {
  const spans = [];

  // Reset global regex state
  PATIENT_HEADER_RE.lastIndex = 0;
  MRN_RE.lastIndex = 0;
  MRN_SPACED_RE.lastIndex = 0;
  INLINE_PATIENT_NAME_RE.lastIndex = 0;
  PROCEDURAL_NAME_RE.lastIndex = 0;
  PT_NAME_MRN_RE.lastIndex = 0;
  PT_STANDALONE_RE.lastIndex = 0;
  TITLE_NAME_RE.lastIndex = 0;
  NARRATIVE_FOR_NAME_RE.lastIndex = 0;
  PLACEHOLDER_NAME_RE.lastIndex = 0;
  PATIENT_SHORTHAND_RE.lastIndex = 0;
  SENTENCE_START_NAME_RE.lastIndex = 0;
  LINE_START_NAME_RE.lastIndex = 0;
  INFORMAL_NAME_HERE_RE.lastIndex = 0;
  UNDERSCORE_NAME_RE.lastIndex = 0;
  UNDERSCORE_ID_RE.lastIndex = 0;
  UNDERSCORE_DATE_RE.lastIndex = 0;
  TITLE_NAME_LOWERCASE_RE.lastIndex = 0;
  FIRST_NAME_CLINICAL_RE.lastIndex = 0;
  PROCEDURE_NOTE_NAME_RE.lastIndex = 0;
  STANDALONE_ALPHANUMERIC_ID_RE.lastIndex = 0;
  PT_LOWERCASE_NAME_RE.lastIndex = 0;
  LOWERCASE_NAME_DATE_RE.lastIndex = 0;
  LOWERCASE_NAME_AGE_GENDER_RE.lastIndex = 0;
  INFORMAL_NAME_HERE_TO_RE.lastIndex = 0;
  LOWERCASE_NAME_NOTE_RE.lastIndex = 0;
  NAME_START_CLINICAL_CONTEXT_RE.lastIndex = 0;
  LOWERCASE_FOR_NAME_RE.lastIndex = 0;
  DATE_DDMMMYYYY_RE.lastIndex = 0;
  DATE_SLASH_RE.lastIndex = 0;
  DATE_ISO_RE.lastIndex = 0;
  DOB_HEADER_RE.lastIndex = 0;

  // Helper: check if followed by provider credentials (to exclude provider names)
  function isFollowedByCredentials(matchEnd) {
    const after = text.slice(matchEnd, Math.min(text.length, matchEnd + 40));
    return /^,?\s*(?:MD|DO|RN|RT|PA|NP|CRNA|PhD|FCCP|DAABIP)\b/i.test(after);
  }

  // Helper: check if preceded by provider context
  function isPrecededByProviderContext(matchStart) {
    const before = text.slice(Math.max(0, matchStart - 60), matchStart).toLowerCase();
    return /(?:dr\.?|attending|proceduralist|assistant|fellow|resident|surgeon|operator|anesthesiologist|physician)\s*[:\-]?\s*$/i.test(before);
  }

  // 1) Patient header names
  for (const match of text.matchAll(PATIENT_HEADER_RE)) {
    const fullMatch = match[0];
    const nameGroup = match[1];
    const groupOffset = fullMatch.indexOf(nameGroup);
    if (groupOffset !== -1 && match.index != null) {
      spans.push({
        start: match.index + groupOffset,
        end: match.index + groupOffset + nameGroup.length,
        label: "PATIENT",
        score: 1.0,
        source: "regex_header",
      });
    }
  }

  // 1a) Placeholder/artifact names: "<PERSON>", "[Name]", "***NAME***"
  for (const match of text.matchAll(PLACEHOLDER_NAME_RE)) {
    const fullMatch = match[0];
    const placeholderGroup = match[1];
    const groupOffset = fullMatch.indexOf(placeholderGroup);
    if (groupOffset !== -1 && match.index != null) {
      spans.push({
        start: match.index + groupOffset,
        end: match.index + groupOffset + placeholderGroup.length,
        label: "PATIENT",
        score: 1.0,
        source: "regex_placeholder",
      });
    }
  }

  // 1b) Patient shorthand: "Patient 69F" (age/gender cluster as identifier)
  for (const match of text.matchAll(PATIENT_SHORTHAND_RE)) {
    const fullMatch = match[0];
    const shorthandGroup = match[1];
    const groupOffset = fullMatch.indexOf(shorthandGroup);
    if (groupOffset !== -1 && match.index != null) {
      spans.push({
        start: match.index + groupOffset,
        end: match.index + groupOffset + shorthandGroup.length,
        label: "PATIENT",
        score: 0.9,
        source: "regex_shorthand",
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

  // 2a) MRN with spaces: "A92 555" or "AB 123 456"
  for (const match of text.matchAll(MRN_SPACED_RE)) {
    const fullMatch = match[0];
    const idGroup = match[1];
    const groupOffset = fullMatch.indexOf(idGroup);
    if (groupOffset !== -1 && match.index != null) {
      spans.push({
        start: match.index + groupOffset,
        end: match.index + groupOffset + idGroup.length,
        label: "ID",
        score: 1.0,
        source: "regex_mrn_spaced",
      });
    }
  }

  // 3) Inline narrative names: "Emma Jones, a 64-year-old..."
  for (const match of text.matchAll(INLINE_PATIENT_NAME_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const matchEnd = match.index + nameGroup.length;
      // Skip if followed by credentials (likely provider, not patient)
      if (!isFollowedByCredentials(matchEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: matchEnd,
          label: "PATIENT",
          score: 0.95,
          source: "regex_inline_name",
        });
      }
    }
  }

  // 3a) Procedural verb + name: "performed on Robert Chen", "procedure for Jane Doe"
  for (const match of text.matchAll(PROCEDURAL_NAME_RE)) {
    const nameGroup = match[1];
    const fullMatch = match[0];
    if (nameGroup && match.index != null) {
      const groupOffset = fullMatch.indexOf(nameGroup);
      if (groupOffset !== -1) {
        const nameStart = match.index + groupOffset;
        const nameEnd = nameStart + nameGroup.length;
        // Skip if followed by credentials (likely provider)
        if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
          spans.push({
            start: nameStart,
            end: nameEnd,
            label: "PATIENT",
            score: 0.9,
            source: "regex_procedural_name",
          });
        }
      }
    }
  }

  // 4) "pt Name mrn 1234" pattern
  for (const match of text.matchAll(PT_NAME_MRN_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      // Find where the name starts within the match
      const fullMatch = match[0];
      const groupOffset = fullMatch.toLowerCase().indexOf(nameGroup.toLowerCase());
      if (groupOffset !== -1) {
        spans.push({
          start: match.index + groupOffset,
          end: match.index + groupOffset + nameGroup.length,
          label: "PATIENT",
          score: 0.95,
          source: "regex_pt_mrn",
        });
      }
    }
  }

  // 5) Title + Name: "Mr. Smith", "Mrs. Johnson"
  for (const match of text.matchAll(TITLE_NAME_RE)) {
    const nameGroup = match[1];
    const fullMatch = match[0];
    if (nameGroup && match.index != null) {
      const matchEnd = match.index + fullMatch.length;
      // Skip if followed by credentials (likely provider)
      if (!isFollowedByCredentials(matchEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: matchEnd,
          label: "PATIENT",
          score: 0.9,
          source: "regex_title_name",
        });
      }
    }
  }

  // 5a) PT standalone: "PT James Wilson" (without MRN pattern)
  for (const match of text.matchAll(PT_STANDALONE_RE)) {
    const nameGroup = match[1];
    const fullMatch = match[0];
    if (nameGroup && match.index != null) {
      const groupOffset = fullMatch.indexOf(nameGroup);
      if (groupOffset !== -1) {
        const nameStart = match.index + groupOffset;
        const nameEnd = nameStart + nameGroup.length;
        // Skip if followed by credentials (likely provider)
        if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
          spans.push({
            start: nameStart,
            end: nameEnd,
            label: "PATIENT",
            score: 0.9,
            source: "regex_pt_standalone",
          });
        }
      }
    }
  }

  // 5b) Narrative "for [Name]" pattern: "bronch for Logan Roy massive bleeding"
  for (const match of text.matchAll(NARRATIVE_FOR_NAME_RE)) {
    const nameGroup = match[1];
    const fullMatch = match[0];
    if (nameGroup && match.index != null) {
      const groupOffset = fullMatch.indexOf(nameGroup);
      if (groupOffset !== -1) {
        const nameStart = match.index + groupOffset;
        const nameEnd = nameStart + nameGroup.length;
        // Skip if followed by credentials (likely provider)
        if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
          spans.push({
            start: nameStart,
            end: nameEnd,
            label: "PATIENT",
            score: 0.85,
            source: "regex_narrative_for",
          });
        }
      }
    }
  }

  // 5c) Sentence-start name pattern: "Robert Smith has a LLL nodule..."
  for (const match of text.matchAll(SENTENCE_START_NAME_RE)) {
    const nameGroup = match[1];
    const fullMatch = match[0];
    if (nameGroup && match.index != null) {
      const groupOffset = fullMatch.indexOf(nameGroup);
      if (groupOffset !== -1) {
        const nameStart = match.index + groupOffset;
        const nameEnd = nameStart + nameGroup.length;
        // Skip if followed by credentials (likely provider)
        if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
          spans.push({
            start: nameStart,
            end: nameEnd,
            label: "PATIENT",
            score: 0.85,
            source: "regex_sentence_start",
          });
        }
      }
    }
  }

  // 5d) Line-start name pattern: "Kimberly Garcia. Ion Bronchoscopy." (name at very start of line)
  for (const match of text.matchAll(LINE_START_NAME_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const nameEnd = match.index + nameGroup.length;
      // Skip if followed by credentials (likely provider)
      if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: nameEnd,
          label: "PATIENT",
          score: 0.8,
          source: "regex_line_start",
        });
      }
    }
  }

  // 5e) Informal lowercase names: "jason phillips here for right lung lavage"
  for (const match of text.matchAll(INFORMAL_NAME_HERE_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const nameEnd = match.index + nameGroup.length;
      // Skip if followed by credentials (unlikely for lowercase but check anyway)
      if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: nameEnd,
          label: "PATIENT",
          score: 0.85,
          source: "regex_informal_here",
        });
      }
    }
  }

  // 5f) Underscore-wrapped template names: "___Lisa Anderson___"
  for (const match of text.matchAll(UNDERSCORE_NAME_RE)) {
    const nameGroup = match[1];
    const fullMatch = match[0];
    if (nameGroup && match.index != null) {
      // Redact the entire match including underscores
      spans.push({
        start: match.index,
        end: match.index + fullMatch.length,
        label: "PATIENT",
        score: 1.0,
        source: "regex_underscore_name",
      });
    }
  }

  // 5g) Underscore-wrapped IDs: "___BB-8472-K___"
  for (const match of text.matchAll(UNDERSCORE_ID_RE)) {
    const idGroup = match[1];
    const fullMatch = match[0];
    if (idGroup && match.index != null) {
      spans.push({
        start: match.index,
        end: match.index + fullMatch.length,
        label: "ID",
        score: 1.0,
        source: "regex_underscore_id",
      });
    }
  }

  // 5h) Underscore-wrapped dates: "___03/19/1961___"
  for (const match of text.matchAll(UNDERSCORE_DATE_RE)) {
    const dateGroup = match[1];
    const fullMatch = match[0];
    if (dateGroup && match.index != null) {
      spans.push({
        start: match.index,
        end: match.index + fullMatch.length,
        label: "DATE",
        score: 1.0,
        source: "regex_underscore_date",
      });
    }
  }

  // 5i) Lowercase honorific + name: "mrs lopez", "mr harris"
  for (const match of text.matchAll(TITLE_NAME_LOWERCASE_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const matchEnd = match.index + nameGroup.length;
      // Skip if followed by credentials (likely provider)
      if (!isFollowedByCredentials(matchEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: matchEnd,
          label: "PATIENT",
          score: 0.85,
          source: "regex_title_lowercase",
        });
      }
    }
  }

  // 5j) Standalone first name followed by clinical verb: "liam came in", "Frank underwent"
  for (const match of text.matchAll(FIRST_NAME_CLINICAL_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const nameEnd = match.index + nameGroup.length;
      // Skip if followed by credentials or preceded by provider context
      if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: nameEnd,
          label: "PATIENT",
          score: 0.75,
          source: "regex_first_name_clinical",
        });
      }
    }
  }

  // 5k) Procedure note header names: "Procedure note Justin Fowler 71M."
  for (const match of text.matchAll(PROCEDURE_NOTE_NAME_RE)) {
    const nameGroup = match[1];
    const fullMatch = match[0];
    if (nameGroup && match.index != null) {
      const groupOffset = fullMatch.toLowerCase().indexOf(nameGroup.toLowerCase());
      if (groupOffset !== -1) {
        const nameStart = match.index + groupOffset;
        const nameEnd = nameStart + nameGroup.length;
        // Skip if followed by credentials (likely provider)
        if (!isFollowedByCredentials(nameEnd)) {
          spans.push({
            start: nameStart,
            end: nameEnd,
            label: "PATIENT",
            score: 0.95,
            source: "regex_procedure_note",
          });
        }
      }
    }
  }

  // 5l) Standalone alphanumeric IDs: "LM-9283", "AB-1234-K"
  for (const match of text.matchAll(STANDALONE_ALPHANUMERIC_ID_RE)) {
    const idGroup = match[1];
    if (idGroup && match.index != null) {
      // Check context to confirm this looks like an identifier (not a device model)
      const ctx = text.slice(Math.max(0, match.index - 30), Math.min(text.length, match.index + idGroup.length + 30)).toLowerCase();
      // Only match if in patient/ID context, not device context
      if (/\b(?:mrn|patient|id|record|chart)\b/i.test(ctx) || !(/\b(?:model|scope|device|system|platform)\b/i.test(ctx))) {
        spans.push({
          start: match.index,
          end: match.index + idGroup.length,
          label: "ID",
          score: 0.8,
          source: "regex_alphanumeric_id",
        });
      }
    }
  }

  // 5m) "pt [Name]" patterns in informal notes: "pt Juan C R long term trach"
  for (const match of text.matchAll(PT_LOWERCASE_NAME_RE)) {
    const nameGroup = match[1];
    const fullMatch = match[0];
    if (nameGroup && match.index != null) {
      const groupOffset = fullMatch.toLowerCase().indexOf(nameGroup.toLowerCase());
      if (groupOffset !== -1) {
        const nameStart = match.index + groupOffset;
        const nameEnd = nameStart + nameGroup.length;
        if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
          spans.push({
            start: nameStart,
            end: nameEnd,
            label: "PATIENT",
            score: 0.9,
            source: "regex_pt_lowercase",
          });
        }
      }
    }
  }

  // 5n) Lowercase names followed by date: "oscar godsey 5/15/19"
  for (const match of text.matchAll(LOWERCASE_NAME_DATE_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const nameEnd = match.index + nameGroup.length;
      if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: nameEnd,
          label: "PATIENT",
          score: 0.85,
          source: "regex_lowercase_date",
        });
      }
    }
  }

  // 5o) Lowercase names followed by age/gender: "barbara kim 69 female"
  for (const match of text.matchAll(LOWERCASE_NAME_AGE_GENDER_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const nameEnd = match.index + nameGroup.length;
      if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: nameEnd,
          label: "PATIENT",
          score: 0.85,
          source: "regex_lowercase_age_gender",
        });
      }
    }
  }

  // 5p) Lowercase names followed by "here to": "gilbert barkley here to get his stents out"
  for (const match of text.matchAll(INFORMAL_NAME_HERE_TO_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const nameEnd = match.index + nameGroup.length;
      if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: nameEnd,
          label: "PATIENT",
          score: 0.85,
          source: "regex_informal_here_to",
        });
      }
    }
  }

  // 5q) Lowercase names followed by "note": "michael foster note hard to read"
  for (const match of text.matchAll(LOWERCASE_NAME_NOTE_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const nameEnd = match.index + nameGroup.length;
      if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: nameEnd,
          label: "PATIENT",
          score: 0.85,
          source: "regex_lowercase_note",
        });
      }
    }
  }

  // 5m) Name at start with clinical context: "Brenda Lewis transplant patient with stenosis"
  for (const match of text.matchAll(NAME_START_CLINICAL_CONTEXT_RE)) {
    const nameGroup = match[1];
    if (nameGroup && match.index != null) {
      const nameEnd = match.index + nameGroup.length;
      if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
        spans.push({
          start: match.index,
          end: nameEnd,
          label: "PATIENT",
          score: 0.85,
          source: "regex_name_start_clinical",
        });
      }
    }
  }

  // 5n) Lowercase name after "for": "diag bronch for charlene king she has hilar adenopathy"
  for (const match of text.matchAll(LOWERCASE_FOR_NAME_RE)) {
    const nameGroup = match[1];
    const fullMatch = match[0];
    if (nameGroup && match.index != null) {
      // Find where the name starts within the match (after "for ")
      const groupOffset = fullMatch.toLowerCase().indexOf(nameGroup.toLowerCase());
      if (groupOffset !== -1) {
        const nameStart = match.index + groupOffset;
        const nameEnd = nameStart + nameGroup.length;
        if (!isFollowedByCredentials(nameEnd) && !isPrecededByProviderContext(match.index)) {
          spans.push({
            start: nameStart,
            end: nameEnd,
            label: "PATIENT",
            score: 0.8,
            source: "regex_lowercase_for",
          });
        }
      }
    }
  }

  // 6) DOB header dates: "DOB: 01/15/1960"
  for (const match of text.matchAll(DOB_HEADER_RE)) {
    const dateGroup = match[1];
    const fullMatch = match[0];
    if (dateGroup && match.index != null) {
      const groupOffset = fullMatch.indexOf(dateGroup);
      if (groupOffset !== -1) {
        spans.push({
          start: match.index + groupOffset,
          end: match.index + groupOffset + dateGroup.length,
          label: "DATE",
          score: 1.0,
          source: "regex_dob",
        });
      }
    }
  }

  // 7) Date formats: "18Apr2022", "18-Apr-2022"
  for (const match of text.matchAll(DATE_DDMMMYYYY_RE)) {
    const dateGroup = match[1];
    if (dateGroup && match.index != null) {
      spans.push({
        start: match.index,
        end: match.index + dateGroup.length,
        label: "DATE",
        score: 0.95,
        source: "regex_date_ddmmm",
      });
    }
  }

  // 8) Slash/dash dates: "6/3/2016", "06-03-2016"
  for (const match of text.matchAll(DATE_SLASH_RE)) {
    const dateGroup = match[1];
    if (dateGroup && match.index != null) {
      spans.push({
        start: match.index,
        end: match.index + dateGroup.length,
        label: "DATE",
        score: 0.9,
        source: "regex_date_slash",
      });
    }
  }

  // 9) ISO dates: "2024-01-15" (YYYY-MM-DD)
  for (const match of text.matchAll(DATE_ISO_RE)) {
    const dateGroup = match[1];
    if (dateGroup && match.index != null) {
      spans.push({
        start: match.index,
        end: match.index + dateGroup.length,
        label: "DATE",
        score: 0.95,
        source: "regex_date_iso",
      });
    }
  }

  return spans;
}

// =============================================================================
// NER: robust offsets
// =============================================================================

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
  const raw = await classifier(chunk, {
    aggregation_strategy: "simple",
    ignore_labels: ["O"],
  });

  const rawList = normalizeRawOutput(raw);
  log("[PHI] raw spans (simple) count:", rawList.length);

  const spans = [];
  let offsets = null;
  let offsetsTried = false;
  let searchCursor = 0;

  for (const ent of rawList) {
    let start =
      toFiniteNumber(ent?.start) ??
      toFiniteNumber(ent?.start_offset) ??
      toFiniteNumber(ent?.begin);

    let end =
      toFiniteNumber(ent?.end) ??
      toFiniteNumber(ent?.end_offset) ??
      toFiniteNumber(ent?.finish);

    const score =
      toFiniteNumber(ent?.score) ??
      toFiniteNumber(ent?.confidence) ??
      toFiniteNumber(ent?.probability) ??
      0.0;

    // If offsets are missing/bad, try to recover.
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
        tokenIndex !== null ||
        startTokenIndex !== null ||
        endTokenIndex !== null ||
        Boolean(getEntityText(ent));

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

      // Last-resort: find token text in the chunk (case-insensitive) with cursor.
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
    if (end - start < 1) continue;
    if (typeof score === "number" && score < aiThreshold) continue;

    searchCursor = Math.max(searchCursor, end);

    spans.push({
      start,
      end,
      label: normalizeLabel(ent?.entity_group || ent?.entity || ent?.label),
      score: typeof score === "number" ? score : 0.0,
      source: "ner",
    });
  }

  // If model returns nothing, optionally dump token debug once per run.
  if (spans.length === 0 && debug && !didTokenDebug) {
    didTokenDebug = true;
    await debugTokenPredictions(chunk);
  }

  return spans;
}

// =============================================================================
// Span utilities: dedupe, merge, word-boundary expansion
// =============================================================================

function dedupeSpans(spans) {
  const seen = new Set();
  const out = [];
  for (const s of spans) {
    const k = `${s.start}:${s.end}:${s.label}:${s.source || ""}`;
    if (!seen.has(k)) {
      seen.add(k);
      out.push(s);
    }
  }
  return out;
}

function isRegexSpan(s) {
  return typeof s?.source === "string" && s.source.startsWith("regex_");
}

function overlapsOrAdjacent(aStart, aEnd, bStart, bEnd) {
  // include adjacency (aEnd === bStart)
  return aStart <= bEnd && bStart <= aEnd;
}

function mergeOverlapsBestOf(spans) {
  const sorted = [...spans].sort((a, b) => {
    if (a.start !== b.start) return a.start - b.start;
    // Prefer regex then higher score
    const aR = isRegexSpan(a) ? 1 : 0;
    const bR = isRegexSpan(b) ? 1 : 0;
    if (aR !== bR) return bR - aR;
    return (b.score ?? 0) - (a.score ?? 0);
  });

  const out = [];
  for (const s of sorted) {
    const last = out[out.length - 1];
    if (!last || !overlapsOrAdjacent(last.start, last.end, s.start, s.end)) {
      out.push({ ...s });
      continue;
    }

    // Overlapping or adjacent
    const overlapLen = Math.max(0, Math.min(last.end, s.end) - Math.max(last.start, s.start));
    const lastIsRegex = isRegexSpan(last);
    const sIsRegex = isRegexSpan(s);

    // If either is regex and they overlap, prefer regex to avoid double-highlights and prefix-capture.
    if (overlapLen > 0 && (lastIsRegex || sIsRegex)) {
      const keep = lastIsRegex ? last : s;
      out[out.length - 1] = { ...keep };
      continue;
    }

    // If same label, union them (also merges adjacent token pieces nicely)
    if (last.label === s.label) {
      out[out.length - 1] = {
        ...last,
        start: Math.min(last.start, s.start),
        end: Math.max(last.end, s.end),
        score: Math.max(last.score ?? 0, s.score ?? 0),
        source: last.source || s.source,
      };
      continue;
    }

    // Different labels: only replace if overlap is huge; otherwise keep both.
    const lastLen = Math.max(1, last.end - last.start);
    const sLen = Math.max(1, s.end - s.start);
    const overlapRatio = overlapLen / Math.min(lastLen, sLen);

    if (overlapRatio >= 0.8) {
      if ((s.score ?? 0) > (last.score ?? 0)) out[out.length - 1] = { ...s };
    } else {
      out.push({ ...s });
    }
  }

  return out;
}

/**
 * Expand spans to full word boundaries to prevent partial-word redactions.
 * - Fixes cases like "id[REDACTED]" when the model only tagged part of a token.
 */
function expandToWordBoundaries(spans, fullText) {
  function isWordCharAt(i) {
    if (i < 0 || i >= fullText.length) return false;
    const ch = fullText[i];
    if (/[A-Za-z0-9]/.test(ch)) return true;

    // Treat apostrophe/hyphen as word-char only when adjacent to alnum
    if (ch === "'" || ch === "’" || ch === "-") {
      const left = i > 0 ? fullText[i - 1] : "";
      const right = i + 1 < fullText.length ? fullText[i + 1] : "";
      return /[A-Za-z0-9]/.test(left) || /[A-Za-z0-9]/.test(right);
    }
    return false;
  }

  return spans.map((span) => {
    let { start, end } = span;

    while (start > 0 && isWordCharAt(start - 1)) start--;
    while (end < fullText.length && isWordCharAt(end)) end++;

    if (start !== span.start || end !== span.end) {
      return { ...span, start, end, text: fullText.slice(start, end) };
    }
    return span;
  });
}

/**
 * Extend GEO spans to include common multi-word city prefixes.
 * Fixes partial redactions like "San [REDACTED]" → "[REDACTED]" for "San Francisco".
 */
const CITY_PREFIXES = new Set([
  "san", "los", "las", "new", "fort", "saint", "st", "santa", "el", "la",
  "port", "mount", "mt", "north", "south", "east", "west", "upper", "lower",
  "lake", "palm", "long", "grand", "great", "little", "old", "big"
]);

function extendGeoSpans(spans, fullText) {
  return spans.map((span) => {
    // Only extend GEO-labeled spans
    const label = String(span.label || "").toUpperCase().replace(/^[BI]-/, "");
    if (label !== "GEO") return span;

    let { start } = span;

    // Look for city prefix word before the span
    const beforeWindow = fullText.slice(Math.max(0, start - 20), start);
    const prefixMatch = beforeWindow.match(/\b([A-Za-z]+)\s+$/);

    if (prefixMatch) {
      const prefix = prefixMatch[1].toLowerCase();
      if (CITY_PREFIXES.has(prefix)) {
        // Extend start to include the prefix
        const prefixStart = start - prefixMatch[0].length;
        return {
          ...span,
          start: prefixStart,
          end: span.end,
          text: fullText.slice(prefixStart, span.end)
        };
      }
    }

    return span;
  });
}

// =============================================================================
// Debug helpers (optional)
// =============================================================================

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
        ignore_labels: [],
        return_offsets_mapping: true,
        topk: 1,
      });
    } catch (err) {
      log("[PHI] token preds debug (with offsets) failed; retrying without offsets:", err);
      tokenRaw = await classifier(chunk, {
        aggregation_strategy: "none",
        ignore_labels: [],
        topk: 1,
      });
    }

    const tokenList = normalizeRawOutput(tokenRaw);
    log("[PHI] token preds count:", tokenList.length);
    if (tokenList.length > 0) {
      log("[PHI] token preds preview:", tokenList.slice(0, 10).map(formatTokenPreview));
      return;
    }
  } catch (err) {
    log("[PHI] token preds debug failed:", err);
  }

  if (didLogitsDebug) return;
  didLogitsDebug = true;

  try {
    const inputs = await classifier.tokenizer(chunk, { return_tensors: "np" });
    const out = await classifier.model(inputs);
    const logits = out?.logits;
    log("[PHI] logits dims:", logits?.dims);
    const data = logits?.data;
    log("[PHI] logits sample:", data ? Array.from(data.slice(0, 20)) : null);
  } catch (err) {
    log("[PHI] logits debug failed:", err);
  }
}

// =============================================================================
// Worker message loop
// =============================================================================

self.onmessage = async (e) => {
  const msg = e.data;
  if (!msg || typeof msg.type !== "string") return;

  if (msg.type === "cancel") {
    cancelled = true;
    return;
  }

  if (msg.type === "init") {
    cancelled = false;
    didTokenDebug = false;
    didLogitsDebug = false;

    const config = msg.config && typeof msg.config === "object" ? msg.config : {};
    debug = Boolean(msg.debug ?? config.debug);

    try {
      await loadProtectedTerms();
      await loadModel(config);
      post("ready");
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    }
    return;
  }

  if (msg.type === "start") {
    cancelled = false;
    didTokenDebug = false;
    didLogitsDebug = false;

    try {
      await loadProtectedTerms();

      const text = String(msg.text || "");
      const config = msg.config && typeof msg.config === "object" ? msg.config : {};
      debug = Boolean(config.debug);

      await loadModel(config);

      const aiThreshold = typeof config.aiThreshold === "number" ? config.aiThreshold : 0.45;

      const allSpans = [];
      const windowCount = Math.max(1, Math.ceil(Math.max(0, text.length - OVERLAP) / STEP));
      let windowIndex = 0;

      post("progress", { stage: "Running detection (local model)…", windowIndex, windowCount });

      for (let start = 0; start < text.length; start += STEP) {
        const end = Math.min(text.length, start + WINDOW);
        const chunk = text.slice(start, end);

        // Avoid an extra tiny tail window (often low signal / higher false positives)
        if (start > 0 && chunk.length < 50) break;

        windowIndex += 1;

        // 1) ML spans (robust offsets)
        const nerSpans = await runNER(chunk, aiThreshold);

        // 2) Regex injection spans (header guarantees)
        const regexSpans = runRegexDetectors(chunk);

        // 3) Combine (still chunk-relative)
        const combined = dedupeSpans([...nerSpans, ...regexSpans]);

        // 4) Convert to absolute offsets
        for (const s of combined) {
          allSpans.push({
            ...s,
            start: s.start + start,
            end: s.end + start,
          });
        }

        post("progress", { windowIndex, windowCount });
        if (cancelled) break;
      }

      // 5) Merge/dedupe across windows
      let merged = mergeOverlapsBestOf(allSpans);

      // 6) Expand to word boundaries (fixes partial-word redactions)
      merged = expandToWordBoundaries(merged, text);

      // 7) Extend GEO spans to include city prefixes (fixes "San [REDACTED]" → "[REDACTED]")
      merged = extendGeoSpans(merged, text);

      // 8) Re-merge after expansion
      merged = mergeOverlapsBestOf(merged);

      // 9) Apply veto (protected allow-list)
      merged = applyVeto(merged, text, protectedTerms, { debug });

      post("done", { detections: merged });
    } catch (err) {
      post("error", { message: String(err?.message || err) });
    }
  }
};
