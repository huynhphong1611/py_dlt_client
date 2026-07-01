"""Verbose DLT payload decoding for the first-version supported subset."""

from __future__ import annotations

import logging
import struct

from .constants import (
    TYPE_BOOL,
    TYPE_FLOAT,
    TYPE_KIND_MASK,
    TYPE_RAW,
    TYPE_SIGNED_INT,
    TYPE_SIZE_8,
    TYPE_SIZE_16,
    TYPE_SIZE_32,
    TYPE_SIZE_64,
    TYPE_SIZE_MASK,
    TYPE_STRING,
    TYPE_UNSIGNED_INT,
)
from .exceptions import DltParserError, DltUnsupportedTypeError
from .models import DltArgument

logger = logging.getLogger("py_dlt_client")


def decode_verbose_payload(
    payload: bytes,
    *,
    noar: int,
    big_endian: bool,
    strict: bool = False,
) -> list[DltArgument]:
    order = ">" if big_endian else "<"
    offset = 0
    args: list[DltArgument] = []
    for _ in range(noar):
        if offset >= len(payload):
            break
        start = offset
        if offset + 4 > len(payload):
            raise DltParserError("verbose payload ended before type_info")
        type_info = struct.unpack_from(f"{order}I", payload, offset)[0]
        offset += 4
        kind = type_info & TYPE_KIND_MASK
        size = type_info & TYPE_SIZE_MASK
        try:
            if kind == TYPE_STRING:
                value, raw, offset = _decode_length_bytes(payload, offset, order)
                text = _decode_string(value)
                args.append(DltArgument("string", text, payload[start:offset], type_info))
            elif kind == TYPE_SIGNED_INT:
                value, offset = _decode_int(payload, offset, order, size, signed=True)
                args.append(DltArgument("signed_int", value, payload[start:offset], type_info))
            elif kind == TYPE_UNSIGNED_INT:
                value, offset = _decode_int(payload, offset, order, size, signed=False)
                args.append(DltArgument("unsigned_int", value, payload[start:offset], type_info))
            elif kind == TYPE_BOOL:
                _ensure(payload, offset, 1)
                value = payload[offset] != 0
                offset += 1
                args.append(DltArgument("bool", value, payload[start:offset], type_info))
            elif kind == TYPE_FLOAT:
                value, offset = _decode_float(payload, offset, order, size)
                args.append(DltArgument("float", value, payload[start:offset], type_info))
            elif kind == TYPE_RAW:
                value, raw, offset = _decode_length_bytes(payload, offset, order)
                args.append(DltArgument("raw", raw, payload[start:offset], type_info))
            else:
                remaining = payload[start:]
                if strict:
                    raise DltUnsupportedTypeError(f"unsupported verbose argument type_info=0x{type_info:08x}")
                logger.debug("unsupported verbose argument type_info=0x%08x", type_info)
                args.append(
                    DltArgument(
                        "unsupported",
                        None,
                        remaining,
                        type_info,
                        supported=False,
                        display=f"unsupported={remaining.hex()}",
                    )
                )
                break
        except (DltParserError, DltUnsupportedTypeError):
            raise
        except Exception as exc:  # pragma: no cover - defensive conversion
            raise DltParserError(str(exc)) from exc
    return args


def _decode_length_bytes(payload: bytes, offset: int, order: str) -> tuple[bytes, bytes, int]:
    _ensure(payload, offset, 2)
    length = struct.unpack_from(f"{order}H", payload, offset)[0]
    offset += 2
    _ensure(payload, offset, length)
    raw = payload[offset : offset + length]
    return raw, raw, offset + length


def _decode_string(raw: bytes) -> str:
    if raw.endswith(b"\x00"):
        raw = raw[:-1]
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-8", "replace")


def _decode_int(payload: bytes, offset: int, order: str, size: int, *, signed: bool) -> tuple[int, int]:
    fmt_map = {
        (TYPE_SIZE_8, True): "b",
        (TYPE_SIZE_8, False): "B",
        (TYPE_SIZE_16, True): "h",
        (TYPE_SIZE_16, False): "H",
        (TYPE_SIZE_32, True): "i",
        (TYPE_SIZE_32, False): "I",
        (TYPE_SIZE_64, True): "q",
        (TYPE_SIZE_64, False): "Q",
    }
    fmt = fmt_map.get((size, signed))
    if fmt is None:
        raise DltParserError(f"unsupported integer size flag {size}")
    width = struct.calcsize(fmt)
    _ensure(payload, offset, width)
    return struct.unpack_from(f"{order}{fmt}", payload, offset)[0], offset + width


def _decode_float(payload: bytes, offset: int, order: str, size: int) -> tuple[float, int]:
    if size == TYPE_SIZE_32:
        fmt = "f"
    elif size == TYPE_SIZE_64:
        fmt = "d"
    else:
        raise DltParserError(f"unsupported float size flag {size}")
    width = struct.calcsize(fmt)
    _ensure(payload, offset, width)
    return struct.unpack_from(f"{order}{fmt}", payload, offset)[0], offset + width


def _ensure(payload: bytes, offset: int, size: int) -> None:
    if offset + size > len(payload):
        raise DltParserError("verbose payload is truncated")
