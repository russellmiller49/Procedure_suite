#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${MODEL_BUNDLE_S3_URI_PYTORCH:-}" ]]; then
  echo "Missing MODEL_BUNDLE_S3_URI_PYTORCH (example: s3://.../pytorch/bundle.tar.gz)" >&2
  exit 2
fi

DEST_DIR="${REGISTRY_RUNTIME_DIR:-data/models/registry_runtime}"

echo "[dev_pull_model] Downloading: ${MODEL_BUNDLE_S3_URI_PYTORCH}"
echo "[dev_pull_model] Extracting to: ${DEST_DIR}"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

TARBALL="${TMPDIR}/bundle.tar.gz"
aws s3 cp "${MODEL_BUNDLE_S3_URI_PYTORCH}" "${TARBALL}"

rm -rf "${DEST_DIR}"
mkdir -p "${DEST_DIR}"
tar -xzf "${TARBALL}" -C "${DEST_DIR}"

echo "[dev_pull_model] Done."

