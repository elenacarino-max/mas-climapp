##TESTS DE LA API DE MEDICIONES CLIMATICAS
# Este archivo comprueba el funcionamiento completo del CRUD (Create, Read, Update, Delete) del endpoint /mediciones.

import pytest
from fastapi.testclient import TestClient
from mas_climapp.main import app

#Cliente de test -> TestClient permite simular peticiones HTTP sin arrancar el servidor real.

client = TestClient(app)

#DATOS DE PRUEBA
medicion_data = {
    "estacion_id": 1,
    "fecha_hora": "2024-06-01T12:00:00",
    "temperatura": 25.5,
    "humedad": 60.0,
    "presion": 1013.25
}

#####--------------------------------------------------------- C - CREATE - POST /mediciones/ ---------------------------------------------------------------------
# Verificar que se puede crear una medición con datos válidos y que se devuelve la información correcta, incluyendo el ID generado automáticamente.

def test_crear_medicion():
    # ARRANGE: Crear una zona para asociar la nueva medición, ya que la medición requiere un zona_id válido.
    response_zona = client.post("/zonas/",json=zona_data)

    zona_id = response_zona.json()["id"]

    nueva_medicion = {
        "zona_id": zona_id, 
        **medicion_data
    }

    # ACT: Enviar petición POST al endpoint /mediciones/ con los datos de la nueva medición.
    response = client.post("/mediciones/", json=nueva_medicion)

    # ASSERT: Verificar creación correcta de la medición
    # La respuesta tenga un código de estado 201 (Created) y que los datos devueltos coincidan con los enviados.
    assert response.status_code == 201
    data = response.json()

    assert data["zona_id"] == zona_id
    assert data["fecha_datos"] == medicion_data["fecha_datos"]
    assert data["temperatura"] == medicion_data["temperatura"]
    assert data["humedad"] == medicion_data["humedad"]
    assert data["viento"] == medicion_data["viento"]
    assert data["lluvia"] == medicion_data["lluvia"]

     # Verificar que existe ID generado automáticamente
    assert "id" in data

    #-----
    #Verificar que no es posible crear una medición con datos inválidos (por ejemplo, temperatura como string en lugar de número).

def test_crear_medicion_tipo_dato_invalido():

        # ARRANGE: Crear una zona para asociar la nueva medición, ya que la medición requiere un zona_id válido.
        response_zona = client.post("/zonas/",json=zona_data)

        zona_id = response_zona.json()["id"]

        nueva_medicion_invalida = {
            "zona_id": zona_id, 
            "fecha_datos": "2024-06-01T12:00:00",
            "temperatura": "no es un número",  # Valor inválido
            "humedad": 60.0,
            "viento": 5.0,
            "lluvia": 0.0
        }

        # ACT: Enviar petición POST al endpoint /mediciones/ con datos inválidos.
        response = client.post("/mediciones/", json=nueva_medicion_invalida)

        # ASSERT: Verificar que se devuelve un error de validación (código 422 Unprocessable Entity).
        assert response.status_code == 422

#-----
#Verificar que no es posible crear una medición sin campos obligatorios (por ejemplo, zona_id o fecha_datos).

def test_crear_medicion_invalida():

    # ACT: Intentar crear medición sin campos obligatorios.

    response = client.post(
        "/mediciones/",
        json={
            "temperatura": 25.0
        }
    )

    # ASSERT
    

    assert response.status_code == 422

# ----
# Verificar que no es posible crear una medición asociada a una zona que no existe (zona_id inválido).

def test_crear_medicion_zona_inexistente():

    # ACT : Intentar crear una medición usando una zona que no existe.

    response = client.post(
        "/mediciones/",
        json={
            "zona_id": 99999,
            **medicion_data
        }
    )

    # ASSERT: Verificar que se devuelve un error indicando que la zona no existe (código 400 Bad Request).

    assert response.status_code == 400

    assert "No se pudo crear la medición" in response.json()["detail"]   


