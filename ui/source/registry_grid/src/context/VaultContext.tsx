import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  decryptPatientData,
  encryptPatientData,
  initNewVault,
  type VaultRecordPayload,
  type VaultSettingsPayload,
  unlockVault,
} from "../utils/cryptoVault";

type VaultRecordResponse = VaultRecordPayload & {
  user_id: string;
  created_at: string;
  updated_at: string;
};

type VaultContextValue = {
  isLocked: boolean;
  isUnlocking: boolean;
  unlockedUserId: string | null;
  patientMap: ReadonlyMap<string, unknown>;
  unlock: (params: { userId: string; password: string }) => Promise<void>;
  lock: () => void;
  upsertPatient: (registryUuid: string, patientJson: unknown) => Promise<void>;
  deletePatient: (registryUuid: string) => Promise<void>;
};

type VaultProviderProps = {
  children: React.ReactNode;
  apiBasePath?: string;
  idleTimeoutMs?: number;
};

type SettingsGetResponse = VaultSettingsPayload & {
  user_id: string;
  created_at: string;
  updated_at: string;
};

const DEFAULT_API_BASE = "/api/v1/vault";
const DEFAULT_IDLE_TIMEOUT_MS = 10 * 60 * 1000;

const VaultContext = createContext<VaultContextValue | null>(null);

async function parseJsonSafe<T>(response: Response): Promise<T | null> {
  const text = await response.text();
  if (!text) return null;
  return JSON.parse(text) as T;
}

function buildUserHeaders(userId: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-User-Id": userId,
  };
}

async function fetchSettings(
  apiBasePath: string,
  userId: string,
): Promise<{ exists: false } | { exists: true; settings: VaultSettingsPayload }> {
  const res = await fetch(`${apiBasePath}/settings`, {
    method: "GET",
    headers: buildUserHeaders(userId),
  });
  if (res.status === 404) return { exists: false };
  if (!res.ok) {
    throw new Error(`Failed to load vault settings (${res.status})`);
  }
  const body = await parseJsonSafe<SettingsGetResponse>(res);
  if (!body) throw new Error("Vault settings response is empty");
  return {
    exists: true,
    settings: {
      wrapped_vmk_b64: body.wrapped_vmk_b64,
      wrap_iv_b64: body.wrap_iv_b64,
      kdf_salt_b64: body.kdf_salt_b64,
      kdf_iterations: body.kdf_iterations,
      kdf_hash: body.kdf_hash,
      crypto_version: body.crypto_version,
    },
  };
}

