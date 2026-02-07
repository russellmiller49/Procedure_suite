import { describe, expect, it } from "vitest";

import { buildEvidenceIndex } from "../evidence/buildEvidenceIndex";

describe("buildEvidenceIndex", () => {
  it("normalizes relative pointers and dotted paths", () => {
    const resp = {
      evidence: {
        "/clinical_context/age": [{ source: "ui", text: "Age 63", span: [10, 16] }],
        codes: [{ source: "ui", text: "should-ignore", span: [0, 1] }],
      },
      explain: {
        evidence_by_path: {
          "registry.procedures.ebus.performed": [
            { source: "ml", text: "EBUS performed", start: 20, end: 33, confidence: 0.9 },
          ],
        },
        items: [{ path: "procedures.ebus.stations.0.station", source: "ml", text: "4R", start: 40, end: 42 }],
      },
    };

    const idx = buildEvidenceIndex(resp);

    expect(idx.get("/registry/clinical_context/age")?.length).toBe(1);
    expect(idx.has("/registry/codes")).toBe(false);
    expect(idx.get("/registry/procedures/ebus/performed")?.[0]?.span).toEqual([20, 33]);
    expect(idx.get("/registry/procedures/ebus/stations/0/station")?.length).toBe(1);
  });
});

