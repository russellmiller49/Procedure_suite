#!/usr/bin/env python3
"""
Safety regression audit for PHI NER false positives (must-not-redact terms).

Checks CPT splits, LN station patterns, device terms, "Left Upper Lobe",
and new (Dec 2025) audit checks:
- dangling_entity: stopwords, very short spans, purely punctuation
- leading_punct_entity: entity spans starting with punctuation
- numeric_code_fp: 4-6 digit codes in CPT/CBCT context tagged as PHI

Reports raw vs vetoed violations. Post-veto violations should ALWAYS be 0.
"""

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

from modules.phi.adapters.phi_redactor_hybrid import DEVICE_MANUFACTURERS, PROTECTED_DEVICE_NAMES
from modules.phi.safety.protected_terms import LN_CONTEXT_WORDS, normalize, reconstruct_wordpiece
from modules.phi.safety.veto import apply_protected_veto

CPT_CONTEXT_WORDS = {
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
    "cbct",
    "fluoro",
    "fluoroscopy",
    "localization",
    "rationale",
}
CPT_PUNCT_TOKENS = {",", ";", ":", "/", "(", ")", "[", "]"}
LN_STATION_RE = re.compile(r"^\d{1,2}[lr](?:[is])?$")
UNIT_TOKENS = {"l", "liter", "liters", "ml", "cc"}
VOLUME_VERBS = {"drained", "output", "removed"}
EXTRA_DEVICE_TERMS = {"chartis"}
DEVICE_TERM_SET = (
    {normalize(term) for term in DEVICE_MANUFACTURERS}
    | {normalize(term) for term in PROTECTED_DEVICE_NAMES}
    | {normalize(term) for term in EXTRA_DEVICE_TERMS}
)

# Stopwords for dangling entity detection
STOPWORDS = {
    "a", "an", "the", "of", "in", "and", "with", "to", "for", "or", "by", "at",
    "is", "was", "are", "were", "be", "been", "being", "has", "had", "have",
    "did", "does", "do", "will", "would", "could", "should", "may", "might",
    "on", "as", "from", "but", "not", "no", "yes", "so", "if", "then",
}

PUNCTUATION_CHARS = set("()[]{},.;:!?/\\-_\"'")


@dataclass
class Violation:
    kind: str
    indices: List[int]
    phrase: str


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", default="artifacts/phi_distilbert_ner")
    ap.add_argument("--data", default="data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl")
    ap.add_argument("--limit", type=int, default=2000)
    ap.add_argument("--max-bad", type=int, default=20)
    ap.add_argument("--report-out", default="artifacts/phi_distilbert_ner/audit_report.json")
    return ap


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    return build_arg_parser().parse_args(argv)


def validate_paths(args: argparse.Namespace) -> None:
    if not os.path.isfile(args.data):
        raise FileNotFoundError(f"Data file not found: {args.data}")
    if not os.path.isdir(args.model_dir):
        raise FileNotFoundError(f"Model directory not found: {args.model_dir}")


def read_jsonl(path: str, limit: int | None = None) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def normalize_token(token: str) -> str:
    if token.startswith("##"):
        token = token[2:]
    return normalize(token)


def build_word_index(tokens: List[str]) -> Tuple[List[str], List[List[int]]]:
    words: List[str] = []
    word_to_pieces: List[List[int]] = []
    idx = 0
    while idx < len(tokens):
        word, end_idx = reconstruct_wordpiece(tokens, idx)
        words.append(normalize(word))
        word_to_pieces.append(list(range(idx, end_idx + 1)))
        idx = end_idx + 1
    return words, word_to_pieces


