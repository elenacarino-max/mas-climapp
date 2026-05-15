## TEST DE LA API DE ZONAS
## Test automátiocos para verificar los endpoints de la API de zonas, que es la que se encarga de devolver las zonas climáticas de una ciudad dada.

import pytest
from uuid import uuid4
# Cliente HTTP de testing FastAPI
from fastapi.testclient import TestClient
# Importamos la aplicación FastAPI
from mas_climapp.main import app

# Crear un cliente de pruebas para la aplicación FastAPI
# Simula peticiones HTTP reales contra la API. / Permite probar los endpoints sin necesidad de ejecutar el servidor.
# Ejecuta client.get() / .post() / .patch() / .delete()
client = TestClient(app)

# Crear datos de prueba para una zona climática
zona_data = {
    "municipio": "Madrid",
    "cod_ine": f"28079{uuid4().hex[:6]}",
    "id_estacion": "3195",
    "estacion_referencia": "Retiro"
}


def crear_o_obtener_zona():
    response = client.post("/zonas/", json=zona_data)

    if response.status_code == 409:
        response = client.get(f"/zonas/cod-ine/{zona_data['cod_ine']}")

    assert response.status_code in (200, 201)
    return response.json()


####------------------------------------------ C- CREATE - POST /zonas/ ---------------------------------------------------------------------
# Verificar que una zona climática se pueda crear correctamente a través del endpoint POST /zonas/. 
# Se envía una solicitud con los datos de la zona y se verifica que la respuesta tenga un código de estado 201 (Creado) y que los datos de la zona creada coincidan con los datos enviados.

def test_crear_zona():
    ## ACT : Enviar (en JSON) una solicitud POST para crear una nueva zona climática con los datos de prueba
    response = client.post("/zonas/", json=zona_data)

    ## ASSERT : 
    # Verificar que la respuesta tenga un código de estado 201 (Creado)
    assert response.status_code == 201
    # Convertir la respuesta JSON a un diccionario de Python
    data = response.json()
    
    # Verificar que la respuesta contenga los datos de la zona creada y que coincidan con los datos enviados
    assert data["municipio"] == zona_data["municipio"]
    assert data["cod_ine"] == zona_data["cod_ine"]
    assert data["id_estacion"] == zona_data["id_estacion"]
    assert data["estacion_referencia"] == zona_data["estacion_referencia"]

    # Verificar que existe ID generado por BD y es numérico
    assert isinstance(data["id"], int)

# Crear zona duplicada -> Debería devolver un error 409 (Conflict) porque el código INE ya existe en la base de datos.
# Verificar restrirción de unicidad del código INE para evitar zonas duplicadas.

def test_crear_zona_duplicada():

    # Crear primera zona
    client.post(
        "/zonas/",
        json=zona_data
    )
    # ACT : Intentar crear una segunda zona con el mismo código INE (zona duplicada)
    response = client.post(
        "/zonas/",
        json=zona_data
    )

    # ASSERT : 
    # Verificar que la respuesta tenga un código de estado 409 (Conflict) debido a la restricción de unicidad del código INE
    assert response.status_code == 409

    # Verificar que la respuesta contenga un mensaje de error indicando que el código INE ya existe
    assert "Ya existe una zona" in response.json()["detail"]

# Crear zona inválida -> Debería devolver un error 422 (Unprocessable Entity) porque faltan campos obligatorios o los datos no cumplen con el formato esperado.
# Verificar validación automática de Pydantic. 

def test_crear_zona_invalida():

    # ACT : Intentar crear zona con datos incompletos (falta el campo "municipio")
    response = client.post(
        "/zonas/",
        json={
            "cod_ine": "28079",
            "id_estacion": "3195",
            "estacion_referencia": "Retiro"
        }
    )

    # ASSERT :
    # Verificar que la respuesta tenga un código de estado 422 (Unprocessable Entity) debido a la falta de campos obligatorios
    assert response.status_code == 422
    # Verificar que la respuesta contenga un mensaje de error indicando que el campo "municipio" es obligatorio
    assert "municipio" in str (response.json()["detail"])


####------------------------------------------ R - READ - GET /zonas/ ---------------------------------------------------------------------
    # Verificar que se puedan obtener todas las zonas climáticas a través del endpoint GET /zonas/

    # Test listar zonas -> Debería devolver una lista de zonas climáticas que incluya la zona creada en el test anterior. 
    # Verificar que la respuesta tenga un código de estado 200 (OK) y que los datos de la zona creada estén presentes en la lista de zonas devuelta por la API.

