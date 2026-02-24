import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { RegistryGrid } from "./components/RegistryGrid";
import { resolveEditRoute } from "./grid/domainRouting";
import type { RegistryGridEditsExport } from "./edits/types";
import { hostPatchSignature, sanitizeHostPatchOps } from "./edits/hostPatch";
import { usePatchStore } from "./edits/usePatchStore";
import { buildEvidenceIndex } from "./evidence/buildEvidenceIndex";
import { flattenRegistryToRows } from "./flatten/flattenRegistryToRows";
import { highlightSpan } from "./monaco/monacoBridge";
import type { EvidenceSpan, RegistryRow } from "./types";
import { normalizeVaultPatientData, type CanonicalVaultPatient } from "./utils/cryptoVault";

type Props = {
  processResponse: unknown;
  registryUuid?: string | null;
  vaultLocalData?: unknown;
  remoteCaseData?: unknown;
  getMonacoEditor?: (() => unknown) | null;
  onEditsExport?: ((payload: RegistryGridEditsExport | null) => void) | null;
  onSaveLocalVaultData?: ((payload: unknown) => Promise<unknown> | unknown) | null;
  onSaveRemotePatch?: ((payload: unknown) => Promise<unknown> | unknown) | null;
  hostEditedPatch?: unknown;
};

type LocalFieldDef = {
  pointer: string;
  label: string;
};

const LOCAL_GROUP_ID = "local:/local";
const REMOTE_GROUP_ID = "remote:/registry";

const LOCAL_FIELD_DEFS: LocalFieldDef[] = [
  { pointer: "/local/patient_label", label: "Patient Label" },
  { pointer: "/local/index_date", label: "Index Date" },
  { pointer: "/local/local_meta/mrn", label: "MRN" },
  { pointer: "/local/local_meta/custom_notes", label: "Custom Notes" },
];

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function deepClone<T>(value: T): T {
  if (typeof globalThis.structuredClone === "function") return globalThis.structuredClone(value);
  return JSON.parse(JSON.stringify(value)) as T;
}

function decodeJsonPointerSegment(seg: string): string {
  // JSON Pointer (RFC 6901): "~1" => "/", "~0" => "~" (order matters).
  return String(seg || "").replace(/~1/g, "/").replace(/~0/g, "~");
}

function looksLikeArrayIndex(seg: string): boolean {
  if (!seg) return false;
  if (!/^\d+$/.test(seg)) return false;
  const idx = Number(seg);
  return Number.isInteger(idx) && idx >= 0;
}

function ensureRegistryPointerPathExists(registry: Record<string, unknown>, pointer: string): void {
  const path = String(pointer || "").trim();
  if (!path || path === "/registry") return;
  if (!path.startsWith("/registry/")) return;

  const parts = path.split("/").slice(2).map(decodeJsonPointerSegment).filter((p) => p !== "");
  if (parts.length === 0) return;

  let curr: unknown = registry;
  for (let i = 0; i < parts.length; i += 1) {
    const key = parts[i];
    const isLast = i === parts.length - 1;
    const nextKey = parts[i + 1] ?? "";

    if (Array.isArray(curr)) {
      const idx = Number(key);
      if (!Number.isInteger(idx) || idx < 0) return;
      if (curr[idx] === undefined) {
        if (isLast) {
          curr[idx] = null;
          return;
        }
        curr[idx] = looksLikeArrayIndex(nextKey) ? [] : {};
      }

      if (isLast) return;
      const next = curr[idx];
      if (next === null || typeof next !== "object") {
        curr[idx] = looksLikeArrayIndex(nextKey) ? [] : {};
      }
      curr = curr[idx];
      continue;
    }

    if (!isRecord(curr)) return;
    if (curr[key] === undefined) {
      if (isLast) {
        curr[key] = null;
        return;
      }
      curr[key] = looksLikeArrayIndex(nextKey) ? [] : {};
    }

    if (isLast) return;
    const next = curr[key];
    if (next === null || typeof next !== "object") {
      curr[key] = looksLikeArrayIndex(nextKey) ? [] : {};
    }
    curr = curr[key];
  }
}

function buildRemoteRegistryRowsInput(
  remoteRegistry: unknown,
  hostPatchOps: Array<{ op: string; path: string }>,
): unknown {
  if (!isRecord(remoteRegistry)) return remoteRegistry;
  if (!hostPatchOps.length) return remoteRegistry;

  const clone = deepClone(remoteRegistry);
  for (const op of hostPatchOps) {
    if (!op || typeof op !== "object") continue;
    // Only materialize paths for adds/replaces (removals don't need placeholder rows).
    if (op.op === "remove") continue;
    ensureRegistryPointerPathExists(clone, op.path);
  }
  return clone;
}

