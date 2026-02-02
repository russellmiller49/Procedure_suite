import { useCallback, useMemo, useState } from "react";

import type { JSONPatchOp } from "./types";
import {
  EMPTY_PATCH_STORE_STATE,
  buildEditedValueByPath,
  patchStoreClearAll,
  patchStoreClearEditedValue,
  patchStoreRedo,
  patchStoreSetEditedValue,
  patchStoreUndo,
  type PatchStoreState,
} from "./patchStoreCore";

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

export function usePatchStore(): PatchStore {
  const [state, setState] = useState<PatchStoreState>(EMPTY_PATCH_STORE_STATE);

  const editedValueByPath = useMemo(() => buildEditedValueByPath(state.patchOps), [state.patchOps]);

  const hasEdits = state.patchOps.length > 0;
  const canUndo = state.undoStack.length > 0;
  const canRedo = state.redoStack.length > 0;

  const setEditedValue = useCallback((path: string, extractedValue: unknown, nextValue: unknown) => {
    setState((prev) => patchStoreSetEditedValue(prev, path, extractedValue, nextValue));
  }, []);

  const clearEditedValue = useCallback((path: string) => {
    setState((prev) => patchStoreClearEditedValue(prev, path));
  }, []);

  const clearAll = useCallback(() => {
    setState((prev) => patchStoreClearAll(prev));
  }, []);

  const undo = useCallback(() => {
    setState((prev) => patchStoreUndo(prev));
  }, []);

  const redo = useCallback(() => {
    setState((prev) => patchStoreRedo(prev));
  }, []);

  return {
    patchOps: state.patchOps,
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

