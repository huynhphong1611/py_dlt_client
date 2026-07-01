from __future__ import annotations

import pytest

from py_dlt_client import cli
from py_dlt_client.constants import DEFAULT_MAX_FRAME_SIZE, DEFAULT_PORT, DEFAULT_TIMEOUT


def test_host_is_required():
    with pytest.raises(SystemExit) as excinfo:
        cli.parse_args([])

    assert excinfo.value.code == cli.EXIT_USAGE


def test_default_port_timeout_and_frame_size():
    args = cli.parse_args(["--host", "localhost"])

    assert args.host == "localhost"
    assert args.port == DEFAULT_PORT
    assert args.timeout == DEFAULT_TIMEOUT
    assert args.max_frame_size == DEFAULT_MAX_FRAME_SIZE


def test_explicit_port_is_parsed():
    args = cli.parse_args(["--host", "localhost", "--port", "3500"])

    assert args.port == 3500


def test_help_exits_successfully(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.parse_args(["--help"])

    assert excinfo.value.code == cli.EXIT_SUCCESS
    assert "--host" in capsys.readouterr().out
