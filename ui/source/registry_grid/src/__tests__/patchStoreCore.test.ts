import { describe, expect, it } from "vitest";

import {
  EMPTY_PATCH_STORE_STATE,
  patchStoreClearEditedValue,
  patchStoreRedo,
  patchStoreSetEditedValue,
  patchStoreUndo,
} from "../edits/patchStoreCore";

describe("patchStoreCore", () => {
  it("tracks edits and supports undo/redo", () => {
    let state = EMPTY_PATCH_STORE_STATE;

    state = patchStoreSetEditedValue(state, "/registry/foo", 1, 2);
    expect(state.patchOps).toEqual([{ op: "replace", path: "/registry/foo", value: 2 }]);
    expect(state.undoStack.length).toBe(1);
    expect(state.redoStack.length).toBe(0);

    const unchanged = patchStoreSetEditedValue(state, "/registry/foo", 1, 2);
    expect(unchanged).toBe(state);

    state = patchStoreSetEditedValue(state, "/registry/foo", 1, 1);
    expect(state.patchOps).toEqual([]);
    expect(state.undoStack.length).toBe(2);

    state = patchStoreUndo(state);
    expect(state.patchOps).toEqual([{ op: "replace", path: "/registry/foo", value: 2 }]);
    expect(state.redoStack.length).toBe(1);

    state = patchStoreRedo(state);
    expect(state.patchOps).toEqual([]);

    const stillEmpty = patchStoreClearEditedValue(state, "/registry/foo");
    expect(stillEmpty).toBe(state);
  });
});

