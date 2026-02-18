const DEFAULT_LINE_Y_TOLERANCE = 2.5;
const DEFAULT_SEGMENT_GAP_MIN = 14;
const DEFAULT_REGION_MARGIN = 3;

export function clamp01(value) {
  if (!Number.isFinite(value)) return 0;
  if (value < 0) return 0;
  if (value > 1) return 1;
  return value;
}

export function normalizeRect(rect) {
  const rawX = Number(rect?.x) || 0;
  const rawY = Number(rect?.y) || 0;
  const rawWidth = Number(rect?.width) || 0;
  const rawHeight = Number(rect?.height) || 0;

  const x = rawWidth >= 0 ? rawX : rawX + rawWidth;
  const y = rawHeight >= 0 ? rawY : rawY + rawHeight;
  const width = Math.abs(rawWidth);
  const height = Math.abs(rawHeight);

  return { x, y, width, height };
}

export function rectArea(rect) {
  const normalized = normalizeRect(rect);
  return Math.max(0, normalized.width) * Math.max(0, normalized.height);
}

export function intersectionArea(a, b) {
  const ra = normalizeRect(a);
  const rb = normalizeRect(b);

  const left = Math.max(ra.x, rb.x);
  const top = Math.max(ra.y, rb.y);
  const right = Math.min(ra.x + ra.width, rb.x + rb.width);
  const bottom = Math.min(ra.y + ra.height, rb.y + rb.height);

  const width = Math.max(0, right - left);
  const height = Math.max(0, bottom - top);
  return width * height;
}

export function expandRect(rect, margin = DEFAULT_REGION_MARGIN) {
  const normalized = normalizeRect(rect);
  const m = Math.max(0, Number(margin) || 0);
  return {
    x: normalized.x - m,
    y: normalized.y - m,
    width: normalized.width + m * 2,
    height: normalized.height + m * 2,
  };
}

function rectsTouchOrOverlap(a, b, gap = 0) {
  const ra = normalizeRect(a);
  const rb = normalizeRect(b);
  const g = Math.max(0, Number(gap) || 0);

  return !(
    ra.x + ra.width + g < rb.x ||
    rb.x + rb.width + g < ra.x ||
    ra.y + ra.height + g < rb.y ||
    rb.y + rb.height + g < ra.y
  );
}

function unionRect(a, b) {
  const ra = normalizeRect(a);
  const rb = normalizeRect(b);

  const x1 = Math.min(ra.x, rb.x);
  const y1 = Math.min(ra.y, rb.y);
  const x2 = Math.max(ra.x + ra.width, rb.x + rb.width);
  const y2 = Math.max(ra.y + ra.height, rb.y + rb.height);

  return { x: x1, y: y1, width: x2 - x1, height: y2 - y1 };
}

function horizontalOverlapRatio(a, b) {
  const ra = normalizeRect(a);
  const rb = normalizeRect(b);

  const overlap = Math.max(0, Math.min(ra.x + ra.width, rb.x + rb.width) - Math.max(ra.x, rb.x));
  const minWidth = Math.max(1, Math.min(ra.width, rb.width));
  return overlap / minWidth;
}

function verticalGap(a, b) {
  const ra = normalizeRect(a);
  const rb = normalizeRect(b);
  if (ra.y + ra.height < rb.y) return rb.y - (ra.y + ra.height);
  if (rb.y + rb.height < ra.y) return ra.y - (rb.y + rb.height);
  return 0;
}

function rectCenterX(rect) {
  const normalized = normalizeRect(rect);
  return normalized.x + normalized.width / 2;
}

function lineSort(a, b, yTolerance = DEFAULT_LINE_Y_TOLERANCE) {
  const dy = b.y - a.y;
  if (Math.abs(dy) > yTolerance) return dy;
  return a.x - b.x;
}

function normalizeToken(value) {
  if (typeof value !== "string") return "";
  return value.replace(/\s+/g, " ").trim();
}

function startsWithPunctuation(token) {
  return /^[,.;:!?)]/.test(token);
}

