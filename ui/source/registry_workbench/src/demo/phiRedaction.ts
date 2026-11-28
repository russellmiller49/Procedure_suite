/** In-browser de-identification for the demo page: token replacement and scan bookkeeping.
 *
 * The detection itself runs in the existing redactor worker (served from /ui/). This file
 * owns what the page must get right on its own: one fixed placeholder, overlap merging, and
 * knowing whether the text on screen has had a *completed* scan reviewed and applied.
 */

export const PLACEHOLDER = "[REDACTED]";

export type Detection = {
  id: string;
  start: number;
  end: number;
  label: string;
  score: number | null;
  source: string;
};

export const WORKER_CONFIG = {
  aiThreshold: 0.5,
  debug: false,
  // Quantized ONNX can collapse to all-"O" under WASM; keep the full model until validated.
  forceUnquantized: true,
  mergeMode: "union",
  // Clinician names are treated as identifiers and can be redacted.
  protectProviders: false,
};

/** Sort and merge overlapping or touching spans, dropping anything outside the text. */
export function mergeSpans(spans: [number, number][], length: number): [number, number][] {
  const valid = spans
    .filter(([s, e]) => Number.isFinite(s) && Number.isFinite(e) && s >= 0 && e <= length && e > s)
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const out: [number, number][] = [];
  for (const [s, e] of valid) {
    const last = out[out.length - 1];
    if (last && s <= last[1]) last[1] = Math.max(last[1], e);
    else out.push([s, e]);
  }
  return out;
}

/** Replace every kept detection with the placeholder. Excluded detections are left as they are. */
export function applyRedactions(text: string, detections: Detection[], excluded: ReadonlySet<string>): string {
  const spans = mergeSpans(
    detections.filter(d => !excluded.has(d.id)).map(d => [d.start, d.end] as [number, number]),
    text.length,
  );
  let out = text;
  for (let i = spans.length - 1; i >= 0; i--) out = out.slice(0, spans[i][0]) + PLACEHOLDER + out.slice(spans[i][1]);
  return out;
}

/** A detection the reader added by selecting text the scan missed. */
export function manualDetection(start: number, end: number): Detection {
  return {id: `manual:${start}-${end}`, start, end, label: "MANUAL", score: null, source: "manual"};
}

/** Replace one span with the placeholder (a manual redaction after the scan was applied). */
export function redactSpan(text: string, span: [number, number]): string {
  const [start, end] = mergeSpans([span], text.length)[0] ?? [0, 0];
  return end > start ? text.slice(0, start) + PLACEHOLDER + text.slice(end) : text;
}

/** Character offsets of the current selection inside ``root``, or null when there is none. */
export function selectionSpan(root: HTMLElement | null): [number, number] | null {
  const selection = typeof window === "undefined" ? null : window.getSelection();
  if (!root || !selection || selection.rangeCount === 0 || selection.isCollapsed) return null;
  const range = selection.getRangeAt(0);
  if (!root.contains(range.startContainer) || !root.contains(range.endContainer)) return null;
  const before = document.createRange();
  before.selectNodeContents(root);
  before.setEnd(range.startContainer, range.startOffset);
  const start = before.toString().length;
  const end = start + range.toString().length;
  return end > start ? [start, end] : null;
}

/** Normalise what the worker reports into detections with stable ids. */
export function readDetections(raw: unknown): Detection[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .filter(d => Number.isFinite(d?.start) && Number.isFinite(d?.end) && d.end > d.start)
    .map((d, i) => ({
      id: typeof d.id === "string" ? d.id : `d${i}:${d.start}-${d.end}`,
      start: Number(d.start),
      end: Number(d.end),
      label: String(d.label || "PHI"),
      score: typeof d.score === "number" ? d.score : null,
      source: typeof d.source === "string" ? d.source : "auto",
    }));
}

/**
 * Tracks which scan results may be trusted.
 *
 * The worker posts an ordinary "done" after a cancelled scan, carrying only the windows it
 * finished. So a result counts only if it belongs to the latest scan, that scan was not
 * cancelled, and the text has not changed since the scan began.
 */
export class ScanGate {
  private revision = 0;
  private scan = 0;
  private scanRevision = -1;
  private cancelled = new Set<number>();
  private reviewed = -1;
  private applied = -1;

  /** Call whenever the note text changes (edit, paste, new sample, applied redaction). */
  textChanged(): number {
    this.revision += 1;
    return this.revision;
  }

  begin(): number {
    this.scan += 1;
    this.scanRevision = this.revision;
    return this.scan;
  }

  cancel(): void {
    if (this.scan > 0) this.cancelled.add(this.scan);
  }

