import type { JSONPatchOp } from "./types";

export type PatchStoreState = {
  patchOps: JSONPatchOp[];
  undoStack: JSONPatchOp[][];
  redoStack: JSONPatchOp[][];
};

export const EMPTY_PATCH_STORE_STATE: PatchStoreState = { patchOps: [], undoStack: [], redoStack: [] };

const MAX_HISTORY = 80;

function isPatchOpForPath(op: JSONPatchOp, path: string): boolean {
  return Boolean(op && typeof op === "object" && op.path === path);
}

export function shallowEqualPrimitive(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  // Treat NaN as equal to NaN for numeric edits.
  if (typeof a === "number" && typeof b === "number" && Number.isNaN(a) && Number.isNaN(b)) return true;
  return false;
}

function pushUndo(undoStack: JSONPatchOp[][], snapshot: JSONPatchOp[]): JSONPatchOp[][] {
  const next = undoStack.concat([snapshot]);
  return next.length > MAX_HISTORY ? next.slice(next.length - MAX_HISTORY) : next;
}

function upsertReplaceOp(ops: JSONPatchOp[], path: string, value: unknown): JSONPatchOp[] {
  const next: JSONPatchOp[] = [];
  for (const op of ops) {
    if (isPatchOpForPath(op, path)) continue;
    next.push(op);
  }
  next.push({ op: "replace", path, value });
  return next;
}

function removeOp(ops: JSONPatchOp[], path: string): JSONPatchOp[] {
  return ops.filter((op) => !isPatchOpForPath(op, path));
}

export function buildEditedValueByPath(patchOps: JSONPatchOp[]): Map<string, unknown> {
  const map = new Map<string, unknown>();
  for (const op of patchOps) {
    if (!op || typeof op !== "object") continue;
    if (op.op === "replace" || op.op === "add") map.set(op.path, op.value);
    else if (op.op === "remove") map.set(op.path, undefined);
  }
  return map;
}

export function patchStoreSetEditedValue(
  state: PatchStoreState,
  path: string,
  extractedValue: unknown,
  nextValue: unknown,
): PatchStoreState {
  const p = String(path || "").trim();
  if (!p) return state;

  const existingOp = state.patchOps.find((op) => isPatchOpForPath(op, p)) ?? null;
  const isSame = shallowEqualPrimitive(extractedValue, nextValue);

  if (isSame) {
    if (!existingOp) return state;
    const nextOps = removeOp(state.patchOps, p);
    if (nextOps.length === state.patchOps.length) return state;
    return {
      patchOps: nextOps,
      undoStack: pushUndo(state.undoStack, state.patchOps),
      redoStack: [],
    };
  }

  if (
    existingOp &&
    (existingOp.op === "replace" || existingOp.op === "add") &&
    shallowEqualPrimitive(existingOp.value, nextValue)
  ) {
    return state;
  }

  const nextOps = upsertReplaceOp(state.patchOps, p, nextValue);
  return {
    patchOps: nextOps,
    undoStack: pushUndo(state.undoStack, state.patchOps),
    redoStack: [],
  };
}

export function patchStoreClearEditedValue(state: PatchStoreState, path: string): PatchStoreState {
  const p = String(path || "").trim();
  if (!p) return state;
  const nextOps = removeOp(state.patchOps, p);
  if (nextOps.length === state.patchOps.length) return state;
  return {
    patchOps: nextOps,
    undoStack: pushUndo(state.undoStack, state.patchOps),
    redoStack: [],
  };
}

export function patchStoreClearAll(state: PatchStoreState): PatchStoreState {
  if (state.patchOps.length === 0) return state;
  return {
    patchOps: [],
    undoStack: pushUndo(state.undoStack, state.patchOps),
    redoStack: [],
  };
}

export function patchStoreUndo(state: PatchStoreState): PatchStoreState {
  if (state.undoStack.length === 0) return state;
  const nextUndo = state.undoStack.slice(0, -1);
  const snapshot = state.undoStack[state.undoStack.length - 1] ?? [];
  return {
    patchOps: snapshot,
    undoStack: nextUndo,
    redoStack: state.redoStack.concat([state.patchOps]),
  };
}

export function patchStoreRedo(state: PatchStoreState): PatchStoreState {
  if (state.redoStack.length === 0) return state;
  const nextRedo = state.redoStack.slice(0, -1);
  const snapshot = state.redoStack[state.redoStack.length - 1] ?? [];
  return {
    patchOps: snapshot,
    undoStack: state.undoStack.concat([state.patchOps]),
    redoStack: nextRedo,
  };
}

