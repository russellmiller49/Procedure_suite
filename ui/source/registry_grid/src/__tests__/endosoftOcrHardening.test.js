import { describe, expect, it } from "vitest";

import { classifyPage } from "../../../../static/phi_redactor/pdf_local/pdf/pageClassifier.js";
import { mergeNativeAndOcrText } from "../../../../static/phi_redactor/pdf_local/pdf/fusion.js";
import {
  ENDOSOFT_CLEAN_PAGE_SNIPPET,
  ENDOSOFT_FRAGMENT_RECOVERY_LINE,
  ENDOSOFT_FRAGMENTED_PAGE_SNIPPET,
} from "./fixtures/endosoftBackfillSamples.js";

describe("endosoft OCR hardening", () => {
  it("does not trigger backfill on clean EndoSoft native text", () => {
    const text = Array.from(
      { length: 10 },
      () => ENDOSOFT_CLEAN_PAGE_SNIPPET,
    ).join("\n");
    const stats = {
      charCount: text.length,
      pageArea: 520000,
      nativeTextDensity: text.length / 520000,
      singleCharItemRatio: 0.03,
      nonPrintableRatio: 0,
      imageOpCount: 1,
      overlapRatio: 0.03,
      contaminationScore: 0.05,
      completenessConfidence: 0.93,
    };

    const classification = classifyPage(stats, text);
    expect(classification.needsOcrBackfill).toBe(false);
  });

  it("triggers backfill on fragmented EndoSoft native text", () => {
    const text = [
      ...Array.from({ length: 3 }, () => ENDOSOFT_CLEAN_PAGE_SNIPPET),
      ENDOSOFT_FRAGMENTED_PAGE_SNIPPET,
      ...Array.from({ length: 2 }, () => ENDOSOFT_CLEAN_PAGE_SNIPPET),
    ].join("\n");
    const stats = {
      charCount: text.length,
      pageArea: 520000,
      nativeTextDensity: text.length / 520000,
      singleCharItemRatio: 0.03,
      nonPrintableRatio: 0,
      imageOpCount: 2,
      overlapRatio: 0.05,
      contaminationScore: 0.08,
      completenessConfidence: 0.9,
    };

    const classification = classifyPage(stats, text);
    expect(classification.needsOcrBackfill).toBe(true);
  });

  it("repair-only merge avoids OCR takeover while keeping fragment recovery", () => {
    const nativeText = [
      "PROCEDURE TECHNIQUE:",
      "surgeon every 4 hours.",
      "Bleeding:",
      "nose.",
    ].join("\n");
    const ocrText = [
      "Give the prescribed pain medication Oxycodone and acetaminophen as ordered by your",
      "surgeon every 4 hours.",
      "When the tonsil or adenoid scabs fall off, your child may have bleeding from the mouth or",
      "nose.",
      "This extra OCR-only line should not be inserted in repair-only mode.",
    ].join("\n");

    const merged = mergeNativeAndOcrText(nativeText, ocrText, { mode: "repair_only" });
    expect(merged).toContain(ENDOSOFT_FRAGMENT_RECOVERY_LINE);
    expect(merged).toContain("mouth or nose.");
    expect(merged).not.toContain("This extra OCR-only line");
  });
});
