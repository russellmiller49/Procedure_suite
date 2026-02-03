import React, { useCallback, useEffect, useMemo } from "react";

import { buildEvidenceIndex } from "./evidence/buildEvidenceIndex";
import { RegistryGrid } from "./components/RegistryGrid";
import type { RegistryGridEditsExport } from "./edits/types";
import { usePatchStore } from "./edits/usePatchStore";
import { flattenRegistryToRows } from "./flatten/flattenRegistryToRows";
import { highlightSpan } from "./monaco/monacoBridge";
import type { EvidenceSpan } from "./types";

type Props = {
  processResponse: unknown;
  getMonacoEditor?: (() => unknown) | null;
  onEditsExport?: ((payload: RegistryGridEditsExport | null) => void) | null;
};

function formatValueForType(valueType: string, value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (valueType === "boolean" || typeof value === "boolean") return value ? "Yes" : "No";
  if (valueType === "number" || typeof value === "number")
    return typeof value === "number" && Number.isFinite(value) ? String(value) : "—";
  if (valueType === "string" || typeof value === "string") return String(value ?? "");
  return String(value ?? "—");
}

export function RegistryGridApp({ processResponse, getMonacoEditor, onEditsExport }: Props) {
  const patchStore = usePatchStore();

  const registry = useMemo(() => {
    if (!processResponse || typeof processResponse !== "object") return null;
    const raw = (processResponse as { registry?: unknown }).registry;
    return raw && typeof raw === "object" ? raw : null;
  }, [processResponse]);

  const evidenceIndex = useMemo(() => buildEvidenceIndex(processResponse), [processResponse]);
  const baseRows = useMemo(() => flattenRegistryToRows(registry, evidenceIndex), [registry, evidenceIndex]);
  const rows = useMemo(() => {
    if (!patchStore.hasEdits) return baseRows;
    return baseRows.map((row) => {
      const edited = patchStore.editedValueByPath.get(row.jsonPointer);
      if (edited === undefined) return row;
      return {
        ...row,
        editedValueRaw: edited,
        editedValueDisplay: formatValueForType(row.valueType, edited),
      };
    });
  }, [baseRows, patchStore.editedValueByPath, patchStore.hasEdits]);
  const evidenceCount = useMemo(
    () => Array.from(evidenceIndex.values()).reduce((acc, spans) => acc + spans.length, 0),
    [evidenceIndex],
  );
  const rowsWithEvidence = useMemo(() => rows.filter((r) => r.evidence.length > 0).length, [rows]);

  useEffect(() => {
    // New response => clear prior edits (edits are per-run).
    patchStore.clearAll();
  }, [processResponse, patchStore.clearAll]);

  const onEvidenceClick = useCallback(
    (ev: EvidenceSpan) => {
      const editor = getMonacoEditor?.() ?? null;
      highlightSpan(editor, ev.span?.[0], ev.span?.[1], { label: ev.source || "Evidence" });
    },
    [getMonacoEditor],
  );

  const onEditValue = useCallback(
    (row: { jsonPointer: string; extractedValueRaw: unknown }, nextValue: unknown) => {
      patchStore.setEditedValue(row.jsonPointer, row.extractedValueRaw, nextValue);
    },
    [patchStore.setEditedValue],
  );

  const onClearEdit = useCallback(
    (row: { jsonPointer: string }) => {
      patchStore.clearEditedValue(row.jsonPointer);
    },
    [patchStore.clearEditedValue],
  );

  const editsExport = useMemo<RegistryGridEditsExport | null>(() => {
    if (!patchStore.hasEdits) return null;
    const editedFields = rows
      .filter((r) => !r.isGroup && r.editedValueRaw !== null && r.editedValueRaw !== undefined)
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
  }, [patchStore.hasEdits, patchStore.patchOps, rows]);

  useEffect(() => {
    try {
      onEditsExport?.(editsExport);
    } catch {
      // ignore host callback failures
    }
  }, [editsExport, onEditsExport]);

  return (
    <div className="ps-registry-grid-shell">
      <div className="ps-registry-grid-header">
        Registry V3 Grid{" "}
        <span className="ps-muted">
          (evidence: {evidenceCount}, rows: {rowsWithEvidence})
        </span>
      </div>
      <div className="ps-registry-grid-body">
        {processResponse ? (
          registry ? (
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
            <div className="ps-registry-grid-meta">No registry object found on process response.</div>
          )
        ) : (
          <div className="ps-registry-grid-meta">No process response yet.</div>
        )}
      </div>
    </div>
  );
}