  /** True when a "done" for ``scanId`` is a complete result for the text on screen. */
  accept(scanId: number): boolean {
    const ok = scanId === this.scan && !this.cancelled.has(scanId) && this.scanRevision === this.revision;
    if (ok) this.reviewed = this.revision;
    return ok;
  }

  get scanComplete(): boolean {
    return this.reviewed === this.revision;
  }

  /** Mark redactions applied; the redacted text is the new revision and is the one cleared. */
  markApplied(): void {
    if (!this.scanComplete) throw new Error("apply requires a completed scan of the current text");
    this.revision += 1;
    this.applied = this.revision;
  }

  /** Use a reviewed redacted text as-is (the reviewed redaction of a bundled sample). */
  markReviewedText(): void {
    this.revision += 1;
    this.applied = this.revision;
  }

  /** The reader redacted more text by hand after applying; the new text stays cleared. */
  markManualEdit(): void {
    if (!this.readyToExtract) throw new Error("a manual redaction needs applied redactions first");
    this.revision += 1;
    this.applied = this.revision;
  }

  get readyToExtract(): boolean {
    return this.applied === this.revision;
  }
}

export type RedactorEvent =
  | {type: "status"; message: string}
  | {type: "ready"}
  | {type: "progress"; message: string}
  | {type: "done"; scanId: number; detections: Detection[]}
  | {type: "error"; message: string};

function forceLegacy(): boolean {
  if (new URLSearchParams(location.search).get("legacy_phi") === "1") return true;
  const ua = navigator.userAgent || "";
  const ios = /iPad|iPhone|iPod/i.test(ua) || (ua.includes("Mac") && "ontouchend" in document);
  const safari = /Safari/i.test(ua) && !/Chrome|CriOS|FxiOS|EdgiOS|OPR/i.test(ua);
  return ios && safari;
}

/** Drives the existing redactor worker. Loaded lazily: the model is a large download. */
export class Redactor {
  private worker: Worker | null = null;
  private legacy = false;
  private triedLegacy = false;
  private ready = false;
  private activeScan = 0;
  private pending: {scanId: number; text: string} | null = null;

  constructor(private emit: (event: RedactorEvent) => void) {}

  get usingLegacy(): boolean {
    return this.legacy;
  }

  private start(legacy: boolean): void {
    this.worker?.terminate();
    this.ready = false;
    this.legacy = legacy;
    let worker: Worker | null = null;
    if (!legacy) {
      try {
        worker = new Worker(`/ui/redactor.worker.js?v=${Date.now()}`, {type: "module"});
      } catch {
        this.triedLegacy = true;
        this.legacy = true;
      }
    }
    if (!worker) worker = new Worker(`/ui/redactor.worker.legacy.js?v=${Date.now()}`);
    this.worker = worker;
    worker.addEventListener("error", ev => {
      if (!this.legacy && !this.triedLegacy) {
        this.triedLegacy = true;
        this.emit({type: "status", message: "Falling back to the compatibility redactor…"});
        this.start(true);
        return;
      }
      this.ready = false;
      this.emit({type: "error", message: ev.message || "The local redactor failed to load."});
    });
    worker.onmessage = e => {
      const msg = e.data;
      if (!msg || typeof msg.type !== "string") return;
      if (msg.type === "ready") {
        this.ready = true;
        this.emit({type: "ready"});
        if (this.pending) {
          const next = this.pending;
          this.pending = null;
          this.post(next.scanId, next.text);
        }
      } else if (msg.type === "progress") {
        const window = msg.windowCount ? `Scanning ${msg.windowIndex ?? "?"} of ${msg.windowCount}` : "";
        this.emit({type: "progress", message: String(msg.stage || window)});
      } else if (msg.type === "done") {
        this.emit({type: "done", scanId: this.activeScan, detections: readDetections(msg.detections)});
      } else if (msg.type === "error") {
        this.emit({type: "error", message: String(msg.message || "unknown error")});
      }
    };
    this.emit({type: "status", message: "Loading the local de-identification model (large first download)…"});
    worker.postMessage({type: "init", debug: false, config: WORKER_CONFIG});
  }

  private post(scanId: number, text: string): void {
    this.activeScan = scanId;
    this.worker!.postMessage({type: "start", text, config: WORKER_CONFIG});
  }

  /** Scan ``text``; the "done" event carries ``scanId`` so the page can gate it. */
  scan(scanId: number, text: string): void {
    if (!this.worker) {
      this.pending = {scanId, text};
      this.start(forceLegacy());
      return;
    }
    if (!this.ready) {
      this.pending = {scanId, text};
      return;
    }
    this.post(scanId, text);
  }

  cancel(): void {
    this.pending = null;
    this.worker?.postMessage({type: "cancel"});
  }

  dispose(): void {
    this.worker?.terminate();
    this.worker = null;
  }
}
