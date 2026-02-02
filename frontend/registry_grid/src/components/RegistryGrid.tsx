import React, { useCallback, useMemo, useRef, useState } from "react";
import type { ColDef, ICellRendererParams } from "ag-grid-community";
import { AgGridReact } from "ag-grid-react";

import type { EvidenceSpan, RegistryRow, ValueType } from "../types";

type Props = {
  rows: RegistryRow[];
  onEvidenceClick?: (ev: EvidenceSpan) => void;
  onEditValue?: (row: RegistryRow, nextValue: unknown) => void;
  onClearEdit?: (row: RegistryRow) => void;
  onClearAllEdits?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
  editCount?: number;
};

type TreeIndex = {
  parentById: Map<string, string | null>;
  childrenById: Map<string, string[]>;
  groupIds: string[];
};

function buildTreeIndex(rows: RegistryRow[]): TreeIndex {
  const parentById = new Map<string, string | null>();
  const childrenById = new Map<string, string[]>();
  const groupIds: string[] = [];

  for (const row of rows) {
    parentById.set(row.id, row.parentId);
    if (row.isGroup) groupIds.push(row.id);
    if (row.parentId) {
      const list = childrenById.get(row.parentId) ?? [];
      list.push(row.id);
      childrenById.set(row.parentId, list);
    }
  }

  return { parentById, childrenById, groupIds };
}

function isPopulatedLeaf(row: RegistryRow): boolean {
  if (row.evidence.length > 0) return true;
  const v = row.editedValueRaw ?? row.extractedValueRaw;
  if (v === null || v === undefined) return false;
  if (typeof v === "string") return v.trim().length > 0;
  if (typeof v === "number") return Number.isFinite(v);
  if (typeof v === "boolean") return v === true; // hide explicit false in "only populated" mode
  return true;
}

function isEditableValueType(valueType: ValueType): boolean {
  return valueType === "boolean" || valueType === "number" || valueType === "string";
}

function deriveVisibleRows(
  rows: RegistryRow[],
  index: TreeIndex,
  showAllFields: boolean,
  collapsedIds: Set<string>,
): RegistryRow[] {
  const included = new Set<string>();

  if (showAllFields) {
    rows.forEach((r) => included.add(r.id));
  } else {
    for (const row of rows) {
      if (row.isGroup) {
        if (row.evidence.length > 0) included.add(row.id);
        continue;
      }
      if (isPopulatedLeaf(row)) included.add(row.id);
    }

    // Ensure ancestors stay visible for tree navigation.
    for (const id of Array.from(included)) {
      let parent = index.parentById.get(id) ?? null;
      while (parent) {
        included.add(parent);
        parent = index.parentById.get(parent) ?? null;
      }
    }
  }

  const hiddenByCollapse = (rowId: string): boolean => {
    let parent = index.parentById.get(rowId) ?? null;
    while (parent) {
      if (collapsedIds.has(parent)) return true;
      parent = index.parentById.get(parent) ?? null;
    }
    return false;
  };

  return rows.filter((r) => included.has(r.id) && !hiddenByCollapse(r.id));
}

function formatEvidenceLabel(ev: EvidenceSpan): string {
  const source = ev.source || "evidence";
  const conf =
    ev.confidence === null || ev.confidence === undefined || !Number.isFinite(ev.confidence)
      ? ""
      : ` ${(ev.confidence * 100).toFixed(0)}%`;
  return `${source}${conf}`;
}

