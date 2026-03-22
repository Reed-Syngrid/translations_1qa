from src.cli.translation_eval_cli import parse_args


def test_cli_args_basic() -> None:
    args = parse_args(["--lang", "ru", "--limit", "10"])
    assert args.lang == "ru"
    assert args.limit == 10
    assert args.inputs_root == "inputs"
    assert args.use_benchmark is False


def test_cli_use_benchmark_flag() -> None:
    args = parse_args(["--lang", "ru", "--use-benchmark"])
    assert args.use_benchmark is True