function asText(value: unknown): string {
  return String(value ?? "");
}

function formatValueForType(valueType: string, value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (valueType === "boolean" || typeof value === "boolean") return value ? "Yes" : "No";
  if (valueType === "number" || typeof value === "number")
    return typeof value === "number" && Number.isFinite(value) ? String(value) : "—";
  if (valueType === "string" || typeof value === "string") return String(value ?? "");
  return String(value ?? "—");
}

function resolveRegistryUuid(
  registryUuid: string | null | undefined,
  vaultLocalData: unknown,
  remoteCaseData: unknown,
): string {
  const direct = String(registryUuid || "").trim();
  if (direct) return direct;

  if (isRecord(vaultLocalData)) {
    const fromLocal = String(vaultLocalData.registry_uuid || "").trim();
    if (fromLocal) return fromLocal;
  }

  if (isRecord(remoteCaseData)) {
    const fromRemote = String(remoteCaseData.registry_uuid || "").trim();
    if (fromRemote) return fromRemote;
  }

  return "";
}

function getLocalFieldValue(localData: CanonicalVaultPatient, pointer: string): string {
  if (pointer === "/local/patient_label") return asText(localData.patient_label);
  if (pointer === "/local/index_date") return asText(localData.index_date || "");
  if (pointer === "/local/local_meta/mrn") return asText(localData.local_meta?.mrn || "");
  if (pointer === "/local/local_meta/custom_notes") return asText(localData.local_meta?.custom_notes || "");
  return "";
}

function setLocalFieldValue(
  localData: CanonicalVaultPatient,
  pointer: string,
  value: unknown,
  registryUuid: string,
): CanonicalVaultPatient {
  const next = {
    ...localData,
    local_meta: { ...(isRecord(localData.local_meta) ? localData.local_meta : {}) },
    saved_at: new Date().toISOString(),
  } as Record<string, unknown>;
  const text = asText(value);

  if (pointer === "/local/patient_label") next.patient_label = text;
  if (pointer === "/local/index_date") next.index_date = text;
  if (pointer === "/local/local_meta/mrn" && isRecord(next.local_meta)) next.local_meta.mrn = text;
  if (pointer === "/local/local_meta/custom_notes" && isRecord(next.local_meta)) {
    next.local_meta.custom_notes = text;
  }

  return normalizeVaultPatientData(next, registryUuid);
}

function withRemoteDomainRows(rows: RegistryRow[]): RegistryRow[] {
  if (!rows.length) return [];

  const groupRow: RegistryRow = {
    id: REMOTE_GROUP_ID,
    jsonPointer: "/registry",
    pathSegments: ["Remote (Registry)"],
    depth: 0,
    fieldLabel: "Remote (Registry)",
    extractedValueRaw: null,
    extractedValueDisplay: "Canonical registry record",
    editedValueRaw: null,
    editedValueDisplay: null,
    valueType: "object",
    evidence: [],
    isGroup: true,
    parentId: null,
    domain: "remote",
  };

  const remoteRows = rows.map((row) => {
    const pathSegments = ["Remote (Registry)", ...row.pathSegments];
    return {
      ...row,
      id: `remote:${row.id}`,
      parentId: row.parentId ? `remote:${row.parentId}` : REMOTE_GROUP_ID,
      pathSegments,
      depth: Math.max(pathSegments.length - 1, 0),
      domain: "remote" as const,
    };
  });

  return [groupRow, ...remoteRows];
}

function buildLocalRows(draft: CanonicalVaultPatient, baseline: CanonicalVaultPatient): RegistryRow[] {
  const groupRow: RegistryRow = {
    id: LOCAL_GROUP_ID,
    jsonPointer: "/local",
    pathSegments: ["Local (Vault)"],
    depth: 0,
    fieldLabel: "Local (Vault)",
    extractedValueRaw: null,
    extractedValueDisplay: "Encrypted local-only metadata",
    editedValueRaw: null,
    editedValueDisplay: null,
    valueType: "object",
    evidence: [],
    isGroup: true,
    parentId: null,
    domain: "local",
  };

  const leafRows = LOCAL_FIELD_DEFS.map((field) => {
    const current = getLocalFieldValue(draft, field.pointer);
    const previous = getLocalFieldValue(baseline, field.pointer);
    const changed = current !== previous;

    return {
      id: `local:${field.pointer}`,
      jsonPointer: field.pointer,
      pathSegments: ["Local (Vault)", field.label],
      depth: 1,
      fieldLabel: field.label,
      extractedValueRaw: current,
      extractedValueDisplay: current.trim() ? current : "—",
      editedValueRaw: changed ? current : null,
      editedValueDisplay: changed ? (current.trim() ? current : "—") : null,
      valueType: "string" as const,
      evidence: [],
      isGroup: false,
      parentId: LOCAL_GROUP_ID,
      domain: "local" as const,
    } satisfies RegistryRow;
  });

  return [groupRow, ...leafRows];
}

