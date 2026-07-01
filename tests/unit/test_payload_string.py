from __future__ import annotations

from py_dlt_client.payload_verbose import decode_verbose_payload


def test_decodes_string_and_strips_null(frames):
    payload = frames.verbose_payload(frames.arg_string("Crash service started"))

    args = decode_verbose_payload(payload, noar=1, big_endian=True)

    assert args[0].type_name == "string"
    assert args[0].value == "Crash service started"
    assert args[0].display == "Crash service started"


def test_decodes_invalid_utf8_with_replacement(frames):
    payload = frames.verbose_payload(frames.arg_string(b"bad-\xff-text", nul=False))

    args = decode_verbose_payload(payload, noar=1, big_endian=True)

    assert args[0].value == "bad-\ufffd-text"
