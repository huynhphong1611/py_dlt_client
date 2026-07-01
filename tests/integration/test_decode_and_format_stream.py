from __future__ import annotations

from py_dlt_client import DltClient

from tests.integration.tcp_harness import TcpFrameServer


def test_mixed_decode_and_format_stream_continues_in_non_strict_mode(frames):
    verbose = frames.build_frame(frames.verbose_payload(frames.arg_string("hello"), frames.arg_unsigned(12))).frame
    non_verbose = frames.sample_non_verbose_frame()
    unsupported = frames.build_frame(frames.verbose_payload(frames.arg_string("first"), frames.arg_unsupported())).frame

    with TcpFrameServer([verbose + non_verbose + unsupported]) as server:
        client = DltClient(host=server.host, port=server.port, timeout=1.0, strict=False)
        messages = []
        for message in client.messages():
            messages.append(message)
            if len(messages) == 3:
                break
        client.close()

    assert messages[0].text == "[ECU1] [TEL:CRSH] INFO: hello 12"
    assert messages[1].text.endswith("payload_hex=0000000c01ff90aa")
    assert messages[2].args[-1].supported is False
