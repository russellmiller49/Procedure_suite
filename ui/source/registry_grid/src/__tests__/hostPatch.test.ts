import { describe, expect, it } from "vitest";

import { hostPatchSignature, sanitizeHostPatchOps } from "../edits/hostPatch";

describe("sanitizeHostPatchOps", () => {
  it("keeps only valid registry patch ops", () => {
    const out = sanitizeHostPatchOps([
      { op: "replace", path: "/registry/clinical_context/asa_class", value: 3 },
      { op: "add", path: "/registry/procedure/indication", value: "Adenopathy" },
      { op: "remove", path: "/registry/clinical_context/ecog_text" },
      { op: "replace", path: "/local/patient_label", value: "Case 1" },
      { op: "copy", path: "/registry/foo", value: "x" },
      { op: "replace", path: "/registry/no_value" },
      null,
      "bad",
    ]);

    expect(out).toEqual([
      { op: "replace", path: "/registry/clinical_context/asa_class", value: 3 },
      { op: "add", path: "/registry/procedure/indication", value: "Adenopathy" },
      { op: "remove", path: "/registry/clinical_context/ecog_text" },
    ]);
  });

  it("deduplicates by path and keeps the last op", () => {
    const out = sanitizeHostPatchOps([
      { op: "replace", path: "/registry/a", value: 1 },
      { op: "replace", path: "/registry/b", value: 2 },
      { op: "replace", path: "/registry/a", value: 3 },
      { op: "remove", path: "/registry/b" },
    ]);

    expect(out).toEqual([
      { op: "replace", path: "/registry/a", value: 3 },
      { op: "remove", path: "/registry/b" },
    ]);
  });
});

describe("hostPatchSignature", () => {
  it("returns a stable signature for sanitized ops", () => {
    const ops = sanitizeHostPatchOps([
      { op: "replace", path: "/registry/a", value: "x" },
      { op: "replace", path: "/registry/a", value: "x" },
    ]);
    expect(hostPatchSignature(ops)).toBe('[{"op":"replace","path":"/registry/a","value":"x"}]');
  });
});
