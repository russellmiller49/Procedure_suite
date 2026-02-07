import type { EvidenceSpan, RegistryRow, ValueType } from "../types";
import { joinJsonPointer } from "./jsonPointer";

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function valueTypeOf(value: unknown): ValueType {
  if (value === null || value === undefined) return "null";
  if (Array.isArray(value)) return "array";
  if (typeof value === "boolean") return "boolean";
  if (typeof value === "number") return "number";
  if (typeof value === "string") return "string";
  if (typeof value === "object") return "object";
  return "unknown";
}

const ACRONYMS = new Map<string, string>([
  ["ebus", "EBUS"],
  ["tbna", "TBNA"],
  ["bal", "BAL"],
  ["ct", "CT"],
  ["icu", "ICU"],
  ["pdl1", "PD-L1"],
]);

function titleCaseToken(token: string): string {
  const raw = token.trim();
  if (!raw) return "";
  const lower = raw.toLowerCase();
  const mapped = ACRONYMS.get(lower);
  if (mapped) return mapped;
  if (/^\d+$/.test(raw)) return raw;
  if (/^[A-Z0-9]+$/.test(raw)) return raw;
  return raw.charAt(0).toUpperCase() + raw.slice(1);
}

function formatKeyLabel(key: string): string {
  const cleaned = String(key || "").trim();
  if (!cleaned) return "(empty)";
  const tokens = cleaned
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .split(/\s+/)
    .filter(Boolean);
  return tokens.map(titleCaseToken).join(" ");
}

function clampText(text: string, maxLen: number): string {
  const t = String(text ?? "");
  if (t.length <= maxLen) return t;
  return `${t.slice(0, maxLen - 1)}…`;
}

function formatValueDisplay(value: unknown, valueType: ValueType): string {
  switch (valueType) {
    case "null":
      return "—";
    case "boolean":
      return value ? "Yes" : "No";
    case "number":
      return Number.isFinite(value as number) ? String(value) : "—";
    case "string":
      return String(value || "");
    case "array":
      return Array.isArray(value) ? `Array (${value.length})` : "Array";
    case "object":
      return isRecord(value) ? `Object (${Object.keys(value).length})` : "Object";
    default:
      return String(value ?? "—");
  }
}

function arrayElementLabel(value: unknown, index: number): string {
  const vt = valueTypeOf(value);
  if (vt === "string") {
    const s = String(value || "").trim();
    return s ? clampText(s, 60) : `[${index}]`;
  }
  if (vt === "number") return String(value);
  if (vt === "boolean") return value ? "true" : "false";

  if (vt === "object" && isRecord(value)) {
    const preferredKeys = [
      "station",
      "name",
      "id",
      "code",
      "site",
      "lobe",
      "location",
      "target",
      "specimen",
    ];
    for (const k of preferredKeys) {
      const v = value[k];
      const vType = valueTypeOf(v);
      if (vType === "string" || vType === "number") {
        const s = String(v);
        if (s.trim()) return clampText(s.trim(), 60);
      }
    }
  }

  return `[${index}]`;
}

type AddRowArgs = {
  jsonPointer: string;
  pathSegments: string[];
  parentId: string | null;
  valueType: ValueType;
  isGroup: boolean;
  extractedValueRaw: unknown;
  extractedValueDisplay: string;
  evidence: EvidenceSpan[];
};

function makeRow(args: AddRowArgs): RegistryRow {
  const depth = Math.max(args.pathSegments.length - 1, 0);
  const fieldLabel = args.pathSegments[args.pathSegments.length - 1] ?? "—";
  return {
    id: args.jsonPointer,
    jsonPointer: args.jsonPointer,
    pathSegments: args.pathSegments,
    depth,
    fieldLabel,
    extractedValueRaw: args.extractedValueRaw,
    extractedValueDisplay: args.extractedValueDisplay,
    editedValueRaw: null,
    editedValueDisplay: null,
    valueType: args.valueType,
    evidence: args.evidence,
    isGroup: args.isGroup,
    parentId: args.parentId,
  };
}

type WalkContext = {
  evidenceIndex: Map<string, EvidenceSpan[]>;
  rows: RegistryRow[];
  visited: WeakSet<object>;
};

function walkValue(
  ctx: WalkContext,
  value: unknown,
  jsonPointer: string,
  pathSegments: string[],
  parentId: string | null,
): void {
  const vt = valueTypeOf(value);
  const isGroup = vt === "array" || vt === "object";

  const evidence = ctx.evidenceIndex.get(jsonPointer) ?? [];
  const extractedValueDisplay = formatValueDisplay(value, vt);
  const extractedValueRaw = isGroup ? null : value;

  ctx.rows.push(
    makeRow({
      jsonPointer,
      pathSegments,
      parentId,
      valueType: vt,
      isGroup,
      extractedValueRaw,
      extractedValueDisplay,
      evidence,
    }),
  );

  if (!isGroup) return;
  if (value && typeof value === "object") {
    if (ctx.visited.has(value as object)) return;
    ctx.visited.add(value as object);
  }

  if (vt === "array" && Array.isArray(value)) {
    value.forEach((item, index) => {
      const childPointer = joinJsonPointer(jsonPointer, String(index));
      const label = arrayElementLabel(item, index);
      walkValue(ctx, item, childPointer, [...pathSegments, label], jsonPointer);
    });
    return;
  }

  if (vt === "object" && isRecord(value)) {
    for (const key of Object.keys(value)) {
      const childPointer = joinJsonPointer(jsonPointer, key);
      const label = formatKeyLabel(key);
      walkValue(ctx, value[key], childPointer, [...pathSegments, label], jsonPointer);
    }
  }
}

export function flattenRegistryToRows(
  registry: unknown,
  evidenceIndex: Map<string, EvidenceSpan[]>,
): RegistryRow[] {
  if (!isRecord(registry)) return [];

  const ctx: WalkContext = { evidenceIndex, rows: [], visited: new WeakSet<object>() };
  const skipTopLevelKeys = new Set(["evidence", "billing"]);

  for (const key of Object.keys(registry)) {
    if (skipTopLevelKeys.has(key)) continue;
    const pointer = joinJsonPointer("/registry", key);
    const label = formatKeyLabel(key);
    walkValue(ctx, registry[key], pointer, [label], null);
  }

  return ctx.rows;
}
