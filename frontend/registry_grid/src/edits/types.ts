export type JSONPatchOp =
  | { op: "replace"; path: string; value: unknown }
  | { op: "add"; path: string; value: unknown }
  | { op: "remove"; path: string };

export type RegistryGridEditsExport = {
  edited_source: "ui_registry_grid";
  edited_patch: JSONPatchOp[];
  edited_fields: Array<{
    path: string;
    field_label: string;
    value_type: string;
    extracted: unknown;
    edited: unknown;
    evidence?: unknown;
  }>;
};

