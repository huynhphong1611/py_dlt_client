from __future__ import annotations

from py_dlt_client.constants import LOG_LEVEL_ERROR, LOG_LEVEL_INFO

from tests.integration.cli_runner import run_module_cli
from tests.integration.tcp_harness import TcpFrameServer


def mixed_frames(frames) -> bytes:
    return b"".join(
        [
            frames.build_frame(
                frames.verbose_payload(frames.arg_string("sys init")),
                apid="SYS",
                ctid="INIT",
                level=LOG_LEVEL_INFO,
            ).frame,
            frames.build_frame(
                frames.verbose_payload(frames.arg_string("tel error")),
                apid="TEL",
                ctid="CRSH",
                level=LOG_LEVEL_ERROR,
            ).frame,
            frames.build_frame(
                frames.verbose_payload(frames.arg_string("other ecu")),
                ecu="ECU2",
                apid="SYS",
                ctid="INIT",
                level=LOG_LEVEL_ERROR,
            ).frame,
            frames.sample_non_verbose_frame(),
        ]
    )


def run_filtered(frames, *args: str) -> list[str]:
    with TcpFrameServer([mixed_frames(frames)]) as server:
        result = run_module_cli(["--host", server.host, "--port", str(server.port), *args])

    assert result.returncode == 0
    return result.stdout.splitlines()


def test_filter_by_apid_and_ctid(frames):
    assert run_filtered(frames, "--apid", "SYS", "--ctid", "INIT") == [
        "[ECU1] [SYS:INIT] INFO: sys init",
        "[ECU2] [SYS:INIT] ERROR: other ecu",
    ]


def test_filter_by_ecu(frames):
    assert run_filtered(frames, "--ecu", "ECU2") == ["[ECU2] [SYS:INIT] ERROR: other ecu"]


def test_filter_by_level_name_and_number(frames):
    assert run_filtered(frames, "--level", "ERROR") == [
        "[ECU1] [TEL:CRSH] ERROR: tel error",
        "[ECU2] [SYS:INIT] ERROR: other ecu",
    ]
    assert run_filtered(frames, "--level", "2") == [
        "[ECU1] [TEL:CRSH] ERROR: tel error",
        "[ECU2] [SYS:INIT] ERROR: other ecu",
    ]


def test_verbose_only_and_non_verbose_only(frames):
    assert len(run_filtered(frames, "--verbose-only")) == 3
    assert run_filtered(frames, "--non-verbose-only") == [
        "[ECU1] [TEL:CRSH] NON_VERBOSE: payload_hex=0000000c01ff90aa"
    ]


def test_no_filter_matches_prints_no_stdout(frames):
    assert run_filtered(frames, "--apid", "NONE") == []
