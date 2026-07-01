from __future__ import annotations

import pytest

from py_dlt_client.client import DltClient
from py_dlt_client.filters import matches_filter, normalize_filter


def test_filters_by_apid_ctid_level_and_verbose(frames):
    message = DltClient(host="127.0.0.1").parse_frame(frames.sample_verbose_frame())

    assert matches_filter(message, normalize_filter({"apid": ["TEL"], "ctid": ["CRSH"], "level": ["INFO"]}))
    assert not matches_filter(message, normalize_filter({"apid": ["SYS"]}))
    assert matches_filter(message, normalize_filter({"verbose_only": True}))
    assert not matches_filter(message, normalize_filter({"non_verbose_only": True}))


def test_rejects_conflicting_verbose_filters():
    with pytest.raises(ValueError):
        normalize_filter({"verbose_only": True, "non_verbose_only": True})
