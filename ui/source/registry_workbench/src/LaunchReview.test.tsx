import {renderToStaticMarkup} from "react-dom/server";
import {describe, expect, it} from "vitest";
import profileJson from "./__fixtures__/profile.json";
import {LaunchReview} from "./LaunchReview";
import {fresh} from "./review";
import type {Profile} from "./types";

const profile = profileJson as unknown as Profile;

function render(values = fresh("2026-09-04")) {
  return renderToStaticMarkup(<LaunchReview profile={profile} values={values} onChange={() => {}} />);
}

describe("LaunchReview", () => {
  it("renders every contract section from the live profile", () => {
    const html = render();
    for (const title of Object.values(profile.sections)) expect(html).toContain(title);
  });

  it("labels fields with dictionary units and definitions", () => {
    const values = {...fresh(), targets: [{target_id: "t1", site: "lung", lobe: "RUL"}]};
    const html = render(values);
    expect(html).toContain("max diameter mm");
    expect(html).toContain("(mm)");
    expect(html).toContain('title="Bronchus visibly leading to or entering lesion."');
  });

  it("shows evidence and flags unresolved conflicts", () => {
    const values = {
      ...fresh(),
      targets: [{target_id: "t1", site: "lymph_node", iaslc_station: "7"}],
      field_provenance: [
        {field_path: "/targets/0/iaslc_station", source_document_id: "d", source_start: 0, source_end: 15, source_excerpt: "A station 7 node", value_origin: "extracted", review_status: "proposed", conflict_status: "none"},
        {field_path: "/targets/0/short_axis_mm", value_origin: "extracted", raw_value: "10.0", missingness_reason: "unknown", conflict_status: "unresolved"},
      ],
    };
    const html = render(values);
    expect(html).toContain("“A station 7 node”");
    expect(html).toContain("the extractor claimed 10.0");
  });
});
