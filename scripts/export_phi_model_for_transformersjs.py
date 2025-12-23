#!/usr/bin/env python3
"""Export PHI DistilBERT model to transformers.js-compatible ONNX bundle."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from pathlib import Path

from modules.phi.adapters.phi_redactor_hybrid import (
    ANATOMICAL_TERMS,
    DEVICE_MANUFACTURERS,
    PROTECTED_DEVICE_NAMES,
)

MODEL_FILES = [
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "vocab.txt",
    "label_map.json",
]


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", default="artifacts/phi_distilbert_ner")
    ap.add_argument(
        "--out-dir",
        default="modules/api/static/phi_redactor/vendor/phi_distilbert_ner",
    )
    ap.add_argument("--quantize", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument(
        "--quantize-target",
        choices=["arm64", "avx2", "avx512", "avx512_vnni", "ppc64le", "tensorrt"],
        default=None,
    )
    ap.add_argument("--quantize-config", default=None)
    return ap


def run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        tool = cmd[0]
        raise RuntimeError(
            f"{tool} not found. Install with: pip install 'optimum[onnxruntime]' onnxruntime"
        ) from exc


def ensure_model_onnx(out_dir: Path, onnx_dir: Path) -> Path:
    onnx_dir.mkdir(parents=True, exist_ok=True)
    model_path = onnx_dir / "model.onnx"
    if model_path.exists():
        return model_path

    root_model = out_dir / "model.onnx"
    if root_model.exists():
        root_model.rename(model_path)
        return model_path

    candidates = sorted(out_dir.glob("*.onnx"))
    if not candidates:
        raise FileNotFoundError(f"No ONNX files found in {out_dir}")
    candidates[0].rename(model_path)
    return model_path


def write_protected_terms(out_dir: Path) -> None:
    terms = {
        "anatomy_terms": sorted({t.lower() for t in ANATOMICAL_TERMS}),
        "device_manufacturers": sorted({t.lower() for t in DEVICE_MANUFACTURERS}),
        "protected_device_names": sorted({t.lower() for t in PROTECTED_DEVICE_NAMES}),
        "ln_station_regex": r"^\\d{1,2}[LRlr](?:[is])?$",
        "segment_regex": r"^[LRlr][Bb]\\d{1,2}(?:\\+\\d{1,2})?$",
        "address_markers": [
            "street",
            "st",
            "rd",
            "road",
            "ave",
            "avenue",
            "dr",
            "drive",
            "blvd",
            "boulevard",
            "lane",
            "ln",
            "zip",
            "zipcode",
            "address",
            "city",
            "state",
            "ste",
            "suite",
            "apt",
            "unit",
        ],
        "code_markers": [
            "cpt",
            "code",
            "codes",
            "billing",
            "submitted",
            "justification",
            "rvu",
            "coding",
            "radiology",
            "guidance",
            "ct",
            "modifier",
            "billed",
            "cbct",
        ],
        "station_markers": ["station", "stations", "nodes", "sampled", "ebus", "tbna", "ln"],
    }
    with open(out_dir / "protected_terms.json", "w") as f:
        json.dump(terms, f, indent=2)


def resolve_quantize_args(args: argparse.Namespace) -> list[str]:
    if args.quantize_config:
        return ["--config", args.quantize_config]
    if args.quantize_target:
        return [f"--{args.quantize_target}"]
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "darwin" and machine in ("arm64", "aarch64"):
        return ["--arm64"]
    if machine in ("x86_64", "amd64"):
        return ["--avx2"]
    raise RuntimeError("Unable to infer quantize target. Pass --quantize-target or --quantize-config.")


def format_size(size_bytes: int) -> str:
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def main() -> None:
    args = build_arg_parser().parse_args()
    model_dir = Path(args.model_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if shutil.which("optimum-cli") is None:
        raise RuntimeError(
            "optimum-cli not found. Install with: pip install 'optimum[onnxruntime]' onnxruntime"
        )

    run(
        [
            "optimum-cli",
            "export",
            "onnx",
            "--model",
            str(model_dir),
            "--task",
            "token-classification",
            str(out_dir),
        ]
    )

    onnx_dir = out_dir / "onnx"
    model_path = ensure_model_onnx(out_dir, onnx_dir)
    if not model_path.exists():
        raise RuntimeError("Export failed: model.onnx not found.")
    model_size = model_path.stat().st_size
    if model_size < 5_000_000:
        raise RuntimeError("Export failed: model.onnx is unexpectedly small.")
    print(f"Exported model.onnx size: {format_size(model_size)}")

    if args.quantize:
        quant_args = resolve_quantize_args(args)
        run(
            [
                "optimum-cli",
                "onnxruntime",
                "quantize",
                "--onnx_model",
                str(model_path),
                "--output",
                str(onnx_dir / "model_quantized.onnx"),
                *quant_args,
            ]
        )
        qpath = onnx_dir / "model_quantized.onnx"
        if not qpath.exists() or qpath.stat().st_size < 5_000_000:
            raise RuntimeError("Quantization failed: model_quantized.onnx missing or too small.")
        print(f"Quantized model_quantized.onnx size: {format_size(qpath.stat().st_size)}")

    for name in MODEL_FILES:
        src = model_dir / name
        if src.exists():
            shutil.copy2(src, out_dir / name)

    write_protected_terms(out_dir)


if __name__ == "__main__":
    main()
