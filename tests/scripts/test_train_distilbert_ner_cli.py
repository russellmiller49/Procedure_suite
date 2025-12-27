import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")

from scripts import train_distilbert_ner


def test_parse_defaults():
    args = train_distilbert_ner.parse_args([])
    assert args.eval_only is False
    assert args.model_dir is None
    assert args.eval_split == "heldout"


def test_validate_paths_eval_only_requires_model_dir(tmp_path):
    data_path = tmp_path / "data.jsonl"
    data_path.write_text("{}\n")
    args = train_distilbert_ner.parse_args(
        ["--data", str(data_path), "--eval-only", "--model-dir", str(tmp_path / "missing")]
    )
    model_dir = train_distilbert_ner.resolve_model_dir(args)
    resolved_data = train_distilbert_ner.resolve_data_path(args)
    with pytest.raises(FileNotFoundError):
        train_distilbert_ner.validate_paths(args, model_dir, resolved_data)


def test_validate_paths_eval_only_ok(tmp_path):
    data_path = tmp_path / "data.jsonl"
    data_path.write_text("{}\n")
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    args = train_distilbert_ner.parse_args(
        ["--data", str(data_path), "--eval-only", "--model-dir", str(model_dir)]
    )
    train_distilbert_ner.validate_paths(
        args,
        train_distilbert_ner.resolve_model_dir(args),
        train_distilbert_ner.resolve_data_path(args),
    )