#####--------------------------------------------------------- R - READ - GET /mediciones/ ---------------------------------------------------------------------
# Verificar que se puede obtener una medición existente por su ID y que los datos coinciden con lo creado.

def test_leer_medicion():

    # ARRANGE: Crear una zona y una medición para luego leerla.
    response_zona = client.post("/zonas/",json=zona_data)
    zona_id = response_zona.json()["id"]

    nueva_medicion = {
        "zona_id": zona_id, 
        **medicion_data
    }

    response_crear = client.post("/mediciones/", json=nueva_medicion)
    medicion_id = response_crear.json()["id"]

    # ACT: Enviar petición GET al endpoint /mediciones/{id} para obtener la medición creada.
    response = client.get(f"/mediciones/{medicion_id}")

    # ASSERT: Verificar que se obtiene la medición correctamente (código 200 OK) y que los datos coinciden.
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == medicion_id
    assert data["zona_id"] == zona_id
    assert data["fecha_datos"] == medicion_data["fecha_datos"]
    assert data["temperatura"] == medicion_data["temperatura"]
    assert data["humedad"] == medicion_data["humedad"]
    assert data["viento"] == medicion_data["viento"]
    assert data["lluvia"] == medicion_data["lluvia"]

#-----
# Verificar que se obtiene un error al intentar leer una medición que no existe (ID inválido).

def test_leer_medicion_inexistente():

     # ACT: Intentar leer una medición con un ID que no existe.
    response = client.get("/mediciones/99999")

    # ASSERT: Verificar que se devuelve un error indicando que la medición no existe (código 404 Not Found).
    assert response.status_code == 404
    assert "No existe la medición" in response.json()["detail"]        
    
#-----
# Verificar que no se puede consultar una medición usando un ID no numérico.

def test_leer_medicion_id_invalido():

    # ACT: Intentar obtener una medición usando un ID inválido.
    response = client.get("/mediciones/abc")

    # ASSERT: FastAPI debe devolver error de validación 422.
    assert response.status_code == 422


#####------------------------------------------------- U - UPDATE - PATCH /mediciones/{id} ---------------------------------------------------------------------
# Verificar que se puede actualizar una medición existente y que los datos se modifican correctamente.

def test_actualizar_medicion():

    # ARRANGE: Crear una zona y una medición para luego actualizarla.
    response_zona = client.post("/zonas/",json=zona_data)
    zona_id = response_zona.json()["id"]

    nueva_medicion = {
        "zona_id": zona_id, 
        **medicion_data
    }

    response_crear = client.post("/mediciones/", json=nueva_medicion)
    medicion_id = response_crear.json()["id"]

    # ACT: Enviar petición PATCH al endpoint /mediciones/{id} con los datos actualizados.
    medicion_actualizada = {
        "fecha_datos": "2024-06-01T15:00:00",
        "temperatura": 28.0,
        "humedad": 55.0,
        "viento": 10.0,
        "lluvia": 0.0
    }

    response = client.patch(f"/mediciones/{medicion_id}", json=medicion_actualizada)

    # ASSERT: Verificar que se actualiza la medición correctamente (código 200 OK) y que los datos coinciden con los enviados.
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == medicion_id
    assert data["zona_id"] == zona_id
    assert data["fecha_datos"] == medicion_actualizada["fecha_datos"]
    assert data["temperatura"] == medicion_actualizada["temperatura"]
    assert data["humedad"] == medicion_actualizada["humedad"]
    assert data["viento"] == medicion_actualizada["viento"]
    assert data["lluvia"] == medicion_actualizada["lluvia"]

#-----
# Verificar que no se puede actualizar una medición con datos inválidos (por ejemplo, temperatura como string).

