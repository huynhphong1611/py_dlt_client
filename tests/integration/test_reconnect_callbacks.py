from __future__ import annotations

import socket

from py_dlt_client import DltClient


def test_connection_failure_emits_reconnect_attempts():
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    host, port = probe.getsockname()
    probe.close()
    attempts = []
    errors = []

    client = DltClient(
        host=host,
        port=port,
        timeout=0.05,
        auto_reconnect=True,
        reconnect_interval=0.01,
        max_retries=1,
    )
    client.on_reconnect_attempt(attempts.append)
    client.on_error(errors.append)

    try:
        list(client.messages())
    except Exception:
        pass

    assert attempts == [1]
    assert errors
