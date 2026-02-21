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

  it("normalizes crop boxes and includes crop metadata in OCR export", () => {
    const queue = createCameraCaptureQueue({
      urlApi: {
        createObjectURL: vi.fn((blob) => `blob:${blob.id}`),
        revokeObjectURL: vi.fn(),
      },
    });

    queue.addPage({ bitmap: { close: vi.fn() }, blob: { id: 1 }, width: 2000, height: 1200 });
    queue.addPage({ bitmap: { close: vi.fn() }, blob: { id: 2 }, width: 2000, height: 1200 });

    queue.setPageCrop(0, { x0: 0.84, y0: 0.9, x1: 0.14, y1: 0.1 });
    queue.setPageCrop(1, { x0: 0.12, y0: 0.1, x1: 0.13, y1: 0.2 });

    const exported = queue.exportForOcr();
    expect(exported).toHaveLength(2);
    expect(exported[0].crop).toEqual({ x0: 0.14, y0: 0.1, x1: 0.84, y1: 0.9 });
    expect(exported[1].crop).toBeNull();
  });

  it("clears all crop metadata from captured pages", () => {
    const queue = createCameraCaptureQueue({
      urlApi: {
        createObjectURL: vi.fn((blob) => `blob:${blob.id}`),
        revokeObjectURL: vi.fn(),
      },
    });

    queue.addPage({ bitmap: { close: vi.fn() }, blob: { id: "a" }, width: 1000, height: 700 });
    queue.addPage({ bitmap: { close: vi.fn() }, blob: { id: "b" }, width: 1000, height: 700 });
    queue.setPageCrop(0, { x0: 0.1, y0: 0.1, x1: 0.95, y1: 0.95 });
    queue.setPageCrop(1, { x0: 0.2, y0: 0.2, x1: 0.85, y1: 0.8 });

    expect(queue.clearAllCrops()).toBe(2);
    const exported = queue.exportForOcr();
    expect(exported[0].crop).toBeNull();
    expect(exported[1].crop).toBeNull();
    expect(queue.clearAllCrops()).toBe(0);
  });
});
