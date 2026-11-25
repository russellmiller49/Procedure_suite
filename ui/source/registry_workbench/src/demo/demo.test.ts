import {describe, expect, it} from "vitest";
import profile from "../__fixtures__/profile.json";
import type {Profile} from "../types";
import {buildSections, countStates, show, verifiedSpan} from "./fields";
import {applyRedactions, mergeSpans, PLACEHOLDER, readDetections, ScanGate, type Detection} from "./phiRedaction";

const det = (id: string, start: number, end: number): Detection => ({id, start, end, label: "PATIENT", score: 0.9, source: "auto"});

describe("redaction replacement", () => {
  const text = "Patient: Marian Delacroix. MRN: 00481516. Station 7 was sampled.";

  it("writes one fixed placeholder and leaves the rest of the note byte-identical", () => {
    const out = applyRedactions(text, [det("a", 9, 25), det("b", 32, 40)], new Set());
    expect(out).toBe(`Patient: ${PLACEHOLDER}. MRN: ${PLACEHOLDER}. Station 7 was sampled.`);
    expect(PLACEHOLDER).toBe("[REDACTED]");
  });

  it("merges overlapping and touching detections into one placeholder", () => {
    expect(mergeSpans([[9, 15], [12, 25], [25, 26], [40, 30], [0, 999]], text.length)).toEqual([[9, 26]]);
    const out = applyRedactions(text, [det("a", 9, 15), det("b", 12, 25)], new Set());
    expect(out.split(PLACEHOLDER)).toHaveLength(2);
  });

  it("leaves an excluded detection untouched", () => {
    const out = applyRedactions(text, [det("a", 9, 25), det("b", 32, 40)], new Set(["a"]));
    expect(out).toContain("Marian Delacroix");
    expect(out).not.toContain("00481516");
  });

  it("gives every detection an id and drops malformed ones", () => {
    const read = readDetections([{start: 1, end: 4, label: "ID"}, {start: 5, end: 5}, {start: "x", end: 9}, null]);
    expect(read).toHaveLength(1);
    expect(read[0].id).toBeTruthy();
    expect(readDetections("nope")).toEqual([]);
  });
});

describe("scan gate", () => {
  it("allows extraction only after a completed scan is applied to the current text", () => {
    const gate = new ScanGate();
    gate.textChanged();
    expect(gate.readyToExtract).toBe(false);
    const scan = gate.begin();
    expect(gate.accept(scan)).toBe(true);
    expect(gate.readyToExtract).toBe(false);
    gate.markApplied();
    expect(gate.readyToExtract).toBe(true);
  });

  it("rejects the partial result a cancelled scan still reports", () => {
    const gate = new ScanGate();
    gate.textChanged();
    const scan = gate.begin();
    gate.cancel();
    expect(gate.accept(scan)).toBe(false);
    expect(gate.scanComplete).toBe(false);
    expect(() => gate.markApplied()).toThrow();
  });

  it("rejects a result for text that changed while the scan ran, and an older scan", () => {
    const gate = new ScanGate();
    gate.textChanged();
    const first = gate.begin();
    gate.textChanged();
    expect(gate.accept(first)).toBe(false);
    const second = gate.begin();
    const third = gate.begin();
    expect(gate.accept(second)).toBe(false);
    expect(gate.accept(third)).toBe(true);
  });

  it("invalidates an applied review when the text is edited or the sample is switched", () => {
    const gate = new ScanGate();
    gate.textChanged();
    gate.accept(gate.begin());
    gate.markApplied();
    gate.textChanged();
    expect(gate.readyToExtract).toBe(false);
    gate.markReviewedText();
    expect(gate.readyToExtract).toBe(true);
  });
});

