"""Pure Python DLT V1 TCP receiver/parser for Windows."""

from .constants import DEFAULT_PORT
from .exceptions import (
    DltConnectionError,
    DltError,
    DltFrameError,
    DltParserError,
    DltUnsupportedTypeError,
)
from .models import (
    ClientEvent,
    DltArgument,
    DltClientConfig,
    DltErrorInfo,
    DltExtendedHeader,
    DltFilter,
    DltHeader,
    DltMessage,
)

try:
    from .client import DltClient
except ImportError:  # pragma: no cover - available after implementation tasks
    DltClient = None  # type: ignore[assignment]

try:
    from .formatter import format_message
except ImportError:  # pragma: no cover - available after implementation tasks
    format_message = None  # type: ignore[assignment]

__all__ = [
    "DEFAULT_PORT",
    "ClientEvent",
    "DltArgument",
    "DltClient",
    "DltClientConfig",
    "DltConnectionError",
    "DltError",
    "DltErrorInfo",
    "DltExtendedHeader",
    "DltFilter",
    "DltFrameError",
    "DltHeader",
    "DltMessage",
    "DltParserError",
    "DltUnsupportedTypeError",
    "format_message",
]