def resolve_id2label(model: Any, model_dir: str) -> Dict[int, str]:
    id2label_raw = getattr(model.config, "id2label", {}) or {}
    id2label: Dict[int, str] = {}
    for key, value in id2label_raw.items():
        try:
            idx = int(key)
        except (TypeError, ValueError):
            continue
        id2label[idx] = str(value)
    if id2label:
        return id2label

    label_map_path = os.path.join(model_dir, "label_map.json")
    if os.path.exists(label_map_path):
        with open(label_map_path, "r") as f:
            data = json.load(f)
        raw = data.get("id2label", {})
        for key, value in raw.items():
            try:
                idx = int(key)
            except (TypeError, ValueError):
                continue
            id2label[idx] = str(value)
    if id2label:
        return id2label
    raise RuntimeError("No id2label mapping found in model config or label_map.json.")


def prepare_inputs(tokens: List[str], tokenizer: Any, max_length: int = 512) -> Tuple[List[str], List[int], List[int]]:
    max_wordpieces = max_length - 2
    tokens = tokens[:max_wordpieces]
    if tokenizer.unk_token_id is None:
        raise RuntimeError("Tokenizer must have an UNK token id.")
    ids = tokenizer.convert_tokens_to_ids(tokens)
    input_ids: List[int] = []
    for x in ids:
        if x is None or x == -1:
            input_ids.append(int(tokenizer.unk_token_id))
        else:
            input_ids.append(int(x))
    if tokenizer.cls_token_id is None or tokenizer.sep_token_id is None:
        raise RuntimeError("Tokenizer must have CLS/SEP token ids.")
    input_ids = [tokenizer.cls_token_id] + input_ids + [tokenizer.sep_token_id]
    attention_mask = [1] * len(input_ids)
    return tokens, input_ids, attention_mask


def predict_labels(
    tokens: List[str],
    tokenizer: Any,
    model: Any,
    id2label: Dict[int, str],
    device: torch.device,
) -> Tuple[List[str], List[str]]:
    tokens, input_ids, attention_mask = prepare_inputs(tokens, tokenizer)
    if not tokens:
        return [], []
    input_ids_tensor = torch.tensor([input_ids], device=device)
    attention_tensor = torch.tensor([attention_mask], device=device)
    with torch.no_grad():
        outputs = model(input_ids=input_ids_tensor, attention_mask=attention_tensor)
    logits = outputs.logits
    pred_ids = logits.argmax(-1).squeeze(0).tolist()
    pred_ids = pred_ids[1 : 1 + len(tokens)]
    labels = [id2label.get(int(pid), "O") for pid in pred_ids]
    return tokens, labels


def is_non_o(label: str) -> bool:
    return label != "O"


def is_stable_cpt_split(tokens: List[str], i: int) -> str | None:
    if i + 1 >= len(tokens):
        return None
    if tokens[i].isdigit() and len(tokens[i]) == 3 and tokens[i + 1].startswith("##"):
        suffix = tokens[i + 1][2:]
        if suffix.isdigit() and len(suffix) == 2:
            return tokens[i] + suffix
    return None


def has_cpt_context(tokens: List[str], i: int, j: int, text: str | None) -> bool:
    start = max(0, i - 10)
    end = min(len(tokens), j + 11)
    context_tokens = tokens[start:end]
    norm_context = {normalize_token(tok) for tok in context_tokens}
    if any(word in norm_context for word in CPT_CONTEXT_WORDS):
        return True
    # Slash-separated in parentheses pattern
    has_parens = "(" in context_tokens or ")" in context_tokens
    has_slash = "/" in context_tokens
    if has_parens and has_slash:
        return True
    if text:
        text_norm = normalize(text)
        return any(word in text_norm.split() for word in CPT_CONTEXT_WORDS)
    return False


def is_volume_context(tokens: List[str], idx: int) -> bool:
    unit_window = tokens[max(0, idx - 3) : min(len(tokens), idx + 4)]
    verb_window = tokens[max(0, idx - 6) : min(len(tokens), idx + 7)]
    if not any(normalize_token(tok) in UNIT_TOKENS for tok in unit_window):
        return False
    return any(normalize_token(tok) in VOLUME_VERBS for tok in verb_window)


