from __future__ import annotations

from tests.integration.cli_runner import run_module_cli
from tests.integration.test_cli_diagnostics import unused_local_port


def test_reconnect_attempt_is_reported_before_retry_exhaustion():
    result = run_module_cli(
        [
            "--host",
            "127.0.0.1",
            "--port",
            str(unused_local_port()),
            "--timeout",
            "0.05",
            "--reconnect",
            "--reconnect-interval",
            "0.01",
            "--max-retries",
            "1",
        ]
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "reconnect attempt 1" in result.stderr
    assert "connect error:" in result.stderr
