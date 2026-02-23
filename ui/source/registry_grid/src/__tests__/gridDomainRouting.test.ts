import { describe, expect, it } from "vitest";

import { resolveEditRoute } from "../grid/domainRouting";

describe("grid domain routing", () => {
  it("routes local-domain rows to vault updates", () => {
    const route = resolveEditRoute({
      domain: "local",
      jsonPointer: "/local/patient_label",
    });
    expect(route).toBe("local_vault");
  });

  it("routes remote-domain rows to registry patch", () => {
    const route = resolveEditRoute({
      domain: "remote",
      jsonPointer: "/registry/clinical_context/lesion_location",
    });
    expect(route).toBe("remote_patch");
  });

  it("falls back to pointer prefix when domain is missing", () => {
    const localRoute = resolveEditRoute({
      // @ts-expect-error intentionally testing malformed host payload
      domain: undefined,
      jsonPointer: "/local/local_meta/mrn",
    });
    const remoteRoute = resolveEditRoute({
      // @ts-expect-error intentionally testing malformed host payload
      domain: undefined,
      jsonPointer: "/registry/complications",
    });
    expect(localRoute).toBe("local_vault");
    expect(remoteRoute).toBe("remote_patch");
  });
});

