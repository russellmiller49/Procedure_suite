import { describe, expect, it } from "vitest";

import { calculateDayOffset, parseIsoYmd } from "../utils/dateMath";

describe("dateMath", () => {
  it("parses valid ISO dates", () => {
    expect(parseIsoYmd("2026-02-23")).toEqual({ year: 2026, month: 2, day: 23 });
  });

  it("returns null for invalid ISO dates", () => {
    expect(parseIsoYmd("2026-02-30")).toBeNull();
    expect(parseIsoYmd("02/23/2026")).toBeNull();
  });

  it("calculates positive offsets", () => {
    expect(calculateDayOffset("2026-02-23", "2026-03-01")).toBe(6);
  });

  it("calculates zero offsets", () => {
    expect(calculateDayOffset("2026-02-23", "2026-02-23")).toBe(0);
  });

  it("calculates negative offsets", () => {
    expect(calculateDayOffset("2026-02-23", "2026-02-20")).toBe(-3);
  });

  it("returns null when either date is invalid", () => {
    expect(calculateDayOffset("2026-02-23", "invalid")).toBeNull();
    expect(calculateDayOffset("", "2026-02-24")).toBeNull();
  });
});

