import type {Values} from "./types";

export const KEYS: Record<string, string> = {
  targets: "target_id",
  ebus_sessions: "ebus_session_id",
  station_surveys: "station_survey_id",
  navigation_runs: "navigation_run_id",
  localization_events: "localization_event_id",
  sampling_acquisitions: "sampling_pass_id",
  specimens: "specimen_id",
  sampling_specimen_links: "sampling_specimen_link_id",
  pathology_results: "pathology_result_id",
  complications: "adverse_event_id",
};
export const REFERENCES: Record<string, string> = {
  target_id: "targets",
  ebus_session_id: "ebus_sessions",
  station_survey_id: "station_surveys",
  navigation_run_id: "navigation_runs",
  localization_event_id_before_pass: "localization_events",
  sampling_pass_id: "sampling_acquisitions",
  specimen_id: "specimens",
  supersedes_pathology_result_id: "pathology_results",
};
export const MISSING = [
  "not_documented", "unknown", "not_done", "not_applicable", "pending",
  "technical_failure", "patient_declined", "not_available_at_site", "lost_to_followup",
];
export const COLLECTIONS = [
  "procedures", "case_details", "targets", "ebus_sessions", "station_surveys", "navigation_runs",
  "localization_events", "sampling_acquisitions", "specimens", "sampling_specimen_links",
  "pathology_results", "complications", "follow_up",
];

export const label = (s: string) => s.replaceAll("_", " ");

export function fresh(eventDate = ""): Values {
  return {
    schema_version: "0.2.0",
    registry_profile: "robotic_ebus_v1",
    event_date: eventDate,
    case_details: {},
    procedures: [{category: "robotic_bronchoscopy", performance: "not_documented", planned: null, completion: null}],
    ...Object.fromEntries(COLLECTIONS.filter(c => !["case_details", "procedures"].includes(c)).map(c => [c, []])),
    complication_assessment: "not_documented",
    evidence: [],
    field_provenance: [],
    suggested_codes: [],
    manual_fields: [],
  };
}

/** A draft seeded from an extraction proposal; proposals carry no event date. */
export function fromProposal(proposal: Values, eventDate: string | null): Values {
  const base = fresh(eventDate || "");
  const draft: Values = {...base, ...structuredClone(proposal), event_date: eventDate || ""};
  for (const collection of COLLECTIONS) if (draft[collection] == null) draft[collection] = base[collection];
  if (!draft.procedures.length) draft.procedures = base.procedures;
  return draft;
}

export function provenanceFor(values: Values, path: string): Values | undefined {
  return (values.field_provenance || []).find((p: Values) => p.field_path === path);
}

export type Segment = {text: string; start: number; mark: "none" | "evidence" | "focus"};

/** Split text into runs so evidence spans can be rendered as <mark> without reflowing offsets. */
export function segments(text: string, spans: [number, number][], focus?: [number, number] | null): Segment[] {
  const boundaries = new Set<number>([0, text.length]);
  const ranges = spans.filter(([s, e]) => e > s && s >= 0 && e <= text.length);
  if (focus) ranges.push(focus);
  for (const [s, e] of ranges) {
    boundaries.add(s);
    boundaries.add(e);
  }
  const points = [...boundaries].sort((a, b) => a - b);
  const out: Segment[] = [];
  for (let i = 0; i < points.length - 1; i++) {
    const [start, end] = [points[i], points[i + 1]];
    const inFocus = focus && start >= focus[0] && end <= focus[1];
    const inEvidence = spans.some(([s, e]) => start >= s && end <= e);
    out.push({text: text.slice(start, end), start, mark: inFocus ? "focus" : inEvidence ? "evidence" : "none"});
  }
  return out;
}

export function evidenceSpans(values: Values | null, documentId: string): [number, number][] {
  if (!values) return [];
  return (values.field_provenance || [])
    .filter((p: Values) => p.source_document_id === documentId && p.source_start != null)
    .map((p: Values) => [p.source_start, p.source_end] as [number, number]);
}
