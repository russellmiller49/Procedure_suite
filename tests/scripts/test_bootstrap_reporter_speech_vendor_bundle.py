from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "ops" / "tools" / "bootstrap_reporter_speech_vendor_bundle.py"
    spec = importlib.util.spec_from_file_location("bootstrap_reporter_speech_vendor_bundle", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_bootstrap_reporter_speech_vendor_bundle_declares_expected_core_files(tmp_path: Path) -> None:
    module = _load_module()
    model_files = tuple(module.MODEL_TEXT_FILES) + tuple(module.MODEL_ONNX_FILES)

    assert tuple(module.DEFAULT_MODEL_VARIANTS) == ("base", "tiny")
    assert module.MODEL_VARIANTS["base"]["repo_id"] == "Xenova/whisper-base.en"
    assert module.MODEL_VARIANTS["tiny"]["repo_id"] == "Xenova/whisper-tiny.en"
    assert "config.json" in model_files
    assert "generation_config.json" in model_files
    assert "preprocessor_config.json" in model_files
    assert "tokenizer.json" in model_files
    assert "onnx/encoder_model_quantized.onnx" in model_files
    assert "onnx/decoder_model_merged_quantized.onnx" in model_files
    assert "ort-wasm.wasm" in tuple(module.TRANSFORMERS_WASM_FILES)


def test_bootstrap_reporter_speech_vendor_bundle_dry_run_resolves_dirs_without_writing(
    tmp_path: Path,
) -> None:
    module = _load_module()

    atlas_dir = tmp_path / "atlas" / "speech_whisper_base_en"
    classic_dir = tmp_path / "classic" / "speech_whisper_base_en"
    result = module.ensure_reporter_speech_vendor_bundle(
        repo_id="Xenova/whisper-base.en",
        revision="main",
        models=("base", "tiny"),
        atlas_vendor_dir=atlas_dir,
        classic_vendor_dir=classic_dir,
        include_classic=True,
        force=False,
        dry_run=True,
    )

    assert result.atlas_vendor_dir == atlas_dir
    assert result.atlas_runtime_dir == atlas_dir.parent / "transformers"
    assert result.classic_vendor_dir == classic_dir
    assert result.classic_runtime_dir == classic_dir.parent / "transformers"
    assert set(result.models) == {"base", "tiny"}
    assert result.models["base"].atlas_vendor_dir == atlas_dir
    assert result.models["tiny"].atlas_vendor_dir == atlas_dir.parent / "speech_whisper_tiny_en"
    assert result.models["base"].classic_vendor_dir == classic_dir
    assert result.models["tiny"].classic_vendor_dir == classic_dir.parent / "speech_whisper_tiny_en"
    assert atlas_dir.exists() is False
    assert classic_dir.exists() is False
