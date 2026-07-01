from __future__ import annotations

import pytest

import py_dlt_client
from py_dlt_client import DltClient, DltMessage


def test_public_exports_available():
    assert py_dlt_client.DltClient is DltClient
    assert py_dlt_client.DltMessage is DltMessage
    assert callable(py_dlt_client.format_message)


def test_constructor_validation():
    with pytest.raises(ValueError):
        DltClient(host="")
    with pytest.raises(ValueError):
        DltClient(host="x", port=0)
    with pytest.raises(ValueError):
        DltClient(host="x", timeout=0)
    with pytest.raises(ValueError):
        DltClient(host="x", reconnect_interval=0)


def test_callback_registration_returns_client():
    client = DltClient(host="127.0.0.1")

    assert client.on_message(lambda msg: None) is client
    assert client.on_connect(lambda: None) is client
    assert client.on_disconnect(lambda err: None) is client
    assert client.on_reconnect_attempt(lambda count: None) is client
    assert client.on_error(lambda err: None) is client
