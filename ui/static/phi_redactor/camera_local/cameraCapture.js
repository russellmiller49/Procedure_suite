function hasFunction(value) {
  return typeof value === "function";
}

function resolveEnv(env) {
  if (env && typeof env === "object") return env;
  return globalThis;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function canUseCameraScan(env) {
  const runtime = resolveEnv(env);
  if (!runtime.isSecureContext) {
    return {
      ok: false,
      reason: "Camera scan requires HTTPS and a secure context.",
      code: "secure_context_required",
    };
  }

  const mediaDevices = runtime.navigator?.mediaDevices;
  if (!mediaDevices || !hasFunction(mediaDevices.getUserMedia)) {
    return {
      ok: false,
      reason: "Camera scan requires browser support for live camera capture.",
      code: "getusermedia_unavailable",
    };
  }

  if (!hasFunction(runtime.Worker)) {
    return {
      ok: false,
      reason: "Camera scan requires Web Worker support.",
      code: "worker_unavailable",
    };
  }

  if (!hasFunction(runtime.OffscreenCanvas)) {
    return {
      ok: false,
      reason: "Camera scan requires OffscreenCanvas support.",
      code: "offscreen_canvas_unavailable",
    };
  }

  if (!hasFunction(runtime.createImageBitmap)) {
    return {
      ok: false,
      reason: "Camera scan requires ImageBitmap support.",
      code: "image_bitmap_unavailable",
    };
  }

  return { ok: true, reason: "ok", code: "ok" };
}

function buildConstraints(options = {}) {
  const facingMode = String(options.facingMode || "environment").trim() || "environment";
  const preferredWidth = Number.isFinite(options.preferredWidth)
    ? clamp(Number(options.preferredWidth), 640, 3840)
    : 1280;
  const preferredHeight = Number.isFinite(options.preferredHeight)
    ? clamp(Number(options.preferredHeight), 480, 2160)
    : undefined;

  const video = {
    facingMode: { ideal: facingMode },
    width: { ideal: preferredWidth },
  };
  if (preferredHeight) {
    video.height = { ideal: preferredHeight };
  }

  return {
    video,
    audio: false,
  };
}

export async function startCamera(videoEl, options = {}, env) {
  const runtime = resolveEnv(env);
  const mediaDevices = runtime.navigator?.mediaDevices;
  if (!videoEl) throw new Error("camera preview element is required");
  if (!mediaDevices || !hasFunction(mediaDevices.getUserMedia)) {
    throw new Error("getUserMedia is unavailable");
  }

  const constraints = buildConstraints(options);
  let stream = null;
  try {
    stream = await mediaDevices.getUserMedia(constraints);
  } catch (error) {
    const requestedFacing = String(options.facingMode || "environment").toLowerCase();
    if (requestedFacing !== "environment") throw error;
    // Fallback for devices that refuse rear camera constraints.
    stream = await mediaDevices.getUserMedia({
      video: { width: constraints.video.width },
      audio: false,
    });
  }

  videoEl.setAttribute("playsinline", "true");
  videoEl.muted = true;
  videoEl.srcObject = stream;
  if (hasFunction(videoEl.play)) {
    try {
      await videoEl.play();
    } catch {
      // iOS can block autoplay until explicit gesture; caller starts via button click.
    }
  }

  return stream;
}

export function stopCamera(target) {
  let stream = null;
  if (target && hasFunction(target.getTracks)) {
    stream = target;
  } else if (target && target.srcObject && hasFunction(target.srcObject.getTracks)) {
    stream = target.srcObject;
  }

  if (!stream) return 0;

  const tracks = stream.getTracks();
  for (const track of tracks) {
    try {
      track.stop();
    } catch {
      // ignore per-track stop failures
    }
  }

  if (target && Object.prototype.hasOwnProperty.call(target, "srcObject")) {
    try {
      target.srcObject = null;
    } catch {
      // ignore
    }
  }

  return tracks.length;
}

function createCanvas(width, height, runtime) {
  if (hasFunction(runtime.OffscreenCanvas)) {
    return new runtime.OffscreenCanvas(width, height);
  }

  const doc = runtime.document;
  if (!doc || !hasFunction(doc.createElement)) {
    throw new Error("No canvas API available for camera capture");
  }

  const canvas = doc.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  return canvas;
}

function canvasToBlob(canvas, quality) {
  if (hasFunction(canvas.convertToBlob)) {
    return canvas.convertToBlob({ type: "image/jpeg", quality });
  }

  if (!hasFunction(canvas.toBlob)) {
    return Promise.resolve(null);
  }

  return new Promise((resolve) => {
    canvas.toBlob(
      (blob) => resolve(blob || null),
      "image/jpeg",
      quality,
    );
  });
}

export async function captureFrame(videoEl, options = {}, env) {
  const runtime = resolveEnv(env);
  if (!videoEl) throw new Error("camera preview element is required");

  const sourceWidth = Math.max(1, Number(videoEl.videoWidth) || 0);
  const sourceHeight = Math.max(1, Number(videoEl.videoHeight) || 0);
  if (!sourceWidth || !sourceHeight) {
    throw new Error("Camera has not produced a frame yet");
  }

  const maxDim = Number.isFinite(options.maxDim)
    ? clamp(Number(options.maxDim), 320, 4096)
    : 2000;
  const scale = Math.min(1, maxDim / Math.max(sourceWidth, sourceHeight));
  const width = Math.max(1, Math.round(sourceWidth * scale));
  const height = Math.max(1, Math.round(sourceHeight * scale));

  const canvas = createCanvas(width, height, runtime);
  const context = canvas.getContext("2d", { alpha: false, willReadFrequently: true });
  if (!context) throw new Error("Unable to acquire 2D context for capture");

  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, width, height);
  context.drawImage(videoEl, 0, 0, sourceWidth, sourceHeight, 0, 0, width, height);

  const bitmap = await runtime.createImageBitmap(canvas);
  const quality = Number.isFinite(options.jpegQuality)
    ? clamp(Number(options.jpegQuality), 0.5, 0.98)
    : 0.92;
  const blob = await canvasToBlob(canvas, quality);

  return {
    bitmap,
    width,
    height,
    blob,
    sourceWidth,
    sourceHeight,
  };
}
