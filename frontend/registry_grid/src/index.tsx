import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import "./styles.css";

import React from "react";
import { createRoot, type Root } from "react-dom/client";

import { RegistryGridApp } from "./RegistryGridApp";
import { clearHighlight } from "./monaco/monacoBridge";

type MountArgs = {
  rootEl: HTMLElement;
  getMonacoEditor?: () => unknown;
  processResponse?: unknown;
  onExportEditedJson?: (payload: unknown) => void;
};

type UpdateArgs = {
  processResponse?: unknown;
};

type RegistryGridApi = {
  mount: (args: MountArgs) => void;
  update: (args: UpdateArgs) => void;
  unmount: () => void;
};

let root: Root | null = null;
let mountedEl: HTMLElement | null = null;
let getMonacoEditorFn: (() => unknown) | null = null;
let onExportEditedJsonFn: ((payload: unknown) => void) | null = null;

function mount(args: MountArgs) {
  if (!args?.rootEl) throw new Error("RegistryGrid.mount requires rootEl");
  if (mountedEl && args.rootEl !== mountedEl) unmount();

  getMonacoEditorFn = typeof args.getMonacoEditor === "function" ? args.getMonacoEditor : null;
  onExportEditedJsonFn = typeof args.onExportEditedJson === "function" ? args.onExportEditedJson : null;

  if (root && mountedEl === args.rootEl) {
    root.render(
      <RegistryGridApp
        processResponse={args.processResponse}
        getMonacoEditor={getMonacoEditorFn}
        onEditsExport={onExportEditedJsonFn}
      />,
    );
    return;
  }

  mountedEl = args.rootEl;
  root = createRoot(args.rootEl);
  root.render(
    <RegistryGridApp
      processResponse={args.processResponse}
      getMonacoEditor={getMonacoEditorFn}
      onEditsExport={onExportEditedJsonFn}
    />,
  );
}

function update(args: UpdateArgs) {
  if (!root) return;
  root.render(
    <RegistryGridApp
      processResponse={args.processResponse}
      getMonacoEditor={getMonacoEditorFn}
      onEditsExport={onExportEditedJsonFn}
    />,
  );
}

function unmount() {
  if (!root) return;
  try {
    const editor = getMonacoEditorFn?.() ?? null;
    clearHighlight(editor as unknown);
  } catch {
    // ignore
  }
  try {
    onExportEditedJsonFn?.(null);
  } catch {
    // ignore
  }
  root.unmount();
  root = null;
  mountedEl = null;
  getMonacoEditorFn = null;
  onExportEditedJsonFn = null;
}

const api: RegistryGridApi = { mount, update, unmount };

declare global {
  interface Window {
    RegistryGrid?: RegistryGridApi;
  }
}

window.RegistryGrid = api;

export { mount, update, unmount };