def test_actualizar_medicion_datos_invalidos():
    
    # ARRANGE: Crear una zona y una medición para luego intentar actualizarla con datos inválidos.
    response_zona = client.post("/zonas/",json=zona_data)
    zona_id = response_zona.json()["id"]

    nueva_medicion = {
        "zona_id": zona_id, 
        **medicion_data
    }

    response_crear = client.post("/mediciones/", json=nueva_medicion)
    medicion_id = response_crear.json()["id"]

    # ACT: Intentar actualizar la medición con datos inválidos.
    medicion_invalida = {
        "fecha_datos": "2024-06-01T15:00:00",
        "temperatura": "no es un número",  # Valor inválido
        "humedad": 55.0,
        "viento": 10.0,
        "lluvia": 0.0
    }

    response = client.patch(f"/mediciones/{medicion_id}", json=medicion_invalida)

    # ASSERT: Verificar que se devuelve un error de validación (código 422 Unprocessable Entity).
    assert response.status_code == 422

#----- Verificar que no se puede actualizar una medición que no existe (ID inválido).

def test_actualizar_medicion_inexistente():
    # ACT: Intentar actualizar una medición con un ID que no existe.
    response = client.patch(
    "/mediciones/99999",
    json={
        "temperatura": 30.0
    })

    # ASSERT: Verificar que se devuelve un error indicando que la medición no existe (código 404 Not Found).
    assert response.status_code == 404
    assert "No existe la medición" in response.json()["detail"]


######------------------------------------------------- D - DELETE - DELETE /mediciones/{id} ---------------------------------------------------------------------
# Verificar que se puede eliminar una medición existente y que ya no se puede acceder a ella.

def test_eliminar_medicion():

    # ARRANGE: Crear una zona y una medición para luego eliminarla.
    response_zona = client.post("/zonas/",json=zona_data)
    zona_id = response_zona.json()["id"]

    nueva_medicion = {
        "zona_id": zona_id, 
        **medicion_data
    }

    response_crear = client.post("/mediciones/", json=nueva_medicion)
    medicion_id = response_crear.json()["id"]

    # ACT: Enviar petición DELETE al endpoint /mediciones/{id} para eliminar la medición creada.
    response = client.delete(f"/mediciones/{medicion_id}")

    # ASSERT: Verificar que se elimina la medición correctamente (código 200 OK).
    assert response.status_code == 200
    
    data = response.json()

    assert data["message"] == "Medición eliminada correctamente"
    assert data["medicion_id"] == medicion_id

    # Intentar obtener la medición eliminada para verificar que ya no existe.
    response_get = client.get(f"/mediciones/{medicion_id}")
    assert response_get.status_code == 404
    assert "No existe la medición" in response_get.json()["detail"]   

#-----
# Verificar que no se puede eliminar una medición que no existe (ID inválido).

def test_eliminar_medicion_inexistente():

    # ACT: Intentar eliminar una medición con un ID que no existe.
    response = client.delete("/mediciones/99999")

    # ASSERT: Verificar que se devuelve un error indicando que la medición no existe (código 404 Not Found).
    assert response.status_code == 404
    assert "No existe la medición" in response.json()["detail"] 

#----- 
# Verificar que no se puede eliminar una medición usando un ID no numérico.
def test_eliminar_medicion_id_invalido():

    # ACT: Intentar eliminar una medición usando un ID inválido.
    response = client.delete("/mediciones/abc")

    # ASSERT: FastAPI debe devolver error de validación 422.
    assert response.status_code == 422


#####------------------------------------------------- O - OTROS - Validación de tipo de respuesta ---------------------------------------------------------------------
# Verificar que el endpoint /mediciones/ devuelve una respuesta con tipo de contenido JSON.

def test_respuesta_tipo_json():

    # ACT: Enviar petición GET al endpoint /mediciones/ para obtener la lista de mediciones.

    response = client.get("/mediciones/")

    # ASSERT: Verificar que la respuesta tiene un código de estado 200 OK y que el tipo de contenido es JSON.
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/json"
    )