from __future__ import annotations

from tests.integration.cli_runner import run_module_cli
from tests.integration.tcp_harness import TcpFrameServer


def test_module_cli_prints_verbose_and_non_verbose_lines(frames):
    verbose = frames.sample_verbose_frame()
    non_verbose = frames.sample_non_verbose_frame()

    with TcpFrameServer([verbose + non_verbose]) as server:
        result = run_module_cli(["--host", server.host, "--port", str(server.port)])

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.splitlines() == [
        "[ECU1] [TEL:CRSH] INFO: Crash event received 12 True",
        "[ECU1] [TEL:CRSH] NON_VERBOSE: payload_hex=0000000c01ff90aa",
    ]
