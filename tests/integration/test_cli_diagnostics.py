from __future__ import annotations

import socket

from tests.integration.cli_runner import run_module_cli
from tests.integration.tcp_harness import TcpFrameServer


def unused_local_port() -> int:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    _, port = probe.getsockname()
    probe.close()
    return port


def test_connection_refused_reports_stderr_and_exits_nonzero():
    result = run_module_cli(["--host", "127.0.0.1", "--port", str(unused_local_port()), "--timeout", "0.05"])

    assert result.returncode == 1
    assert result.stdout == ""
    assert "connect error:" in result.stderr
    assert "Traceback" not in result.stderr


def test_disconnect_before_messages_reports_stderr_and_exits_nonzero():
    with TcpFrameServer([]) as server:
        result = run_module_cli(["--host", server.host, "--port", str(server.port), "--timeout", "0.5"])

    assert result.returncode == 1
    assert result.stdout == ""
    assert "disconnect:" in result.stderr


def test_malformed_frame_in_strict_mode_reports_parser_error():
    malformed = b"\x20\x01\x03\x00"

    with TcpFrameServer([malformed]) as server:
        result = run_module_cli(["--host", server.host, "--port", str(server.port), "--strict"])

    assert result.returncode == 1
    assert result.stdout == ""
    assert "parser error:" in result.stderr
    assert "Traceback" not in result.stderr
