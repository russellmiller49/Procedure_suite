import {describe, expect, it} from "vitest";
import {evidenceSpans, fresh, fromProposal, segments} from "./review";

describe("segments", () => {
  it("preserves the text and offsets while marking evidence and focus", () => {
    const text = "Radial EBUS showed a concentric pattern.";
    const parts = segments(text, [[0, 11], [21, 31]], [21, 31]);
    expect(parts.map(p => p.text).join("")).toBe(text);
    for (const part of parts) expect(text.slice(part.start, part.start + part.text.length)).toBe(part.text);
    expect(parts.find(p => p.text === "Radial EBUS")?.mark).toBe("evidence");
    expect(parts.find(p => p.text === "concentric")?.mark).toBe("focus");
  });

  it("ignores spans outside the document", () => {
    expect(segments("abc", [[2, 9]]).map(p => p.mark)).toEqual(["none"]);
  });
});

describe("drafts", () => {
  it("seeds an assisted draft from a proposal without inventing an event date", () => {
    const proposal = {procedures: [{category: "linear_ebus", performance: "performed"}], targets: [{target_id: "t", site: "lung"}],
      field_provenance: [{field_path: "/targets/0/site", source_document_id: "d", source_start: 3, source_end: 9}]};
    const draft = fromProposal(proposal, null);
    expect(draft.event_date).toBe("");
    expect(draft.targets).toHaveLength(1);
    expect(draft.station_surveys).toEqual([]);
    expect(evidenceSpans(draft, "d")).toEqual([[3, 9]]);
    expect(evidenceSpans(draft, "other")).toEqual([]);
  });

  it("starts a blinded draft empty apart from one undocumented component", () => {
    const draft = fresh("2026-09-04");
    expect(draft.event_date).toBe("2026-09-04");
    expect(draft.procedures).toEqual([{category: "robotic_bronchoscopy", performance: "not_documented", planned: null, completion: null}]);
    expect(draft.field_provenance).toEqual([]);
  });
});
