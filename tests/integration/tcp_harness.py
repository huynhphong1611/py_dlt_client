"""Small local TCP server harness for integration tests."""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterable
from contextlib import AbstractContextManager


class TcpFrameServer(AbstractContextManager["TcpFrameServer"]):
    def __init__(self, chunks: Iterable[bytes], *, delay: float = 0.0) -> None:
        self._chunks = list(chunks)
        self._delay = delay
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(1)
        self.host, self.port = self._sock.getsockname()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._stop = threading.Event()

    def __enter__(self) -> "TcpFrameServer":
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _serve(self) -> None:
        try:
            conn, _ = self._sock.accept()
        except OSError:
            return
        with conn:
            for chunk in self._chunks:
                if self._stop.is_set():
                    break
                if self._delay:
                    time.sleep(self._delay)
                conn.sendall(chunk)

    def close(self) -> None:
        self._stop.set()
        try:
            self._sock.close()
        except OSError:
            pass
        self._thread.join(timeout=1.0)
