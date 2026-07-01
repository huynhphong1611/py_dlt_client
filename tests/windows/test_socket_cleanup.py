from __future__ import annotations

from py_dlt_client import DltClient

from tests.integration.tcp_harness import TcpFrameServer
from tests.windows.cleanup_helpers import assert_client_closed


def test_repeated_connect_read_close_cleanup(frames):
    for _ in range(2):
        with TcpFrameServer([frames.sample_verbose_frame()]) as server:
            client = DltClient(host=server.host, port=server.port, timeout=1.0)
            iterator = client.messages()
            assert next(iterator).raw_frame
            assert_client_closed(client)
