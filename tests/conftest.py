from __future__ import annotations

import pytest

from tests.fixtures import dlt_frames


@pytest.fixture
def frames():
    return dlt_frames


def assert_message_identity(message, *, ecu="ECU1", apid="TEL", ctid="CRSH") -> None:
    assert message.ecu == ecu
    assert message.apid == apid
    assert message.ctid == ctid
    assert message.raw_frame
    assert message.payload_hex == message.raw_payload.hex()
