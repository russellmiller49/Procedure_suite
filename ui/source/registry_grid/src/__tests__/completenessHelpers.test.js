import { describe, expect, it } from "vitest";

import {
  buildCompletenessCandidatePaths,
  buildCompletenessEbusStationHintsByIndex,
  collectStagedCompletenessEntries,
  getCompletenessEbusStationHintForPath,
  normalizeCompletenessStationToken,
} from "../../../../static/phi_redactor/completenessHelpers.js";

function resolvePromptPath(_registry, promptPath) {
  return { effectivePath: String(promptPath || "").trim(), hasWildcard: false, wildcardCount: 0 };
}

function getStoredWildcardEffectivePathsForPrompt() {
  return [];
}

function getInputSpec(promptPath) {
  const path = String(promptPath || "").trim();
  if (path.endsWith(".short_axis_mm")) return { type: "number" };
  if (path.endsWith(".lymphocytes_present")) return { type: "boolean" };
  if (path === "clinical_context.ecog_score") return { type: "ecog" };
  return { type: "string" };
}

function coerceValue(spec, rawValue) {
  const raw = String(rawValue ?? "").trim();
  if (!raw) return null;
  if (spec?.type === "number") {
    const n = Number.parseFloat(raw);
    return Number.isFinite(n) ? n : null;
  }
  if (spec?.type === "boolean") {
    if (raw.toLowerCase() === "true" || raw.toLowerCase() === "yes") return true;
    if (raw.toLowerCase() === "false" || raw.toLowerCase() === "no") return false;
    return null;
  }
  return raw;
}

describe("completeness helper staging/apply planning", () => {
  it("collects only staged entries and includes station hints for EBUS rows", () => {
    const prompts = [
      {
        target_path: "granular_data.linear_ebus_stations_detail[1].short_axis_mm",
        label: "Node size short axis (station 4L)",
      },
      {
        target_path: "granular_data.linear_ebus_stations_detail[1].lymphocytes_present",
        label: "Adequacy/ROSE (station 4L)",
      },
    ];
    const staged = new Map([
      ["granular_data.linear_ebus_stations_detail[1].short_axis_mm", "12.5"],
    ]);
    const hintsByIndex = buildCompletenessEbusStationHintsByIndex(prompts);

    const { entries, invalidCount } = collectStagedCompletenessEntries({
      prompts,
      registry: {},
      rawValueByPath: staged,
      resolvePromptPath,
      getStoredWildcardEffectivePathsForPrompt,
      getInputSpec,
      coerceValue,
      getStationHintForPath: (prompt, effectivePath) =>
        getCompletenessEbusStationHintForPath(prompt, effectivePath, hintsByIndex),
    });

    expect(invalidCount).toBe(0);
    expect(entries).toHaveLength(1);
    expect(entries[0].effectivePath).toBe("granular_data.linear_ebus_stations_detail[1].short_axis_mm");
    expect(entries[0].rawEmpty).toBe(false);
    expect(entries[0].invalid).toBe(false);
    expect(entries[0].coerced).toBe(12.5);
    expect(entries[0].stationHint).toBe("4L");
  });

  it("marks invalid staged values so Update Table can skip them", () => {
    const prompts = [
      {
        target_path: "granular_data.linear_ebus_stations_detail[1].lymphocytes_present",
        label: "Adequacy/ROSE (station 4L)",
      },
    ];
    const staged = new Map([
      ["granular_data.linear_ebus_stations_detail[1].lymphocytes_present", "unknown"],
    ]);

    const { entries, invalidCount } = collectStagedCompletenessEntries({
      prompts,
      registry: {},
      rawValueByPath: staged,
      resolvePromptPath,
      getStoredWildcardEffectivePathsForPrompt,
      getInputSpec,
      coerceValue,
      getStationHintForPath: () => "4L",
    });

    expect(entries).toHaveLength(1);
    expect(entries[0].invalid).toBe(true);
    expect(invalidCount).toBe(1);
  });

  it("supports station fallback from existing row values when label is generic", () => {
    const prompts = [
      {
        target_path: "granular_data.linear_ebus_stations_detail[2].short_axis_mm",
        label: "Node size short axis",
      },
    ];
    const hintsByIndex = buildCompletenessEbusStationHintsByIndex(prompts);
    const hint = getCompletenessEbusStationHintForPath(
      prompts[0],
      "granular_data.linear_ebus_stations_detail[2].short_axis_mm",
      hintsByIndex,
      () => "11r"
    );

    expect(hint).toBe("11R");
  });

  it("normalizes station tokens from mixed formatting", () => {
    expect(normalizeCompletenessStationToken(" station 4 l ")).toBe("4L");
    expect(normalizeCompletenessStationToken("11ri")).toBe("11RI");
    expect(normalizeCompletenessStationToken("")).toBe("");
  });

  it("builds candidate paths including source-path fallback aliases", () => {
    const candidates = buildCompletenessCandidatePaths({
      promptPath: "risk_assessment.asa_class",
      sourcePath: "clinical_context.asa_class",
      effectivePath: "risk_assessment.asa_class",
    });
    expect(candidates).toEqual(["risk_assessment.asa_class", "clinical_context.asa_class"]);
  });

  it("resolves wildcard source path to effective index", () => {
    const candidates = buildCompletenessCandidatePaths({
      promptPath: "granular_data.navigation_targets[2].pet_suv_max",
      sourcePath: "granular_data.navigation_targets[*].pet_suv_max",
      effectivePath: "granular_data.navigation_targets[2].pet_suv_max",
    });
    expect(candidates).toEqual(["granular_data.navigation_targets[2].pet_suv_max"]);
  });
});
