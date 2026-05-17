import pytest

from controllers.compare_controller import (
    calculate_difference,
    get_discrepancy_details,
    has_discrepancy,
    compare_latest_records,
)


# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture
def manual_record():
    """
    Registro manual simulado, como si viniera del JSON.
    """

    return {
        "id": "manual_1",
        "municipio": "Madrid",
        "fecha": "22/04/2026",
        "fuente": "manual",
        "estacion_id": "3195",
        "temperatura": 20.0,
        "humedad": 60,
        "viento": 10.0,
        "lluvia": 0.0,
    }


@pytest.fixture
def api_record():
    """
    Registro API simulado, como si viniera normalizado desde AEMET.
    """

    return {
        "id": "api_1",
        "municipio": "Madrid",
        "fecha": "2026-04-22 12:30:00",
        "fuente": "api_aemet",
        "estacion": "Madrid",
        "temperatura": 21.0,
        "humedad": 58,
        "viento": 12.0,
        "lluvia": 0.0,
    }


# =====================================================
# TESTS calculate_difference()
# =====================================================

def test_calculate_difference_with_numbers():
    """
    Comprueba que calcula correctamente la diferencia entre dos números.
    """

    assert calculate_difference(20, 23) == 3.0
    assert calculate_difference(10.5, 8.0) == 2.5


def test_calculate_difference_with_none():
    """
    Comprueba que si recibe None lo trata como 0.0.
    """

    assert calculate_difference(None, 5) == 5.0
    assert calculate_difference(5, None) == 5.0


def test_calculate_difference_with_invalid_values():
    """
    Comprueba que si recibe valores no convertibles devuelve 0.0.
    """

    assert calculate_difference("hola", 5) == 0.0
    assert calculate_difference(5, "adios") == 0.0


# =====================================================
# TESTS has_discrepancy()
# =====================================================

def test_has_discrepancy_false():
    """
    Comprueba que no hay discrepancia si las diferencias están dentro
    de los límites aceptados.
    """

    differences = {
        "temperatura": 2,
        "humedad": 5,
        "viento": 8,
        "lluvia": 3,
    }

    assert has_discrepancy(differences) is False


def test_has_discrepancy_true_temperature():
    """
    Comprueba que hay discrepancia si la temperatura supera el límite.
    """

    differences = {
        "temperatura": 4,
        "humedad": 5,
        "viento": 8,
        "lluvia": 3,
    }

    assert has_discrepancy(differences) is True


def test_has_discrepancy_true_humidity():
    """
    Comprueba que hay discrepancia si la humedad supera el límite.
    """

    differences = {
        "temperatura": 2,
        "humedad": 11,
        "viento": 8,
        "lluvia": 3,
    }

    assert has_discrepancy(differences) is True


def test_has_discrepancy_true_wind():
    """
    Comprueba que hay discrepancia si el viento supera el límite.
    """

    differences = {
        "temperatura": 2,
        "humedad": 5,
        "viento": 11,
        "lluvia": 3,
    }

    assert has_discrepancy(differences) is True


def test_has_discrepancy_true_rain():
    """
    Comprueba que hay discrepancia si la lluvia supera el límite.
    """

    differences = {
        "temperatura": 2,
        "humedad": 5,
        "viento": 8,
        "lluvia": 6,
    }

    assert has_discrepancy(differences) is True


def test_get_discrepancy_details_marks_each_field():
    differences = {
        "temperatura": 4,
        "humedad": 8,
        "viento": 12,
        "lluvia": 0,
    }

    assert get_discrepancy_details(differences) == {
        "temperatura": True,
        "humedad": False,
        "viento": True,
        "lluvia": False,
    }


# =====================================================
# TESTS compare_latest_records()
# =====================================================

def test_compare_latest_records_success(monkeypatch, manual_record, api_record):
    """
    Comprueba que compare_latest_records funciona correctamente
    cuando existen tanto el registro manual como el registro API.
    """

    # Simulamos que filter_records encuentra un registro manual en el JSON.
    def fake_filter_records(municipio, fecha):
        return [manual_record]

    # Simulamos el servicio de AEMET.
    # Tiene que tener el método _obtener_datos_crudos()
    # porque eso es lo que usa compare_latest_records().
    class FakeWeatherAPIService:
        class FakeAemetClient:
            def obtener_observaciones_actuales(self):
                return [
                    {
                        "idema": manual_record["estacion_id"],
                        "ubi": "Madrid",
                        "fint": "2026-04-22T12:30:00",
                        "ta": "21",
                        "hr": "58",
                        "vv": "12",
                        "prec": "0",
                    }
                ]

        def __init__(self):
            self.aemet_client = self.FakeAemetClient()

    # Simulamos el normalizador para que devuelva nuestro api_record.
    def fake_normalizar_datos_aemet(raw_data):
        return api_record.copy()

    monkeypatch.setattr(
        "controllers.compare_controller.filter_records",
        fake_filter_records,
    )

    monkeypatch.setattr(
        "controllers.compare_controller.WeatherAPIService",
        FakeWeatherAPIService,
    )

    monkeypatch.setattr(
        "controllers.compare_controller.normalizar_datos_aemet",
        fake_normalizar_datos_aemet,
    )

    resultado = compare_latest_records("Madrid", "2026-04-22")

    assert resultado["success"] is True
    assert resultado["municipio"] == "Madrid"
    assert resultado["fecha"] == "22/04/2026"
    assert resultado["manual"] == manual_record
    assert resultado["api"]["fuente"] == "AEMET (Oficial)"
    assert "diferencias" in resultado
    assert "discrepancias" in resultado
    assert "hay_discrepancia" in resultado


