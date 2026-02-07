from __future__ import annotations

import ast
from pathlib import Path


def _allowed_label_types() -> set[str]:
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "ml" / "scripts" / "train_registry_ner.py"
    if not script_path.exists():
        script_path = repo_root / "scripts" / "train_registry_ner.py"
    module = ast.parse(script_path.read_text(encoding="utf-8"))

    for node in module.body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "ALLOWED_LABEL_TYPES":
            value = ast.literal_eval(node.value)
            return {str(v) for v in value}
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", "") == "ALLOWED_LABEL_TYPES":
                    value = ast.literal_eval(node.value)
                    return {str(v) for v in value}

    raise AssertionError(f"ALLOWED_LABEL_TYPES not found in {script_path}")


def test_train_registry_ner_allowlist_contains_stent_context_labels() -> None:
    allowed = _allowed_label_types()
    assert "DEV_STENT" in allowed
    assert "NEG_STENT" in allowed
    assert "CTX_STENT_PRESENT" in allowed
