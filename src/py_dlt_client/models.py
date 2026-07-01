"""Public data models for parsed DLT messages and client configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .constants import (
    DEFAULT_MAX_FRAME_SIZE,
    DEFAULT_PORT,
    DEFAULT_RECONNECT_INTERVAL,
    DEFAULT_TIMEOUT,
)


@dataclass(slots=True)
class DltErrorInfo:
    category: str
    message: str
    offset: int | None = None
    raw: bytes | None = None


@dataclass(slots=True)
class DltArgument:
    type_name: str
    value: Any
    raw: bytes
    type_info: int
    supported: bool = True
    display: str | None = None

    def __post_init__(self) -> None:
        if self.display is None:
            if self.type_name == "raw" and isinstance(self.value, (bytes, bytearray)):
                self.display = f"raw={bytes(self.value).hex()}"
            elif self.supported:
                self.display = str(self.value)
            else:
                self.display = f"unsupported={self.raw.hex()}"


@dataclass(slots=True)
class DltHeader:
    htyp: int
    mcnt: int
    length: int
    big_endian: bool
    has_extended_header: bool
    has_ecu_id: bool
    has_session_id: bool
    has_timestamp: bool
    ecu: str | None = None
    session_id: int | None = None
    timestamp: int | None = None
    header_size: int = 0


@dataclass(slots=True)
class DltExtendedHeader:
    msin: int
    noar: int
    apid: str
    ctid: str
    verbose: bool
    level: int | None
    level_name: str | None


@dataclass(slots=True)
class DltMessage:
    ecu: str | None
    apid: str | None
    ctid: str | None
    session_id: int | None
    timestamp: int | None
    counter: int
    level: int | None
    level_name: str | None
    verbose: bool
    args: list[DltArgument] = field(default_factory=list)
    text: str = ""
    raw_payload: bytes = b""
    raw_frame: bytes = b""
    payload_hex: str = ""
    message_id: int | None = None
    errors: list[DltErrorInfo] = field(default_factory=list)
    header: DltHeader | None = None
    extended_header: DltExtendedHeader | None = None

    def __post_init__(self) -> None:
        if not self.payload_hex:
            self.payload_hex = self.raw_payload.hex()


@dataclass(slots=True)
class DltFilter:
    ecu: set[str] | None = None
    apid: set[str] | None = None
    ctid: set[str] | None = None
    level: set[str | int] | None = None
    verbose_only: bool = False
    non_verbose_only: bool = False


@dataclass(slots=True)
class DltClientConfig:
    host: str
    port: int = DEFAULT_PORT
    timeout: float | None = DEFAULT_TIMEOUT
    auto_reconnect: bool = False
    reconnect_interval: float = DEFAULT_RECONNECT_INTERVAL
    max_retries: int | None = None
    strict: bool = False
    max_frame_size: int = DEFAULT_MAX_FRAME_SIZE
    filters: DltFilter | dict[str, Any] | None = None


@dataclass(slots=True)
class ClientEvent:
    type: str
    message: DltMessage | None = None
    error: BaseException | None = None
    attempt: int | None = None
    delay: float | None = None
