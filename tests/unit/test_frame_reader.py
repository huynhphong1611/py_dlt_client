from __future__ import annotations

from py_dlt_client.frame_reader import DltFrameBuffer


def test_frame_buffer_waits_for_complete_fragmented_frame(frames):
    frame = frames.sample_verbose_frame()
    reader = DltFrameBuffer()

    reader.feed(frame[:5])
    assert reader.pop_frame() is None

    reader.feed(frame[5:])
    assert reader.pop_frame() == frame
    assert reader.pop_frame() is None


def test_frame_buffer_emits_multiple_coalesced_frames(frames):
    first = frames.sample_verbose_frame()
    second = frames.sample_non_verbose_frame()
    reader = DltFrameBuffer()

    reader.feed(first + second)

    assert reader.pop_frame() == first
    assert reader.pop_frame() == second
    assert reader.pop_frame() is None
