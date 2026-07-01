from __future__ import annotations

import pytest

from py_dlt_client.client import DltClient
from py_dlt_client.exceptions import DltUnsupportedTypeError


def test_strict_mode_raises_unsupported_verbose_type(frames):
    frame = frames.build_frame(frames.verbose_payload(frames.arg_unsupported()), noar=1).frame

    with pytest.raises(DltUnsupportedTypeError):
        DltClient(host="127.0.0.1", strict=True).parse_frame(frame)


def test_non_strict_mode_preserves_unsupported_verbose_type(frames):
    frame = frames.build_frame(frames.verbose_payload(frames.arg_unsupported()), noar=1).frame

    message = DltClient(host="127.0.0.1", strict=False).parse_frame(frame)

    assert message.args[0].supported is False
    assert message.text.endswith(message.args[0].display)
