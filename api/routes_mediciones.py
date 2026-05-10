"""
Rutas de mediciones climáticas.

Este archivo contiene los endpoints relacionados con las mediciones:
consultar, crear, actualizar y borrar mediciones.

IMPORTANTE:
De momento usamos una lista en memoria como datos simulados.
Más adelante, esta lista se sustituirá por llamadas reales al CRUD
y a la base de datos.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel


# Creamos el router de mediciones.
# Todas las rutas de este archivo empezarán por /mediciones.
router = APIRouter(
    prefix="/mediciones",
    tags=["Mediciones"],
)


# ==========================================================
# SCHEMAS TEMPORALES
# ==========================================================
# Estos modelos sirven para validar los datos que llegan a la API.
# Son temporales hasta que el equipo cierre los schemas definitivos.


class MedicionCreate(BaseModel):
    """
    Datos necesarios para crear una medición.

    No incluimos id porque el sistema lo genera automáticamente.
    """

    estacion_id: int
    temperatura: float
    humedad: float
    viento: float
    lluvia: float


class MedicionUpdate(BaseModel):
    """
    Datos para actualizar una medición.

    De momento pedimos todos los campos.
    Más adelante se puede separar PUT y PATCH si queréis permitir
    actualizaciones parciales.
    """

    estacion_id: int
    temperatura: float
    humedad: float
    viento: float
    lluvia: float


# ==========================================================
# DATOS SIMULADOS
# ==========================================================
# Esta lista actúa como una base de datos temporal.
# Cuando el CRUD esté terminado, esto se cambiará por funciones reales.

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

def buscar_medicion_por_id(medicion_id: int):
    """
    Busca una medición dentro de la lista simulada.

    Si encuentra la medición, la devuelve.
    Si no la encuentra, devuelve None.
    """
    for medicion in mediciones:
        if medicion["id"] == medicion_id:
            return medicion

    return None


# ==========================================================
# ENDPOINTS
# ==========================================================

@router.get("/")
def listar_mediciones():
    """
    GET /mediciones/

    Devuelve todas las mediciones existentes.
    """
    return mediciones


@router.get("/{medicion_id}")
def obtener_medicion(medicion_id: int):
    """
    GET /mediciones/{medicion_id}

    Devuelve una medición concreta según su ID.
    Si no existe, devuelve un error 404.
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

    Recibe los datos en formato JSON.
    Devuelve código 201 porque se ha creado un recurso nuevo.
    """
    nuevo_id = max(medicion["id"] for medicion in mediciones) + 1

    medicion_creada = {
        "id": nuevo_id,
        "estacion_id": nueva_medicion.estacion_id,
        "temperatura": nueva_medicion.temperatura,
        "humedad": nueva_medicion.humedad,
        "viento": nueva_medicion.viento,
        "lluvia": nueva_medicion.lluvia,
    }

    mediciones.append(medicion_creada)

    return medicion_creada


@router.put("/{medicion_id}")
def actualizar_medicion(medicion_id: int, datos_actualizados: MedicionUpdate):
    """
    PUT /mediciones/{medicion_id}

    Actualiza una medición completa.

    Si la medición no existe, devuelve 404.
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

    Si no existe, devuelve 404.
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