function localEditsPending(draft: CanonicalVaultPatient, baseline: CanonicalVaultPatient): boolean {
  return LOCAL_FIELD_DEFS.some(
    (field) => getLocalFieldValue(draft, field.pointer) !== getLocalFieldValue(baseline, field.pointer),
  );
}

export function RegistryGridApp({
  processResponse,
  registryUuid,
  vaultLocalData,
  remoteCaseData,
  getMonacoEditor,
  onEditsExport,
  onSaveLocalVaultData,
  onSaveRemotePatch,
  hostEditedPatch,
}: Props) {
  const patchStore = usePatchStore();
  const lastAppliedHostPatchSignatureRef = useRef<string>("");

  const resolvedRegistryUuid = useMemo(
    () => resolveRegistryUuid(registryUuid, vaultLocalData, remoteCaseData),
    [registryUuid, vaultLocalData, remoteCaseData],
  );

  const localBase = useMemo(
    () => normalizeVaultPatientData(vaultLocalData, resolvedRegistryUuid),
    [vaultLocalData, resolvedRegistryUuid],
  );
  const localBaseKey = useMemo(
    () =>
      JSON.stringify({
        registry_uuid: localBase.registry_uuid,
        patient_label: localBase.patient_label,
        index_date: localBase.index_date,
        local_meta: localBase.local_meta,
      }),
    [localBase],
  );

  const [localDraft, setLocalDraft] = useState<CanonicalVaultPatient>(localBase);
  const [localCommitted, setLocalCommitted] = useState<CanonicalVaultPatient>(localBase);
  const [localSaveStatus, setLocalSaveStatus] = useState<string>("");
  const [remoteSaveStatus, setRemoteSaveStatus] = useState<string>("");
  const [remoteCaseOverride, setRemoteCaseOverride] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    setLocalDraft(localBase);
    setLocalCommitted(localBase);
    setLocalSaveStatus("");
  }, [localBase, localBaseKey]);

  const remoteCaseKey = useMemo(() => {
    if (!isRecord(remoteCaseData)) return "";
    return `${String(remoteCaseData.registry_uuid || "")}:${String(remoteCaseData.version || "")}:${String(
      remoteCaseData.updated_at || "",
    )}`;
  }, [remoteCaseData]);

  useEffect(() => {
    setRemoteCaseOverride(null);
    setRemoteSaveStatus("");
  }, [remoteCaseKey, processResponse, resolvedRegistryUuid]);

  const effectiveRemoteCase = useMemo(() => {
    if (remoteCaseOverride) return remoteCaseOverride;
    return isRecord(remoteCaseData) ? remoteCaseData : null;
  }, [remoteCaseData, remoteCaseOverride]);

  const remoteRegistry = useMemo(() => {
    if (isRecord(effectiveRemoteCase?.registry)) return effectiveRemoteCase.registry;
    if (!processResponse || typeof processResponse !== "object") return null;
    const raw = (processResponse as { registry?: unknown }).registry;
    return raw && typeof raw === "object" ? raw : null;
  }, [effectiveRemoteCase, processResponse]);

  const remoteVersion = useMemo(() => {
    const raw = isRecord(effectiveRemoteCase) ? effectiveRemoteCase.version : null;
    return Number.isInteger(raw) ? Number(raw) : null;
  }, [effectiveRemoteCase]);

  const hostPatchOps = useMemo(() => sanitizeHostPatchOps(hostEditedPatch), [hostEditedPatch]);
  const hostPatchOpsSignature = useMemo(() => hostPatchSignature(hostPatchOps), [hostPatchOps]);

  const evidenceIndex = useMemo(() => buildEvidenceIndex(processResponse), [processResponse]);
  const remoteRegistryRowsInput = useMemo(
    () => buildRemoteRegistryRowsInput(remoteRegistry, hostPatchOps),
    [remoteRegistry, hostPatchOpsSignature, hostPatchOps],
  );
  const remoteBaseRows = useMemo(
    () => flattenRegistryToRows(remoteRegistryRowsInput, evidenceIndex),
    [remoteRegistryRowsInput, evidenceIndex],
  );
  const remoteRowsWithDomain = useMemo(() => withRemoteDomainRows(remoteBaseRows), [remoteBaseRows]);

  const remoteRows = useMemo(() => {
    if (!patchStore.hasEdits) return remoteRowsWithDomain;
    return remoteRowsWithDomain.map((row) => {
      if (row.domain !== "remote" || row.isGroup) return row;
      const edited = patchStore.editedValueByPath.get(row.jsonPointer);
      if (edited === undefined) return row;
      return {
        ...row,
        editedValueRaw: edited,
        editedValueDisplay: formatValueForType(row.valueType, edited),
      };
    });
  }, [patchStore.editedValueByPath, patchStore.hasEdits, remoteRowsWithDomain]);

  const remoteLeafRowByPointer = useMemo(() => {
    const out = new Map<string, RegistryRow>();
    remoteRowsWithDomain.forEach((row) => {
      if (row.domain !== "remote" || row.isGroup) return;
      out.set(row.jsonPointer, row);
    });
    return out;
  }, [remoteRowsWithDomain]);

  const localRows = useMemo(
    () => buildLocalRows(localDraft, localCommitted),
    [localCommitted, localDraft],
  );

  const rows = useMemo(() => [...localRows, ...remoteRows], [localRows, remoteRows]);

  const evidenceCount = useMemo(
    () => Array.from(evidenceIndex.values()).reduce((acc, spans) => acc + spans.length, 0),
    [evidenceIndex],
  );
  const rowsWithEvidence = useMemo(() => remoteRows.filter((r) => r.evidence.length > 0).length, [remoteRows]);
  const localDirty = useMemo(() => localEditsPending(localDraft, localCommitted), [localCommitted, localDraft]);

  useEffect(() => {
    // New response/case => clear prior remote edits.
    patchStore.clearAll();
  }, [processResponse, resolvedRegistryUuid, patchStore.clearAll]);

  useEffect(() => {
    // New response/case should accept the latest host patch as fresh input.
    lastAppliedHostPatchSignatureRef.current = "";
  }, [processResponse, resolvedRegistryUuid]);

  useEffect(() => {
    if (hostPatchOpsSignature === lastAppliedHostPatchSignatureRef.current) return;
    lastAppliedHostPatchSignatureRef.current = hostPatchOpsSignature;
    if (!hostPatchOps.length) return;

    hostPatchOps.forEach((op) => {
      if (op.op === "remove") {
        patchStore.clearEditedValue(op.path);
        return;
      }
      const row = remoteLeafRowByPointer.get(op.path);
      patchStore.setEditedValue(op.path, row?.extractedValueRaw, op.value);
    });
  }, [
    hostPatchOps,
    hostPatchOpsSignature,
    patchStore.clearEditedValue,
    patchStore.setEditedValue,
    remoteLeafRowByPointer,
  ]);

  const onEvidenceClick = useCallback(
    (ev: EvidenceSpan) => {
      const editor = getMonacoEditor?.() ?? null;
      highlightSpan(editor, ev.span?.[0], ev.span?.[1], { label: ev.source || "Evidence" });
    },
    [getMonacoEditor],
  );

  const onEditValue = useCallback(
    (row: RegistryRow, nextValue: unknown) => {
      const route = resolveEditRoute(row);
      if (route === "local_vault") {
        setLocalSaveStatus("");
        setLocalDraft((prev) => setLocalFieldValue(prev, row.jsonPointer, nextValue, resolvedRegistryUuid));
        return;
      }
      setRemoteSaveStatus("");
      patchStore.setEditedValue(row.jsonPointer, row.extractedValueRaw, nextValue);
    },
    [patchStore.setEditedValue, resolvedRegistryUuid],
  );

  const onClearEdit = useCallback(
    (row: RegistryRow) => {
      const route = resolveEditRoute(row);
      if (route === "local_vault") {
        setLocalSaveStatus("");
        const baselineValue = getLocalFieldValue(localCommitted, row.jsonPointer);
        setLocalDraft((prev) => setLocalFieldValue(prev, row.jsonPointer, baselineValue, resolvedRegistryUuid));
        return;
      }
      setRemoteSaveStatus("");
      patchStore.clearEditedValue(row.jsonPointer);
    },
    [localCommitted, patchStore.clearEditedValue, resolvedRegistryUuid],
  );

  const saveLocalVault = useCallback(async () => {
    if (!onSaveLocalVaultData || !resolvedRegistryUuid) return;
    setLocalSaveStatus("Saving locally…");
    try {
      await onSaveLocalVaultData({
        registry_uuid: resolvedRegistryUuid,
        vault_local_data: localDraft,
      });
      setLocalCommitted(localDraft);
      setLocalSaveStatus("Saved locally");
    } catch (err) {
      const message = String((err as Error)?.message || err || "Unknown error");
      setLocalSaveStatus(`Local save failed: ${message}`);
    }
  }, [localDraft, onSaveLocalVaultData, resolvedRegistryUuid]);

  const saveRemotePatch = useCallback(async () => {
    if (!onSaveRemotePatch || !resolvedRegistryUuid || !isRecord(remoteRegistry) || !patchStore.hasEdits) return;
    setRemoteSaveStatus("Saving to registry…");
    try {
      const result = await onSaveRemotePatch({
        registry_uuid: resolvedRegistryUuid,
        expected_version: remoteVersion,
        base_registry: remoteRegistry,
        edited_patch: patchStore.patchOps,
      });
      if (isRecord(result)) {
        setRemoteCaseOverride(result);
      }
      patchStore.clearAll();
      setRemoteSaveStatus("Saved to registry");
    } catch (err) {
      const message = String((err as Error)?.message || err || "Unknown error");
      setRemoteSaveStatus(`Remote save failed: ${message}`);
    }
  }, [
    onSaveRemotePatch,
    patchStore.clearAll,
    patchStore.hasEdits,
    patchStore.patchOps,
    remoteRegistry,
    remoteVersion,
    resolvedRegistryUuid,
  ]);

  const editsExport = useMemo<RegistryGridEditsExport | null>(() => {
    if (!patchStore.hasEdits) return null;
    const editedFields = remoteRows
      .filter((r) => r.domain === "remote" && !r.isGroup && r.editedValueRaw !== null && r.editedValueRaw !== undefined)
      .map((r) => ({
        path: r.jsonPointer,
        field_label: r.pathSegments.join(" › "),
        value_type: r.valueType,
        extracted: r.extractedValueRaw,
        edited: r.editedValueRaw,
        evidence: r.evidence,
      }))
      .sort((a, b) => a.path.localeCompare(b.path));

    return {
      edited_source: "ui_registry_grid",
      edited_patch: patchStore.patchOps,
      edited_fields: editedFields,
    };
  }, [patchStore.hasEdits, patchStore.patchOps, remoteRows]);

  useEffect(() => {
    try {
      onEditsExport?.(editsExport);
    } catch {
      // ignore host callback failures
    }
  }, [editsExport, onEditsExport]);

  const remotePatchCount = patchStore.patchOps.length;
  const remoteSaveDisabled =
    !onSaveRemotePatch || !resolvedRegistryUuid || !isRecord(remoteRegistry) || remotePatchCount === 0;
  const localSaveDisabled = !onSaveLocalVaultData || !resolvedRegistryUuid || !localDirty;

  return (
    <div className="ps-registry-grid-shell">
      <div className="ps-registry-grid-header">
        Zero-Knowledge Clinical Registry{" "}
        <span className="ps-muted">
          (evidence: {evidenceCount}, evidence rows: {rowsWithEvidence})
        </span>
      </div>

      <div className="ps-registry-grid-savebar">
        <button type="button" className="ps-btn" onClick={saveLocalVault} disabled={localSaveDisabled}>
          Save Local (Vault)
        </button>
        <span className="ps-muted">{localSaveStatus || (localDirty ? "Local edits pending" : "Saved locally")}</span>
        <button type="button" className="ps-btn" onClick={saveRemotePatch} disabled={remoteSaveDisabled}>
          Save Remote (Registry)
        </button>
        <span className="ps-muted">
          {remoteSaveStatus || (remotePatchCount > 0 ? `Remote edits pending (${remotePatchCount})` : "Saved to registry")}
        </span>
      </div>

      <div className="ps-registry-grid-body">
        {rows.length > 0 ? (
          <RegistryGrid
            rows={rows}
            onEvidenceClick={onEvidenceClick}
            onEditValue={onEditValue}
            onClearEdit={onClearEdit}
            onClearAllEdits={patchStore.clearAll}
            onUndo={patchStore.undo}
            onRedo={patchStore.redo}
            canUndo={patchStore.canUndo}
            canRedo={patchStore.canRedo}
            editCount={patchStore.patchOps.length}
          />
        ) : (
          <div className="ps-registry-grid-meta">No case data available yet.</div>
        )}
      </div>
    </div>
  );
}
