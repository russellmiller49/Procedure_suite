import type { EvidenceSpan } from "../types";
import { escapeJsonPointerSegment } from "../flatten/jsonPointer";

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function normalizeEvidenceKeyToPointer(key: string): string | null {
  const trimmed = String(key || "").trim();
  if (!trimmed) return null;

  if (trimmed.startsWith("/")) {
    // Some backends emit full pointers ("/registry/..."), others emit pointers
    // relative to the registry root ("/clinical_context/...").
    if (trimmed === "/registry" || trimmed.startsWith("/registry/")) return trimmed;
    return `/registry${trimmed}`;
  }

  const denylist = new Set(["code_evidence", "codes", "cpt_codes", "suggestions"]);

  let path = trimmed;
  if (path.startsWith("registry.")) path = path.slice("registry.".length);
  if (!path.includes(".") && denylist.has(path)) return null;

  const segments = path.split(".").filter(Boolean);
  if (segments.length === 0) return null;

  const encoded = segments.map((s) => escapeJsonPointerSegment(String(s)));
  return `/registry/${encoded.join("/")}`;
}

function normalizeEvidenceSpan(span: unknown): EvidenceSpan | null {
  if (!isRecord(span)) return null;

  const source = typeof span.source === "string" ? span.source : "registry_span";
  const text = typeof span.text === "string" ? span.text : typeof span.quote === "string" ? span.quote : "";

  let start: number | null = null;
  let end: number | null = null;

  const rawSpan = span.span;
  if (Array.isArray(rawSpan) && rawSpan.length >= 2 && Number.isFinite(rawSpan[0]) && Number.isFinite(rawSpan[1])) {
    start = Number(rawSpan[0]);
    end = Number(rawSpan[1]);
  } else {
    const s = span.start ?? span.start_char;
    const e = span.end ?? span.end_char;
    if (Number.isFinite(s)) start = Number(s);
    if (Number.isFinite(e)) end = Number(e);
  }

  if (start === null || end === null) return null;

  const confidence =
    span.confidence === null || span.confidence === undefined || Number.isFinite(span.confidence)
      ? (span.confidence as number | null | undefined)
      : undefined;

  return { source, text, span: [start, end], confidence };
}

function addEvidenceObject(index: Map<string, EvidenceSpan[]>, evObj: unknown): void {
  if (!isRecord(evObj)) return;
  for (const [key, value] of Object.entries(evObj)) {
    const pointer = normalizeEvidenceKeyToPointer(key);
    if (!pointer) continue;
    if (!Array.isArray(value)) continue;
    for (const item of value) {
      const normalized = normalizeEvidenceSpan(item);
      if (!normalized) continue;
      const existing = index.get(pointer);
      if (existing) existing.push(normalized);
      else index.set(pointer, [normalized]);
    }
  }
}

function addEvidenceItems(index: Map<string, EvidenceSpan[]>, items: unknown): void {
  if (!Array.isArray(items)) return;
  for (const item of items) {
    if (!isRecord(item)) continue;
    const path = typeof item.path === "string" ? item.path : typeof item.field === "string" ? item.field : null;
    if (!path) continue;
    const pointer = normalizeEvidenceKeyToPointer(path);
    if (!pointer) continue;
    const normalized = normalizeEvidenceSpan(item);
    if (!normalized) continue;
    const existing = index.get(pointer);
    if (existing) existing.push(normalized);
    else index.set(pointer, [normalized]);
  }
}

export function buildEvidenceIndex(processResponse: unknown): Map<string, EvidenceSpan[]> {
  const index = new Map<string, EvidenceSpan[]>();
  if (!isRecord(processResponse)) return index;

  const resp = processResponse as Record<string, unknown>;
  const registry = isRecord(resp.registry) ? (resp.registry as Record<string, unknown>) : null;

  // Path 0: V3 unified response contract (top-level evidence dict).
  addEvidenceObject(index, resp.evidence);

  // Path 0b: some payloads may nest evidence inside registry.
  addEvidenceObject(index, registry?.evidence);

  // Path 1: explain object with evidence_by_path.
  const explain = isRecord(resp.explain) ? (resp.explain as Record<string, unknown>) : null;
  addEvidenceObject(index, explain?.evidence_by_path);
  addEvidenceItems(index, explain?.items);

  // Path 2: registry.explain object with evidence_by_path.
  const registryExplain = registry && isRecord(registry.explain) ? (registry.explain as Record<string, unknown>) : null;
  addEvidenceObject(index, registryExplain?.evidence_by_path);
  addEvidenceItems(index, registryExplain?.items);

  // Path 3: alternate naming (explanation).
  const explanation = isRecord(resp.explanation) ? (resp.explanation as Record<string, unknown>) : null;
  addEvidenceObject(index, explanation?.evidence_by_path);
  addEvidenceItems(index, explanation?.items);

  const registryExplanation =
    registry && isRecord(registry.explanation) ? (registry.explanation as Record<string, unknown>) : null;
  addEvidenceObject(index, registryExplanation?.evidence_by_path);
  addEvidenceItems(index, registryExplanation?.items);

  return index;
}
