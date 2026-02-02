export type EvidenceSpan = {
  source: string;
  text: string;
  span: [number, number];
  confidence?: number | null;
};

export type ValueType = "null" | "boolean" | "number" | "string" | "array" | "object" | "unknown";

export type RegistryRow = {
  id: string;
  jsonPointer: string;
  pathSegments: string[];
  depth: number;
  fieldLabel: string;
  extractedValueRaw: unknown;
  extractedValueDisplay: string;
  editedValueRaw: unknown | null;
  editedValueDisplay: string | null;
  valueType: ValueType;
  evidence: EvidenceSpan[];
  isGroup: boolean;
  parentId: string | null;
};