def test_compare_latest_records_no_manual(monkeypatch):
    """
    Comprueba que compare_latest_records devuelve error
    si no existe registro manual.
    """

    # Simulamos que filter_records no encuentra registros.
    def fake_filter_records(municipio, fecha):
        return []

    monkeypatch.setattr(
        "controllers.compare_controller.filter_records",
        fake_filter_records,
    )

    resultado = compare_latest_records("Madrid", "2026-04-22")

    assert resultado["success"] is False
    assert "No hay datos manuales" in resultado["message"]


def test_compare_latest_records_no_api(monkeypatch, manual_record):
    """
    Comprueba que compare_latest_records devuelve error
    si no existe registro API AEMET para la estación manual.
    """

    # Simulamos que sí existe registro manual.
    def fake_filter_records(municipio, fecha):
        return [manual_record]

    # Simulamos que AEMET no devuelve ninguna observación.
    class FakeWeatherAPIService:
        class FakeAemetClient:
            def obtener_observaciones_actuales(self):
                return []

        class FakeMunicipalityService:
            def obtener_municipio_por_nombre(self, municipio):
                return None

        def __init__(self):
            self.aemet_client = self.FakeAemetClient()
            self.municipality_service = self.FakeMunicipalityService()

    monkeypatch.setattr(
        "controllers.compare_controller.filter_records",
        fake_filter_records,
    )

    monkeypatch.setattr(
        "controllers.compare_controller.WeatherAPIService",
        FakeWeatherAPIService,
    )

    resultado = compare_latest_records("Madrid", "2026-04-22")

    assert resultado["success"] is False
    assert "AEMET" in resultado["message"]


def test_compare_latest_records_usa_estacion_cercana_si_falta_estacion(
    monkeypatch,
    manual_record,
    api_record,
):
    """
    Comprueba que la comparativa usa coordenadas de municipio como plan B
    si AEMET no devuelve la estacion manual exacta.
    """

    def fake_filter_records(municipio, fecha):
        return [manual_record]

    class FakeWeatherAPIService:
        class FakeAemetClient:
            def obtener_observaciones_actuales(self):
                return []

        class FakeMunicipalityService:
            def obtener_municipio_por_nombre(self, municipio):
                return {
                    "nombre": municipio,
                    "lat": 40.4168,
                    "lon": -3.7038,
                }

        def __init__(self):
            self.aemet_client = self.FakeAemetClient()
            self.municipality_service = self.FakeMunicipalityService()

        def obtener_clima_por_coordenadas(self, lat, lon):
            return {
                "idema": "3195",
                "ubi": "Madrid",
                "fint": "2026-04-22T12:30:00",
                "ta": "21",
                "hr": "58",
                "vv": "12",
                "prec": "0",
            }

    def fake_normalizar_datos_aemet(raw_data):
        return api_record.copy()

    monkeypatch.setattr(
        "controllers.compare_controller.filter_records",
        fake_filter_records,
    )
    monkeypatch.setattr(
        "controllers.compare_controller.WeatherAPIService",
        FakeWeatherAPIService,
    )
    monkeypatch.setattr(
        "controllers.compare_controller.normalizar_datos_aemet",
        fake_normalizar_datos_aemet,
    )

    resultado = compare_latest_records("Madrid", "2026-04-22")

    assert resultado["success"] is True
    assert resultado["api"]["fuente"] == "AEMET (Oficial)"


def test_compare_latest_records_api_exception(monkeypatch, manual_record):
    """
    Comprueba que compare_latest_records devuelve error
    si falla la conexión o la consulta a la API.
    """

    # Simulamos que sí existe registro manual.
    def fake_filter_records(municipio, fecha):
        return [manual_record]

    # Simulamos que el servicio de AEMET falla.
    class FakeWeatherAPIService:
        class FakeAemetClient:
            def obtener_observaciones_actuales(self):
                raise Exception("Error simulado de API")

        def __init__(self):
            self.aemet_client = self.FakeAemetClient()

    monkeypatch.setattr(
        "controllers.compare_controller.filter_records",
        fake_filter_records,
    )

    monkeypatch.setattr(
        "controllers.compare_controller.WeatherAPIService",
        FakeWeatherAPIService,
    )

    resultado = compare_latest_records("Madrid", "2026-04-22")

    assert resultado["success"] is False
    assert "API" in resultado["message"] or "AEMET" in resultado["message"]

    #para probar py -m pytest tests/test_compare_controller.py tests/test_json_repository.py -v
