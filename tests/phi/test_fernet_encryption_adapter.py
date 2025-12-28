"""Tests for FernetEncryptionAdapter."""

from __future__ import annotations

import os

import pytest

from modules.phi.adapters.fernet_encryption import FernetEncryptionAdapter


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("PHI_ENCRYPTION_KEY", "tWw3G2Nn7n1ZlqvJ6mW1FjwF2CJK8H4XfRrx5mE0Gd8=")
    yield


def test_encrypt_decrypt_round_trip():
    adapter = FernetEncryptionAdapter()
    plaintext = "Patient X synthetic note."

    ciphertext, algorithm, key_version = adapter.encrypt(plaintext)
    assert algorithm == "FERNET"
    assert key_version == 1
    assert ciphertext != plaintext.encode()

    decrypted = adapter.decrypt(ciphertext, algorithm, key_version)
    assert decrypted == plaintext


def test_decrypt_raises_on_wrong_algorithm():
    adapter = FernetEncryptionAdapter()
    ciphertext, algorithm, key_version = adapter.encrypt("Synthetic PHI")

    with pytest.raises(ValueError):
        adapter.decrypt(ciphertext, "OTHER", key_version)
