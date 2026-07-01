"""Command-line interface for live DLT TCP streaming."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TextIO

from .client import DltClient
from .constants import (
    DEFAULT_MAX_FRAME_SIZE,
    DEFAULT_PORT,
    DEFAULT_RECONNECT_INTERVAL,
    DEFAULT_TIMEOUT,
)
from .exceptions import DltConnectionError, DltError, DltFrameError, DltParserError

EXIT_SUCCESS = 0
EXIT_RUNTIME_ERROR = 1
EXIT_USAGE = 2


@dataclass(slots=True)
class _RunState:
    messages_seen: int = 0
    reported_error: bool = False
    disconnect_error: BaseException | None = None


def port_arg(value: str) -> int:
    try:
        port = int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not 1 <= port <= 65_535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def positive_float_arg(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be a positive number") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def non_negative_int_arg(value: str) -> int:
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be a non-negative integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def frame_size_arg(value: str) -> int:
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("max frame size must be an integer") from exc
    if parsed < 4:
        raise argparse.ArgumentTypeError("max frame size must be at least 4")
    return parsed


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="py-dlt-client",
        description="Receive live DLT V1 messages from a TCP dlt-daemon endpoint.",
    )
    parser.add_argument("--host", required=True, help="DLT TCP host or IP address")
    parser.add_argument("--port", type=port_arg, default=DEFAULT_PORT, help="DLT TCP port")
    parser.add_argument(
        "--timeout",
        type=positive_float_arg,
        default=DEFAULT_TIMEOUT,
        help="Socket connect/read timeout in seconds",
    )
    parser.add_argument(
        "--max-frame-size",
        type=frame_size_arg,
        default=DEFAULT_MAX_FRAME_SIZE,
        help="Maximum accepted DLT frame size in bytes",
    )
    parser.add_argument("--strict", action="store_true", help="Exit on parser/frame errors")
    parser.add_argument("--reconnect", action="store_true", help="Reconnect after socket loss")
    parser.add_argument(
        "--reconnect-interval",
        type=positive_float_arg,
        default=DEFAULT_RECONNECT_INTERVAL,
        help="Delay between reconnect attempts in seconds",
    )
    parser.add_argument(
        "--max-retries",
        type=non_negative_int_arg,
        default=None,
        help="Maximum reconnect attempts; omit for unlimited retries",
    )
    parser.add_argument("--ecu", action="append", default=None, help="Filter by ECU ID")
    parser.add_argument("--apid", action="append", default=None, help="Filter by APID")
    parser.add_argument("--ctid", action="append", default=None, help="Filter by CTID")
    parser.add_argument("--level", action="append", default=None, help="Filter by log level name or number")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verbose-only", action="store_true", help="Print only verbose messages")
    mode.add_argument("--non-verbose-only", action="store_true", help="Print only non-verbose messages")
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = create_parser()
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    state = _RunState()
    stderr = sys.stderr
    stdout = sys.stdout
    client = _build_client(args)
    _attach_diagnostics(client, state, stderr)

    try:
        for message in client.messages():
            state.messages_seen += 1
            _write_line(stdout, message.text)
    except KeyboardInterrupt:
        return EXIT_SUCCESS
    except (DltConnectionError, DltParserError, DltFrameError, DltError, OSError) as exc:
        if not state.reported_error:
            _print_expected_error(exc, stderr)
        return EXIT_RUNTIME_ERROR
    finally:
        client.close()

    if state.reported_error:
        return EXIT_RUNTIME_ERROR
    if state.messages_seen == 0 and state.disconnect_error is not None and not _has_filters(args):
        _write_line(stderr, f"disconnect: {state.disconnect_error}")
        return EXIT_RUNTIME_ERROR
    return EXIT_SUCCESS


def _build_client(args: argparse.Namespace) -> DltClient:
    return DltClient(
        host=args.host,
        port=args.port,
        timeout=args.timeout,
        auto_reconnect=args.reconnect,
        reconnect_interval=args.reconnect_interval,
        max_retries=args.max_retries,
        strict=args.strict,
        max_frame_size=args.max_frame_size,
        filters=_build_filters(args),
    )


def _build_filters(args: argparse.Namespace) -> dict[str, object] | None:
    filters: dict[str, object] = {}
    if args.ecu:
        filters["ecu"] = args.ecu
    if args.apid:
        filters["apid"] = args.apid
    if args.ctid:
        filters["ctid"] = args.ctid
    if args.level:
        filters["level"] = [_level_filter_value(level) for level in args.level]
    if args.verbose_only:
        filters["verbose_only"] = True
    if args.non_verbose_only:
        filters["non_verbose_only"] = True
    return filters or None


def _has_filters(args: argparse.Namespace) -> bool:
    return bool(args.ecu or args.apid or args.ctid or args.level or args.verbose_only or args.non_verbose_only)


def _level_filter_value(value: str) -> str | int:
    return int(value, 10) if value.isdigit() else value.upper()


def _attach_diagnostics(client: DltClient, state: _RunState, stderr: TextIO) -> None:
    def on_error(error: BaseException) -> None:
        state.reported_error = True
        _print_expected_error(error, stderr)

    def on_disconnect(error: BaseException | None) -> None:
        state.disconnect_error = error
        if isinstance(error, DltFrameError):
            state.reported_error = True
            _write_line(stderr, f"parser error: {error}")

    def on_reconnect_attempt(attempt: int) -> None:
        _write_line(stderr, f"reconnect attempt {attempt}")

    client.on_error(on_error)
    client.on_disconnect(on_disconnect)
    client.on_reconnect_attempt(on_reconnect_attempt)


def _print_expected_error(error: BaseException, stderr: TextIO) -> None:
    if isinstance(error, DltConnectionError):
        _write_line(stderr, f"connect error: {error}")
    elif isinstance(error, DltParserError):
        _write_line(stderr, f"parser error: {error}")
    else:
        _write_line(stderr, f"runtime error: {error}")


def _write_line(stream: TextIO, text: str) -> None:
    stream.write(f"{text}\n")
    stream.flush()
