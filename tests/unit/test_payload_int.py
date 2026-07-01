from __future__ import annotations

from py_dlt_client.payload_verbose import decode_verbose_payload


def test_decodes_signed_integer_sizes(frames):
    payload = frames.verbose_payload(
        frames.arg_signed(-1, 8),
        frames.arg_signed(-12, 16),
        frames.arg_signed(-1234, 32),
        frames.arg_signed(-123456789, 64),
    )

    args = decode_verbose_payload(payload, noar=4, big_endian=True)

    assert [arg.value for arg in args] == [-1, -12, -1234, -123456789]


def test_decodes_unsigned_integer_sizes(frames):
    payload = frames.verbose_payload(
        frames.arg_unsigned(1, 8),
        frames.arg_unsigned(152, 16),
        frames.arg_unsigned(1234, 32),
        frames.arg_unsigned(123456789, 64),
    )

    args = decode_verbose_payload(payload, noar=4, big_endian=True)

    assert [arg.value for arg in args] == [1, 152, 1234, 123456789]


def test_decodes_little_endian_integer(frames):
    payload = frames.verbose_payload(frames.arg_unsigned(0x01020304, 32, big_endian=False))

    args = decode_verbose_payload(payload, noar=1, big_endian=False)

    assert args[0].value == 0x01020304
