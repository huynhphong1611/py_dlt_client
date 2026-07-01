from __future__ import annotations

from py_dlt_client import cli


def test_keyboard_interrupt_closes_client_and_exits_success(monkeypatch):
    closed = False

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def on_error(self, callback):
            return self

        def on_disconnect(self, callback):
            return self

        def on_reconnect_attempt(self, callback):
            return self

        def messages(self):
            raise KeyboardInterrupt
            yield

        def close(self):
            nonlocal closed
            closed = True

    monkeypatch.setattr(cli, "DltClient", FakeClient)

    assert cli.main(["--host", "127.0.0.1"]) == cli.EXIT_SUCCESS
    assert closed is True