function appendTokenWithGap(buffer, prevItem, item, token) {
  let output = buffer;

  if (prevItem) {
    const prevRight = prevItem.x + prevItem.width;
    const gap = item.x - prevRight;
    const avgCharWidth = item.width > 0 ? item.width / Math.max(1, token.length) : 1;
    const likelyWordBoundary = gap > Math.max(2, avgCharWidth * 0.5);
    if (likelyWordBoundary && !startsWithPunctuation(token) && !output.endsWith(" ")) {
      output += " ";
    }
  }

  const start = output.length;
  output += token;
  const end = output.length;

  return { text: output, start, end };
}

function itemToRect(item) {
  const width = Math.max(0.1, Number(item?.width) || 0);
  const height = Math.max(0.1, Math.abs(Number(item?.height) || 0));
  const x = Number(item?.x) || 0;
  const baselineY = Number(item?.y) || 0;
  return normalizeRect({ x, y: baselineY - height, width, height });
}

function shouldBreakSegment(previousItem, item, token) {
  if (!previousItem) return false;
  const gap = item.x - (previousItem.x + previousItem.width);
  const avgCharWidth = item.width > 0 ? item.width / Math.max(1, token.length) : 1;
  return gap > Math.max(DEFAULT_SEGMENT_GAP_MIN, avgCharWidth * 2.5);
}

function buildLineText(items) {
  let text = "";
  let prev = null;

  for (const item of items) {
    const token = normalizeToken(item.str);
    if (!token) continue;
    const next = appendTokenWithGap(text, prev, item, token);
    text = next.text;
    prev = item;
  }

  return text;
}

export function mergeRegions(regions, opts = {}) {
  const mergeGap = Number.isFinite(opts.mergeGap) ? Math.max(0, opts.mergeGap) : 2;
  const normalized = (Array.isArray(regions) ? regions : [])
    .map(normalizeRect)
    .filter((rect) => rect.width > 0 && rect.height > 0)
    .sort((a, b) => {
      if (a.y !== b.y) return a.y - b.y;
      return a.x - b.x;
    });

  if (!normalized.length) return [];

  const merged = [];

  for (const region of normalized) {
    let mergedInto = false;

    for (const current of merged) {
      if (rectsTouchOrOverlap(current, region, mergeGap)) {
        const union = unionRect(current, region);
        current.x = union.x;
        current.y = union.y;
        current.width = union.width;
        current.height = union.height;
        mergedInto = true;
        break;
      }
    }

    if (!mergedInto) {
      merged.push({ ...region });
    }
  }

  return merged;
}

export function buildLayoutBlocks(items, opts = {}) {
  const yTolerance = Number.isFinite(opts.lineYTolerance) ? Math.max(0.5, opts.lineYTolerance) : DEFAULT_LINE_Y_TOLERANCE;
  const normalizedItems = (Array.isArray(items) ? items : [])
    .map((item, index) => ({
      ...item,
      itemIndex: Number.isFinite(item?.itemIndex) ? item.itemIndex : index,
      width: Math.max(0.1, Number(item?.width) || 0),
      height: Math.max(0.1, Math.abs(Number(item?.height) || 0)),
      x: Number(item?.x) || 0,
      y: Number(item?.y) || 0,
    }))
    .sort((a, b) => lineSort(a, b, yTolerance));

  const lines = [];
  for (const item of normalizedItems) {
    const last = lines[lines.length - 1];
    if (!last || Math.abs(last.y - item.y) > yTolerance) {
      lines.push({ y: item.y, items: [item] });
    } else {
      last.items.push(item);
    }
  }

  const segments = [];
  let segmentId = 1;

  for (const line of lines) {
    line.items.sort((a, b) => a.x - b.x);
    let current = [];

    for (const item of line.items) {
      const token = normalizeToken(item.str);
      if (!token) continue;

      if (current.length && shouldBreakSegment(current[current.length - 1], item, token)) {
        segments.push(buildSegment(current, segmentId++));
        current = [];
      }
      current.push(item);
    }

    if (current.length) {
      segments.push(buildSegment(current, segmentId++));
    }
  }

  segments.sort((a, b) => {
    const dy = b.baselineY - a.baselineY;
    if (Math.abs(dy) > yTolerance) return dy;
    return a.bbox.x - b.bbox.x;
  });

  const blocks = [];
  for (const segment of segments) {
    let best = null;
    let bestScore = Number.POSITIVE_INFINITY;

    for (const block of blocks) {
      const vGap = verticalGap(block.bbox, segment.bbox);
      const xOverlap = horizontalOverlapRatio(block.bbox, segment.bbox);
      const xDistance = Math.abs(rectCenterX(block.bbox) - rectCenterX(segment.bbox));
      const allowAttach = vGap <= 14 && (xOverlap >= 0.15 || xDistance <= 38);
      if (!allowAttach) continue;

      const score = vGap + (1 - Math.min(1, xOverlap)) * 4 + xDistance * 0.02;
      if (score < bestScore) {
        bestScore = score;
        best = block;
      }
    }

    if (!best) {
      blocks.push({
        id: `block-${blocks.length + 1}`,
        bbox: { ...segment.bbox },
        lines: [segment],
        itemIndices: [...segment.itemIndices],
      });
    } else {
      best.lines.push(segment);
      best.itemIndices.push(...segment.itemIndices);
      best.bbox = unionRect(best.bbox, segment.bbox);
    }
  }

  for (const block of blocks) {
    block.lines.sort((a, b) => {
      const dy = b.baselineY - a.baselineY;
      if (Math.abs(dy) > yTolerance) return dy;
      return a.bbox.x - b.bbox.x;
    });
    block.text = block.lines.map((line) => line.text).filter(Boolean).join("\n");
    block.lineCount = block.lines.length;
  }

  blocks.sort((a, b) => {
    const dy = b.bbox.y - a.bbox.y;
    if (Math.abs(dy) > 8) return dy;
    return a.bbox.x - b.bbox.x;
  });

  return blocks;
}