def is_ln_station_split(tokens: List[str], i: int) -> Tuple[str, List[int]] | None:
    if i + 1 >= len(tokens):
        return None
    if not tokens[i].isdigit() or len(tokens[i]) not in (1, 2):
        return None
    if not tokens[i + 1].startswith("##"):
        return None
    side = tokens[i + 1][2:].lower()
    if side not in ("r", "l"):
        return None
    station = tokens[i] + side
    indices = [i, i + 1]
    if i + 2 < len(tokens) and tokens[i + 2].startswith("##"):
        suffix = tokens[i + 2][2:].lower()
        if suffix in ("i", "s"):
            station += suffix
            indices.append(i + 2)
    if not LN_STATION_RE.match(station):
        return None
    return station, indices


def is_station7_context(tokens: List[str], i: int) -> bool:
    if tokens[i] != "7":
        return False
    start = max(0, i - 6)
    end = min(len(tokens), i + 7)
    context = {normalize_token(tok) for tok in tokens[start:end]}
    return any(word in context for word in LN_CONTEXT_WORDS)


def find_left_upper_lobe(words: List[str], word_to_pieces: List[List[int]]) -> List[Violation]:
    violations: List[Violation] = []
    for i in range(len(words) - 2):
        if words[i] == "left" and words[i + 1] == "upper" and words[i + 2] == "lobe":
            indices = word_to_pieces[i] + word_to_pieces[i + 1] + word_to_pieces[i + 2]
            violations.append(Violation(kind="left_upper_lobe", indices=indices, phrase="left upper lobe"))
    return violations


def find_device_terms(words: List[str], word_to_pieces: List[List[int]]) -> List[Violation]:
    violations: List[Violation] = []
    for word, indices in zip(words, word_to_pieces):
        if word in DEVICE_TERM_SET:
            violations.append(Violation(kind="device_term", indices=indices, phrase=word))
    return violations


# =============================================================================
# NEW AUDIT CHECKS (Dec 2025)
# =============================================================================


def extract_entity_spans(labels: List[str]) -> List[Tuple[int, int, str]]:
    """Extract entity spans from BIO labels.

    Returns list of (start_idx, end_idx_inclusive, entity_type).
    """
    spans: List[Tuple[int, int, str]] = []
    i = 0
    while i < len(labels):
        label = labels[i]
        if not label or label == "O" or "-" not in label:
            i += 1
            continue
        prefix, entity_type = label.split("-", 1)
        start = i
        end = i
        # Extend to include I- continuations
        while end + 1 < len(labels):
            next_label = labels[end + 1]
            if next_label == f"I-{entity_type}":
                end += 1
            else:
                break
        spans.append((start, end, entity_type))
        i = end + 1
    return spans


def reconstruct_span_text(tokens: List[str], start: int, end: int) -> str:
    """Reconstruct surface text from a token span, handling wordpieces."""
    result = []
    for i in range(start, end + 1):
        tok = tokens[i]
        if tok.startswith("##"):
            if result:
                result[-1] += tok[2:]
            else:
                result.append(tok[2:])
        else:
            result.append(tok)
    return " ".join(result)


def is_punctuation_token(token: str) -> bool:
    """Check if token is purely punctuation."""
    return all(c in PUNCTUATION_CHARS for c in token)


def is_numeric_code(text: str) -> bool:
    """Check if text is a 4-6 digit numeric code."""
    clean = text.replace(" ", "")
    return clean.isdigit() and 4 <= len(clean) <= 6


