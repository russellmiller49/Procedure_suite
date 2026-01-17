"""Granular NER inference module.

This module provides inference for the trained DistilBERT NER model,
converting BIO token tags back to character-span entities with confidence scores.
"""

from __future__ import annotations

import os
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

from modules.common.logger import get_logger

logger = get_logger("ner.inference")


@dataclass
class NEREntity:
    """A single recognized entity from the NER model."""

    text: str
    """The extracted text span."""

    label: str
    """Entity type (e.g., 'ANAT_LN_STATION')."""

    start_char: int
    """Start character offset in original text."""

    end_char: int
    """End character offset in original text."""

    confidence: float
    """Model confidence (0-1), average of token confidences."""

    evidence_quote: str = ""
    """Surrounding context for evidence."""

    token_count: int = 1
    """Number of tokens in this entity."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "label": self.label,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "confidence": round(self.confidence, 4),
            "evidence_quote": self.evidence_quote,
        }


@dataclass
class NERExtractionResult:
    """Result from NER inference on a procedure note."""

    entities: List[NEREntity]
    """All extracted entities."""

    entities_by_type: Dict[str, List[NEREntity]] = field(default_factory=dict)
    """Entities grouped by type."""

    raw_text: str = ""
    """Original input text."""

    inference_time_ms: float = 0.0
    """Time taken for inference in milliseconds."""

    truncated: bool = False
    """True if input was truncated to max_length."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_count": len(self.entities),
            "entities": [e.to_dict() for e in self.entities],
            "entities_by_type": {
                k: [e.to_dict() for e in v]
                for k, v in self.entities_by_type.items()
            },
            "inference_time_ms": round(self.inference_time_ms, 2),
            "truncated": self.truncated,
        }


