type MonacoEditorLike = {
  getModel?: () => { getValue?: () => string; getPositionAt?: (offset: number) => { lineNumber: number; column: number } } | null;
  deltaDecorations?: (oldDecorations: string[], newDecorations: unknown[]) => string[];
  revealRangeInCenter?: (range: unknown) => void;
  setSelection?: (range: unknown) => void;
  focus?: () => void;
};

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
    ed.revealRangeInCenter?.(range);
    ed.focus?.();
  } catch (err) {
    console.warn("RegistryGrid: failed to reveal/select evidence span (ignored).", err);
  }
}
