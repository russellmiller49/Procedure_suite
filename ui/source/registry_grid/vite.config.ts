import path from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.resolve(here, "../../static/phi_redactor/registry_grid");

export default defineConfig({
  plugins: [react()],
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
  build: {
    lib: {
      entry: path.resolve(here, "src/index.tsx"),
      name: "RegistryGrid",
      formats: ["iife"],
      fileName: "registry_grid",
    },
    outDir,
    emptyOutDir: true,
    cssCodeSplit: false,
    minify: "esbuild",
    target: "es2020",
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === "style.css") return "registry_grid.css";
          return assetInfo.name ?? "asset[extname]";
        },
      },
    },
  },
});
