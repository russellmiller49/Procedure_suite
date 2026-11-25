/** Read-only view model: every contract field of every extracted row, with an honest state. */
import {KEYS, label} from "../review";
import type {Profile, Schema, Values} from "../types";

export type FieldState = "value" | "negative" | "stated_missing" | "conflict" | "not_extracted";
export type FieldView = {
  path: string;
  name: string;
  state: FieldState;
  display: string;
  units?: string;
  definition?: string;
  quote?: string;
  span?: [number, number];
  derived: boolean;
};
export type RowView = {key: string; title: string; fields: FieldView[]; extracted: number};
export type SectionView = {collection: string; title: string; rows: RowView[]};

const HIDDEN = new Set([
  "target_identity_id", "operator_id", "source_document_id", "adverse_event_id",
  "run_sequence_number", "event_sequence_number", "pass_sequence_number",
]);
export const SECTION_ORDER = [
  "procedures", "case_details", "targets", "ebus_sessions", "station_surveys", "navigation_runs",
  "localization_events", "sampling_acquisitions", "specimens", "sampling_specimen_links", "complications",
];

export const STATE_LABEL: Record<FieldState, string> = {
  value: "",
  negative: "",
  stated_missing: "Stated in the note as",
  conflict: "Unclear, needs review",
  not_extracted: "Not extracted",
};

function resolve(schema: Schema, s: Schema): Schema {
  if (s?.$ref) return resolve(schema, schema.$defs[s.$ref.split("/").at(-1)]);
  if (s?.anyOf) return resolve(schema, s.anyOf.find((x: Schema) => x.type !== "null") || {});
  return s || {};
}

const ACRONYMS: Record<string, string> = {
  iaslc: "IASLC", rose: "ROSE", pet: "PET", suv: "SUV", asa: "ASA", ebus: "EBUS", eus: "EUS", icu: "ICU", til: "TIL", ct: "CT", cbct: "CBCT",
};
const UNIT_SUFFIX = /_(mm|years|minutes)$/;

/** "max_diameter_mm" -> "Max diameter" (units are shown beside the value); acronyms keep their case. */
export function fieldLabel(name: string, units?: string): string {
  const base = units ? name.replace(UNIT_SUFFIX, "") : name;
  const words = base.split("_").map(w => ACRONYMS[w] || w);
  const text = words.join(" ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export function show(value: unknown): string {
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "string") return /^[a-z0-9_]+$/.test(value) ? label(value) : value;
  return String(value);
}

/** Short human name for a row, from what a reviewer would call it. */
export function rowTitle(collection: string, row: Values, index: number, all: Values): string {
  const target = (id: unknown) => {
    const t = (all.targets || []).find((x: Values) => x.target_id === id);
    if (!t) return "";
    if (t.site === "lymph_node") return `station ${t.iaslc_station ?? "?"}`;
    return [t.anatomic_label, t.lobe].filter(Boolean).join(", ") || label(t.site || "target");
  };
  switch (collection) {
    case "procedures": return label(row.category || `component ${index + 1}`);
    case "targets":
      return row.site === "lymph_node" ? `Lymph node, station ${row.iaslc_station ?? "?"}` : `${label(row.site || "target")}: ${target(row.target_id) || index + 1}`;
    case "station_surveys": return `Station ${row.iaslc_station ?? "?"}`;
    case "ebus_sessions": return "Linear EBUS examination";
    case "navigation_runs": return `Navigation to ${target(row.target_id) || "target"}`;
    case "localization_events": return `${label(row.localization_modality || "localization")} at ${target(row.target_id) || "target"}`;
    case "sampling_acquisitions": return `${label(row.sampling_tool || "sampling")} of ${target(row.target_id) || "an unattributed target"}`;
    case "specimens": return `Specimen ${row.specimen_label ?? index + 1}`;
    case "sampling_specimen_links": {
      const pass = (all.sampling_acquisitions || []).find((a: Values) => a.sampling_pass_id === row.sampling_pass_id);
      const specimen = (all.specimens || []).find((s: Values) => s.specimen_id === row.specimen_id);
      return `${label(pass?.sampling_tool || "sampling")} → specimen ${specimen?.specimen_label ?? "?"}`;
    }
    case "complications": return label(row.category || `event ${index + 1}`);
    default: return `${label(collection)} ${index + 1}`;
  }
}

function fieldView(profile: Profile, proposal: Values, collection: string, path: string, name: string, value: unknown): FieldView {
  const help = profile.help[`${collection}.${name}`] || {};
  const prov = (proposal.field_provenance || []).find((p: Values) => p.field_path === path);
  const span = prov?.source_start != null ? ([prov.source_start, prov.source_end] as [number, number]) : undefined;
  const base = {path, name, units: help.units, definition: help.definition, quote: prov?.source_excerpt, span, derived: prov?.value_origin === "derived"};
  if (prov?.conflict_status === "unresolved") {
    return {...base, state: "conflict", display: prov.raw_value ? String(prov.raw_value) : ""};
  }
  if (value == null) {
    if (prov?.missingness_reason) return {...base, state: "stated_missing", display: label(prov.missingness_reason)};
    return {...base, state: "not_extracted", display: ""};
  }
  const negative = value === false || prov?.assertion_context === "negated" || value === "absent" || value === "not_performed";
  return {...base, state: negative ? "negative" : "value", display: show(value)};
}

/** Sections with one entry per extracted row; fields the extractor left blank are kept, marked. */
export function buildSections(profile: Profile, proposal: Values | null): SectionView[] {
  if (!proposal) return [];
  const schema = profile.schema;
  const out: SectionView[] = [];
  for (const collection of SECTION_ORDER) {
    const property = schema.properties[collection];
    if (!property) continue;
    const singleton = collection === "case_details";
    const entity = resolve(schema, singleton ? property : resolve(schema, property).items);
    const rows: Values[] = singleton ? [proposal.case_details || {}] : proposal[collection] || [];
    const views: RowView[] = rows.map((row, index) => {
      const prefix = singleton ? `/${collection}` : `/${collection}/${index}`;
      const fields = Object.keys(entity.properties || {})
        .filter(name => name !== KEYS[collection] && !HIDDEN.has(name) && !name.endsWith("_id"))
        .map(name => fieldView(profile, proposal, collection, `${prefix}/${name}`, name, row[name]));
      return {
        key: prefix,
        title: singleton ? "Case and anesthesia" : rowTitle(collection, row, index, proposal),
        fields,
        extracted: fields.filter(f => f.state !== "not_extracted").length,
      };
    });
    out.push({collection, title: profile.sections[collection] || label(collection), rows: views});
  }
  return out;
}

export function countStates(sections: SectionView[]): Record<FieldState, number> {
  const counts: Record<FieldState, number> = {value: 0, negative: 0, stated_missing: 0, conflict: 0, not_extracted: 0};
  for (const section of sections) for (const row of section.rows) for (const field of row.fields) counts[field.state] += 1;
  return counts;
}

/** A stored span is trusted only if the excerpt is really at that place in the text on screen. */
export function verifiedSpan(text: string, span?: [number, number], quote?: string): [number, number] | null {
  if (!span) return null;
  if (quote == null || text.slice(span[0], span[1]) === quote) return span;
  const found = text.indexOf(quote);
  return found >= 0 ? [found, found + quote.length] : null;
}
