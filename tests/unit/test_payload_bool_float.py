from __future__ import annotations

from py_dlt_client.payload_verbose import decode_verbose_payload


def test_decodes_boolean_values(frames):
    payload = frames.verbose_payload(frames.arg_bool(False), frames.arg_bool(True))

    args = decode_verbose_payload(payload, noar=2, big_endian=True)

    assert [arg.value for arg in args] == [False, True]


def test_decodes_float32_and_float64(frames):
    payload = frames.verbose_payload(frames.arg_float(12.5, 32), frames.arg_float(25.25, 64))

    args = decode_verbose_payload(payload, noar=2, big_endian=True)

    assert args[0].value == 12.5
    assert args[1].value == 25.25


def test_decodes_little_endian_float(frames):
    payload = frames.verbose_payload(frames.arg_float(1.5, 32, big_endian=False))

    args = decode_verbose_payload(payload, noar=1, big_endian=False)

    assert args[0].value == 1.5
