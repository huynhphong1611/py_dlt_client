from __future__ import annotations

from py_dlt_client.client import DltClient
from py_dlt_client.formatter import format_message


def test_formats_verbose_message(frames):
    payload = frames.verbose_payload(frames.arg_string("hello"), frames.arg_unsigned(7))
    message = DltClient(host="127.0.0.1").parse_frame(frames.build_frame(payload, level=4).frame)

    assert format_message(message) == "[ECU1] [TEL:CRSH] INFO: hello 7"


def test_formats_non_verbose_payload_hex(frames):
    message = DltClient(host="127.0.0.1").parse_frame(frames.sample_non_verbose_frame())

    assert format_message(message) == "[ECU1] [TEL:CRSH] NON_VERBOSE: payload_hex=0000000c01ff90aa"


def test_formats_unknown_level(frames):
    payload = frames.verbose_payload(frames.arg_string("hello"))
    message = DltClient(host="127.0.0.1").parse_frame(frames.build_frame(payload, level=9).frame)

    assert "UNKNOWN: hello" in format_message(message)