function buildSegment(items, id) {
  const itemIndices = [];
  let bbox = null;

  for (const item of items) {
    const rect = itemToRect(item);
    bbox = bbox ? unionRect(bbox, rect) : rect;
    itemIndices.push(item.itemIndex);
  }

  return {
    id: `segment-${id}`,
    items: [...items],
    itemIndices,
    bbox: bbox || { x: 0, y: 0, width: 0, height: 0 },
    baselineY: items[0]?.y || 0,
    text: buildLineText(items),
  };
}

export function buildTextRegionsFromBlocks(blocks) {
  const out = [];
  for (const block of Array.isArray(blocks) ? blocks : []) {
    for (const line of block.lines || []) {
      out.push(normalizeRect(line.bbox));
    }
  }
  return mergeRegions(out, { mergeGap: 0 });
}

export function computeOverlapRatio(textRegions, imageRegions, opts = {}) {
  const margin = Number.isFinite(opts.margin) ? Math.max(0, opts.margin) : DEFAULT_REGION_MARGIN;
  const textRects = Array.isArray(textRegions) ? textRegions.map(normalizeRect) : [];
  const imageRects = mergeRegions(
    (Array.isArray(imageRegions) ? imageRegions : []).map((region) => expandRect(region, margin)),
    { mergeGap: 0 },
  );

  let totalTextArea = 0;
  let totalOverlapArea = 0;

  for (const textRect of textRects) {
    const area = rectArea(textRect);
    if (area <= 0) continue;
    totalTextArea += area;

    let overlap = 0;
    for (const imageRect of imageRects) {
      overlap += intersectionArea(textRect, imageRect);
    }
    totalOverlapArea += Math.min(area, overlap);
  }

  return totalTextArea > 0 ? clamp01(totalOverlapArea / totalTextArea) : 0;
}

