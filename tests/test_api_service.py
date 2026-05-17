import pytest

# Importamos la clase que queremos probar.
# Esta clase está en services/weather_api_service.py
from services.weather_api_service import WeatherAPIService


OBSERVACIONES_FAKE = [
    {
        "ubi": "Madrid-Retiro",
        "lat": "40.4168",
        "lon": "-3.7038",
        "ta": "22.5",
    },
    {
        "ubi": "Barcelona",
        "lat": "41.3874",
        "lon": "2.1686",
        "ta": "20.1",
    },
]


class FakeAemetClient:
    """
    Cliente AEMET falso para probar WeatherAPIService sin llamadas reales.
    """

    def __init__(self, observaciones=None):
        self.api_key = "fake_api_key"
        self.base_url = "https://opendata.aemet.es/opendata"
        self.observaciones = (
            OBSERVACIONES_FAKE if observaciones is None else observaciones
        )

    def obtener_observaciones_actuales(self):
        return self.observaciones

    def obtener_prediccion_municipio_diaria(self, codigo_municipio):
        return None

    def obtener_prediccion_municipio_horaria(self, codigo_municipio):
        return None

    def obtener_municipios(self):
        return [
            {
                "id": "id28079",
                "nombre": "Madrid",
                "provincia": "Madrid",
                "lat": "40.4168",
                "lon": "-3.7038",
            }
        ]


# =====================================================
# FIXTURE: servicio API preparado para tests
# =====================================================

@pytest.fixture
def api_service(monkeypatch):
    """
    Esta fixture prepara una instancia de WeatherAPIService
    sin usar datos reales.

    Inyecta un cliente AEMET falso para evitar llamadas reales a internet.
    """

    return WeatherAPIService(aemet_client=FakeAemetClient())


# =====================================================
# TEST 1: inicialización correcta
# =====================================================

def test_weather_api_service_init(api_service):
    """
    Comprueba que WeatherAPIService se inicializa correctamente
    cuando existe la variable AEMET_API_KEY.
    """

    assert api_service.aemet_client.api_key == "fake_api_key"
    assert api_service.aemet_client.base_url == "https://opendata.aemet.es/opendata"


# =====================================================
# TEST 2: error si no hay API KEY
# =====================================================

def test_weather_api_service_no_api_key(monkeypatch):
    """
    Comprueba que el servicio lanza ValueError
    si no existe AEMET_API_KEY.

    Esto es importante porque sin API key no se puede consultar AEMET.
    """

    # Eliminamos la variable de entorno si existe.
    monkeypatch.delenv("AEMET_API_KEY", raising=False)

    # Esperamos que al crear el servicio se lance ValueError.
    with pytest.raises(ValueError):
        WeatherAPIService()


# =====================================================
# TEST 3: obtener observaciones correctamente
# =====================================================

def test_obtener_observaciones_actuales_success(api_service):
    """
    Comprueba que el cliente AEMET inyectado devuelve una lista
    de observaciones cuando las respuestas simuladas son correctas.
    """

    result = api_service.aemet_client.obtener_observaciones_actuales()

    # Debe devolver una lista.
    assert isinstance(result, list)

    # En FakeSession hemos preparado 2 observaciones.
    assert len(result) == 2

    # Comprobamos que la primera observación es Madrid-Retiro.
    assert result[0]["ubi"] == "Madrid-Retiro"


# =====================================================
# TEST 4: sin observaciones
# =====================================================

def test_obtener_observaciones_actuales_sin_datos():
    """
    Comprueba que si el cliente no devuelve observaciones,
    el servicio recibe una lista vacía.
    """

    service = WeatherAPIService(aemet_client=FakeAemetClient(observaciones=[]))
    result = service.aemet_client.obtener_observaciones_actuales()

    assert result == []


# =====================================================
# TEST 5: servicio sin observaciones
# =====================================================

def test_obtener_clima_por_coordenadas_devuelve_none_sin_observaciones():
    """
    Comprueba que si AEMET no trae observaciones,
    el servicio no puede calcular clima cercano.
    """

    service = WeatherAPIService(aemet_client=FakeAemetClient(observaciones=[]))
    result = service.obtener_clima_por_coordenadas(40.4168, -3.7038)

    assert result is None


# =====================================================
# TEST 6: estación más cercana por coordenadas
# =====================================================

def test_obtener_clima_por_coordenadas_devuelve_estacion_cercana(api_service):
    """
    Comprueba que obtener_clima_por_coordenadas()
    devuelve la estación más cercana a las coordenadas dadas.

    Usamos las coordenadas de Madrid, por lo que esperamos Madrid-Retiro.
    """

    result = api_service.obtener_clima_por_coordenadas(40.4168, -3.7038)

    assert result is not None
    assert result["ubi"] == "Madrid-Retiro"


# =====================================================
# TEST 7: sin observaciones
# =====================================================

def test_obtener_clima_por_coordenadas_sin_observaciones(monkeypatch, api_service):
    """
    Comprueba que si no hay observaciones de AEMET,
    la función devuelve None.
    """

    api_service.aemet_client.observaciones = []

    result = api_service.obtener_clima_por_coordenadas(40.4168, -3.7038)

    assert result is None


# =====================================================
# TEST 8: ignorar datos corruptos
# =====================================================

def test_obtener_clima_por_coordenadas_ignora_datos_corruptos(monkeypatch, api_service):
    """
    Comprueba que el servicio ignora observaciones con coordenadas corruptas.

    Si una estación trae latitud o longitud inválida, se salta.
    """

    observaciones = [
        {
            "ubi": "Estación corrupta",
            "lat": "no_valido",
            "lon": "-3.7"
        },
        {
            "ubi": "Madrid-Retiro",
            "lat": "40.4168",
            "lon": "-3.7038"
        }
    ]

    api_service.aemet_client.observaciones = observaciones

    result = api_service.obtener_clima_por_coordenadas(40.4168, -3.7038)

    assert result is not None
    assert result["ubi"] == "Madrid-Retiro"


