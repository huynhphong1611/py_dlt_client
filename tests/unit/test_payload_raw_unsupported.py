from __future__ import annotations

import pytest

from py_dlt_client.exceptions import DltUnsupportedTypeError
from py_dlt_client.payload_verbose import decode_verbose_payload


def test_decodes_raw_bytes(frames):
    payload = frames.verbose_payload(frames.arg_raw(b"\x01\xff\x90"))

    args = decode_verbose_payload(payload, noar=1, big_endian=True)

    assert args[0].type_name == "raw"
    assert args[0].value == b"\x01\xff\x90"
    assert args[0].display == "raw=01ff90"


def test_preserves_unsupported_argument_in_non_strict_mode(frames):
    payload = frames.verbose_payload(frames.arg_unsupported(b"\xaa\xbb"))

    args = decode_verbose_payload(payload, noar=1, big_endian=True, strict=False)

    assert args[0].supported is False
    assert args[0].raw.endswith(b"\xaa\xbb")
    assert args[0].display == f"unsupported={args[0].raw.hex()}"


def test_raises_for_unsupported_argument_in_strict_mode(frames):
    payload = frames.verbose_payload(frames.arg_unsupported(b"\xaa\xbb"))

    with pytest.raises(DltUnsupportedTypeError):
        decode_verbose_payload(payload, noar=1, big_endian=True, strict=True)