describe("field states", () => {
  const text = "Station 4R was sampled. Station 11L was not sampled. Pathology pending.";
  const proposal = {
    procedures: [{category: "linear_ebus", performance: "performed"}],
    case_details: {},
    ebus_sessions: [{ebus_session_id: "e"}],
    station_surveys: [
      {station_survey_id: "s1", ebus_session_id: "e", iaslc_station: "4R", station_sampled: true},
      {station_survey_id: "s2", ebus_session_id: "e", iaslc_station: "11L", station_sampled: false},
    ],
    targets: [{target_id: "t1", site: "lymph_node", iaslc_station: "4R", short_axis_mm: null, node_interpretation: null}],
    field_provenance: [
      {field_path: "/station_surveys/0/station_sampled", source_start: 0, source_end: 23, source_excerpt: "Station 4R was sampled.", conflict_status: "none", assertion_context: "active"},
      {field_path: "/station_surveys/1/station_sampled", source_start: 24, source_end: 52, source_excerpt: "Station 11L was not sampled.", conflict_status: "none", assertion_context: "negated"},
      {field_path: "/targets/0/node_interpretation", source_start: 53, source_end: 71, source_excerpt: "Pathology pending.", conflict_status: "none", missingness_reason: "pending"},
      {field_path: "/targets/0/short_axis_mm", conflict_status: "unresolved", raw_value: "[12, 14]"},
    ],
  };
  const sections = buildSections(profile as unknown as Profile, proposal);
  const field = (collection: string, row: number, name: string) =>
    sections.find(s => s.collection === collection)!.rows[row].fields.find(f => f.name === name)!;

  it("shows an explicit negative as No with its quote, never as a blank", () => {
    const sampled = field("station_surveys", 1, "station_sampled");
    expect(sampled.state).toBe("negative");
    expect(sampled.display).toBe("No");
    expect(text.slice(...sampled.span!)).toBe(sampled.quote);
  });

  it("calls a blank Not extracted and never renders it as No", () => {
    const blank = field("station_surveys", 0, "station_visualized");
    expect(blank.state).toBe("not_extracted");
    expect(blank.display).toBe("");
    const all = sections.flatMap(s => s.rows.flatMap(r => r.fields));
    expect(all.filter(f => f.state === "not_extracted").every(f => f.display === "")).toBe(true);
  });

  it("separates stated-missing and unresolved conflicts from blanks", () => {
    expect(field("targets", 0, "node_interpretation")).toMatchObject({state: "stated_missing", display: "pending"});
    expect(field("targets", 0, "short_axis_mm")).toMatchObject({state: "conflict", display: "[12, 14]"});
    const counts = countStates(sections);
    expect(counts.conflict).toBe(1);
    expect(counts.stated_missing).toBe(1);
    expect(counts.negative).toBe(1);
  });

  it("names rows the way a reviewer would and hides identifiers", () => {
    const rows = sections.find(s => s.collection === "station_surveys")!.rows;
    expect(rows.map(r => r.title)).toEqual(["Station 4R", "Station 11L"]);
    expect(rows[0].fields.some(f => f.name.endsWith("_id"))).toBe(false);
    expect(show("part_solid")).toBe("part solid");
    expect(show("RUL")).toBe("RUL");
  });

  it("only trusts a span whose excerpt is really at that place", () => {
    expect(verifiedSpan(text, [0, 23], "Station 4R was sampled.")).toEqual([0, 23]);
    expect(verifiedSpan(text, [3, 26], "Station 4R was sampled.")).toEqual([0, 23]);
    expect(verifiedSpan(text, [0, 23], "not in the note")).toBeNull();
    expect(verifiedSpan(text, undefined, "x")).toBeNull();
  });
});

describe("field labels", () => {
  it("keeps acronyms, uses sentence case and drops a unit suffix only when units are shown", async () => {
    const {fieldLabel} = await import("./fields");
    expect(fieldLabel("iaslc_station")).toBe("IASLC station");
    expect(fieldLabel("max_diameter_mm", "mm")).toBe("Max diameter");
    expect(fieldLabel("max_diameter_mm")).toBe("Max diameter mm");
    expect(fieldLabel("rose_used")).toBe("ROSE used");
  });
});
