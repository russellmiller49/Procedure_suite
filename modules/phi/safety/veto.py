from typing import List

from modules.phi.safety.protected_terms import (
    LN_CONTEXT_WORDS,
    is_ln_station,
    is_protected_anatomy_phrase,
    is_protected_device,
    normalize,
    reconstruct_wordpiece,
)

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
}
CPT_PUNCT_TOKENS = {",", ";", ":", "/", "(", ")", "[", "]"}
UNIT_TOKENS = {"l", "liter", "liters", "ml", "cc"}
VOLUME_VERBS = {"drained", "output", "removed"}


def _normalize_token(token: str) -> str:
    if token.startswith("##"):
        token = token[2:]
    return normalize(token)


def _is_stable_cpt_split(tokens: List[str], i: int) -> str | None:
    if i + 1 >= len(tokens):
        return None
    if tokens[i].isdigit() and len(tokens[i]) == 3 and tokens[i + 1].startswith("##"):
        suffix = tokens[i + 1][2:]
        if suffix.isdigit() and len(suffix) == 2:
            return tokens[i] + suffix
    return None


def _has_cpt_context(tokens: List[str], i: int, j: int, text: str | None) -> bool:
    start = max(0, i - 10)
    end = min(len(tokens), j + 11)
    context_tokens = tokens[start:end]
    norm_context = {_normalize_token(tok) for tok in context_tokens}
    if any(word in norm_context for word in CPT_CONTEXT_WORDS):
        return True
    if any(tok in CPT_PUNCT_TOKENS for tok in context_tokens):
        return True
    if text:
        text_norm = normalize(text)
        return any(word in text_norm.split() for word in CPT_CONTEXT_WORDS)
    return False


def _is_volume_context(tokens: List[str], idx: int) -> bool:
    unit_window = tokens[max(0, idx - 3) : min(len(tokens), idx + 4)]
    verb_window = tokens[max(0, idx - 6) : min(len(tokens), idx + 7)]
    if not any(_normalize_token(tok) in UNIT_TOKENS for tok in unit_window):
        return False
    return any(_normalize_token(tok) in VOLUME_VERBS for tok in verb_window)


def _repair_bio(tags: List[str]) -> List[str]:
    corrected = tags[:]
    prev_type = "O"
    for i, tag in enumerate(corrected):
        if not tag or tag == "O":
            prev_type = "O"
            corrected[i] = "O"
            continue
        if "-" not in tag:
            corrected[i] = "O"
            prev_type = "O"
            continue
        prefix, label = tag.split("-", 1)
        if prefix == "B":
            prev_type = label
            continue
        if prefix == "I":
            if prev_type != label:
                corrected[i] = f"B-{label}"
                prev_type = label
            else:
                prev_type = label
            continue
        corrected[i] = "O"
        prev_type = "O"
    return corrected


def apply_protected_veto(
    tokens: List[str],
    pred_tags: List[str],
    text: str | None = None,
) -> List[str]:
    if len(tokens) != len(pred_tags):
        raise ValueError("Tokens and predicted tags must be the same length.")

    corrected = pred_tags[:]

    # Wordpiece reconstruction for device/anatomy terms.
    idx = 0
    while idx < len(tokens):
        word, end_idx = reconstruct_wordpiece(tokens, idx)
        norm_word = normalize(word)
        if is_protected_device(norm_word) or is_protected_anatomy_phrase(norm_word):
            for j in range(idx, end_idx + 1):
                corrected[j] = "O"
        idx = end_idx + 1

    # Anatomy phrase scan: left/right + upper/lower/middle + lobe.
    words: List[str] = []
    word_spans: List[List[int]] = []
    idx = 0
    while idx < len(tokens):
        word, end_idx = reconstruct_wordpiece(tokens, idx)
        words.append(normalize(word))
        word_spans.append(list(range(idx, end_idx + 1)))
        idx = end_idx + 1
    for i in range(len(words) - 2):
        if words[i] in ("left", "right") and words[i + 1] in ("upper", "lower", "middle") and words[i + 2] == "lobe":
            for j in word_spans[i] + word_spans[i + 1] + word_spans[i + 2]:
                corrected[j] = "O"

    # CPT codes via stable split with context cues.
    for i in range(len(tokens) - 1):
        cpt = _is_stable_cpt_split(tokens, i)
        if not cpt:
            continue
        if _has_cpt_context(tokens, i, i + 1, text):
            corrected[i] = "O"
            corrected[i + 1] = "O"

    # LN stations via digit+side (+ optional i/s) and station 7 context.
    for i in range(len(tokens) - 1):
        if tokens[i].isdigit() and len(tokens[i]) in (1, 2) and tokens[i + 1].startswith("##"):
            side = tokens[i + 1][2:].lower()
            if side in ("r", "l") and not _is_volume_context(tokens, i):
                station = tokens[i] + side
                indices = [i, i + 1]
                if i + 2 < len(tokens) and tokens[i + 2].startswith("##"):
                    suffix = tokens[i + 2][2:].lower()
                    if suffix in ("i", "s"):
                        station += suffix
                        indices.append(i + 2)
                if is_ln_station(station):
                    for idx in indices:
                        corrected[idx] = "O"

    for i, tok in enumerate(tokens):
        if tok == "7" and not _is_volume_context(tokens, i):
            start = max(0, i - 6)
            end = min(len(tokens), i + 7)
            context = {_normalize_token(t) for t in tokens[start:end]}
            if any(word in context for word in LN_CONTEXT_WORDS):
                corrected[i] = "O"

    return _repair_bio(corrected)
