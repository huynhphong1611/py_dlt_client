"""Deterministic DLT V1 frame builders for tests."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Iterable

from py_dlt_client.constants import (
    HTYP_MSBF,
    HTYP_UEH,
    HTYP_VERSION_1,
    HTYP_WEID,
    HTYP_WSID,
    HTYP_WTMS,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARN,
    MSIN_VERB,
    TYPE_BOOL,
    TYPE_FLOAT,
    TYPE_RAW,
    TYPE_SIGNED_INT,
    TYPE_SIZE_8,
    TYPE_SIZE_16,
    TYPE_SIZE_32,
    TYPE_SIZE_64,
    TYPE_STRING,
    TYPE_UNSIGNED_INT,
)


def _id4(value: str) -> bytes:
    return value.encode("ascii", "replace")[:4].ljust(4, b"\x00")


def type_info(kind: int, size: int = 0) -> int:
    return kind | size


@dataclass(frozen=True)
class FrameParts:
    frame: bytes
    payload: bytes
    length: int


def build_frame(
    payload: bytes = b"",
    *,
    mcnt: int = 1,
    ecu: str | None = "ECU1",
    session_id: int | None = 1234,
    timestamp: int | None = 987654321,
    apid: str | None = "TEL",
    ctid: str | None = "CRSH",
    verbose: bool = True,
    level: int = LOG_LEVEL_INFO,
    noar: int | None = None,
    big_endian: bool = True,
) -> FrameParts:
    htyp = HTYP_VERSION_1
    htyp |= HTYP_MSBF if big_endian else 0
    optional = b""
    if ecu is not None:
        htyp |= HTYP_WEID
        optional += _id4(ecu)
    order = ">" if big_endian else "<"
    if session_id is not None:
        htyp |= HTYP_WSID
        optional += struct.pack(f"{order}I", session_id)
    if timestamp is not None:
        htyp |= HTYP_WTMS
        optional += struct.pack(f"{order}I", timestamp)

    extended = b""
    if apid is not None and ctid is not None:
        htyp |= HTYP_UEH
        count = noar if noar is not None else count_verbose_args(payload)
        msin = (level << 4) | (MSIN_VERB if verbose else 0)
        extended = bytes([msin, count & 0xFF]) + _id4(apid) + _id4(ctid)

    length = 4 + len(optional) + len(extended) + len(payload)
    header = bytes([htyp, mcnt & 0xFF]) + struct.pack(f"{order}H", length)
    return FrameParts(header + optional + extended + payload, payload, length)


def count_verbose_args(payload: bytes, *, big_endian: bool = True) -> int:
    order = ">" if big_endian else "<"
    offset = 0
    count = 0
    while offset + 4 <= len(payload):
        info = struct.unpack_from(f"{order}I", payload, offset)[0]
        offset += 4
        kind = info & 0x00000F00
        size = info & 0x0000000F
        if kind in {TYPE_STRING, TYPE_RAW}:
            if offset + 2 > len(payload):
                break
            length = struct.unpack_from(f"{order}H", payload, offset)[0]
            offset += 2 + length
        elif kind == TYPE_BOOL:
            offset += 1
        elif size == TYPE_SIZE_8:
            offset += 1
        elif size == TYPE_SIZE_16:
            offset += 2
        elif size == TYPE_SIZE_32:
            offset += 4
        elif size == TYPE_SIZE_64:
            offset += 8
        else:
            count += 1
            break
        count += 1
    return count


def arg_string(value: str | bytes, *, big_endian: bool = True, nul: bool = True) -> bytes:
    raw = value if isinstance(value, bytes) else value.encode("utf-8")
    if nul:
        raw += b"\x00"
    order = ">" if big_endian else "<"
    return struct.pack(f"{order}IH", type_info(TYPE_STRING), len(raw)) + raw


def arg_signed(value: int, size: int = 32, *, big_endian: bool = True) -> bytes:
    order = ">" if big_endian else "<"
    size_map = {
        8: (TYPE_SIZE_8, "b"),
        16: (TYPE_SIZE_16, "h"),
        32: (TYPE_SIZE_32, "i"),
        64: (TYPE_SIZE_64, "q"),
    }
    size_flag, fmt = size_map[size]
    return struct.pack(f"{order}I{fmt}", type_info(TYPE_SIGNED_INT, size_flag), value)


def arg_unsigned(value: int, size: int = 32, *, big_endian: bool = True) -> bytes:
    order = ">" if big_endian else "<"
    size_map = {
        8: (TYPE_SIZE_8, "B"),
        16: (TYPE_SIZE_16, "H"),
        32: (TYPE_SIZE_32, "I"),
        64: (TYPE_SIZE_64, "Q"),
    }
    size_flag, fmt = size_map[size]
    return struct.pack(f"{order}I{fmt}", type_info(TYPE_UNSIGNED_INT, size_flag), value)


def arg_bool(value: bool, *, big_endian: bool = True) -> bytes:
    order = ">" if big_endian else "<"
    return struct.pack(f"{order}IB", type_info(TYPE_BOOL, TYPE_SIZE_8), 1 if value else 0)


def arg_float(value: float, size: int = 32, *, big_endian: bool = True) -> bytes:
    order = ">" if big_endian else "<"
    if size == 32:
        return struct.pack(f"{order}If", type_info(TYPE_FLOAT, TYPE_SIZE_32), value)
    if size == 64:
        return struct.pack(f"{order}Id", type_info(TYPE_FLOAT, TYPE_SIZE_64), value)
    raise ValueError("float size must be 32 or 64")


def arg_raw(value: bytes, *, big_endian: bool = True) -> bytes:
    order = ">" if big_endian else "<"
    return struct.pack(f"{order}IH", type_info(TYPE_RAW), len(value)) + value


def arg_unsupported(value: bytes = b"\xAA\xBB", *, big_endian: bool = True) -> bytes:
    order = ">" if big_endian else "<"
    return struct.pack(f"{order}I", 0x00000F00) + value


def verbose_payload(*args: bytes) -> bytes:
    return b"".join(args)


def sample_verbose_frame() -> bytes:
    payload = verbose_payload(arg_string("Crash event received"), arg_signed(12), arg_bool(True))
    return build_frame(payload, level=LOG_LEVEL_INFO).frame


def sample_non_verbose_frame() -> bytes:
    payload = b"\x00\x00\x00\x0c\x01\xff\x90\xaa"
    return build_frame(payload, verbose=False, level=LOG_LEVEL_WARN, noar=0).frame


def coalesced(frames: Iterable[bytes]) -> bytes:
    return b"".join(frames)
