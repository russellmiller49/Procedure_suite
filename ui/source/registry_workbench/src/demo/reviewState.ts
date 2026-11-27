/** A reviewer's confirmations and corrections, held in this browser tab only. */
import type {Values} from "../types";
import {isNegative, show, type FieldInput, type FieldState, type FieldView, type RowView, type SectionView} from "./fields";

export type Decision =
  | {status: "confirmed"}
  | {status: "corrected"; value: unknown}
  | {status: "added"; value: unknown}
  | {status: "removed"};
/** Decisions by field path, and the keys of rows the reviewer removed whole. */
export type Review = {decisions: Record<string, Decision>; removedRows: string[]};
export const EMPTY_REVIEW: Review = {decisions: {}, removedRows: []};

const RECORDED: FieldState[] = ["value", "negative", "stated_missing", "conflict"];
export const isRecorded = (field: FieldView) => RECORDED.includes(field.state);

/** Set, replace or (with null) undo the decision on one field. */
export function decide(review: Review, path: string, decision: Decision | null): Review {
  const decisions = {...review.decisions};
  if (decision) decisions[path] = decision;
  else delete decisions[path];
  return {...review, decisions};
}

export function toggleRow(review: Review, rowKey: string): Review {
  const removed = review.removedRows.includes(rowKey);
  return {...review, removedRows: removed ? review.removedRows.filter(k => k !== rowKey) : [...review.removedRows, rowKey]};
}

/** Confirm every recorded value of a row that has no decision yet. An unresolved field is never confirmed. */
export function confirmRow(review: Review, row: RowView): Review {
  const decisions = {...review.decisions};
  for (const field of row.fields) {
    if ((field.state === "value" || field.state === "negative" || field.state === "stated_missing") && !decisions[field.path]) {
      decisions[field.path] = {status: "confirmed"};
    }
  }
  return {...review, decisions};
}

export type ReviewCounts = {confirmed: number; corrected: number; removed: number; added: number; rowsRemoved: number; total: number; reviewed: number};

/** Progress over the recorded values of the rows the reviewer kept. */
export function countReview(review: Review, sections: SectionView[]): ReviewCounts {
  const counts: ReviewCounts = {confirmed: 0, corrected: 0, removed: 0, added: 0, rowsRemoved: review.removedRows.length, total: 0, reviewed: 0};
  const removed = new Set(review.removedRows);
  for (const section of sections) {
    for (const row of section.rows) {
      if (removed.has(row.key)) continue;
      for (const field of row.fields) {
        const decision = review.decisions[field.path];
        if (decision?.status === "added") counts.added += 1;
        if (!isRecorded(field)) continue;
        counts.total += 1;
        if (!decision) continue;
        counts.reviewed += 1;
        if (decision.status !== "added") counts[decision.status] += 1;
      }
    }
  }
  return counts;
}

/** True when the review changed the record itself (a confirmation alone changes nothing). */
export function changesRecord(review: Review): boolean {
  return review.removedRows.length > 0 || Object.values(review.decisions).some(d => d.status !== "confirmed");
}

/** How a field reads once the reviewer's decision is applied. */
export function reviewedDisplay(field: FieldView, decision: Decision | undefined): {state: FieldState; display: string} {
  if (decision?.status === "corrected" || decision?.status === "added") {
    return {state: isNegative(decision.value) ? "negative" : "value", display: show(decision.value)};
  }
  return {state: field.state, display: field.display};
}

/** Turn what the reviewer typed into a contract value, or say why it cannot be one. */
export function parseInput(input: FieldInput, raw: string): {ok: true; value: unknown} | {ok: false; message: string} {
  const text = raw.trim();
  if (!text) return {ok: false, message: "Enter a value."};
  if (input.kind === "enum") return input.options.includes(text) ? {ok: true, value: text} : {ok: false, message: "Choose one of the listed values."};
  if (input.kind === "boolean") return text === "true" || text === "false" ? {ok: true, value: text === "true"} : {ok: false, message: "Choose yes or no."};
  if (input.kind === "integer" || input.kind === "number") {
    const number = Number(text);
    if (!Number.isFinite(number)) return {ok: false, message: "Enter a number."};
    if (input.kind === "integer" && !Number.isInteger(number)) return {ok: false, message: "Enter a whole number."};
    return {ok: true, value: number};
  }
  return {ok: true, value: text};
}

/**
 * The record with the review applied: corrected and added values set, removed values blanked,
 * removed rows dropped, and the supporting passages kept in step with the rows that remain.
 */
export function reviewedRecord(proposal: Values, review: Review): Values {
  const out: Values = structuredClone(proposal);
  let provenance: Values[] = out.field_provenance || [];
  const setAt = (path: string, value: unknown) => {
    const parts = path.split("/").filter(Boolean);
    if (parts.length === 1) out[parts[0]] = value;
    else if (parts.length === 2) out[parts[0]] = {...(out[parts[0]] || {}), [parts[1]]: value};
    else if (out[parts[0]]?.[Number(parts[1])]) out[parts[0]][Number(parts[1])][parts[2]] = value;
  };
  for (const [path, decision] of Object.entries(review.decisions)) {
    if (decision.status === "confirmed") continue;
    if (decision.status === "removed") {
      setAt(path, null);
      provenance = provenance.filter(p => p.field_path !== path);
      continue;
    }
    setAt(path, decision.value);
    const entry = provenance.find(p => p.field_path === path);
    if (entry) {
      // The reviewer settled it: the passage stays as where the fact was read from.
      entry.conflict_status = "none";
      entry.value_origin = "reviewer";
      delete entry.missingness_reason;
    }
  }
  const removed = new Set(review.removedRows);
  for (const [collection, rows] of Object.entries(out)) {
    if (!Array.isArray(rows) || collection === "field_provenance") continue;
    const moved = new Map<number, number>();
    const kept: unknown[] = [];
    rows.forEach((row, index) => {
      if (removed.has(`/${collection}/${index}`)) return;
      moved.set(index, kept.length);
      kept.push(row);
    });
    if (kept.length === rows.length) continue;
    out[collection] = kept;
    provenance = provenance.flatMap(p => {
      const parts = String(p.field_path || "").split("/").filter(Boolean);
      if (parts[0] !== collection || parts.length < 2) return [p];
      const next = moved.get(Number(parts[1]));
      return next === undefined ? [] : [{...p, field_path: "/" + [collection, next, ...parts.slice(2)].join("/")}];
    });
  }
  out.field_provenance = provenance;
  return out;
}
