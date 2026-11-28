"""Offline-only safetensors NER candidate; asset compatibility is fail-closed."""

import hashlib
import json
from pathlib import Path

ONTOLOGY = {
    "ANAT_LN_STATION",
    "PROC_ACTION",
    "DEV_STENT",
    "NEG_STENT",
    "CTX_STENT_PRESENT",
    "DEV_VALVE",
    "OBS_ROSE",
}
LABELS = ["O"] + [prefix + label for label in sorted(ONTOLOGY) for prefix in ("B-", "I-")]


class LocalNER:
    def __init__(self, directory):
        root = Path(directory).resolve()
        manifest_bytes = (root / "focused-model-manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        if (
            manifest.get("registry_profile") != "robotic_ebus_v1"
            or manifest.get("engine_version") != "0.2.0"
            or manifest.get("labels") != LABELS
        ):
            raise ValueError("model_incompatible")
        files = manifest.get("files", {})
        if "config.json" not in files or "model.safetensors" not in files:
            raise ValueError("model_incompatible")
        actual = {
            p.relative_to(root).as_posix()
            for p in root.rglob("*")
            if p.is_file() and p.name != "focused-model-manifest.json"
        }
        if actual != set(files):
            raise ValueError("model_inventory_mismatch")
        for name, digest in files.items():
            file = (root / name).resolve()
            if (
                root not in file.parents
                or file.suffix not in {".safetensors", ".json", ".txt"}
                or (root / name).is_symlink()
            ):
                raise ValueError("model_incompatible")
            if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
                raise ValueError("model_digest_mismatch")
        config = json.loads((root / "config.json").read_text())
        if (
            config.get("auto_map")
            or config.get("trust_remote_code")
            or config.get("model_type") != "bert"
            or config.get("architectures") != ["BertForTokenClassification"]
            or sorted(config.get("id2label", {}).values()) != sorted(LABELS)
        ):
            raise ValueError("model_incompatible")
        from transformers import AutoModelForTokenClassification, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(
            root, local_files_only=True, trust_remote_code=False
        )
        self.model = AutoModelForTokenClassification.from_pretrained(
            root, local_files_only=True, trust_remote_code=False, use_safetensors=True
        )
        self.model.eval()
        self.manifest = manifest
        self.manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()

    def predict(self, text):
        import torch

        encoded = self.tokenizer(
            text,
            return_offsets_mapping=True,
            return_overflowing_tokens=True,
            truncation=True,
            max_length=512,
            stride=64,
            padding=True,
            return_tensors="pt",
        )
        offsets = encoded.pop("offset_mapping").tolist()
        encoded.pop("overflow_to_sample_mapping", None)
        with torch.inference_mode():
            probabilities = self.model(**encoded).logits.softmax(-1)
        result = {}
        for batch, spans in enumerate(offsets):
            for index, (start, end) in enumerate(spans):
                score, label_id = probabilities[batch, index].max(-1)
                label = self.model.config.id2label[int(label_id)]
                if end > start and label != "O" and float(score) >= 0.90:
                    key = (start, end, label)
                    result[key] = {
                        "start": start,
                        "end": end,
                        "text": text[start:end],
                        "label": label,
                        "confidence": round(float(score), 6),
                    }
        return sorted(result.values(), key=lambda row: (row["start"], row["end"]))
