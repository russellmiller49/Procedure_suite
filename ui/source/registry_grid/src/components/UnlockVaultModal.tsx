import React, { useEffect, useMemo, useState } from "react";

import { useVault } from "../context/VaultContext";

type UnlockVaultModalProps = {
  open: boolean;
  userId: string;
  apiBasePath?: string;
  onClose?: () => void;
  onUnlocked?: () => void;
};

const DEFAULT_API_BASE = "/api/v1/vault";

export function UnlockVaultModal({
  open,
  userId,
  apiBasePath = DEFAULT_API_BASE,
  onClose,
  onUnlocked,
}: UnlockVaultModalProps) {
  const { isLocked, isUnlocking, unlock } = useVault();
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const [hasSettings, setHasSettings] = useState<boolean | null>(null);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setPassword("");
    setError(null);
    setHasSettings(null);
    setChecking(true);

    (async () => {
      try {
        const res = await fetch(`${apiBasePath}/settings`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "X-User-Id": userId,
          },
        });
        if (cancelled) return;
        if (res.status === 404) {
          setHasSettings(false);
          return;
        }
        if (!res.ok) {
          throw new Error(`Failed to load vault settings (${res.status})`);
        }
        setHasSettings(true);
      } catch (err) {
        if (!cancelled) setError(String((err as Error)?.message || err));
      } finally {
        if (!cancelled) setChecking(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [apiBasePath, open, userId]);

  const title = useMemo(() => {
    if (hasSettings === false) return "Create Local Vault";
    return "Unlock Local Vault";
  }, [hasSettings]);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!password) {
      setError("Password is required");
      return;
    }
    setError(null);
    try {
      await unlock({ userId, password });
      setPassword("");
      onUnlocked?.();
      onClose?.();
    } catch (err) {
      setError(String((err as Error)?.message || err));
    }
  }

  if (!open) return null;

  return (
    <div className="ps-vault-modal-backdrop" role="presentation">
      <div className="ps-vault-modal" role="dialog" aria-modal="true" aria-label={title}>
        <div className="ps-vault-modal-title">{title}</div>
        {hasSettings === false ? (
          <p className="ps-vault-modal-copy">
            First-time setup: your browser will create and wrap a vault key, then store only ciphertext settings on
            the server.
          </p>
        ) : (
          <p className="ps-vault-modal-copy">
            Enter your vault password to decrypt patient labels in-memory. Passwords are never stored.
          </p>
        )}

        <form onSubmit={onSubmit} className="ps-vault-modal-form">
          <label className="ps-vault-modal-label" htmlFor="vaultPasswordInput">
            Vault Password
          </label>
          <input
            id="vaultPasswordInput"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            disabled={checking || isUnlocking || !isLocked}
          />

          {error ? <div className="ps-vault-modal-error">{error}</div> : null}

          <div className="ps-vault-modal-actions">
            <button type="button" onClick={onClose} disabled={isUnlocking}>
              Cancel
            </button>
            <button type="submit" disabled={checking || isUnlocking || !isLocked}>
              {hasSettings === false ? "Initialize Vault" : "Unlock"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

