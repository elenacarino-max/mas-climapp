from services.municipality_service import MunicipalityService


class FakeAemetClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def obtener_municipios(self):
        self.calls += 1
        return self.responses.pop(0)


def test_obtener_municipios_no_cachea_respuesta_invalida():
    client = FakeAemetClient([None, [{"id": "id28079", "nombre": "Madrid"}]])
    service = MunicipalityService(aemet_client=client)

    assert service._obtener_municipios() == []
    assert service._municipios_cache is None

    assert service._obtener_municipios() == [{"id": "id28079", "nombre": "Madrid"}]
    assert client.calls == 2


def test_obtener_municipios_no_cachea_lista_vacia():
    client = FakeAemetClient([[], [{"id": "id28079", "nombre": "Madrid"}]])
    service = MunicipalityService(aemet_client=client)

    assert service._obtener_municipios() == []
    assert service._municipios_cache is None

    assert service._obtener_municipios() == [{"id": "id28079", "nombre": "Madrid"}]
    assert client.calls == 2


def test_obtener_municipios_cachea_lista_valida():
    municipios = [{"id": "id28079", "nombre": "Madrid"}]
    client = FakeAemetClient([municipios])
    service = MunicipalityService(aemet_client=client)

    assert service._obtener_municipios() == municipios
    assert service._obtener_municipios() == municipios
    assert client.calls == 1
