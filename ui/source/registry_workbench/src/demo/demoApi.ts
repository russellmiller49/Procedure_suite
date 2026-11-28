import type {Profile, Values} from "../types";
import type {Comparison} from "../Compare";
import type {RulesAgreement} from "./fields";

export type SampleSummary = {
  id: string;
  title: string;
  teaching_point: string;
  platform: string | null;
  components: string[];
  style: string | null;
  traps: string[];
  chars: number;
  has_result: boolean;
};
export type SampleDetail = SampleSummary & {text: string; reviewed_redactions: {worker: string | null; text: string}[]};
export type DemoConfig = {
  enabled: boolean;
  notice: string;
  placeholder: string;
  max_text_chars: number;
  live_extraction: {enabled: boolean; reason: string | null};
  samples: SampleSummary[];
  profile: Profile;
};
export type Mention = {kind: string; note: string; start?: number; end?: number; excerpt?: string};
export type Side = {
  status: string | null;
  warnings: string[];
  proposal: Values | null;
  unresolved_mentions: Mention[];
  quality_signals: Values[];
  inference: Values;
};
export type CodeEvidence = {label: string; derived_from: string[]; quote?: string; start?: number; end?: number; reason?: string};
export type SuggestedCode = {
  code: string;
  description: string | null;
  units: number | null;
  modifiers: string[];
  role: string | null;
  rationale: string | null;
  evidence: CodeEvidence[];
  excluded: CodeEvidence[];
  review_flags: string[];
  needs_review: boolean;
};
export type Codes = {
  title: string;
  codes: SuggestedCode[];
  dropped: {code: string; reason: string | null}[];
  review_flags: {flag: string; message: string; codes: string[]}[];
  excluded: Record<string, CodeEvidence[]>;
  not_assessed: {codes: string[]; label: string; reason: string}[];
  scope_note: string;
};
export type NoteKind = "synthetic" | "real_redacted";
/** Whether the model read a tester's note and, if not, why. */
export type Reader = {model_used: boolean; sent_to_provider: boolean; reason: string | null; message: string | null};
export type TesterAccess = {
  ok: boolean;
  model_configured: boolean;
  real_notes_to_model: boolean;
  model: string;
  effort: string;
  provider: string;
  max_text_chars: number;
};
export type LiveParams = {access_code: string; note_kind: NoteKind; attested: boolean};
export type ExtractResult = {
  status: string;
  source: string;
  source_label: string;
  sample_id: string | null;
  generated_at: string | null;
  notice: string;
  /** Which reading the fields and codes come from. */
  primary?: "llm" | "rules";
  note_kind?: NoteKind;
  reader?: Reader;
  llm: Side | null;
  rules: Side | null;
  comparison: Comparison & {summary: Record<string, number>};
  rules_agreement?: RulesAgreement;
  codes: Codes | null;
};

export class DemoApiError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message);
  }
}

async function call<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch("/api/v1/demo/robotic-ebus" + path, {
    method: body === undefined ? "GET" : "POST",
    cache: "no-store",
    headers: body === undefined ? {} : {"Content-Type": "application/json"},
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = (await response.json().catch(() => ({}))).detail;
    const code = typeof detail === "object" && detail?.code ? detail.code : `http_${response.status}`;
    const message = typeof detail === "object" && detail?.message ? detail.message : "The demo service did not answer.";
    throw new DemoApiError(response.status, code, message);
  }
  return response.json();
}

export const getConfig = () => call<DemoConfig>("/config");
export const getSample = (id: string) => call<SampleDetail>(`/samples/${encodeURIComponent(id)}`);
export const extract = (text: string, sampleId: string | null, live?: LiveParams) =>
  call<ExtractResult>("/extract", {text, sample_id: sampleId, ...(live || {})});
export const unlock = (accessCode: string) => call<TesterAccess>("/unlock", {access_code: accessCode});
/** Codes for a record as corrected by the reviewer. The note text is not sent. */
export const recode = (proposal: Values, unresolved: Mention[]) => call<Codes>("/codes", {proposal, unresolved});
