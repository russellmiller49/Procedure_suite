import { webcrypto } from "node:crypto";
import { beforeAll, describe, expect, it } from "vitest";

import {
  base64ToBytes,
  bytesToBase64,
  decryptPatientData,
  encryptPatientData,
  initNewVault,
  normalizeVaultPatientData,
  unlockVault,
} from "../utils/cryptoVault";

beforeAll(() => {
  if (!globalThis.crypto) {
    Object.defineProperty(globalThis, "crypto", {
      value: webcrypto,
      configurable: true,
      writable: true,
    });
  }
});

describe("cryptoVault", () => {
  it("roundtrips base64 helpers", () => {
    const input = new Uint8Array([1, 2, 3, 255, 128, 64, 32, 16]);
    const encoded = bytesToBase64(input);
    const decoded = base64ToBytes(encoded);
    expect(Array.from(decoded)).toEqual(Array.from(input));
  });

  it("encrypts/decrypts patient data with VMK", async () => {
    const userId = "user_a";
    const password = "Correct-Horse-Battery-Staple!";
    const registryUuid = "11111111-1111-1111-1111-111111111111";
    const patientJson = {
      patient_label: "Jane Doe",
      index_date: "2026-02-23",
      local_meta: { mrn: "123456" },
      registry_uuid: registryUuid,
      saved_at: "2026-02-23T12:00:00.000Z",
    };

    const { settingsPayload, vmk } = await initNewVault(password, userId);
    const wrappedVmk = await unlockVault(password, userId, settingsPayload);
    const record = await encryptPatientData(vmk, userId, registryUuid, patientJson);
    const decrypted = await decryptPatientData(wrappedVmk, userId, registryUuid, record);

    expect(decrypted).toEqual({
      schema_version: 2,
      patient_label: "Jane Doe",
      index_date: "2026-02-23",
      local_meta: { mrn: "123456" },
      registry_uuid: registryUuid,
      saved_at: "2026-02-23T12:00:00.000Z",
    });
  });

  it("fails decrypt when registry_uuid in AAD mismatches", async () => {
    const userId = "user_a";
    const password = "correct-password";
    const { settingsPayload, vmk } = await initNewVault(password, userId);
    const unlocked = await unlockVault(password, userId, settingsPayload);
    const record = await encryptPatientData(
      vmk,
      userId,
      "22222222-2222-2222-2222-222222222222",
      { patient_name: "Mismatch" },
    );

    await expect(
      decryptPatientData(unlocked, userId, "33333333-3333-3333-3333-333333333333", record),
    ).rejects.toThrow();
  });

  it("fails unlock with wrong password", async () => {
    const userId = "user_a";
    const { settingsPayload } = await initNewVault("right-password", userId);
    await expect(unlockVault("wrong-password", userId, settingsPayload)).rejects.toThrow();
  });

  it("normalizes legacy vault payloads", () => {
    const registryUuid = "55555555-5555-5555-5555-555555555555";
    const normalized = normalizeVaultPatientData(
      {
        name: "Legacy Name",
        mrn: "MRN-9",
        saved_at: "2026-01-01T00:00:00.000Z",
      },
      registryUuid,
    );
    expect(normalized).toEqual({
      schema_version: 2,
      patient_label: "Legacy Name",
      index_date: null,
      local_meta: { mrn: "MRN-9" },
      registry_uuid: registryUuid,
      saved_at: "2026-01-01T00:00:00.000Z",
    });
  });
});
