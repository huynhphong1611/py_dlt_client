from __future__ import annotations

from py_dlt_client.constants import HTYP_MSBF, HTYP_VERSION_1
from py_dlt_client.headers import parse_standard_header


def test_parse_standard_header_without_optional_fields(frames):
    payload = b"\x01\x02\x03"
    parts = frames.build_frame(
        payload,
        ecu=None,
        session_id=None,
        timestamp=None,
        apid=None,
        ctid=None,
        big_endian=True,
        mcnt=12,
    )

    header, offset = parse_standard_header(parts.frame)

    assert header.htyp & HTYP_VERSION_1
    assert header.htyp & HTYP_MSBF
    assert header.mcnt == 12
    assert header.length == len(parts.frame)
    assert header.big_endian is True
    assert header.has_ecu_id is False
    assert header.has_session_id is False
    assert header.has_timestamp is False
    assert header.has_extended_header is False
    assert header.header_size == 4
    assert offset == 4


def test_parse_little_endian_standard_header(frames):
    parts = frames.build_frame(b"\x01", big_endian=False, mcnt=3)

    header, _ = parse_standard_header(parts.frame)

    assert header.mcnt == 3
    assert header.big_endian is False
    assert header.length == len(parts.frame)
