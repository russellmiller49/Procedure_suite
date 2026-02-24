import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import "./styles.css";

import React from "react";
import { createRoot, type Root } from "react-dom/client";

import { RegistryGridApp } from "./RegistryGridApp";
import { VaultProvider } from "./context/VaultContext";
import { clearHighlight } from "./monaco/monacoBridge";

type MountArgs = {
  rootEl: HTMLElement;
  getMonacoEditor?: () => unknown;
  processResponse?: unknown;
  hostEditedPatch?: unknown;
  onExportEditedJson?: (payload: unknown) => void;
  registryUuid?: string | null;
  vaultLocalData?: unknown;
  remoteCaseData?: unknown;
  onSaveLocalVaultData?: (payload: unknown) => Promise<unknown> | unknown;
  onSaveRemotePatch?: (payload: unknown) => Promise<unknown> | unknown;
};

type UpdateArgs = {
  processResponse?: unknown;
  hostEditedPatch?: unknown;
  registryUuid?: string | null;
  vaultLocalData?: unknown;
  remoteCaseData?: unknown;
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
let processResponseValue: unknown = null;
let hostEditedPatchValue: unknown = null;
let registryUuidValue: string | null = null;
let vaultLocalDataValue: unknown = null;
let remoteCaseDataValue: unknown = null;
let onSaveLocalVaultDataFn: ((payload: unknown) => Promise<unknown> | unknown) | null = null;
let onSaveRemotePatchFn: ((payload: unknown) => Promise<unknown> | unknown) | null = null;

function mount(args: MountArgs) {
  if (!args?.rootEl) throw new Error("RegistryGrid.mount requires rootEl");
  if (mountedEl && args.rootEl !== mountedEl) unmount();

  getMonacoEditorFn = typeof args.getMonacoEditor === "function" ? args.getMonacoEditor : null;
  onExportEditedJsonFn = typeof args.onExportEditedJson === "function" ? args.onExportEditedJson : null;
  processResponseValue = args.processResponse;
  hostEditedPatchValue = args.hostEditedPatch ?? null;
  registryUuidValue = typeof args.registryUuid === "string" ? args.registryUuid : null;
  vaultLocalDataValue = args.vaultLocalData ?? null;
  remoteCaseDataValue = args.remoteCaseData ?? null;
  onSaveLocalVaultDataFn =
    typeof args.onSaveLocalVaultData === "function" ? args.onSaveLocalVaultData : null;
  onSaveRemotePatchFn = typeof args.onSaveRemotePatch === "function" ? args.onSaveRemotePatch : null;

  if (root && mountedEl === args.rootEl) {
    root.render(
      <VaultProvider>
        <RegistryGridApp
          processResponse={processResponseValue}
          registryUuid={registryUuidValue}
          vaultLocalData={vaultLocalDataValue}
          remoteCaseData={remoteCaseDataValue}
          hostEditedPatch={hostEditedPatchValue}
          getMonacoEditor={getMonacoEditorFn}
          onEditsExport={onExportEditedJsonFn}
          onSaveLocalVaultData={onSaveLocalVaultDataFn}
          onSaveRemotePatch={onSaveRemotePatchFn}
        />
      </VaultProvider>,
    );
    return;
  }

  mountedEl = args.rootEl;
  root = createRoot(args.rootEl);
  root.render(
    <VaultProvider>
      <RegistryGridApp
        processResponse={processResponseValue}
        registryUuid={registryUuidValue}
        vaultLocalData={vaultLocalDataValue}
        remoteCaseData={remoteCaseDataValue}
        hostEditedPatch={hostEditedPatchValue}
        getMonacoEditor={getMonacoEditorFn}
        onEditsExport={onExportEditedJsonFn}
        onSaveLocalVaultData={onSaveLocalVaultDataFn}
        onSaveRemotePatch={onSaveRemotePatchFn}
      />
    </VaultProvider>,
  );
}

function update(args: UpdateArgs) {
  if (!root) return;
  if ("processResponse" in args) processResponseValue = args.processResponse;
  if ("hostEditedPatch" in args) hostEditedPatchValue = args.hostEditedPatch ?? null;
  if (typeof args.registryUuid === "string") {
    registryUuidValue = args.registryUuid;
  } else if (args.registryUuid === null) {
    registryUuidValue = null;
  }
  if ("vaultLocalData" in args) vaultLocalDataValue = args.vaultLocalData ?? null;
  if ("remoteCaseData" in args) remoteCaseDataValue = args.remoteCaseData ?? null;
  root.render(
    <VaultProvider>
      <RegistryGridApp
        processResponse={processResponseValue}
        registryUuid={registryUuidValue}
        vaultLocalData={vaultLocalDataValue}
        remoteCaseData={remoteCaseDataValue}
        hostEditedPatch={hostEditedPatchValue}
        getMonacoEditor={getMonacoEditorFn}
        onEditsExport={onExportEditedJsonFn}
        onSaveLocalVaultData={onSaveLocalVaultDataFn}
        onSaveRemotePatch={onSaveRemotePatchFn}
      />
    </VaultProvider>,
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
  processResponseValue = null;
  hostEditedPatchValue = null;
  registryUuidValue = null;
  vaultLocalDataValue = null;
  remoteCaseDataValue = null;
  onSaveLocalVaultDataFn = null;
  onSaveRemotePatchFn = null;
}

const api: RegistryGridApi = { mount, update, unmount };

declare global {
  interface Window {
    RegistryGrid?: RegistryGridApi;
  }
}

window.RegistryGrid = api;

export { mount, update, unmount };
export { LockVaultButton } from "./components/LockVaultButton";
export { UnlockVaultModal } from "./components/UnlockVaultModal";
export { VaultProvider, useVault } from "./context/VaultContext";
