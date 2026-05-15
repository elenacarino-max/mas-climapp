import logging

import pytest
import requests

from services.aemet_client import AemetClient


class FakeResponse:
    def __init__(self, json_data=None, json_error=None):
        self.json_data = json_data
        self.json_error = json_error

    def raise_for_status(self):
        return None

    def json(self):
        if self.json_error:
            raise self.json_error

        return self.json_data


@pytest.fixture
def aemet_client(monkeypatch):
    monkeypatch.setenv("AEMET_API_KEY", "fake_api_key")
    return AemetClient()


def test_get_payload_logs_metadata_request_errors(aemet_client, caplog):
    class FakeSession:
        def get(self, *args, **kwargs):
            raise requests.exceptions.ConnectionError("sin conexión")

    aemet_client.session = FakeSession()

    with caplog.at_level(logging.ERROR):
        result = aemet_client._get_payload_from_endpoint("/fake")

    assert result is None
    assert "metadatos" in caplog.text
    assert "sin conexión" in caplog.text


def test_get_payload_logs_unexpected_metadata_format(aemet_client, caplog):
    class FakeSession:
        def get(self, *args, **kwargs):
            return FakeResponse([])

    aemet_client.session = FakeSession()

    with caplog.at_level(logging.ERROR):
        result = aemet_client._get_payload_from_endpoint("/fake")

    assert result is None
    assert "formato inesperado" in caplog.text
    assert "list" in caplog.text


def test_get_payload_logs_payload_json_errors(aemet_client, caplog):
    class FakeSession:
        def __init__(self):
            self.calls = 0

        def get(self, *args, **kwargs):
            self.calls += 1

            if self.calls == 1:
                return FakeResponse({"datos": "https://fake-url-aemet/datos"})

            return FakeResponse(json_error=ValueError("JSON roto"))

    aemet_client.session = FakeSession()

    with caplog.at_level(logging.ERROR):
        result = aemet_client._get_payload_from_endpoint("/fake")

    assert result is None
    assert "JSON de datos inválido" in caplog.text
    assert "https://fake-url-aemet/datos" in caplog.text