def find_dangling_entities(tokens: List[str], labels: List[str]) -> List[Violation]:
    """Find dangling entity violations.

    Dangling entity = entity span that is:
    - A stopword/article (a, an, the, of, for, etc.)
    - Length < 3 chars after stripping punctuation
    - Purely punctuation
    """
    violations: List[Violation] = []
    spans = extract_entity_spans(labels)

    for start, end, entity_type in spans:
        text = reconstruct_span_text(tokens, start, end)
        norm = normalize(text)

        # Check if it's a stopword
        if norm in STOPWORDS:
            violations.append(Violation(
                kind="dangling_entity",
                indices=list(range(start, end + 1)),
                phrase=f"{text} (stopword)"
            ))
            continue

        # Check if very short (< 2 chars after normalization)
        if len(norm) < 2:
            violations.append(Violation(
                kind="dangling_entity",
                indices=list(range(start, end + 1)),
                phrase=f"{text} (too_short)"
            ))
            continue

        # Check if all words are stopwords
        words = norm.split()
        if all(w in STOPWORDS for w in words):
            violations.append(Violation(
                kind="dangling_entity",
                indices=list(range(start, end + 1)),
                phrase=f"{text} (all_stopwords)"
            ))
            continue

        # Check if purely punctuation
        if all(is_punctuation_token(tokens[i]) for i in range(start, end + 1)):
            violations.append(Violation(
                kind="dangling_entity",
                indices=list(range(start, end + 1)),
                phrase=f"{text} (punctuation_only)"
            ))

    return violations


def find_leading_punct_entities(tokens: List[str], labels: List[str]) -> List[Violation]:
    """Find entities that start with punctuation token."""
    violations: List[Violation] = []
    spans = extract_entity_spans(labels)

    for start, end, entity_type in spans:
        if start < len(tokens) and is_punctuation_token(tokens[start]):
            text = reconstruct_span_text(tokens, start, end)
            violations.append(Violation(
                kind="leading_punct_entity",
                indices=list(range(start, end + 1)),
                phrase=text
            ))

    return violations


def find_numeric_code_fps(tokens: List[str], labels: List[str], text: str | None) -> List[Violation]:
    """Find numeric codes in CPT/CBCT context tagged as PHI (false positives)."""
    violations: List[Violation] = []
    spans = extract_entity_spans(labels)

    for start, end, entity_type in spans:
        span_text = reconstruct_span_text(tokens, start, end)
        # Check if it's a numeric code in CPT context
        if is_numeric_code(span_text) and has_cpt_context(tokens, start, end, text):
            violations.append(Violation(
                kind="numeric_code_fp",
                indices=list(range(start, end + 1)),
                phrase=span_text
            ))

    return violations


def find_violations(tokens: List[str], labels: List[str], text: str | None) -> List[Violation]:
    violations: List[Violation] = []

    for i in range(len(tokens) - 1):
        cpt = is_stable_cpt_split(tokens, i)
        if not cpt:
            continue
        if not has_cpt_context(tokens, i, i + 1, text):
            continue
        if is_non_o(labels[i]) or is_non_o(labels[i + 1]):
            violations.append(Violation(kind="cpt_split", indices=[i, i + 1], phrase=cpt))

    for i in range(len(tokens) - 1):
        ln_match = is_ln_station_split(tokens, i)
        if not ln_match:
            continue
        station, indices = ln_match
        if is_volume_context(tokens, i):
            continue
        if any(is_non_o(labels[idx]) for idx in indices):
            violations.append(Violation(kind="ln_station", indices=indices, phrase=station))

    for i in range(len(tokens)):
        if tokens[i] == "7" and is_station7_context(tokens, i) and not is_volume_context(tokens, i):
            if is_non_o(labels[i]):
                violations.append(Violation(kind="ln_station7", indices=[i], phrase="7"))

    words, word_to_pieces = build_word_index(tokens)
    for violation in find_left_upper_lobe(words, word_to_pieces):
        if any(is_non_o(labels[idx]) for idx in violation.indices):
            violations.append(violation)

    for violation in find_device_terms(words, word_to_pieces):
        if any(is_non_o(labels[idx]) for idx in violation.indices):
            violations.append(violation)

    # NEW: Add dangling entity, leading punct, and numeric code FP checks
    violations.extend(find_dangling_entities(tokens, labels))
    violations.extend(find_leading_punct_entities(tokens, labels))
    violations.extend(find_numeric_code_fps(tokens, labels, text))

    return violations


