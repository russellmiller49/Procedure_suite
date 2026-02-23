const CRYPTO_VERSION = 1;
const DEFAULT_PBKDF2_ITERATIONS = 210000;
const PBKDF2_HASH = "PBKDF2-SHA256";

const WRAP_AAD_SCOPE = "vault-wrap";
const RECORD_AAD_SCOPE = "vault-record";
const encoder = new TextEncoder();
const decoder = new TextDecoder();

function asBuffer(bytes) {
  const copy = new Uint8Array(bytes.byteLength);
  copy.set(bytes);
  return copy.buffer;
}

function getSubtle() {
  const subtle = globalThis.crypto?.subtle;
  if (!subtle) throw new Error("WebCrypto SubtleCrypto is unavailable");
  return subtle;
}

function buildWrapAad(userId, cryptoVersion) {
  return asBuffer(encoder.encode(`${WRAP_AAD_SCOPE}|v${cryptoVersion}|u:${userId}`));
}

function buildRecordAad(userId, registryUuid, cryptoVersion) {
  return asBuffer(
    encoder.encode(`${RECORD_AAD_SCOPE}|v${cryptoVersion}|u:${userId}|r:${String(registryUuid || "").toLowerCase()}`)
  );
}

function randomBytes(size) {
  const bytes = new Uint8Array(size);
  globalThis.crypto.getRandomValues(bytes);
  return bytes;
}

export function bytesToBase64(bytes) {
  let binary = "";
  const chunkSize = 0x8000;
  for (let i = 0; i < bytes.length; i += chunkSize) {
    const chunk = bytes.subarray(i, i + chunkSize);
    binary += String.fromCharCode(...chunk);
  }
  if (typeof globalThis.btoa === "function") return globalThis.btoa(binary);
  throw new Error("No base64 encoder available");
}

export function base64ToBytes(base64) {
  if (typeof base64 !== "string") throw new Error("Invalid base64 input");
  if (typeof globalThis.atob !== "function") throw new Error("No base64 decoder available");
  const binary = globalThis.atob(base64);
  const out = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) out[i] = binary.charCodeAt(i);
  return out;
}

async function deriveKekFromPassword(password, saltBytes, iterations) {
  const subtle = getSubtle();
  const keyMaterial = await subtle.importKey(
    "raw",
    asBuffer(encoder.encode(String(password || ""))),
    { name: "PBKDF2" },
    false,
    ["deriveKey"]
  );
  return subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: asBuffer(saltBytes),
      iterations,
      hash: "SHA-256",
    },
    keyMaterial,
    { name: "AES-GCM", length: 256 },
    false,
    ["wrapKey", "unwrapKey"]
  );
}

export async function initNewVault(password, userId) {
  const subtle = getSubtle();
  const vmk = await subtle.generateKey({ name: "AES-GCM", length: 256 }, true, ["encrypt", "decrypt"]);
  const salt = randomBytes(16);
  const iv = randomBytes(12);
  const kek = await deriveKekFromPassword(password, salt, DEFAULT_PBKDF2_ITERATIONS);
  const wrapped = await subtle.wrapKey("raw", vmk, kek, {
    name: "AES-GCM",
    iv: asBuffer(iv),
    additionalData: buildWrapAad(userId, CRYPTO_VERSION),
    tagLength: 128,
  });

  return {
    settingsPayload: {
      wrapped_vmk_b64: bytesToBase64(new Uint8Array(wrapped)),
      wrap_iv_b64: bytesToBase64(iv),
      kdf_salt_b64: bytesToBase64(salt),
      kdf_iterations: DEFAULT_PBKDF2_ITERATIONS,
      kdf_hash: PBKDF2_HASH,
      crypto_version: CRYPTO_VERSION,
    },
    vmk,
  };
}

export async function unlockVault(password, userId, settings) {
  if (!settings || Number(settings.crypto_version) !== CRYPTO_VERSION) {
    throw new Error("Unsupported crypto version");
  }
  const subtle = getSubtle();
  const salt = base64ToBytes(settings.kdf_salt_b64);
  const iv = base64ToBytes(settings.wrap_iv_b64);
  const wrapped = base64ToBytes(settings.wrapped_vmk_b64);
  const kek = await deriveKekFromPassword(password, salt, Number(settings.kdf_iterations || 0));

  return subtle.unwrapKey(
    "raw",
    asBuffer(wrapped),
    kek,
    {
      name: "AES-GCM",
      iv: asBuffer(iv),
      additionalData: buildWrapAad(userId, CRYPTO_VERSION),
      tagLength: 128,
    },
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
  );
}

