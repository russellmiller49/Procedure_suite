import type { JSONPatchOp } from "./types";

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function normalizePatchOpKind(value: unknown): "add" | "replace" | "remove" | null {
  const op = String(value || "").trim().toLowerCase();
  if (op === "add" || op === "replace" || op === "remove") return op;
  return null;
}

function isRegistryPointer(path: unknown): path is string {
  const pointer = String(path || "").trim();
  return pointer === "/registry" || pointer.startsWith("/registry/");
}

export function sanitizeHostPatchOps(input: unknown): JSONPatchOp[] {
  const list = Array.isArray(input) ? input : [];
  const byPath = new Map<string, JSONPatchOp>();

  list.forEach((item) => {
    if (!isRecord(item)) return;
    const opKind = normalizePatchOpKind(item.op);
    if (!opKind) return;
    const path = String(item.path || "").trim();
    if (!isRegistryPointer(path)) return;

    if (byPath.has(path)) byPath.delete(path);

    if (opKind === "remove") {
      byPath.set(path, { op: "remove", path });
      return;
    }

    if (!("value" in item)) return;
    byPath.set(path, { op: opKind, path, value: item.value });
  });

  return Array.from(byPath.values());
}

export function hostPatchSignature(ops: JSONPatchOp[]): string {
  return JSON.stringify(Array.isArray(ops) ? ops : []);
}