class GranularNERPredictor:
    """Runs granular NER inference using trained DistilBERT model."""

    DEFAULT_MODEL_DIR = Path("artifacts/granular_ner_model")
    DEFAULT_CONFIDENCE_THRESHOLD = 0.5
    DEFAULT_CONTEXT_CHARS = 50
    MODEL_DIR_ENV_VAR = "GRANULAR_NER_MODEL_DIR"

    def __init__(
        self,
        model_dir: str | Path | None = None,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        context_chars: int = DEFAULT_CONTEXT_CHARS,
        device: str | None = None,
    ) -> None:
        """
        Initialize the NER predictor.

        Args:
            model_dir: Path to trained model directory
            confidence_threshold: Minimum confidence to include entity
            context_chars: Characters of context for evidence quotes
            device: Device to run on ('cpu', 'cuda', 'mps', or None for auto)
        """
        if model_dir:
            self.model_dir = Path(model_dir)
        else:
            env_dir = os.getenv(self.MODEL_DIR_ENV_VAR, "").strip()
            self.model_dir = Path(env_dir) if env_dir else self.DEFAULT_MODEL_DIR
        self.confidence_threshold = confidence_threshold
        self.context_chars = context_chars
        self.available = False

        self._tokenizer = None
        self._model = None
        self._label2id: Dict[str, int] = {}
        self._id2label: Dict[int, str] = {}
        self._device = None

        # Determine device
        if device:
            self._device = torch.device(device)
        elif torch.cuda.is_available():
            self._device = torch.device("cuda")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self._device = torch.device("mps")
        else:
            self._device = torch.device("cpu")

        try:
            self._load_model()
            self.available = True
            logger.info(
                "GranularNERPredictor loaded: %d labels, device=%s",
                len(self._label2id),
                self._device,
            )
        except Exception as exc:
            logger.warning("GranularNERPredictor unavailable: %s", exc)

    def _load_model(self) -> None:
        """Load model, tokenizer, and label mappings."""
        if not self.model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {self.model_dir}")

        # Load label map
        label_map_path = self.model_dir / "label_map.json"
        if label_map_path.exists():
            with open(label_map_path) as f:
                label_data = json.load(f)
                self._label2id = label_data.get("label2id", {})
                self._id2label = {int(k): v for k, v in label_data.get("id2label", {}).items()}
        else:
            raise FileNotFoundError(f"Label map not found: {label_map_path}")

        # Load tokenizer
        self._tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir))

        # Load model
        self._model = AutoModelForTokenClassification.from_pretrained(str(self.model_dir))
        self._model.to(self._device)
        self._model.eval()

    @property
    def labels(self) -> List[str]:
        """Get list of entity labels (without B-/I- prefixes)."""
        labels = set()
        for label in self._label2id.keys():
            if label.startswith("B-") or label.startswith("I-"):
                labels.add(label[2:])
        return sorted(labels)

    def predict(self, note_text: str, max_length: int = 512) -> NERExtractionResult:
        """
        Run NER inference on procedure note text.

        Args:
            note_text: The procedure note text
            max_length: Maximum sequence length

        Returns:
            NERExtractionResult with extracted entities
        """
        if not self.available:
            return NERExtractionResult(
                entities=[],
                raw_text=note_text,
                inference_time_ms=0.0,
            )

        start_time = time.time()

        # Tokenize with offset mapping
        encoding = self._tokenizer(
            note_text,
            truncation=True,
            max_length=max_length,
            return_offsets_mapping=True,
            return_tensors="pt",
        )

        truncated = len(note_text) > max_length * 4  # Rough estimate

        # Get offset mapping before moving tensors
        offset_mapping = encoding.pop("offset_mapping")[0].tolist()

        # Move to device
        input_ids = encoding["input_ids"].to(self._device)
        attention_mask = encoding["attention_mask"].to(self._device)

        # Run inference
        with torch.no_grad():
            outputs = self._model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits[0]  # Shape: (seq_len, num_labels)

            # Get probabilities and predictions
            probs = torch.softmax(logits, dim=-1)
            predictions = torch.argmax(logits, dim=-1).cpu().tolist()
            confidence_scores = probs.max(dim=-1).values.cpu().tolist()

        # Convert predictions to entities
        entities = self._decode_predictions(
            predictions,
            confidence_scores,
            offset_mapping,
            note_text,
        )

        # Filter by confidence threshold
        entities = [e for e in entities if e.confidence >= self.confidence_threshold]

        # Group by type
        entities_by_type: Dict[str, List[NEREntity]] = {}
        for entity in entities:
            if entity.label not in entities_by_type:
                entities_by_type[entity.label] = []
            entities_by_type[entity.label].append(entity)

        inference_time = (time.time() - start_time) * 1000

        return NERExtractionResult(
            entities=entities,
            entities_by_type=entities_by_type,
            raw_text=note_text,
            inference_time_ms=inference_time,
            truncated=truncated,
        )

    def _decode_predictions(
        self,
        predictions: List[int],
        confidence_scores: List[float],
        offset_mapping: List[tuple],
        text: str,
    ) -> List[NEREntity]:
        """
        Decode BIO predictions to character-span entities.

        Merges consecutive B-X and I-X tokens into single entities.
        """
        entities: List[NEREntity] = []
        current_entity: Optional[Dict[str, Any]] = None

        for idx, (pred_id, conf, offset) in enumerate(
            zip(predictions, confidence_scores, offset_mapping)
        ):
            # Skip special tokens (offset is (0, 0))
            if offset[0] == 0 and offset[1] == 0:
                continue

            label = self._id2label.get(pred_id, "O")

            if label.startswith("B-"):
                # Start of new entity - save current if exists
                if current_entity:
                    entities.append(self._finalize_entity(current_entity, text))

                entity_type = label[2:]
                current_entity = {
                    "label": entity_type,
                    "start_char": offset[0],
                    "end_char": offset[1],
                    "confidences": [conf],
                }

            elif label.startswith("I-"):
                entity_type = label[2:]
                if current_entity and current_entity["label"] == entity_type:
                    # Continue current entity
                    current_entity["end_char"] = offset[1]
                    current_entity["confidences"].append(conf)
                else:
                    # I- without matching B- - treat as new entity
                    if current_entity:
                        entities.append(self._finalize_entity(current_entity, text))

                    current_entity = {
                        "label": entity_type,
                        "start_char": offset[0],
                        "end_char": offset[1],
                        "confidences": [conf],
                    }

            else:
                # O tag - finalize current entity
                if current_entity:
                    entities.append(self._finalize_entity(current_entity, text))
                    current_entity = None

        # Don't forget the last entity
        if current_entity:
            entities.append(self._finalize_entity(current_entity, text))

        return entities

    def _finalize_entity(
        self,
        entity_data: Dict[str, Any],
        text: str,
    ) -> NEREntity:
        """Create NEREntity from accumulated data."""
        start = entity_data["start_char"]
        end = entity_data["end_char"]
        entity_text = text[start:end]

        # Calculate average confidence
        confidences = entity_data["confidences"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Build evidence quote with context
        context_start = max(0, start - self.context_chars)
        context_end = min(len(text), end + self.context_chars)
        evidence = text[context_start:context_end]

        return NEREntity(
            text=entity_text,
            label=entity_data["label"],
            start_char=start,
            end_char=end,
            confidence=avg_confidence,
            evidence_quote=evidence,
            token_count=len(confidences),
        )

    def predict_batch(
        self,
        texts: List[str],
        max_length: int = 512,
        batch_size: int = 8,
    ) -> List[NERExtractionResult]:
        """
        Run NER inference on multiple texts.

        Args:
            texts: List of procedure note texts
            max_length: Maximum sequence length per text
            batch_size: Number of texts to process at once

        Returns:
            List of NERExtractionResult, one per input text
        """
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            for text in batch:
                results.append(self.predict(text, max_length))
        return results
