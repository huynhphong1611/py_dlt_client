from __future__ import annotations

import pytest

from py_dlt_client import cli


def test_repeated_filter_arguments_are_preserved():
    args = cli.parse_args(
        [
            "--host",
            "localhost",
            "--ecu",
            "ECU1",
            "--ecu",
            "ECU2",
            "--apid",
            "SYS",
            "--ctid",
            "INIT",
            "--level",
            "ERROR",
            "--level",
            "2",
        ]
    )
    filters = cli._build_filters(args)

    assert filters == {
        "ecu": ["ECU1", "ECU2"],
        "apid": ["SYS"],
        "ctid": ["INIT"],
        "level": ["ERROR", 2],
    }


def test_verbose_only_filter_argument():
    args = cli.parse_args(["--host", "localhost", "--verbose-only"])

    assert cli._build_filters(args) == {"verbose_only": True}


def test_non_verbose_only_filter_argument():
    args = cli.parse_args(["--host", "localhost", "--non-verbose-only"])

    assert cli._build_filters(args) == {"non_verbose_only": True}


def test_verbose_mode_filters_are_mutually_exclusive():
    with pytest.raises(SystemExit) as excinfo:
        cli.parse_args(["--host", "localhost", "--verbose-only", "--non-verbose-only"])

    assert excinfo.value.code == cli.EXIT_USAGE
