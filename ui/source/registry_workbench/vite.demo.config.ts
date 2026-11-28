import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";

import react from "@vitejs/plugin-react";
import {defineConfig} from "vite";

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.resolve(here, "../../static/phi_redactor/registry_demo");

// Built into the /ui/ static tree so the page shares the redactor worker's origin and
// the COOP/COEP headers FastAPI sets on /ui/*. File names are fixed to keep diffs small.
export default defineConfig({
  base: "/ui/registry_demo/",
  plugins: [
    react(),
    {
      name: "demo-index",
      closeBundle() {
        const built = path.join(outDir, "demo.html");
        if (fs.existsSync(built)) fs.renameSync(built, path.join(outDir, "index.html"));
      },
    },
  ],
  build: {
    outDir,
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      input: path.resolve(here, "demo.html"),
      output: {
        entryFileNames: "registry_demo.js",
        chunkFileNames: "registry_demo.[name].js",
        assetFileNames: "registry_demo[extname]",
      },
    },
  },
  server: {
    proxy: {"/api": "http://127.0.0.1:8000", "^/ui/(?!registry_demo/)": "http://127.0.0.1:8000"},
  },
});
