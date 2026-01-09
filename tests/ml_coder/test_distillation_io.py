import numpy as np

import pytest

from modules.ml_coder.distillation_io import (
    TeacherLogits,
    align_teacher_logits,
    load_teacher_logits_npz,
    validate_label_fields_match,
)


def test_teacher_logits_npz_load_and_label_match(tmp_path):
    path = tmp_path / "teacher_logits.npz"
    ids = np.array(["a", "b"])
    logits = np.zeros((2, 3), dtype=np.float32)
    label_fields = np.array(["l1", "l2", "l3"])
    np.savez_compressed(path, ids=ids, logits=logits, label_fields=label_fields)

    loaded = load_teacher_logits_npz(path)
    assert loaded.ids == ["a", "b"]
    assert loaded.logits.shape == (2, 3)
    assert loaded.label_fields == ["l1", "l2", "l3"]

    validate_label_fields_match(loaded.label_fields, ["l1", "l2", "l3"])
    with pytest.raises(ValueError):
        validate_label_fields_match(loaded.label_fields, ["l2", "l1", "l3"])


def test_align_teacher_logits_missing_ids_is_safe():
    teacher = TeacherLogits(
        ids=["a"],
        logits=np.array([[1.0, 2.0]], dtype=np.float32),
        label_fields=["l1", "l2"],
    )
    aligned, mask = align_teacher_logits(["a", "missing"], teacher)
    assert aligned.shape == (2, 2)
    assert mask.tolist() == [1.0, 0.0]
    assert aligned[0].tolist() == [1.0, 2.0]
    assert aligned[1].tolist() == [0.0, 0.0]

