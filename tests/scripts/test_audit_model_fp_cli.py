import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")

from scripts import audit_model_fp


def test_parse_defaults():
    args = audit_model_fp.parse_args([])
    assert args.model_dir == "artifacts/phi_distilbert_ner"
    assert args.limit == 2000
    assert args.max_bad == 20


def test_validate_paths_requires_existing_model_dir(tmp_path):
    data_path = tmp_path / "data.jsonl"
    data_path.write_text("{}\n")
    args = audit_model_fp.parse_args(["--data", str(data_path), "--model-dir", str(tmp_path / "missing")])
    with pytest.raises(FileNotFoundError):
        audit_model_fp.validate_paths(args)


def test_validate_paths_ok(tmp_path):
    data_path = tmp_path / "data.jsonl"
    data_path.write_text("{}\n")
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    args = audit_model_fp.parse_args(["--data", str(data_path), "--model-dir", str(model_dir)])
    audit_model_fp.validate_paths(args)
