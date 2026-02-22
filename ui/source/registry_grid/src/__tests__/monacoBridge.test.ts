import { afterEach, describe, expect, it, vi } from "vitest";

import { highlightSpan } from "../monaco/monacoBridge";

type EditorOverrides = Partial<{
  revealRangeInCenterIfOutsideViewport: (range: unknown) => void;
  revealRangeInCenter: (range: unknown) => void;
  revealRange: (range: unknown) => void;
  setSelection: (range: unknown) => void;
}>;

function buildEditor(overrides: EditorOverrides = {}) {
  return {
    getModel: () => ({
      getValue: () => "0123456789",
      getPositionAt: (offset: number) => ({ lineNumber: 1, column: Number(offset) + 1 }),
    }),
    deltaDecorations: () => [],
    focus: () => undefined,
    ...overrides,
  };
}

afterEach(() => {
  delete (globalThis as typeof globalThis & { __ensureEvidenceContextVisible?: unknown }).__ensureEvidenceContextVisible;
});

describe("highlightSpan", () => {
  it("invokes the host visibility hook and reveals the span", () => {
    const hook = vi.fn();
    (globalThis as typeof globalThis & { __ensureEvidenceContextVisible?: unknown }).__ensureEvidenceContextVisible = hook;

    const setSelection = vi.fn();
    const reveal = vi.fn();
    const editor = buildEditor({
      setSelection,
      revealRangeInCenterIfOutsideViewport: reveal,
    });

    highlightSpan(editor, 2, 5, { label: "Evidence" });

    expect(hook).toHaveBeenCalledWith({ start: 2, end: 5 });
    expect(setSelection).toHaveBeenCalledTimes(1);
    expect(setSelection).toHaveBeenCalledWith({
      startLineNumber: 1,
      startColumn: 3,
      endLineNumber: 1,
      endColumn: 6,
    });
    expect(reveal.mock.calls.length).toBeGreaterThan(0);
  });

  it("falls back to revealRangeInCenter when center-if-outside is unavailable", () => {
    const revealCenter = vi.fn();
    const editor = buildEditor({
      revealRangeInCenter: revealCenter,
    });

    highlightSpan(editor, 1, 4);

    expect(revealCenter.mock.calls.length).toBeGreaterThan(0);
  });

  it("ignores invalid spans", () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    const setSelection = vi.fn();
    const hook = vi.fn();
    (globalThis as typeof globalThis & { __ensureEvidenceContextVisible?: unknown }).__ensureEvidenceContextVisible = hook;
    const editor = buildEditor({ setSelection });

    highlightSpan(editor, "bad-start", 10);

    expect(hook).not.toHaveBeenCalled();
    expect(setSelection).not.toHaveBeenCalled();
    warnSpy.mockRestore();
  });
});