export function RegistryGrid({
  rows,
  onEvidenceClick,
  onEditValue,
  onClearEdit,
  onClearAllEdits,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
  editCount,
}: Props) {
  const gridRef = useRef<AgGridReact<RegistryRow>>(null);

  const [quickFilter, setQuickFilter] = useState("");
  const [showAllFields, setShowAllFields] = useState(false);
  const [collapsedIds, setCollapsedIds] = useState<Set<string>>(() => new Set());

  const treeIndex = useMemo(() => buildTreeIndex(rows), [rows]);

  const visibleRows = useMemo(
    () => deriveVisibleRows(rows, treeIndex, showAllFields, collapsedIds),
    [rows, treeIndex, showAllFields, collapsedIds],
  );

  const isCollapsed = useCallback((id: string) => collapsedIds.has(id), [collapsedIds]);

  const toggleCollapse = useCallback((id: string) => {
    setCollapsedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const expandAll = useCallback(() => setCollapsedIds(new Set()), []);

  const collapseAll = useCallback(() => setCollapsedIds(new Set(treeIndex.groupIds)), [treeIndex.groupIds]);

  const onQuickFilterChange = useCallback((value: string) => {
    setQuickFilter(value);
    const api = gridRef.current?.api;
    if (!api) return;
    // ag-Grid API surface has shifted across versions; support both.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const anyApi = api as any;
    if (typeof anyApi.setQuickFilter === "function") anyApi.setQuickFilter(value);
    else if (typeof anyApi.setGridOption === "function") anyApi.setGridOption("quickFilterText", value);
  }, []);

  const columnDefs = useMemo<ColDef<RegistryRow>[]>(
    () => [
      {
        headerName: "Field",
        field: "fieldLabel",
        flex: 2,
        cellRenderer: (params: ICellRendererParams<RegistryRow>) => {
          const row = params.data;
          if (!row) return null;
          const hasChildren = (treeIndex.childrenById.get(row.id) ?? []).length > 0;
          const collapsed = row.isGroup ? isCollapsed(row.id) : false;
          const indentPx = row.depth * 14;
          const path = row.pathSegments.join(" › ");
          return (
            <div className="ps-field-cell" style={{ paddingLeft: `${indentPx}px` }} title={path}>
              {row.isGroup && hasChildren ? (
                <button
                  type="button"
                  className="ps-tree-toggle"
                  aria-label={collapsed ? "Expand" : "Collapse"}
                  onClick={() => toggleCollapse(row.id)}
                >
                  {collapsed ? "▸" : "▾"}
                </button>
              ) : (
                <span className="ps-tree-spacer" />
              )}
              <span className={row.isGroup ? "ps-field-label ps-field-group" : "ps-field-label"}>
                {row.fieldLabel}
              </span>
            </div>
          );
        },
      },
      {
        headerName: "Extracted Value",
        field: "extractedValueDisplay",
        flex: 2,
        cellClass: "ps-cell-ellipsis",
      },
      {
        headerName: "Evidence",
        field: "evidence",
        flex: 2,
        cellRenderer: (params: ICellRendererParams<RegistryRow>) => {
          const ev = params.data?.evidence ?? [];
          if (!ev || ev.length === 0) return <span className="ps-muted">—</span>;
          const max = 3;
          const shown = ev.slice(0, max);
          const extra = ev.length - shown.length;
          return (
            <div className="ps-evidence-cell" title={ev.map((e) => e.text).filter(Boolean).join("\n\n")}>
              {shown.map((e, idx) => (
                <button
                  key={`${e.source}:${e.span[0]}:${e.span[1]}:${idx}`}
                  type="button"
                  className="ps-pill"
                  onClick={() => onEvidenceClick?.(e)}
                  disabled={!onEvidenceClick}
                  title={e.text || undefined}
                >
                  {formatEvidenceLabel(e)}
                </button>
              ))}
              {extra > 0 ? <span className="ps-muted">+{extra}</span> : null}
            </div>
          );
        },
      },
      {
        headerName: "Edit",
        field: "editedValueDisplay",
        flex: 2,
        cellRenderer: (params: ICellRendererParams<RegistryRow>) => {
          const row = params.data;
          if (!row) return <span className="ps-muted">—</span>;
          if (row.isGroup || !isEditableValueType(row.valueType)) return <span className="ps-muted">—</span>;

          const edited = row.editedValueRaw;
          const hasEdit = edited !== null && edited !== undefined;
          const extracted = row.extractedValueRaw;
          const valueType = row.valueType;
          const baseKey = `${row.id}:${hasEdit ? "edited" : "base"}`;

          const commit = (nextValue: unknown) => {
            if (!onEditValue) return;
            onEditValue(row, nextValue);
          };
          const revert = () => onClearEdit?.(row);

          if (valueType === "boolean") {
            const val = hasEdit ? Boolean(edited) : Boolean(extracted);
            return (
              <div className="ps-edit-cell">
                <select
                  className={hasEdit ? "ps-edit-select ps-edited" : "ps-edit-select"}
                  value={val ? "true" : "false"}
                  onChange={(e) => commit(e.target.value === "true")}
                >
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
                {hasEdit ? (
                  <button type="button" className="ps-edit-revert" onClick={revert} title="Revert edit">
                    ↩
                  </button>
                ) : null}
              </div>
            );
          }

          if (valueType === "number") {
            const current = hasEdit ? edited : extracted;
            const currentText = typeof current === "number" && Number.isFinite(current) ? String(current) : "";
            const placeholder = typeof extracted === "number" && Number.isFinite(extracted) ? String(extracted) : "";
            return (
              <div className="ps-edit-cell">
                <input
                  key={`${baseKey}:num:${currentText}`}
                  className={hasEdit ? "ps-edit-input ps-edited" : "ps-edit-input"}
                  type="number"
                  inputMode="decimal"
                  defaultValue={currentText}
                  placeholder={placeholder}
                  onBlur={(e) => {
                    const text = String((e.target as HTMLInputElement).value || "").trim();
                    if (!text) {
                      if (hasEdit) revert();
                      return;
                    }
                    const num = Number(text);
                    if (!Number.isFinite(num)) return;
                    commit(num);
                  }}
                  onKeyDown={(e) => {
                    if (e.key !== "Enter") return;
                    (e.target as HTMLInputElement).blur();
                  }}
                />
                {hasEdit ? (
                  <button type="button" className="ps-edit-revert" onClick={revert} title="Revert edit">
                    ↩
                  </button>
                ) : null}
              </div>
            );
          }

          // string
          const current = hasEdit ? String(edited ?? "") : String(extracted ?? "");
          const placeholder = hasEdit ? "" : String(extracted ?? "");
          return (
            <div className="ps-edit-cell">
              <input
                key={`${baseKey}:str:${String(edited ?? "")}`}
                className={hasEdit ? "ps-edit-input ps-edited" : "ps-edit-input"}
                type="text"
                defaultValue={current}
                placeholder={placeholder}
                onBlur={(e) => commit(String((e.target as HTMLInputElement).value ?? ""))}
                onKeyDown={(e) => {
                  if (e.key !== "Enter") return;
                  (e.target as HTMLInputElement).blur();
                }}
              />
              {hasEdit ? (
                <button type="button" className="ps-edit-revert" onClick={revert} title="Revert edit">
                  ↩
                </button>
              ) : null}
            </div>
          );
        },
      },
    ],
    [treeIndex.childrenById, isCollapsed, toggleCollapse, onEvidenceClick, onEditValue, onClearEdit],
  );

  const defaultColDef = useMemo<ColDef>(() => ({ sortable: false, resizable: true, filter: false }), []);

  return (
    <div className="ps-registry-grid">
      <div className="ps-registry-grid-toolbar">
        <div className="ps-toolbar-left">
          <input
            className="ps-input"
            type="text"
            value={quickFilter}
            onChange={(e) => onQuickFilterChange(e.target.value)}
            placeholder="Filter…"
            aria-label="Quick filter"
          />
          <div className="ps-toggle-group" role="group" aria-label="Field visibility">
            <button
              type="button"
              className={showAllFields ? "ps-toggle" : "ps-toggle active"}
              onClick={() => setShowAllFields(false)}
            >
              Only populated
            </button>
            <button
              type="button"
              className={showAllFields ? "ps-toggle active" : "ps-toggle"}
              onClick={() => setShowAllFields(true)}
            >
              Show all fields
            </button>
          </div>
        </div>

        <div className="ps-toolbar-right">
          <button type="button" className="ps-btn" onClick={onUndo} disabled={!canUndo}>
            Undo
          </button>
          <button type="button" className="ps-btn" onClick={onRedo} disabled={!canRedo}>
            Redo
          </button>
          <button
            type="button"
            className="ps-btn"
            onClick={onClearAllEdits}
            disabled={!onClearAllEdits || !editCount}
          >
            Revert all
          </button>
          <button type="button" className="ps-btn" onClick={expandAll}>
            Expand all
          </button>
          <button type="button" className="ps-btn" onClick={collapseAll}>
            Collapse all
          </button>
          <div className="ps-muted" title="Visible rows">
            {visibleRows.length.toLocaleString()} rows
          </div>
          <div className="ps-muted" title="Edits">
            {Number(editCount || 0).toLocaleString()} edits
          </div>
        </div>
      </div>

      <div className="ag-theme-quartz ps-grid-host">
        <AgGridReact<RegistryRow>
          ref={gridRef}
          rowData={visibleRows}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          suppressMovableColumns
          suppressCellFocus
          rowSelection="single"
          getRowId={(p) => p.data.id}
          headerHeight={34}
          rowHeight={34}
          animateRows={false}
        />
      </div>
    </div>
  );
}
