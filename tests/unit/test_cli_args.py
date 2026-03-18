from src.cli.translation_eval_cli import parse_args


def test_cli_args_basic() -> None:
    args = parse_args(["--lang", "ru", "--limit", "10"])
    assert args.lang == "ru"
    assert args.limit == 10

