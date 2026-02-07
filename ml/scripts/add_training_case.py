import json
import datetime
import re
from pathlib import Path

def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _resolve_repo_root(repo_root: Path | str | None) -> Path:
    """
    Resolve the actual repository root for this checkout.

    Many generated scripts pass an incorrect "repo_root" (often a subdirectory
    under ``data/``). When that subdirectory is still within this checkout, we
    can reliably correct it to the real repo root based on this module's path.
    """

    module_repo_root = Path(__file__).resolve().parents[2]
    if repo_root is None:
        return module_repo_root

    candidate = Path(repo_root).expanduser()
    try:
        candidate = candidate.resolve()
    except FileNotFoundError:
        candidate = candidate.absolute()

    if candidate.is_file():
        candidate = candidate.parent

    if _is_within(candidate, module_repo_root):
        return module_repo_root

    return candidate


def add_case(note_id, raw_text, entities, repo_root):
    """
    Central logic to update ML training files.
    
    Args:
        note_id (str): Unique identifier for the note.
        raw_text (str): The clinical text.
        entities (list): List of dicts [{'label': '...', 'start': 0, 'end': 5, 'text': '...'}, ...]
        repo_root (Path): Path object pointing to the repository root.
    """
    
    repo_root = _resolve_repo_root(repo_root)

    # --- Guard against the most common generated-script bug ---
    # Some generated scripts accidentally swap (note_id, raw_text) and call:
    #   add_case(<full note text>, <script_name_or_dataset_tag>, entities, repo_root)
    # That corrupts the dataset (entities get clamped to the short "raw_text").
    if isinstance(note_id, str) and isinstance(raw_text, str):
        note_id_looks_like_text = (len(note_id) > 200) and (("\n" in note_id) or (" " in note_id))
        raw_text_looks_like_id = (len(raw_text) <= 80) and ("\n" not in raw_text) and (
            raw_text.endswith(".py") or re.fullmatch(r"[A-Za-z0-9_.-]+", raw_text) is not None
        )
        if note_id_looks_like_text and raw_text_looks_like_id:
            raise ValueError(
                "add_case() expects (note_id, raw_text, entities, repo_root), but it looks like "
                "the first two arguments were swapped. Got a note_id that looks like note text "
                f"(len={len(note_id)}), and a raw_text that looks like an identifier ({raw_text!r}). "
                "Fix the caller to pass a short unique note_id and the full note text as raw_text."
            )

    # Define Output Directory Structure
    output_dir = repo_root / "data" / "ml_training" / "granular_ner"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files = {
        "ner": output_dir / "ner_dataset_all.jsonl",
        "notes": output_dir / "notes.jsonl",
        "spans": output_dir / "spans.jsonl",
        "stats": output_dir / "stats.json",
        "log": output_dir / "alignment_warnings.log"
    }

    if entities is None:
        entities = []

    # 1. Normalize + sort entities
    normalized_entities = []
    for ent in entities:
        if not isinstance(ent, dict):
            continue

        label = ent.get("label")
        start = ent.get("start")
        end = ent.get("end")
        text = ent.get("text", ent.get("token"))

        try:
            start = int(start)
            end = int(end)
        except (TypeError, ValueError):
            if isinstance(text, str) and raw_text:
                idx = raw_text.find(text)
                if idx != -1:
                    start = idx
                    end = idx + len(text)
                else:
                    continue
            else:
                continue

        if not isinstance(label, str) or not label:
            continue

        if start < 0:
            start = 0
        if end < start:
            end = start
        if raw_text:
            max_len = len(raw_text)
            if start > max_len:
                start = max_len
            if end > max_len:
                end = max_len

        if text is None:
            text = raw_text[start:end]
        elif raw_text:
            text = raw_text[start:end]

        if end <= start:
            continue

        normalized_entities.append(
            {"label": label, "start": start, "end": end, "text": text}
        )

    entities = sorted(normalized_entities, key=lambda x: x["start"])

    # 2. Append to ner_dataset_all.jsonl
    with open(files["ner"], 'a', encoding='utf-8') as f:
        record = {"id": note_id, "text": raw_text, "entities": entities}
        f.write(json.dumps(record) + "\n")

    # 3. Append to notes.jsonl
    with open(files["notes"], 'a', encoding='utf-8') as f:
        record = {"id": note_id, "text": raw_text}
        f.write(json.dumps(record) + "\n")

    # 4. Append to spans.jsonl
    with open(files["spans"], 'a', encoding='utf-8') as f:
        for ent in entities:
            span_record = {
                "span_id": f"{ent['label']}_{ent['start']}",
                "note_id": note_id,
                "label": ent['label'],
                "text": ent["text"],
                "start": ent['start'],
                "end": ent['end']
            }
            f.write(json.dumps(span_record) + "\n")

    # 5. Update stats.json
    if files["stats"].exists():
        with open(files["stats"], 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {"total_notes": 0, "total_spans_valid": 0, "label_counts": {}}

    stats["total_notes"] += 1
    stats["total_spans_valid"] += len(entities)
    for ent in entities:
        lbl = ent['label']
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1
    
    with open(files["stats"], 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)

    # 6. Validation & Logging
    with open(files["log"], 'a', encoding='utf-8') as log:
        for ent in entities:
            extracted = raw_text[ent['start']:ent['end']]
            if extracted != ent['text']:
                log.write(f"[{datetime.datetime.now()}] MISMATCH: {note_id} | Label {ent['label']} expected '{ent['text']}' but got '{extracted}'\n")

    print(f"✅ Success: {note_id} added to pipeline. ({len(entities)} entities)")
