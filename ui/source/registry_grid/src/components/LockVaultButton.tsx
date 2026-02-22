import React from "react";

import { useVault } from "../context/VaultContext";

type LockVaultButtonProps = {
  className?: string;
};

export function LockVaultButton({ className }: LockVaultButtonProps) {
  const { isLocked, lock } = useVault();
  if (isLocked) return null;

  return (
    <button type="button" className={className} onClick={lock}>
      Lock Vault
    </button>
  );
}

