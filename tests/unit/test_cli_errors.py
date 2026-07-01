from __future__ import annotations

import pytest

from py_dlt_client import cli


@pytest.mark.parametrize(
    "args",
    [
        ["--host", "localhost", "--port", "0"],
        ["--host", "localhost", "--port", "65536"],
        ["--host", "localhost", "--port", "abc"],
        ["--host", "localhost", "--timeout", "0"],
        ["--host", "localhost", "--reconnect-interval", "-1"],
        ["--host", "localhost", "--max-retries", "-1"],
        ["--host", "localhost", "--max-frame-size", "3"],
    ],
)
def test_invalid_arguments_exit_with_usage(args):
    with pytest.raises(SystemExit) as excinfo:
        cli.parse_args(args)

    assert excinfo.value.code == cli.EXIT_USAGE


def test_strict_reconnect_arguments_parse():
    args = cli.parse_args(
        [
            "--host",
            "localhost",
            "--strict",
            "--reconnect",
            "--reconnect-interval",
            "0.5",
            "--max-retries",
            "2",
        ]
    )

    assert args.strict is True
    assert args.reconnect is True
    assert args.reconnect_interval == 0.5
    assert args.max_retries == 2
