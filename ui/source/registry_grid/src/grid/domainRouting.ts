import type { RegistryRow } from "../types";

export type GridEditRoute = "local_vault" | "remote_patch";

export function resolveEditRoute(row: Pick<RegistryRow, "domain" | "jsonPointer">): GridEditRoute {
  if (row.domain === "local") return "local_vault";
  if (row.domain === "remote") return "remote_patch";
  const pointer = String(row.jsonPointer || "");
  if (pointer === "/local" || pointer.startsWith("/local/")) return "local_vault";
  return "remote_patch";
}

