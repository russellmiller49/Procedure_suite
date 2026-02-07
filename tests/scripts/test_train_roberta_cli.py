from pathlib import Path


def test_train_roberta_cli_parses_new_flags():
    from ml.scripts.train_roberta import build_arg_parser

    parser = build_arg_parser()
    args = parser.parse_args(
        [
            "--loss",
            "asl",
            "--asl-gamma-neg",
            "4",
            "--asl-gamma-pos",
            "1",
            "--asl-clip",
            "0.05",
            "--dormant-mode",
            "auto",
            "--dormant-min-positives",
            "20",
            "--teacher-logits",
            str(Path("data/ml_training/teacher_logits.npz")),
            "--distill-alpha",
            "0.5",
            "--distill-temp",
            "2.0",
            "--distill-loss",
            "mse",
        ]
    )

    assert args.loss == "asl"
    assert args.teacher_logits == Path("data/ml_training/teacher_logits.npz")
    assert args.distill_loss == "mse"