def test_obtener_zonas():

    # ARRANGE: Crear una zona de prueba para asegurarnos de que hay al menos una zona en la base de datos
    client.post(
        "/zonas/",
        json=zona_data
    )

    # ACT : Enviar una solicitud GET para obtener todas las zonas climáticas
    response = client.get("/zonas/")

    # ASSERT :
    # Verificar que la respuesta tenga un código de estado 200 (OK)
    assert response.status_code == 200
    # Convertir la respuesta JSON a una lista de diccionarios de Python
    data = response.json()
    
    # Verificar que la respuesta contenga una lista de zonas climáticas y que al menos una zona coincida con los datos de prueba
    assert isinstance(data, list)
    assert any(zona["municipio"] == zona_data["municipio"] for zona in data)

    # -----
    # Test obtener zona por ID -> Debería devolver los datos de la zona climática correspondiente al ID especificado.
    # Verificar que la respuesta tenga un código de estado 200 (OK) y que los datos de la zona devuelta coincidan con los datos de la zona creada en el test anterior

def test_obtener_zona_por_id():

    # ARRANGE: Crear una zona de prueba para obtener su ID
    zona_id = crear_o_obtener_zona()["id"]

    # ACT : Enviar una solicitud GET para obtener la zona climática por su ID
    response = client.get(f"/zonas/{zona_id}")

    # ASSERT :
    # Verificar que la respuesta tenga un código de estado 200 (OK)
    assert response.status_code == 200
    # Convertir la respuesta JSON a un diccionario de Python
    data = response.json()
    
    # Verificar que los datos de la zona devuelta coincidan con los datos de la zona creada en el test anterior
    assert data["id"] == zona_id
    assert data["municipio"] == zona_data["municipio"]
    assert data["cod_ine"] == zona_data["cod_ine"]
    assert data["id_estacion"] == zona_data["id_estacion"]
    assert data["estacion_referencia"] == zona_data["estacion_referencia"]

    # -----
    # Test para obtener zona por código INE -> Debería devolver los datos de la zona climática correspondiente al código INE especificado.
    # Verificar que la respuesta tenga un código de estado 200 (OK) y que los datos de la zona devuelta coincidan con los datos de la zona creada en el test anterior

def test_obtener_zona_por_cod_ine():

    # ARRANGE: Crear una zona de prueba para obtener su código INE
    client.post(
        "/zonas/",
        json=zona_data
    )
    cod_ine = zona_data["cod_ine"]

    # ACT : Enviar una solicitud GET para obtener la zona climática por su código INE
    response = client.get(f"/zonas/cod-ine/{cod_ine}")

    # ASSERT :
    # Verificar que la respuesta tenga un código de estado 200 (OK)
    assert response.status_code == 200
    # Convertir la respuesta JSON a un diccionario de Python
    data = response.json()
    
    # Verificar que los datos de la zona devuelta coincidan con los datos de la zona creada en el test anterior
    assert data["municipio"] == zona_data["municipio"]
    assert data["cod_ine"] == cod_ine
    assert data["id_estacion"] == zona_data["id_estacion"]
    assert data["estacion_referencia"] == zona_data["estacion_referencia"]

    
    # -----
    #Test para zona inexistente por cod_ine -> Debería devolver un error 404 (Not Found) porque no existe ninguna zona climática con el código INE especificado.
    # Verificar que la respuesta tenga un código de estado 404 (Not Found) 
    # La respuesta tiene que contener un mensaje de error indicando que no se encontró ninguna zona climática con el cod_ine especificado

def test_obtener_zona_inexistente_por_cod_ine():

    # ACT : Enviar una solicitud GET para obtener una zona climática con un código INE que no existe en la base de datos
    response = client.get("/zonas/cod-ine/99999")

    # ASSERT :
    # Verificar que la respuesta tenga un código de estado 404 (Not Found)
    assert response.status_code == 404
    # Verificar que la respuesta contenga un mensaje de error indicando que no se encontró ninguna zona climática con el código INE especificado
    assert "No existe ninguna zona" in response.json()["detail"]

    #Test para ID de zona inexistente -> Debería devolver un error 404 (Not Found) porque no existe ninguna zona climática con el ID especificado.
    # La respuesta tiene que contener un mensaje de error indicando que no se encontró ninguna zona climática con el ID especificado
   
