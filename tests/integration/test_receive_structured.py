from __future__ import annotations

from py_dlt_client import DltClient

from tests.conftest import assert_message_identity
from tests.integration.tcp_harness import TcpFrameServer


def test_client_receives_structured_messages_in_stream_order(frames):
    first = frames.sample_verbose_frame()
    second = frames.sample_non_verbose_frame()

    with TcpFrameServer([first[:7], first[7:] + second]) as server:
        client = DltClient(host=server.host, port=server.port, timeout=1.0)
        messages = []
        for message in client.messages():
            messages.append(message)
            if len(messages) == 2:
                break
        client.close()

    assert len(messages) == 2
    assert_message_identity(messages[0])
    assert messages[0].verbose is True
    assert messages[0].raw_frame == first
    assert_message_identity(messages[1])
    assert messages[1].verbose is False
    assert messages[1].raw_frame == second
