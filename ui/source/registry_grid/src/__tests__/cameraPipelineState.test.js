import { describe, expect, it, vi } from "vitest";

import { createCameraCaptureQueue } from "../../../../static/phi_redactor/camera_local/cameraUi.js";

describe("camera capture queue", () => {
  it("adds pages and exports OCR payload in page order", () => {
    const queue = createCameraCaptureQueue({
      urlApi: {
        createObjectURL: vi.fn(() => "blob:one"),
        revokeObjectURL: vi.fn(),
      },
    });

    queue.addPage({ bitmap: { close: vi.fn() }, blob: { id: 1 }, width: 1200, height: 900 });
    queue.addPage({ bitmap: { close: vi.fn() }, blob: { id: 2 }, width: 1200, height: 900 });

    const exported = queue.exportForOcr();
    expect(exported).toHaveLength(2);
    expect(exported.map((p) => p.pageIndex)).toEqual([0, 1]);
  });

  it("retake closes bitmap and revokes preview URL", () => {
    const revokeObjectURL = vi.fn();
    const close = vi.fn();
    const queue = createCameraCaptureQueue({
      urlApi: {
        createObjectURL: vi.fn(() => "blob:last"),
        revokeObjectURL,
      },
    });

    queue.addPage({ bitmap: { close }, blob: { id: 1 }, width: 100, height: 100 });
    queue.retakeLast();

    expect(close).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledTimes(1);
    expect(queue.pages).toHaveLength(0);
  });

  it("clearAll releases every captured page", () => {
    const revokeObjectURL = vi.fn();
    const closeA = vi.fn();
    const closeB = vi.fn();
    const queue = createCameraCaptureQueue({
      urlApi: {
        createObjectURL: vi.fn((blob) => `blob:${blob.id}`),
        revokeObjectURL,
      },
    });

    queue.addPage({ bitmap: { close: closeA }, blob: { id: "a" }, width: 100, height: 100 });
    queue.addPage({ bitmap: { close: closeB }, blob: { id: "b" }, width: 100, height: 100 });

    const cleared = queue.clearAll();
    expect(cleared).toBe(2);
    expect(closeA).toHaveBeenCalledTimes(1);
    expect(closeB).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledTimes(2);
    expect(queue.pages).toHaveLength(0);
  });
});