def test_obtener_zona_inexistente_por_id():

    # ACT : Enviar una solicitud GET para obtener una zona climática con un ID que no existe en la base de datos
    response = client.get("/zonas/99999")

    # ASSERT :
    # Verificar que la respuesta tenga un código de estado 404 (Not Found)
    assert response.status_code == 404
    # Verificar que la respuesta contenga un mensaje de error indicando que no se encontró ninguna zona climática con el ID especificado
    assert "No existe ninguna zona" in response.json()["detail"]

    ####------------------------------------------ U - UPDATE - PATCH /zonas/ ---------------------------------------------------------------------
    # Verificar que PATCH / zonas / {id} actualice correctamente una la zona climática.

    def test_actualizar_zona():

        # ARRANGE: Crear una zona de prueba para obtener su ID
        response_crear = client.post(
            "/zonas/",
            json=zona_data
        )
        zona_id = response_crear.json()["id"]

        # ACT : Enviar una solicitud PATCH para actualizar solo el campo "estacion_referencia" de la zona climática por su ID
        response = client.patch(
            f"/zonas/{zona_id}",
            json={
                "estacion_referencia": "Atocha"
            }
        )

        # ASSERT :
        # Verificar que la respuesta tenga un código de estado 200 (OK)
        assert response.status_code == 200
        # Convertir la respuesta JSON a un diccionario de Python
        data = response.json()
        
        # Verificar que el campo "estacion_referencia" se haya actualizado correctamente y que los demás campos no hayan cambiado
        assert data["id"] == zona_id
        assert data["municipio"] == zona_data["municipio"]
        assert data["cod_ine"] == zona_data["cod_ine"]
        assert data["id_estacion"] == zona_data["id_estacion"]
        assert data["estacion_referencia"] == "Atocha"

    # -----
    # Test para actualizar zona inexistente -> Verificar que la respuesta es un error 404 (Not Found) porque no existe ninguna zona climática con el ID especificado para actualizar. 
    def test_actualizar_zona_inexistente():

        # ACT : Enviar una solicitud PATCH para actualizar una zona climática con un ID que no existe en la base de datos
        response = client.patch(
            "/zonas/99999",
            json={
                "estacion_referencia": "Atocha"
            }
        )

        # ASSERT :
        # Verificar que la respuesta tenga un código de estado 404 (Not Found)
        assert response.status_code == 404
        # Verificar que la respuesta contenga un mensaje de error indicando que no se encontró ninguna zona climática con el ID especificado para actualizar
        assert "No existe ninguna zona" in response.json()["detail"]

    #-----
    # Test para actualizar zona con código INE duplicado -> Verificar que la respuesta es un error 409 (Conflict) porque el código INE actualizado ya existe en otra zona climática de la base de datos.
    def test_actualizar_zona_cod_ine_duplicado():

        # ARRANGE: Crear dos zonas de prueba para obtener sus IDs y códigos INE
        response_crear_1 = client.post(
            "/zonas/",
            json=zona_data
        )
        zona_id_1 = response_crear_1.json()["id"]

        client.post(
            "/zonas/",
            json={
                "municipio": "Barcelona",
                "cod_ine": "08019",
                "id_estacion": "1234",
                "estacion_referencia": "Sants"
            }
        )
        cod_ine_2 = "08019"

        # ACT : Enviar una solicitud PATCH para actualizar el código INE de la primera zona al código INE de la segunda zona (código INE duplicado)
        response = client.patch(
            f"/zonas/{zona_id_1}",
            json={
                "cod_ine": cod_ine_2
            }
        )

        # ASSERT :
        # Verificar que la respuesta tenga un código de estado 409 (Conflict) debido a la restricción de unicidad del código INE
        assert response.status_code == 409
        # Verificar que la respuesta contenga un mensaje de error indicando que ya existe una zona climática con el código INE actualizado
        assert "Ya existe una zona" in response.json()["detail"]


    ####------------------------------------------ D - DELETE - DELETE /zonas/ ---------------------------------------------------------------------
    # Verificar que DELETE /zonas/{id} elimine correctamente una zona climática

    def test_eliminar_zona():

        # ARRANGE: Crear una zona de prueba para obtener su ID
        response_crear = client.post(
            "/zonas/",
            json=zona_data
        )
        zona_id = response_crear.json()["id"]

        # ACT : Enviar una solicitud DELETE para eliminar la zona climática por su ID
        response = client.delete(f"/zonas/{zona_id}")

        # ASSERT :
        # Verificar que la respuesta tenga un código de estado 200 (OK) indicando que la eliminación fue exitosa
        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Zona eliminada correctamente"
        assert data["zona_id"] == zona_id

        # Verificar que la zona climática ya no exista en la base de datos enviando una solicitud GET para obtener la zona por su ID
        response_get = client.get(f"/zonas/{zona_id}")
        assert response_get.status_code == 404

    #-----
    # Test para eliminar zona inexistente -> Verificar que la respuesta es un error 404 (Not Found) porque no existe ninguna zona climática con el ID especificado para eliminar.
    def test_eliminar_zona_inexistente():

        # ACT : Enviar una solicitud DELETE para eliminar una zona climática con un ID que no existe en la base de datos
        response = client.delete("/zonas/99999")

        # ASSERT :
        # Verificar que la respuesta tenga un código de estado 404 (Not Found)
        assert response.status_code == 404
        # Verificar que la respuesta contenga un mensaje de error indicando que no se encontró ninguna zona climática con el ID especificado para eliminar
        assert "No existe ninguna zona" in response.json()["detail"]


    #####------------------------------------------ VERIFICAR QUE LA API DEVUELVE JSON ---------------------------------------------------------------------

    def test_respuesta_tipo_json():

        #ACT : Enviar una solicitud GET para obtener todas las zonas climáticas
        response = client.get("/zonas/")
        # ASSERT : Verificar que la respuesta tiene formato JSON comprobando el encabezado "content-type" de la respuesta
        assert response.headers["content-type"].startswith(
        "application/json"
        )

    #####------------------------------------------ FIN DE TEST API ---------------------------------------------------------------------
