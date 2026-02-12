import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
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

type FieldMode = "populated" | "all" | "edited";

const DROPDOWNS_BY_POINTER: Record<string, Array<string | number>> = {
  "/registry/risk_assessment/asa_class": [1, 2, 3, 4, 5, 6],
  "/registry/clinical_context/bronchus_sign": ["Positive", "Negative", "Not assessed"],
  "/registry/clinical_context/ecog_score": [0, 1, 2, 3, 4],
  "/registry/complications/bleeding/bleeding_grade_nashville": [0, 1, 2, 3, 4],
  "/registry/procedures_performed/radial_ebus/probe_position": ["Concentric", "Eccentric", "Adjacent", "Not visualized"],
  "/registry/procedures_performed/navigational_bronchoscopy/confirmation_method": [
    "Radial EBUS",
    "CBCT",
    "Fluoroscopy",
    "Augmented Fluoroscopy",
    "None",
  ],
};

const DROPDOWN_PATTERNS: Array<{ pattern: RegExp; options: Array<string | number> }> = [
  {
    pattern: /^\/registry\/granular_data\/navigation_targets\/\d+\/ct_characteristics$/,
    options: ["Solid", "Part-solid", "Ground-glass", "Cavitary", "Calcified"],
  },
  {
    pattern: /^\/registry\/granular_data\/navigation_targets\/\d+\/bronchus_sign$/,
    options: ["Positive", "Negative", "Not assessed"],
  },
  {
    pattern: /^\/registry\/granular_data\/navigation_targets\/\d+\/rebus_view$/,
    options: ["Concentric", "Eccentric", "Adjacent", "Not visualized"],
  },
  {
    pattern: /^\/registry\/granular_data\/navigation_targets\/\d+\/confirmation_method$/,
    options: ["CBCT", "Augmented fluoroscopy", "Fluoroscopy", "Radial EBUS", "None"],
  },
  {
    pattern: /^\/registry\/granular_data\/linear_ebus_stations_detail\/\d+\/needle_gauge$/,
    options: [19, 21, 22, 25],
  },
];

function getDropdown(pointer: string): Array<string | number> | null {
  const exact = DROPDOWNS_BY_POINTER[pointer];
  if (exact) return exact;
  for (const item of DROPDOWN_PATTERNS) {
    if (item.pattern.test(pointer)) return item.options;
  }
  return null;
}

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

function hasEditedValue(row: RegistryRow): boolean {
  return row.editedValueRaw !== null && row.editedValueRaw !== undefined;
}

function isEditableValueType(valueType: ValueType): boolean {
  return valueType === "null" || valueType === "boolean" || valueType === "number" || valueType === "string";
}

type NullEditKind = "text" | "number" | "boolean";

function inferNullEditKind(value: unknown): NullEditKind {
  if (typeof value === "boolean") return "boolean";
  if (typeof value === "number") return "number";
  return "text";
}

type NullEditCellProps = {
  row: RegistryRow;
  onEditValue?: (row: RegistryRow, nextValue: unknown) => void;
  onClearEdit?: (row: RegistryRow) => void;
};

