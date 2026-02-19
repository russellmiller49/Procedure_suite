import { intersectionArea, normalizeRect, rectArea } from "./layoutAnalysis.js";
import { OCR_BOILERPLATE_PATTERNS } from "./ocrMetrics.js";

function safeText(value) {
  return typeof value === "string" ? value : "";
}

function normalizeBBox(bbox) {
  const normalized = normalizeRect(bbox || { x: 0, y: 0, width: 0, height: 0 });
  if (!Number.isFinite(normalized.x) || !Number.isFinite(normalized.y)) {
    return { x: 0, y: 0, width: 0, height: 0 };
  }
  if (!Number.isFinite(normalized.width) || !Number.isFinite(normalized.height)) {
    return { x: normalized.x, y: normalized.y, width: 0, height: 0 };
  }
  return normalized;
}

function normalizeLine(line) {
  const text = safeText(line?.text).replace(/\s+/g, " ").trim();
  return {
    text,
    confidence: Number.isFinite(line?.confidence)
      ? Number(line.confidence)
      : Number.isFinite(line?.conf)
        ? Number(line.conf)
        : null,
    bbox: normalizeBBox(line?.bbox),
    words: Array.isArray(line?.words) ? line.words : [],
    pageIndex: Number.isFinite(line?.pageIndex) ? Number(line.pageIndex) : 0,
  };
}

function normalizeLineKey(text) {
  return safeText(text)
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function isBoilerplateLine(text) {
  if (!text) return false;
  return OCR_BOILERPLATE_PATTERNS.some((pattern) => pattern.test(text));
}

function isLikelyCaptionLine(text) {
  if (!text || text.length > 58) return false;
  if (/[:;%]/.test(text)) return false;
  const tokens = text.split(/\s+/).filter(Boolean);
  if (tokens.length < 2 || tokens.length > 7) return false;
  const anatomyTokenPattern = /^(left|right|upper|lower|middle|lobe|lobar|mainstem|entrance|segment|bronchus|airway|carina|trachea|lingula|LUL|LLL|RUL|RML|RLL)$/i;
  const anatomyCount = tokens.filter((token) => anatomyTokenPattern.test(token)).length;
  return anatomyCount >= 2 && anatomyCount / tokens.length >= 0.5;
}

function maxOverlapRatio(lineBBox, regions) {
  const lineRect = normalizeBBox(lineBBox);
  const lineArea = Math.max(1, rectArea(lineRect));
  let maxRatio = 0;

  for (const region of Array.isArray(regions) ? regions : []) {
    const overlap = intersectionArea(lineRect, normalizeBBox(region));
    if (overlap <= 0) continue;
    const ratio = overlap / lineArea;
    if (ratio > maxRatio) maxRatio = ratio;
  }

  return maxRatio;
}

export function dedupeConsecutiveLines(lines) {
  const out = [];
  let prevKey = "";

  for (const rawLine of Array.isArray(lines) ? lines : []) {
    const line = normalizeLine(rawLine);
    if (!line.text) continue;
    const key = normalizeLineKey(line.text);
    if (key && key === prevKey) continue;
    prevKey = key;
    out.push(line);
  }

  return out;
}

/**
 * Filter OCR lines using detected figure regions and confidence gates.
 *
 * @param {Array<{text:string,confidence?:number,conf?:number,bbox?:{x:number,y:number,width:number,height:number},words?:Array,pageIndex?:number}>} lines
 * @param {Array<{x:number,y:number,width:number,height:number}>} figureRegions
 * @param {{overlapThreshold?:number,shortLowConfThreshold?:number,dropCaptions?:boolean,dropBoilerplate?:boolean}} [opts]
 * @returns {{lines:Array,dropped:Array<{line:object,reason:string,overlapRatio?:number}>}}
 */
export function filterOcrLinesDetailed(lines, figureRegions, opts = {}) {
  const overlapThreshold = Number.isFinite(opts.overlapThreshold) ? Number(opts.overlapThreshold) : 0.35;
  const shortLowConfThreshold = Number.isFinite(opts.shortLowConfThreshold)
    ? Number(opts.shortLowConfThreshold)
    : 30;
  const disableFigureOverlap = opts.disableFigureOverlap === true;
  const dropCaptions = opts.dropCaptions !== false;
  const dropBoilerplate = opts.dropBoilerplate !== false;

  const normalizedRegions = (Array.isArray(figureRegions) ? figureRegions : []).map(normalizeBBox);
  const dropped = [];
  const kept = [];

  for (const rawLine of dedupeConsecutiveLines(lines)) {
    const line = normalizeLine(rawLine);
    if (!line.text) continue;

    if (dropBoilerplate && isBoilerplateLine(line.text)) {
      dropped.push({ line, reason: "boilerplate" });
      continue;
    }

    if (dropCaptions && isLikelyCaptionLine(line.text)) {
      dropped.push({ line, reason: "caption" });
      continue;
    }

    if (!disableFigureOverlap) {
      const overlapRatio = maxOverlapRatio(line.bbox, normalizedRegions);
      if (overlapRatio > overlapThreshold) {
        dropped.push({ line, reason: "figure_overlap", overlapRatio });
        continue;
      }
    }

    const textLen = line.text.length;
    if (Number.isFinite(line.confidence) && line.confidence < shortLowConfThreshold && textLen < 6) {
      dropped.push({ line, reason: "low_conf_short" });
      continue;
    }

    kept.push(line);
  }

  return {
    lines: dedupeConsecutiveLines(kept),
    dropped,
  };
}

export function filterOcrLines(lines, figureRegions, opts = {}) {
  return filterOcrLinesDetailed(lines, figureRegions, opts).lines;
}

export function composeOcrPageText(lines) {
  return dedupeConsecutiveLines(lines)
    .map((line) => line.text)
    .filter(Boolean)
    .join("\n");
}