export function markContaminatedItems(items, imageRegions, opts = {}) {
  const margin = Number.isFinite(opts.margin) ? Math.max(0, opts.margin) : DEFAULT_REGION_MARGIN;
  const minOverlapRatio = Number.isFinite(opts.minOverlapRatio) ? clamp01(opts.minOverlapRatio) : 0.12;

  const expandedImageRegions = mergeRegions(
    (Array.isArray(imageRegions) ? imageRegions : []).map((region) => expandRect(region, margin)),
    { mergeGap: 2 },
  );

  const contaminatedByItemIndex = new Set();
  let contaminatedItemCount = 0;
  let shortContaminatedCount = 0;

  for (const item of Array.isArray(items) ? items : []) {
    const itemIndex = Number.isFinite(item?.itemIndex) ? item.itemIndex : null;
    if (itemIndex === null) continue;

    const rect = itemToRect(item);
    const rectSize = rectArea(rect);
    if (rectSize <= 0) continue;

    let overlapArea = 0;
    for (const imageRegion of expandedImageRegions) {
      overlapArea += intersectionArea(rect, imageRegion);
    }
    const overlapRatio = clamp01(overlapArea / rectSize);
    if (overlapRatio < minOverlapRatio) continue;

    contaminatedByItemIndex.add(itemIndex);
    contaminatedItemCount += 1;

    const token = normalizeToken(item.str);
    const shortSymbolic = token.length <= 3 && !/[A-Za-z]/.test(token);
    if (shortSymbolic) shortContaminatedCount += 1;
  }

  const itemCount = Array.isArray(items) ? items.length : 0;
  return {
    contaminatedByItemIndex,
    contaminatedItemCount,
    shortContaminatedCount,
    contaminatedRatio: itemCount ? contaminatedItemCount / itemCount : 0,
    shortContaminatedRatio: itemCount ? shortContaminatedCount / itemCount : 0,
    expandedImageRegions,
  };
}

function shouldExcludeContaminatedToken(token, contaminated) {
  if (!contaminated) return false;
  if (!token) return true;
  if (token.length <= 2) return true;
  if (/^[\d]+$/.test(token) && token.length <= 4) return true;
  if (/^[^A-Za-z0-9]+$/.test(token)) return true;
  return false;
}

function mergeSpanList(spans) {
  if (!spans.length) return [];
  const sorted = [...spans].sort((a, b) => {
    if (a.start !== b.start) return a.start - b.start;
    return a.end - b.end;
  });

  const out = [];
  for (const span of sorted) {
    const last = out[out.length - 1];
    if (!last || span.start > last.end + 1) {
      out.push({ ...span });
      continue;
    }
    last.end = Math.max(last.end, span.end);
  }
  return out;
}

export function assembleTextFromBlocks(blocks, contamination, opts = {}) {
  const dropContaminatedNumericTokens = opts.dropContaminatedNumericTokens !== false;
  const contaminatedByItemIndex = contamination?.contaminatedByItemIndex || new Set();

  let text = "";
  let rawText = "";
  const contaminatedSpans = [];
  let excludedTokenCount = 0;
  let keptContaminatedCount = 0;
  let totalTokenCount = 0;

  const sortedBlocks = [...(Array.isArray(blocks) ? blocks : [])].sort((a, b) => {
    const dy = b.bbox.y - a.bbox.y;
    if (Math.abs(dy) > 8) return dy;
    return a.bbox.x - b.bbox.x;
  });

  for (const block of sortedBlocks) {
    const lines = [...(block.lines || [])].sort((a, b) => {
      const dy = b.baselineY - a.baselineY;
      if (Math.abs(dy) > DEFAULT_LINE_Y_TOLERANCE) return dy;
      return a.bbox.x - b.bbox.x;
    });

    const blockFilteredLines = [];
    const blockRawLines = [];

    for (const line of lines) {
      const lineItems = [...(line.items || [])].sort((a, b) => a.x - b.x);
      let filteredLine = "";
      let rawLine = "";
      let filteredPrev = null;
      let rawPrev = null;
      const lineContaminatedSpans = [];

      for (const item of lineItems) {
        const token = normalizeToken(item.str);
        if (!token) continue;
        totalTokenCount += 1;

        const rawNext = appendTokenWithGap(rawLine, rawPrev, item, token);
        rawLine = rawNext.text;
        rawPrev = item;

        const contaminated = contaminatedByItemIndex.has(item.itemIndex);
        const exclude = dropContaminatedNumericTokens && shouldExcludeContaminatedToken(token, contaminated);
        if (exclude) {
          excludedTokenCount += 1;
          continue;
        }

        const filteredNext = appendTokenWithGap(filteredLine, filteredPrev, item, token);
        filteredLine = filteredNext.text;
        filteredPrev = item;

        if (contaminated) {
          keptContaminatedCount += 1;
          lineContaminatedSpans.push({
            start: filteredNext.start,
            end: filteredNext.end,
          });
        }
      }

      if (filteredLine) {
        blockFilteredLines.push({
          text: filteredLine,
          contaminatedSpans: lineContaminatedSpans,
        });
      }
      if (rawLine) {
        blockRawLines.push(rawLine);
      }
    }

    if (!blockFilteredLines.length && !blockRawLines.length) continue;

    if (text && blockFilteredLines.length) text += "\n\n";
    if (rawText && blockRawLines.length) rawText += "\n\n";

    for (let lineIndex = 0; lineIndex < blockFilteredLines.length; lineIndex += 1) {
      if (lineIndex > 0) text += "\n";
      const line = blockFilteredLines[lineIndex];
      const lineStart = text.length;
      text += line.text;

      for (const span of line.contaminatedSpans) {
        contaminatedSpans.push({
          start: lineStart + span.start,
          end: lineStart + span.end,
          kind: "image_overlap",
        });
      }
    }

    for (let lineIndex = 0; lineIndex < blockRawLines.length; lineIndex += 1) {
      if (lineIndex > 0) rawText += "\n";
      rawText += blockRawLines[lineIndex];
    }
  }

  return {
    text,
    rawText: rawText || text,
    contaminatedSpans: mergeSpanList(contaminatedSpans),
    excludedTokenCount,
    keptContaminatedCount,
    totalTokenCount,
    excludedTokenRatio: totalTokenCount ? excludedTokenCount / totalTokenCount : 0,
  };
}

