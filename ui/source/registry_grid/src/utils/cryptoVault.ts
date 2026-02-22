export const CRYPTO_VERSION = 1 as const;
export const DEFAULT_PBKDF2_ITERATIONS = 210_000;
export const PBKDF2_HASH = "PBKDF2-SHA256";

export type VaultSettingsPayload = {
  wrapped_vmk_b64: string;
  wrap_iv_b64: string;
  kdf_salt_b64: string;
  kdf_iterations: number;
  kdf_hash: string;
  crypto_version: typeof CRYPTO_VERSION;
};

export type VaultRecordPayload = {
  registry_uuid: string;
  ciphertext_b64: string;
  iv_b64: string;
  crypto_version: typeof CRYPTO_VERSION;
};

type VaultRecordLike = {
  ciphertext_b64: string;
  iv_b64: string;
  crypto_version: number;
};

const WRAP_AAD_SCOPE = "vault-wrap";
const RECORD_AAD_SCOPE = "vault-record";

const encoder = new TextEncoder();
const decoder = new TextDecoder();

function getSubtle(): SubtleCrypto {
  const subtle = globalThis.crypto?.subtle;
  if (!subtle) {
    throw new Error("WebCrypto SubtleCrypto is unavailable");
  }
  return subtle;
}

function getBufferCtor():
  | {
      from(input: string, encoding?: string): { toString(encoding?: string): string };
    }
  | null {
  const maybe = (globalThis as unknown as { Buffer?: unknown }).Buffer;
  if (!maybe || typeof maybe !== "function") return null;
  return maybe as unknown as {
    from(input: string, encoding?: string): { toString(encoding?: string): string };
  };
}

function asBufferSource(bytes: Uint8Array): ArrayBuffer {
  const normalized = new Uint8Array(bytes.byteLength);
  normalized.set(bytes);
  return normalized.buffer;
}

export function bytesToBase64(bytes: Uint8Array): string {
  let binary = "";
  const chunkSize = 0x8000;
  for (let i = 0; i < bytes.length; i += chunkSize) {
    const chunk = bytes.subarray(i, i + chunkSize);
    binary += String.fromCharCode(...chunk);
  }

  if (typeof globalThis.btoa === "function") {
    return globalThis.btoa(binary);
  }
  const BufferCtor = getBufferCtor();
  if (BufferCtor) {
    return BufferCtor.from(binary, "binary").toString("base64");
  }
  throw new Error("No base64 encoder available");
}

export function base64ToBytes(base64: string): Uint8Array {
  let binary: string;
  if (typeof globalThis.atob === "function") {
    binary = globalThis.atob(base64);
  } else {
    const BufferCtor = getBufferCtor();
    if (!BufferCtor) throw new Error("No base64 decoder available");
    binary = BufferCtor.from(base64, "base64").toString("binary");
  }
  const out = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    out[i] = binary.charCodeAt(i);
  }
  return out;
}

function randomBytes(size: number): Uint8Array {
  const bytes = new Uint8Array(size);
  globalThis.crypto.getRandomValues(bytes);
  return bytes;
}

function buildWrapAad(userId: string, cryptoVersion: number): ArrayBuffer {
  return asBufferSource(encoder.encode(`${WRAP_AAD_SCOPE}|v${cryptoVersion}|u:${userId}`));
}

function buildRecordAad(userId: string, registryUuid: string, cryptoVersion: number): ArrayBuffer {
  return asBufferSource(
    encoder.encode(`${RECORD_AAD_SCOPE}|v${cryptoVersion}|u:${userId}|r:${registryUuid.toLowerCase()}`),
  );
}

export async function deriveKekFromPassword(
  password: string,
  _userId: string,
  saltBytes: Uint8Array,
  iterations: number,
): Promise<CryptoKey> {
  const subtle = getSubtle();
  const keyMaterial = await subtle.importKey(
    "raw",
    asBufferSource(encoder.encode(password)),
    { name: "PBKDF2" },
    false,
    ["deriveKey"],
  );

  return subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: asBufferSource(saltBytes),
      iterations,
      hash: "SHA-256",
    },
    keyMaterial,
    {
      name: "AES-GCM",
      length: 256,
    },
    false,
    ["wrapKey", "unwrapKey"],
  );
}

export async function initNewVault(
  password: string,
  userId: string,
): Promise<{ settingsPayload: VaultSettingsPayload; vmk: CryptoKey }> {
  const subtle = getSubtle();
  const vmk = await subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"],
  );

  const salt = randomBytes(16);
  const iv = randomBytes(12);
  const kek = await deriveKekFromPassword(password, userId, salt, DEFAULT_PBKDF2_ITERATIONS);
  const wrapped = await subtle.wrapKey("raw", vmk, kek, {
    name: "AES-GCM",
    iv: asBufferSource(iv),
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

export async function unlockVault(
  password: string,
  userId: string,
  settings: VaultSettingsPayload,
): Promise<CryptoKey> {
  if (settings.crypto_version !== CRYPTO_VERSION) {
    throw new Error(`Unsupported crypto_version: ${settings.crypto_version}`);
  }
  const subtle = getSubtle();
  const salt = base64ToBytes(settings.kdf_salt_b64);
  const iv = base64ToBytes(settings.wrap_iv_b64);
  const wrapped = base64ToBytes(settings.wrapped_vmk_b64);
  const kek = await deriveKekFromPassword(password, userId, salt, settings.kdf_iterations);

  return subtle.unwrapKey(
    "raw",
    asBufferSource(wrapped),
    kek,
    {
      name: "AES-GCM",
      iv: asBufferSource(iv),
      additionalData: buildWrapAad(userId, settings.crypto_version),
      tagLength: 128,
    },
    {
      name: "AES-GCM",
      length: 256,
    },
    true,
    ["encrypt", "decrypt"],
  );
}

export async function encryptPatientData(
  vmk: CryptoKey,
  userId: string,
  registryUuid: string,
  patientJson: unknown,
): Promise<VaultRecordPayload> {
  const subtle = getSubtle();
  const iv = randomBytes(12);
  const plaintext = encoder.encode(JSON.stringify(patientJson));
  const ciphertext = await subtle.encrypt(
    {
      name: "AES-GCM",
      iv: asBufferSource(iv),
      additionalData: buildRecordAad(userId, registryUuid, CRYPTO_VERSION),
      tagLength: 128,
    },
    vmk,
    asBufferSource(plaintext),
  );

  return {
    registry_uuid: registryUuid,
    ciphertext_b64: bytesToBase64(new Uint8Array(ciphertext)),
    iv_b64: bytesToBase64(iv),
    crypto_version: CRYPTO_VERSION,
  };
}

export async function decryptPatientData(
  vmk: CryptoKey,
  userId: string,
  registryUuid: string,
  record: VaultRecordLike,
): Promise<unknown> {
  if (record.crypto_version !== CRYPTO_VERSION) {
    throw new Error(`Unsupported crypto_version: ${record.crypto_version}`);
  }
  const subtle = getSubtle();
  const ciphertext = base64ToBytes(record.ciphertext_b64);
  const iv = base64ToBytes(record.iv_b64);
  const plaintext = await subtle.decrypt(
    {
      name: "AES-GCM",
      iv: asBufferSource(iv),
      additionalData: buildRecordAad(userId, registryUuid, record.crypto_version),
      tagLength: 128,
    },
    vmk,
    asBufferSource(ciphertext),
  );

  return JSON.parse(decoder.decode(plaintext));
}
