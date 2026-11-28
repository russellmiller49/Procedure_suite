import {describe, expect, it} from "vitest";
import profile from "../__fixtures__/profile.json";
import type {Profile} from "../types";
import {buildSections, countRules, countStates, show, verifiedSpan} from "./fields";
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

  it("marks a value the rules engine also extracted, and never a blank or an unresolved field", () => {
    const withRules = buildSections(profile as unknown as Profile, proposal, {
      "/station_surveys/0/station_sampled": {state: "agree", other_value: true},
      "/station_surveys/1/station_sampled": {state: "differ", other_value: true},
      "/station_surveys/0/station_visualized": {state: "agree", other_value: true},
      "/targets/0/short_axis_mm": {state: "differ", other_value: 12},
    });
    const at = (collection: string, row: number, name: string) =>
      withRules.find(s => s.collection === collection)!.rows[row].fields.find(f => f.name === name)!;
    expect(at("station_surveys", 0, "station_sampled").rules).toEqual({state: "agree", display: "Yes"});
    expect(at("station_surveys", 1, "station_sampled").rules).toEqual({state: "differ", display: "Yes"});
    expect(at("station_surveys", 0, "station_visualized").rules).toBeUndefined();
    expect(at("targets", 0, "short_axis_mm").rules).toBeUndefined();
    expect(countRules(withRules)).toEqual({agree: 1, differ: 1});
    expect(countRules(sections)).toEqual({agree: 0, differ: 0});
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

describe("set-aside statements", () => {
  it("shows one entry per passage with a plain reason and keeps the extractor notes", async () => {
    const {mentionsView} = await import("./fields");
    const text = "Prior EBUS in 2024. There was no pneumothorax on fluoroscopy.";
    const views = mentionsView(
      [
        {kind: "uncertain", note: "negated complications.category = 'pneumothorax'", start: 20, end: 61},
        {kind: "unmapped_detail", note: "complications C1 dropped: missing category", start: 20, end: 61},
        {kind: "historical", note: "station 7", start: 0, end: 19, excerpt: "Prior EBUS in 2024."},
      ],
      text,
    );
    expect(views).toHaveLength(2);
    expect(views[0]).toMatchObject({label: "Stated, but not recorded as a value", quote: "There was no pneumothorax on fluoroscopy.", span: [20, 61]});
    expect(views[0].notes).toHaveLength(2);
    expect(views[1].label).toBe("From the history, not this procedure");
  });
});

describe("display details from real results", () => {
  it("names specimens once and shows the overall complications answer with its quote", async () => {
    const {buildSections, specimenName} = await import("./fields");
    expect(specimenName("Specimen A", 0)).toBe("Specimen A");
    expect(specimenName("A", 0)).toBe("Specimen A");
    expect(specimenName(null, 2)).toBe("Specimen 3");
    const text = "Complications: none.";
    const sections = buildSections(profile as unknown as Profile, {
      procedures: [], case_details: {}, complications: [], complication_assessment: "absent",
      field_provenance: [{field_path: "/complication_assessment", source_start: 0, source_end: 20, source_excerpt: text, conflict_status: "none", assertion_context: "negated"}],
    });
    const overall = sections.find(s => s.collection === "complications")!.rows[0];
    expect(overall.title).toBe("Overall");
    expect(overall.fields[0]).toMatchObject({state: "negative", display: "absent", quote: text});
  });
});

describe("unlabelled specimens", () => {
  it("are told apart by their target, in the specimen row and in its link", async () => {
    const {rowTitle} = await import("./fields");
    const all = {
      targets: [{target_id: "t1", site: "lymph_node", iaslc_station: "4R"}, {target_id: "t2", site: "lymph_node", iaslc_station: "7"}],
      sampling_acquisitions: [{sampling_pass_id: "p2", sampling_tool: "aspiration_needle", target_id: "t2"}],
      specimens: [{specimen_id: "s1", target_id: "t1"}, {specimen_id: "s2", target_id: "t2"}],
    };
    expect(rowTitle("specimens", all.specimens[1], 1, all)).toBe("Specimen 2 (station 7)");
    expect(rowTitle("sampling_specimen_links", {sampling_pass_id: "p2", specimen_id: "s2"}, 0, all)).toBe("aspiration needle → Specimen 2 (station 7)");
    expect(rowTitle("specimens", {specimen_id: "s3", specimen_label: "Specimen C"}, 2, all)).toBe("Specimen C");
  });
});

describe("manual redaction", () => {
  it("lists a hand-picked span as a detection and replaces it like any other", async () => {
    const {manualDetection, redactSpan} = await import("./phiRedaction");
    const text = "Seen with Dr. Okonkwo-Reyes at the bedside. Station 7 was sampled.";
    const added = manualDetection(14, 27);
    expect(added).toMatchObject({source: "manual", start: 14, end: 27});
    expect(applyRedactions(text, [added], new Set())).toBe(`Seen with Dr. ${PLACEHOLDER} at the bedside. Station 7 was sampled.`);
    expect(redactSpan(text, [14, 27])).toBe(`Seen with Dr. ${PLACEHOLDER} at the bedside. Station 7 was sampled.`);
    expect(redactSpan(text, [70, 900])).toBe(text);
  });

  it("keeps the text cleared after a manual redaction, but only once redactions were applied", () => {
    const gate = new ScanGate();
    gate.textChanged();
    expect(() => gate.markManualEdit()).toThrow();
    gate.accept(gate.begin());
    gate.markApplied();
    gate.markManualEdit();
    expect(gate.readyToExtract).toBe(true);
    gate.textChanged();
    expect(gate.readyToExtract).toBe(false);
  });
});

describe("confirm and correct", () => {
  const proposal = {
    procedures: [{category: "linear_ebus", performance: "performed"}],
    case_details: {},
    ebus_sessions: [{ebus_session_id: "e"}],
    station_surveys: [
      {station_survey_id: "s1", ebus_session_id: "e", iaslc_station: "4R", station_sampled: true},
      {station_survey_id: "s2", ebus_session_id: "e", iaslc_station: "11L", station_sampled: true},
      {station_survey_id: "s3", ebus_session_id: "e", iaslc_station: "7", station_sampled: true},
    ],
    targets: [{target_id: "t1", site: "lymph_node", iaslc_station: "4R", short_axis_mm: null}],
    field_provenance: [
      {field_path: "/station_surveys/0/station_sampled", source_start: 0, source_end: 5, source_excerpt: "a", conflict_status: "none"},
      {field_path: "/station_surveys/1/station_sampled", source_start: 6, source_end: 9, source_excerpt: "b", conflict_status: "none"},
      {field_path: "/station_surveys/2/station_sampled", source_start: 10, source_end: 12, source_excerpt: "c", conflict_status: "none"},
      {field_path: "/targets/0/short_axis_mm", conflict_status: "unresolved", raw_value: "[12, 14]"},
    ],
  };
  const sections = buildSections(profile as unknown as Profile, proposal);
  const row = (collection: string, index: number) => sections.find(s => s.collection === collection)!.rows[index];

  it("gives every field the right kind of input", () => {
    const at = (collection: string, name: string) => row(collection, 0).fields.find(f => f.name === name)!;
    expect(at("station_surveys", "station_sampled").input).toEqual({kind: "boolean"});
    expect(at("targets", "short_axis_mm").input.kind).toBe("number");
    expect(at("station_surveys", "iaslc_station").input.kind).toMatch(/enum|text/);
    const site = at("targets", "site").input;
    expect(site.kind).toBe("enum");
    expect(site.kind === "enum" && site.options).toContain("lymph_node");
  });

  it("checks what the reviewer typed against the field type", async () => {
    const {parseInput} = await import("./reviewState");
    expect(parseInput({kind: "boolean"}, "false")).toEqual({ok: true, value: false});
    expect(parseInput({kind: "integer"}, "3")).toEqual({ok: true, value: 3});
    expect(parseInput({kind: "integer"}, "3.5").ok).toBe(false);
    expect(parseInput({kind: "number"}, "12.5")).toEqual({ok: true, value: 12.5});
    expect(parseInput({kind: "number"}, "twelve").ok).toBe(false);
    expect(parseInput({kind: "enum", options: ["lung", "lymph_node"]}, "pleura").ok).toBe(false);
    expect(parseInput({kind: "text"}, "  Specimen A ")).toEqual({ok: true, value: "Specimen A"});
    expect(parseInput({kind: "text"}, "   ").ok).toBe(false);
  });

  it("applies corrections, removals and additions to a copy and leaves the extraction untouched", async () => {
    const {decide, EMPTY_REVIEW, reviewedRecord, changesRecord} = await import("./reviewState");
    let review = decide(EMPTY_REVIEW, "/station_surveys/1/station_sampled", {status: "corrected", value: false});
    review = decide(review, "/station_surveys/0/station_sampled", {status: "confirmed"});
    review = decide(review, "/targets/0/short_axis_mm", {status: "corrected", value: 12});
    review = decide(review, "/station_surveys/0/station_visualized", {status: "added", value: true});
    review = decide(review, "/targets/0/iaslc_station", {status: "removed"});
    review = decide(review, "/case_details/asa_class", {status: "added", value: 3});
    const out = reviewedRecord(proposal, review);
    expect(out.station_surveys[1].station_sampled).toBe(false);
    expect(out.station_surveys[0]).toMatchObject({station_sampled: true, station_visualized: true});
    expect(out.targets[0]).toMatchObject({short_axis_mm: 12, iaslc_station: null});
    expect(out.case_details.asa_class).toBe(3);
    const settled = out.field_provenance.find((p: {field_path: string}) => p.field_path === "/targets/0/short_axis_mm");
    expect(settled).toMatchObject({conflict_status: "none", value_origin: "reviewer"});
    expect(proposal.station_surveys[1].station_sampled).toBe(true);
    expect(proposal.field_provenance[3].conflict_status).toBe("unresolved");
    expect(changesRecord(review)).toBe(true);
    expect(changesRecord(decide(EMPTY_REVIEW, "/x", {status: "confirmed"}))).toBe(false);
    expect(decide(review, "/case_details/asa_class", null).decisions["/case_details/asa_class"]).toBeUndefined();
  });

  it("drops a removed row and keeps each passage with the row it belongs to", async () => {
    const {EMPTY_REVIEW, reviewedRecord, toggleRow} = await import("./reviewState");
    const review = toggleRow(EMPTY_REVIEW, "/station_surveys/1");
    const out = reviewedRecord(proposal, review);
    expect(out.station_surveys.map((r: {iaslc_station: string}) => r.iaslc_station)).toEqual(["4R", "7"]);
    const passages = Object.fromEntries(out.field_provenance.map((p: {field_path: string; source_excerpt?: string}) => [p.field_path, p.source_excerpt]));
    expect(passages["/station_surveys/0/station_sampled"]).toBe("a");
    expect(passages["/station_surveys/1/station_sampled"]).toBe("c");
    expect(passages["/station_surveys/2/station_sampled"]).toBeUndefined();
    expect(toggleRow(review, "/station_surveys/1").removedRows).toEqual([]);
  });

  it("confirms a whole row except an unresolved field, and counts progress over kept rows", async () => {
    const {confirmRow, countReview, decide, EMPTY_REVIEW, reviewedDisplay, toggleRow} = await import("./reviewState");
    const target = row("targets", 0);
    const confirmed = confirmRow(EMPTY_REVIEW, target);
    expect(confirmed.decisions["/targets/0/site"]).toEqual({status: "confirmed"});
    expect(confirmed.decisions["/targets/0/short_axis_mm"]).toBeUndefined();
    let review = decide(confirmed, "/station_surveys/0/station_sampled", {status: "corrected", value: false});
    review = toggleRow(review, "/station_surveys/2");
    const counts = countReview(review, sections);
    expect(counts).toMatchObject({corrected: 1, rowsRemoved: 1, removed: 0, added: 0});
    expect(counts.confirmed).toBe(Object.keys(confirmed.decisions).length);
    expect(counts.reviewed).toBe(counts.confirmed + 1);
    const all = countReview(EMPTY_REVIEW, sections);
    expect(all.total - counts.total).toBe(row("station_surveys", 2).fields.filter(f => f.state !== "not_extracted").length);
    const sampled = row("station_surveys", 0).fields.find(f => f.name === "station_sampled")!;
    expect(reviewedDisplay(sampled, {status: "corrected", value: false})).toEqual({state: "negative", display: "No"});
    expect(reviewedDisplay(sampled, {status: "confirmed"})).toEqual({state: "value", display: "Yes"});
  });
});
