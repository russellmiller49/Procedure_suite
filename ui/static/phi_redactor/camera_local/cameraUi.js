function hasFunction(value) {
  return typeof value === "function";
}

function defaultUrlApi() {
  const runtimeUrl = globalThis.URL;
  if (runtimeUrl && hasFunction(runtimeUrl.createObjectURL) && hasFunction(runtimeUrl.revokeObjectURL)) {
    return runtimeUrl;
  }
  return null;
}

export function releaseCapturedPage(page, urlApi = defaultUrlApi()) {
  if (!page || typeof page !== "object") return;

  if (page.bitmap && hasFunction(page.bitmap.close)) {
    try {
      page.bitmap.close();
    } catch {
      // ignore
    }
  }

  if (page.previewUrl && urlApi && hasFunction(urlApi.revokeObjectURL)) {
    try {
      urlApi.revokeObjectURL(page.previewUrl);
    } catch {
      // ignore
    }
  }

  page.bitmap = null;
  page.previewUrl = "";
}

export function createCameraCaptureQueue(opts = {}) {
  const urlApi = opts.urlApi || defaultUrlApi();
  const pages = [];

  const getPages = () => pages;

  const addPage = (input = {}) => {
    if (!input.bitmap) {
      throw new Error("bitmap is required");
    }

    let previewUrl = "";
    if (input.blob && urlApi && hasFunction(urlApi.createObjectURL)) {
      try {
        previewUrl = urlApi.createObjectURL(input.blob);
      } catch {
        previewUrl = "";
      }
    }

    const page = {
      pageIndex: Number.isFinite(input.pageIndex) ? Number(input.pageIndex) : pages.length,
      bitmap: input.bitmap,
      previewUrl,
      width: Number.isFinite(input.width) ? Number(input.width) : 0,
      height: Number.isFinite(input.height) ? Number(input.height) : 0,
      capturedAt: Number.isFinite(input.capturedAt) ? Number(input.capturedAt) : Date.now(),
      warnings: Array.isArray(input.warnings) ? [...input.warnings] : [],
    };

    pages.push(page);
    return page;
  };

  const retakeLast = () => {
    if (!pages.length) return null;
    const last = pages.pop();
    releaseCapturedPage(last, urlApi);
    return last;
  };

  const clearAll = () => {
    let cleared = 0;
    while (pages.length) {
      const page = pages.pop();
      releaseCapturedPage(page, urlApi);
      cleared += 1;
    }
    return cleared;
  };

  const exportForOcr = () => pages.map((page, idx) => ({
    pageIndex: idx,
    bitmap: page.bitmap,
    width: page.width,
    height: page.height,
  }));

  return {
    get pages() {
      return getPages();
    },
    addPage,
    retakeLast,
    clearAll,
    exportForOcr,
  };
}
