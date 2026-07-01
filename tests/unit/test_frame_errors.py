from __future__ import annotations

import pytest

from py_dlt_client.constants import DEFAULT_MAX_FRAME_SIZE, HTYP_MSBF, HTYP_VERSION_1
from py_dlt_client.exceptions import DltFrameError
from py_dlt_client.frame_reader import DltFrameBuffer
from py_dlt_client.headers import parse_standard_header


def test_rejects_too_short_standard_header():
    with pytest.raises(DltFrameError):
        parse_standard_header(b"\x20\x01")


def test_rejects_length_smaller_than_header():
    frame = bytes([HTYP_VERSION_1 | HTYP_MSBF, 1, 0, 2])

    with pytest.raises(DltFrameError):
        parse_standard_header(frame)


def test_rejects_truncated_declared_frame(frames):
    frame = frames.sample_verbose_frame()

    with pytest.raises(DltFrameError):
        parse_standard_header(frame[:-1])


def test_rejects_oversized_frame_in_buffer(frames):
    frame = frames.build_frame(b"ok").frame
    reader = DltFrameBuffer(max_frame_size=len(frame) - 1)
    reader.feed(frame)

    with pytest.raises(DltFrameError):
        reader.pop_frame()


def test_rejects_declared_length_larger_than_configured_limit(frames):
    frame = frames.build_frame(b"payload").frame

    with pytest.raises(DltFrameError):
        parse_standard_header(frame, max_frame_size=len(frame) - 1)
