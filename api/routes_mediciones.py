"""
Rutas de mediciones climáticas.

Este archivo contiene los endpoints relacionados con las mediciones:
consultar, crear, actualizar y borrar mediciones.

IMPORTANTE:
- Ya usamos el schema real MedicionCreate desde schemas/medicion_schema.py.
- Todavía usamos datos simulados porque db/crud.py aún no tiene funciones CRUD.
- Más adelante se sustituirá la lista mock por llamadas reales a la base de datos.
"""

# Importamos APIRouter para crear rutas separadas del archivo principal.
# Importamos HTTPException para devolver errores claros como 404.
# Importamos status para usar códigos HTTP con nombres legibles.
from fastapi import APIRouter, HTTPException, status

# Importamos el schema real de mediciones.
# Este schema valida los datos de entrada:
# - estacion_id
# - temperatura
# - humedad
# - viento
# - lluvia
from schemas.medicion_schema import MedicionCreate


# ==========================================================
# ROUTER DE MEDICIONES
# ==========================================================

# Creamos el router de mediciones.
# prefix="/mediciones" significa que todas las rutas de este archivo
# empezarán por /mediciones.
#
# tags=["Mediciones"] sirve para que Swagger agrupe estos endpoints
# bajo el bloque "Mediciones".
router = APIRouter(
    prefix="/mediciones",
    tags=["Mediciones"],
)


# ==========================================================
# DATOS SIMULADOS
# ==========================================================

# Esta lista actúa como una base de datos temporal.
#
# IMPORTANTE:
# Esto NO es la base de datos real.
# Es una solución provisional para poder probar los endpoints
# mientras db/crud.py todavía está vacío.
#
# Cuando exista el CRUD real, eliminaremos esta lista y llamaremos
# a funciones como:
# - obtener_mediciones()
# - obtener_medicion_por_id()
# - crear_medicion()
# - actualizar_medicion()
# - eliminar_medicion()

mediciones = [
    {
        "id": 1,
        "estacion_id": 101,
        "temperatura": 22.5,
        "humedad": 60.0,
        "viento": 12.0,
        "lluvia": 0.0,
    },
    {
        "id": 2,
        "estacion_id": 102,
        "temperatura": 28.1,
        "humedad": 45.0,
        "viento": 18.5,
        "lluvia": 1.2,
    },
]


# ==========================================================
# FUNCIONES AUXILIARES
# ==========================================================

# Estas funciones ayudan a no repetir código dentro de los endpoints.


def buscar_medicion_por_id(medicion_id: int):
    """
    Busca una medición dentro de la lista simulada.

    Parámetros:
        medicion_id: ID de la medición que queremos encontrar.

    Devuelve:
        - La medición si existe.
        - None si no existe.

    Más adelante esta función se sustituirá por una función CRUD real.
    """
    for medicion in mediciones:
        if medicion["id"] == medicion_id:
            return medicion

    return None


def generar_nuevo_id():
    """
    Genera un nuevo ID para una medición simulada.

    Como todavía no usamos base de datos real en estos endpoints,
    calculamos el siguiente ID a partir de la lista mock.

    Si la lista está vacía, empezamos en 1.
    """
    if not mediciones:
        return 1

    return max(medicion["id"] for medicion in mediciones) + 1


# ==========================================================
# ENDPOINTS DE MEDICIONES
# ==========================================================

# Aquí empieza realmente la parte de API REST.
#
# Cada endpoint combina:
# - un verbo HTTP: GET, POST, PUT, DELETE
# - una ruta: /mediciones/, /mediciones/{medicion_id}
# - una función de Python


@router.get("/")
def listar_mediciones():
    """
    GET /mediciones/

    Devuelve todas las mediciones existentes.

    Estado actual:
        Devuelve datos simulados.

    Estado futuro:
        Llamará al CRUD para consultar la base de datos real.
    """
    return mediciones


@router.get("/{medicion_id}")
def obtener_medicion(medicion_id: int):
    """
    GET /mediciones/{medicion_id}

    Devuelve una medición concreta según su ID.

    Ejemplo:
        /mediciones/1

    Si la medición no existe, devuelve error 404.
    """
    medicion = buscar_medicion_por_id(medicion_id)

    if medicion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medición no encontrada",
        )

    return medicion


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_medicion(nueva_medicion: MedicionCreate):
    """
    POST /mediciones/

    Crea una nueva medición.

    Recibe los datos en formato JSON y los valida usando el schema real
    MedicionCreate de schemas/medicion_schema.py.

    Ejemplo de body JSON:

    {
        "estacion_id": 103,
        "temperatura": 24.8,
        "humedad": 55.0,
        "viento": 10.5,
        "lluvia": 0.0
    }

    Devuelve:
        - La medición creada.
        - Código 201 porque se ha creado un recurso nuevo.
    """
    medicion_creada = {
        "id": generar_nuevo_id(),
        "estacion_id": nueva_medicion.estacion_id,
        "temperatura": nueva_medicion.temperatura,
        "humedad": nueva_medicion.humedad,
        "viento": nueva_medicion.viento,
        "lluvia": nueva_medicion.lluvia,
    }

    mediciones.append(medicion_creada)

    return medicion_creada


@router.put("/{medicion_id}")
def actualizar_medicion(medicion_id: int, datos_actualizados: MedicionCreate):
    """
    PUT /mediciones/{medicion_id}

    Actualiza una medición completa.

    Ejemplo:
        /mediciones/1

    De momento usamos MedicionCreate también para actualizar,
    porque todavía no existe un MedicionUpdate definitivo en
    schemas/medicion_schema.py.

    Si la medición no existe, devuelve error 404.
    """
    medicion = buscar_medicion_por_id(medicion_id)

    if medicion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medición no encontrada",
        )

    medicion["estacion_id"] = datos_actualizados.estacion_id
    medicion["temperatura"] = datos_actualizados.temperatura
    medicion["humedad"] = datos_actualizados.humedad
    medicion["viento"] = datos_actualizados.viento
    medicion["lluvia"] = datos_actualizados.lluvia

    return medicion


@router.delete("/{medicion_id}")
def eliminar_medicion(medicion_id: int):
    """
    DELETE /mediciones/{medicion_id}

    Elimina una medición por ID.

    Ejemplo:
        /mediciones/1

    Si la medición no existe, devuelve error 404.
    """
    medicion = buscar_medicion_por_id(medicion_id)

    if medicion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medición no encontrada",
        )

    mediciones.remove(medicion)

    return {
        "mensaje": f"Medición con ID {medicion_id} eliminada correctamente"
    }