import pytest

from services.normalizer_service import normalizar_datos_aemet
from services.alert_service import AlertService


def test_normalizer_handles_ip_rain():
    """Verifica que la lluvia inapreciable 'Ip' se convierta en 0.0."""

    raw_data = {
        "fint": "2023-10-27T10:00:00",
        "prec": "Ip",
        "ta": "20",
        "hr": "50",
        "vv": "10"
    }

    normalized = normalizar_datos_aemet(raw_data)

    assert normalized["lluvia"] == 0.0
    assert isinstance(normalized["lluvia"], float)


def test_alert_service_returns_list():
    """Verifica que evaluar_alertas devuelve una lista."""

    service = AlertService()

    data = {
        "temperatura": 20.0,
        "viento": 10.0,
        "lluvia": 0.0,
        "humedad": 50
    }

    alertas = service.evaluar_alertas(data)

    assert isinstance(alertas, list)


def test_alert_service_no_alerts_with_normal_weather():
    """Verifica que con datos normales no se generan alertas."""

    service = AlertService()

    data = {
        "temperatura": 20.0,
        "viento": 10.0,
        "lluvia": 0.0,
        "humedad": 50
    }

    alertas = service.evaluar_alertas(data)

    assert alertas == []