export function scoreContamination({
  overlapRatio = 0,
  contaminatedRatio = 0,
  shortContaminatedRatio = 0,
  excludedTokenRatio = 0,
}) {
  const score =
    clamp01(overlapRatio) * 0.55 +
    clamp01(contaminatedRatio) * 0.2 +
    clamp01(shortContaminatedRatio) * 0.15 +
    clamp01(excludedTokenRatio) * 0.1;
  return clamp01(score);
}

export function computeTextStats(items, text) {
  const sourceText = typeof text === "string"
    ? text
    : (Array.isArray(items) ? items.map((item) => item?.str || "").join("") : "");

  const chars = [...sourceText];
  let nonPrintableCount = 0;
  for (const ch of chars) {
    if (/[\x00-\x08\x0E-\x1F\x7F-\x9F]/.test(ch)) {
      nonPrintableCount += 1;
    }
  }

  let singleCharItems = 0;
  const itemList = Array.isArray(items) ? items : [];
  for (const item of itemList) {
    if (normalizeToken(item?.str).length === 1) {
      singleCharItems += 1;
    }
  }

  const charCount = chars.length;
  const itemCount = itemList.length;
  return {
    charCount,
    itemCount,
    nonPrintableRatio: charCount ? nonPrintableCount / charCount : 0,
    singleCharItemRatio: itemCount ? singleCharItems / itemCount : 0,
  };
}

export function estimateCompletenessConfidence(stats, opts = {}) {
  const safeStats = stats || {};
  const excludedTokenRatio = Number.isFinite(opts.excludedTokenRatio)
    ? clamp01(opts.excludedTokenRatio)
    : clamp01(safeStats.excludedTokenRatio || 0);

  let confidence = 1;
  const charCount = Number(safeStats.charCount) || 0;
  const singleCharItemRatio = Number(safeStats.singleCharItemRatio) || 0;
  const nonPrintableRatio = Number(safeStats.nonPrintableRatio) || 0;
  const imageOpCount = Number(safeStats.imageOpCount) || 0;
  const layoutBlockCount = Number(safeStats.layoutBlockCount) || 0;
  const overlapRatio = Number(safeStats.overlapRatio) || 0;
  const contaminationScore = Number(safeStats.contaminationScore) || 0;

  if (charCount < 80) confidence -= 0.35;
  if (singleCharItemRatio >= 0.55) confidence -= 0.17;
  if (nonPrintableRatio >= 0.08) confidence -= 0.12;
  if (imageOpCount >= 5 && charCount <= 1800) confidence -= 0.2;
  if (layoutBlockCount <= 1 && imageOpCount >= 4) confidence -= 0.12;

  confidence -= Math.min(0.32, clamp01(overlapRatio) * 0.6);
  confidence -= Math.min(0.28, clamp01(contaminationScore) * 0.55);
  confidence -= Math.min(0.2, excludedTokenRatio * 0.6);

  return clamp01(confidence);
}
