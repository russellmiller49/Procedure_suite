import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { persistCaseSnapshot, loadCaseSnapshot, listCaseSnapshotMeta } from "../../../../static/phi_redactor/caseSnapshotStore.js";
import { initNewVault } from "../../../../static/phi_redactor/vaultClient.js";

class LocalStorageMock {
  store = new Map();

  get length() {
    return this.store.size;
  }

  clear() {
    this.store.clear();
  }

  getItem(key) {
    const k = String(key);
    return this.store.has(k) ? this.store.get(k) : null;
  }

  key(index) {
    const keys = Array.from(this.store.keys());
    return keys[index] ?? null;
  }

  removeItem(key) {
    this.store.delete(String(key));
  }

  setItem(key, value) {
    this.store.set(String(key), String(value));
  }
}

describe("caseSnapshotStore", () => {
  const originalLocalStorage = globalThis.localStorage;

  beforeEach(() => {
    globalThis.localStorage = new LocalStorageMock();
  });

  afterEach(() => {
    globalThis.localStorage = originalLocalStorage;
  });

  it("roundtrips snapshot encrypt→decrypt", async () => {
    const userId = "tester";
    const registryUuid = "00000000-0000-0000-0000-000000000001";
    const { vmk } = await initNewVault("pw", userId);

    const snapshot = {
      registry_uuid: registryUuid,
      total_work_rvu: 12.34,
      estimated_payment: 567.89,
      per_code_billing: [
        { code: "31624", work_rvu: 3.5 },
        { code: "31625", work_rvu: 4.0 },
      ],
      registry: {
        billing: { cpt_codes: [{ code: "31624" }, { code: "31625" }] },
      },
    };

    const meta = await persistCaseSnapshot(vmk, userId, registryUuid, snapshot);
    expect(meta?.registry_uuid).toBe(registryUuid);
    expect(meta?.cpt_count).toBe(2);

    const loaded = await loadCaseSnapshot(vmk, userId, registryUuid);
    expect(loaded).toEqual(snapshot);

    const metaRows = listCaseSnapshotMeta(userId);
    expect(metaRows.length).toBe(1);
    expect(metaRows[0].registry_uuid).toBe(registryUuid);
    expect(metaRows[0].cpt_count).toBe(2);
    expect(metaRows[0].total_work_rvu).toBe(12.34);
  });

  it("reassembles chunked snapshots correctly", async () => {
    const userId = "tester";
    const registryUuid = "00000000-0000-0000-0000-000000000002";
    const { vmk } = await initNewVault("pw", userId);

    const bigText = "x".repeat(1_000_000);
    const snapshot = {
      registry_uuid: registryUuid,
      registry: { note_stub: bigText },
      per_code_billing: [],
      total_work_rvu: 0,
      estimated_payment: null,
    };

    const meta = await persistCaseSnapshot(vmk, userId, registryUuid, snapshot);
    expect(meta?.registry_uuid).toBe(registryUuid);
    expect(meta?.chunk_count).toBeGreaterThan(1);

    const recordKey = `procsuite.vault.snapshot.v1:${userId}:${registryUuid}`;
    const rawRecord = globalThis.localStorage.getItem(recordKey);
    expect(rawRecord).toBeTruthy();

    const record = JSON.parse(rawRecord);
    expect(record.chunk_count).toBeGreaterThan(1);
    expect(record.ciphertext_b64).toBeUndefined();

    const firstChunkKey = `procsuite.vault.snapshot.v1:${userId}:${registryUuid}:chunk:0`;
    expect(globalThis.localStorage.getItem(firstChunkKey)).toBeTruthy();

    const loaded = await loadCaseSnapshot(vmk, userId, registryUuid);
    expect(String(loaded?.registry?.note_stub || "").length).toBe(1_000_000);
    expect(loaded).toEqual(snapshot);
  });
});

