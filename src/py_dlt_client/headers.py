"""DLT V1 standard and extended header parsing."""

from __future__ import annotations

import struct

from .constants import (
    DEFAULT_MAX_FRAME_SIZE,
    EXTENDED_HEADER_SIZE,
    HTYP_MSBF,
    HTYP_UEH,
    HTYP_WEID,
    HTYP_WSID,
    HTYP_WTMS,
    LOG_LEVEL_NAMES,
    MSIN_MTIN_MASK,
    MSIN_MTIN_SHIFT,
    MSIN_VERB,
    STANDARD_HEADER_SIZE,
)
from .exceptions import DltFrameError
from .models import DltExtendedHeader, DltHeader


def decode_id(raw: bytes) -> str:
    return raw.rstrip(b"\x00 ").decode("ascii", "replace")


def parse_standard_header(frame: bytes, *, max_frame_size: int = DEFAULT_MAX_FRAME_SIZE) -> tuple[DltHeader, int]:
    if len(frame) < STANDARD_HEADER_SIZE:
        raise DltFrameError("DLT frame is shorter than the standard header")

    htyp = frame[0]
    mcnt = frame[1]
    big_endian = bool(htyp & HTYP_MSBF)
    order = ">" if big_endian else "<"
    length = struct.unpack_from(f"{order}H", frame, 2)[0]
    if length < STANDARD_HEADER_SIZE:
        raise DltFrameError(f"DLT frame length {length} is smaller than the standard header")
    if length > max_frame_size:
        raise DltFrameError(f"DLT frame length {length} exceeds max frame size {max_frame_size}")
    if len(frame) < length:
        raise DltFrameError("DLT frame is truncated")

    offset = STANDARD_HEADER_SIZE
    has_ecu_id = bool(htyp & HTYP_WEID)
    has_session_id = bool(htyp & HTYP_WSID)
    has_timestamp = bool(htyp & HTYP_WTMS)
    has_extended_header = bool(htyp & HTYP_UEH)

    needed = offset
    needed += 4 if has_ecu_id else 0
    needed += 4 if has_session_id else 0
    needed += 4 if has_timestamp else 0
    if length < needed or len(frame) < needed:
        raise DltFrameError("DLT optional standard header fields are truncated")

    ecu: str | None = None
    session_id: int | None = None
    timestamp: int | None = None

    if has_ecu_id:
        ecu = decode_id(frame[offset : offset + 4])
        offset += 4
    if has_session_id:
        session_id = struct.unpack_from(f"{order}I", frame, offset)[0]
        offset += 4
    if has_timestamp:
        timestamp = struct.unpack_from(f"{order}I", frame, offset)[0]
        offset += 4

    return (
        DltHeader(
            htyp=htyp,
            mcnt=mcnt,
            length=length,
            big_endian=big_endian,
            has_extended_header=has_extended_header,
            has_ecu_id=has_ecu_id,
            has_session_id=has_session_id,
            has_timestamp=has_timestamp,
            ecu=ecu,
            session_id=session_id,
            timestamp=timestamp,
            header_size=offset,
        ),
        offset,
    )


def parse_extended_header(
    frame: bytes, offset: int, header: DltHeader
) -> tuple[DltExtendedHeader | None, int]:
    if not header.has_extended_header:
        return None, offset

    end = offset + EXTENDED_HEADER_SIZE
    if header.length < end or len(frame) < end:
        raise DltFrameError("DLT extended header is truncated")

    msin = frame[offset]
    noar = frame[offset + 1]
    apid = decode_id(frame[offset + 2 : offset + 6])
    ctid = decode_id(frame[offset + 6 : offset + 10])
    verbose = bool(msin & MSIN_VERB)
    level = (msin & MSIN_MTIN_MASK) >> MSIN_MTIN_SHIFT
    level_name = LOG_LEVEL_NAMES.get(level)
    return (
        DltExtendedHeader(
            msin=msin,
            noar=noar,
            apid=apid,
            ctid=ctid,
            verbose=verbose,
            level=level,
            level_name=level_name,
        ),
        end,
    )


def parse_headers(frame: bytes, *, max_frame_size: int = DEFAULT_MAX_FRAME_SIZE) -> tuple[DltHeader, DltExtendedHeader | None, int]:
    header, offset = parse_standard_header(frame, max_frame_size=max_frame_size)
    extended, payload_offset = parse_extended_header(frame, offset, header)
    return header, extended, payload_offset