async function putSettings(apiBasePath: string, userId: string, payload: VaultSettingsPayload): Promise<void> {
  const res = await fetch(`${apiBasePath}/settings`, {
    method: "PUT",
    headers: buildUserHeaders(userId),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Failed to save vault settings (${res.status})`);
  }
}

async function fetchRecords(apiBasePath: string, userId: string): Promise<VaultRecordResponse[]> {
  const res = await fetch(`${apiBasePath}/records`, {
    method: "GET",
    headers: buildUserHeaders(userId),
  });
  if (!res.ok) throw new Error(`Failed to load vault records (${res.status})`);
  const body = await parseJsonSafe<VaultRecordResponse[]>(res);
  return Array.isArray(body) ? body : [];
}

export function VaultProvider({
  children,
  apiBasePath = DEFAULT_API_BASE,
  idleTimeoutMs = DEFAULT_IDLE_TIMEOUT_MS,
}: VaultProviderProps) {
  const [isUnlocking, setIsUnlocking] = useState(false);
  const [unlockedUserId, setUnlockedUserId] = useState<string | null>(null);
  const [vmk, setVmk] = useState<CryptoKey | null>(null);
  const [patientMap, setPatientMap] = useState<Map<string, unknown>>(new Map());

  const idleTimerRef = useRef<number | null>(null);
  const isLocked = vmk === null;

  const clearIdleTimer = useCallback(() => {
    if (idleTimerRef.current !== null) {
      window.clearTimeout(idleTimerRef.current);
      idleTimerRef.current = null;
    }
  }, []);

  const lock = useCallback(() => {
    clearIdleTimer();
    setVmk(null);
    setUnlockedUserId(null);
    setPatientMap(new Map());
  }, [clearIdleTimer]);

  const armIdleTimer = useCallback(() => {
    if (idleTimeoutMs <= 0 || isLocked) return;
    clearIdleTimer();
    idleTimerRef.current = window.setTimeout(() => {
      lock();
    }, idleTimeoutMs);
  }, [clearIdleTimer, idleTimeoutMs, isLocked, lock]);

  const unlock = useCallback(
    async ({ userId, password }: { userId: string; password: string }) => {
      setIsUnlocking(true);
      try {
        const settingsResult = await fetchSettings(apiBasePath, userId);
        let resolvedVmk: CryptoKey;
        if (!settingsResult.exists) {
          const { settingsPayload, vmk: generatedVmk } = await initNewVault(password, userId);
          await putSettings(apiBasePath, userId, settingsPayload);
          resolvedVmk = generatedVmk;
        } else {
          resolvedVmk = await unlockVault(password, userId, settingsResult.settings);
        }

        const rows = await fetchRecords(apiBasePath, userId);
        const nextMap = new Map<string, unknown>();
        for (const row of rows) {
          const decrypted = await decryptPatientData(resolvedVmk, userId, row.registry_uuid, row);
          nextMap.set(row.registry_uuid, decrypted);
        }

        setVmk(resolvedVmk);
        setUnlockedUserId(userId);
        setPatientMap(nextMap);
        armIdleTimer();
      } catch (err) {
        // Never keep partial decrypt state after a failed unlock.
        lock();
        throw err;
      } finally {
        setIsUnlocking(false);
      }
    },
    [apiBasePath, armIdleTimer, lock],
  );

  const upsertPatient = useCallback(
    async (registryUuid: string, patientJson: unknown) => {
      if (!vmk || !unlockedUserId) throw new Error("Vault is locked");
      const payload = await encryptPatientData(vmk, unlockedUserId, registryUuid, patientJson);
      const res = await fetch(`${apiBasePath}/record`, {
        method: "PUT",
        headers: buildUserHeaders(unlockedUserId),
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        throw new Error(`Failed to save vault record (${res.status})`);
      }

      setPatientMap((prev) => {
        const next = new Map(prev);
        next.set(registryUuid, patientJson);
        return next;
      });
      armIdleTimer();
    },
    [apiBasePath, armIdleTimer, unlockedUserId, vmk],
  );

  const deletePatient = useCallback(
    async (registryUuid: string) => {
      if (!unlockedUserId) throw new Error("Vault is locked");
      const res = await fetch(`${apiBasePath}/records/${encodeURIComponent(registryUuid)}`, {
        method: "DELETE",
        headers: buildUserHeaders(unlockedUserId),
      });
      if (!res.ok) {
        throw new Error(`Failed to delete vault record (${res.status})`);
      }

      setPatientMap((prev) => {
        const next = new Map(prev);
        next.delete(registryUuid);
        return next;
      });
      armIdleTimer();
    },
    [apiBasePath, armIdleTimer, unlockedUserId],
  );

  useEffect(() => {
    if (isLocked || idleTimeoutMs <= 0) {
      clearIdleTimer();
      return;
    }

    const onActivity = () => armIdleTimer();
    const opts: AddEventListenerOptions = { passive: true };
    window.addEventListener("mousemove", onActivity, opts);
    window.addEventListener("mousedown", onActivity, opts);
    window.addEventListener("keydown", onActivity, opts);
    window.addEventListener("touchstart", onActivity, opts);
    window.addEventListener("scroll", onActivity, opts);
    armIdleTimer();

    return () => {
      window.removeEventListener("mousemove", onActivity);
      window.removeEventListener("mousedown", onActivity);
      window.removeEventListener("keydown", onActivity);
      window.removeEventListener("touchstart", onActivity);
      window.removeEventListener("scroll", onActivity);
      clearIdleTimer();
    };
  }, [armIdleTimer, clearIdleTimer, idleTimeoutMs, isLocked]);

  useEffect(() => {
    const onLogout = () => lock();
    window.addEventListener("logout", onLogout as EventListener);
    window.addEventListener("procsuite:logout", onLogout as EventListener);
    return () => {
      window.removeEventListener("logout", onLogout as EventListener);
      window.removeEventListener("procsuite:logout", onLogout as EventListener);
    };
  }, [lock]);

  const value = useMemo<VaultContextValue>(
    () => ({
      isLocked,
      isUnlocking,
      unlockedUserId,
      patientMap,
      unlock,
      lock,
      upsertPatient,
      deletePatient,
    }),
    [deletePatient, isLocked, isUnlocking, lock, patientMap, unlock, unlockedUserId, upsertPatient],
  );

  return <VaultContext.Provider value={value}>{children}</VaultContext.Provider>;
}

export function useVault(): VaultContextValue {
  const ctx = useContext(VaultContext);
  if (!ctx) {
    throw new Error("useVault must be used within VaultProvider");
  }
  return ctx;
}

