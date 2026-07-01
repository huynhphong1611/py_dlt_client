from __future__ import annotations

import struct

from py_dlt_client.constants import LOG_LEVEL_ERROR
from py_dlt_client.headers import parse_extended_header, parse_standard_header


def test_parse_optional_and_extended_headers(frames):
    payload = frames.verbose_payload(frames.arg_string("hello"))
    frame = frames.build_frame(
        payload,
        ecu="ECU1",
        session_id=42,
        timestamp=99,
        apid="SYS",
        ctid="INIT",
        level=LOG_LEVEL_ERROR,
    ).frame

    header, offset = parse_standard_header(frame)
    extended, payload_offset = parse_extended_header(frame, offset, header)

    assert header.ecu == "ECU1"
    assert header.session_id == 42
    assert header.timestamp == 99
    assert header.has_extended_header is True
    assert extended.apid == "SYS"
    assert extended.ctid == "INIT"
    assert extended.verbose is True
    assert extended.level == LOG_LEVEL_ERROR
    assert extended.level_name == "ERROR"
    assert extended.noar == 1
    assert frame[payload_offset:] == payload


def test_message_without_extended_header_stops_after_standard_header(frames):
    frame = frames.build_frame(b"raw", apid=None, ctid=None).frame

    header, offset = parse_standard_header(frame)
    extended, payload_offset = parse_extended_header(frame, offset, header)

    assert extended is None
    assert payload_offset == offset
    assert frame[payload_offset:] == b"raw"


def test_little_endian_optional_fields(frames):
    frame = frames.build_frame(
        b"x",
        big_endian=False,
        session_id=0x01020304,
        timestamp=0x05060708,
    ).frame

    header, _ = parse_standard_header(frame)

    assert header.session_id == 0x01020304
    assert header.timestamp == 0x05060708
    assert struct.unpack_from("<H", frame, 2)[0] == len(frame)
