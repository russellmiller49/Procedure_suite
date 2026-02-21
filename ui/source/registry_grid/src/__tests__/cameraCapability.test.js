import { describe, expect, it } from "vitest";

import { canUseCameraScan } from "../../../../static/phi_redactor/camera_local/cameraCapture.js";

describe("camera capability gating", () => {
  const FakeWorker = class {};
  const FakeOffscreenCanvas = class {};

  it("blocks when secure context is unavailable", () => {
    const result = canUseCameraScan({
      isSecureContext: false,
      navigator: { mediaDevices: { getUserMedia: async () => null } },
      Worker: FakeWorker,
      OffscreenCanvas: FakeOffscreenCanvas,
      createImageBitmap: () => null,
    });

    expect(result.ok).toBe(false);
    expect(result.code).toBe("secure_context_required");
  });

  it("blocks when getUserMedia is unavailable", () => {
    const result = canUseCameraScan({
      isSecureContext: true,
      navigator: {},
      Worker: FakeWorker,
      OffscreenCanvas: FakeOffscreenCanvas,
      createImageBitmap: () => null,
    });

    expect(result.ok).toBe(false);
    expect(result.code).toBe("getusermedia_unavailable");
  });

  it("blocks when OffscreenCanvas is unavailable", () => {
    const result = canUseCameraScan({
      isSecureContext: true,
      navigator: { mediaDevices: { getUserMedia: async () => null } },
      Worker: FakeWorker,
      createImageBitmap: () => null,
    });

    expect(result.ok).toBe(false);
    expect(result.code).toBe("offscreen_canvas_unavailable");
  });

  it("returns ok when required camera stack is available", () => {
    const result = canUseCameraScan({
      isSecureContext: true,
      navigator: { mediaDevices: { getUserMedia: async () => ({}) } },
      Worker: class FakeWorker {},
      OffscreenCanvas: class FakeOffscreenCanvas {},
      createImageBitmap: async () => ({})
    });

    expect(result.ok).toBe(true);
    expect(result.code).toBe("ok");
  });
});
