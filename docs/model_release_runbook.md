# Model Release Runbook (Registry Predictor)

This runbook describes how to package and deploy the **registry predictor** model bundles.

## Bundle types

### A) Local-dev PyTorch bundle (no ONNX)

**Contents (tarball root):**
- `config.json`
- `model.safetensors` (or `pytorch_model.bin`)
- `tokenizer/`
- `thresholds.json`
- `label_order.json`
- `registry_label_fields.json`
- `manifest.json`

**S3 destination:**
- `s3://procedure-suite-models/deploy/registry/<version>/pytorch/`
  - `bundle.tar.gz`
  - `manifest.json`

### B) Production ONNX bundle

Same structure, but includes:
- `registry_model_int8.onnx`

**S3 destination:**
- `s3://procedure-suite-models/deploy/registry/<version>/onnx/`

> Note: ONNX export/upload may be intentionally skipped during active model iteration.

## Build + upload (PyTorch)

From the `proc_suite/` repo:

```bash
VERSION="distilled-$(date +%Y%m%d)-$(git rev-parse --short HEAD)"
python ops/tools/build_registry_bundle.py --src distilled --out-dir dist/registry_bundle --backend pytorch --version "$VERSION"
./ops/tools/upload_registry_bundle.sh "$VERSION" pytorch dist/registry_bundle
```

## Runtime configuration (IU / FastAPI)

### Common env vars

- `MODEL_BACKEND=pytorch` or `MODEL_BACKEND=onnx`
- `REGISTRY_RUNTIME_DIR=data/models/registry_runtime` (optional override)

### PyTorch mode

- `MODEL_BUNDLE_S3_URI_PYTORCH=s3://procedure-suite-models/deploy/registry/<version>/pytorch/bundle.tar.gz`

Resolved paths (set by bootstrap):
- `REGISTRY_MODEL_DIR` (directory containing `config.json` + weights)
- `REGISTRY_TOKENIZER_PATH`
- `REGISTRY_THRESHOLDS_PATH`
- `REGISTRY_LABEL_FIELDS_PATH`

### ONNX mode

- `MODEL_BUNDLE_S3_URI_ONNX=s3://procedure-suite-models/deploy/registry/<version>/onnx/bundle.tar.gz`

Resolved paths (set by bootstrap):
- `REGISTRY_ONNX_MODEL_PATH`
- `REGISTRY_TOKENIZER_PATH`
- `REGISTRY_THRESHOLDS_PATH`
- `REGISTRY_LABEL_FIELDS_PATH`

## Verification

- The backend `/qa/run` response includes:
  - `model_backend`
  - `model_version` (from `manifest.json`, when present)

