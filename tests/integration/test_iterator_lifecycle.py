from __future__ import annotations

from py_dlt_client import DltClient

from tests.integration.tcp_harness import TcpFrameServer


def test_iterator_close_releases_socket(frames):
    with TcpFrameServer([frames.sample_verbose_frame()]) as server:
        client = DltClient(host=server.host, port=server.port, timeout=1.0)
        iterator = client.messages()
        message = next(iterator)
        assert message.raw_frame
        client.close()

    assert client._sock is None
