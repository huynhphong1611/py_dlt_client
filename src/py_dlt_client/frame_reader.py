"""Binary DLT frame reconstruction from arbitrary TCP chunks."""

from __future__ import annotations

import socket
import struct

from .constants import DEFAULT_MAX_FRAME_SIZE, HTYP_MSBF, STANDARD_HEADER_SIZE
from .exceptions import DltFrameError


class DltFrameBuffer:
    def __init__(self, *, max_frame_size: int = DEFAULT_MAX_FRAME_SIZE) -> None:
        self.max_frame_size = max_frame_size
        self._buffer = bytearray()

    def feed(self, data: bytes) -> None:
        if data:
            self._buffer.extend(data)

    def pop_frame(self) -> bytes | None:
        if len(self._buffer) < STANDARD_HEADER_SIZE:
            return None

        htyp = self._buffer[0]
        order = ">" if htyp & HTYP_MSBF else "<"
        length = struct.unpack_from(f"{order}H", self._buffer, 2)[0]
        if length < STANDARD_HEADER_SIZE:
            raise DltFrameError(f"DLT frame length {length} is smaller than the standard header")
        if length > self.max_frame_size:
            raise DltFrameError(f"DLT frame length {length} exceeds max frame size {self.max_frame_size}")
        if len(self._buffer) < length:
            return None
        frame = bytes(self._buffer[:length])
        del self._buffer[:length]
        return frame

    def pending(self) -> bytes:
        return bytes(self._buffer)

    def clear(self) -> None:
        self._buffer.clear()


class SocketFrameReader:
    def __init__(self, sock: socket.socket, *, max_frame_size: int = DEFAULT_MAX_FRAME_SIZE, recv_size: int = 4096) -> None:
        self.sock = sock
        self.recv_size = recv_size
        self.buffer = DltFrameBuffer(max_frame_size=max_frame_size)

    def read_frame(self) -> bytes:
        while True:
            frame = self.buffer.pop_frame()
            if frame is not None:
                return frame
            chunk = self.sock.recv(self.recv_size)
            if not chunk:
                pending = self.buffer.pending()
                if pending:
                    raise DltFrameError(f"socket closed with {len(pending)} buffered partial-frame bytes")
                raise EOFError("socket closed")
            self.buffer.feed(chunk)


def read_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise DltFrameError(f"socket closed before {size} bytes could be read")
        chunks.extend(chunk)
    return bytes(chunks)
