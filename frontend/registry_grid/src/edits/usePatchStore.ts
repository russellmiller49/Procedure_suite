import { useCallback, useMemo, useState } from "react";

import type { JSONPatchOp } from "./types";

type PatchSnapshot = JSONPatchOp[];

type PatchStore = {
  patchOps: JSONPatchOp[];
  hasEdits: boolean;
  canUndo: boolean;
  canRedo: boolean;
  editedValueByPath: Map<string, unknown>;
  setEditedValue: (path: string, extractedValue: unknown, nextValue: unknown) => void;
  clearEditedValue: (path: string) => void;
  clearAll: () => void;
  undo: () => void;
  redo: () => void;
};

function isPatchOpForPath(op: JSONPatchOp, path: string): boolean {
  return Boolean(op && typeof op === "object" && op.path === path);
}

function shallowEqualPrimitive(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  // Treat NaN as equal to NaN for numeric edits.
  if (typeof a === "number" && typeof b === "number" && Number.isNaN(a) && Number.isNaN(b)) return true;
  return false;
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

export function usePatchStore(): PatchStore {
  const [patchOps, setPatchOps] = useState<JSONPatchOp[]>([]);
  const [undoStack, setUndoStack] = useState<PatchSnapshot[]>([]);
  const [redoStack, setRedoStack] = useState<PatchSnapshot[]>([]);

  const editedValueByPath = useMemo(() => {
    const map = new Map<string, unknown>();
    for (const op of patchOps) {
      if (!op || typeof op !== "object") continue;
      if (op.op === "replace" || op.op === "add") map.set(op.path, op.value);
      else if (op.op === "remove") map.set(op.path, undefined);
    }
    return map;
  }, [patchOps]);

  const hasEdits = patchOps.length > 0;
  const canUndo = undoStack.length > 0;
  const canRedo = redoStack.length > 0;

  const pushUndo = useCallback((snapshot: PatchSnapshot) => {
    setUndoStack((prev) => {
      const next = prev.concat([snapshot]);
      const max = 80;
      return next.length > max ? next.slice(next.length - max) : next;
    });
  }, []);

  const setEditedValue = useCallback(
    (path: string, extractedValue: unknown, nextValue: unknown) => {
      const p = String(path || "").trim();
      if (!p) return;

      setPatchOps((prev) => {
        const existingOp = prev.find((op) => isPatchOpForPath(op, p)) ?? null;
        // If the user sets a value back to the extracted value, clear the edit for cleanliness.
        const isSame = shallowEqualPrimitive(extractedValue, nextValue);
        if (isSame) {
          if (!existingOp) return prev;
          const next = removeOp(prev, p);
          if (next.length === prev.length) return prev;
          pushUndo(prev);
          setRedoStack([]); // new edit invalidates redo history
          return next;
        }

        if (
          existingOp &&
          (existingOp.op === "replace" || existingOp.op === "add") &&
          shallowEqualPrimitive(existingOp.value, nextValue)
        ) {
          return prev;
        }

        const next = upsertReplaceOp(prev, p, nextValue);

        pushUndo(prev);
        setRedoStack([]); // new edit invalidates redo history
        return next;
      });
    },
    [pushUndo],
  );

  const clearEditedValue = useCallback(
    (path: string) => {
      const p = String(path || "").trim();
      if (!p) return;
      setPatchOps((prev) => {
        const next = removeOp(prev, p);
        if (next.length === prev.length) return prev;
        pushUndo(prev);
        setRedoStack([]);
        return next;
      });
    },
    [pushUndo],
  );

  const clearAll = useCallback(() => {
    setPatchOps((prev) => {
      if (prev.length === 0) return prev;
      pushUndo(prev);
      setRedoStack([]);
      return [];
    });
  }, [pushUndo]);

  const undo = useCallback(() => {
    setUndoStack((prevUndo) => {
      if (prevUndo.length === 0) return prevUndo;
      const nextUndo = prevUndo.slice(0, -1);
      const snapshot = prevUndo[prevUndo.length - 1] ?? [];
      setPatchOps((current) => {
        setRedoStack((prevRedo) => prevRedo.concat([current]));
        return snapshot;
      });
      return nextUndo;
    });
  }, []);

  const redo = useCallback(() => {
    setRedoStack((prevRedo) => {
      if (prevRedo.length === 0) return prevRedo;
      const nextRedo = prevRedo.slice(0, -1);
      const snapshot = prevRedo[prevRedo.length - 1] ?? [];
      setPatchOps((current) => {
        setUndoStack((prevUndo) => prevUndo.concat([current]));
        return snapshot;
      });
      return nextRedo;
    });
  }, []);

  return {
    patchOps,
    hasEdits,
    canUndo,
    canRedo,
    editedValueByPath,
    setEditedValue,
    clearEditedValue,
    clearAll,
    undo,
    redo,
  };
}
