from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

import app.registry.infra.model_provider as model_provider_module
from app.registry.infra.model_provider import RegistryModelProvider


def test_model_provider_uses_onnx_backend_when_configured(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class FakeOnnxPredictor:
        def __init__(self, **_: object) -> None:
            self.available = True
            self.labels = ["label_a"]

    fake_onnx_module = types.ModuleType("app.registry.inference_onnx")
    fake_onnx_module.ONNXRegistryPredictor = FakeOnnxPredictor

    (tmp_path / "registry_model.onnx").write_text("fake", encoding="utf-8")
    (tmp_path / "tokenizer").mkdir()
    (tmp_path / "thresholds.json").write_text("{}", encoding="utf-8")

    monkeypatch.setitem(sys.modules, "app.registry.inference_onnx", fake_onnx_module)
    monkeypatch.setattr(model_provider_module, "resolve_model_backend", lambda: "onnx")
    monkeypatch.setattr(model_provider_module, "get_registry_runtime_dir", lambda: tmp_path)

    provider = RegistryModelProvider()
    predictor = provider.get_predictor()

    assert isinstance(predictor, FakeOnnxPredictor)
    assert provider.get_predictor() is predictor


def test_model_provider_falls_back_to_sklearn_predictor(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class FakeUnavailableOnnxPredictor:
        def __init__(self, **_: object) -> None:
            self.available = False
            self.labels = []

    class FakeRegistryMLPredictor:
        init_calls = 0

        def __init__(self) -> None:
            type(self).init_calls += 1
            self.available = True
            self.labels = ["field_a", "field_b"]

    fake_onnx_module = types.ModuleType("app.registry.inference_onnx")
    fake_onnx_module.ONNXRegistryPredictor = FakeUnavailableOnnxPredictor

    monkeypatch.setitem(sys.modules, "app.registry.inference_onnx", fake_onnx_module)
    monkeypatch.setattr(model_provider_module, "resolve_model_backend", lambda: "default")
    monkeypatch.setattr(model_provider_module, "get_registry_runtime_dir", lambda: tmp_path)
    monkeypatch.setattr(model_provider_module, "RegistryMLPredictor", FakeRegistryMLPredictor)

    provider = RegistryModelProvider()
    predictor = provider.get_predictor()

    assert isinstance(predictor, FakeRegistryMLPredictor)
    assert FakeRegistryMLPredictor.init_calls == 1


def test_model_provider_raises_when_onnx_required_but_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class FakeUnavailableOnnxPredictor:
        def __init__(self, **_: object) -> None:
            self.available = False
            self.labels = []

    fake_onnx_module = types.ModuleType("app.registry.inference_onnx")
    fake_onnx_module.ONNXRegistryPredictor = FakeUnavailableOnnxPredictor

    monkeypatch.setitem(sys.modules, "app.registry.inference_onnx", fake_onnx_module)
    monkeypatch.setattr(model_provider_module, "resolve_model_backend", lambda: "onnx")
    monkeypatch.setattr(model_provider_module, "get_registry_runtime_dir", lambda: tmp_path)

    provider = RegistryModelProvider()
    with pytest.raises(RuntimeError, match="MODEL_BACKEND=onnx"):
        provider.get_predictor()