def format_slice(
    tokens: List[str],
    labels: List[str],
    indices: List[int],
    window: int = 8,
) -> Tuple[List[str], List[str]]:
    if not indices:
        return [], []
    start = max(0, min(indices) - window)
    end = min(len(tokens), max(indices) + window + 1)
    return tokens[start:end], labels[start:end]


def resolve_record_id(row: Dict[str, Any], fallback: int) -> str:
    record_id = row.get("id") or row.get("id_base") or row.get("record_index") or fallback
    return str(record_id)


def main() -> None:
    args = parse_args()
    validate_paths(args)

    rows = read_jsonl(args.data, limit=args.limit)
    if not rows:
        raise RuntimeError(f"No rows loaded from {args.data}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, use_fast=True)
    model = AutoModelForTokenClassification.from_pretrained(args.model_dir)
    model.to(device)
    model.eval()

    id2label = resolve_id2label(model, args.model_dir)

    violation_counts_raw: Dict[str, int] = {}
    violation_counts_veto: Dict[str, int] = {}
    examples: List[Dict[str, Any]] = []
    checked = 0

    for idx, row in enumerate(rows):
        tokens = row.get("tokens") or []
        if not isinstance(tokens, list) or not tokens:
            continue
        record_id = resolve_record_id(row, idx)
        text = row.get("text")
        tokens, labels = predict_labels(tokens, tokenizer, model, id2label, device)
        if not tokens or not labels:
            continue
        checked += 1

        vetoed_labels = apply_protected_veto(tokens, labels, text=text)

        raw_violations = find_violations(tokens, labels, text)
        veto_violations = find_violations(tokens, vetoed_labels, text)

        for violation in raw_violations:
            violation_counts_raw[violation.kind] = violation_counts_raw.get(violation.kind, 0) + 1
            if len(examples) < args.max_bad:
                tok_slice, pred_slice = format_slice(tokens, labels, violation.indices)
                _, veto_slice = format_slice(tokens, vetoed_labels, violation.indices)
                excerpt = text[:240] if isinstance(text, str) else None
                examples.append(
                    {
                        "type": violation.kind,
                        "id": record_id,
                        "token_index": min(violation.indices),
                        "span_len": len(violation.indices),
                        "phrase": violation.phrase,
                        "tokens": tok_slice,
                        "pred": pred_slice,
                        "post_veto": veto_slice,
                        "text_excerpt": excerpt,
                    }
                )

        for violation in veto_violations:
            violation_counts_veto[violation.kind] = violation_counts_veto.get(violation.kind, 0) + 1

    total_raw = sum(violation_counts_raw.values())
    total_veto = sum(violation_counts_veto.values())

    print(f"Checked records: {checked}")
    print(f"Raw violations: total={total_raw} detail={violation_counts_raw}")
    print(f"After veto: total={total_veto} detail={violation_counts_veto}")

    if examples:
        print(f"First {min(len(examples), args.max_bad)} raw violations:")
        for ex in examples:
            print(
                f"[{ex['type']}] id={ex['id']} phrase={ex['phrase']} "
                f"tokens={ex['tokens']} pred={ex['pred']} post_veto={ex['post_veto']}"
            )
            if ex.get("text_excerpt"):
                print(f"  text={ex['text_excerpt']}")

    report = {
        "checked_records": checked,
        "violations_raw": violation_counts_raw,
        "violations_after_veto": violation_counts_veto,
        "examples": examples,
    }
    report_dir = os.path.dirname(args.report_out)
    if report_dir:
        os.makedirs(report_dir, exist_ok=True)
    with open(args.report_out, "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
