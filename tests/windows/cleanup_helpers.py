from __future__ import annotations


def assert_client_closed(client) -> None:
    client.close()
    sock = getattr(client, "_sock", None)
    assert sock is None
