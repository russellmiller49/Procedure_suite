type MonacoEditorLike = {
  getModel?: () => { getValue?: () => string; getPositionAt?: (offset: number) => { lineNumber: number; column: number } } | null;
  deltaDecorations?: (oldDecorations: string[], newDecorations: unknown[]) => string[];
  revealRangeInCenterIfOutsideViewport?: (range: unknown) => void;
  revealRangeInCenter?: (range: unknown) => void;
  revealRange?: (range: unknown) => void;
  setSelection?: (range: unknown) => void;
  focus?: () => void;
};

type EvidenceContextHook = ((payload?: { start?: number; end?: number }) => void) | undefined;

let activeDecorationIds: string[] = [];

function asInt(value: unknown): number | null {
  if (value === null || value === undefined) return null;
  const n = Number(value);
  if (!Number.isFinite(n)) return null;
  return Math.trunc(n);
}

function clamp(n: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, n));
}

function ensureEvidenceContextVisible(start: number, end: number): void {
  const hook = (globalThis as typeof globalThis & { __ensureEvidenceContextVisible?: EvidenceContextHook })
    .__ensureEvidenceContextVisible;
  if (typeof hook === "function") {
    try {
      hook({ start, end });
      return;
    } catch (err) {
      console.warn("RegistryGrid: host evidence visibility hook failed (ignored).", err);
    }
  }

  if (typeof document === "undefined") return;
  const el = (document.getElementById("editor") || document.querySelector(".editorPane")) as HTMLElement | null;
  if (!el || typeof el.scrollIntoView !== "function") return;
  try {
    const reduceMotion = globalThis.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
    el.scrollIntoView({
      block: document.body?.classList.contains("ps-review-split") ? "nearest" : "start",
      inline: "nearest",
      behavior: reduceMotion ? "auto" : "smooth",
    });
  } catch {
    // Ignore scroll failures and continue with Monaco-only navigation.
  }
}

function revealRangeInEditor(ed: MonacoEditorLike, range: unknown): void {
  const reveal = () => {
    if (typeof ed.revealRangeInCenterIfOutsideViewport === "function") {
      ed.revealRangeInCenterIfOutsideViewport(range);
      return;
    }
    if (typeof ed.revealRangeInCenter === "function") {
      ed.revealRangeInCenter(range);
      return;
    }
    if (typeof ed.revealRange === "function") ed.revealRange(range);
  };

  reveal();
  if (typeof globalThis.requestAnimationFrame === "function") {
    globalThis.requestAnimationFrame(() => reveal());
  }
}

export function clearHighlight(editor: unknown): void {
  const ed = editor as MonacoEditorLike | null | undefined;
  if (!ed || typeof ed.deltaDecorations !== "function") return;
  if (activeDecorationIds.length === 0) return;
  try {
    activeDecorationIds = ed.deltaDecorations(activeDecorationIds, []);
  } catch {
    activeDecorationIds = [];
  }
}

export function highlightSpan(
  editor: unknown,
  start: unknown,
  end: unknown,
  opts?: { label?: string },
): void {
  const ed = editor as MonacoEditorLike | null | undefined;
  if (!ed || typeof ed.getModel !== "function") {
    console.warn("RegistryGrid: Monaco editor unavailable; cannot highlight evidence.");
    return;
  }

  const model = ed.getModel?.() ?? null;
  const getValue = model?.getValue;
  const getPositionAt = model?.getPositionAt;
  if (!model || typeof getValue !== "function" || typeof getPositionAt !== "function") {
    console.warn("RegistryGrid: Monaco model unavailable; cannot highlight evidence.");
    return;
  }

  const text = String(getValue.call(model) ?? "");
  const len = text.length;

  const s0 = asInt(start);
  const e0 = asInt(end);
  if (s0 === null || e0 === null) {
    console.warn("RegistryGrid: invalid evidence span (non-numeric).", { start, end });
    return;
  }
  if (e0 <= s0) {
    console.warn("RegistryGrid: invalid evidence span (end <= start).", { start: s0, end: e0 });
    return;
  }

  const s = clamp(s0, 0, len);
  const e = clamp(e0, 0, len);
  if (e <= s) {
    console.warn("RegistryGrid: invalid evidence span after clamping.", { start: s0, end: e0, clamped: [s, e], len });
    return;
  }

  const startPos = getPositionAt.call(model, s);
  const endPos = getPositionAt.call(model, e);
  if (!startPos || !endPos) {
    console.warn("RegistryGrid: failed to compute Monaco positions for span.", { start: s, end: e });
    return;
  }

  const range = {
    startLineNumber: startPos.lineNumber,
    startColumn: startPos.column,
    endLineNumber: endPos.lineNumber,
    endColumn: endPos.column,
  };

  ensureEvidenceContextVisible(s, e);
  clearHighlight(ed);

  if (typeof ed.deltaDecorations === "function") {
    const label = opts?.label || "Evidence";
    try {
      activeDecorationIds = ed.deltaDecorations(activeDecorationIds, [
        {
          range,
          options: {
            inlineClassName: "ps-monaco-evidence-highlight",
            hoverMessage: { value: label },
          },
        },
      ]);
    } catch (err) {
      console.warn("RegistryGrid: failed to set Monaco decoration (ignored).", err);
      activeDecorationIds = [];
    }
  }

  try {
    ed.setSelection?.(range);
    revealRangeInEditor(ed, range);
    ed.focus?.();
  } catch (err) {
    console.warn("RegistryGrid: failed to reveal/select evidence span (ignored).", err);
  }
}