function NullEditCell({ row, onEditValue, onClearEdit }: NullEditCellProps) {
  const edited = row.editedValueRaw;
  const hasEdit = edited !== null && edited !== undefined;
  const disabled = !onEditValue;

  const [kind, setKind] = useState<NullEditKind>(() => inferNullEditKind(hasEdit ? edited : null));

  const commit = (nextValue: unknown) => {
    if (!onEditValue) return;
    onEditValue(row, nextValue);
  };

  const revert = () => onClearEdit?.(row);

  if (kind === "boolean") {
    let current = "";
    if (hasEdit) {
      if (typeof edited === "boolean") current = edited ? "true" : "false";
      else if (typeof edited === "string") {
        const normalized = edited.trim().toLowerCase();
        if (normalized === "true" || normalized === "yes") current = "true";
        else if (normalized === "false" || normalized === "no") current = "false";
      } else if (typeof edited === "number") {
        if (Number.isFinite(edited)) current = edited === 0 ? "false" : "true";
      }
    }
    return (
      <div className="ps-edit-cell">
        <select
          className="ps-edit-select"
          value={kind}
          onChange={(e) => setKind(e.target.value as NullEditKind)}
          disabled={disabled}
          title="Type"
        >
          <option value="text">Text</option>
          <option value="number">Number</option>
          <option value="boolean">Yes/No</option>
        </select>
        <select
          className={hasEdit ? "ps-edit-select ps-edited" : "ps-edit-select"}
          value={current}
          onChange={(e) => {
            const v = String(e.target.value || "");
            if (!v) {
              revert();
              return;
            }
            commit(v === "true");
          }}
          disabled={disabled}
          title="Set value"
        >
          <option value="">—</option>
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

  if (kind === "number") {
    const current = hasEdit ? String(edited ?? "") : "";
    return (
      <div className="ps-edit-cell">
        <select
          className="ps-edit-select"
          value={kind}
          onChange={(e) => setKind(e.target.value as NullEditKind)}
          disabled={disabled}
          title="Type"
        >
          <option value="text">Text</option>
          <option value="number">Number</option>
          <option value="boolean">Yes/No</option>
        </select>
        <input
          key={`${row.id}:null:num:${current}`}
          className={hasEdit ? "ps-edit-input ps-edited" : "ps-edit-input"}
          type="number"
          inputMode="decimal"
          defaultValue={current}
          placeholder=""
          onBlur={(e) => {
            const text = String((e.target as HTMLInputElement).value || "").trim();
            if (!text) {
              revert();
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
          disabled={disabled}
        />
        {hasEdit ? (
          <button type="button" className="ps-edit-revert" onClick={revert} title="Revert edit">
            ↩
          </button>
        ) : null}
      </div>
    );
  }

  const current = hasEdit ? String(edited ?? "") : "";
  return (
    <div className="ps-edit-cell">
      <select
        className="ps-edit-select"
        value={kind}
        onChange={(e) => setKind(e.target.value as NullEditKind)}
        disabled={disabled}
        title="Type"
      >
        <option value="text">Text</option>
        <option value="number">Number</option>
        <option value="boolean">Yes/No</option>
      </select>
      <input
        key={`${row.id}:null:text:${current}`}
        className={hasEdit ? "ps-edit-input ps-edited" : "ps-edit-input"}
        type="text"
        defaultValue={current}
        placeholder=""
        onBlur={(e) => {
          const text = String((e.target as HTMLInputElement).value ?? "");
          if (!text.trim()) {
            revert();
            return;
          }
          commit(text);
        }}
        onKeyDown={(e) => {
          if (e.key !== "Enter") return;
          (e.target as HTMLInputElement).blur();
        }}
        disabled={disabled}
      />
      {hasEdit ? (
        <button type="button" className="ps-edit-revert" onClick={revert} title="Revert edit">
          ↩
        </button>
      ) : null}
    </div>
  );
}

function deriveVisibleRows(
  rows: RegistryRow[],
  index: TreeIndex,
  fieldMode: FieldMode,
  collapsedIds: Set<string>,
  editedIds: Set<string>,
): RegistryRow[] {
  const included = new Set<string>();

  if (fieldMode === "all") {
    rows.forEach((r) => included.add(r.id));
  } else if (fieldMode === "edited") {
    editedIds.forEach((id) => included.add(id));
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
  const [fieldMode, setFieldMode] = useState<FieldMode>("populated");
  const [collapsedIds, setCollapsedIds] = useState<Set<string>>(() => new Set());

  const treeIndex = useMemo(() => buildTreeIndex(rows), [rows]);
  const editedIds = useMemo(() => {
    const set = new Set<string>();
    for (const row of rows) {
      if (!hasEditedValue(row)) continue;
      set.add(row.id);
      let parent = treeIndex.parentById.get(row.id) ?? null;
      while (parent) {
        set.add(parent);
        parent = treeIndex.parentById.get(parent) ?? null;
      }
    }
    return set;
  }, [rows, treeIndex.parentById]);

  const visibleRows = useMemo(
    () => deriveVisibleRows(rows, treeIndex, fieldMode, collapsedIds, editedIds),
    [rows, treeIndex, fieldMode, collapsedIds, editedIds],
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

  const applyQuickFilter = useCallback((value: string) => {
    const api = gridRef.current?.api;
    if (!api) return;
    // ag-Grid API surface has shifted across versions; support both.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const anyApi = api as any;
    if (typeof anyApi.setQuickFilter === "function") anyApi.setQuickFilter(value);
    else if (typeof anyApi.setGridOption === "function") anyApi.setGridOption("quickFilterText", value);
  }, []);

  useEffect(() => {
    const handle = window.setTimeout(() => applyQuickFilter(quickFilter), 180);
    return () => window.clearTimeout(handle);
  }, [quickFilter, applyQuickFilter]);

  useEffect(() => {
    // Avoid a blank grid if the user is in "Only edited" mode and clears edits.
    if (fieldMode === "edited" && !editCount) setFieldMode("populated");
  }, [fieldMode, editCount]);

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
          const isEdited = editedIds.has(row.id);
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
              {isEdited ? <span className="ps-edit-badge">edited</span> : null}
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

          const dropdown = DROPDOWNS_BY_POINTER[row.jsonPointer];
          const dropdownOrPattern = dropdown ?? getDropdown(row.jsonPointer);
          if (dropdownOrPattern) {
            const currentRaw = hasEdit ? edited : extracted;
            const current = currentRaw === null || currentRaw === undefined ? "" : String(currentRaw);
            const wantsNumber = dropdownOrPattern.length > 0 && typeof dropdownOrPattern[0] === "number";
            return (
              <div className="ps-edit-cell">
                <select
                  className={hasEdit ? "ps-edit-select ps-edited" : "ps-edit-select"}
                  value={current}
                  onChange={(e) => {
                    const v = String(e.target.value || "");
                    if (!v) {
                      if (hasEdit) revert();
                      return;
                    }
                    commit(wantsNumber ? Number(v) : v);
                  }}
                  disabled={!onEditValue}
                >
                  <option value="">—</option>
                  {dropdownOrPattern.map((opt) => (
                    <option key={String(opt)} value={String(opt)}>
                      {String(opt)}
                    </option>
                  ))}
                </select>
                {hasEdit ? (
                  <button type="button" className="ps-edit-revert" onClick={revert} title="Revert edit">
                    ↩
                  </button>
                ) : null}
              </div>
            );
          }

          if (valueType === "null") {
            return <NullEditCell key={row.id} row={row} onEditValue={onEditValue} onClearEdit={onClearEdit} />;
          }

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
    [treeIndex.childrenById, isCollapsed, toggleCollapse, onEvidenceClick, onEditValue, onClearEdit, editedIds],
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
            onChange={(e) => setQuickFilter(e.target.value)}
            placeholder="Filter…"
            aria-label="Quick filter"
          />
          <div className="ps-toggle-group" role="group" aria-label="Field visibility">
            <button
              type="button"
              className={fieldMode === "populated" ? "ps-toggle active" : "ps-toggle"}
              onClick={() => setFieldMode("populated")}
            >
              Only populated
            </button>
            <button
              type="button"
              className={fieldMode === "edited" ? "ps-toggle active" : "ps-toggle"}
              onClick={() => setFieldMode("edited")}
              disabled={!editCount}
              title={!editCount ? "No edits yet" : "Show only edited fields"}
            >
              Only edited
            </button>
            <button
              type="button"
              className={fieldMode === "all" ? "ps-toggle active" : "ps-toggle"}
              onClick={() => setFieldMode("all")}
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
          getRowClass={(p) => (p.data && editedIds.has(p.data.id) ? "ps-row-edited" : "")}
          headerHeight={34}
          rowHeight={34}
          animateRows={false}
        />
      </div>
    </div>
  );
}
