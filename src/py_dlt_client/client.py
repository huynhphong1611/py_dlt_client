"""DLT TCP client lifecycle and message delivery."""

from __future__ import annotations

import logging
import socket
import time
from collections.abc import Callable, Iterator
from typing import Any

from .constants import (
    DEFAULT_MAX_FRAME_SIZE,
    DEFAULT_PORT,
    DEFAULT_RECONNECT_INTERVAL,
    DEFAULT_TIMEOUT,
)
from .exceptions import DltConnectionError, DltError, DltFrameError, DltParserError
from .filters import matches_filter, normalize_filter
from .formatter import format_message
from .frame_reader import SocketFrameReader
from .headers import parse_headers
from .models import DltErrorInfo, DltFilter, DltMessage
from .payload_verbose import decode_verbose_payload

logger = logging.getLogger("py_dlt_client")


class DltClient:
    def __init__(
        self,
        host: str,
        *,
        port: int = DEFAULT_PORT,
        timeout: float | None = DEFAULT_TIMEOUT,
        auto_reconnect: bool = False,
        reconnect_interval: float = DEFAULT_RECONNECT_INTERVAL,
        max_retries: int | None = None,
        strict: bool = False,
        filters: DltFilter | dict[str, Any] | None = None,
        max_frame_size: int = DEFAULT_MAX_FRAME_SIZE,
    ) -> None:
        if not host:
            raise ValueError("host is required")
        if not 1 <= port <= 65_535:
            raise ValueError("port must be between 1 and 65535")
        if timeout is not None and timeout <= 0:
            raise ValueError("timeout must be positive")
        if reconnect_interval <= 0:
            raise ValueError("reconnect_interval must be positive")
        if max_retries is not None and max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if max_frame_size < 4:
            raise ValueError("max_frame_size must be at least the DLT standard header size")
        self.host = host
        self.port = port
        self.timeout = timeout
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        self.max_retries = max_retries
        self.strict = strict
        self.max_frame_size = max_frame_size
        self.filters = normalize_filter(filters)
        self._sock: socket.socket | None = None
        self._closed = False
        self._callbacks: dict[str, list[Callable[..., None]]] = {
            "message": [],
            "connect": [],
            "disconnect": [],
            "reconnect_attempt": [],
            "error": [],
        }

    def connect(self) -> None:
        self.close()
        try:
            self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            if self.timeout is not None:
                self._sock.settimeout(self.timeout)
            self._closed = False
            self._emit("connect")
        except OSError as exc:
            self._sock = None
            error = DltConnectionError(str(exc))
            self._emit("error", error)
            raise error from exc

    def close(self) -> None:
        self._closed = True
        self._drop_socket()

    def _drop_socket(self) -> None:
        sock = self._sock
        self._sock = None
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass

    def messages(self) -> Iterator[DltMessage]:
        attempts = 0
        while not self._closed:
            if self._sock is None:
                try:
                    self.connect()
                    attempts = 0
                except DltConnectionError:
                    if not self.auto_reconnect or self._retry_exhausted(attempts):
                        raise
                    attempts += 1
                    self._emit("reconnect_attempt", attempts)
                    time.sleep(self.reconnect_interval)
                    continue

            assert self._sock is not None
            reader = SocketFrameReader(self._sock, max_frame_size=self.max_frame_size)
            try:
                while not self._closed:
                    frame = reader.read_frame()
                    message = self.parse_frame(frame)
                    if matches_filter(message, self.filters):
                        yield message
            except EOFError as exc:
                self._handle_disconnect(exc)
            except (OSError, DltFrameError, DltParserError) as exc:
                if self.strict:
                    self._emit("error", exc)
                    raise
                self._handle_disconnect(exc)
            if not self.auto_reconnect or self._retry_exhausted(attempts):
                break
            attempts += 1
            self._emit("reconnect_attempt", attempts)
            time.sleep(self.reconnect_interval)

    def run_forever(self) -> None:
        for message in self.messages():
            self._emit("message", message)

    def parse_frame(self, frame: bytes) -> DltMessage:
        header, extended, payload_offset = parse_headers(frame, max_frame_size=self.max_frame_size)
        payload = frame[payload_offset : header.length]
        errors: list[DltErrorInfo] = []
        args = []
        verbose = bool(extended.verbose) if extended else False
        if extended and extended.verbose:
            try:
                args = decode_verbose_payload(
                    payload,
                    noar=extended.noar,
                    big_endian=header.big_endian,
                    strict=self.strict,
                )
            except DltError as exc:
                if self.strict:
                    raise
                errors.append(DltErrorInfo("parser", str(exc), raw=payload))
        message_id = None
        if not verbose and len(payload) >= 4:
            byteorder = "big" if header.big_endian else "little"
            message_id = int.from_bytes(payload[:4], byteorder)
        message = DltMessage(
            ecu=header.ecu,
            apid=extended.apid if extended else None,
            ctid=extended.ctid if extended else None,
            session_id=header.session_id,
            timestamp=header.timestamp,
            counter=header.mcnt,
            level=extended.level if extended else None,
            level_name=extended.level_name if extended else None,
            verbose=verbose,
            args=args,
            raw_payload=payload,
            raw_frame=frame[: header.length],
            payload_hex=payload.hex(),
            message_id=message_id,
            errors=errors,
            header=header,
            extended_header=extended,
        )
        message.text = format_message(message)
        return message

    def on_message(self, callback: Callable[[DltMessage], None]) -> "DltClient":
        self._callbacks["message"].append(callback)
        return self

    def on_connect(self, callback: Callable[[], None]) -> "DltClient":
        self._callbacks["connect"].append(callback)
        return self

    def on_disconnect(self, callback: Callable[[BaseException | None], None]) -> "DltClient":
        self._callbacks["disconnect"].append(callback)
        return self

    def on_reconnect_attempt(self, callback: Callable[[int], None]) -> "DltClient":
        self._callbacks["reconnect_attempt"].append(callback)
        return self

    def on_error(self, callback: Callable[[BaseException], None]) -> "DltClient":
        self._callbacks["error"].append(callback)
        return self

    def _handle_disconnect(self, exc: BaseException | None) -> None:
        self._emit("disconnect", exc)
        self._drop_socket()

    def _retry_exhausted(self, attempts: int) -> bool:
        return self.max_retries is not None and attempts >= self.max_retries

    def _emit(self, event: str, *args: Any) -> None:
        for callback in list(self._callbacks[event]):
            try:
                callback(*args)
            except Exception as exc:  # pragma: no cover - callback-owned failure
                logger.exception("DLT callback failed")
                if event != "error":
                    self._emit("error", exc)
