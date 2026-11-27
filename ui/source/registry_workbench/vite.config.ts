import path from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const here = path.dirname(fileURLToPath(import.meta.url));

// Served by FastAPI at /workbench when PROCSUITE_WORKBENCH_ENABLED=1.
export default defineConfig({
  base: "/workbench/",
  plugins: [react()],
  build: {
    outDir: path.resolve(here, "../../static/registry_workbench"),
    emptyOutDir: true,
    sourcemap: false,
  },
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
});
