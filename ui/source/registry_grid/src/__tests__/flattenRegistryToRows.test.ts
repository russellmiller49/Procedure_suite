import { describe, expect, it } from "vitest";

import { flattenRegistryToRows } from "../flatten/flattenRegistryToRows";
import type { EvidenceSpan } from "../types";

describe("flattenRegistryToRows", () => {
  it("creates stable json pointers and attaches evidence", () => {
    const registry = {
      clinical_context: { age: 63 },
      procedures: {
        ebus: { performed: true, stations: [{ station: "4R", sampled: true }, { station: "7", sampled: false }] },
        bal: { performed: false, volume_ml: 20 },
      },
      pathology_results: { pdl1_tps_text: "<1%" },
      billing: { should_skip: true },
      evidence: { should_skip: true },
    };

    const evidenceIndex = new Map<string, EvidenceSpan[]>();
    evidenceIndex.set("/registry/procedures/ebus/performed", [{ source: "ml", text: "EBUS", span: [0, 4] }]);
    evidenceIndex.set("/registry/procedures/bal/performed", [{ source: "ml", text: "BAL", span: [5, 8] }]);

    const rows = flattenRegistryToRows(registry, evidenceIndex);
    const ids = rows.map((r) => r.id);

    expect(ids).toContain("/registry/clinical_context");
    expect(ids).toContain("/registry/clinical_context/age");
    expect(ids).toContain("/registry/procedures/ebus/performed");
    expect(ids).toContain("/registry/procedures/bal/performed");
    expect(ids).not.toContain("/registry/billing");
    expect(ids).not.toContain("/registry/evidence");

    const ebusPerformed = rows.find((r) => r.id === "/registry/procedures/ebus/performed");
    expect(ebusPerformed?.evidence.length).toBe(1);
    expect(ebusPerformed?.extractedValueDisplay).toBe("Yes");

    const balPerformed = rows.find((r) => r.id === "/registry/procedures/bal/performed");
    expect(balPerformed?.extractedValueDisplay).toBe("No");
  });
});

