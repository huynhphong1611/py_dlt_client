"""Typed exceptions for DLT client failures."""

from __future__ import annotations


class DltError(Exception):
    """Base class for all py_dlt_client errors."""


class DltConnectionError(DltError):
    """Raised when socket connection or lifecycle handling fails."""


class DltParserError(DltError):
    """Raised when DLT bytes cannot be parsed according to the supported subset."""


class DltUnsupportedTypeError(DltParserError):
    """Raised in strict mode for unsupported verbose payload argument types."""


class DltFrameError(DltParserError):
    """Raised for invalid, truncated, or oversized DLT frames."""