export async function encryptPatientData(vmk, userId, registryUuid, patientJson) {
  const subtle = getSubtle();
  const iv = randomBytes(12);
  const plaintext = encoder.encode(JSON.stringify(patientJson));
  const ciphertext = await subtle.encrypt(
    {
      name: "AES-GCM",
      iv: asBuffer(iv),
      additionalData: buildRecordAad(userId, registryUuid, CRYPTO_VERSION),
      tagLength: 128,
    },
    vmk,
    asBuffer(plaintext)
  );

  return {
    registry_uuid: registryUuid,
    ciphertext_b64: bytesToBase64(new Uint8Array(ciphertext)),
    iv_b64: bytesToBase64(iv),
    crypto_version: CRYPTO_VERSION,
  };
}

export async function decryptPatientData(vmk, userId, registryUuid, record) {
  if (!record || Number(record.crypto_version) !== CRYPTO_VERSION) {
    throw new Error("Unsupported crypto version");
  }
  const subtle = getSubtle();
  const ciphertext = base64ToBytes(record.ciphertext_b64);
  const iv = base64ToBytes(record.iv_b64);
  const plaintext = await subtle.decrypt(
    {
      name: "AES-GCM",
      iv: asBuffer(iv),
      additionalData: buildRecordAad(userId, registryUuid, CRYPTO_VERSION),
      tagLength: 128,
    },
    vmk,
    asBuffer(ciphertext)
  );
  return JSON.parse(decoder.decode(plaintext));
}

function userHeaders(userId) {
  return {
    "Content-Type": "application/json",
    "X-User-Id": String(userId || "").trim(),
  };
}

async function safeJson(response) {
  const text = await response.text();
  if (!text) return null;
  return JSON.parse(text);
}

async function safeDetail(response, { maxLen = 280 } = {}) {
  try {
    const text = await response.text();
    if (!text) return "";
    try {
      const parsed = JSON.parse(text);
      const detail = parsed?.detail;
      if (typeof detail === "string" && detail.trim()) return detail.trim();
    } catch {
      // ignore JSON parse failures
    }
    return String(text).trim().slice(0, maxLen);
  } catch {
    return "";
  }
}

export async function unlockOrInitVault({ apiBase = "/api/v1/vault", userId, password }) {
  const settingsRes = await fetch(`${apiBase}/settings`, {
    method: "GET",
    headers: userHeaders(userId),
  });

  if (settingsRes.status === 404) {
    const { settingsPayload, vmk } = await initNewVault(password, userId);
    const putRes = await fetch(`${apiBase}/settings`, {
      method: "PUT",
      headers: userHeaders(userId),
      body: JSON.stringify(settingsPayload),
    });
    if (!putRes.ok) {
      const detail = await safeDetail(putRes);
      throw new Error(
        `Failed to save new vault settings (${putRes.status}${detail ? `): ${detail}` : ")"}`,
      );
    }
    return { vmk, created: true };
  }

  if (!settingsRes.ok) {
    const detail = await safeDetail(settingsRes);
    throw new Error(
      `Failed to load vault settings (${settingsRes.status}${detail ? `): ${detail}` : ")"}`,
    );
  }
  const settings = await safeJson(settingsRes);
  const vmk = await unlockVault(password, userId, settings);
  return { vmk, created: false };
}

export async function loadVaultPatients({ apiBase = "/api/v1/vault", userId, vmk }) {
  const res = await fetch(`${apiBase}/records`, {
    method: "GET",
    headers: userHeaders(userId),
  });
  if (!res.ok) {
    const detail = await safeDetail(res);
    throw new Error(`Failed to load vault records (${res.status}${detail ? `): ${detail}` : ")"}`);
  }
  const rows = (await safeJson(res)) || [];
  const map = new Map();
  for (const row of rows) {
    const registryUuid = String(row?.registry_uuid || "");
    if (!registryUuid) continue;
    const decrypted = await decryptPatientData(vmk, userId, registryUuid, row);
    map.set(registryUuid, decrypted);
  }
  return map;
}

export async function upsertVaultPatient({ apiBase = "/api/v1/vault", userId, vmk, registryUuid, patientJson }) {
  const payload = await encryptPatientData(vmk, userId, registryUuid, patientJson);
  const res = await fetch(`${apiBase}/record`, {
    method: "PUT",
    headers: userHeaders(userId),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const detail = await safeDetail(res);
    throw new Error(`Failed to save vault record (${res.status}${detail ? `): ${detail}` : ")"}`);
  }
  return safeJson(res);
}

export async function deleteVaultPatient({ apiBase = "/api/v1/vault", userId, registryUuid }) {
  const res = await fetch(`${apiBase}/records/${encodeURIComponent(registryUuid)}`, {
    method: "DELETE",
    headers: userHeaders(userId),
  });
  if (!res.ok) {
    const detail = await safeDetail(res);
    throw new Error(`Failed to delete vault record (${res.status}${detail ? `): ${detail}` : ")"}`);
  }
  return safeJson(res);
}
