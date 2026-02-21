import { describe, expect, it } from "vitest";

import {
  buildCameraOcrDocumentText,
  runCameraOcrJob,
} from "../../../../static/phi_redactor/camera_local/imagePipeline.js";

describe("camera OCR text assembly", () => {
  it("builds page-separated camera OCR text in page order", () => {
    const text = buildCameraOcrDocumentText([
      { pageIndex: 1, text: "Second page text" },
      { pageIndex: 0, text: "First page text" },
    ]);

    expect(text).toContain("===== PAGE 1 (CAMERA_OCR) =====");
    expect(text).toContain("===== PAGE 2 (CAMERA_OCR) =====");
    expect(text.indexOf("First page text")).toBeLessThan(text.indexOf("Second page text"));
  });

  it("returns empty string when no pages exist", () => {
    expect(buildCameraOcrDocumentText([])).toBe("");
  });

  it("forwards crop metadata to camera OCR worker payload", async () => {
    let postedPayload = null;
    let postedTransferList = null;
    const listeners = new Map();
    const worker = {
      addEventListener(type, handler) {
        listeners.set(type, handler);
      },
      removeEventListener(type) {
        listeners.delete(type);
      },
      postMessage(payload, transferList) {
        postedPayload = payload;
        postedTransferList = transferList;
        const onMessage = listeners.get("message");
        if (onMessage) {
          onMessage({
            data: {
              type: "camera_ocr_done",
              jobId: payload.jobId,
              pages: [{ pageIndex: 0, text: "ok" }],
            },
          });
        }
      },
    };

    const bitmap = { id: "page_bitmap" };
    await runCameraOcrJob(
      worker,
      [
        {
          pageIndex: 0,
          bitmap,
          width: 1600,
          height: 1200,
          crop: { x0: 0.16, y0: 0.11, x1: 0.79, y1: 0.88 },
        },
      ],
      { jobId: "crop-forwarding-test", warningProfile: "ios_safari", sceneHint: "monitor" },
    );

    expect(postedPayload?.type).toBe("camera_ocr_run");
    expect(postedPayload?.pages?.[0]?.crop).toEqual({ x0: 0.16, y0: 0.11, x1: 0.79, y1: 0.88 });
    expect(postedPayload?.options?.warningProfile).toBe("ios_safari");
    expect(postedPayload?.options?.sceneHint).toBe("monitor");
    expect(postedTransferList).toHaveLength(1);
    expect(postedTransferList[0]).toBe(bitmap);
  });
});
